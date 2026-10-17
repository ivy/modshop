-- Oops! All Juhani: the grove cutscene and its transformation, the fight with her clones, the
-- companions down and back up, and the flags the dialogs read.

local DAMAGED = 22  -- SW_FLAG_EVENT_ON_DAMAGED
local YIELDED = 4   -- SW_PLOT_BOOLEAN_05, set when she surrenders
local AI_OFF = 62   -- SW_FLAG_AI_OFF
local HIDDEN = 529  -- the appearance row make.py adds; the test's k_oaj_gen.nss says the same
local NPC_BASTILA, NPC_CARTH, NPC_MISSION = 0, 2, 6
local TIRED, HORROR, PRONE = 12, 18, 23  -- ANIMATION_LOOPING_PAUSE_TIRED, _HORROR, _PRONE
local FORCE_HOLD = 29
local NEUTRAL, HOSTILE = 5, 1

-- The party routines and effects the world model doesn't answer: the party is the world's lists,
-- and `effects` counts each creature's effects by id, every one of them Juhani's.
local function party(w, members, effects)
  w.engine.RemovePartyMember = function(npc)
    local o = members[npc]
    local kept = {}
    for _, m in ipairs(w.party) do
      if m ~= o then kept[#kept + 1] = m end
    end
    w.party = kept
    local npcs = {}
    for _, n in ipairs(w.npc_party) do
      if n ~= npc then npcs[#npcs + 1] = n end
    end
    w.npc_party = npcs
    return 1
  end
  w.engine.AddPartyMember = function(npc)
    local p, n = w.party, w.npc_party
    p[#p + 1] = members[npc]
    n[#n + 1] = npc
    w.party, w.npc_party = p, n
    return 1
  end
  local walking, at = nil, 0  -- the creature whose effects a script is walking, and how far
  w.engine.GetFirstEffect = function(o)
    walking, at = o.id, 1
  end
  w.engine.GetNextEffect = function()
    at = at + 1
  end
  w.engine.GetIsEffectValid = function()
    return at <= (effects[walking] or 0) and 1 or 0
  end
  w.engine.ApplyEffectToObject = function(_, _, o)
    effects[o.id] = (effects[o.id] or 0) + 1
  end
  w.engine.RemoveEffect = function(o)
    effects[o.id] = effects[o.id] - 1
  end
  -- 0 is OBJECT_SELF as the bytecode holds it: nws compares objects by that id, so its creator is
  -- given as OBJECT_SELF itself, not as the object it stands for
  w.engine.GetEffectCreator = function() return 0 end
end

-- The grove with the party in it: Carth and Mission, as the special path needs; Bastila left on
-- the Hawk.
local function grove()
  local w = nws.world()
  local area = w:create("area", "danm14ac")
  local pc = w:create("creature", "player", { is_pc = true, area = area })
  -- tagged as the grove has them, in lower case, unlike their blueprints' "Carth" and "Mission"
  local carth = w:create("creature", "carth", { area = area, position = { x = 430, y = 378, z = 62 } })
  local mission = w:create("creature", "mission", { area = area, position = { x = 432, y = 376, z = 62 } })
  local juhani = w:create("creature", "dan14_juhani", { area = area, hp = 150, max_hp = 150 })
  w:create("creature", "dan14ac_cutobj01", { area = area })
  w:create("creature", "dan14ac_cutobj02", { area = area })
  w:create("creature", "Bastila", { area = w:create("area", "ebo_m12aa") })
  w.party = { pc, carth, mission }
  w.npc_party = { NPC_CARTH, NPC_MISSION }
  w.self = juhani
  juhani:set_local(DAMAGED, true)
  local effects = { [carth.id] = 0, [mission.id] = 0 }
  party(w, { [NPC_CARTH] = carth, [NPC_MISSION] = mission }, effects)
  return w, pc, carth, mission, juhani, effects
end

-- After the transformation: both down, hidden by one effect each, and two clones standing.
local function transformed(w, carth, mission, effects)
  w.party = { w.party[1] }
  w.npc_party = {}
  w.globals.OAJ_SPECIAL = true
  w.globals.OAJ_DOWN_2 = true
  w.globals.OAJ_DOWN_6 = true
  effects[carth.id], effects[mission.id] = 1, 1
  return { w:create("creature", "oaj_juhani1"), w:create("creature", "oaj_juhani2") }
end

-- Her hit points at each half-second watch: each tick is { hp, down }, down meaning both clones
-- have been beaten by then; the last tick repeats.
local function watch(w, clones, ticks)
  local watches = 0
  w.engine.GetCurrentHitPoints = function()
    watches = watches + 1
    local tick = ticks[math.min(watches, #ticks)]
    if tick.down then
      clones[1].dead, clones[2].dead = true, true
    end
    return tick.hp
  end
end

-- The player's distance from a companion lying down, at each look; the last repeats.
local function walk(w, distances)
  local looks = 0
  w.engine.GetDistanceBetween = function()
    looks = looks + 1
    return distances[math.min(looks, #distances)]
  end
end

local function count(run, name, first)
  local n = 0
  for _, call in ipairs(run:calls(name)) do
    if first == nil or call.args[1] == first then n = n + 1 end
  end
  return n
end

describe("k_pdan_14juh_d: her user-defined events, decompiled", function()
  local script = nws.script("k_pdan_14juh_d")

  for _, case in ipairs({ { event = 30, member = 2 }, { event = 40, member = 3 } }) do
    it("in the cutscene's event " .. case.event .. ", holds a companion in stasis, as in the game", function()
      local w = grove()
      local member = w.party[case.member]
      w.user_event = case.event
      local run = script:run(w)
      assert.called(run, "ActionCastFakeSpellAtObject", FORCE_HOLD, member)
      assert.called(run, "EffectCutSceneParalyze")
      assert.called(run, "ApplyEffectToObject", 2, nws.any, member)
    end)
  end

  it("walks to her mark without the battlecry, which would speak over her lines", function()
    local w = grove()
    w.user_event = 10
    local run = script:run(w)
    assert.called(run, "ActionMoveToObject")
    assert.not_called(run, "EventUserDefined", 110)
  end)
end)

describe("k_pdan_juhani31: the grove cutscene ends", function()
  local script = nws.script("k_pdan_juhani31")

  it("after the game's choices, starts the game's fight, with her battlecry and no clones", function()
    local w, _, _, _, juhani = grove()
    local run = script:run(w)
    assert.called(run, "EventUserDefined", 110)
    assert.called(run, "SignalEvent", juhani)
    assert.called(run, "EventUserDefined", 80)
    assert.not_called(run, "ExecuteScript")
  end)

  it("after the last insult, starts the clones' fight, her own line already spoken", function()
    local w, _, _, _, juhani = grove()
    w.globals.OAJ_SPECIAL = true
    local run = script:run(w)
    assert.not_called(run, "EventUserDefined", 110)
    assert.called(run, "EventUserDefined", 80)
    assert.called(run, "ExecuteScript", "k_oaj_fight", juhani)
  end)
end)

describe("the cutscene's last insult", function()
  it("is offered only with Carth and Mission in the party", function()
    local script = nws.script("k_oaj_c_cm")
    local w = grove()
    assert.is_true(script:conditional(w).result)
    w.npc_party = { NPC_CARTH }
    assert.is_false(script:conditional(w).result)
  end)

  it("marks the fight as the clones'", function()
    local w = grove()
    nws.script("k_oaj_special"):run(w)
    assert.is_true(w.globals.OAJ_SPECIAL)
  end)
end)

describe("the transformation", function()
  it("has the three of them draw their sabers", function()
    local w, _, carth, mission, _, effects = grove()
    transformed(w, carth, mission, effects)
    local run = nws.script("k_oaj_cs_draw"):run(w)
    assert.equal(3, #run:calls("ActionEquipMostDamagingMelee"))
  end)

  it("has both companions clutch their heads as she casts, by animation, with no stasis or effect", function()
    local w, _, carth, mission, _, effects = grove()
    local run = nws.script("k_oaj_cs_horror"):run(w)
    assert.called(run, "ActionPauseConversation")
    assert.called(run, "ActionCastFakeSpellAtObject", 16, carth)  -- FORCE_POWER_FEAR
    assert.equal(2, count(run, "ActionPlayAnimation", HORROR))
    assert.equal(0, effects[carth.id])
    assert.equal(0, effects[mission.id])
    assert.not_called(run, "EffectCutSceneParalyze")
    assert.not_called(run, "EffectCutSceneHorrified")
    assert.called_before(run, "ActionPauseConversation", "ActionResumeConversation")
  end)

  it("turns Carth first, then Mission, each hidden in place and out of the party, a neutral clone on their spot", function()
    local w, _, carth, mission, _, effects = grove()
    local clones = { w:create("creature", "oaj_juhani1"), w:create("creature", "oaj_juhani2") }
    w.engine.CreateObject = function(_, template)
      return template == "oaj_juhani1" and clones[1] or clones[2]
    end
    local trans = nws.script("k_oaj_cs_trans")
    local first = trans:run(w)
    assert.called(first, "RemovePartyMember", NPC_CARTH)
    assert.not_called(first, "RemovePartyMember", NPC_MISSION)
    assert.called(first, "CreateObject", nws.any, "oaj_juhani1")
    assert.is_true(w.globals.OAJ_DOWN_2)
    local second = trans:run(w)
    assert.called(second, "RemovePartyMember", NPC_MISSION)
    assert.called(second, "CreateObject", nws.any, "oaj_juhani2")
    assert.is_true(w.globals.OAJ_DOWN_6)
    for _, run in ipairs({ first, second }) do
      assert.called_before(run, "RemovePartyMember", "EffectDisguise")  -- leaving the party undoes a disguise put on before
      assert.called(run, "EffectDisguise", HIDDEN)
      assert.called(run, "ChangeToStandardFaction", nws.any, NEUTRAL)
      assert.not_called(run, "ChangeToStandardFaction", nws.any, HOSTILE)
      assert.not_called(run, "JumpToLocation")
      assert.called(run, "SetLocalBoolean", nws.any, DAMAGED, 0)
    end
    assert.equal(1, effects[carth.id], "hidden by one effect")
    assert.equal(1, effects[mission.id])
    assert.equal(1, #w.party)
  end)

  it("brings a companion back, held as they were, when their clone can't be made", function()
    local w, _, carth, _, _, effects = grove()
    local run = nws.script("k_oaj_cs_trans"):run(w)  -- CreateObject unanswered: no clone
    assert.called(run, "AddPartyMember", NPC_CARTH)
    assert.is_false(w.globals.OAJ_DOWN_2 or false)
    assert.equal(1, effects[carth.id], "her stasis, as before the hiding")
    assert.not_called(run, "SetLocalBoolean", nws.any, DAMAGED, 0)
  end)
end)

describe("k_oaj_fight", function()
  local script = nws.script("k_oaj_fight")

  it("turns the clones on the player, each drawing her saber first", function()
    local w, pc, carth, mission, _, effects = grove()
    local clones = transformed(w, carth, mission, effects)
    watch(w, clones, { { hp = 150 }, { hp = 40, down = true } })
    walk(w, { 30 })
    local run = script:run(w)
    assert.called(run, "ChangeToStandardFaction", clones[1], HOSTILE)
    assert.called(run, "ChangeToStandardFaction", clones[2], HOSTILE)
    assert.called_before(run, "ActionEquipMostDamagingMelee", "ActionAttack")
    assert.called(run, "ActionAttack", pc)
  end)

  it("stands her down below 50 while a clone stands, and ends the fight once they fall", function()
    local w, _, carth, mission, juhani, effects = grove()
    local clones = transformed(w, carth, mission, effects)
    watch(w, clones, { { hp = 150 }, { hp = 40 }, { hp = 40 }, { hp = 40, down = true } })
    walk(w, { 5 })  -- the player stays beside the companions
    local run = script:run(w)
    assert.called(run, "SetLocalBoolean", juhani, AI_OFF, 1)
    assert.called(run, "ChangeToStandardFaction", juhani, NEUTRAL)
    assert.equal(1, count(run, "ActionPlayAnimation", TIRED), "she stands down once")
    assert.is_true(clones[1].destroyed)
    assert.is_true(clones[2].destroyed)
    assert.called_before(run, "SetIsDestroyable", "DestroyObject")
    assert.called(run, "SetLocalBoolean", juhani, AI_OFF, 0)
    assert.called(run, "SetLocalBoolean", juhani, DAMAGED, 1)
    assert.called(run, "EventUserDefined", 1006)
    -- seen again where they were hidden, free, lying unconscious out of the party
    assert.equal(0, effects[carth.id])
    assert.equal(0, effects[mission.id])
    assert.equal(2, count(run, "ActionPlayAnimation", PRONE))
    -- their AI back on, which the cutscene's trigger turned off and her yield turns on only for the party
    assert.equal(2, #run:calls("ExecuteScript"))
    assert.called(run, "ExecuteScript", "k_pman_aion")
    local aion, prone
    for i, call in ipairs(run.trace) do
      if call.name == "ExecuteScript" and not aion then aion = i end
      if call.name == "ActionPlayAnimation" and call.args[1] == PRONE and not prone then prone = i end
    end
    assert(aion and prone and aion < prone, "AI on before lying down")
    assert.not_called(run, "AddPartyMember")
    assert.not_called(run, "JumpToLocation")
  end)

  it("takes every effect of hers off them, not just the first", function()
    local w, _, carth, mission, _, effects = grove()
    local clones = transformed(w, carth, mission, effects)
    effects[carth.id], effects[mission.id] = 3, 2
    watch(w, clones, { { hp = 40, down = true } })
    walk(w, { 5 })
    script:run(w)
    assert.equal(0, effects[carth.id])
    assert.equal(0, effects[mission.id])
  end)

  it("clears her stand-down before she yields, so her conversation is not queued behind it", function()
    local w, _, carth, mission, _, effects = grove()
    local clones = transformed(w, carth, mission, effects)
    watch(w, clones, { { hp = 40 }, { hp = 40, down = true } })
    walk(w, { 5 })
    local run = script:run(w)
    local tired, cleared, signal
    for i, call in ipairs(run.trace) do
      if call.name == "ActionPlayAnimation" and call.args[1] == TIRED then tired = i end
      if call.name == "ClearAllActions" and tired and not signal then cleared = i end
      if call.name == "SignalEvent" then signal = i end
    end
    assert(tired, "she stood down first")
    assert(signal and cleared and tired < cleared and cleared < signal, "ClearAllActions after the stand-down, then SignalEvent")
  end)

  it("leaves the bodies down and fights on while she is above 50", function()
    local w, _, carth, mission, juhani, effects = grove()
    local clones = transformed(w, carth, mission, effects)
    watch(w, clones, { { hp = 150, down = true }, { hp = 120, down = true }, { hp = 40, down = true } })
    walk(w, { 30 })
    local run = script:run(w)
    assert.equal(3, #run:calls("GetCurrentHitPoints"), "the fight ends at the first watch below 50")
    assert.not_called(run, "SetLocalBoolean", juhani, AI_OFF, 1)
    assert.called(run, "EventUserDefined", 1006)
  end)

  -- Each rejoins from their own context, as OBJECT_SELF, which nws records as itself: the NPC
  -- number says who.
  it("brings each back to the party once the player walks away from them", function()
    local w, _, carth, mission, _, effects = grove()
    local clones = transformed(w, carth, mission, effects)
    w.globals.DAN_JUHANI_PLOT = 3
    watch(w, clones, { { hp = 40, down = true } })
    walk(w, { 5, 5, 5, 5, 40 })
    local run = script:run(w)
    assert.called(run, "AddPartyMember", NPC_CARTH)
    assert.called(run, "AddPartyMember", NPC_MISSION)
    assert.not_called(run, "AddPartyMember", NPC_BASTILA)
    assert.equal(3, #w.party)
    assert.is_false(w.globals.OAJ_DOWN_2)
    assert.is_false(w.globals.OAJ_DOWN_6)
    assert(#run:calls("GetDistanceBetween") >= 5, "not before the player is far enough away")
  end)

  it("leaves the recovery to the player's click, starting no conversation itself", function()
    local w, _, carth, mission, _, effects = grove()
    local clones = transformed(w, carth, mission, effects)
    w.globals.DAN_JUHANI_PLOT = 3
    watch(w, clones, { { hp = 40, down = true } })
    walk(w, { 2 })
    assert.not_called(script:run(w), "ActionStartConversation")
  end)

  it("keeps them down while her own conversation is still to come, however far the player is", function()
    local w, _, carth, mission, _, effects = grove()
    local clones = transformed(w, carth, mission, effects)
    watch(w, clones, { { hp = 40, down = true } })
    local looks = 0
    w.engine.GetDistanceBetween = function()
      looks = looks + 1
      if looks > 20 then w.globals.DAN_JUHANI_PLOT = 3 end  -- she leaves for the Enclave
      return 40
    end
    local run = script:run(w)
    assert.called(run, "AddPartyMember", NPC_CARTH)
    assert(looks > 20, "not before she is done")
  end)

  it("does nothing once she has yielded", function()
    local w, _, carth, mission, juhani, effects = grove()
    local clones = transformed(w, carth, mission, effects)
    juhani:set_local(YIELDED, true)
    watch(w, clones, { { hp = 40, down = true } })
    assert.not_called(script:run(w), "EventUserDefined", 1006)
  end)
end)

describe("after the fight", function()
  it("opens her defeat once, in place of her own opening line, only after the clones' fight", function()
    local cond = nws.script("k_oaj_c_defeat")
    local w = grove()
    assert.is_false(cond:conditional(w).result)
    w.globals.OAJ_SPECIAL = true
    assert.is_true(cond:conditional(w).result)
    assert.is_true(w.globals.DAN_JUHANIF_DONE)
    assert.is_false(cond:conditional(w).result)
  end)

  it("opens a companion's recovery while they are down", function()
    local cond = nws.script("k_oaj_c_down")
    local w, _, carth = grove()
    w.self = carth
    assert.is_false(cond:conditional(w).result)
    w.globals.OAJ_DOWN_2 = true
    assert.is_true(cond:conditional(w).result)
  end)

  it("brings Carth back at his recovery's end, and opens his epilogue question", function()
    local w, _, carth = grove()
    w.party, w.npc_party = { w.party[1], w.party[3] }, { NPC_MISSION }
    w.globals.OAJ_DOWN_2 = true
    w.self = carth
    local run = nws.script("k_oaj_up"):run(w)
    assert.called(run, "AddPartyMember", NPC_CARTH)
    assert.is_false(w.globals.OAJ_DOWN_2)
    assert.is_true(w.globals.OAJ_DONE)
  end)

  it("starts Mission and Carth's banter once, when the second of them is back", function()
    local w, _, carth, mission = grove()
    w.party, w.npc_party = { w.party[1], carth }, { NPC_CARTH }
    w.globals.OAJ_DOWN_6 = true
    w.self = mission
    local run = nws.script("k_oaj_up"):run(w)
    assert.called(run, "AddPartyMember", NPC_MISSION)
    assert.called(run, "ActionStartConversation", nws.any, "oaj_banter")
    -- as the game's party-initiated conversations: the player leading, the party's actions cleared first
    assert.called(run, "SetPartyLeader", -1)
    assert.called_before(run, "ClearAllActions", "ActionStartConversation")
    assert.is_true(w.globals.OAJ_BANTER)
    assert.is_nil(w.globals.OAJ_DONE)
    assert.not_called(nws.script("k_oaj_up"):run(w), "ActionStartConversation")
  end)

  it("doesn't start the banter while the other is still down", function()
    local w, _, _, mission = grove()
    w.party, w.npc_party = { w.party[1] }, {}
    w.globals.OAJ_DOWN_2, w.globals.OAJ_DOWN_6 = true, true
    w.self = mission
    assert.not_called(nws.script("k_oaj_up"):run(w), "ActionStartConversation")
    assert.is_true(nws.script("k_oaj_c_cardn"):conditional(w).result, "and she sends the player to him")
  end)
end)
