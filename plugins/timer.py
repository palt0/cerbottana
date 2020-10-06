from __future__ import annotations

import asyncio
import math
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Dict

from plugins import command_wrapper

if TYPE_CHECKING:
    from models.message import Message
    from models.room import Room


# Mutex: Allow up to 1 active timer per room.
timers: Dict[Room, datetime] = {}  # Room, expire dt


def remaining(minutes: float) -> str:
    """Returns a phrase that describes the remaining time.

    Args:
        minutes (float): Remaining time expressed in minutes.
    """
    if minutes <= 1:
        return "Meno di 1 minuto rimanente!"
    return f"Meno di {math.ceil(minutes)} minuti rimanenti!"


@command_wrapper(
    aliases=("countdown",),
    helpstr="Aspetta una quantità di tempo in minuti",
)
async def timer(msg: Message) -> None:
    if msg.room is None:
        return

    # If there is already an active timer in the current room, print the remaining time
    # and don't start another timer concurently.
    if msg.room in timers:
        delta = timers[msg.room] - datetime.now()
        minutes = delta.seconds / 60
        await msg.reply(f"C'è già un timer attivo. {remaining(minutes)}")
        return

    try:
        minutes = float(msg.arg)
        seconds = math.ceil(minutes * 60)
        if seconds <= 0:
            raise ValueError
    except ValueError:
        await msg.reply("Inserire un numero valido di minuti")
        return

    max_minutes = 300  # 5 hours
    if minutes > max_minutes:
        await msg.reply(f"Tempo massimo di {max_minutes} minuti")
        return

    timers[msg.room] = datetime.now() + timedelta(seconds=seconds)
    await msg.reply(f"Timer avviato. {remaining(minutes)}")

    await asyncio.sleep(seconds)
    del timers[msg.room]
    await msg.reply(f"**Tempo scaduto**, {msg.user}!")
