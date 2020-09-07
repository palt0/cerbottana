from __future__ import annotations

import json
from collections import deque
from datetime import datetime
from math import ceil, log2
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set

from environs import Env
from flask import abort, render_template, request
from flask import session as web_session
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.session import Session
from typing_extensions import TypedDict

import databases.database as d
import utils
from database import Database
from handlers import handler_wrapper
from plugins import command_wrapper, parametrize_room, route_wrapper

if TYPE_CHECKING:
    from connection import Connection

env = Env()
env.read_env()

TournamentEnd = TypedDict(  # type: ignore[misc]
    "TournamentEnd",
    {
        "results": List[List[str]],
        "format": str,
        "generator": str,
        "bracketData": Dict[str, Any],
    },
)

Leaderboard = List[List[str]]


# --- Common logic ---


@handler_wrapper(["tournament"])  # hooked on |tournament|end|
async def tourlogger(conn: Connection, roomid: str, *args: str) -> None:
    if len(args) != 2 or args[0] != "end":
        return

    data: TournamentEnd
    try:
        data = json.loads(args[1])
    except ValueError:
        print("Received invalid tournament data")
        return

    leaderboard = parse_tourdata(data)
    nr_players = sum(len(sublist) for sublist in leaderboard)

    # Rewards system: we award point to winner, runner-up and semifinalists
    # We don't want to award points to every player by default, so we need at least
    # 2^2 + 1 partecipants
    if nr_players <= 4:
        return

    # On a small tour with at most 8 players we give 3, 2, 1 points to winner,
    # runner-up, semifinalists respectively
    # At every power of 2 increase of the number of partecipants, rewards are
    # incremented by 1, capped at 64 players
    increment = ceil(log2(nr_players)) - 3
    if increment > 4:  # log2(64) - 2 = 4
        increment = 4
    rewards = [x + increment for x in (3, 2, 1)]

    message = ""  # string sent at the end of the evaluation

    print(leaderboard)
    db = Database.open()
    with db.get_session() as session:
        for placement, players in enumerate(leaderboard):
            points = rewards[placement] if placement < len(rewards) else 0

            # Update message (scope: placement)
            if points:
                message += ", ".join(players)
                message += " ricevono" if len(players) > 1 else " riceve"
                message += f" {points}"
                message += " punto. " if points == 1 else " punti. "

            # Register into database (scope: player)
            for player in leaderboard[placement]:
                userid = utils.to_user_id(player)
                now = datetime.now()
                date = f"{now.month}/{now.year}"
                query_ = session.query(d.Points).filter_by(
                    userid=userid, roomid=roomid, date=date
                )
                if not query_.one_or_none():
                    row = d.Points(
                        userid=userid,
                        roomid=roomid,
                        date=date,
                        tourpoints=points,
                        games=1,
                        first=0,
                        second=0,
                        third=0,
                    )
                    session.add(row)
                    session.commit()  # type: ignore  # sqlalchemy
                else:
                    query_.update(
                        {
                            d.Points.tourpoints: d.Points.tourpoints + points,
                            d.Points.games: d.Points.games + 1,
                        }
                    )

                # Besides nr. of games played (needed to calc percentages), we only
                # register wins, finals, semifinals in the db. This simplifies the
                # logic at the expense of not being able to re-calc past player points
                # in the future if the formula changes, but it appears negligible.
                cols = (d.Points.first, d.Points.second, d.Points.third)
                if placement < len(cols):
                    col = cols[placement]
                    query_.update({col: col + 1})

    await conn.send_message(roomid, message)


def parse_tourdata(tourdata: TournamentEnd) -> Leaderboard:
    """
    Parses tourdata into a Leaderboard object by calling the appropriate parser
    depending on the bracket data type.
    It also performs operations common to every bracket type, such as sorting
    usernames alphabetically.
    """
    parsers = {"tree": parse_tree, "table": parse_table}

    type_ = tourdata["bracketData"]["type"]
    if type_ in parsers:
        leaderbord: Leaderboard = parsers[type_](tourdata)

        # Sort alphabetically people finished on equal place
        for placement in leaderbord:
            placement.sort()

        return leaderbord
    else:
        msg = f'Unsupported tour with generator: {tourdata["generator"]}\n'
        msg += f"Bracket data type: {type_}"
        print(f"Unsupported tour generator: {msg}")
        return []


# --- Tour generator parsers ---


def parse_tree(tourdata: TournamentEnd) -> Leaderboard:
    """
    Parses a tree bracket, used by Elimination tours.
    Dispatched by parse_tourdata().
    """
    bracket = tourdata["bracketData"]["rootNode"]
    queue = deque([(id(bracket), bracket, 0)])  # dict id, dict, depth
    refs: Set[int] = set()
    players: Set[str] = set()
    leaderboard: Leaderboard = []

    while queue:
        id_, node, depth = queue.popleft()

        if len(leaderboard) < depth + 1:
            leaderboard.append([])

        if node["team"] not in players:
            leaderboard[depth].append(node["team"])
            players.add(node["team"])

        # Safety check: avoid circular references
        # (see https://stackoverflow.com/a/23499088)
        if id_ in refs:
            continue
        refs.add(id_)

        if "children" in node:
            queue += ((id(elem), elem, depth + 1) for elem in node["children"])

    return leaderboard


def parse_table(tourdata: TournamentEnd) -> Leaderboard:
    """
    Parses a table bracket, used by Round Robin tours.
    Dispatched by parse_tourdata().
    """
    return tourdata["results"]


# --- Visualization tools ---


def get_points_query(
    session: Session,
    roomid: str,
    month: Optional[int] = None,
    year: Optional[int] = None,
) -> Query[d.Points]:  # pylint: disable=unsubscriptable-object
    """
    Returns a query of d.Points that applies common filtering and ordering.

    :param roomid: room filter
    :param month: month filter, defaults to current month
    :param year: year filter, defaults to current year
    """
    now = datetime.now()
    month = month if month else now.month
    year = year if year else now.year
    date = f"{month}/{year}"

    return (
        session.query(d.Points)
        .filter(
            d.Points.roomid == roomid,
            d.Points.date == date,
            d.Points.tourpoints > 0,
        )
        .order_by(d.Points.tourpoints.desc(), d.Points.userid)
    )


@command_wrapper(helpstr="Mostra i punti totalizzati nei tornei di questo mese")
@parametrize_room
async def rank(conn: Connection, room: Optional[str], user: str, arg: str) -> None:
    target_room = arg.split(",")[0]
    db = Database.open()
    with db.get_session() as session:
        row = (
            get_points_query(session, target_room)
            .filter_by(userid=utils.to_user_id(user))
            .one_or_none()
        )

        tourpoints = row.tourpoints if row else 0
        msg = f"Hai **{tourpoints}** "
        msg += "punto " if tourpoints == 1 else "punti "
        msg += f"nella room {target_room}. "
        msg += f"Classifica completa: {conn.domain}/leaderboard/{target_room}"
        await conn.send_reply(room, user, msg)


@command_wrapper(
    aliases=("leaderboard",), helpstr="Mostra la leaderboard mensile dei tornei"
)
@parametrize_room
async def top(conn: Connection, room: Optional[str], user: str, arg: str) -> None:
    target_room = arg.split(",")[0]

    # limit: Max nr. of entries; this might be received as a user argument in the future
    limit = 10

    # url: Links to the Flask webpage that shows the same leaderboard; it's a
    # protected webpage if the room is private
    #
    # FIXME: Can't use utils.create_token within a session scope because the function
    # also closes a session scope that points to the same database
    url = f"{conn.domain}leaderboard/{target_room}"
    if utils.is_private(conn, target_room):
        token_id = utils.create_token({target_room: " "})
        url += f"?token={token_id}"

    db = Database.open()
    with db.get_session() as session:
        query_ = get_points_query(session, target_room)
        rs = query_.limit(limit).all()
        if not rs:
            await conn.send_reply(room, user, "Nessuna partita giocata questo mese...")
            return

        # Linking an htmlbox in PM generally exceeds PS' character limit and it also
        # looks quite messy, as people usually have less horizontal space even on
        # larger screens
        if room is None:
            await conn.send_pm(user, url)
            return

        # is_truncated: Holds True if the generated leaderboard shows doesn't all the
        # players memorized in d.Points
        is_truncated = query_.count() > limit

        html = utils.render_template(
            "commands/points.html",
            rs=rs,
            room=target_room.upper(),
            url=url,
            is_truncated=is_truncated,
        )
        await conn.send_htmlbox(room, None, html)


@route_wrapper("/leaderboard/<room>", methods=["GET"])
def top_route(room: str) -> str:
    """
    Flask webpage alternative to `top` command.
    This is a stub, will be expanded after an initial testing period.

    Optional GET parameters:
    - y: year, defaults to the current year
    - m: month, defaults to the current month
    """
    if room in env.list("PRIVATE_ROOMS"):
        if not web_session.get(room):
            abort(401)

    now = datetime.now()
    year = request.args.get("y", now.year, type=int)
    month = request.args.get("m", now.month, type=int)
    date = f"{month}/{year}"

    db = Database.open()
    with db.get_session() as session:
        rs = get_points_query(session, room, month=month, year=year).all()
        return render_template("points.html", rs=rs, room=room.upper(), date=date)
