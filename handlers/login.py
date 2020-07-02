import json

import urllib.request
import urllib.parse

from handler_loader import handler_wrapper
import utils


@handler_wrapper(["challstr"])
async def challstr(self, roomid, *challstring):
    challstring = "|".join(challstring)

    payload = "act=login&name={username}&pass={password}&challstr={challstr}".format(
        username=self.username, password=self.password, challstr=challstring
    ).encode()

    req = urllib.request.Request(
        "https://play.pokemonshowdown.com/action.php",
        payload,
        {"User-Agent": "Mozilla"},
    )
    resp = urllib.request.urlopen(req)

    assertion = json.loads(resp.read().decode("utf-8")[1:])["assertion"]

    if assertion:
        await self.send_message("", "/trn {},0,{}".format(self.username, assertion))


@handler_wrapper(["updateuser"])
async def updateuser(self, roomid, user, named, avatar, settings):
    username = user.split("@")[0]
    if utils.to_user_id(username) != utils.to_user_id(self.username):
        return

    if avatar != self.avatar:
        await self.send_message("", "/avatar {}".format(self.avatar))

    await self.send_message("", "/status {}".format(self.statustext))

    for public_room in self.rooms:
        await self.send_message("", "/join {}".format(public_room))

    for private_room in self.private_rooms:
        await self.send_message("", "/join {}".format(private_room))