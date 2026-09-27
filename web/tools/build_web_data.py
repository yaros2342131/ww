"""Данные браузерной версии: config/brainrot_lab_tycoon.json → web/brainrot-lab/data.js (window.LAB).

    python web/tools/build_web_data.py
Игра в браузере и Verse читают один и тот же конфиг, поэтому правила совпадают.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CFG = ROOT / "config" / "brainrot_lab_tycoon.json"
OUT = ROOT / "web" / "brainrot-lab" / "data.js"
RAR = ["common", "rare", "epic", "legendary", "mythic", "iconic"]
VAR = ["base", "gold", "diamond", "rainbow", "lava", "viral", "cosmic"]


def main():
    c = json.loads(CFG.read_text(encoding="utf-8"))
    ids = [b["id"] for b in c["brainrots"]]
    idx = {k: i for i, k in enumerate(ids)}
    fam_of = {m: i for i, f in enumerate(c["families"]) for m in f["members"]}
    title = {k: json.loads((ROOT / "models" / "brainrots" / k / "info.json").read_text(encoding="utf-8"))["title"] for k in ids}
    reb, sr, fu = c["rebirth"], c["super_rebirth"], c["fusion"]
    junk, likes = c["meme_junk"], c["guest_likes"]
    lo, hi = sr["crystals_at_rebirth"]["12"], sr["crystals_at_rebirth"]["35"]
    start, top = sr["unlock"]["rebirth"], reb["levels"]
    g = {x["what"]: x for x in c["belt"]["guaranteed"]}
    data = {
        "rarities": [{"key": r["id"], "name": r["name"], "income": r["income_per_sec"], "payback": r["payback_sec"] or 0,
                      "hatch": r["hatch_sec"], "weight": r["belt_weight"],
                      "sellLikes": r["sell_likes"] or 0} for r in c["rarities"]],
        "variants": [{"key": v["id"], "name": v["name"], "mult": v["income_mult"], "belt": v["belt_chance"] or 0,
                      "week": v["available_from_week"]} for v in c["variants"]],
        "brainrots": [{"key": b["id"], "title": title[b["id"]], "rarity": RAR.index(b["rarity"]), "family": fam_of[b["id"]],
                       "source": b["source"], "week": b["release_week"], "perk": b.get("perk", "")} for b in c["brainrots"]],
        "families": [{"key": f["id"], "name": f["name"], "perk": f["companion_perk"], "members": [idx[m] for m in f["members"]]}
                     for f in c["families"]],
        "perkText": c["companion_perks"],
        "familyBonus": {int(k): v for k, v in c["family_combo"]["by_count"].items()},
        "familyFull": c["family_combo"]["full_family_extra"],
        "combos": [{"name": x["name"], "bonus": x["bonus"], "members": [idx[m] for m in x["members"]], "week": x["release_week"]}
                   for x in c["special_combos"]],
        "recipes": [{"result": idx[r["result"]], "inputs": [idx[i] for i in r["inputs"]], "hint": r["hint"]} for r in fu["recipes"]],
        "rebirthReqs": [{"ids": [idx[n] for n, _ in r["need"]], "vars": [VAR.index(v) for _, v in r["need"]]}
                        for r in sorted(reb["requirements"], key=lambda r: r["level"])],
        "upgrade": [c["upgrade_costs_likes"][r] or [] for r in RAR],
        "shop": c["hype_shop"],
        "tours": c["tours"]["list"],
        "quests": {k: [{"kind": q[0], "target": q[1]} for q in v] for k, v in c["daily_quests"]["pool"].items()},
        "questRewards": c["daily_quests"]["rewards"],
        "offers": c["vbucks_offers"],
        "lucky": [0] + [c["lucky_machine"]["chance_to_next_variant"][v] for v in VAR[1:]],
        "superCrystals": [round(lo * (hi / lo) ** ((r - start) / (top - start))) for r in range(start, top + 1)],
        "companionPerk": [c["companion_perk_by_rarity"][r] for r in RAR[:5]] + [0.4],
        "events": c["events"]["schedule"],
        "junk": [{"name": k["name"], "weight": k["weight"], "variant": VAR.index(k["surge_variant"]), "week": k["from_week"]} for k in junk["kinds"]],
        "n": {
            "startCash": c["start_cash"], "sellShare": c["sell"]["cash_share"], "reserveMax": c["reserve_max"],
            "rebirthFirst": reb["first_cost"], "rebirthGrowth": reb["cost_growth"], "rebirthMult": reb["income_mult_per_level"],
            "rebirthLevels": top, "slotsStart": reb["podium_slots"]["start"], "slotsPer": reb["podium_slots"]["per_level"],
            "slotsMax": reb["podium_slots"]["max"], "superWeek": sr["available_from_week"], "superRebirth": start,
            "superMult": sr["permanent_income_mult_per_super_rebirth"], "idealChance": c["ideal"]["chance_on_hatch"],
            "idealBonus": c["ideal"]["income_bonus_per_unique"], "offlineRate": c["offline"]["rate"],
            "offlineCap": c["offline"]["cap_hours"], "beltStep": c["belt"]["spawn_interval_sec"],
            "gLegend": g["legendary"]["every_min"] * 60, "gRainbow": g["rainbow_variant"]["every_min"] * 60,
            "gMythic": g["mythic"]["every_min"] * 60, "gMythicWeek": g["mythic"]["from_week"],
            "gLava": g["lava_variant"]["every_min"] * 60, "gLavaWeek": g["lava_variant"]["from_week"],
            "incStart": c["incubators"]["start"], "incMax": c["incubators"]["max"], "hit": c["incubators"]["pickaxe_hit_speedup_sec"],
            "crit": c["incubators"]["crit_chance"], "critMult": c["incubators"]["crit_mult"],
            "epicPlus": [0, 0] + [c["epic_plus_weights"][r] for r in ("epic", "legendary", "mythic")],
            "junkRespawn": junk["pile_respawn_sec"], "junkHits": junk["hits_to_collect"], "junkSpots": junk["pile_spots"],
            "spicyWeek": junk["spicy_week"]["week"], "spicyRespawn": junk["spicy_week"]["respawn_mult"], "spicyLava": junk["spicy_week"]["lava_weight"],
            "ownerLikes": likes["owner_likes"], "guestLikes": likes["guest_likes"],
            "fusionWeek": fu["available_from_week"], "fusionRebirth": fu["unlock_rebirth"],
            "fusionVarMin": fu["variant_upgrade"]["time_min"], "fusionMin": [0, 0, fu["time_min"]["epic"], fu["time_min"]["legendary"],
                                                                         fu["time_min"]["mythic"], fu["time_min"]["mythic"]],
            "eventIncome": c["events"]["weekly_main"]["income_mult"], "eventHatch": c["events"]["weekly_main"]["hatch_speed_mult"],
            "pinataEvery": c["events"]["weekly_mini"]["spawn_every_min"] * 60, "pinataHits": c["events"]["weekly_mini"]["hp_hits_per_player"],
            "pinataCrystals": c["events"]["weekly_mini"]["reward_crystals"], "miniLikes": c["events"]["weekly_mini"]["likes_mult"],
            "players": c["server"]["max_players"],
        },
    }
    OUT.write_text("// АВТОГЕНЕРАЦИЯ: python web/tools/build_web_data.py (из config/brainrot_lab_tycoon.json)\n"
                   "window.LAB = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(OUT.relative_to(ROOT), OUT.stat().st_size, "байт")


if __name__ == "__main__":
    main()
