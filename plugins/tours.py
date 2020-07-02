from typing import Optional

from plugin_loader import plugin_wrapper
import utils


async def create_tour(
    self,
    room: str,
    *,
    formatid: str = "customgame",
    generator: str = "elimination",
    playercap: Optional[int] = None,
    generatormod: str = "",
    name: str = "",
    autostart: float = 2,
    autodq: float = 1.5,
    allow_scouting: bool = False,
    forcetimer: bool = False,
    rules=[]
) -> None:
    tournew = "/tour new {formatid}, {generator}, {playercap}, {generatormod}, {name}"
    await self.send_message(
        room,
        tournew.format(
            formatid=formatid,
            generator=generator,
            playercap=str(playercap) if playercap else "",
            generatormod=generatormod,
            name=name,
        ),
    )
    if autostart is not None:
        await self.send_message(room, "/tour autostart {}".format(autostart))
    if autodq is not None:
        await self.send_message(room, "/tour autodq {}".format(autodq))
    if not allow_scouting:
        await self.send_message(room, "/tour scouting off")
    if forcetimer:
        await self.send_message(room, "/tour forcetimer on")
    if rules:
        await self.send_message(room, "/tour rules {}".format(",".join(rules)))


@plugin_wrapper(
    helpstr="<i> poke1, poke2, ... </i> Avvia un randpoketour.", is_unlisted=True
)
async def randpoketour(self, room: str, user: str, arg: str) -> None:
    if room is None or not utils.is_driver(user):
        return

    if arg.strip() == "":
        return await self.send_message(room, "Inserisci almeno un Pokémon")

    formatid = "nationaldex"
    name = "!RANDPOKE TOUR"
    rules = ["Z-Move Clause", "Dynamax Clause"]
    bans = ["All Pokemon"]
    unbans = []
    if "," in arg:
        sep = ","
    else:
        sep = " "
    for item in arg.split(sep):
        unbans.append(item.strip() + "-base")

    rules.extend(["-" + i for i in bans])
    rules.extend(["+" + i for i in unbans])

    await create_tour(
        self, room, formatid=formatid, name=name, autostart=12, rules=rules
    )


@plugin_wrapper(
    aliases=["sibb"],
    helpstr="Avvia un torneo Super Italian Bros. Brawl",
    is_unlisted=True,
)
async def waffletour(self, room: str, user: str, arg: str) -> None:
    if room is None or not utils.is_driver(user):
        return

    name = "Super Italian Bros. Brawl"
    rules = [
        "Cancel Mod",
        "Dynamax Clause",
        "Endless Battle Clause",
        "Evasion Moves Clause",
        "HP Percentage Mod",
        "Obtainable Formes",  # to avoid multiple Mega-Evolutions
        "Sleep Clause Mod",
        "Species Clause",
    ]

    await create_tour(
        self, room, name=name, autostart=5, autodq=3, forcetimer=True, rules=rules
    )

    await self.send_message(room, "!viewfaq sibb")
