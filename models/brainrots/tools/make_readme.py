"""Пересобрать models/brainrots/README.md по info.json всех моделей."""
import glob
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

rows = []
for f in sorted(glob.glob(os.path.join(ROOT, '*', 'info.json'))):
    i = json.load(open(f, encoding='utf-8'))
    d = os.path.basename(os.path.dirname(f))
    w, dp, h = i['size_cm']
    rows.append(f"| {len(rows) + 1} | {i['title']} | {i['tris']:,} | {w}×{dp}×{h} см | [превью]({d}/preview.png) |"
                .replace(',', ' '))

text = f"""# Брейнроты для UEFN — {len(rows)} моделей

Гладкие мультяшные модели мем-брейнротов. Статичные меши для подставок в тайкуне.

## Готовый пакет для импорта
**[`Brainrots_UEFN.zip`](Brainrots_UEFN.zip)** — всё, что нужно для UEFN:
- `Brainrots_All.fbx` — все модели одним файлом (каждая — отдельный Static Mesh, текстуры встроены);
- `Meshes/SM_*.fbx` — по одной модели, `Textures/T_*.png` — текстуры 1024², `Previews/` — картинки;
- `README_UEFN.txt` — пошаговый импорт.

Модели в пакете уже подготовлены: лицом по +X (стандарт Unreal), сантиметры, пивот на полу по центру,
коллизия `UCX_` (выпуклая оболочка) внутри FBX, 15 000 треугольников и один материал на модель.

**Главное при импорте `Brainrots_All.fbx`:** `Combine Meshes` — выключить, `Auto Generate Collision` — выключить.

## Список
| # | Персонаж | Треугольники | Размер (Ш×Г×В) | Превью |
|---|---|---|---|---|
""" + "\n".join(rows) + """

## Генератор
Каждый персонаж описан кодом: объёмные формы на мелкой сетке → гладкая поверхность → 15 000 треугольников →
цвета запекаются в одну текстуру.
```
pip install bpy==4.2.0 pillow numpy scipy scikit-image   # Python 3.11
python tools/build.py                                   # собрать все модели
python tools/build.py Cocofanto_Elefanto                # одну
python tools/pack_uefn.py                               # пакет для UEFN (zip)
python tools/make_readme.py                             # этот README
```
- `tools/voxel_chars.py`, `tools/chars_a.py`, `chars_b.py`, `chars_c.py` — персонажи;
- `tools/parts.py` — общие детали (глаза, рты, лапы, крылья, хвосты, узоры);
- `tools/voxel.py` — рисование формами, гладкая поверхность, запекание; `tools/kit.py` — экспорт и превью.
"""
open(os.path.join(ROOT, 'README.md'), 'w', encoding='utf-8').write(text)
print(len(rows), 'models in README')
