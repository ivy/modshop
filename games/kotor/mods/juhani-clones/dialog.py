"""Adding to a dialog the build already has: new entries and replies go at the ends of its lists, so
every index the dialog (or another mod's change to it) already uses stays where it is."""

from pykotor.common.language import LocalizedString
from pykotor.common.misc import ResRef
from pykotor.resource.formats.gff import GFFList, GFFStruct, bytes_gff, read_gff

NO_DELAY = 0xFFFFFFFF  # the node lasts as long as its voice line, or until the player goes on
CAMERA_STATIC = 6  # CameraAngle: the module's placed camera named by CameraID (the .git's CameraList)
GET_UP = 10055  # dialog animation: up from ANIMATION_LOOPING_PRONE, as banter.dlg gets Mission up


class Dialog:
    def __init__(self, data: bytes) -> None:
        self.gff = read_gff(data)
        self.root = self.gff.root

    @classmethod
    def empty_like(cls, data: bytes) -> "Dialog":
        """A dialog with `data`'s settings (conversation type, skippable, ...) and no lines."""
        dlg = cls(data)
        for name in ("EntryList", "ReplyList", "StartingList"):
            dlg.root.set_list(name, GFFList())
        for name in ("EndConversation", "EndConverAbort"):
            dlg.root.set_resref(name, ResRef(""))
        return dlg

    def entries(self) -> GFFList:
        return self.root["EntryList"]

    def replies(self) -> GFFList:
        return self.root["ReplyList"]

    def entry(self, i: int) -> GFFStruct:
        return self.entries().at(i)

    def reply(self, i: int) -> GFFStruct:
        return self.replies().at(i)

    def _node(self, nodes: GFFList, text: str | int, links: str, *, vo: str, script: str, listener: str) -> GFFStruct:
        node = nodes.add(len(nodes))
        node.set_list("AnimList", GFFList())
        if isinstance(text, int):
            node.set_locstring("Text", LocalizedString(text))  # the game's own line, by its dialog.tlk number
        else:
            node.set_locstring("Text", LocalizedString.from_english(text) if text else LocalizedString.from_invalid())
        node.set_resref("VO_ResRef", ResRef(vo))
        node.set_resref("Script", ResRef(script))
        node.set_uint32("Delay", NO_DELAY)
        node.set_string("Comment", "Oops! All Juhani")
        node.set_resref("Sound", ResRef(""))
        node.set_string("Quest", "")
        node.set_int32("PlotIndex", -1)
        node.set_single("PlotXPPercentage", 1.0)
        node.set_string("Listener", listener)
        node.set_uint32("WaitFlags", 0)
        node.set_uint32("CameraAngle", 0)
        node.set_uint8("FadeType", 0)
        node.set_list(links, GFFList())
        return node

    def add_entry(
        self,
        text: str | int,
        *,
        speaker: str = "",
        vo: str = "",
        script: str = "",
        listener: str = "",
        anims: tuple[tuple[str, int], ...] = (),
        quest: tuple[str, int] | None = None,
        camera: int | None = None,
    ) -> int:
        """A line of an NPC's (`speaker`'s tag, or the dialog's owner), as its index. `anims` are
        (participant's tag, dialog animation); `quest` a journal entry; `camera` a placed camera."""
        node = self._node(self.entries(), text, "RepliesList", vo=vo, script=script, listener=listener)
        node.set_string("Speaker", speaker)
        node.set_uint8("SoundExists", 1 if vo else 0)
        for participant, animation in anims:
            anim = node["AnimList"].add(len(node["AnimList"]))
            anim.set_string("Participant", participant)
            anim.set_uint16("Animation", animation)
        if quest is not None:
            node.set_string("Quest", quest[0])
            node.set_uint32("QuestEntry", quest[1])
        if camera is not None:
            node.set_uint32("CameraAngle", CAMERA_STATIC)
            node.set_int32("CameraID", camera)
            node.set_int32("CamVidEffect", -1)
        return len(self.entries()) - 1

    def add_reply(self, text: str = "", *, script: str = "") -> int:
        """A line of the player's, as its index; without text, the conversation just goes on."""
        self._node(self.replies(), text, "EntriesList", vo="", script=script, listener="")
        return len(self.replies()) - 1

    @staticmethod
    def _links(node: GFFStruct) -> GFFList:
        return node["RepliesList"] if node.exists("RepliesList") else node["EntriesList"]

    @classmethod
    def link(cls, node: GFFStruct, index: int, *, active: str = "", at: int | None = None) -> None:
        """From an entry to a reply, or a reply to an entry; `active` is the condition script, `at`
        the place among the node's links (the end by default)."""
        links = cls._links(node)
        link = GFFStruct(len(links))
        link.set_uint32("Index", index)
        link.set_resref("Active", ResRef(active))
        link.set_uint8("IsChild", 0)
        links.insert(len(links) if at is None else at, link)

    @classmethod
    def links(cls, node: GFFStruct) -> list[tuple[int, str]]:
        return [(link.get_uint32("Index"), str(link.get_resref("Active"))) for link in cls._links(node)]

    @staticmethod
    def unlink_all(node: GFFStruct) -> None:
        node.set_list("RepliesList" if node.exists("RepliesList") else "EntriesList", GFFList())

    def start(self, entry: int, *, active: str = "") -> None:
        """A way in, tried before the dialog's own."""
        starts: GFFList = self.root["StartingList"]
        link = GFFStruct(len(starts))
        link.set_uint32("Index", entry)
        link.set_resref("Active", ResRef(active))
        starts.insert(0, link)

    def __bytes__(self) -> bytes:
        return bytes(bytes_gff(self.gff))
