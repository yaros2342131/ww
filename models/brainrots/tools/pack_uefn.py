"""Пакет для UEFN: все брейнроты в одном архиве, готовые к импорту.

    python pack_uefn.py            # → models/brainrots/Brainrots_UEFN.zip

Что делается с каждой моделью:
  * разворот лицом к +X (в Unreal «вперёд» — ось X), пивот — центр основания, единицы — сантиметры;
  * текстура уменьшается до 1024² и встраивается в FBX — материал создастся сам при импорте;
  * добавляется коллизия UCX_<меш> (выпуклая оболочка) — Unreal подхватывает её автоматически.
В архиве: Brainrots_All.fbx (все модели одним файлом, каждая — отдельный Static Mesh),
Meshes/SM_*.fbx (по одной), Textures/T_*.png, Previews/*.jpg, README_UEFN.txt.
"""
import glob
import json
import math
import os
import shutil
import sys
import zipfile

sys.path.insert(0, os.path.dirname(__file__))
import kit  # noqa: E402
import bmesh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Matrix  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TEX_RES = 1024
HULL_TRIS = 120  # упрощённая коллизия: мало треугольников — дёшево для физики

README = """Брейнроты для UEFN — {n} моделей

ИМПОРТ ВСЕХ СРАЗУ
1. Content Browser → создайте папку Brainrots → Import → Brainrots_All.fbx
2. В окне импорта FBX:
   - Import Mesh: Static Mesh (Skeletal Mesh выключен)
   - Combine Meshes: ВЫКЛЮЧЕН  (иначе все {n} слипнутся в один меш)
   - Auto Generate Collision: ВЫКЛЮЧЕН (коллизия UCX уже внутри файла)
   - Material Import Method: Create New Materials, Import Textures: ВКЛ
3. Import All. Получится {n} Static Mesh + материалы + текстуры.

ИМПОРТ ПО ОДНОЙ
Meshes/SM_<Имя>.fbx — те же настройки. Сначала импортируйте Textures/T_<Имя>_BaseColor.png,
затем в материале M_<Имя> подключите её к Base Color (в общем файле текстуры уже встроены).

ПАРАМЕТРЫ
- Масштаб: сантиметры, рост 1.2–1.9 м. Пивот — центр основания на полу.
- Лицом по +X (стандарт Unreal).
- 15 000 треугольников, 1 материал, текстура 1024x1024 на модель.
- Коллизия: UCX (выпуклая оболочка, ~{hull} треугольников).

СОВЕТЫ
- Много брейнротов в кадре → в каждом меше LOD Settings → Number of LODs = 3 → Apply.
- Покачивание/вращение на подставке — через Verse (MoveTo / TeleportTo по таймеру).

Список: {names}
"""


def prepare(folder):
    """Импортировать собранную модель и подготовить её к UEFN. Возвращает (меш, коллизия, путь текстуры)."""
    info = json.load(open(os.path.join(folder, 'info.json'), encoding='utf-8'))
    name = info['name']
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=os.path.join(folder, info['fbx']))
    obj = [o for o in bpy.data.objects if o not in before and o.type == 'MESH'][0]
    kit.select(obj)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    obj.data.transform(Matrix.Rotation(math.radians(90), 4, 'Z'))  # лицо -Y → +X
    obj.name = obj.data.name = 'SM_' + name

    # текстура 1024² и материал с ней
    src = os.path.join(folder, info['texture'])
    img = bpy.data.images.load(src)
    img.scale(TEX_RES, TEX_RES)
    tex_path = os.path.join(OUT_TEX, f'T_{name}_BaseColor.png')
    img.filepath_raw = tex_path
    img.file_format = 'PNG'
    img.save()
    m = bpy.data.materials.new('M_' + name)
    m.use_nodes = True
    t = m.node_tree.nodes.new('ShaderNodeTexImage')
    t.image = img
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Roughness'].default_value = 0.5
    m.node_tree.links.new(t.outputs['Color'], b.inputs['Base Color'])
    obj.data.materials.clear()
    obj.data.materials.append(m)

    # коллизия UCX: выпуклая оболочка, упрощённая до HULL_TRIS
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.convex_hull(bm, input=bm.verts, use_existing_faces=False)
    me = bpy.data.meshes.new('UCX_' + obj.name)
    bm.to_mesh(me)
    bm.free()
    hull = bpy.data.objects.new('UCX_' + obj.name, me)
    bpy.context.collection.objects.link(hull)
    kit.decimate(hull, HULL_TRIS)
    kit.select(hull)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.convex_hull()  # после упрощения снова строго выпуклая
    bpy.ops.object.mode_set(mode='OBJECT')
    return obj, hull, tex_path, info


def export(objs, path, embed=True):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={'MESH'},
                             apply_unit_scale=True, apply_scale_options='FBX_SCALE_UNITS',
                             mesh_smooth_type='FACE', path_mode='COPY' if embed else 'STRIP', embed_textures=embed,
                             bake_anim=False, axis_forward='-Z', axis_up='Y')


def pack(folders, zpath, all_name):
    global OUT_TEX
    stage = os.path.join(ROOT, '_uefn_pack')
    shutil.rmtree(stage, ignore_errors=True)
    out_mesh, OUT_TEX, out_prev = (os.path.join(stage, d) for d in ('Meshes', 'Textures', 'Previews'))
    for d in (out_mesh, OUT_TEX, out_prev):
        os.makedirs(d)
    kit.reset()
    all_objs, names = [], []
    from PIL import Image
    for folder in folders:
        obj, hull, tex, info = prepare(folder)
        export([obj, hull], os.path.join(out_mesh, obj.name + '.fbx'), embed=False)
        im = Image.open(os.path.join(folder, 'preview.png')).convert('RGB')
        im.thumbnail((1280, 1280))
        im.save(os.path.join(out_prev, info['name'] + '.jpg'), quality=85)
        all_objs += [obj, hull]
        names.append(info['title'])
        print('PACKED', obj.name)
    export(all_objs, os.path.join(stage, all_name))
    with open(os.path.join(stage, 'README_UEFN.txt'), 'w', encoding='utf-8') as f:
        f.write(README.format(n=len(names), hull=HULL_TRIS, names=', '.join(names)).replace('Brainrots_All.fbx', all_name))
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
        for base, _, files in os.walk(stage):
            for fn in files:
                full = os.path.join(base, fn)
                z.write(full, os.path.join(os.path.splitext(os.path.basename(zpath))[0], os.path.relpath(full, stage)))
    shutil.rmtree(stage)
    print('ZIP', zpath, round(os.path.getsize(zpath) / 1e6, 1), 'MB', len(names), 'models')


if __name__ == '__main__':
    # python pack_uefn.py             → Brainrots_UEFN.zip (все модели)
    # python pack_uefn.py --parts 3   → Brainrots_UEFN_1of3.zip ... (каждая часть < 30 МБ, для пересылки)
    folders = sorted(f for f in glob.glob(os.path.join(ROOT, '*')) if os.path.isfile(os.path.join(f, 'info.json')))
    out_dir = ROOT
    if '--out' in sys.argv:
        out_dir = sys.argv[sys.argv.index('--out') + 1]
    if '--parts' in sys.argv:
        n = int(sys.argv[sys.argv.index('--parts') + 1])
        size = -(-len(folders) // n)
        for i in range(n):
            chunk = folders[i * size:(i + 1) * size]
            if chunk:
                pack(chunk, os.path.join(out_dir, f'Brainrots_UEFN_{i + 1}of{n}.zip'), f'Brainrots_Part{i + 1}.fbx')
    else:
        pack(folders, os.path.join(out_dir, 'Brainrots_UEFN.zip'), 'Brainrots_All.fbx')
