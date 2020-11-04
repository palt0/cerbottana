from __future__ import annotations

import re
import string
from typing import TYPE_CHECKING, List

from flask import abort, current_app, render_template
from flask import session as web_session
from sqlalchemy.orm.exc import ObjectDeletedError
from sqlalchemy.sql import func

import databases.database as d
import utils
from database import Database
from plugins import command_wrapper, parametrize_room, route_wrapper

if TYPE_CHECKING:
    from models.message import Message


def to_html_quotebox(quote: str) -> str:
    """Generates HTML that shows a quote.

    Args:
        quote (str): Raw quote string, added through `.addquote`.

    Raises:
        BaseException: quote is empty.

    Returns:
        str: htmlbox.
    """
    if not quote:
        # This shouldn't happen because empty quotes are ignored by `.addquote`.
        raise BaseException("Trying to create quotebox for empty quote.")

    # Valid timestamp formats: [xx:xx], [xx:xx:xx]
    timestamp_regex = r"(\[\d{2}:\d{2}(?::\d{2})?\])"
    splitted = re.split(timestamp_regex, quote)

    # Return the quote unparsed if it has a custom format, aka one of these conditions
    # applies:
    # (1) Quote doesn't start with a timestamp.
    # (2) Quote only has timestamps.
    if splitted[0] or not any(part.lstrip() for part in splitted[::2]):
        return utils.linkify(quote)

    lines: List[str] = []
    for timestamp, phrase in zip(splitted[1::2], splitted[2::2]):
        # Wrap every line in a <div class="chat"></div> and if it is a regular chat
        # message format it accordingly.

        if not phrase:
            # Timestamp with an empty phrase.
            # Append the timestamp to the previous phrase, it was probably part of it.
            if not lines:
                lines.append(timestamp)
            else:
                lines[-1] += timestamp
        elif ": " in phrase and phrase[0] != "(":
            # phrase is a chat message.
            # Example: "[03:56] @Plat0: Hi"

            # userstring: Username, optionally preceded by its rank.
            # body: Content of the message sent by the user.
            userstring, body = phrase.split(": ", 1)
            userstring = userstring.lstrip()

            # rank: Character rank or "" (not " ") in case of a regular user.
            # username: userstring variable stripped of the character rank.
            if userstring[0] not in string.ascii_letters + string.digits:
                rank = userstring[0]
                username = userstring[1:]
            else:
                rank = ""
                username = userstring

            # Escape special characters: needs to be done last.
            # Timestamp doesn't need to be escaped.
            rank = utils.html_escape(rank)
            username = utils.html_escape(username)
            body = utils.linkify(body)

            lines.append(
                f"<small>{timestamp} {rank}</small>"
                f"<username>{username}:</username> "
                f"<em>{body}</em>"
            )
        else:
            # phrase is a PS message that may span over multiple lines.
            # Example: "[14:20:43] (plat0 forcibly ended a tournament.)"

            # Text contained within round parentheses is considered a separated line.
            # This is true for most use-cases but it's still euristic.
            sublines = re.split(r"(\(.*\))", phrase)
            sublines = [utils.linkify(s) for s in sublines if s.strip()]

            # The timestamp is written only on the first subline.
            sublines[0] = f"<small>{timestamp}</small> <em>{sublines[0]}</em>"
            lines += sublines
    # Merge lines
    html = '<div class="message-log" style="float: left">'
    for line in lines:
        html += f'<div class="chat">{line}</div>'
    html += "</div>"
    return html


@command_wrapper(aliases=("newquote", "quote"))
async def addquote(msg: Message) -> None:
    # Permissions for this command are temporarily lowered to voice level.
    # if msg.room is None or not msg.user.has_role("driver", msg.room):
    #   return
    if msg.room is None:
        return

    if not msg.arg:
        await msg.room.send("Cosa devo salvare?")
        return

    maxlen = 250  # lower than the message limit to have space for metadata
    if len(msg.arg) > maxlen:
        await msg.room.send(f"Quote troppo lunga, max {maxlen} caratteri.")
        return

    db = Database.open()
    with db.get_session() as session:
        result = d.Quotes(
            message=msg.arg,
            roomid=msg.room.roomid,
            author=msg.user.userid,
            date=func.date(),
        )
        session.add(result)
        session.commit()  # type: ignore  # sqlalchemy

        try:
            if result.id:
                await msg.room.send("Quote salvata.")
                return
        except ObjectDeletedError:
            pass
        await msg.room.send("Quote già esistente.")


@command_wrapper(aliases=("q",))
@parametrize_room
async def randquote(msg: Message) -> None:
    db = Database.open()
    with db.get_session() as session:
        query_ = session.query(d.Quotes).filter_by(roomid=msg.parametrized_room.roomid)
        if msg.arg:
            # LIKE wildcards are supported and "*" is considered an alias for "%".
            keyword = msg.arg.replace("*", "%")
            query_ = query_.filter(d.Quotes.message.ilike(f"%{keyword}%"))

        quote_row = query_.order_by(func.random()).first()
        if not quote_row:
            await msg.reply("Nessuna quote trovata.")
            return
        await msg.reply_htmlbox(to_html_quotebox(quote_row.message))


@command_wrapper(aliases=("deletequote", "delquote", "rmquote"))
async def removequote(msg: Message) -> None:
    # Permissions for this command are temporarily lowered to voice level.
    # if msg.room is None or not msg.user.has_role("driver", msg.room):
    #   return
    if msg.room is None:
        return

    if not msg.arg:
        await msg.room.send("Che quote devo cancellare?")
        return

    db = Database.open()
    with db.get_session() as session:
        result = (
            session.query(d.Quotes)
            .filter_by(message=msg.arg, roomid=msg.room.roomid)
            .delete()
        )

        if result:
            await msg.room.send("Quote cancellata.")
        else:
            await msg.room.send("Quote inesistente.")


@command_wrapper(aliases=("quotes", "quoteslist"))
@parametrize_room
async def quotelist(msg: Message) -> None:
    db = Database.open()
    with db.get_session() as session:
        quotes_n = (
            session.query(func.count(d.Quotes.id))  # type: ignore  # sqlalchemy
            .filter_by(roomid=msg.parametrized_room.roomid)
            .scalar()
        )

    if not quotes_n:
        await msg.reply("Nessuna quote da visualizzare.")
        return

    phrase = f"{msg.conn.domain}quotes/{msg.parametrized_room}"
    if msg.parametrized_room.is_private:
        token_id = utils.create_token({msg.parametrized_room.roomid: " "})
        phrase += f"?token={token_id}"

    await msg.reply(phrase)


@route_wrapper("/quotes/<room>")
def quotes_route(room: str) -> str:
    if room not in current_app.conn.rooms or current_app.conn.rooms[room].is_private:
        if not web_session.get(room):
            abort(401)

    db = Database.open()

    with db.get_session() as session:
        rs = session.query(d.Quotes).filter_by(roomid=room).all()
        if not rs:
            abort(401)  # no quotes for this room

        return render_template("quotes.html", rs=rs, room=room)
