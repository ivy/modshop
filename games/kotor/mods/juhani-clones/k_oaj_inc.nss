// Oops! All Juhani: what the mod's scripts share. Its story is SCRIPT.md; how it hooks the game is
// README.md.
//
// Every effect put on a companion here has Juhani as its creator, as her own stasis does
// (k_pdan_14juh_d, events 30 and 40), so the functions that put them on run on her. A companion
// taken out of the party here is "down" (OAJ_DOWN_<NPC number>) until they rejoin it.

#include "k_inc_generic"
#include "k_inc_utility"
#include "k_oaj_gen" // from make.py: APPEARANCE_HIDDEN, the row it adds; NpcTag, from the party blueprints

int YIELD_BELOW = 50; // the hit points under which she yields, in her own k_pdan_14juh_d
float RECOVER_BEYOND = 30.0; // metres from the player at which a companion still down gets up, once she is done
int VFX_IMP_POLYMORPH = 1046; // visualeffects.2da; nwscript.nss has no name for it
int SPECIAL_NPC_1 = NPC_CARTH; // transformed first: Mission sees it happen, which she teases him about after
int SPECIAL_NPC_2 = NPC_MISSION;

string JUHANI = "dan14_juhani";

object Juhani()
{
    return GetObjectByTag(JUHANI);
}

string CloneTag(int nClone)
{
    return "oaj_juhani" + IntToString(nClone);
}

int CloneStanding(int nClone)
{
    object oClone = GetObjectByTag(CloneTag(nClone));
    return GetIsObjectValid(oClone) && !GetIsDead(oClone);
}

// A party NPC's number from their creature, in or out of the party, by tag; -1 for anyone else.
// Tags compare without case, as GetObjectByTag finds them: a companion's in the world can differ
// from its blueprint's in case (the grove's Carth is "carth", p_carth's "Carth").
int NpcOf(object oCreature)
{
    string sTag = GetStringLowerCase(GetTag(oCreature));
    int nNPC;
    for (nNPC = NPC_BASTILA; nNPC <= NPC_ZAALBAR; nNPC++) {
        if (GetStringLowerCase(NpcTag(nNPC)) == sTag) {
            return nNPC;
        }
    }
    return -1;
}

int IsDown(int nNPC)
{
    return GetGlobalBoolean("OAJ_DOWN_" + IntToString(nNPC));
}

void SetDown(int nNPC, int bDown)
{
    SetGlobalBoolean("OAJ_DOWN_" + IntToString(nNPC), bDown);
}

// Every effect of hers on oMember: her stasis, the hiding. The walk starts over after a removal,
// which leaves the walk's place undefined.
void Release(object oMember)
{
    effect eEffect = GetFirstEffect(oMember);
    while (GetIsEffectValid(eEffect)) {
        if (GetEffectCreator(eEffect) == OBJECT_SELF) {
            RemoveEffect(oMember, eEffect);
            eEffect = GetFirstEffect(oMember);
        } else {
            eEffect = GetNextEffect(oMember);
        }
    }
}

// Her stasis, as k_pdan_14juh_d puts it on in events 30 and 40.
void Hold(object oMember)
{
    ApplyEffectToObject(DURATION_TYPE_PERMANENT, EffectLinkEffects(EffectCutSceneParalyze(), EffectVisualEffect(2008)), oMember);
}

// One effect, so one Release undoes it: held, and unseen (an appearance whose model is the
// invisible placeable's).
void Hide(object oMember)
{
    effect eHidden = EffectLinkEffects(EffectCutSceneParalyze(), EffectDisguise(APPEARANCE_HIDDEN));
    Release(oMember);
    ApplyEffectToObject(DURATION_TYPE_PERMANENT, eHidden, oMember);
}

// Run on a companion who is down: back in the party, and no longer down.
void Rejoin()
{
    int nNPC = NpcOf(OBJECT_SELF);
    if (nNPC < 0) {
        return;
    }
    ClearAllActions();
    AddPartyMember(nNPC, OBJECT_SELF);
    SetDown(nNPC, FALSE);
}

// Her part is over once she has gone, died, or settled her plot (k_pdan_juhani12, or her death's
// event 1007).
int JuhaniDone()
{
    object oJuhani = Juhani();
    return !GetIsObjectValid(oJuhani) || GetIsDead(oJuhani) || GetGlobalNumber("DAN_JUHANI_PLOT") >= 2;
}

// Run on a companion lying down: their recovery is their own conversation, which the player's
// click opens. Walked away from once she is done, and still down, they come back unwoken.
void WatchDowned()
{
    if (!IsDown(NpcOf(OBJECT_SELF))) {
        return;
    }
    if (GetDistanceBetween(OBJECT_SELF, GetFirstPC()) > RECOVER_BEYOND && JuhaniDone()) {
        Rejoin();
        return;
    }
    DelayCommand(1.0, WatchDowned());
}

// Run on a companion: their AI back on, and down, as banter.dlg lays Mission down
// (k_swg_bantforce), whose next line gets her up with dialog animation 10055, as each recovery
// conversation's first line does. The cutscene's trigger (k_pdan_juhani27) turned their AI off
// (k_pman_aioff) and her yield turns it back on (k_pman_aion) only for the party, which they are
// out of; with it off, their AI (k_ai_master) ignores the player's interaction and no
// conversation starts.
void LieDown()
{
    ExecuteScript("k_pman_aion", OBJECT_SELF);
    ClearAllActions();
    ActionPlayAnimation(ANIMATION_LOOPING_PRONE, 1.0, -1.0);
    WatchDowned();
}

// Every companion down, by what marks them: in this area and down. Free and seen again, lying
// where they were hidden.
void CollapseAll()
{
    int nNPC;
    for (nNPC = NPC_BASTILA; nNPC <= NPC_ZAALBAR; nNPC++) {
        object oMember = GetObjectByTag(NpcTag(nNPC));
        if (IsDown(nNPC) && GetIsObjectValid(oMember) && GetArea(oMember) == GetArea(OBJECT_SELF)) {
            Release(oMember);
            DelayCommand(0.5, AssignCommand(oMember, LieDown())); // once the hold has let go of them
        }
    }
}

void StandDown()
{
    GN_SetSpawnInCondition(SW_FLAG_AI_OFF, TRUE);
    ChangeToStandardFaction(OBJECT_SELF, STANDARD_FACTION_NEUTRAL);
    ClearAllActions();
    ActionPlayAnimation(ANIMATION_LOOPING_PAUSE_TIRED, 1.0, -1.0);
}

// The bodies gone and each companion seen again where they were hidden, unconscious.
void EndFight()
{
    int nClone;
    for (nClone = 1; nClone <= 2; nClone++) {
        object oBody = GetObjectByTag(CloneTag(nClone));
        if (GetIsObjectValid(oBody)) {
            ApplyEffectAtLocation(DURATION_TYPE_INSTANT, EffectVisualEffect(VFX_IMP_POLYMORPH), GetLocation(oBody));
            AssignCommand(oBody, SetIsDestroyable(TRUE)); // a body kept by k_oaj_clsp resists DestroyObject
            DelayCommand(0.2, DestroyObject(oBody));
        }
    }
    CollapseAll();
    GN_SetSpawnInCondition(SW_FLAG_AI_OFF, FALSE);
    GN_SetSpawnInCondition(SW_FLAG_EVENT_ON_DAMAGED, TRUE);
    ClearAllActions(); // ends a stand-down's endless animation, which her conversation would queue behind
    DelayCommand(1.0, SignalEvent(OBJECT_SELF, EventUserDefined(1006))); // below 50, so she yields
}

// Her damaged event, where she would yield, is off while a clone stands, so her hit points are
// watched here: below 50 while a clone stands she stands down; once none stands, the fight ends.
void Watch()
{
    if (UT_GetPlotBooleanFlag(OBJECT_SELF, SW_PLOT_BOOLEAN_05)) {
        return; // she has yielded
    }
    if (GetCurrentHitPoints(OBJECT_SELF) < YIELD_BELOW) {
        if (!CloneStanding(1) && !CloneStanding(2)) {
            EndFight();
            return;
        }
        if (!GN_GetSpawnInCondition(SW_FLAG_AI_OFF)) {
            StandDown();
        }
    }
    DelayCommand(0.5, Watch());
}

// A clone of her on the companion's spot, neutral until the fight starts. Her yield is held only
// once a clone stands; without one the companion rejoins the party, seen again and held in her
// stasis as they were, which her yield lifts.
void SpawnClone(int nClone, location lAt, object oMember, int nNPC)
{
    object oClone = CreateObject(OBJECT_TYPE_CREATURE, CloneTag(nClone), lAt);
    if (!GetIsObjectValid(oClone)) {
        AddPartyMember(nNPC, oMember);
        SetDown(nNPC, FALSE);
        Release(oMember);
        Hold(oMember);
        return;
    }
    GN_SetSpawnInCondition(SW_FLAG_EVENT_ON_DAMAGED, FALSE);
    ChangeToStandardFaction(oClone, STANDARD_FACTION_NEUTRAL);
    AssignCommand(oClone, SetFacingPoint(GetPosition(GetFirstPC())));
}

// Out of the party, so the player can't switch to them, and neutral, so nothing fights them; a
// clone of her where they stood.
void Transform(object oMember, int nClone)
{
    int nNPC = NpcOf(oMember);
    if (nNPC < 0 || !IsNPCPartyMember(nNPC)) {
        return;
    }
    location lSpot = GetLocation(oMember);
    ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectVisualEffect(VFX_IMP_POLYMORPH), oMember);
    RemovePartyMember(nNPC);
    SetDown(nNPC, TRUE);
    ChangeToStandardFaction(oMember, STANDARD_FACTION_NEUTRAL);
    DelayCommand(0.1, Hide(oMember)); // after leaving the party, which undoes a disguise put on before
    DelayCommand(0.3, SpawnClone(nClone, lSpot, oMember, nNPC));
}

// The clones turn on the player, her saber drawn; run on her.
void StartFight()
{
    int nClone;
    for (nClone = 1; nClone <= 2; nClone++) {
        object oClone = GetObjectByTag(CloneTag(nClone));
        if (GetIsObjectValid(oClone)) {
            ChangeToStandardFaction(oClone, STANDARD_FACTION_HOSTILE_1);
            AssignCommand(oClone, ActionEquipMostDamagingMelee()); // her blueprint carries the saber unequipped
            AssignCommand(oClone, ActionAttack(GetFirstPC()));
        }
    }
    if (CloneStanding(1) || CloneStanding(2)) {
        Watch();
    }
}
