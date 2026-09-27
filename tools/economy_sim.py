"""Симуляция темпа перерождений для «Брейнрот Лаборатории».

Читает config/brainrot_lab_tycoon.json и гоняет бота-игрока: конвейер → инкубаторы → подиум →
перерождение. Показывает медианное время (в часах игры) до каждого уровня перерождения.

Бот играет идеально, поэтому живой игрок медленнее примерно в 2–3 раза. Лайки бот тратит только
на варианты, которых требует перерождение. Прокачка дохода за Лайки, скрещивание, комбо семей и
супер-перерождение не моделируются: «стена» после R20 — место, где эти системы должны включаться.
Брейнротов, которые выдаёт только скрещивание (нужны с R22), бот получить не может.

    python tools/economy_sim.py                 # контент недели 0 (запуск)
    python tools/economy_sim.py --week 8 --seeds 20 --hours 200
"""
import argparse
import json
import random
import statistics
from pathlib import Path

CONFIG = Path(__file__).resolve().parent.parent / "config" / "brainrot_lab_tycoon.json"
TIERS = ["common", "rare", "epic", "legendary", "mythic"]
VARIANTS = ["base", "gold", "diamond", "rainbow", "lava", "viral", "cosmic"]


def load(week):
    c = json.loads(CONFIG.read_text(encoding="utf-8"))
    rar = {r["id"]: r for r in c["rarities"]}
    var = {v["id"]: v for v in c["variants"]}
    pool = {t: [b["id"] for b in c["brainrots"]
                if b["rarity"] == t and b["source"] == "belt" and b["release_week"] <= week]
            for t in TIERS}
    guaranteed = {g["what"]: g["every_min"] * 60 for g in c["belt"]["guaranteed"] if g["from_week"] <= week}
    reqs = {r["level"]: [(n, VARIANTS.index(v)) for n, v in r["need"]] for r in c["rebirth"]["requirements"]}
    rarity_of = {b["id"]: b["rarity"] for b in c["brainrots"]}
    return c, rar, var, pool, guaranteed, reqs, rarity_of


def requirement(level, reqs, pool):
    """Требования из конфига, дальше — 3 случайных легендарки/мифика (как заглушка)."""
    if level in reqs:
        return reqs[level]
    tier = "legendary" if level <= 16 or not pool["mythic"] else "mythic"
    rng = random.Random(1000 + level)
    names = pool[tier]
    return [(n, 0) for n in rng.sample(names, min(3, len(names)))]


def roll_variant(rng, var):
    x = rng.random()
    acc = 0.0
    for vid in ("rainbow", "diamond", "gold"):
        acc += var[vid]["belt_chance"]
        if x < acc:
            return VARIANTS.index(vid)
    return 0


def run(seed, hours, week, grab, players):
    c, rar, var, pool, guaranteed, reqs, rarity_of = load(week)
    upgrade = c["upgrade_costs_likes"]
    rng = random.Random(seed)
    tiers = [t for t in TIERS if pool[t]]
    reb, junk = c["rebirth"], c["meme_junk"]
    belt, inc_cfg = c["belt"], c["incubators"]
    kinds = [k for k in junk["kinds"] if k["from_week"] <= week]
    junk_every = 180.0   # бот раз в ~3 минуты разбивает кучу и сдаёт мусор Сахуру
    next_junk, surge = junk_every, 0
    surges = 0

    cash = float(c["start_cash"])
    likes = 0
    best = {}          # id брейнрота -> лучший вариант
    incomes = []       # доход каждого юнита на подиуме/в запасе
    top_sum = 0.0
    hatching = []      # (время готовности, id, вариант, доход)
    level, t, dt = 0, 0.0, float(belt["spawn_interval_sec"])
    next_g = dict(guaranteed)
    marks = {}

    while t < hours * 3600 and level < reb["levels"]:
        weights = [rar[k]["belt_weight"] for k in tiers]
        if t >= next_junk:   # сёрдж: следующая капсула у портала станет этого варианта
            next_junk += junk_every
            kind = rng.choices(kinds, [k["weight"] for k in kinds])[0]
            surge = max(surge, VARIANTS.index(kind["surge_variant"]))
            surges += 1
        slots = min(reb["podium_slots"]["max"], reb["podium_slots"]["start"] + level * reb["podium_slots"]["per_level"])

        done = [h for h in hatching if h[0] <= t]
        if done:
            hatching = [h for h in hatching if h[0] > t]
            for _, bid, v, income in done:
                best[bid] = max(best.get(bid, -1), v)
                incomes.append(income)
                likes += rar[rarity_of[bid]]["sell_likes"]   # дубли и вытесненные с подиума продаются
            incomes.sort(reverse=True)
            del incomes[reb["podium_slots"]["max"]:]   # лишние всё равно продаются
            top_sum = sum(incomes[:slots])

        need = requirement(level + 1, reqs, pool)
        for _ in range(1):
            k = rng.choices(tiers, weights)[0]
            v = max(roll_variant(rng, var), surge)
            surge = 0
            for what, every in guaranteed.items():
                if t >= next_g[what]:
                    next_g[what] += every
                    if what.endswith("_variant"):
                        v = VARIANTS.index(what[: -len("_variant")])
                    elif pool.get(what):
                        k = what
            bid = rng.choice(pool[k])
            mult = var[VARIANTS[v]]["income_mult"]
            income = rar[k]["income_per_sec"] * mult
            price = income * rar[k]["payback_sec"]
            worst = incomes[slots - 1] if len(incomes) >= slots else 0
            wanted = any(n == bid and best.get(bid, -1) < mv <= v for n, mv in need) or \
                any(n == bid and bid not in best for n, _ in need)
            if len(hatching) < inc_cfg["start"] and cash >= price and (income > worst or wanted) and rng.random() < grab:
                cash -= price
                hatching.append((t + rar[k]["hatch_sec"], bid, v, income))

        cash += top_sum * reb["income_mult_per_level"] ** level * dt

        for n, mv in need:   # нужный вариант докачиваем за Лайки, как сделал бы живой игрок
            have = best.get(n, -1)
            if 0 <= have < mv and upgrade[rarity_of[n]]:
                price = sum(upgrade[rarity_of[n]][have:mv])
                if likes >= price:
                    likes -= price
                    best[n] = mv

        cost = reb["first_cost"] * reb["cost_growth"] ** level
        if cash >= cost and all(best.get(n, -1) >= mv for n, mv in need):
            cash = 0.0
            level += 1
            marks[level] = t / 3600
            slots = min(reb["podium_slots"]["max"], reb["podium_slots"]["start"] + level * reb["podium_slots"]["per_level"])
            top_sum = sum(incomes[:slots])
        t += dt
    return marks, surges / max(t / 3600, 1e-9)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--hours", type=float, default=120)
    ap.add_argument("--week", type=int, default=0, help="неделя контента после запуска")
    ap.add_argument("--grab", type=float, default=0.3, help="шанс успеть купить капсулу раньше других")
    ap.add_argument("--players", type=int, default=8)
    a = ap.parse_args()
    c = json.loads(CONFIG.read_text(encoding="utf-8"))
    results = [run(s, a.hours, a.week, a.grab, a.players) for s in range(a.seeds)]
    runs = [m for m, _ in results]
    for lvl in (1, 2, 3, 5, 8, 10, 12, 15, 20, 25, 30, 35):
        cost = c["rebirth"]["first_cost"] * c["rebirth"]["cost_growth"] ** (lvl - 1)
        got = [m[lvl] for m in runs if lvl in m]
        tail = f"медиана {statistics.median(got):6.2f} ч  ({len(got)}/{a.seeds})" if got else f"не достигнут за {a.hours:g} ч"
        print(f"R{lvl:<2}  цена {cost:>10.3g}  {tail}")
    per_hour = statistics.median(r for _, r in results)
    print(f"Сёрджей от мем-мусора (свои): {per_hour:.0f} в час")


if __name__ == "__main__":
    main()
