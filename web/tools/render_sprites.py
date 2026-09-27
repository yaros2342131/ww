"""Спрайты для браузерной игры: брейнроты и пропсы на прозрачном фоне (WebP с альфой).

    python web/tools/render_sprites.py          # все
    python web/tools/render_sprites.py Tim_Cheese
Нужен Python 3.11 с bpy 4.2 и pillow. Результат: web/brainrot-lab/img/b/*.webp, img/p/*.webp
"""
import json
import math
import os
import sys

import bpy
from mathutils import Vector
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(ROOT, 'web', 'brainrot-lab', 'img')
SIZE = 256
PROPS = ['Capsule_Common', 'Capsule_Rare', 'Capsule_Epic', 'Capsule_Legendary', 'Capsule_Mythic', 'Capsule_Iconic',
         'Incubator', 'MemePortal', 'FusionTable', 'MemeMachine', 'TourBus', 'Pinata', 'HypeTower', 'SahurTotem',
         'RebirthAltar', 'CappuccinoFountain', 'LemonTree', 'CafeUmbrella']


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = 24
    sc.cycles.use_denoising = True
    sc.render.film_transparent = True
    sc.render.resolution_x = sc.render.resolution_y = SIZE
    sc.view_settings.view_transform = 'Standard'
    w = bpy.data.worlds.new('w')
    sc.world = w
    w.use_nodes = True
    w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.55, 0.52, 0.6, 1)
    w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.9


def import_model(fbx, texture=None):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=fbx)
    objs = [o for o in bpy.data.objects if o not in before and o.type == 'MESH' and not o.name.startswith('UCX_')]
    for o in bpy.data.objects:
        if o.name.startswith('UCX_'):
            bpy.data.objects.remove(o)
    if texture:
        img = bpy.data.images.load(texture)
        m = bpy.data.materials.new('tex')
        m.use_nodes = True
        t = m.node_tree.nodes.new('ShaderNodeTexImage')
        t.image = img
        b = m.node_tree.nodes['Principled BSDF']
        b.inputs['Roughness'].default_value = 0.5
        m.node_tree.links.new(t.outputs['Color'], b.inputs['Base Color'])
        for o in objs:
            o.data.materials.clear()
            o.data.materials.append(m)
    return objs


def frame(objs, yaw_deg):
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    center = (lo + hi) / 2
    size = max(hi - lo)
    sc = bpy.context.scene
    cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = size * 1.08
    a = math.radians(yaw_deg)
    d = size * 3
    cam.location = center + Vector((math.sin(a) * d, -math.cos(a) * d, size * 0.35))
    cam.rotation_euler = (center - cam.location).to_track_quat('-Z', 'Y').to_euler()
    for name, off, energy in (('key', (-1.2, -1.6, 1.8), 700), ('fill', (1.6, -1.0, 0.8), 250), ('rim', (0.3, 1.8, 1.6), 600)):
        light = bpy.data.lights.new(name, 'AREA')
        light.energy, light.size = energy * size * size / 2.5, size * 1.5
        lo_ = bpy.data.objects.new(name, light)
        sc.collection.objects.link(lo_)
        lo_.location = center + Vector(off) * size * 1.4
        lo_.rotation_euler = (center - lo_.location).to_track_quat('-Z', 'Y').to_euler()


def render(path_png, path_webp):
    bpy.context.scene.render.filepath = path_png
    bpy.ops.render.render(write_still=True)
    im = Image.open(path_png).convert('RGBA')
    bbox = im.getbbox()
    if bbox:
        im = im.crop(bbox)
    side = max(im.size)
    canvas = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    canvas.paste(im, ((side - im.width) // 2, side - im.height))
    canvas.resize((192, 192), Image.LANCZOS).save(path_webp, 'WEBP', quality=86, method=6)
    os.remove(path_png)


def brainrot(key):
    folder = os.path.join(ROOT, 'models', 'brainrots', key)
    info = json.load(open(os.path.join(folder, 'info.json'), encoding='utf-8'))
    reset()
    objs = import_model(os.path.join(folder, info['fbx']), os.path.join(folder, info['texture']))
    frame(objs, 20)   # лицо модели смотрит в −Y
    render(os.path.join(OUT, 'b', key + '.png'), os.path.join(OUT, 'b', key + '.webp'))


def prop(name):
    folder = os.path.join(ROOT, 'models', 'lab_props', name)
    reset()
    objs = import_model(os.path.join(folder, f'SM_{name}.fbx'), os.path.join(folder, f'T_{name}_BaseColor.png'))
    frame(objs, 110)  # пропсы развёрнуты лицом в +X
    render(os.path.join(OUT, 'p', name + '.png'), os.path.join(OUT, 'p', name + '.webp'))


if __name__ == '__main__':
    os.makedirs(os.path.join(OUT, 'b'), exist_ok=True)
    os.makedirs(os.path.join(OUT, 'p'), exist_ok=True)
    cfg = json.load(open(os.path.join(ROOT, 'config', 'brainrot_lab_tycoon.json'), encoding='utf-8'))
    keys = [b['id'] for b in cfg['brainrots']]
    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    for k in (args or keys + PROPS):
        (brainrot if k in keys else prop)(k)
        print('SPRITE', k)
