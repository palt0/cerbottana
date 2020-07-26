from __future__ import annotations

import glob
import importlib
from functools import wraps
from os.path import basename, dirname, isfile, join
from typing import (
    TYPE_CHECKING,
    Awaitable,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Set,
    Tuple,
    Union,
)

from flask import abort, session

import utils
from room import Room

if TYPE_CHECKING:
    from connection import Connection

    CommandFunc = Callable[[Connection, Optional[str], str, str], Awaitable[None]]
    RouteFunc = Union[Callable[[], str], Callable[[str], str]]


# --- Command logic and complementary decorators ---


class Command:
    """See ./README.md for an explanation of the purpose of this class."""

    _instances: List[Command] = []
    _groups: Set[str] = set()

    def __init__(
        self,
        func: CommandFunc,
        aliases: List[str] = [],
        group: str = "misc",
        helpstr: str = "",
        is_unlisted: bool = False,
    ) -> None:
        self.name = func.__name__
        self.callback = func
        self._aliases = [self.name] + aliases
        self.group = group
        self.helpstr = helpstr
        self.is_unlisted = is_unlisted

        # check that this new instance isn't conflicting with previous ones
        for old_alias, old_inst in self.get_pairs().items():
            if old_alias in self._aliases:
                errmsg = f"Error: '{old_alias}' alias of {old_inst.name} command "
                errmsg += f"is redefined by {self.name} command, keeping old definition"
                print(errmsg)
                return  # skip registering phase

        self._instances.append(self)
        self._instances.sort(key=lambda inst: inst.name)  # TODO: optimize
        self._groups.add(group)

    @property
    def aliases(self) -> List[str]:
        return self._aliases  # expose self._aliases as read-only

    async def __call__(
        self, conn: Connection, room: Optional[str], user: str, arg: str
    ) -> None:
        if room is not None and not utils.is_voice(user):
            return
        await self.callback(conn, room, user, arg)

    @classmethod
    def get_groups(cls) -> Set[str]:
        return cls._groups  # expose cls._groups as read-only

    @classmethod
    def get_pairs(
        cls, with_aliases: bool = True, group: Optional[str] = None
    ) -> Dict[str, Command]:
        """
        Returns a dictionary that maps alias strings to Command instances.
        Aliases of the same command are mapped to the same instance.
        To get a dictionary of unique commands, set with_aliases = True
        """

        if group is not None:  # restrict commands to a specific group
            if group not in cls._groups:  # save calculation time
                return dict()
            instances = [inst for inst in cls._instances if inst.group == group]
        else:  # no restrictions: entire list of commands
            instances = cls._instances

        pairs: Dict[str, Command] = dict()
        for inst in instances:
            if with_aliases:
                pairs.update({alias: inst for alias in inst.aliases})
            else:
                pairs.update({inst.name: inst})
        return pairs


def command_wrapper(
    aliases: List[str] = [],
    group: str = "misc",
    helpstr: str = "",
    is_unlisted: bool = False,
) -> Callable[[CommandFunc], Command]:
    def cls_wrapper(func: CommandFunc) -> Command:
        return Command(func, aliases, group, helpstr, is_unlisted)

    return cls_wrapper


def parametrize_room(func: CommandFunc) -> CommandFunc:
    """
    Changes the syntax of a command depending on its context:
    (1) If it's used in a room, it automatically adds its roomid at the
    beginning of arg.
    (2) If it's used in PM, it requires to specify an additional parameter
    at the beginning of arg representing a roomid.

    This way, room-dependant commands can be used in PM too without coding
    any additional logic. An example is randquote (quotes.py).
    """

    @wraps(func)
    async def wrapper(
        conn: Connection, room: Optional[str], user: str, arg: str
    ) -> None:
        if room:  # (1) command used in a room: just add the roomid param to arg
            args = arg.split(",") if arg else []
            args.insert(0, room)
        else:  # (2) command used in PM: check perms
            if not arg:
                await conn.send_pm(user, "Specifica il nome della room.")
                return

            args = arg.split(",")
            args[0] = utils.to_room_id(args[0], fallback="")  # target room
            if not args[0]:
                await conn.send_pm(user, "Specifica il nome della room.")
                return

            if (
                args[0] not in conn.rooms + conn.private_rooms  # bot in room
                or utils.to_user_id(user) not in Room.get(args[0]).users  # user in room
            ):
                # Send the same message for both errors to avoid leaking private rooms
                await conn.send_pm(user, "Sei nella room?")
                return

        arg = ",".join(args)  # update original arg
        await func(conn, room, user, arg)

    return wrapper


# --- Flask implementation ---


routes: List[Tuple[RouteFunc, str, Optional[Iterable[str]]]] = list()


def route_require_driver(func: RouteFunc) -> RouteFunc:
    @wraps(func)
    def wrapper(*args: str) -> str:
        if not utils.is_driver(session.get("_rank")):
            abort(401)
        return func(*args)

    return wrapper


def route_wrapper(
    rule: str, methods: Optional[Iterable[str]] = None, require_driver: bool = False
) -> Callable[[RouteFunc], RouteFunc]:
    def wrapper(func: RouteFunc) -> RouteFunc:
        if require_driver:
            func = route_require_driver(func)  # manual decorator binding
        routes.append((func, rule, methods))
        return func

    return wrapper


# --- Module loading and post-loading objects ---


modules = glob.glob(join(dirname(__file__), "*.py"))

for f in modules:
    if isfile(f) and not f.endswith("__init__.py"):
        name = basename(f)[:-3]
        importlib.import_module("plugins." + name)

commands = Command.get_pairs()
