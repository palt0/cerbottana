from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional

from plugins import Command, command_wrapper

if TYPE_CHECKING:
    from connection import Connection


@command_wrapper(is_unlisted=True)
async def help(conn: Connection, room: Optional[str], user: str, arg: str) -> None:
    query = arg.strip().lower()
    pairs: Dict[str, Command] = dict()  # remains empty if no match is found

    if not query:
        # requesting a list of all command: exclude unlisted commands, exclude aliases
        pairs = Command.get_pairs(with_aliases=False)
        pairs = {k: inst for k, inst in pairs.items() if not inst.is_unlisted}
    elif query in Command.get_groups():
        # requesting a group of commands: include unlisted commands, exclude aliases
        pairs = Command.get_pairs(with_aliases=False, group=query)
    else:
        # requesting a specific command: consider unlisted commands and aliases
        all_aliases = Command.get_pairs(with_aliases=True)
        if query in all_aliases:
            pairs = {query: all_aliases[query]}

    # filter out commands without a helpstring
    help_dict = {alias: inst.helpstr for alias, inst in pairs.items() if inst.helpstr}

    if not help_dict:
        await conn.send_reply(room, user, "Nessun comando trovato")
        return

    html = ""
    for alias, helpstr in help_dict.items():
        html += f"<b>{alias}</b> {helpstr}<br>"
    await conn.send_htmlbox(room, user, html[:-4])
