"""Сборка брейнротов: модель → запекание текстуры → FBX → превью.

    python build.py                 # все персонажи
    python build.py Keksolino_Meteorino
Нужен Python 3.11 с модулем bpy 4.2 (pip install bpy==4.2.0) и pillow.
Результат: models/brainrots/<Имя>/SM_<Имя>.fbx, T_<Имя>_BaseColor.png, preview.png
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import kit  # noqa: E402
from characters import CHARACTERS  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MAX_TRIS = 20000  # лимит UEFN-пилота: запас до 30k


def build(key):
    title, fn = CHARACTERS[key]
    out = os.path.join(ROOT, key)
    os.makedirs(out, exist_ok=True)
    kit.reset()
    parts = fn()
    obj = kit.finalize(parts, key, MAX_TRIS)
    n_tris = kit.tris(obj)
    bb = [v for v in obj.bound_box]
    height = max(v[2] for v in bb)
    kit.bake(obj, out)
    fbx = kit.export_fbx(obj, out)
    views = kit.render_views(obj, out)
    ims = [Image.open(f) for f in views]
    w, h = ims[0].size
    sheet = Image.new('RGB', (w * len(ims), h + 50), (20, 24, 50))
    for i, im in enumerate(ims):
        sheet.paste(im, (i * w, 50))
        os.remove(views[i])
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype('DejaVuSans-Bold.ttf', 26)
    except OSError:
        font = ImageFont.load_default()
    d.text((16, 10), f'{title}  ·  {n_tris:,} tris  ·  {height * 100:.0f} см'.replace(',', ' '), fill=(255, 255, 255),
           font=font)
    sheet.save(os.path.join(out, 'preview.png'))
    info = {'name': key, 'title': title, 'tris': n_tris, 'height_cm': round(height * 100), 'fbx': os.path.basename(fbx),
            'texture': f'T_{key}_BaseColor.png', 'materials': 1}
    with open(os.path.join(out, 'info.json'), 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    print('BUILT', info)
    return info


if __name__ == '__main__':
    keys = [a for a in sys.argv[1:] if not a.startswith('-')] or list(CHARACTERS)
    for k in keys:
        build(k)
