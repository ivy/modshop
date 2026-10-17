"""SCRIPT.md as the game's dialogs: the grove cutscene (Scenes 1-3 and the transformation), Juhani's
defeat (Scene 5), the companions' recoveries (Scenes 6-10), their banter (Scene 11) and Carth's
epilogue. Each voiced line names the take it is cut from (voice/<take>.mp3) and, where a take holds
more than one node's worth, the transcript's phrases it spans."""

from dataclasses import dataclass, field

from dialog import GET_UP, Dialog
from voice import Line

JUHANI = "dan14_juhani"  # her tag, and the speaker of her lines in the cutscene, whose owner is an invisible object
CARTH, MISSION = "Carth", "Mission"
ARRIVED = 2  # the cutscene's entry that walks her to her mark; its reply goes on to the stasis and the fight
NEVER_MIND = 2  # Carth's reply "Never mind.", the last of each of his menus of questions
NEVER_MIND_STRREF = 2818

# The game's own lines of hers, by dialog.tlk number and voice file
DEATH = (8553, "nm14acjuha07024_")  # "I, Juhani, shall be your death!"
UNFORGIVABLE = (8531, "nm14acjuha07043_")  # "Oh, how can the Council ever take me back with what I have done? ..."
RETURN = (8545, "nm14acjuha07050_")  # "I will return to the Council, then. ..."
THANKS = (8544, "nm14acjuha07049_")  # "[Success] I... I thank you, master Jedi."; the text drops the check's tag

# Placed cameras of the grove (m14ac.git), as the game's cutscene uses them
CAMERA_HOLD, CAMERA_HORROR = 10, 9  # 10 frames her and both companions; 13, the opening wide shot, frames only ground


@dataclass
class Talk:
    """One dialog's new lines, and the voice lines they need."""

    dlg: Dialog
    prefix: dict[str, str]  # speaker -> resref prefix
    lines: list[Line] = field(default_factory=lambda: [])
    counts: dict[str, int] = field(default_factory=lambda: {})

    def say(self, who: str, take: str, text: str, first: int | None = None, last: int | None = None, **kw: object) -> int:
        """A voiced line of `who`'s (a key of `prefix`), cut from `take`; its entry's index."""
        code = self.prefix[who]
        self.counts[code] = self.counts.get(code, 0) + 1
        resref = f"oaj_{code}{self.counts[code]:02d}"
        self.lines.append(Line(resref, take, text, first, first if last is None and first is not None else last))
        speaker = kw.pop("speaker", "")
        return self.dlg.add_entry(text, vo=resref, speaker=str(speaker), **kw)  # type: ignore[arg-type]

    def go(self, *entries: int, script: str = "") -> int:
        """Each entry on to the next through a reply without text; the last reply's index."""
        reply = -1
        for a, b in zip(entries, entries[1:], strict=False):
            reply = self.dlg.add_reply(script=script)
            Dialog.link(self.dlg.entry(a), reply)
            Dialog.link(self.dlg.reply(reply), b)
        return reply

    def end(self, entry: int, *, script: str = "") -> int:
        reply = self.dlg.add_reply(script=script)
        Dialog.link(self.dlg.entry(entry), reply)
        return reply

    def choice(self, entry: int, text: str, then: int | None = None, *, active: str = "", script: str = "") -> int:
        """A reply of the player's to `entry`, leading to `then` (or ending the conversation)."""
        reply = self.dlg.add_reply(text, script=script)
        Dialog.link(self.dlg.entry(entry), reply, active=active)
        if then is not None:
            Dialog.link(self.dlg.reply(reply), then)
        return reply


def cutscene(dlg: Dialog) -> list[Line]:
    """Scenes 1-3 between her arrival and the game's stasis; after the last insult, the
    transformation in its place."""
    t = Talk(dlg, {JUHANI: "juh"})
    arrived = dlg.reply(Dialog.links(dlg.entry(ARRIVED))[0][0])
    onward = Dialog.links(arrived)

    def fight(reply: int) -> None:  # on as the game's cutscene goes: her stasis, her saber, the fight
        for index, active in onward:
            Dialog.link(dlg.reply(reply), index, active=active)

    j = {"speaker": JUHANI}
    refuge = t.say(JUHANI, "juhani-another-servant-of-the-council-have-they-sent-you",
                   "Another servant of the Jedi Council... Have they sent you to drive me from my own refuge?", **j)
    mine = t.say(JUHANI, "juhani-this-grove-is-mine-leave-now-or-you-shall",
                 "This grove is mine! Leave! Now! ...or you shall suffer the consequences.", **j)
    Dialog.unlink_all(arrived)
    Dialog.link(arrived, refuge)
    t.go(refuge, mine)
    fight(t.choice(mine, "The Council sent me to investigate the darkness in this grove."))
    fight(t.choice(mine, "I don't want to fight you. We can talk about this."))

    failed = t.say(JUHANI, "juhani-failed-you-know-nothing-of-me-nothing-of-the", "Failed?! You know nothing of me!", 0, 1, **j)
    power = t.say(JUHANI, "juhani-failed-you-know-nothing-of-me-nothing-of-the", "Nothing... of the power I possess.", 2, **j)
    t.choice(mine, "This is the great darkness the Council feared? A failed Padawan hiding in the woods?", failed)
    t.go(failed, power)
    fight(t.choice(power, "Then prove it. I'm not afraid of you."))
    apology = t.say(JUHANI, "juhani-keep-your-apology-jedi-it-changes-nothing", "Keep your apology, Jedi. It changes nothing.", **j)
    t.choice(power, "You're right. I shouldn't have said that.", apology)
    fight(t.end(apology))

    master = t.say(JUHANI, "juhani-my-master-she-i-warned-you-to-leave", "My master...? She...", 0, 1, **j)
    silence = dlg.add_entry("", speaker=JUHANI, script="k_oaj_beat")
    warned = t.say(JUHANI, "juhani-my-master-she-i-warned-you-to-leave", "I warned you to leave.", 2, **j)
    mocking = t.say(JUHANI, "juhani-you-stand-there-mocking-me-judging-me-you-think", "You stand there... mocking me? Judging me?!", 0, **j)
    powerful = t.say(JUHANI, "juhani-you-stand-there-mocking-me-judging-me-you-think", "You think yourself so powerful?!", 1, **j)
    padawan = t.say(JUHANI, "juhani-you-are-just-a-padawan-i-will-show-you", "You are just a Padawan!", 0, **j)
    show = t.say(JUHANI, "juhani-you-are-just-a-padawan-i-will-show-you", "I will show you the true meaning of power!", 1, **j)
    t.choice(power, "Your master must be proud. All that training, just to bully kath hounds.", master,
             active="k_oaj_c_cm", script="k_oaj_special")
    horror = dlg.add_entry("", script="k_oaj_cs_horror", camera=CAMERA_HOLD)
    first = dlg.add_entry("", script="k_oaj_cs_trans", camera=CAMERA_HORROR)  # Carth, Mission watching
    second = dlg.add_entry("", script="k_oaj_cs_trans", camera=CAMERA_HOLD)
    three = dlg.add_entry("", script="k_oaj_cs_draw", camera=CAMERA_HOLD)
    death = dlg.add_entry(DEATH[0], vo=DEATH[1], speaker=JUHANI)
    t.go(master, silence, warned, mocking, powerful, padawan, show, horror, first, second, three, death)
    t.end(death)  # the cutscene's EndConversation, k_pdan_juhani31, starts the fight
    return t.lines


def defeat(dlg: Dialog) -> list[Line]:
    """Scene 5, before her own opening line, once she yields after the clones' fight."""
    t = Talk(dlg, {JUHANI: "juh"})
    t.counts["juh"] = 20  # her cutscene lines are oaj_juh01..; these follow on
    what = t.say(JUHANI, "juhani-i-what-have-i-done-i-cannot-defeat-you", "I... What have I done...?", 0, 1)
    cannot = t.say(JUHANI, "juhani-i-what-have-i-done-i-cannot-defeat-you", "I cannot defeat you. I see that now.", 2, 3)
    dlg.start(what, active="k_oaj_c_defeat")
    t.go(what, cannot)
    unforgivable = dlg.add_entry(UNFORGIVABLE[0], vo=UNFORGIVABLE[1])

    know = t.say(JUHANI, "juhani-do-you-think-i-do-not-know-this-i", "Do you think I do not know this?", 0)
    tried = t.say(JUHANI, "juhani-do-you-think-i-do-not-know-this-i", "I have tried... I have tried so hard to put my past behind me.", 1)
    failure = t.say(JUHANI, "juhani-do-you-think-i-do-not-know-this-i", "But everywhere I turn, I am reminded of my failure.", 2)
    t.choice(cannot, "It's over, Juhani. You don't have to fight anymore.", know)
    t.go(know, tried, failure, unforgivable)

    wrought = t.say(JUHANI, "juhani-yes-i-see-now-what-my-anger-has-wrought", "Yes... I see now what my anger has wrought.", 0, 1)
    willingly = t.say(JUHANI, "juhani-yes-i-see-now-what-my-anger-has-wrought",
                      "I told myself that I had embraced the dark side willingly. That its power would free me from my suffering.", 2, 3)
    free = t.say(JUHANI, "juhani-yes-i-see-now-what-my-anger-has-wrought", "But I am no more free now than I was before.", 4)
    t.choice(cannot, "You let your anger control you. Look what you've done.", wrought)
    t.go(wrought, willingly, free, unforgivable)

    mock = t.say(JUHANI, "juhani-must-you-continue-to-mock-me-even-now-i", "Must you continue to mock me... even now?", 0)
    prove = t.say(JUHANI, "juhani-must-you-continue-to-mock-me-even-now-i", "I have nothing left to prove to you.", 1)
    t.choice(cannot, "So much for all that power.", mock)
    t.go(mock, prove, unforgivable)

    compassion = t.say(JUHANI, "juhani-you-would-still-offer-me-compassion-after-everything-i",
                       "You would still offer me compassion? After everything I have done?", 0, 1)
    this = t.say(JUHANI, "juhani-you-would-still-offer-me-compassion-after-everything-i", "Even after this...?", 2)
    hope = t.say(JUHANI, "juhani-then-perhaps-perhaps-there-is-still-hope-for-me", "Then... perhaps... perhaps there is still hope for me.")
    back = dlg.add_entry(RETURN[0], vo=RETURN[1], script="k_pdan_juhani12")  # the game's: redeemed, she will join you
    thanks = dlg.add_entry("I... I thank you, master Jedi.", vo=THANKS[1], quest=("dan_trials", 45))
    t.choice(unforgivable, "You made a terrible mistake. That doesn't mean you can't make things right.", compassion)
    t.choice(unforgivable, "The dark side wants you to believe there's no way back.", compassion)
    t.go(compassion, this)
    t.choice(this, "Especially after this. You still have a choice.", hope)
    t.go(hope, back, thanks)
    t.end(thanks, script="k_pdan_14juh_01")  # the game's: she leaves the grove for the Enclave

    right = t.say(JUHANI, "juhani-perhaps-you-are-right-but-i-will-not-remain",
                  "Perhaps you are right. But I will not remain here, surrendering myself to this darkness.", 0, 1)
    face = t.say(JUHANI, "juhani-perhaps-you-are-right-but-i-will-not-remain", "I must face what I have done.", 2,
                 script="k_pdan_juhani12", quest=("dan_trials", 45))
    t.choice(unforgivable, "Perhaps you don't deserve their forgiveness.", right, script="k_act_darkmed")
    t.go(right, face)
    t.end(face, script="k_pdan_14juh_01")
    return t.lines


def mission(dlg: Dialog) -> list[Line]:
    """Scene 6, first in her own conversation while she is down."""
    t = Talk(dlg, {MISSION: "mis"})
    head = t.say(MISSION, "mission-oh-my-head", "Ow! My head...", anims=((MISSION, GET_UP),))
    dlg.start(head, active="k_oaj_c_down")
    think = t.say(MISSION, "mission-yeah-i-think-so-what-happened-fuzzy", "Yeah... yeah, I think so?", 0)
    fuzzy = t.say(MISSION, "mission-yeah-i-think-so-what-happened-fuzzy", "What the heck happened? ...everything's kinda fuzzy...", 1)
    again = t.say(MISSION, "mission-whatever-it-was-i-dont-want-to-do-it", "Ughh... whatever that was... I don't wanna do it again.")
    okay = t.say(MISSION, "mission-ill-be-ok-trust-me-but-carth-maybe-you", "I'll be okay. Trust me.", 0)
    check = t.say(MISSION, "mission-ill-be-ok-trust-me-but-carth-maybe-you", "But Carth...? Maybe you should go check on him...", 1)
    t.choice(head, "Mission! Are you okay?", think)
    t.go(think, fuzzy, again, okay)
    up = t.end(okay, script="k_oaj_up")
    Dialog.link(dlg.reply(up), check, active="k_oaj_c_cardn")  # not once he's already up beside her
    t.end(check)
    return t.lines


def carth(dlg: Dialog) -> list[Line]:
    """Scenes 7-10, first in his own conversation while he is down, and the epilogue's question in
    each of his menus."""
    t = Talk(dlg, {CARTH: "car"})
    fine = t.say(CARTH, "carth-before-you-say-anything-im-fine", "Before you say anything, I'm fine.", anims=((CARTH, GET_UP),))
    dlg.start(fine, active="k_oaj_c_down")

    # Scene 8, which every opening reaches
    aside = t.say(CARTH, "carth-look-all-joking-aside-i-dont-like-this", "Look, all joking aside... I don't like this.")
    waved = t.say(CARTH, "carth-that-jedi-back-there-she-just-waved-her-hand",
                  "That Jedi back there. She just waved her hand, and suddenly I wasn't myself anymore. I couldn't move. "
                  "Couldn't speak. I couldn't even stop myself from attacking you.")
    strange = t.say(CARTH, "carth-ive-seen-some-pretty-strange-things-since-joining-up",
                    "I've seen some pretty strange things since joining up with you... But this? I-I don't know... "
                    "Something about... having your own mind turned against you...")
    t.choice(aside, "Don't like what?", waved)
    t.go(waved, strange)

    # Branch 1: concern
    minute = t.say(CARTH, "carth-yeah-yeah-im-fine-just-just-give-me-a", "Yeah. Yeah, I'm fine. Just... give me a minute, all right?")
    eyes = t.say(CARTH, "carth-you-think-one-moment-im-standing-here-minding-my",
                 "You think? One moment I'm standing here, minding my own business, and the next I'm looking at myself through someone else's eyes.")
    worst = t.say(CARTH, "carth-and-you-want-to-know-the-worst-part-i",
                  "And you want to know the worst part? I could see everything. I knew exactly what was happening, but I couldn't do a damn thing about it.")
    t.choice(fine, "I was just going to ask if you're all right.", minute)
    t.choice(minute, "That looked pretty unpleasant.", eyes)
    t.go(eyes, worst, aside)

    # Branch 2: what happened?
    training = t.say(CARTH, "carth-how-should-i-know-jedi-training", "How should I know? You're the one with all the Jedi training.")
    reassuring = t.say(CARTH, "carth-well-thats-reassuring", "Well, that's reassuring.")
    remember = t.say(CARTH, "carth-look-i-remember-what-happened-i-remember-trying-to",
                     "Look, I remember what happened. I remember trying to move, trying to tell you something... "
                     "But it was like somebody else was making all the decisions.")
    t.choice(fine, "Carth, what in the galaxy just happened to you?", training)
    t.choice(training, "I've never seen anything like that before.", reassuring)
    t.go(reassuring, remember, aside)

    # Branch 3: the ears
    dont = t.say(CARTH, "carth-dont", "Don't.")
    seriously = t.say(CARTH, "carth-do-you-ever-take-anything-seriously", "Do you ever take anything seriously?")
    enjoying = t.say(CARTH, "carth-yeah-well-im-glad-somebodys-enjoying-themselves-right-now",
                     "Yeah, well, I'm glad somebody's enjoying themselves right now.")
    tail = t.say(CARTH, "carth-i-know-about-the-tail", "I KNOW ABOUT THE TAIL!")
    forget = t.say(CARTH, "carth-can-we-please-just-forget-this-ever-happened", "Can we please just forget this ever happened?")
    t.choice(fine, "You know, the ears actually suited you.", dont)
    t.choice(dont, "I'm serious. Very distinguished.", seriously)
    t.choice(dont, "Sorry. Couldn't resist.", enjoying)
    t.choice(dont, "You even had the tail.", tail)
    t.go(seriously, aside)
    t.go(enjoying, aside)
    t.go(tail, forget, aside)

    # Branch 4: the hissing
    no = t.say(CARTH, "carth-what-no", "What? No!")
    control = t.say(CARTH, "carth-well-i-wasnt-exactly-in-control-of-myself-was", "Well, I wasn't exactly in control of myself, was I?")
    admit = t.say(CARTH, "carth-i-didnt-admit-anything", "I didn't admit anything!")
    think = t.say(CARTH, "carth-well-thanks-i-think", "Well, thanks. I think.")
    finished = t.say(CARTH, "carth-very-funny-are-you-finished", "Very funny. Are you finished?")
    t.choice(fine, "Did you just hiss at me?", no)
    t.choice(no, "I'm pretty sure you hissed.", control)
    t.choice(control, "So you admit you hissed.", admit)
    t.choice(control, "It's all right, Carth. I understand.", think)
    t.choice(control, "Should I be worried about you scratching the furniture?", finished)
    for answer in (admit, think, finished):
        t.go(answer, aside)

    # Scene 9, which every answer to Scene 8 reaches
    chance = t.say(CARTH, "carth-look-im-not-saying-she-doesnt-deserve-another-chance",
                   "Look... I'm not saying she doesn't deserve another chance. I'm just saying... "
                   "I'd feel a lot better if she kept those powers to herself.")
    wish = t.say(CARTH, "carth-yeah-thanks-i-just-wish-there-was-something-we",
                 "Yeah... Thanks. I just wish there was something we could do to keep it from happening again.")
    t.choice(strange, "I understand. Nobody should have to experience that.", wish)
    t.go(wish, chance)
    suppose = t.say(CARTH, "carth-no-i-dont-suppose-you-did-but-you-just",
                    "No, I don't suppose you did. But you just couldn't leave it alone, could you?")
    done = t.say(CARTH, "carth-yeah-well-whats-done-is-done", "Yeah... Well, what's done is done.")
    insulting = t.say(CARTH, "carth-and-you-thought-insulting-her-would-make-things-better",
                      "And you thought insulting her would make things better?")
    funny = t.say(CARTH, "carth-funny-you-know-what-forget-it-i-dont-even", "Funny?! You know what? Forget it! I don't even know why I bother.")
    t.choice(strange, "Well, I didn't exactly expect her to do that.", suppose)
    t.choice(suppose, "You're right. I'm sorry.", done)
    t.choice(suppose, "She was threatening us!", insulting)
    t.choice(suppose, "Oh, come on. That was pretty funny.", funny)
    for answer in (done, insulting, funny):
        t.go(answer, chance)
    survived = t.say(CARTH, "carth-thats-what-you-took-away-from-all-this-look",
                     "That's what you took away from all this? Look, just because we survived doesn't mean nothing happened! Forget it.")
    t.choice(strange, "Come on, Carth. We won, didn't we?", survived)
    t.go(survived, chance)
    rich = t.say(CARTH, "carth-oh-thats-rich-id-like-to-see-you-try",
                 "Oh, that's rich! I'd like to see you try resisting when somebody takes control of your entire body!")
    bother = t.say(CARTH, "carth-you-know-what-forget-it-i-dont-know-why", "You know what? Forget it! I don't know why I even bother.")
    t.choice(strange, "You were weak. You should've resisted.", rich)
    t.go(rich, bother, chance)

    # Scene 10, and the answers to Scene 9
    enough = t.say(CARTH, "carth-look-i-appreciate-you-checking-up-on-me-but",
                   "Look, I appreciate you checking up on me. But I've had enough of this for one day. I don't want to talk about it.")
    t.end(enough, script="k_oaj_up")
    maybe = t.say(CARTH, "carth-maybe-but-that-doesnt-change-what-happened", "Maybe. But that doesn't change what happened.")
    capable = t.say(CARTH, "carth-i-know-the-jedi-believe-in-redemption-and-maybe",
                    "I know the Jedi believe in redemption. And maybe they're right. I just hope she understands what she's capable of.")
    t.choice(chance, "Juhani wasn't herself either. The dark side was controlling her.", maybe)
    t.go(maybe, capable, enough)
    worries = t.say(CARTH, "carth-yeah-thats-what-worries-me-how-exactly-do-you",
                    "Yeah. That's what worries me. How exactly do you prepare for something like that?")
    t.choice(chance, "We'll be more careful next time.", worries)
    t.go(worries, enough)
    nothing = t.say(CARTH, "carth-no-nothing", "No. Nothing.")
    concern = t.say(CARTH, "carth-look-i-appreciate-the-concern-really-but-i-dont",
                    "Look, I appreciate the concern. Really. But... I don't want to talk about it.")
    t.choice(chance, "Carth, is there something else bothering you?", nothing)
    t.go(nothing, concern)
    t.end(concern, script="k_oaj_up")  # its own ending, not Scene 10's, which opens the same way

    # The epilogue, before "Never mind." in every menu of his questions
    if dlg.reply(NEVER_MIND).get_locstring("Text").stringref != NEVER_MIND_STRREF:
        raise SystemExit("Carth's dialog has moved its \"Never mind.\"; the epilogue's place is unknown")
    absolutely = t.say(CARTH, "carth-no-absolutely-not", "No. Absolutely not.")
    again = t.say(CARTH, "carth-absolutely-not", "Absolutely not.")
    t.choice(absolutely, "But--", again)
    t.end(again)
    ask = dlg.add_reply("About what happened on Dantooine...")
    Dialog.link(dlg.reply(ask), absolutely)
    menus = [i for i in range(len(dlg.entries())) if any(index == NEVER_MIND for index, _ in Dialog.links(dlg.entry(i)))]
    for menu in menus:
        links = Dialog.links(dlg.entry(menu))
        Dialog.link(dlg.entry(menu), ask, active="k_oaj_c_done", at=[index for index, _ in links].index(NEVER_MIND))
    return t.lines


def banter(dlg: Dialog) -> list[Line]:
    """Scene 11: Mission and Carth, the player listening."""
    t = Talk(dlg, {MISSION: "mis", CARTH: "car"})
    t.counts["mis"], t.counts["car"] = 20, 60  # after their recoveries' lines
    m, c = {"speaker": MISSION, "listener": CARTH}, {"speaker": CARTH, "listener": MISSION}
    lines = [
        t.say(MISSION, "mission-hey-carth", "Hey, Carth?", **m),
        t.say(CARTH, "carth-what-is-it-mission", "What is it, Mission?", **c),
        t.say(MISSION, "mission-does-this-mean-youre-part-cathar-now", "Does this mean you're part Cathar now?", **m),
        t.say(CARTH, "carth-no-mission", "No, Mission.", **c),
        t.say(MISSION, "mission-cause-i-was-thinking-you-were-kind-of-cute", "'Cause I was thinking you were kinda cute with those little--", **m),
        t.say(CARTH, "carth-mission-shout", "Mission.", **c),
        t.say(MISSION, "mission-what-im-just-saying", "What?! I'm just saying!", **m),
        t.say(CARTH, "carth-can-we-please-just-get-going", "Can we PLEASE just get going?", **c),
        t.say(MISSION, "mission-all-right-already-sheesh", "All right, already! Sheesh!", **m),
        dlg.add_entry("", speaker=MISSION, script="k_oaj_beat"),  # keep the pause; don't rush her last line
        t.say(MISSION, "mission-meow-meow-carth", "Meow, meow, Carth.", **m),
        t.say(CARTH, "carth-oh-thats-real-mature", "Oh, that's real mature.", **c),
    ]
    dlg.start(lines[0])
    t.go(*lines)
    t.end(lines[-1])
    return t.lines
