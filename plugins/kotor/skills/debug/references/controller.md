# A pad button or stick that does nothing

KotOR's PC build reads keyboard and mouse; KMRP's controller module feeds the pad in. When the pad does nothing on one screen while the keyboard works, the question is where the input stops, and registration is not delivery.

## How input reaches the engine

- **Input classes**, in `keymap.2da`'s column order: 0 `ICPC` (gameplay), 1 `ICMiniGame` (Pazaak, swoop, turret), 2 `ICPCGUI` (menus), 3 `ICDialog`, 4 `ICFreeLook`, 5 `ICMovie`. A description is polled only in the classes it was added to.
- **One description per event id.** An id the keyboard or mouse already owns (`keymap.2da`'s high ids, `0xCC`…`0x11E`, and the mouse's `0x17`–`0x19`) cannot also take a pad description. The engine's own joystick descriptions are `0x03`/`0x04` (digital X/Y), `0x07`/`0x08` (analog Y/X), `0x0B`, `0x0C`/`0x0D` (sliders), added to classes 0 and 4 only.
- **What a screen reads.** The minigames build their control vector from the keyboard's axis events (`0x11A`, `0x11B`, `0x11D`, `0x11E`) in class 1 and fire on `0xD9` (Space, `MGshoot`) or `0x19` (the left mouse button); no pad event reaches either, so the pad needs a hook at the consumer (`0x00670FB0`). Conversations answer only their own previous/next events (`0x31`/`0x32`).

## Where it stops

- **Registered but never polled.** KMRP's own axes (`0x3B`/`0x3C`) are added to all six classes, and nothing in class 1 polls them. "Registered in every class" was taken to mean "works in every class" and was wrong; check the consumer, in the disassembly (`PollInput` calls with the class argument).
- **Two paths for one direction.** On a screen the engine navigates itself (conversations, character generation, a list that owns its keys) the D-pad emits the engine's direction codes and KMRP's focus layer stands down ("the engine routes it itself"); the left stick only reached the focus layer, so it did nothing. The fix is to fold the stick's latched direction into the D-pad bits so it takes the same path.
- **A press consumed by a gate.** A HUD button press goes through the engine's click handler, which returns early unless the button is drawn (`[control+0x44] & 2`), and also when a call that looks like a once-only tutorial (`0x005EDF40` with `0x20`) returns non-zero. Read the gate's state live (below) before blaming the press.

## A on someone in the world

KMRP's A, with nothing on the HUD focused, sends the engine's default-action event (`0xEF`) through `HandleInputEvent` (`0x00621210`), so the engine decides what happens, not KMRP:

- `CClientExoAppInternal::GetDefaultActions` (`0x00620620`) asks `0x0060FCC0` what kind of target it is. A creature is kind 3, which adds talk (`i_dialog`), unless its vtable's `+0x138` returns non-zero (on the client creature, `0x006170C0`: the byte at `+0x2DC` is 2) or a client timer (`0x005EE0F0`) is running; then it is kind 4, which adds only attack. The byte at `+0x2DC` is the creature's standing toward the player, sent by the server with its animation block (`0x00666A4B`) and read for the target box's colour (`0x00605D0C`: 1 green, friendly; 0 blue, neutral; 2, hostile). A blue or green target box therefore means talk is on offer.
- The talk action (`0x0060F620`) checks four more things before it asks for a conversation (`0x0062F9A0`, a field at `+0xB4`, the action object's `+0x138`, `0x0063D4B0`); they are not decoded yet.
- Then the creature's OnDialog script runs. For a companion it is `k_hen_dialogue01` → `k_ai_master`, which starts the conversation only if the creature's AI is on (local boolean 62, `SW_FLAG_AI_OFF`) and it is commandable. The game's cutscenes turn the party's AI off (`k_pman_aioff`) and back on (`k_pman_aion`); a companion out of the party when it is turned back on stays off, and A on them does nothing at all.

So when A on a creature does nothing: look at the target box's colour (hostile or not), then at the creature's state in a save ([`evidence.md`](evidence.md), "A creature's state in a save") for its AI flag and `Commandable`, before suspecting the pad.

## Watching it happen

- KMRP's `debug-logs=2` logs the pad on every change and the module's decisions, with the input class ([`evidence.md`](evidence.md)); add a log line in the module at the decision in question when it doesn't.
- Engine state is readable live from `/proc/<pid>/mem` on the device, without a debugger: follow pointers (the GUI manager at `0x007A39F4` → panel array → the panel whose vtable matches → a field) and print when values change. Read only; a probe must not change what it measures.
- A probe or a log answers "what did the engine see"; the player answers "what did it look like". Ask for both in one session: what to press, in what order, and what to note on screen.

## Choosing the mapping

When a screen needs a new binding, use the console game's: the Xbox manual's controls are the reference players expect (the swoop: A starts and shifts, the left stick steers; the turret: the left stick aims, either trigger fires). KMRP keeps an OCR of the manual under `tools/xbox-manual-ocr/`.
