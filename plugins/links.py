from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from plugin_loader import plugin_wrapper

if TYPE_CHECKING:
    from connection import Connection


@plugin_wrapper(
    helpstr="Elenca gli avatar disponibili. Per usarne uno, <code>/avatar [nome]</code>"
)
async def avatars(conn: Connection, room: Optional[str], user: str, arg: str) -> None:
    await conn.send_reply(
        room, user, "https://play.pokemonshowdown.com/sprites/trainers/"
    )
