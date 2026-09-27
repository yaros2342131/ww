# Брейнрот Лаборатория — тайкун для Fortnite (UEFN)

Тайкун по схеме Star Wars: Droid Tycoon, где вместо дроидов — брейнроты.

| Что | Где |
|---|---|
| Разбор Droid Tycoon, концепт, деньги | [docs/brainrot-lab-tycoon.md](docs/brainrot-lab-tycoon.md) |
| **Готовый тайкун: механики, карта, модели, Verse, сборка** | [docs/brainrot-lab/](docs/brainrot-lab/README.md) |
| Verse-код | [verse/](verse) |
| Баланс (один источник чисел) | [config/brainrot_lab_tycoon.json](config/brainrot_lab_tycoon.json) |
| 40 моделей брейнротов | [models/brainrots/](models/brainrots/README.md) |
| 29 пропсов лаборатории | [models/lab_props/](models/lab_props) |
| План удержания на 30 дней (мобильный концепт) | [docs/retention-30-days.md](docs/retention-30-days.md) |

Инструменты:
```
python tools/gen_verse_data.py                  # конфиг → verse/lab_data.verse
python tools/economy_sim.py --week 0            # темп перерождений и шторма
python models/lab_props/tools/build_props.py    # пересобрать пропсы (нужен bpy 4.2)
```
