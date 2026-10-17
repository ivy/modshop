// The end of a companion's recovery conversation, run on them: back in the party. Once Carth and
// Mission both are, their banter (oaj_banter.dlg) starts by itself, once.

#include "k_oaj_inc"

// As the game's party-initiated conversations start (k_trg_partyinit, and the banter triggers,
// k_bant_trig): the player leading, the party's actions cleared, which otherwise hold a party
// member's standing action that a conversation would wait behind for ever.
void StartBanter()
{
    object oCarth = GetObjectByTag(NpcTag(NPC_CARTH));
    object oMission = GetObjectByTag(NpcTag(NPC_MISSION));
    SetPartyLeader(NPC_PLAYER);
    AssignCommand(oCarth, ClearAllActions());
    AssignCommand(oMission, ClearAllActions());
    AssignCommand(oMission, ActionStartConversation(GetFirstPC(), "oaj_banter"));
}

void main()
{
    Rejoin();
    if (NpcOf(OBJECT_SELF) == NPC_CARTH) {
        SetGlobalBoolean("OAJ_DONE", TRUE); // his "About what happened on Dantooine..." from here on
    }
    if (IsNPCPartyMember(NPC_CARTH) && IsNPCPartyMember(NPC_MISSION) && !GetGlobalBoolean("OAJ_BANTER")) {
        SetGlobalBoolean("OAJ_BANTER", TRUE);
        DelayCommand(2.0, StartBanter());
    }
}
