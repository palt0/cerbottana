from __future__ import annotations

import asyncio
import datetime
from typing import TYPE_CHECKING, Optional

from flask import abort, render_template, request
from flask import session as web_session
from lxml.html import fromstring
from sqlalchemy.sql import func

import databases.logs as l
import utils
from database import Database
from handlers import handler_wrapper
from plugins import command_wrapper, parametrize_room, route_wrapper
from room import Room
from tasks import recurring_task_wrapper

if TYPE_CHECKING:
    from connection import Connection


@recurring_task_wrapper()
async def logger_task(conn: Connection) -> None:
    db = Database.open("logs")
    while True:
        with db.get_session() as session:
            yesterday = datetime.date.today() - datetime.timedelta(days=1)

            for room in conn.rooms + conn.private_rooms:
                last_date = (
                    session.query(func.max(l.Logs.date)).filter_by(roomid=room).scalar()
                )

                if last_date:
                    date = datetime.date.fromisoformat(last_date) + datetime.timedelta(
                        days=1
                    )
                else:
                    date = yesterday - datetime.timedelta(days=2)

                while date < yesterday:
                    await asyncio.sleep(30)
                    await conn.send_message(
                        "", f"/join view-chatlog-{room}--{date.isoformat()}", False
                    )
                    date += datetime.timedelta(days=1)

        await asyncio.sleep(12 * 60 * 60)


@handler_wrapper(["pagehtml"])
async def logger(conn: Connection, roomid: str, *args: str) -> None:
    if roomid[:13] != "view-chatlog-":
        return

    room, date = roomid[13:].split("--")
    chatlog = "|".join(args).strip()

    html = fromstring(chatlog)

    values = []

    for el in html.xpath('//div[@class="chat"]'):
        time = el.xpath("small")
        user = el.xpath("strong")
        message = el.xpath("q")
        if time and user and message:
            userrank = user[0].xpath("small")
            values.append(
                {
                    "roomid": room,
                    "date": date,
                    "time": time[0].text.strip("[] "),
                    "userrank": userrank[0].text if userrank else " ",
                    "userid": utils.to_user_id(user[0].text_content()),
                    "message": message[0].text_content(),
                }
            )

    if not values:
        values.append({"roomid": room, "date": date})

    db = Database.open("logs")
    with db.get_session() as session:
        session.query(l.Logs).filter_by(date=date, roomid=room).delete(
            synchronize_session=False
        )
        n = 0
        while True:
            v = values[n * 1000 : (n + 1) * 1000]
            if not v:
                break
            session.bulk_insert_mappings(l.Logs, v)
            n += 1


@command_wrapper()
@parametrize_room
async def getlogs(conn: Connection, room: Optional[str], user: str, arg: str) -> None:
    if utils.to_user_id(user) in conn.administrators:
        args = arg.split(",")
        logsroom = utils.to_room_id(args[0])
        date = args[1].strip()
        await conn.send_message("", f"/join view-chatlog-{logsroom}--{date}", False)


@command_wrapper(aliases=("linecount",))
@parametrize_room
async def linecounts(
    conn: Connection, room: Optional[str], user: str, arg: str
) -> None:
    userid = utils.to_user_id(user)
    args = arg.split(",")
    logsroom = utils.to_room_id(args[0])

    users = Room.get(logsroom).users
    if userid not in users:
        return

    rank = users[userid]["rank"]

    token_id = utils.create_token({logsroom: rank}, 1)

    message = f"{conn.domain}linecounts/{logsroom}?token={token_id}"
    if len(args) > 1:
        search = ",".join([utils.to_user_id(u) for u in args[1:]])
        message += f"&search={search}"

    await conn.send_pm(user, message)


@route_wrapper("/linecounts/<room>")
def linecounts_route(room: str) -> str:
    if not utils.is_driver(web_session.get(room)):
        abort(401)

    return render_template("linecounts.html", room=room)


@route_wrapper("/linecounts/<room>/data")
def linecounts_data(room: str) -> str:
    if not utils.is_driver(web_session.get(room)):
        abort(401)

    params = {"roomid": room}

    sql = "SELECT date"
    if request.args.get("users"):
        n = 0
        for user in request.args["users"].split(","):
            n += 1
            sql += f" || ',' || SUM(CASE WHEN userid = :userid_{n} THEN 1 ELSE 0 END) "
            params[f"userid_{n}"] = utils.to_user_id(user)
    else:
        sql += " || ',' || SUM(CASE WHEN userrank IS NOT NULL THEN 1 ELSE 0 END) "
        sql += " || ',' || SUM(CASE WHEN userrank = ' ' THEN 1 ELSE 0 END) "
        sql += " || ',' || SUM(CASE WHEN userrank != ' ' THEN 1 ELSE 0 END) "
        sql += " || ',' || SUM(CASE WHEN userrank NOT IN(' ', '+') THEN 1 ELSE 0 END) "
        sql += " || ',' || SUM(CASE WHEN userrank = '+' THEN 1 ELSE 0 END) "
        sql += " || ',' || SUM(CASE WHEN userrank = '%' THEN 1 ELSE 0 END) "
        sql += " || ',' || SUM(CASE WHEN userrank = '@' THEN 1 ELSE 0 END) "
        sql += " || ',' || SUM(CASE WHEN userrank = '*' THEN 1 ELSE 0 END) "
        sql += " || ',' || SUM(CASE WHEN userrank IN('&', '~') THEN 1 ELSE 0 END) "
        sql += " || ',' || SUM(CASE WHEN userrank = '#' THEN 1 ELSE 0 END) "
    sql += " AS data "
    sql += " FROM logs WHERE roomid = :roomid GROUP BY date"

    db = Database.open("logs")

    with db.get_session() as session:
        data = session.execute(sql, params)

        return "\n".join([row["data"] for row in data])
