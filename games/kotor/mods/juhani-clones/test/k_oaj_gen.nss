// The include make.py generates (k_oaj_gen), with this build's values, for the tests.

int APPEARANCE_HIDDEN = 529;

string NpcTag(int nNPC)
{
    if (nNPC == 0) {
        return "Bastila";
    }
    if (nNPC == 1) {
        return "Cand";
    }
    if (nNPC == 2) {
        return "Carth";
    }
    if (nNPC == 3) {
        return "HK47";
    }
    if (nNPC == 4) {
        return "Jolee";
    }
    if (nNPC == 5) {
        return "Juhani";
    }
    if (nNPC == 6) {
        return "Mission";
    }
    if (nNPC == 7) {
        return "T3M4";
    }
    if (nNPC == 8) {
        return "Zaalbar";
    }
    return "";
}
