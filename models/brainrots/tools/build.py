"""Сборка воксельных брейнротов: сетка кубиков → greedy-меш → FBX + палитра + превью.

    python build.py                     # все персонажи
    python build.py SixSeven_67
Нужен Python 3.11 с bpy 4.2 (pip install bpy==4.2.0 pillow numpy).
Результат: models/brainrots/<Имя>/SM_<Имя>.fbx, T_<Имя>_Palette.png, preview.png, info.json
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import kit  # noqa: E402
import voxel  # noqa: E402
from voxel_chars import VOX_CHARACTERS  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MAX_TRIS = 20000


def build(key):
    title, fn = VOX_CHARACTERS[key]
    out = os.path.join(ROOT, key)
    os.makedirs(out, exist_ok=True)
    kit.reset()
    vox, size = fn()
    obj, tex = voxel.finalize(vox, key, out, size)
    n_tris = kit.tris(obj)
    assert n_tris <= MAX_TRIS, f'{key}: {n_tris} треугольников > {MAX_TRIS}'
    dims = obj.dimensions
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
    d.text((16, 10), f'{title}  ·  {n_tris:,} tris  ·  {dims.z * 100:.0f} см'.replace(',', ' '), fill=(255, 255, 255),
           font=font)
    sheet.save(os.path.join(out, 'preview.png'))
    info = {'name': key, 'title': title, 'tris': n_tris,
            'size_cm': [round(dims.x * 100), round(dims.y * 100), round(dims.z * 100)],
            'fbx': os.path.basename(fbx), 'texture': os.path.basename(tex), 'materials': 1,
            'colors': len(vox.palette)}
    with open(os.path.join(out, 'info.json'), 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    print('BUILT', info)
    return info


if __name__ == '__main__':
    keys = [a for a in sys.argv[1:] if not a.startswith('-')] or list(VOX_CHARACTERS)
    for k in keys:
        build(k)
