"""Генерирует verse/lab_data.verse из config/brainrot_lab_tycoon.json.

Цифры баланса живут только в конфиге: поменял JSON → запустил скрипт → скопировал verse/ в проект UEFN.

    python tools/gen_verse_data.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "brainrot_lab_tycoon.json"
MODELS = ROOT / "models" / "brainrots"
OUT = ROOT / "verse" / "lab_data.verse"

RARITIES = ["common", "rare", "epic", "legendary", "mythic", "iconic"]
VARIANTS = ["base", "gold", "diamond", "rainbow", "lava", "viral", "cosmic"]
PERKS = ["hatch_speed", "pickaxe_crit", "belt_discount", "likes_bonus", "variant_up", "cash_bonus",
         "offline_bonus", "tour_speed", "fusion_speed", "junk_bonus", "ideal_luck", "unique"]
SOURCES = ["belt", "fusion", "event"]
QUESTS = ["hatch", "buy_capsule", "pickaxe_hit", "sell", "junk", "tour", "upgrade", "hatch_epic", "fusion", "like"]
WEEKDAYS = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]


def f(x):
    """float-литерал Verse: всегда с точкой."""
    x = float(x)
    return f"{x:.1f}" if x == int(x) and abs(x) < 1e15 else repr(x)


def s(x):
    return '"' + str(x).replace("\\", "\\\\").replace('"', '\\"').replace("{", "\\{").replace("}", "\\}") + '"'


def ints(xs):
    return "array{" + ", ".join(str(int(v)) for v in xs) + "}"


def floats(xs):
    return "array{" + ", ".join(f(v) for v in xs) + "}"


def main():
    c = json.loads(CONFIG.read_text(encoding="utf-8"))
    ids = [b["id"] for b in c["brainrots"]]
    idx = {k: i for i, k in enumerate(ids)}
    fam_of = {m: fi for fi, fam in enumerate(c["families"]) for m in fam["members"]}
    rar = {r["id"]: r for r in c["rarities"]}
    L = []
    w = L.append
    w("# АВТОГЕНЕРАЦИЯ — не править руками.")
    w("# Источник: config/brainrot_lab_tycoon.json, генератор: tools/gen_verse_data.py")
    w("")
    w("rarity_def := struct:")
    for fld, t in [("Name", "string = \"\""), ("Income", "float = 0.0"), ("Payback", "float = 0.0"),
                   ("Hatch", "float = 0.0"), ("Weight", "float = 0.0"), ("SellLikes", "int = 0")]:
        w(f"    {fld}:{t}")
    w("")
    w("variant_def := struct:")
    for fld, t in [("Name", "string = \"\""), ("Mult", "float = 1.0"), ("BeltChance", "float = 0.0"), ("Week", "int = 0")]:
        w(f"    {fld}:{t}")
    w("")
    w("brainrot_def := struct:")
    for fld, t in [("Key", "string = \"\""), ("Title", "string = \"\""), ("Rarity", "int = 0"), ("Family", "int = 0"),
                   ("Source", "int = 0"), ("Week", "int = 0")]:
        w(f"    {fld}:{t}")
    w("")
    w("family_def := struct:")
    w("    Name:string = \"\"")
    w("    Perk:int = 0")
    w("    Members:[]int = array{}")
    w("")
    w("combo_def := struct:")
    w("    Name:string = \"\"")
    w("    Bonus:float = 0.0")
    w("    Members:[]int = array{}")
    w("    Week:int = 0")
    w("")
    w("recipe_def := struct:")
    w("    Result:int = 0")
    w("    Inputs:[]int = array{}")
    w("    Hint:string = \"\"")
    w("")
    w("rebirth_req := struct:")
    w("    Ids:[]int = array{}")
    w("    Variants:[]int = array{}")
    w("")
    w("shop_def := struct:")
    w("    Key:string = \"\"")
    w("    Name:string = \"\"")
    w("    Cost:int = 0")
    w("    MaxLevel:int = 1")
    w("")
    w("tour_def := struct:")
    for fld, t in [("Name", "string = \"\""), ("Minutes", "float = 0.0"), ("CostIncomeMin", "float = 0.0"),
                   ("LikesMin", "int = 0"), ("LikesMax", "int = 0"), ("CapsuleChance", "float = 0.0"),
                   ("EpicPlus", "logic = false")]:
        w(f"    {fld}:{t}")
    w("")
    w("quest_def := struct:")
    w("    Kind:int = 0")
    w("    Target:int = 0")
    w("")
    w("offer_def := struct:")
    w("    Key:string = \"\"")
    w("    Name:string = \"\"")
    w("    Price:int = 0")
    w("    Effect:string = \"\"")
    w("    Week:int = 0")
    w("")

    # ---- перечисления
    w("# Редкости")
    for i, r in enumerate(RARITIES):
        w(f"RarityIdx_{r.capitalize()}:int = {i}")
    w("# Варианты")
    for i, v in enumerate(VARIANTS):
        w(f"VariantIdx_{v.capitalize()}:int = {i}")
    w("# Перки компаньонов")
    for i, p in enumerate(PERKS):
        w(f"Perk_{''.join(x.capitalize() for x in p.split('_'))}:int = {i}")
    w("# Типы ежедневных заданий")
    for i, q in enumerate(QUESTS):
        w(f"Quest_{''.join(x.capitalize() for x in q.split('_'))}:int = {i}")
    w("# Источник брейнрота: 0 конвейер, 1 скрещивание, 2 ивент")
    w("")

    # ---- таблицы
    w("LabRarities:[]rarity_def = array:")
    for r in RARITIES:
        d = rar[r]
        w(f"    rarity_def{{Name := {s(d['name'])}, Income := {f(d['income_per_sec'])}, Payback := {f(d['payback_sec'] or 0)}, "
          f"Hatch := {f(d['hatch_sec'])}, Weight := {f(d['belt_weight'])}, SellLikes := {int(d['sell_likes'] or 0)}}}")
    w("")
    w("LabVariants:[]variant_def = array:")
    for v in c["variants"]:
        w(f"    variant_def{{Name := {s(v['name'])}, Mult := {f(v['income_mult'])}, BeltChance := {f(v['belt_chance'] or 0)}, Week := {v['available_from_week']}}}")
    w("")
    w("# Порядок совпадает с массивом BrainrotProps у lab_manager_device")
    w("LabBrainrots:[]brainrot_def = array:")
    for b in c["brainrots"]:
        info = json.loads((MODELS / b["id"] / "info.json").read_text(encoding="utf-8"))
        w(f"    brainrot_def{{Key := {s(b['id'])}, Title := {s(info['title'])}, Rarity := {RARITIES.index(b['rarity'])}, "
          f"Family := {fam_of[b['id']]}, Source := {SOURCES.index(b['source'])}, Week := {b['release_week']}}}")
    w("")
    for key in ("Tung_Tung_Tung_Sahur", "Tralalero_Tralala", "SixSeven_67"):
        w(f"BrainrotIdx_{key.replace('_', '')}:int = {idx[key]}")
    w("")
    w("LabFamilies:[]family_def = array:")
    for fam in c["families"]:
        w(f"    family_def{{Name := {s(fam['name'])}, Perk := {PERKS.index(fam['companion_perk'])}, Members := {ints(idx[m] for m in fam['members'])}}}")
    w(f"FamilyIdx_Icons:int = {[f_['id'] for f_ in c['families']].index('icons')}")
    w("")
    w("LabCombos:[]combo_def = array:")
    for cb in c["special_combos"]:
        w(f"    combo_def{{Name := {s(cb['name'])}, Bonus := {f(cb['bonus'])}, Members := {ints(idx[m] for m in cb['members'])}, Week := {cb['release_week']}}}")
    w("")
    fc = c["family_combo"]
    by = [0.0] * 5
    for k, v in fc["by_count"].items():
        by[int(k)] = v
    w(f"# Бонус семьи по числу разных членов на подиуме (индекс = число)")
    w(f"LabFamilyBonusByCount:[]float = {floats(by)}")
    w(f"LabFamilyFullExtra:float = {f(fc['full_family_extra'])}")
    w("")
    w("LabRecipes:[]recipe_def = array:")
    for r in c["fusion"]["recipes"]:
        w(f"    recipe_def{{Result := {idx[r['result']]}, Inputs := {ints(idx[i] for i in r['inputs'])}, Hint := {s(r['hint'])}}}")
    w("")
    w("# Требования перерождений 1..35: индекс массива = уровень − 1")
    w("LabRebirthReqs:[]rebirth_req = array:")
    for r in sorted(c["rebirth"]["requirements"], key=lambda r: r["level"]):
        w(f"    rebirth_req{{Ids := {ints(idx[n] for n, _ in r['need'])}, Variants := {ints(VARIANTS.index(v) for _, v in r['need'])}}}")
    w("")
    up = c["upgrade_costs_likes"]
    w("# Цена улучшения в Лайках: [редкость][текущий вариант] → переход на следующий")
    w("LabUpgradeCosts:[][]int = array:")
    for r in RARITIES:
        w(f"    {ints(up[r] or [])}")
    w("")
    w("LabHypeShop:[]shop_def = array:")
    for it in c["hype_shop"]:
        w(f"    shop_def{{Key := {s(it['id'])}, Name := {s(it['name'])}, Cost := {it['cost']}, MaxLevel := {it['max_level']}}}")
    for i, it in enumerate(c["hype_shop"]):
        w(f"Shop_{''.join(x.capitalize() for x in it['id'].split('_'))}:int = {i}")
    w("")
    w("LabTours:[]tour_def = array:")
    for t in c["tours"]["list"]:
        w(f"    tour_def{{Name := {s(t['name'])}, Minutes := {f(t['duration_min'])}, CostIncomeMin := {f(t['cost_income_min'])}, "
          f"LikesMin := {t['likes'][0]}, LikesMax := {t['likes'][1]}, CapsuleChance := {f(t['capsule_chance'])}, "
          f"EpicPlus := {'true' if t['epic_plus'] else 'false'}}}")
    w("")
    dq = c["daily_quests"]
    for diff in ("easy", "medium", "hard"):
        w(f"LabQuests{diff.capitalize()}:[]quest_def = array:")
        for kind, target in dq["pool"][diff]:
            w(f"    quest_def{{Kind := {QUESTS.index(kind)}, Target := {target}}}")
    rw = dq["rewards"]
    w(f"LabQuestLikes:[]int = {ints([rw['easy']['likes'], rw['medium']['likes'], rw['hard']['likes']])}")
    w(f"LabQuestCrystals:[]int = {ints([rw['easy'].get('hype_crystals', 0), rw['medium'].get('hype_crystals', 0), rw['hard'].get('hype_crystals', 0)])}")
    w("")
    w("LabOffers:[]offer_def = array:")
    for o in c["vbucks_offers"]:
        w(f"    offer_def{{Key := {s(o['id'])}, Name := {s(o['name'])}, Price := {o['price']}, Effect := {s(o['effect'])}, Week := {o.get('from_week', 0)}}}")
    w("")
    lm = c["lucky_machine"]["chance_to_next_variant"]
    w("# Мем-автомат: шанс перейти на вариант с индексом i (0 не используется)")
    w(f"LabLuckyChance:[]float = {floats([0] + [lm[v] for v in VARIANTS[1:]])}")
    w("")

    # ---- скаляры
    reb, sr, fu = c["rebirth"], c["super_rebirth"], c["fusion"]
    belt, inc, ev = c["belt"], c["incubators"], c["events"]
    junk, likes = c["meme_junk"], c["guest_likes"]
    g = {x["what"]: x for x in belt["guaranteed"]}
    cw = c["epic_plus_weights"]
    scalars = [
        ("LabStartCash", f(c["start_cash"])),
        ("LabSellCashShare", f(c["sell"]["cash_share"])),
        ("LabReserveMax", str(c["reserve_max"])),
        ("LabMaxPlayers", str(c["server"]["max_players"])),
        ("LabRebirthFirstCost", f(reb["first_cost"])),
        ("LabRebirthGrowth", f(reb["cost_growth"])),
        ("LabRebirthIncomeMult", f(reb["income_mult_per_level"])),
        ("LabRebirthLevels", str(reb["levels"])),
        ("LabSlotsStart", str(reb["podium_slots"]["start"])),
        ("LabSlotsPerLevel", str(reb["podium_slots"]["per_level"])),
        ("LabSlotsMax", str(reb["podium_slots"]["max"])),
        ("LabSuperFromWeek", str(sr["available_from_week"])),
        ("LabSuperUnlockRebirth", str(sr["unlock"]["rebirth"])),
        ("LabCrystalsAt12", f(sr["crystals_at_rebirth"]["12"])),
        ("LabCrystalsAt35", f(sr["crystals_at_rebirth"]["35"])),
        ("LabSuperIncomeMult", f(sr["permanent_income_mult_per_super_rebirth"])),
        ("LabIdealChance", f(c["ideal"]["chance_on_hatch"])),
        ("LabIdealBonus", f(c["ideal"]["income_bonus_per_unique"])),
        ("LabOfflineRate", f(c["offline"]["rate"])),
        ("LabOfflineCapHours", f(c["offline"]["cap_hours"])),
        ("LabBeltStepSec", f(belt["spawn_interval_sec"])),
        ("LabGuaranteedLegendarySec", f(g["legendary"]["every_min"] * 60)),
        ("LabGuaranteedRainbowSec", f(g["rainbow_variant"]["every_min"] * 60)),
        ("LabGuaranteedMythicSec", f(g["mythic"]["every_min"] * 60)),
        ("LabGuaranteedMythicWeek", str(g["mythic"]["from_week"])),
        ("LabGuaranteedLavaSec", f(g["lava_variant"]["every_min"] * 60)),
        ("LabGuaranteedLavaWeek", str(g["lava_variant"]["from_week"])),
        ("LabIncubatorsStart", str(inc["start"])),
        ("LabIncubatorsMax", str(inc["max"])),
        ("LabHitSpeedup", f(inc["pickaxe_hit_speedup_sec"])),
        ("LabCritChance", f(inc["crit_chance"])),
        ("LabCritMult", f(inc["crit_mult"])),
        ("LabJunkRespawnSec", f(junk["pile_respawn_sec"])),
        ("LabJunkHits", str(junk["hits_to_collect"])),
        ("LabSpicyWeek", str(junk["spicy_week"]["week"])),
        ("LabSpicyRespawnMult", f(junk["spicy_week"]["respawn_mult"])),
        ("LabSpicyLavaWeight", f(junk["spicy_week"]["lava_weight"])),
        ("LabOwnerLikes", str(likes["owner_likes"])),
        ("LabGuestLikes", str(likes["guest_likes"])),
        ("LabFusionUnlockRebirth", str(fu["unlock_rebirth"])),
        ("LabFusionWeek", str(fu["available_from_week"])),
        ("LabFusionVariantMin", f(fu["variant_upgrade"]["time_min"])),
        ("LabFusionEpicMin", f(fu["time_min"]["epic"])),
        ("LabFusionLegendaryMin", f(fu["time_min"]["legendary"])),
        ("LabFusionMythicMin", f(fu["time_min"]["mythic"])),
        ("LabFusionCostMult", "2.0"),
        ("LabCompanionSlotsStart", str(c["companion_slots"]["start"])),
        ("LabMainEventWeekday", str(WEEKDAYS.index(ev["weekly_main"]["day"]))),
        ("LabMainEventStartHourUtc", str(ev["weekly_main"]["start_utc_hour"])),
        ("LabMainEventHours", f(ev["weekly_main"]["duration_h"])),
        ("LabMainEventIncomeMult", f(ev["weekly_main"]["income_mult"])),
        ("LabMainEventHatchMult", f(ev["weekly_main"]["hatch_speed_mult"])),
        ("LabMiniEventWeekday", str(WEEKDAYS.index(ev["weekly_mini"]["day"]))),
        ("LabMiniEventLikesMult", f(ev["weekly_mini"]["likes_mult"])),
        ("LabPinataEverySec", f(ev["weekly_mini"]["spawn_every_min"] * 60)),
        ("LabPinataHitsPerPlayer", str(ev["weekly_mini"]["hp_hits_per_player"])),
        ("LabPinataCrystals", str(ev["weekly_mini"]["reward_crystals"])),
    ]
    w("# Скаляры")
    for name, val in scalars:
        typ = "float" if "." in val or "e" in val else "int"
        w(f"{name}:{typ} = {val}")
    w("")
    w("# Веса редкости для наград «Эпик или выше» (гастроли на ночь)")
    w(f"LabEpicPlusWeights:[]float = {floats([0, 0, cw['epic'], cw['legendary'], cw['mythic'], 0])}")
    w("# Мем-мусор: вес, вариант сёрджа, неделя появления (по порядку видов)")
    w(f"LabJunkNames:[]string = array{{{', '.join(s(k['name']) for k in junk['kinds'])}}}")
    w(f"LabJunkWeights:[]float = {floats([k['weight'] for k in junk['kinds']])}")
    w(f"LabJunkVariant:[]int = {ints([VARIANTS.index(k['surge_variant']) for k in junk['kinds']])}")
    w(f"LabJunkWeek:[]int = {ints([k['from_week'] for k in junk['kinds']])}")
    lo, hi = sr["crystals_at_rebirth"]["12"], sr["crystals_at_rebirth"]["35"]
    top, start = reb["levels"], sr["unlock"]["rebirth"]
    table = [round(lo * (hi / lo) ** ((r - start) / (top - start))) for r in range(start, top + 1)]
    w(f"# Кристаллы за «Вирусный взрыв»: индекс = перерождение − {start}")
    w(f"LabSuperCrystals:[]int = {ints(table)}")
    w("# Сила перка компаньона по редкости")
    pr = c["companion_perk_by_rarity"]
    w(f"LabCompanionPerk:[]float = {floats([pr[r] for r in RARITIES[:5]] + [0.4])}")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)}: {len(L)} строк, {len(ids)} брейнротов, {len(c['rebirth']['requirements'])} перерождений")


if __name__ == "__main__":
    main()
