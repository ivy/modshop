// Juhani's user-defined events in the grove (danm14ac), decompiled from the game's bytecode by nws
// (84 of 84 functions verified by recompiling), with one change for juhani-clones: walking to her
// mark (event 10) she no longer has dan14ac_cutobj02 play her battlecry (k_pdan_juhani36), which
// would speak over her lines; k_pdan_juhani31 has it play as the fight starts.
//
// Recovered from NCS bytecode: 84 of 84 functions verified by recompiling.

struct Struct1 {
    int f0;
    int f1;
    int f2;
    object f3;
    int f4;
    int f5;
    int f6;
    int f7;
    int f8;
    int f9;
};

// verified: recompiles to the original bytes
int nGlobal1 = 1;
int nGlobal2 = 2;
int nGlobal3 = 3;
int nGlobal4 = 4;
int nGlobal5 = 5;
int nGlobal6 = 6;
int nGlobal7 = 3;
int nGlobal8 = 4;
int nGlobal9 = 5;
int nGlobal10 = 6;
int nGlobal11 = 7;
int nGlobal12 = 1;
int nGlobal13 = 2;
int nGlobal14 = 3;
int nGlobal15 = 4;
int nGlobal16 = 5;
int nGlobal17 = 6;
int nGlobal18 = 7;
int nGlobal19 = 8;
int nGlobal20 = 9;
int nGlobal21 = 10;
int nGlobal22 = 11;
int nGlobal23 = 12;
int nGlobal24 = 13;
int nGlobal25 = 14;
int nGlobal26 = 15;
int nGlobal27 = 16;
int nGlobal28 = 17;
int nGlobal29 = 18;
int nGlobal30 = 19;
int nGlobal31 = 20;
int nGlobal32 = 21;
int nGlobal33 = 22;
int nGlobal34 = 23;
int nGlobal35 = 24;
int nGlobal36 = 25;
int nGlobal37 = 26;
int nGlobal38 = 27;
int nGlobal39 = 28;
int nGlobal40 = 29;
int nGlobal41 = 30;
int nGlobal42 = 59;
int nGlobal43 = 0;
int nGlobal44 = 1;
int nGlobal45 = 2;
int nGlobal46 = 29;
int nGlobal47 = 30;
int nGlobal48 = 34;
int nGlobal49 = 35;
int nGlobal50 = 36;
int nGlobal51 = 37;
int nGlobal52 = 38;
int nGlobal53 = 39;
int nGlobal54 = 41;
int nGlobal55 = 42;
int nGlobal56 = 46;
int nGlobal57 = 47;
int nGlobal58 = 15;
int nGlobal59 = 10;
int nGlobal60 = 5;
int nGlobal61 = 2;
struct Struct1 stGlobal62;
int nGlobal63 = 1;
int nGlobal64 = 2;
int nGlobal65 = 3;
int nGlobal66 = 20;
int nGlobal67 = 21;
int nGlobal68 = 22;
int nGlobal69 = 23;
int nGlobal70 = 24;
int nGlobal71 = 25;
int nGlobal72 = 26;
int nGlobal73 = 27;
int nGlobal74 = 28;
int nGlobal75 = 31;
int nGlobal76 = 32;
int nGlobal77 = 33;
int nGlobal78 = 40;
int nGlobal79 = 43;
int nGlobal80 = 44;
int nGlobal81 = 45;
int nGlobal82 = 48;
int nGlobal83 = 49;
int nGlobal84 = 50;
int nGlobal85 = 51;
int nGlobal86 = 52;
int nGlobal87 = 53;
int nGlobal88 = 54;
int nGlobal89 = 55;
int nGlobal90 = 56;
int nGlobal91 = 57;
int nGlobal92 = 58;
int nGlobal93 = 60;
int nGlobal94 = 61;
int nGlobal95 = 62;
int nGlobal96 = 63;
int nGlobal97 = 64;
int nGlobal98 = 65;
int nGlobal99 = 66;
int nGlobal100 = 67;
int nGlobal101 = 68;
int nGlobal102 = 69;
int nGlobal103 = 70;
int nGlobal104 = 71;
int nGlobal105 = 72;
int nGlobal106 = 1;
int nGlobal107 = 2;
int nGlobal108 = 3;
int nGlobal109 = 4;
int nGlobal110 = 0;
int nGlobal111 = 1;
int nGlobal112 = 2;
int nGlobal113 = 3;
int nGlobal114 = 4;
int nGlobal115 = 5;
int nGlobal116 = 6;
int nGlobal117 = 7;
int nGlobal118 = 8;
int nGlobal119 = 9;
int nGlobal120 = 10;
int nGlobal121 = 11;
int nGlobal122 = 12;
int nGlobal123 = 13;
int nGlobal124 = 14;
int nGlobal125 = 15;
int nGlobal126 = 16;
int nGlobal127 = 17;
int nGlobal128 = 18;
int nGlobal129 = 19;
int nGlobal130 = 1100;
int nGlobal131 = -6;
int nGlobal132 = -5;
int nGlobal133 = -4;
int nGlobal134 = -2;
int nGlobal135 = -1;
int nGlobal136 = 0;
int nGlobal137 = 1;
int nGlobal138 = 2;
int nGlobal139 = 0;
int nGlobal140 = 1;
int nGlobal141 = 2;
int nGlobal142 = 3;
int nGlobal143 = 4;
int nGlobal144 = 3012;
int nGlobal145 = 2702;
int nGlobal146 = 2548;
int nGlobal147 = 2348;
int nGlobal148 = 3;
int nGlobal149 = 4;
int nGlobal150 = 25;
string sGlobal151 = GetStringByStrRef(32289);
string sGlobal152 = "man27_visstm0";
string sGlobal153 = "man26_repdip";

void sub_1405(object oParam1);
void sub_1964(string sParam1);
string sub_198c(object oParam1);
void sub_19ef();
string sub_1bb8(object oParam1);
int sub_1daf(int nParam1);
int sub_1e3c();
string sub_2151(int nParam1);
void sub_2180(int nParam1, int nParam2);
int sub_21a3();
int sub_23ba();
int sub_296c(object oParam1);
object sub_2b8a();
int sub_3105(int nParam1, object oParam2);
object sub_3f1c(int nParam1);
int sub_47d5();
int sub_5169(object oParam1);
int sub_57f3();
object sub_5a4d();
int sub_5cb9(object oParam1, float fParam2);
int sub_5e0d(object oParam1, float fParam2);
talent sub_5f44(int nParam1, int nParam2);
talent sub_662b(int nParam1);
talent sub_70e7(int nParam1);
talent sub_7e10(int nParam1);
int sub_8c17();
object sub_8e37();
int sub_8fc8();
talent sub_979f(object oParam1, talent tParam2);
talent sub_99df(object oParam1, talent tParam2);
int sub_9e16(object oParam1);
object sub_a74c();
talent sub_a999(int nParam1);
int sub_aedc(int nParam1);
int sub_b204(int nParam1);
int sub_c3c5();
int sub_c6b6();
int sub_c773();
int sub_c830();
int sub_c8be();
int sub_c97b();
int sub_ca38();
int sub_caf5();
int sub_cbb2();
int sub_cc6f();
int sub_ccfd();
int sub_cd8b();
int sub_ce19();
string sub_cea1(int nParam1);
talent sub_d7df(int nParam1);
int sub_ebe4();
int sub_ecbf();
int sub_ed9a();
int sub_ee38();
int sub_ef13();
int sub_efee();
int sub_f0d2();
int sub_f1ad();
int sub_f288();
int sub_f363();
int sub_f401();
int sub_f49f();
int sub_f53d();
int sub_f621(int nParam1);
int sub_f8e2(int nParam1);
talent sub_fba8(object oParam1, talent tParam2);
int sub_10169(object oParam1);
int sub_1038b(object oParam1);
object sub_1090e(object oParam1);
int sub_1119e();
int sub_114de();
void sub_1192f();
int sub_1194f(object oParam1);
void sub_11c70(string sParam1);
void sub_11c98();
int sub_124e7(int nParam1, int nParam2);
void sub_12667();
void sub_129ae(string sParam1, int nParam2, int nParam3, float fParam4);
int sub_129b6(object oParam1, int nParam2);
void sub_12a9e(object oParam1, int nParam2, int nParam3);
void sub_12d6a(object oParam1);
void sub_12e48();

// verified: recompiles to the original bytes
void main()
{
    object oLocal1 = GetPartyMemberByIndex(1);
    object oLocal2 = GetPartyMemberByIndex(2);
    effect eLocal3 = EffectLinkEffects(EffectCutSceneParalyze(), EffectVisualEffect(2008));
    int nLocal4 = GetUserDefinedEventNumber();
    switch (nLocal4) {
        case 10:
            ClearAllActions();
            ActionPlayAnimation(0, 1.0, 0.1);
            ActionMoveToObject(GetObjectByTag("wp_cut01"));
            ActionDoCommand(SignalEvent(GetObjectByTag("dan14ac_cutobj01"), EventUserDefined(0)));
            break;
        case 20:
            ActionWait(1.0);
            ActionEquipMostDamagingMelee();
            ActionWait(1.0);
            ActionDoCommand(SignalEvent(GetObjectByTag("dan14ac_cutobj01"), EventUserDefined(0)));
            break;
        case 30:
            if (GetIsObjectValid(oLocal1)) {
                ActionCastFakeSpellAtObject(29, oLocal1);
                ActionDoCommand(ApplyEffectToObject(2, eLocal3, oLocal1));
                ActionWait(0.5);
                ActionDoCommand(SignalEvent(GetObjectByTag("dan14ac_cutobj01"), EventUserDefined(0)));
            }
            break;
        case 40:
            if (GetIsObjectValid(oLocal2)) {
                ActionCastFakeSpellAtObject(29, oLocal2);
                ActionDoCommand(ApplyEffectToObject(2, eLocal3, oLocal2));
                ActionWait(0.5);
                ActionDoCommand(SignalEvent(GetObjectByTag("dan14ac_cutobj01"), EventUserDefined(0)));
            }
            break;
        case 80:
            ChangeToStandardFaction(OBJECT_SELF, 1);
            ClearAllActions();
            DelayCommand(0.2, sub_1405(GetFirstPC()));
            break;
        case 1003:
            if (sub_129b6(OBJECT_SELF, nGlobal114) == 0) {
                ClearAllActions();
                sub_1405(GetFirstPC());
            }
            break;
        case 1006:
            if (GetCurrentHitPoints() < 50 && sub_129b6(OBJECT_SELF, nGlobal114) == 0) {
                sub_12a9e(OBJECT_SELF, nGlobal114, 1);
                sub_12d6a(oLocal1);
                sub_12d6a(oLocal2);
                sub_12e48();
                SetGlobalBoolean("DAN_JUHANI_FIGHT", 0);
                SurrenderToEnemies();
                CancelCombat(GetFirstPC());
                CancelCombat(oLocal1);
                CancelCombat(oLocal2);
                NoClicksFor(1.2);
                DelayCommand(0.5, SurrenderToEnemies());
                DelayCommand(1.0, ActionStartConversation(GetFirstPC()));
            }
            break;
        case 1007:
            SetGlobalNumber("DAN_JEDI_PLOT", 4);
            SetGlobalNumber("DAN_JUHANI_PLOT", 2);
            {
                object oLocal5 = GetObjectByTag("dan13_groveflee");
                if (GetIsObjectValid(oLocal5)) {
                    DestroyObject(oLocal5);
                }
            }
            break;
        default:
    }
}

// verified: recompiles to the original bytes
void sub_1405(object oParam1)
{
    sub_1964("");
    sub_1964("GENERIC DEBUG *************** START DETERMINE COMBAT ROUND " + sub_198c(OBJECT_SELF));
    sub_19ef();
    int nLocal1 = GetPartyAIStyle();
    int nLocal2 = GetNPCAIStyle(OBJECT_SELF);
    sub_1964("GENERIC DEBUG *************** AI STYLE = " + sub_1bb8(OBJECT_SELF));
    if (!sub_1daf(nGlobal93) && !sub_1daf(nGlobal94) && !sub_1daf(nGlobal95) && !GetUserActionsPending()) {
        if (GetPartyMemberByIndex(0) != OBJECT_SELF && !GetPlayerRestrictMode()) {
            if ((IsObjectPartyMember(OBJECT_SELF) && !GetPlayerRestrictMode()) || !IsObjectPartyMember(OBJECT_SELF)) {
                if (nLocal2 == 2) {
                    if (GetIsObjectValid(oParam1)) {
                        ClearAllActions();
                        ActionAttack(oParam1);
                        return;
                    } else {
                        object oLocal3 = GetNearestCreature(3, 1);
                        if (GetIsObjectValid(oLocal3)) {
                            ClearAllActions();
                            ActionAttack(oLocal3);
                            return;
                        }
                    }
                    return;
                }
                if (sub_1e3c() == 1) {
                    return;
                }
                if (sub_21a3() == 1) {
                    return;
                }
                if (sub_1daf(nGlobal103) == 1) {
                    if (sub_23ba() == 1) {
                        return;
                    }
                }
                if (sub_1daf(nGlobal97) == 1) {
                    if (sub_296c(oParam1) == 1) {
                        return;
                    }
                }
                if (nLocal2 == 0) {
                    if (sub_9e16(oParam1) == 1) {
                        return;
                    }
                } else if (nLocal2 == 4) {
                    if (sub_10169(oParam1) == 1) {
                        return;
                    }
                } else if (nLocal2 == 5) {
                    if (sub_1038b(oParam1) == 1) {
                        return;
                    }
                }
            }
        }
    }
    if (sub_1119e()) {
        sub_1964("GENERIC DEBUG *************** DETERMINE COMBAT ROUND END");
    }
    sub_1964("GENERIC DEBUG *************** WARNING DETERMINE COMBAT ROUND FAILURE");
}

// verified: recompiles to the original bytes
void sub_1964(string sParam1)
{
    if (!ShipBuild()) {
        PrintString(sParam1);
    }
}

// verified: recompiles to the original bytes
string sub_198c(object oParam1)
{
    string sLocal1 = GetName(oParam1) + "_" + ObjectToString(oParam1);
    return sLocal1;
}

// verified: recompiles to the original bytes
void sub_19ef()
{
    talent tLocal1;
    stGlobal62.f3 = GetLastHostileTarget();
    stGlobal62.f5 = GetIsDebilitated(stGlobal62.f3);
    stGlobal62.f0 = GetLastAttackAction();
    if (stGlobal62.f0 == 4) {
        stGlobal62.f1 = GetLastForcePowerUsed();
        stGlobal62.f4 = GetWasForcePowerSuccessful();
        tLocal1 = TalentSpell(stGlobal62.f1);
        stGlobal62.f2 = GetCategoryFromTalent(tLocal1);
    } else if (stGlobal62.f0 == 3) {
        stGlobal62.f1 = GetLastCombatFeatUsed();
        stGlobal62.f4 = GetLastAttackResult();
        tLocal1 = TalentFeat(stGlobal62.f1);
        stGlobal62.f2 = GetCategoryFromTalent(tLocal1);
    }
    stGlobal62.f7 = GetLocalNumber(OBJECT_SELF, nGlobal8);
    stGlobal62.f8 = GetLocalNumber(OBJECT_SELF, nGlobal7);
}

// verified: recompiles to the original bytes
string sub_1bb8(object oParam1)
{
    if (GetNPCAIStyle(oParam1) == 3) {
        return "NPC_AISTYLE_AID";
    } else if (GetNPCAIStyle(oParam1) == 4) {
        return "NPC_AISTYLE_GRENADE_THROWER";
    } else if (GetNPCAIStyle(oParam1) == 5) {
        return "NPC_AISTYLE_JEDI_SUPPORT";
    } else if (GetNPCAIStyle(oParam1) == 0) {
        return "NPC_AISTYLE_DEFAULT_ATTACK";
    }
    int nLocal1 = GetNPCAIStyle(oParam1);
    string sLocal2 = IntToString(nLocal1);
    sLocal2 = "No Valid AI Set, state = " + sLocal2;
    return sLocal2;
}

// verified: recompiles to the original bytes
int sub_1daf(int nParam1)
{
    int nLocal1 = GetLocalBoolean(OBJECT_SELF, nParam1);
    if (nLocal1 > 0) {
        return 1;
    }
    return 0;
}

// verified: recompiles to the original bytes
int sub_1e3c()
{
    sub_1964("GENERIC DEBUG *************** Starting Forcefield Search");
    sub_1964("GENERIC DEBUG *************** Shield Boolean (" + sub_2151(nGlobal98) + ") = " + sub_2151(sub_1daf(nGlobal98)));
    if (sub_1daf(nGlobal98) == 0 && !IsObjectPartyMember(OBJECT_SELF)) {
        int nLocal1;
        int nLocal2;
        int nLocal3 = 0;
        talent tLocal4;
        if (GetRacialType(OBJECT_SELF) == 5) {
            nLocal1 = 110;
            nLocal2 = 115;
        } else {
            nLocal1 = 99;
            nLocal2 = 107;
        }
        while (nLocal3 == 0 && nLocal1 <= nLocal2) {
            tLocal4 = TalentSpell(nLocal1);
            if (GetCreatureHasTalent(tLocal4)) {
                nLocal3 = 1;
            } else {
                nLocal1++;
            }
        }
        if (GetCreatureHasTalent(tLocal4)) {
            sub_1964("GENERIC DEBUG *************** Clear 1700");
            ClearAllActions();
            ActionUseTalentOnObject(tLocal4, OBJECT_SELF);
            sub_2180(nGlobal98, 1);
            return 1;
        } else {
            sub_2180(nGlobal98, 1);
            return 0;
        }
    }
    return 0;
}

// verified: recompiles to the original bytes
string sub_2151(int nParam1)
{
    return IntToString(nParam1);
}

// verified: recompiles to the original bytes
void sub_2180(int nParam1, int nParam2)
{
    SetLocalBoolean(OBJECT_SELF, nParam1, nParam2);
}

// verified: recompiles to the original bytes
int sub_21a3()
{
    int nLocal1 = 0;
    if (sub_1daf(nGlobal100) == 0 && !IsObjectPartyMember(OBJECT_SELF)) {
        if (GetHitDice(GetFirstPC()) >= 15 || sub_1daf(nGlobal97)) {
            talent tLocal2 = TalentSpell(41);
            talent tLocal3 = TalentSpell(20);
            talent tLocal4;
            if (GetCreatureHasTalent(tLocal3)) {
                tLocal4 = tLocal3;
                nLocal1 = 1;
            } else if (GetCreatureHasTalent(tLocal2)) {
                tLocal4 = tLocal2;
                nLocal1 = 1;
            }
            if (nLocal1 == 1) {
                sub_1964("GENERIC DEBUG *************** Clear 1710");
                ClearAllActions();
                ActionUseTalentOnObject(tLocal4, OBJECT_SELF);
            }
            sub_2180(nGlobal100, 1);
        }
    }
    return nLocal1;
}

// verified: recompiles to the original bytes
int sub_23ba()
{
    sub_1964("GENERIC DEBUG *************** Malak AI Start");
    int nLocal1 = GetGlobalNumber("K_END_JEDI_LEFT");
    int nLocal2 = GetGlobalNumber("K_END_MALAK_JEDI_USED");
    object oLocal3 = GetFirstPC();
    int nLocal4;
    int nLocal5;
    int nLocal6;
    float fLocal7 = GetDistanceBetween(OBJECT_SELF, oLocal3);
    if (8 - nLocal1 < nLocal2) {
        nLocal4 = 1;
    }
    sub_1964("GENERIC DEBUG *************** Malak Distance to PC = " + FloatToString(GetDistanceBetween(OBJECT_SELF, oLocal3), 4, 4));
    if (fLocal7 > 10.0) {
        nLocal5 = 1;
    }
    if (nLocal5 == 1) {
        sub_1964("GENERIC DEBUG *************** Clear 1480");
        ClearAllActions();
        if (GetHasSpellEffect(8, oLocal3) || GetHasSpellEffect(34, oLocal3) || GetHasSpellEffect(37, oLocal3)) {
            talent tLocal8 = TalentSpell(19);
            if (GetIsTalentValid(tLocal8)) {
                sub_1964("GENERIC DEBUG *************** Using Breach");
                ActionUseTalentOnObject(tLocal8, oLocal3);
            }
            nLocal6 = 1;
        } else {
            if (fLocal7 > 10.0) {
                int nLocal9 = d3();
                int nLocal10 = -1;
                if (nLocal9 == 1) {
                    nLocal10 = 35;
                } else if (nLocal9 == 2) {
                    nLocal10 = 49;
                } else if (nLocal9 > 2) {
                    nLocal6 = 1;
                }
                if (nLocal10 != -1) {
                    talent tLocal11 = TalentSpell(nLocal10);
                    if (GetIsTalentValid(tLocal11)) {
                        sub_1964("GENERIC DEBUG *************** Malak Using Force Power");
                        ActionUseTalentOnObject(tLocal11, oLocal3);
                        return 1;
                    }
                }
            }
            nLocal6 = 1;
        }
    }
    if (nLocal6 == 1) {
        sub_1964("GENERIC DEBUG *************** Malak Attacking");
        ActionAttack(oLocal3);
        return 1;
    }
    sub_1964("GENERIC DEBUG *************** Malak AI Drop Out");
    return 0;
}

// verified: recompiles to the original bytes
int sub_296c(object oParam1)
{
    sub_1964("GENERIC DEBUG *************** Boss AI Start");
    object oLocal1 = sub_2b8a();
    if (GetIsObjectValid(oLocal1)) {
        if (sub_3105(nGlobal108, oLocal1)) {
            return 1;
        }
    }
    if (sub_47d5()) {
        sub_1964("GENERIC DEBUG *************** Switching Weapons");
    }
    if (sub_57f3() == 1) {
        return 1;
    } else if (sub_8c17() == 1) {
        return 1;
    } else if (sub_8fc8() == 1) {
        return 1;
    }
    sub_1964("GENERIC DEBUG *************** Boss AI: Fall Through");
    return sub_9e16(OBJECT_INVALID);
}

// verified: recompiles to the original bytes
object sub_2b8a()
{
    sub_1964("GENERIC DEBUG ***************  Starting Injury Check Function");
    if (IsObjectPartyMember(OBJECT_SELF) || GetRacialType(OBJECT_SELF) == 5) {
        object oLocal1 = GetPartyMemberByIndex(0);
        object oLocal2 = GetPartyMemberByIndex(1);
        object oLocal3 = GetPartyMemberByIndex(2);
        float fLocal4 = 10.0;
        float fLocal5 = 10.0;
        float fLocal6 = 10.0;
        if (GetIsObjectValid(oLocal1) && GetRacialType(oLocal1) != 5) {
            fLocal4 = IntToFloat(GetCurrentHitPoints(oLocal1)) / IntToFloat(GetMaxHitPoints(oLocal1));
        }
        if (GetIsObjectValid(oLocal2) && GetRacialType(oLocal1) != 5) {
            fLocal5 = IntToFloat(GetCurrentHitPoints(oLocal2)) / IntToFloat(GetMaxHitPoints(oLocal2));
        }
        if (GetIsObjectValid(oLocal3) && GetRacialType(oLocal1) != 5) {
            fLocal6 = IntToFloat(GetCurrentHitPoints(oLocal3)) / IntToFloat(GetMaxHitPoints(oLocal3));
        }
        if (GetIsObjectValid(oLocal1) && !GetIsDead(oLocal1) && (fLocal4 < 0.5 && fLocal4 > 0.0)) {
            sub_1964("GENERIC DEBUG ***************  Return oP0");
            return oLocal1;
        } else if (GetIsObjectValid(oLocal2) && !GetIsDead(oLocal2) && (fLocal4 < 0.5 && fLocal4 > 0.0)) {
            sub_1964("GENERIC DEBUG ***************  Return oP1");
            return oLocal2;
        } else if (GetIsObjectValid(oLocal3) && !GetIsDead(oLocal3) && (fLocal4 < 0.5 && fLocal4 > 0.0)) {
            sub_1964("GENERIC DEBUG ***************  Return oP2");
            return oLocal3;
        }
    } else {
        float fLocal7 = IntToFloat(GetCurrentHitPoints()) / IntToFloat(GetMaxHitPoints());
        if (fLocal7 < 0.5) {
            return OBJECT_SELF;
        }
    }
    return OBJECT_INVALID;
}

// verified: recompiles to the original bytes
int sub_3105(int nParam1, object oParam2)
{
    if (GetIsObjectValid(oParam2)) {
        talent tLocal1;
        talent tLocal2;
        talent tLocal3;
        talent tLocal4;
        talent tLocal5;
        talent tLocal6;
        talent tLocal7;
        talent tLocal8;
        int nLocal9;
        int nLocal10 = 0;
        int nLocal11 = 0;
        if (nParam1 == nGlobal106) {
            nLocal9 = 61473;
        } else if (nParam1 == nGlobal107) {
            tLocal1 = TalentSpell(28);
            tLocal2 = TalentSpell(10);
            tLocal3 = TalentSpell(67);
            if (GetCreatureHasTalent(tLocal1) || GetCreatureHasTalent(tLocal2)) {
                nLocal10 = 1;
                if (GetCreatureHasTalent(tLocal1)) {
                    tLocal8 = tLocal1;
                } else {
                    tLocal8 = tLocal2;
                }
            } else if (GetCreatureHasTalent(tLocal3) && oParam2 == OBJECT_SELF) {
                nLocal10 = 1;
                tLocal8 = tLocal3;
            }
        } else if (nParam1 == nGlobal108) {
            sub_1964("GENERIC DEBUG *************** Starting Heal Talent Checks " + sub_198c(OBJECT_SELF));
            tLocal1 = TalentSpell(28);
            tLocal2 = TalentSpell(10);
            if (GetRacialType(OBJECT_SELF) != 5) {
                tLocal5 = GetCreatureTalentBest(5128, 20);
            } else {
                tLocal5 = TalentSpell(128);
                if (!GetCreatureHasTalent(tLocal5)) {
                    tLocal5 = TalentSpell(127);
                    if (!GetCreatureHasTalent(tLocal5)) {
                        tLocal5 = TalentSpell(84);
                    }
                }
            }
            tLocal6 = TalentSpell(15);
            tLocal7 = TalentSpell(11);
            tLocal8;
            nLocal10 = 0;
            if (GetCreatureHasTalent(tLocal1) || GetCreatureHasTalent(tLocal2)) {
                sub_1964("GENERIC DEBUG *************** I have Heal or Cure");
                nLocal10 = 1;
                if (GetCreatureHasTalent(tLocal1)) {
                    tLocal8 = tLocal1;
                } else {
                    tLocal8 = tLocal2;
                }
            } else if (GetIsTalentValid(tLocal5) || GetCreatureHasTalent(tLocal6) || GetCreatureHasTalent(tLocal7)) {
                if (oParam2 == OBJECT_SELF) {
                    if (GetCreatureHasTalent(tLocal7) && !IsObjectPartyMember(OBJECT_SELF)) {
                        sub_1964("GENERIC DEBUG *************** I have Death Field");
                        nLocal10 = 1;
                        nLocal11 = 1;
                        tLocal8 = tLocal7;
                    } else if (GetCreatureHasTalent(tLocal6) && !IsObjectPartyMember(OBJECT_SELF)) {
                        sub_1964("GENERIC DEBUG *************** I have Drain Life");
                        nLocal10 = 1;
                        nLocal11 = 1;
                        tLocal8 = tLocal6;
                    } else {
                        sub_1964("GENERIC DEBUG *************** I have a Med Pack");
                        nLocal10 = 1;
                        tLocal8 = tLocal5;
                    }
                }
            }
        } else if (nParam1 == nGlobal109) {
            tLocal1 = TalentSpell(36);
            tLocal2 = TalentSpell(33);
            tLocal3 = TalentSpell(22);
            if (GetCreatureHasTalent(tLocal1)) {
                nLocal10 = 1;
                tLocal8 = tLocal1;
            } else if (GetCreatureHasTalent(tLocal2)) {
                nLocal10 = 1;
                tLocal8 = tLocal2;
            } else if (GetCreatureHasTalent(tLocal3)) {
                nLocal10 = 1;
                tLocal8 = tLocal3;
            }
            if (!GetHasSpellEffect(36) && !GetHasSpellEffect(33) && !GetHasSpellEffect(22) && nLocal10 == 1) {
                sub_1964("GENERIC DEBUG *************** I do have VALOR");
                nLocal10 = 1;
            } else {
                sub_1964("GENERIC DEBUG *************** I do not have VALOR");
                nLocal10 = 0;
            }
        }
        if (nLocal10 == 1 && nLocal11 == 0) {
            sub_1964("GENERIC DEBUG *************** Clear 2300");
            int nLocal12 = GetIdFromTalent(tLocal8);
            sub_1964("GENERIC DEBUG *************** Spells.2DA ID = " + sub_2151(nLocal12));
            ClearAllActions();
            ActionUseTalentOnObject(tLocal8, OBJECT_SELF);
            return 1;
        } else if (nLocal10 == 1 && nLocal11 == 1) {
            oParam2 = sub_3f1c(1);
            if (GetIsObjectValid(oParam2)) {
                sub_1964("GENERIC DEBUG *************** Hostile Heal Targeted On: " + sub_198c(oParam2));
                sub_1964("GENERIC DEBUG *************** Clear 2400");
                ClearAllActions();
                ActionUseTalentOnObject(tLocal8, oParam2);
                return 1;
            }
        }
        talent tLocal13 = GetCreatureTalentBest(nLocal9, 20);
        if (GetIsTalentValid(tLocal8) && !GetHasSpellEffect(GetIdFromTalent(tLocal8))) {
            if (GetIsObjectValid(oParam2)) {
                sub_1964("GENERIC DEBUG *************** Clear 2500");
                ClearAllActions();
                sub_1964("GENERIC DEBUG *************** Target = " + GetName(oParam2) + " Talent Code = " + IntToString(nLocal9));
                ActionUseTalentOnObject(tLocal8, OBJECT_SELF);
                return 1;
            }
        }
    }
    sub_1964("GENERIC DEBUG *************** " + sub_198c(OBJECT_SELF) + " VP = " + sub_2151(GetCurrentHitPoints()) + "/" + sub_2151(GetMaxHitPoints()));
    sub_1964("GENERIC DEBUG *************** Healing Not Used");
    return 0;
}

// verified: recompiles to the original bytes
object sub_3f1c(int nParam1)
{
    object oLocal1 = GetPartyMemberByIndex(0);
    object oLocal2 = GetPartyMemberByIndex(1);
    object oLocal3 = GetPartyMemberByIndex(2);
    object oLocal4;
    int nLocal5 = 0;
    int nLocal6;
    int nLocal7 = 0;
    int nLocal8 = 0;
    int nLocal9 = 0;
    if (GetIsObjectValid(oLocal2) && GetCurrentHitPoints(oLocal2) > 0 && GetObjectSeen(oLocal2)) {
        if (GetRacialType(oLocal2) != 5 || nParam1 == 0) {
            nLocal5++;
            nLocal8 = 1;
        }
    }
    if (GetIsObjectValid(oLocal3) && GetCurrentHitPoints(oLocal3) > 0 && GetObjectSeen(oLocal3)) {
        if (GetRacialType(oLocal3) != 5 || nParam1 == 0) {
            nLocal5++;
            nLocal9 = 1;
        }
    }
    if (nParam1 == 1) {
        if (GetIsObjectValid(oLocal1) && GetCurrentHitPoints(oLocal1) > 0 && GetObjectSeen(oLocal1)) {
            if (GetRacialType(oLocal1) != 5) {
                nLocal5++;
                nLocal7 = 1;
            }
        }
    }
    if (nLocal5 == 0) {
        oLocal4 = OBJECT_INVALID;
    } else if (nLocal5 == 1) {
        if (nLocal8 == 1) {
            oLocal4 = oLocal2;
        } else if (nLocal9 == 1) {
            oLocal4 = oLocal3;
        } else if (nLocal7 == 1) {
            oLocal4 = oLocal1;
        }
    } else if (nLocal5 == 2) {
        nLocal6 = d100();
        if (nLocal7 == 1 && nLocal8 == 1) {
            if (nLocal6 > 50) {
                oLocal4 = oLocal1;
            } else {
                oLocal4 = oLocal2;
            }
        } else if (nLocal7 == 1 && nLocal9 == 1) {
            if (nLocal6 > 50) {
                oLocal4 = oLocal1;
            } else {
                oLocal4 = oLocal3;
            }
        } else if (nLocal8 == 1 && nLocal9 == 1) {
            if (nLocal6 > 50) {
                oLocal4 = oLocal2;
            } else {
                oLocal4 = oLocal3;
            }
        }
    } else if (nLocal5 == 3) {
        nLocal6 = d100();
        if (nLocal6 <= 33) {
            oLocal4 = oLocal1;
        } else if (nLocal6 > 33 && nLocal6 <= 66) {
            oLocal4 = oLocal2;
        } else if (nLocal6 > 66 && nLocal6 <= 100) {
            oLocal4 = oLocal3;
        }
    }
    if (!GetIsEnemy(oLocal4) && nParam1 == 1) {
        sub_1964("GENERIC DEBUG *************** Searching for Alternate Target");
        oLocal4 = GetNearestCreature(3, 1, OBJECT_SELF, 1, 0, 6);
        sub_1964("GENERIC DEBUG *************** Alternate Target = " + sub_198c(oLocal4));
    }
    sub_1964("GENERIC DEBUG *************** Heal Drain Target = " + sub_2151(nParam1));
    sub_1964("GENERIC DEBUG *************** Get Active Party Member: " + sub_198c(oLocal4));
    return oLocal4;
}

// verified: recompiles to the original bytes
int sub_47d5()
{
    object oLocal1;
    if (GetIsObjectValid(GetAttackTarget()) && GetDistanceBetween(GetAttackTarget(), OBJECT_SELF) <= 3.0 && sub_5169(OBJECT_SELF) != 1 && GetRacialType(OBJECT_SELF) == 6 && !IsObjectPartyMember(OBJECT_SELF)) {
        oLocal1 = GetFirstItemInInventory();
        while (GetIsObjectValid(oLocal1)) {
            sub_1964("GENERIC DEBUG *************** Checking Melee Weapon");
            if (GetBaseItemType(oLocal1) == 9 || GetBaseItemType(oLocal1) == 6 || GetBaseItemType(oLocal1) == 80 || GetBaseItemType(oLocal1) == 78 || GetBaseItemType(oLocal1) == 8 || GetBaseItemType(oLocal1) == 2 || GetBaseItemType(oLocal1) == 0 || GetBaseItemType(oLocal1) == 10 || GetBaseItemType(oLocal1) == 4 || GetBaseItemType(oLocal1) == 1 || GetBaseItemType(oLocal1) == 5 || GetBaseItemType(oLocal1) == 7 || GetBaseItemType(oLocal1) == 3 || GetBaseItemType(oLocal1) == 79) {
                sub_1964("GENERIC DEBUG *************** Equipping Melee Weapon");
                ActionEquipMostDamagingMelee();
                return 1;
            } else {
                oLocal1 = GetNextItemInInventory();
            }
        }
    } else if (sub_5169(OBJECT_SELF) != 2 && GetLevelByClass(4) == 0 && GetLevelByClass(3) == 0 && GetLevelByClass(5) == 0 && GetDistanceBetween(GetAttemptedAttackTarget(), OBJECT_SELF) > 3.0 && !IsObjectPartyMember(OBJECT_SELF)) {
        oLocal1 = GetFirstItemInInventory();
        while (GetIsObjectValid(oLocal1)) {
            sub_1964("GENERIC DEBUG *************** Checking Ranged Weapon");
            if (GetBaseItemType(oLocal1) == 20 || GetBaseItemType(oLocal1) == 12 || GetBaseItemType(oLocal1) == 77 || GetBaseItemType(oLocal1) == 19 || GetBaseItemType(oLocal1) == 16 || GetBaseItemType(oLocal1) == 21 || GetBaseItemType(oLocal1) == 13 || GetBaseItemType(oLocal1) == 24 || GetBaseItemType(oLocal1) == 14 || GetBaseItemType(oLocal1) == 15 || GetBaseItemType(oLocal1) == 18 || GetBaseItemType(oLocal1) == 23 || GetBaseItemType(oLocal1) == 17 || GetBaseItemType(oLocal1) == 22 || GetBaseItemType(oLocal1) == 17) {
                sub_1964("GENERIC DEBUG *************** Equipping Ranged Weapon");
                ActionEquipMostDamagingRanged();
                return 1;
            } else {
                oLocal1 = GetNextItemInInventory();
            }
        }
    }
    sub_1964("GENERIC DEBUG *************** Should not currently change weapons");
    return 0;
}

// verified: recompiles to the original bytes
int sub_5169(object oParam1)
{
    object oLocal1 = GetItemInSlot(4, oParam1);
    if (GetIsObjectValid(oLocal1)) {
        if (GetBaseItemType(oLocal1) == 20 || GetBaseItemType(oLocal1) == 12 || GetBaseItemType(oLocal1) == 77 || GetBaseItemType(oLocal1) == 19 || GetBaseItemType(oLocal1) == 16 || GetBaseItemType(oLocal1) == 21 || GetBaseItemType(oLocal1) == 13 || GetBaseItemType(oLocal1) == 24 || GetBaseItemType(oLocal1) == 14 || GetBaseItemType(oLocal1) == 15 || GetBaseItemType(oLocal1) == 18 || GetBaseItemType(oLocal1) == 23 || GetBaseItemType(oLocal1) == 17 || GetBaseItemType(oLocal1) == 22 || GetBaseItemType(oLocal1) == 17) {
            return 2;
        } else if (GetBaseItemType(oLocal1) == 9 || GetBaseItemType(oLocal1) == 6 || GetBaseItemType(oLocal1) == 80 || GetBaseItemType(oLocal1) == 78 || GetBaseItemType(oLocal1) == 8 || GetBaseItemType(oLocal1) == 2 || GetBaseItemType(oLocal1) == 0 || GetBaseItemType(oLocal1) == 10 || GetBaseItemType(oLocal1) == 4 || GetBaseItemType(oLocal1) == 1 || GetBaseItemType(oLocal1) == 5 || GetBaseItemType(oLocal1) == 7 || GetBaseItemType(oLocal1) == 3 || GetBaseItemType(oLocal1) == 79) {
            return 1;
        }
    }
    sub_1964("GENERIC DEBUG *************** Return No Weapon Type");
    return 0;
}

// verified: recompiles to the original bytes
int sub_57f3()
{
    sub_1964("GENERIC DEBUG *************** Boss AI: Grenade Function Starting");
    talent tLocal1;
    object oLocal2 = sub_5a4d();
    sub_1964("GENERIC DEBUG *************** Boss AI: Grenade Target = " + sub_2151(GetIsObjectValid(oLocal2)));
    int nLocal3;
    if (GetIsObjectValid(oLocal2)) {
        if (GetRacialType(oLocal2) == 5) {
            nLocal3 == 1;
        }
        tLocal1 = sub_5f44(nGlobal1, nLocal3);
        if (GetIsTalentValid(tLocal1)) {
            sub_1964("GENERIC DEBUG *************** Clear 1460");
            ClearAllActions();
            ActionUseTalentOnObject(tLocal1, oLocal2);
            sub_1964("GENERIC DEBUG *************** Boss AI: AOE Success");
            return 1;
        }
    }
    sub_1964("GENERIC DEBUG *************** Boss AI: AOE Failure");
    return 0;
}

// verified: recompiles to the original bytes
object sub_5a4d()
{
    int nLocal1 = 0;
    if (IsObjectPartyMember(OBJECT_SELF)) {
        nLocal1 = 1;
    }
    int nLocal2 = 0;
    int nLocal3 = 0;
    int nLocal4 = 0;
    object oLocal5;
    object oLocal6;
    for (oLocal6 = GetFirstObjectInShape(4, 40.0, GetLocation(OBJECT_SELF)); GetIsObjectValid(oLocal6); oLocal6 = GetNextObjectInShape(4, 40.0, GetLocation(OBJECT_SELF))) {
        if (GetObjectSeen(oLocal6) && !GetIsDead(oLocal6)) {
            nLocal2 = sub_5cb9(oLocal6, 4.0);
            nLocal3 = sub_5e0d(oLocal6, 4.0);
            if (nLocal3 > nLocal1 && nLocal2 == 0 && nLocal4 < nLocal3) {
                oLocal5 = oLocal6;
                nLocal4 = nLocal3;
            }
        }
    }
    return oLocal5;
}

// verified: recompiles to the original bytes
int sub_5cb9(object oParam1, float fParam2)
{
    int nLocal1;
    int nLocal2;
    int nLocal3 = GetHitDice(OBJECT_SELF);
    object oLocal4;
    for (oLocal4 = GetFirstObjectInShape(4, fParam2, GetLocation(oParam1)); GetIsObjectValid(oLocal4); oLocal4 = GetNextObjectInShape(4, fParam2, GetLocation(oParam1))) {
        if (GetIsFriend(oLocal4) && !GetIsDead(oLocal4)) {
            nLocal1++;
        }
    }
    return nLocal1;
}

// verified: recompiles to the original bytes
int sub_5e0d(object oParam1, float fParam2)
{
    int nLocal1;
    object oLocal2;
    for (oLocal2 = GetFirstObjectInShape(4, fParam2, GetLocation(oParam1)); GetIsObjectValid(oLocal2); oLocal2 = GetNextObjectInShape(4, fParam2, GetLocation(oParam1))) {
        if (GetIsEnemy(oLocal2) && !GetIsDead(oLocal2)) {
            nLocal1++;
        }
    }
    return nLocal1;
}

// verified: recompiles to the original bytes
talent sub_5f44(int nParam1, int nParam2)
{
    talent tLocal1;
    talent tLocal2;
    int nLocal3 = 0;
    if (nParam1 == nGlobal1 || nParam1 == nGlobal5) {
        tLocal2 = sub_662b(nParam2);
        if (GetIsTalentValid(tLocal2)) {
            sub_1964("GENERIC DEBUG *************** Boss AI: Grenade Talent Chosen");
            return tLocal2;
        }
    }
    if (nParam1 == nGlobal2 || nParam1 == nGlobal5) {
        tLocal2 = sub_70e7(nParam2);
        if (GetIsTalentValid(tLocal2)) {
            sub_1964("GENERIC DEBUG *************** Boss AI: AOE Force Power Talent Chosen");
            return tLocal2;
        }
    }
    if (nParam1 == nGlobal3 || nParam1 == nGlobal5) {
        if (d100() > 50) {
            tLocal2 = sub_7e10(nParam2);
            if (GetIsTalentValid(tLocal2)) {
                sub_1964("GENERIC DEBUG *************** Boss AI: Targeted Force Power Talent Chosen");
                return tLocal2;
            }
            tLocal2 = sub_70e7(nParam2);
            if (GetIsTalentValid(tLocal2)) {
                sub_1964("GENERIC DEBUG *************** Boss AI: AOE Force Power Talent Chosen");
                return tLocal2;
            }
        }
        if (sub_5169(OBJECT_SELF) == 1) {
            sub_1964("GENERIC DEBUG *************** Boss AI: Melee Feat Talent Chosen");
            tLocal2 = GetCreatureTalentRandom(4356);
        } else {
            sub_1964("GENERIC DEBUG *************** Boss AI: Range Feat Talent Chosen");
            tLocal2 = GetCreatureTalentRandom(4369);
        }
        if (GetIsTalentValid(tLocal2)) {
            return tLocal2;
        }
    } else if (nParam1 == nGlobal4 || nParam1 == nGlobal5) {
        if (d100() > 70) {
            tLocal2 = sub_7e10(nParam2);
            if (GetIsTalentValid(tLocal2)) {
                return tLocal2;
            }
            tLocal2 = sub_70e7(nParam2);
            if (GetIsTalentValid(tLocal2)) {
                return tLocal2;
            }
        }
        tLocal2 = GetCreatureTalentRandom(4356);
        if (GetIsTalentValid(tLocal2)) {
            return tLocal2;
        }
        sub_1964("GENERIC DEBUG *************** Boss AI: No Feats Available");
    }
    return tLocal2;
}

// verified: recompiles to the original bytes
talent sub_662b(int nParam1)
{
    talent tLocal1;
    int nLocal2;
    int nLocal3;
    int nLocal4;
    int nLocal5;
    int nLocal6;
    int nLocal7;
    int nLocal8;
    int nLocal9;
    int nLocal10;
    int nLocal11 = 0;
    int nLocal12 = 0;
    int nLocal13 = 87;
    nLocal13;
    while (nLocal13 < 96) {
        tLocal1 = TalentSpell(nLocal13);
        if (GetCreatureHasTalent(tLocal1)) {
            switch (nLocal13) {
                case 87:
                    nLocal2 = 1;
                    nLocal11++;
                    break;
                case 88:
                    if (nParam1 == 0) {
                        nLocal3 = 1;
                        nLocal11++;
                    }
                    break;
                case 89:
                    nLocal4 = 1;
                    nLocal11++;
                    break;
                case 90:
                    if (nParam1 == 0) {
                        nLocal5 = 1;
                        nLocal11++;
                    }
                    break;
                case 91:
                    if (nParam1 == 0) {
                        nLocal6 = 1;
                        nLocal11++;
                    }
                    break;
                case 92:
                    if (nParam1 == 0) {
                        nLocal7 = 1;
                        nLocal11++;
                    }
                    break;
                case 93:
                    if (nParam1 == 0) {
                        nLocal8 = 1;
                        nLocal11++;
                    }
                    break;
                case 94:
                    nLocal9 = 1;
                    nLocal11++;
                    break;
                case 95:
                    if (nParam1 == 1) {
                        nLocal10 = 1;
                        nLocal11++;
                    }
                    break;
                default:
            }
        }
        nLocal13++;
    }
    int nLocal14;
    if (nLocal11 > 0) {
        nLocal14 = Random(nLocal11) + 1;
    } else {
        nLocal14 = 0;
    }
    if (nLocal11 > 0) {
        if (nLocal14 == 1 && nLocal2 == 1) {
            return tLocal1 = TalentSpell(87);
        }
        if (nLocal14 > 1 && nLocal2 == 1) {
            nLocal14--;
        }
        if (nLocal14 == 1 && nLocal3 == 1) {
            return tLocal1 = TalentSpell(88);
        }
        if (nLocal14 > 1 && nLocal3 == 1) {
            nLocal14--;
        }
        if (nLocal14 == 1 && nLocal4 == 1) {
            return tLocal1 = TalentSpell(89);
        }
        if (nLocal14 > 1 && nLocal4 == 1) {
            nLocal14--;
        }
        if (nLocal14 == 1 && nLocal5 == 1) {
            return tLocal1 = TalentSpell(90);
        }
        if (nLocal14 > 1 && nLocal5 == 1) {
            nLocal14--;
        }
        if (nLocal14 == 1 && nLocal6 == 1) {
            return tLocal1 = TalentSpell(91);
        }
        if (nLocal14 > 1 && nLocal6 == 1) {
            nLocal14--;
        }
        if (nLocal14 == 1 && nLocal7 == 1) {
            return tLocal1 = TalentSpell(92);
        }
        if (nLocal14 > 1 && nLocal7 == 1) {
            nLocal14--;
        }
        if (nLocal14 == 1 && nLocal8 == 1) {
            return tLocal1 = TalentSpell(93);
        }
        if (nLocal14 > 1 && nLocal8 == 1) {
            nLocal14--;
        }
        if (nLocal14 == 1 && nLocal9 == 1) {
            return tLocal1 = TalentSpell(94);
        }
        if (nLocal14 > 1 && nLocal9 == 1) {
            nLocal14--;
        }
    }
    sub_1964("GENERIC DEBUG *************** Grenade Selection Failure");
    talent tLocal15;
    return tLocal15;
    return tLocal15;
}

// verified: recompiles to the original bytes
talent sub_70e7(int nParam1)
{
    talent tLocal1;
    int nLocal2;
    int nLocal3;
    int nLocal4;
    int nLocal5;
    int nLocal6;
    int nLocal7;
    int nLocal8;
    int nLocal9;
    int nLocal10;
    int nLocal11;
    int nLocal12;
    int nLocal13 = GetLastForcePowerUsed();
    sub_1964("GENERIC DEBUG *************** Last Force Power Used = " + sub_2151(nLocal13));
    if (GetHasSpell(30) && nParam1 == 0 && nLocal13 != 30) {
        nLocal2 = 1;
        nLocal12++;
    }
    if (GetHasSpell(31) && nParam1 == 0 && nLocal13 != 31) {
        nLocal3 = 1;
        nLocal12++;
    }
    if (GetHasSpell(25) && nLocal13 != 25) {
        nLocal4 = 1;
        nLocal12++;
    }
    if (GetHasSpell(26) && nLocal13 != 26) {
        nLocal5 = 1;
        nLocal12++;
    }
    if (GetHasSpell(4) && nLocal13 != 4) {
        nLocal6 = 1;
        nLocal12++;
    }
    if (GetHasSpell(35) && nLocal13 != 35) {
        nLocal7 = 1;
        nLocal12++;
    }
    if (GetHasSpell(44) && nParam1 == 0 && nLocal13 != 44) {
        nLocal8 = 1;
        nLocal12++;
    }
    if (GetHasSpell(47) && nParam1 == 1 && nLocal13 != 47) {
        nLocal9 = 1;
        nLocal12++;
    }
    if (GetHasSpell(13) && nParam1 == 1 && nLocal13 != 13) {
        nLocal10 = 1;
        nLocal12++;
    }
    talent tLocal14 = TalentSpell(131);
    if (GetCreatureHasTalent(tLocal14)) {
        nLocal11 = 1;
        nLocal12++;
    }
    int nLocal15;
    if (nLocal12 > 0) {
        nLocal15 = Random(nLocal12) + 1;
    } else {
        nLocal15 = 0;
    }
    if (nLocal2 == 1 && nLocal15 == 1) {
        tLocal1 = TalentSpell(30);
        nLocal15--;
    }
    if (nLocal2 == 1 && nLocal15 > 1) {
        nLocal15--;
    }
    if (nLocal3 == 1 && nLocal15 == 1) {
        tLocal1 = TalentSpell(31);
        nLocal15--;
    }
    if (nLocal2 == 1 && nLocal15 > 1) {
        nLocal15--;
    }
    if (nLocal4 == 1 && nLocal15 == 1) {
        tLocal1 = TalentSpell(25);
        nLocal15--;
    }
    if (nLocal4 == 1 && nLocal15 > 1) {
        nLocal15--;
    }
    if (nLocal5 == 1 && nLocal15 == 1) {
        tLocal1 = TalentSpell(26);
        nLocal15--;
    }
    if (nLocal5 == 1 && nLocal15 > 1) {
        nLocal15--;
    }
    if (nLocal6 == 1 && nLocal15 == 1) {
        tLocal1 = TalentSpell(4);
        nLocal15--;
    }
    if (nLocal6 == 1 && nLocal15 > 1) {
        nLocal15--;
    }
    if (nLocal7 == 1 && nLocal15 == 1) {
        tLocal1 = TalentSpell(35);
        nLocal15--;
    }
    if (nLocal7 == 1 && nLocal15 > 1) {
        nLocal15--;
    }
    if (nLocal8 == 1 && nLocal15 == 1) {
        tLocal1 = TalentSpell(44);
        nLocal15--;
    }
    if (nLocal8 == 1 && nLocal15 > 1) {
        nLocal15--;
    }
    if (nLocal9 == 1 && nLocal15 == 1) {
        tLocal1 = TalentSpell(47);
        nLocal15--;
    }
    if (nLocal9 == 1 && nLocal15 > 1) {
        nLocal15--;
    }
    if (nLocal10 == 1 && nLocal15 == 1) {
        tLocal1 = TalentSpell(13);
        nLocal15--;
    }
    if (nLocal10 == 1 && nLocal15 > 1) {
        nLocal15--;
    }
    if (nLocal10 == 1 && nLocal15 == 1) {
        tLocal1 = TalentSpell(131);
        nLocal15--;
    }
    if (nLocal11 == 1 && nLocal15 > 1) {
        nLocal15--;
    }
    sub_1964("GENERIC DEBUG *************** Force Power Returned = " + sub_2151(GetIdFromTalent(tLocal1)));
    return tLocal1;
}

// verified: recompiles to the original bytes
talent sub_7e10(int nParam1)
{
    talent tLocal1;
    int nLocal2;
    int nLocal3;
    int nLocal4;
    int nLocal5;
    int nLocal6;
    int nLocal7;
    int nLocal8;
    int nLocal9;
    int nLocal10;
    int nLocal11;
    int nLocal12;
    int nLocal13;
    int nLocal14;
    int nLocal15;
    if (GetRacialType(OBJECT_SELF) == 5) {
        tLocal1 = GetCreatureTalentRandom(32768);
        if (GetIsTalentValid(tLocal1)) {
            return tLocal1;
        }
    }
    if (GetHasSpell(9) && nLocal12 == 0) {
        nLocal2 = 1;
        nLocal15++;
    }
    if (GetHasSpell(7) && nLocal12 == 0) {
        nLocal3 = 1;
        nLocal15++;
    }
    if (GetHasSpell(38) && nLocal12 == 0) {
        nLocal4 = 1;
        nLocal15++;
    }
    if (GetHasSpell(23)) {
        nLocal5 = 1;
        nLocal15++;
    }
    if (GetHasSpell(27)) {
        nLocal6 = 1;
        nLocal15++;
    }
    if (GetHasSpell(35)) {
        nLocal7 = 1;
        nLocal15++;
    }
    if (GetHasSpell(32) && nLocal12 == 0) {
        nLocal8 = 1;
        nLocal15++;
    }
    if (GetHasSpell(30) && nLocal12 == 0) {
        nLocal9 = 1;
        nLocal15++;
    }
    if (GetHasSpell(50) && nLocal12 == 0) {
        nLocal10 = 1;
        nLocal15++;
    }
    if (GetHasSpell(29)) {
        nLocal11 = 1;
        nLocal15++;
    }
    if (GetHasSpell(12) && nLocal12 == 1) {
        nLocal12 = 1;
        nLocal15++;
    }
    talent tLocal16 = TalentSpell(83);
    if (GetCreatureHasTalent(tLocal16)) {
        nLocal13 = 1;
        nLocal15++;
    }
    int nLocal17;
    if (nLocal15 > 0) {
        nLocal17 = Random(nLocal15) + 1;
    } else {
        nLocal17 = 0;
    }
    if (nLocal2 == 1 && nLocal17 == 1) {
        tLocal1 = TalentSpell(9);
        nLocal17--;
    }
    if (nLocal2 == 1 && nLocal17 > 1) {
        nLocal17--;
    }
    if (nLocal3 == 1 && nLocal17 == 1) {
        tLocal1 = TalentSpell(7);
        nLocal17--;
    }
    if (nLocal3 == 1 && nLocal17 > 1) {
        nLocal17--;
    }
    if (nLocal4 == 1 && nLocal17 == 1) {
        tLocal1 = TalentSpell(7);
        nLocal17--;
    }
    if (nLocal4 == 1 && nLocal17 > 1) {
        nLocal17--;
    }
    if (nLocal5 == 1 && nLocal17 == 1) {
        tLocal1 = TalentSpell(23);
        nLocal17--;
    }
    if (nLocal5 == 1 && nLocal17 > 1) {
        nLocal17--;
    }
    if (nLocal6 == 1 && nLocal17 == 1) {
        tLocal1 = TalentSpell(27);
        nLocal17--;
    }
    if (nLocal6 == 1 && nLocal17 > 1) {
        nLocal17--;
    }
    if (nLocal7 == 1 && nLocal17 == 1) {
        tLocal1 = TalentSpell(35);
        nLocal17--;
    }
    if (nLocal7 == 1 && nLocal17 > 1) {
        nLocal17--;
    }
    if (nLocal8 == 1 && nLocal17 == 1) {
        tLocal1 = TalentSpell(32);
        nLocal17--;
    }
    if (nLocal8 == 1 && nLocal17 > 1) {
        nLocal17--;
    }
    if (nLocal9 == 1 && nLocal17 == 1) {
        tLocal1 = TalentSpell(30);
        nLocal17--;
    }
    if (nLocal9 == 1 && nLocal17 > 1) {
        nLocal17--;
    }
    if (nLocal10 == 1 && nLocal17 == 1) {
        tLocal1 = TalentSpell(50);
        nLocal17--;
    }
    if (nLocal10 == 1 && nLocal17 > 1) {
        nLocal17--;
    }
    if (nLocal11 == 1 && nLocal17 == 1) {
        tLocal1 = TalentSpell(29);
        nLocal17--;
    }
    if (nLocal11 == 1 && nLocal17 > 1) {
        nLocal17--;
    }
    if (nLocal12 == 1 && nLocal17 == 1) {
        tLocal1 = TalentSpell(12);
        nLocal17--;
    }
    if (nLocal12 == 1 && nLocal17 > 1) {
        nLocal17--;
    }
    if (nLocal13 == 1 && nLocal17 == 1) {
        tLocal1 = TalentSpell(83);
        nLocal17--;
    }
    if (nLocal13 == 1 && nLocal17 > 1) {
        nLocal17--;
    }
    return tLocal1;
}

// verified: recompiles to the original bytes
int sub_8c17()
{
    sub_1964("GENERIC DEBUG *************** Boss AI: AOE Function Starting");
    talent tLocal1;
    object oLocal2 = sub_8e37();
    sub_1964("GENERIC DEBUG *************** Boss AI: AOE Target = " + sub_2151(GetIsObjectValid(oLocal2)));
    int nLocal3;
    if (GetIsObjectValid(oLocal2)) {
        if (GetRacialType(oLocal2) == 5) {
            nLocal3 == 1;
        }
        tLocal1 = sub_5f44(nGlobal2, nLocal3);
        if (GetIsTalentValid(tLocal1)) {
            ClearAllActions();
            ActionUseTalentOnObject(tLocal1, oLocal2);
            sub_1964("GENERIC DEBUG *************** Boss AI: AOE Success");
            return 1;
        }
    }
    sub_1964("GENERIC DEBUG *************** Boss AI: AOE Failure");
    return 0;
}

// verified: recompiles to the original bytes
object sub_8e37()
{
    int nLocal1 = 0;
    int nLocal2 = 0;
    object oLocal3;
    object oLocal4;
    for (oLocal4 = GetFirstObjectInShape(4, 30.0, GetLocation(OBJECT_SELF)); GetIsObjectValid(oLocal4); oLocal4 = GetNextObjectInShape(4, 30.0, GetLocation(OBJECT_SELF))) {
        nLocal1 = sub_5e0d(oLocal4, 4.0);
        if (nLocal1 > 2 && nLocal2 < nLocal1) {
            oLocal3 = oLocal4;
            nLocal2 = nLocal1;
        }
    }
    return oLocal3;
}

// verified: recompiles to the original bytes
int sub_8fc8()
{
    sub_1964("GENERIC DEBUG *************** Boss AI: Start Targeted Action Routine");
    talent tLocal1;
    object oLocal2;
    int nLocal3;
    int nLocal4 = d6();
    int nLocal5 = 1;
    if (nLocal4 < 4) {
        nLocal4 = 1;
    }
    if (nLocal4 == 4) {
        nLocal4 = 2;
    }
    if (nLocal4 == 5) {
        nLocal4 = 3;
    }
    if (nLocal4 == 6) {
        nLocal4 = 4;
    }
    sub_1964("GENERIC DEBUG *************** Boss AI: Get the #" + sub_2151(nLocal4) + " target");
    object oLocal6 = GetNearestCreature(3, 1, OBJECT_SELF, nLocal5, 7, 7);
    sub_1964("GENERIC DEBUG *************** Boss AI: Initial oFind Search = " + sub_198c(oLocal6));
    while (GetIsObjectValid(oLocal6) && nLocal5 <= nLocal4) {
        sub_1964("GENERIC DEBUG *************** Boss AI: Valid oFind = " + sub_198c(oLocal6) + " nCnt = " + sub_2151(nLocal5));
        if (GetIsObjectValid(oLocal6)) {
            sub_1964("GENERIC DEBUG *************** Boss AI: Valid oTarget Set As = " + sub_198c(oLocal6));
            oLocal2 = oLocal6;
        }
        nLocal5++;
        oLocal6 = GetNearestCreature(3, 1, OBJECT_SELF, nLocal5, 7, 7);
    }
    int nLocal7 = 1;
    if (nLocal7 == 1) {
        if (GetIsTalentValid(tLocal1)) {
            if (GetTypeFromTalent(tLocal1) == 1) {
                sub_1964("GENERIC DEBUG *************** Boss AI: Talent Feat = " + sub_2151(GetIdFromTalent(tLocal1)));
            } else if (GetTypeFromTalent(tLocal1) == 0) {
                sub_1964("GENERIC DEBUG *************** Boss AI: Talent Power = " + sub_2151(GetIdFromTalent(tLocal1)));
            }
        }
    }
    if (GetIsObjectValid(oLocal2)) {
        if (GetRacialType(oLocal2) == 5) {
            sub_1964("GENERIC DEBUG *************** Boss AI: Get Boss Combat Move AI Droid");
            nLocal3 = 1;
        }
        tLocal1 = sub_5f44(nGlobal3, nLocal3);
        tLocal1 = sub_979f(oLocal2, tLocal1);
        tLocal1 = sub_99df(oLocal2, tLocal1);
        sub_1964("GENERIC DEBUG *************** Boss AI: Target = " + sub_2151(GetIsObjectValid(oLocal2)));
        sub_1964("GENERIC DEBUG *************** Boss AI: Talent = " + sub_2151(GetIsTalentValid(tLocal1)));
        if (GetIsTalentValid(tLocal1) && GetIsObjectValid(oLocal2)) {
            ClearAllActions();
            ActionUseTalentOnObject(tLocal1, oLocal2);
            sub_1964("GENERIC DEBUG *************** Boss AI: Targeted Power Success");
            return 1;
        }
    }
    sub_1964("GENERIC DEBUG *************** Boss AI: Targeted Failure");
    return 0;
}

// verified: recompiles to the original bytes
talent sub_979f(object oParam1, talent tParam2)
{
    int nLocal1 = 0;
    if (GetTypeFromTalent(tParam2) == 0) {
        if (GetIdFromTalent(tParam2) == 49 || GetIdFromTalent(tParam2) == 4) {
            sub_1964("GENERIC DEBUG *************** Lightsaber Throw Check = " + FloatToString(GetDistanceBetween(OBJECT_SELF, oParam1), 4, 2));
            if (GetDistanceBetween(OBJECT_SELF, oParam1) < 10.0) {
                nLocal1 = 1;
            }
        }
    }
    if (nLocal1 == 1) {
        talent tLocal2 = GetCreatureTalentBest(4356, 20);
        if (GetIsTalentValid(tParam2) && GetCreatureHasTalent(tParam2)) {
            return tLocal2;
        } else {
            talent tLocal3;
            return tLocal3;
        }
    }
    return tParam2;
}

// verified: recompiles to the original bytes
talent sub_99df(object oParam1, talent tParam2)
{
    int nLocal1 = 0;
    if (GetTypeFromTalent(tParam2) == 0) {
        if (GetIdFromTalent(tParam2) == 29 || GetIdFromTalent(tParam2) == 30 || GetIdFromTalent(tParam2) == 31 || GetIdFromTalent(tParam2) == 32 || GetIdFromTalent(tParam2) == 38 || GetIdFromTalent(tParam2) == 44 || GetIdFromTalent(tParam2) == 45 || GetIdFromTalent(tParam2) == 46 || GetIdFromTalent(tParam2) == 50 || GetIdFromTalent(tParam2) == 7 || GetIdFromTalent(tParam2) == 9 || GetIdFromTalent(tParam2) == 11 || GetIdFromTalent(tParam2) == 15 || GetIdFromTalent(tParam2) == 16) {
            if (GetRacialType(oParam1) == 5) {
                nLocal1 = 1;
            }
        }
    }
    if (nLocal1 == 1) {
        talent tLocal2 = GetCreatureTalentBest(4356, 20);
        if (GetIsTalentValid(tParam2) && GetCreatureHasTalent(tParam2)) {
            return tLocal2;
        } else {
            talent tLocal3;
            return tLocal3;
        }
    }
    return tParam2;
}

// verified: recompiles to the original bytes
int sub_9e16(object oParam1)
{
    object oLocal1;
    object oLocal2;
    int nLocal3;
    talent tLocal4;
    oLocal1 = sub_a74c();
    if (GetIsObjectValid(oLocal1)) {
        if (sub_3105(nGlobal107, oLocal1)) {
            return 1;
        }
    }
    oLocal1 = sub_2b8a();
    if (GetIsObjectValid(oLocal1)) {
        if (sub_3105(nGlobal108, oLocal1)) {
            return 1;
        }
    }
    tLocal4 = sub_a999(0);
    int nLocal5 = GetLocalBoolean(OBJECT_SELF, nGlobal42);
    if (nLocal5 == 1) {
        if (GetNPCAIStyle(OBJECT_SELF) == 5) {
            oLocal1 = GetPartyMemberByIndex(0);
        } else {
            oLocal1 = OBJECT_SELF;
        }
    } else {
        oLocal1 = stGlobal62.f3;
        oLocal2 = GetNearestCreature(3, 1, OBJECT_SELF, 1, 7, 7);
        sub_1964("GENERIC DEBUG *************** Default AI Debug Start *************************");
        sub_1964("GENERIC DEBUG *************** Intruder    = " + sub_198c(oParam1));
        sub_1964("GENERIC DEBUG *************** Last Target = " + sub_198c(oLocal1));
        sub_1964("GENERIC DEBUG *************** Closest     = " + sub_198c(oLocal2));
        if (IsObjectPartyMember(OBJECT_SELF) && GetIsObjectValid(oLocal1) && !GetIsDead(oLocal1) && GetObjectSeen(oLocal1)) {
            oLocal1 = oLocal1;
        } else if (GetIsObjectValid(oParam1) && GetObjectSeen(oParam1)) {
            sub_1964("GENERIC DEBUG *************** Intruder becomes Target");
            oLocal1 = oParam1;
        } else if (GetIsObjectValid(oLocal2) && GetObjectSeen(oLocal2)) {
            if (!GetIsObjectValid(oLocal1) || !GetIsEnemy(oLocal1) || GetIsDead(oLocal1) || GetCurrentHitPoints(oLocal1) < GetCurrentHitPoints(oLocal2)) {
                sub_1964("GENERIC DEBUG *************** Closest becomes Target");
                oLocal1 = oLocal2;
            }
        }
    }
    if (GetRacialType(OBJECT_SELF) == 5) {
        tLocal4 = sub_fba8(oLocal1, tLocal4);
    }
    tLocal4 = sub_979f(oLocal1, tLocal4);
    tLocal4 = sub_99df(oLocal1, tLocal4);
    sub_1964("GENERIC DEBUG *************** Default AI Debug End ***************************");
    sub_1964("GENERIC DEBUG *************** Target = " + sub_198c(oLocal1) + " is Enemy: " + IntToString(GetIsEnemy(oLocal1)));
    if (GetIsObjectValid(oLocal1)) {
        sub_1964("GENERIC DEBUG *************** Clear 1300");
        ClearAllActions();
        if (sub_47d5()) {
            sub_1964("GENERIC DEBUG *************** Switching Weapons");
        }
        if (GetIsTalentValid(tLocal4) && GetIsEnemy(oLocal1)) {
            sub_1964("GENERIC DEBUG *************** Using Talent on Target");
            ActionUseTalentOnObject(tLocal4, oLocal1);
            return 1;
        } else if (GetIsEnemy(oLocal1)) {
            sub_1964("GENERIC DEBUG *************** Action Attack by Default");
            ActionAttack(oLocal1);
            return 1;
        }
    }
    sub_1964("GENERIC DEBUG *************** Default AI has failed to do an action");
    return 0;
}

// verified: recompiles to the original bytes
object sub_a74c()
{
    sub_1964("GENERIC DEBUG *************** Starting Poison Check");
    effect eLocal1;
    if (IsObjectPartyMember(OBJECT_SELF)) {
        int nLocal2 = 0;
        nLocal2;
        while (nLocal2 > 2) {
            for (eLocal1 = GetFirstEffect(GetPartyMemberByIndex(nLocal2)); GetIsEffectValid(eLocal1); eLocal1 = GetNextEffect(GetPartyMemberByIndex(nLocal2))) {
                if (GetEffectType(eLocal1) == 31) {
                    return GetPartyMemberByIndex(nLocal2);
                }
            }
            nLocal2++;
        }
    } else {
        for (eLocal1 = GetFirstEffect(OBJECT_SELF); GetIsEffectValid(eLocal1); eLocal1 = GetNextEffect(OBJECT_SELF)) {
            if (GetEffectType(eLocal1) == 31) {
                return OBJECT_SELF;
            }
        }
    }
    sub_1964("GENERIC DEBUG ***************  Returning Invalid Poison Object");
    return OBJECT_INVALID;
}

// verified: recompiles to the original bytes
talent sub_a999(int nParam1)
{
    int nLocal1;
    int nLocal2;
    talent tLocal3;
    int nLocal4 = GetNPCAIStyle(OBJECT_SELF);
    sub_1964("GENERIC DEBUG *************** Starting GetComboMove");
    if (stGlobal62.f7 == 4 || stGlobal62.f7 == 0) {
        SetLocalNumber(OBJECT_SELF, nGlobal8, 0);
        SetLocalNumber(OBJECT_SELF, nGlobal7, 0);
        nLocal1 = d6();
        if (nLocal1 > 0) {
            if (GetLevelByClass(4) > 0 || GetLevelByClass(3) > 0 || GetLevelByClass(5) > 0) {
                nLocal2 = sub_aedc(nParam1);
                sub_1964("GENERIC DEBUG *************** Starting Jedi Combo " + sub_cea1(nLocal2));
                SetLocalNumber(OBJECT_SELF, nGlobal8, 1);
                SetLocalNumber(OBJECT_SELF, nGlobal7, nLocal2);
                return sub_d7df(nLocal2);
            } else if (GetLevelByClass(6) > 0 || GetLevelByClass(7) > 0) {
                nLocal2 = sub_f621(nParam1);
                sub_1964("GENERIC DEBUG *************** Starting Droid Combo " + sub_cea1(nLocal2));
                SetLocalNumber(OBJECT_SELF, nGlobal8, 1);
                SetLocalNumber(OBJECT_SELF, nGlobal7, nLocal2);
                return sub_d7df(nLocal2);
            } else {
                nLocal2 = sub_f8e2(nParam1);
                sub_1964("GENERIC DEBUG *************** Starting NPC Combo " + sub_cea1(nLocal2));
                SetLocalNumber(OBJECT_SELF, nGlobal8, 1);
                SetLocalNumber(OBJECT_SELF, nGlobal7, nLocal2);
                return sub_d7df(nLocal2);
            }
        } else {
            return tLocal3;
        }
    } else {
        sub_1964("GENERIC DEBUG *************** Continuing Combo " + sub_cea1(stGlobal62.f8));
        return sub_d7df(stGlobal62.f8);
    }
    return tLocal3;
}

// verified: recompiles to the original bytes
int sub_aedc(int nParam1)
{
    int nLocal1;
    int nLocal2;
    while (nLocal1 == 0) {
        if (nParam1 == 0) {
            nLocal2 = Random(23) + 1;
            if (nLocal2 == 1 || nLocal2 == 2) {
                return nGlobal16;
            } else if (nLocal2 == 3 || nLocal2 == 4) {
                return nGlobal17;
            } else if (nLocal2 == 5 || nLocal2 == 6) {
                return nGlobal18;
            } else if (nLocal2 == 7 || nLocal2 == 8 || nLocal2 == 9) {
                return nGlobal19;
            } else if (nLocal2 >= 10 || nLocal2 <= 24) {
                nLocal2 = nLocal2 + 3;
            }
        } else {
            nLocal2 = Random(15);
            nLocal2 = nLocal2 + 13;
        }
        nLocal1 = sub_b204(nLocal2);
    }
    return nLocal2;
}

// verified: recompiles to the original bytes
int sub_b204(int nParam1)
{
    if (nParam1 == nGlobal41) {
        return 0;
    }
    talent tLocal1;
    talent tLocal2;
    if (nParam1 == nGlobal16 || nParam1 == nGlobal17 || nParam1 == nGlobal18) {
        tLocal1 = GetCreatureTalentRandom(4356);
        if (GetIsTalentValid(tLocal1) && GetCreatureHasTalent(tLocal1)) {
            return 1;
        }
    } else if (nParam1 == nGlobal15) {
        return 1;
    } else if (nParam1 == nGlobal12 || nParam1 == nGlobal13 || nParam1 == nGlobal14) {
        if (GetHasFeat(31) || GetHasFeat(20) || GetHasFeat(77) || GetHasFeat(29) || GetHasFeat(18) || GetHasFeat(82) || GetHasFeat(30) || GetHasFeat(26) || GetHasFeat(92)) {
            return 1;
        }
    } else if (nParam1 == nGlobal19) {
        return 1;
    } else if (nParam1 == nGlobal20) {
        tLocal1 = GetCreatureTalentRandom(63743);
        if (GetIsTalentValid(tLocal1) && GetCreatureHasTalent(tLocal1)) {
            return 1;
        }
    } else if (nParam1 == nGlobal21) {
        tLocal1 = GetCreatureTalentRandom(63743);
        tLocal2 = GetCreatureTalentRandom(62207);
        if (GetIsTalentValid(tLocal1) && GetIsTalentValid(tLocal2) && GetCreatureHasTalent(tLocal1) && GetCreatureHasTalent(tLocal2)) {
            return 1;
        }
    } else if (nParam1 == nGlobal22) {
        tLocal1 = GetCreatureTalentRandom(63743);
        if (GetIsTalentValid(tLocal1) && sub_c3c5()) {
            return 1;
        }
    } else if (nParam1 == nGlobal23) {
        tLocal1 = GetCreatureTalentRandom(63743);
        tLocal2 = GetCreatureTalentRandom(62207);
        if (GetIsTalentValid(tLocal1) && GetIsTalentValid(tLocal2) && sub_c3c5()) {
            return 1;
        }
    } else if (nParam1 == nGlobal24) {
        tLocal1 = GetCreatureTalentRandom(65327);
        tLocal2 = GetCreatureTalentRandom(62207);
        if (GetIsTalentValid(tLocal1) && GetIsTalentValid(tLocal2) && sub_c3c5()) {
            return 1;
        }
    } else if (nParam1 == nGlobal25) {
        if (sub_c6b6() && sub_c773() && sub_c830()) {
            return 1;
        }
    } else if (nParam1 == nGlobal26) {
        tLocal1 = GetCreatureTalentRandom(4356);
        if (sub_c8be() && sub_c97b() && GetIsTalentValid(tLocal1)) {
            return 1;
        }
    } else if (nParam1 == nGlobal27) {
        tLocal1 = GetCreatureTalentRandom(4356);
        if (sub_ca38() && GetIsTalentValid(tLocal1)) {
            return 1;
        }
    } else if (nParam1 == nGlobal28) {
        tLocal1 = GetCreatureTalentRandom(4356);
        if (sub_caf5() && GetIsTalentValid(tLocal1)) {
            return 1;
        }
    } else if (nParam1 == nGlobal29) {
        tLocal1 = GetCreatureTalentRandom(4356);
        if (sub_c773() && sub_cbb2() && GetIsTalentValid(tLocal1)) {
            return 1;
        }
    } else if (nParam1 == nGlobal30) {
        if (sub_cbb2() && sub_c6b6() && sub_cc6f()) {
            return 1;
        }
    } else if (nParam1 == nGlobal31) {
        if (sub_ca38() && sub_c6b6() && sub_c830()) {
            return 1;
        }
    } else if (nParam1 == nGlobal32) {
        if (sub_caf5() && sub_c6b6() && sub_c830()) {
            return 1;
        }
    } else if (nParam1 == nGlobal32) {
        if (sub_c773() && sub_ccfd() && sub_c6b6()) {
            return 1;
        }
    } else if (nParam1 == nGlobal34) {
        tLocal1 = GetCreatureTalentRandom(4356);
        if (sub_ccfd() && GetIsTalentValid(tLocal1)) {
            return 1;
        }
    } else if (nParam1 == nGlobal35) {
        if (sub_ccfd() && sub_c6b6() && sub_cc6f()) {
            return 1;
        }
    } else if (nParam1 == nGlobal36) {
        tLocal1 = GetCreatureTalentRandom(4356);
        if (sub_c6b6() && GetIsTalentValid(tLocal1)) {
            return 1;
        }
    } else if (nParam1 == nGlobal37) {
        tLocal1 = GetCreatureTalentRandom(4356);
        if (sub_c6b6() && sub_cbb2() && GetIsTalentValid(tLocal1)) {
            return 1;
        }
    } else if (nParam1 == nGlobal38) {
        tLocal1 = GetCreatureTalentRandom(4356);
        if (sub_ccfd() && sub_cd8b() && GetIsTalentValid(tLocal1)) {
            return 1;
        }
    } else if (nParam1 == nGlobal39 || nParam1 == nGlobal40) {
        object oLocal3 = GetItemInSlot(7);
        object oLocal4 = GetItemInSlot(8);
        sub_1964("GENERIC DEBUG *************** Droid Items = " + sub_198c(oLocal3) + " / " + sub_198c(oLocal4));
        if (sub_ce19()) {
            sub_1964("GENERIC DEBUG *************** Droid Utility Check is TRUE");
            return 1;
        }
        sub_1964("GENERIC DEBUG *************** Droid Utility Check is FALSE");
    }
    return 0;
}

// verified: recompiles to the original bytes
int sub_c3c5()
{
    if (GetHasSpell(9) || GetHasSpell(11) || GetHasSpell(15) || GetHasSpell(13) || GetHasSpell(12) || GetHasSpell(23) || GetHasSpell(25) || GetHasSpell(26) || GetHasSpell(27) || GetHasSpell(32) || GetHasSpell(49) || GetHasSpell(4) || GetHasSpell(35) || GetHasSpell(43) || GetHasSpell(50)) {
        return 1;
    }
    return 0;
}

// verified: recompiles to the original bytes
int sub_c6b6()
{
    if (GetHasSpell(23) || GetHasSpell(27) || GetHasSpell(26)) {
        return 1;
    }
    return 0;
}

// verified: recompiles to the original bytes
int sub_c773()
{
    if (GetHasSpell(9) || GetHasSpell(50) || GetHasSpell(32)) {
        return 1;
    }
    return 0;
}

// verified: recompiles to the original bytes
int sub_c830()
{
    if (GetHasSpell(21) || GetHasSpell(3)) {
        return 1;
    }
    return 0;
}

// verified: recompiles to the original bytes
int sub_c8be()
{
    if (GetHasSpell(17) || GetHasSpell(24) || GetHasSpell(18)) {
        return 1;
    }
    return 0;
}

// verified: recompiles to the original bytes
int sub_c97b()
{
    if (GetHasSpell(8) || GetHasSpell(37) || GetHasSpell(34)) {
        return 1;
    }
    return 0;
}

// verified: recompiles to the original bytes
int sub_ca38()
{
    if (GetHasSpell(43) || GetHasSpell(35) || GetHasSpell(25)) {
        return 1;
    }
    return 0;
}

// verified: recompiles to the original bytes
int sub_caf5()
{
    if (GetHasSpell(46) || GetHasSpell(29) || GetHasSpell(44)) {
        return 1;
    }
    return 0;
}

// verified: recompiles to the original bytes
int sub_cbb2()
{
    if (GetHasSpell(45) || GetHasSpell(7) || GetHasSpell(38)) {
        return 1;
    }
    return 0;
}

// verified: recompiles to the original bytes
int sub_cc6f()
{
    if (GetHasSpell(49) || GetHasSpell(4)) {
        return 1;
    }
    return 0;
}

// verified: recompiles to the original bytes
int sub_ccfd()
{
    if (GetHasSpell(15) || GetHasSpell(11)) {
        return 1;
    }
    return 0;
}

// verified: recompiles to the original bytes
int sub_cd8b()
{
    if (GetHasSpell(48) || GetHasSpell(19)) {
        return 1;
    }
    return 0;
}

// verified: recompiles to the original bytes
int sub_ce19()
{
    talent tLocal1 = GetCreatureTalentRandom(32768);
    if (GetIsTalentValid(tLocal1)) {
        return 1;
    }
    return 0;
}

// verified: recompiles to the original bytes
string sub_cea1(int nParam1)
{
    if (nParam1 == nGlobal12) {
        return "SW_COMBO_RANGED_FEROCIOUS";
    } else if (nParam1 == nGlobal13) {
        return "SW_COMBO_RANGED_AGGRESSIVE";
    } else if (nParam1 == nGlobal14) {
        return "SW_COMBO_RANGED_DISCIPLINED";
    } else if (nParam1 == nGlobal15) {
        return "SW_COMBO_RANGED_CAUTIOUS";
    } else if (nParam1 == nGlobal16) {
        return "SW_COMBO_MELEE_FEROCIOUS";
    } else if (nParam1 == nGlobal17) {
        return "SW_COMBO_MELEE_AGGRESSIVE";
    } else if (nParam1 == nGlobal18) {
        return "SW_COMBO_MELEE_DISCIPLINED";
    } else if (nParam1 == nGlobal19) {
        return "SW_COMBO_MELEE_CAUTIOUS";
    } else if (nParam1 == nGlobal20) {
        return "SW_COMBO_BUFF_PARTY";
    } else if (nParam1 == nGlobal21) {
        return "SW_COMBO_BUFF_DEBILITATE";
    } else if (nParam1 == nGlobal22) {
        return "SW_COMBO_BUFF_DAMAGE";
    } else if (nParam1 == nGlobal23) {
        return "SW_COMBO_BUFF_DEBILITATE_DESTROY";
    } else if (nParam1 == nGlobal24) {
        return "SW_COMBO_SUPRESS_DEBILITATE_DESTROY";
    } else if (nParam1 == nGlobal25) {
        return "SW_COMBO_SITH_ATTACK";
    } else if (nParam1 == nGlobal26) {
        return "SW_COMBO_BUFF_ATTACK";
    } else if (nParam1 == nGlobal27) {
        return "SW_COMBO_SITH_CONFOUND";
    } else if (nParam1 == nGlobal28) {
        return "SW_COMBO_JEDI_SMITE";
    } else if (nParam1 == nGlobal29) {
        return "SW_COMBO_SITH_TAUNT";
    } else if (nParam1 == nGlobal30) {
        return "SW_COMBO_SITH_BLADE";
    } else if (nParam1 == nGlobal31) {
        return "SW_COMBO_SITH_CRUSH";
    } else if (nParam1 == nGlobal32) {
        return "SW_COMBO_JEDI_CRUSH";
    } else if (nParam1 == nGlobal33) {
        return "SW_COMBO_SITH_BRUTALIZE";
    } else if (nParam1 == nGlobal34) {
        return "SW_COMBO_SITH_DRAIN";
    } else if (nParam1 == nGlobal35) {
        return "SW_COMBO_SITH_ESCAPE";
    } else if (nParam1 == nGlobal36) {
        return "SW_COMBO_JEDI_BLITZ";
    } else if (nParam1 == nGlobal37) {
        return "SW_COMBO_SITH_SPIKE";
    } else if (nParam1 == nGlobal38) {
        return "SW_COMBO_SITH_SCYTHE";
    } else if (nParam1 == nGlobal39) {
        return "SW_COMBO_DROID_UTILITIES";
    }
    return "NO COMBO SELECTED";
}

// verified: recompiles to the original bytes
talent sub_d7df(int nParam1)
{
    SetLocalBoolean(OBJECT_SELF, nGlobal42, 0);
    int nLocal1 = GetLocalNumber(OBJECT_SELF, nGlobal8);
    talent tLocal2;
    talent tLocal3;
    int nLocal4 = -1;
    int nLocal5 = 0;
    int nLocal6 = 0;
    if (nParam1 == nGlobal25) {
        if (nLocal1 == 1) {
            nLocal4 = sub_ebe4();
        } else if (nLocal1 == 2) {
            nLocal4 = sub_ecbf();
        } else {
            nLocal4 = sub_ed9a();
        }
    } else if (nParam1 == nGlobal26) {
        if (nLocal1 == 1) {
            nLocal4 = sub_ee38();
            nLocal6 = 1;
        } else if (nLocal1 == 2) {
            nLocal4 = sub_ef13();
            nLocal6 = 1;
        } else {
            nLocal4 = sub_efee();
            nLocal5 = 1;
        }
    } else if (nParam1 == nGlobal27) {
        if (nLocal1 == 1) {
            nLocal4 = sub_f0d2();
        } else if (nLocal1 == 2) {
            nLocal4 = sub_efee();
            nLocal5 = 1;
        } else {
            nLocal4 = sub_efee();
            nLocal5 = 1;
        }
    } else if (nParam1 == nGlobal28) {
        if (nLocal1 == 1) {
            nLocal4 = sub_f1ad();
        } else if (nLocal1 == 2) {
            nLocal4 = sub_efee();
            nLocal5 = 1;
        } else {
            nLocal4 = sub_efee();
            nLocal5 = 1;
        }
    } else if (nParam1 == nGlobal29) {
        if (nLocal1 == 1) {
            nLocal4 = sub_ebe4();
        } else if (nLocal1 == 2) {
            nLocal4 = sub_f288();
        } else {
            nLocal4 = sub_efee();
            nLocal5 = 1;
        }
    } else if (nParam1 == nGlobal30) {
        if (nLocal1 == 1) {
            nLocal4 = sub_f288();
        } else if (nLocal1 == 2) {
            nLocal4 = sub_ecbf();
        } else {
            nLocal4 = sub_f363();
        }
    } else if (nParam1 == nGlobal31) {
        if (nLocal1 == 1) {
            nLocal4 = sub_f0d2();
        } else if (nLocal1 == 2) {
            nLocal4 = sub_ecbf();
        } else {
            nLocal4 = sub_ed9a();
        }
    } else if (nParam1 == nGlobal32) {
        if (nLocal1 == 1) {
            nLocal4 = sub_f1ad();
        } else if (nLocal1 == 2) {
            nLocal4 = sub_ecbf();
        } else {
            nLocal4 = sub_ed9a();
        }
    } else if (nParam1 == nGlobal33) {
        if (nLocal1 == 1) {
            nLocal4 = sub_ebe4();
        } else if (nLocal1 == 2) {
            nLocal4 = sub_f401();
        } else {
            nLocal4 = sub_ecbf();
        }
    } else if (nParam1 == nGlobal34) {
        if (nLocal1 == 1) {
            nLocal4 = sub_efee();
            nLocal5 = 1;
        } else if (nLocal1 == 2) {
            nLocal4 = sub_f401();
        } else {
            nLocal4 = sub_efee();
            nLocal5 = 1;
        }
    } else if (nParam1 == nGlobal35) {
        if (nLocal1 == 1) {
            nLocal4 = sub_f401();
        } else if (nLocal1 == 2) {
            nLocal4 = sub_ecbf();
        } else {
            nLocal4 = sub_f363();
        }
    } else if (nParam1 == nGlobal36) {
        if (nLocal1 == 1) {
            nLocal4 = sub_efee();
            nLocal5 = 1;
        } else if (nLocal1 == 2) {
            nLocal4 = sub_efee();
            nLocal5 = 1;
        } else {
            nLocal4 = sub_ecbf();
        }
    } else if (nParam1 == nGlobal37) {
        if (nLocal1 == 1) {
            nLocal4 = sub_f288();
        } else if (nLocal1 == 2) {
            nLocal4 = sub_efee();
            nLocal5 = 1;
        } else {
            nLocal4 = sub_ecbf();
        }
    } else if (nParam1 == nGlobal38) {
        if (nLocal1 == 1) {
            nLocal4 = sub_f401();
        } else if (nLocal1 == 2) {
            nLocal4 = sub_f49f();
        } else {
            nLocal4 = sub_efee();
            nLocal5 = 1;
        }
    } else if (nParam1 == nGlobal16) {
        nLocal4 = sub_efee();
        nLocal5 = 1;
    } else if (nParam1 == nGlobal17) {
        if (nLocal1 == 1 || nLocal1 == 2) {
            nLocal4 = sub_efee();
            nLocal5 = 1;
        }
    } else if (nParam1 == nGlobal18) {
        if (nLocal1 == 1 || nLocal1 == 2) {
            nLocal4 = sub_efee();
            nLocal5 = 1;
        }
    } else if (nParam1 == nGlobal19 || nParam1 == nGlobal15) {
        sub_1964("GENERIC DEBUG *************** Melee/Ranged Breather");
    } else if (nParam1 == nGlobal12) {
        nLocal4 = sub_f53d();
        nLocal5 = 1;
    } else if (nParam1 == nGlobal13) {
        if (nLocal1 == 1 || nLocal1 == 2) {
            nLocal4 = sub_f53d();
            nLocal5 = 1;
        }
    } else if (nParam1 == nGlobal14) {
        if (nLocal1 == 1 || nLocal1 == 2) {
            nLocal4 = sub_f53d();
            nLocal5 = 1;
        }
    } else if (nParam1 == nGlobal20) {
        tLocal2 = GetCreatureTalentRandom(63743);
    } else if (nParam1 == nGlobal21) {
        if (nLocal1 == 1) {
            tLocal2 = GetCreatureTalentRandom(63743);
        } else {
            tLocal2 = GetCreatureTalentRandom(62207);
        }
    } else if (nParam1 == nGlobal22) {
        if (nLocal1 == 1) {
            tLocal2 = GetCreatureTalentRandom(63743);
        } else {
            tLocal2 = GetCreatureTalentRandom(61951);
        }
    } else if (nParam1 == nGlobal23) {
        if (nLocal1 == 1) {
            tLocal2 = GetCreatureTalentRandom(63743);
        }
        if (nLocal1 == 2) {
            tLocal2 = GetCreatureTalentRandom(62207);
        }
        if (nLocal1 == 3) {
            tLocal2 = GetCreatureTalentRandom(4353);
        }
    } else if (nParam1 == nGlobal24) {
        if (nLocal1 == 1) {
            tLocal2 = GetCreatureTalentRandom(61951);
        }
        if (nLocal1 == 2) {
            tLocal2 = GetCreatureTalentRandom(62207);
        }
        if (nLocal1 == 3) {
            tLocal2 = GetCreatureTalentRandom(4353);
        }
    } else if (nParam1 == nGlobal39) {
        if (nLocal1 == 1) {
            nLocal4 = sub_f53d();
            nLocal5 = 1;
        }
        if (nLocal1 == 2) {
            nLocal4 = sub_f53d();
            nLocal5 = 1;
        }
        if (nLocal1 == 3) {
            tLocal2 = GetCreatureTalentRandom(32768);
        }
    } else if (nParam1 == nGlobal40) {
        if (nLocal1 == 1) {
            tLocal2 = GetCreatureTalentRandom(32768);
        }
        if (nLocal1 == 2) {
            nLocal4 = sub_f53d();
            nLocal5 = 1;
        }
        if (nLocal1 == 3) {
            tLocal2 = GetCreatureTalentRandom(32768);
        }
    }
    nLocal1++;
    SetLocalNumber(OBJECT_SELF, nGlobal8, nLocal1);
    if (!GetIsTalentValid(tLocal2) || !GetCreatureHasTalent(tLocal2)) {
        if (nLocal4 != -1 && nLocal5 == 0) {
            tLocal2 = TalentSpell(nLocal4);
        } else if (nLocal4 != -1 && nLocal5 == 1) {
            tLocal2 = TalentFeat(nLocal4);
        }
    } else {
        nLocal4 = GetIdFromTalent(tLocal2);
    }
    if (GetIsTalentValid(tLocal2) && GetCreatureHasTalent(tLocal2)) {
        return tLocal2;
    }
    return tLocal3;
}

// verified: recompiles to the original bytes
int sub_ebe4()
{
    if (GetHasSpell(32)) {
        return 32;
    } else if (GetHasSpell(9)) {
        return 9;
    } else if (GetHasSpell(50)) {
        return 50;
    }
    return -1;
}

// verified: recompiles to the original bytes
int sub_ecbf()
{
    if (GetHasSpell(26)) {
        return 26;
    } else if (GetHasSpell(27)) {
        return 27;
    } else if (GetHasSpell(23)) {
        return 23;
    }
    return -1;
}

// verified: recompiles to the original bytes
int sub_ed9a()
{
    if (GetHasSpell(3)) {
        return 3;
    } else if (GetHasSpell(21)) {
        return 21;
    }
    return -1;
}

// verified: recompiles to the original bytes
int sub_ee38()
{
    if (GetHasSpell(17)) {
        return 17;
    } else if (GetHasSpell(24)) {
        return 24;
    } else if (GetHasSpell(18)) {
        return 18;
    }
    return -1;
}

// verified: recompiles to the original bytes
int sub_ef13()
{
    if (GetHasSpell(37)) {
        return 37;
    } else if (GetHasSpell(34)) {
        return 34;
    } else if (GetHasSpell(8)) {
        return 8;
    }
    return -1;
}

// verified: recompiles to the original bytes
int sub_efee()
{
    talent tLocal1 = GetCreatureTalentBest(4356, 20);
    if (GetIsTalentValid(tLocal1) && GetCreatureHasTalent(tLocal1)) {
        int nLocal2 = GetIdFromTalent(tLocal1);
        return nLocal2;
    }
    return -1;
}

// verified: recompiles to the original bytes
int sub_f0d2()
{
    if (GetHasSpell(25)) {
        return 25;
    } else if (GetHasSpell(35)) {
        return 35;
    } else if (GetHasSpell(43)) {
        return 43;
    }
    return -1;
}

// verified: recompiles to the original bytes
int sub_f1ad()
{
    if (GetHasSpell(44)) {
        return 44;
    } else if (GetHasSpell(29)) {
        return 29;
    } else if (GetHasSpell(46)) {
        return 46;
    }
    return -1;
}

// verified: recompiles to the original bytes
int sub_f288()
{
    if (GetHasSpell(38)) {
        return 38;
    } else if (GetHasSpell(7)) {
        return 7;
    } else if (GetHasSpell(45)) {
        return 45;
    }
    return -1;
}

// verified: recompiles to the original bytes
int sub_f363()
{
    if (GetHasSpell(4)) {
        return 4;
    } else if (GetHasSpell(49)) {
        return 49;
    }
    return -1;
}

// verified: recompiles to the original bytes
int sub_f401()
{
    if (GetHasSpell(11)) {
        return 11;
    } else if (GetHasSpell(15)) {
        return 15;
    }
    return -1;
}

// verified: recompiles to the original bytes
int sub_f49f()
{
    if (GetHasSpell(19)) {
        return 19;
    } else if (GetHasSpell(48)) {
        return 48;
    }
    return -1;
}

// verified: recompiles to the original bytes
int sub_f53d()
{
    talent tLocal1 = GetCreatureTalentBest(4481, 20);
    if (GetIsTalentValid(tLocal1) && GetCreatureHasTalent(tLocal1)) {
        int nLocal2 = GetIdFromTalent(tLocal1);
        return nLocal2;
    }
    return -1;
}

// verified: recompiles to the original bytes
int sub_f621(int nParam1)
{
    int nLocal1 = 0;
    int nLocal2 = d6();
    while (nLocal1 == 0) {
        if (nLocal2 == 1) {
            nLocal2 = nGlobal13;
        } else if (nLocal2 == 2) {
            nLocal2 = nGlobal15;
        } else if (nLocal2 == 3) {
            nLocal2 = nGlobal14;
        } else if (nLocal2 == 4) {
            nLocal2 = nGlobal12;
        } else if (nLocal2 == 5 || nLocal2 == 6) {
            if ((IsObjectPartyMember(OBJECT_SELF) && GetNPCAIStyle(OBJECT_SELF) == 5) || !IsObjectPartyMember(OBJECT_SELF)) {
                if (nLocal2 == 5) {
                    nLocal2 = nGlobal39;
                } else if (nLocal2 == 6) {
                    nLocal2 = nGlobal40;
                }
            } else {
                nLocal2 = nGlobal41;
            }
        }
        nLocal1 = sub_b204(nLocal2);
        if (nLocal1 == 0) {
            nLocal2 = d6();
        }
    }
    return nLocal2;
}

// verified: recompiles to the original bytes
int sub_f8e2(int nParam1)
{
    int nLocal1;
    int nLocal2 = d4();
    if (sub_5169(OBJECT_SELF) != 0) {
        while (nLocal1 == 0) {
            if (sub_5169(OBJECT_SELF) == 1) {
                if (nLocal2 == 1) {
                    nLocal2 = nGlobal17;
                } else if (nLocal2 == 2) {
                    nLocal2 = nGlobal19;
                } else if (nLocal2 == 3) {
                    nLocal2 = nGlobal18;
                } else if (nLocal2 == 4) {
                    nLocal2 = nGlobal16;
                }
            } else if (sub_5169(OBJECT_SELF) == 2) {
                if (nLocal2 == 1) {
                    nLocal2 = nGlobal13;
                } else if (nLocal2 == 2) {
                    nLocal2 = nGlobal15;
                } else if (nLocal2 == 3) {
                    nLocal2 = nGlobal14;
                } else if (nLocal2 == 4) {
                    nLocal2 = nGlobal12;
                }
            }
            nLocal1 = sub_b204(nLocal2);
            if (nLocal1 == 0) {
                nLocal2 = d6();
            }
        }
    } else {
        nLocal2 = 2;
    }
    return nLocal2;
}

// verified: recompiles to the original bytes
talent sub_fba8(object oParam1, talent tParam2)
{
    int nLocal1;
    sub_1964("GENERIC DEBUG *************** Starting Droid Talent Double Check");
    if (GetTypeFromTalent(tParam2) == 0) {
        sub_1964("GENERIC DEBUG *************** Droid Talent is a Spell");
        if (GetIdFromTalent(tParam2) == 116 || GetIdFromTalent(tParam2) == 117) {
            if (GetRacialType(oParam1) == 6) {
                return tParam2;
            } else {
                nLocal1 = 1;
            }
        }
        if (GetIdFromTalent(tParam2) == 118 || GetIdFromTalent(tParam2) == 119) {
            if (GetHasSpellEffect(99, oParam1) || GetHasSpellEffect(100, oParam1) || GetHasSpellEffect(101, oParam1) || GetHasSpellEffect(102, oParam1) || GetHasSpellEffect(103, oParam1) || GetHasSpellEffect(104, oParam1) || GetHasSpellEffect(105, oParam1) || GetHasSpellEffect(106, oParam1) || GetHasSpellEffect(107, oParam1) || GetHasSpellEffect(110, oParam1) || GetHasSpellEffect(111, oParam1) || GetHasSpellEffect(112, oParam1) || GetHasSpellEffect(113, oParam1) || GetHasSpellEffect(114, oParam1) || GetHasSpellEffect(115, oParam1)) {
                return tParam2;
            } else {
                nLocal1 = 1;
            }
        }
    }
    if (nLocal1 == 1) {
        talent tLocal2 = GetCreatureTalentBest(4481, 20);
        if (GetIsTalentValid(tParam2) && GetCreatureHasTalent(tParam2)) {
            return tLocal2;
        } else {
            talent tLocal3;
            return tLocal3;
        }
    }
    return tParam2;
}

// verified: recompiles to the original bytes
int sub_10169(object oParam1)
{
    if (IsObjectPartyMember(OBJECT_SELF) || d100() > 50) {
        int nLocal1 = 0;
        talent tLocal2;
        object oLocal3 = sub_5a4d();
        if (GetRacialType(oLocal3) == 5) {
            nLocal1 = 1;
        }
        tLocal2 = sub_662b(nLocal1);
        if (GetIsObjectValid(oLocal3) && GetIsTalentValid(tLocal2) && GetCreatureHasTalent(tLocal2)) {
            sub_1964("GENERIC DEBUG *************** Clear 1400");
            ClearAllActions();
            ActionUseTalentOnObject(tLocal2, oLocal3);
            return 1;
        }
        sub_1964("GENERIC DEBUG *************** Grenade AI Failure");
        return sub_9e16(oParam1);
    }
    return 0;
}

// verified: recompiles to the original bytes
int sub_1038b(object oParam1)
{
    object oLocal1 = sub_a74c();
    talent tLocal2;
    object oLocal3;
    if (GetRacialType(OBJECT_SELF) == 5) {
        return sub_9e16(OBJECT_INVALID);
    }
    if (sub_3105(nGlobal109, OBJECT_SELF)) {
        return 1;
    }
    if (GetIsObjectValid(oLocal1)) {
        if (sub_3105(nGlobal107, oLocal1)) {
            return 1;
        }
    }
    object oLocal4 = sub_2b8a();
    if (GetIsObjectValid(oLocal4)) {
        if (sub_3105(nGlobal108, oLocal4)) {
            return 1;
        }
    }
    oLocal3 = sub_8e37();
    sub_1964("GENERIC DEBUG *************** Jedi Support AI: AOE Target = " + sub_2151(GetIsObjectValid(oLocal3)));
    if (GetIsObjectValid(oLocal3)) {
        if (GetRacialType(oLocal3) == 5) {
            tLocal2 = sub_5f44(nGlobal2, 1);
        } else {
            tLocal2 = sub_5f44(nGlobal2, 0);
        }
    } else {
        sub_1964("GENERIC DEBUG *************** Jedi Support AI: Inside the Party AI Section");
        oLocal3 = sub_1090e(OBJECT_INVALID);
        sub_1964("GENERIC DEBUG *************** Boss AI: Initial oFind Search = " + sub_198c(oLocal3));
        if (GetIsObjectValid(oLocal3)) {
            sub_1964("GENERIC DEBUG *************** Jedi Support AI: Valid oTarget Set As = " + sub_198c(oLocal3));
            if (GetRacialType(oLocal3) == 5) {
                tLocal2 = sub_5f44(nGlobal3, 1);
            } else {
                tLocal2 = sub_5f44(nGlobal3, 0);
            }
        }
    }
    tLocal2 = sub_979f(oLocal3, tLocal2);
    tLocal2 = sub_99df(oLocal3, tLocal2);
    if (GetIsObjectValid(oLocal3) && GetIsTalentValid(tLocal2)) {
        sub_1964("GENERIC DEBUG *************** Clear 1450");
        ClearAllActions();
        ActionUseTalentOnObject(tLocal2, oLocal3);
        return 1;
    }
    sub_1964("GENERIC DEBUG *************** Jedi Support AI: Fall Through");
    return sub_9e16(OBJECT_INVALID);
}

// verified: recompiles to the original bytes
object sub_1090e(object oParam1)
{
    sub_1964("GENERIC DEBUG *************** Starting: Determine Attack Target");
    int nLocal1 = GetPartyAIStyle();
    int nLocal2 = GetNPCAIStyle(OBJECT_SELF);
    object oLocal3;
    object oLocal4 = GetLastHostileTarget();
    sub_1964("GENERIC DEBUG *************** Intruder = " + IntToString(GetIsObjectValid(oParam1)) + " Last Target = " + IntToString(GetIsObjectValid(oLocal4)));
    if (GetIsObjectValid(oParam1) && !GetIsDead(oParam1) && !GetIsDebilitated(oParam1)) {
        sub_1964("GENERIC DEBUG *************** Intruder Target Returned = " + ObjectToString(oParam1));
        return oParam1;
    } else if (GetIsObjectValid(oLocal4) && !GetIsDead(oLocal4) && !GetIsDebilitated(oLocal4)) {
        sub_1964("GENERIC DEBUG *************** Last Target Returned = " + ObjectToString(oParam1));
        return oLocal4;
    } else if (nLocal1 == 0) {
        int nLocal5 = 1;
        sub_1964("GENERIC DEBUG *************** Getting nearest target - 249");
        object oLocal6 = GetNearestCreature(3, 1, OBJECT_SELF, nLocal5, 7, 7);
        for (oLocal3 = oLocal6; !GetIsDebilitated(oLocal3) && GetIsObjectValid(oLocal3); oLocal3 = GetNearestCreature(3, 1, OBJECT_SELF, nLocal5, 7, 7)) {
            nLocal5++;
        }
        if (!GetIsObjectValid(oLocal3) && GetIsObjectValid(oLocal6)) {
            oLocal3 = oLocal6;
        }
    } else if (nLocal1 == 1) {
        int nLocal7 = 0;
        object oLocal8;
        while (!GetIsObjectValid(oLocal8) && nLocal7 < 3) {
            oLocal8 = GetLastHostileActor(GetPartyMemberByIndex(nLocal7));
            nLocal7++;
        }
        if (GetIsObjectValid(oLocal8)) {
            sub_1964("GENERIC DEBUG *************** Getting nearest target - 262");
            oLocal3 = GetNearestCreature(3, 1, OBJECT_SELF, 1, 7, 7);
        } else {
            oLocal8 = GetLastHostileTarget(GetPartyMemberByIndex(0));
            if (GetIsObjectValid(oLocal8)) {
                sub_1964("GENERIC DEBUG *************** Getting nearest target - 269");
                oLocal3 = GetNearestCreature(3, 1, OBJECT_SELF, 1, 7, 7);
            }
        }
    } else if (nLocal1 != 2) {
        sub_1964("GENERIC DEBUG *************** Getting nearest target - 275");
        oLocal3 = GetNearestCreature(3, 1, OBJECT_SELF, 1, 7, 7);
    } else {
        sub_1964("GENERIC DEBUG *************** Getting nearest target - 279");
        oLocal3 = GetNearestCreature(3, 1, OBJECT_SELF, 1, 7, 7);
    }
    if (GetIsObjectValid(oLocal3)) {
        sub_1964("GENERIC DEBUG *************** Attack Target From Determine Attack Target = " + sub_198c(oLocal3));
        return oLocal3;
    }
    sub_1964("GENERIC DEBUG *************** No Attack Targets Found");
    return OBJECT_INVALID;
}

// verified: recompiles to the original bytes
int sub_1119e()
{
    sub_1964("GENERIC DEBUG *************** Post DCR Checks for " + sub_198c(OBJECT_SELF));
    if (sub_1daf(nGlobal93) && !sub_1daf(nGlobal94)) {
        if (sub_114de()) {
            return 1;
        }
    } else if (sub_1daf(nGlobal94)) {
        sub_1964("GENERIC DEBUG *************** Clear 1000");
        ClearAllActions();
        return 1;
    }
    if (!IsObjectPartyMember(OBJECT_SELF) && sub_1194f(OBJECT_SELF) == 1) {
        sub_1964("GENERIC DEBUG *************** Clear 1100");
        ClearAllActions();
        DelayCommand(1.0, sub_11c98());
        return 1;
    } else if (GetPartyMemberByIndex(0) != OBJECT_SELF && !GetIsObjectValid(GetNearestCreature(3, 1, OBJECT_SELF, 1, 7, 7)) && IsObjectPartyMember(OBJECT_SELF)) {
        if (!GetSoloMode()) {
            sub_129ae("NO TARGET: FOLLOW LEADER", 10, 10, 4.0);
            CancelCombat(OBJECT_SELF);
            sub_1964("GENERIC DEBUG *************** Clear 1200");
            ClearAllActions();
            ActionFollowLeader();
        }
        return 1;
    }
    return 0;
}

// verified: recompiles to the original bytes
int sub_114de()
{
    sub_1964("GENERIC DEBUG *************** Start Commoner AI");
    object oLocal1 = GetNearestCreature(3, 1);
    object oLocal2;
    int nLocal3 = 1;
    int nLocal4 = 1;
    object oLocal5 = GetNearestCreature(3, 2);
    while (GetIsObjectValid(oLocal5) && nLocal3 == 1) {
        if (GetStandardFaction(oLocal5) == 1 || GetStandardFaction(oLocal5) == 3 || GetStandardFaction(oLocal5) == 6) {
            if (GetDistanceBetween(OBJECT_SELF, oLocal5) <= 20.0) {
                oLocal2 = oLocal5;
                nLocal3 = 0;
            }
        } else {
            nLocal4++;
            oLocal5 = GetNearestCreature(3, 2, OBJECT_SELF, nLocal4);
        }
    }
    if (GetIsObjectValid(oLocal1)) {
        sub_1964("GENERIC DEBUG *************** Clear 2710");
        ClearAllActions();
        ActionMoveAwayFromObject(oLocal1, 1, 20.0);
        DelayCommand(0.2, ActionDoCommand(sub_1192f()));
        return 1;
    } else if (GetIsObjectValid(oLocal2)) {
        sub_1964("GENERIC DEBUG *************** Object Flee = " + sub_198c(oLocal2));
        sub_1964("GENERIC DEBUG *************** Clear 2720");
        ClearAllActions();
        ActionMoveAwayFromObject(oLocal2, 1, 20.0);
        DelayCommand(0.2, ActionDoCommand(sub_1192f()));
        return 1;
    }
    return 0;
}

// verified: recompiles to the original bytes
void sub_1192f()
{
    int nLocal1 = sub_1119e();
}

// verified: recompiles to the original bytes
int sub_1194f(object oParam1)
{
    string sLocal1 = "WP_" + GetTag(oParam1) + "_01";
    string sLocal2 = "POST_" + GetTag(oParam1);
    int nLocal3 = GetLocalNumber(oParam1, nGlobal45);
    string sLocal4;
    if (nLocal3 < 10) {
        sLocal4 = "0" + IntToString(nLocal3);
    } else {
        sLocal4 = IntToString(nLocal3);
    }
    string sLocal5 = "WP_" + sLocal4 + "_01";
    object oLocal6 = GetWaypointByTag(sLocal1);
    object oLocal7 = GetWaypointByTag(sLocal5);
    object oLocal8 = GetWaypointByTag(sLocal2);
    sub_11c70("Walk Initiate for " + GetTag(oParam1));
    sub_11c70("TAG WAY FOUND = " + IntToString(GetIsObjectValid(oLocal6)));
    sub_11c70("WAY POINT NAME = " + GetTag(oLocal6));
    sub_11c70("SERIES INT = " + IntToString(nLocal3));
    sub_11c70("SERIES WAY FOUND = " + IntToString(GetIsObjectValid(oLocal7)));
    sub_11c70("SERIES Series Tag = " + sLocal5);
    sub_11c70("");
    if (GetIsObjectValid(oLocal6) || GetIsObjectValid(oLocal7) || GetIsObjectValid(oLocal8)) {
        return 1;
    }
    return 0;
}

// verified: recompiles to the original bytes
void sub_11c70(string sParam1)
{
    if (!ShipBuild()) {
        PrintString(sParam1);
    }
}

// verified: recompiles to the original bytes
void sub_11c98()
{
    if (!sub_1daf(nGlobal55)) {
        string sLocal1 = "POST_";
        string sLocal2 = "WP_";
        string sLocal3;
        int nLocal4 = GetLocalNumber(OBJECT_SELF, nGlobal43);
        int nLocal5 = GetLocalNumber(OBJECT_SELF, nGlobal44);
        int nLocal6 = GetLocalNumber(OBJECT_SELF, nGlobal45);
        if (nLocal4 < 10 && nLocal4 > 0) {
            sLocal3 = "0" + IntToString(nLocal4);
        } else if (nLocal4 == 0) {
            if (sub_1daf(nGlobal52)) {
                nLocal4 = Random(nLocal5) + 1;
                if (nLocal4 < 10) {
                    sLocal3 = "0" + IntToString(nLocal4);
                } else {
                    sLocal3 = IntToString(nLocal4);
                }
            } else {
                sLocal3 = "01";
            }
        } else if (nLocal4 < 10) {
            sLocal3 = "0" + IntToString(nLocal4);
        } else {
            sLocal3 = IntToString(nLocal4);
        }
        string sLocal7;
        string sLocal8;
        if (nLocal6 > 0) {
            string sLocal9;
            if (nLocal6 < 10) {
                sLocal9 = "0" + IntToString(nLocal6);
            } else {
                sLocal9 = IntToString(nLocal6);
            }
            sLocal8 = sLocal2 + sLocal9 + "_02";
        } else {
            sLocal8 = sLocal2 + GetTag(OBJECT_SELF) + "_02";
        }
        object oLocal10 = GetWaypointByTag(sLocal8);
        if (nLocal5 == 0 && GetIsObjectValid(oLocal10)) {
        }
        if (GetIsObjectValid(oLocal10)) {
            int nLocal11 = GetStringLength(sLocal8);
            sLocal7 = GetStringLeft(sLocal8, nLocal11 - 2) + sLocal3;
        } else {
            sLocal2 = "UNKNOWN";
            sLocal7 = sLocal1 + GetTag(OBJECT_SELF);
        }
        object oLocal12 = GetWaypointByTag(sLocal7);
        int nLocal13 = sub_1daf(nGlobal53);
        if (GetDistanceToObject2D(oLocal12) <= 2.5) {
            int nLocal14;
            if (sub_1daf(nGlobal52)) {
                nLocal4 = Random(nLocal5) + 1;
            } else if (nLocal4 < nLocal5 && !sub_1daf(nGlobal52)) {
                nLocal14 = sub_124e7(nLocal5, nLocal4);
                nLocal4 = nLocal4 + nLocal14;
            } else if (nLocal4 == nLocal5) {
                nLocal14 = sub_124e7(nLocal5, nLocal4);
                if (sub_1daf(nGlobal48)) {
                    sub_2180(nGlobal55, 1);
                } else if (sub_1daf(nGlobal49)) {
                    nLocal4 = 1;
                    sub_2180(nGlobal54, 0);
                } else {
                    nLocal4 = nLocal4 + nLocal14;
                }
            }
        }
        if (GetIsObjectValid(GetWaypointByTag(sLocal7))) {
            int nLocal15;
            if (sub_1daf(nGlobal51)) {
                nLocal15 = d3();
            } else if (sub_1daf(nGlobal56)) {
                nLocal15 = d6() + 6;
            } else if (sub_1daf(nGlobal57)) {
                nLocal15 = d12();
            } else if (nLocal15 > 0) {
                ActionWait(IntToFloat(nLocal15));
            }
            oLocal12 = GetWaypointByTag(sLocal7);
            float fLocal16 = GetDistanceBetween2D(GetWaypointByTag(sLocal7), OBJECT_SELF) / 1.25;
            if (fLocal16 < 30.0) {
                fLocal16 = 30.0;
            }
            ActionForceMoveToObject(oLocal12, sub_1daf(nGlobal53), 2.5, fLocal16);
            if (sub_1daf(nGlobal46)) {
                ActionDoCommand(sub_12667());
            }
            SetLocalNumber(OBJECT_SELF, nGlobal43, nLocal4);
            if (sLocal2 != "UNKNOWN") {
                ActionDoCommand(sub_11c98());
            }
        }
    }
}

// verified: recompiles to the original bytes
int sub_124e7(int nParam1, int nParam2)
{
    int nLocal1;
    int nLocal2 = sub_1daf(nGlobal54);
    if (nParam1 == nParam2 && nLocal2 == 0) {
        nLocal1 = -1;
        sub_2180(nGlobal54, 1);
    } else if (nParam2 == 1 && nLocal2 == 1) {
        nLocal1 = 1;
        sub_2180(nGlobal54, 0);
    } else if (nLocal2 == 0) {
        nLocal1 = 1;
    } else if (nLocal2 == 1) {
        nLocal1 = -1;
    }
    return nLocal1;
}

// verified: recompiles to the original bytes
void sub_12667()
{
    int nLocal1 = d8();
    if (nLocal1 == 1) {
        ActionPlayAnimation(103);
    } else if (nLocal1 == 2) {
        ActionPlayAnimation(102);
    } else if (nLocal1 == 3) {
        ActionPlayAnimation(1, 1.0, 3.0);
    } else if ((nLocal1 == 4 || nLocal1 == 5) && GetRacialType(OBJECT_SELF) != 5) {
        if (GetGender(OBJECT_SELF) == 0) {
            sub_2180(nGlobal46, 0);
            ActionPlayAnimation(24, 1.0, 20.4);
            ActionDoCommand(sub_2180(nGlobal46, 1));
        } else if (GetGender(OBJECT_SELF) == 1) {
            sub_2180(nGlobal46, 0);
            ActionPlayAnimation(24, 1.0, 13.3);
            ActionDoCommand(sub_2180(nGlobal46, 1));
        }
    } else if (nLocal1 == 6 || nLocal1 == 4 || nLocal1 == 5) {
        ActionPlayAnimation(100);
    } else if (nLocal1 == 7) {
        ActionPlayAnimation(101);
    } else if (nLocal1 == 8) {
        sub_2180(nGlobal46, 0);
        ActionPlayAnimation(1, 1.0, 5.0);
        ActionDoCommand(sub_2180(nGlobal46, 1));
    }
}

// verified: recompiles to the original bytes
void sub_129ae(string sParam1, int nParam2, int nParam3, float fParam4)
{
}

// verified: recompiles to the original bytes
int sub_129b6(object oParam1, int nParam2)
{
    int nLocal1;
    if (nParam2 >= 0 && nParam2 <= 19 && GetIsObjectValid(oParam1)) {
        nLocal1 = GetLocalBoolean(oParam1, nParam2);
        if (nLocal1 > 0) {
            return 1;
        }
    }
    return 0;
}

// verified: recompiles to the original bytes
void sub_12a9e(object oParam1, int nParam2, int nParam3)
{
    int nLocal1 = GetHitDice(GetFirstPC());
    if (nParam3 == 1) {
        if (nParam2 == nGlobal121 || nParam2 == nGlobal126 || nParam2 == nGlobal127 || nParam2 == nGlobal128) {
            GiveXPToCreature(GetFirstPC(), nLocal1 * 15);
        } else if (nParam2 == nGlobal122 || nParam2 == nGlobal129 || nParam2 == nGlobal125) {
            GiveXPToCreature(GetFirstPC(), nLocal1 * 20);
        } else if (nParam2 == nGlobal123 || nParam2 == nGlobal124) {
            GiveXPToCreature(GetFirstPC(), nLocal1 * 10);
        }
    }
    if (nParam2 >= 0 && nParam2 <= 19 && GetIsObjectValid(oParam1)) {
        if (nParam3 == 1 || nParam3 == 0) {
            SetLocalBoolean(oParam1, nParam2, nParam3);
        }
    }
}

// verified: recompiles to the original bytes
void sub_12d6a(object oParam1)
{
    effect eLocal1;
    int nLocal2;
    if (GetIsObjectValid(oParam1)) {
        for (eLocal1 = GetFirstEffect(oParam1); GetIsEffectValid(eLocal1) && !nLocal2; eLocal1 = GetNextEffect(oParam1)) {
            if (GetEffectCreator(eLocal1) == OBJECT_SELF) {
                RemoveEffect(oParam1, eLocal1);
                nLocal2 = 1;
            }
        }
    }
}

// verified: recompiles to the original bytes
void sub_12e48()
{
    int nLocal1;
    object oLocal2;
    for (nLocal1 = 0; nLocal1 <= 2; nLocal1++) {
        oLocal2 = GetPartyMemberByIndex(nLocal1);
        if (GetIsObjectValid(oLocal2) && GetFirstPC() != oLocal2) {
            ExecuteScript("k_pman_aion", oLocal2);
        }
    }
}

