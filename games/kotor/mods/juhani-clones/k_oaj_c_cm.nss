// The grove cutscene: the last insult is offered only with Carth and Mission in the party, the two
// companions SCRIPT.md's recoveries are written for.

int StartingConditional()
{
    return IsNPCPartyMember(NPC_CARTH) && IsNPCPartyMember(NPC_MISSION);
}
