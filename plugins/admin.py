from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import utils
from models.room import Room
from plugins import command_wrapper

if TYPE_CHECKING:
    from models.message import Message


@command_wrapper(aliases=("ammaz", "ammazz"))
async def kill(msg: Message) -> None:
    if msg.user.is_administrator and msg.conn.websocket is not None:
        for task in asyncio.all_tasks(loop=msg.conn.loop):
            task.cancel()
        await msg.conn.websocket.close()


@command_wrapper()
async def botjoin(msg: Message) -> None:
    roomid = utils.to_room_id(msg.arg)
    if not roomid:
        await msg.reply("Inserire un nome valido per la room")
        return

    if roomid.startswith("battle-"):
        await msg.reply("Non posso joinare una room di lotta...")
        return

    room = Room.get(msg.conn, roomid)
    if not (msg.user.is_administrator or msg.user.has_role("owner", room)):
        return

    if not await room.join():
        await msg.reply("Impossibile joinare la room")


@command_wrapper()
async def botleave(msg: Message) -> None:
    if msg.room is not None and not msg.arg:
        room = msg.room
    else:
        roomid = utils.to_room_id(msg.arg)
        if not roomid:
            await msg.reply("Inserire un nome valido per la room")
            return

        room = Room.get(msg.conn, roomid)

    if not await room.leave():
        await msg.reply("Impossibile leftare la room")
