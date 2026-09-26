"""Набор деталей для процедурных брейнротов: примитивы, лепка через voxel remesh,
глаза/рот/конечности, запекание в одну текстуру, экспорт FBX под UEFN, превью-рендер.

Запуск только через Blender-Python (bpy 4.2): см. build.py.
Единицы: 1 unit Blender = 1 м = 100 см в UEFN. Лицо персонажа смотрит в -Y, ноги стоят на Z=0.
"""
import math
import os
import random

import bpy  # bpy первым: он регистрирует bmesh и mathutils
import bmesh
from mathutils import Vector, Matrix

C = bpy.context


# ---------------------------------------------------------------- сцена и цвета
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.unit_settings.system = 'METRIC'
    random.seed(7)


def hexcol(h):
    """sRGB hex → линейный RGB (Blender работает в линейном пространстве)."""
    h = h.lstrip('#')
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return (*out, 1.0)


def mat(name, color, rough=0.45):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = hexcol(color)
    b.inputs['Roughness'].default_value = rough
    return m


def mat_proc(name, stops, driver='noise', scale=6.0, detail=4.0, rough=0.5, cavity=None):
    """Процедурный материал: ColorRamp по шуму/волне/вороному (+ затемнение впадин через pointiness).
    stops: [(позиция, '#hex'), ...]. cavity: '#hex' цвет для впадин — даёт «вылепленный» объём."""
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    bsdf = N['Principled BSDF']
    bsdf.inputs['Roughness'].default_value = rough
    tc = N.new('ShaderNodeTexCoord')
    if driver == 'voronoi':
        tex = N.new('ShaderNodeTexVoronoi')
        tex.feature = 'DISTANCE_TO_EDGE'
        out = tex.outputs['Distance']
    elif driver == 'wave':
        tex = N.new('ShaderNodeTexWave')
        tex.inputs['Distortion'].default_value = 3.0
        tex.inputs['Detail'].default_value = detail
        out = tex.outputs['Fac']
    else:
        tex = N.new('ShaderNodeTexNoise')
        tex.inputs['Detail'].default_value = detail
        out = tex.outputs['Fac']
    tex.inputs['Scale'].default_value = scale
    L.new(tc.outputs['Object'], tex.inputs['Vector'])
    ramp = N.new('ShaderNodeValToRGB')
    els = ramp.color_ramp.elements
    els[0].position, els[0].color = stops[0][0], hexcol(stops[0][1])
    els[1].position, els[1].color = stops[-1][0], hexcol(stops[-1][1])
    for pos, col in stops[1:-1]:
        e = els.new(pos)
        e.color = hexcol(col)
    L.new(out, ramp.inputs['Fac'])
    color_out = ramp.outputs['Color']
    if cavity:
        geo = N.new('ShaderNodeNewGeometry')
        cr = N.new('ShaderNodeValToRGB')
        cr.color_ramp.elements[0].position = 0.42
        cr.color_ramp.elements[1].position = 0.53
        L.new(geo.outputs['Pointiness'], cr.inputs['Fac'])
        mix = N.new('ShaderNodeMix')
        mix.data_type = 'RGBA'
        mix.inputs['B'].default_value = hexcol(cavity)
        L.new(cr.outputs['Color'], mix.inputs['Factor'])
        inv = N.new('ShaderNodeInvert')
        L.new(cr.outputs['Color'], inv.inputs['Color'])
        L.new(inv.outputs['Color'], mix.inputs['Factor'])
        L.new(color_out, mix.inputs['A'])
        color_out = mix.outputs['Result']
    L.new(color_out, bsdf.inputs['Base Color'])
    return m


# ---------------------------------------------------------------- примитивы
def _new(o, material, name=None):
    if material:
        o.data.materials.append(material)
    if name:
        o.name = name
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    return o


def sphere(loc, scale, material, seg=24, rings=12, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=rings, location=loc, rotation=rot)
    o = C.active_object
    o.scale = scale if isinstance(scale, (tuple, list)) else (scale,) * 3
    return _new(o, material)


def ico(loc, r, material, subdiv=3):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdiv, radius=r, location=loc)
    return _new(C.active_object, material)


def cyl(loc, r, depth, material, verts=24, rot=(0, 0, 0), r2=None):
    if r2 is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc, rotation=rot)
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r, radius2=r2, depth=depth, location=loc, rotation=rot)
    return _new(C.active_object, material)


def torus(loc, R, r, material, rot=(0, 0, 0), maj=32, mnr=12):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=maj, minor_segments=mnr,
                                     location=loc, rotation=rot)
    return _new(C.active_object, material)


def box(loc, size, material, bevel=0.03, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = C.active_object
    o.scale = size
    _new(o, material)
    if bevel:
        mod = o.modifiers.new('bevel', 'BEVEL')
        mod.width, mod.segments = bevel, 3
        apply_mods(o)
    return o


def tube(p1, p2, r, material, verts=12, r2=None):
    """Цилиндр между двумя точками (конечности, антенны)."""
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    rot = d.to_track_quat('Z', 'Y').to_euler()
    return cyl((p1 + p2) / 2, r, d.length, material, verts=verts, rot=rot, r2=r2)


def limb(p1, p2, r, material, r2=None):
    """Конечность-капсула: труба + сферы на концах."""
    r2 = r if r2 is None else r2
    return [tube(p1, p2, r, material, 16, r2), sphere(p1, r, material, 16, 8), sphere(p2, r2, material, 16, 8)]


def star(loc, r_out, r_in, depth, material, rot=(math.pi / 2, 0, 0), points=5):
    me = bpy.data.meshes.new('star')
    bm = bmesh.new()
    pts = []
    for i in range(points * 2):
        a = math.pi / 2 + i * math.pi / points
        rr = r_out if i % 2 == 0 else r_in
        pts.append((rr * math.cos(a), rr * math.sin(a)))
    front = [bm.verts.new((x, y, depth / 2)) for x, y in pts]
    back = [bm.verts.new((x, y, -depth / 2)) for x, y in pts]
    cf, cb = bm.verts.new((0, 0, depth)), bm.verts.new((0, 0, -depth))
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((cf, front[i], front[j]))
        bm.faces.new((cb, back[j], back[i]))
        bm.faces.new((front[i], back[i], back[j], front[j]))
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new('star', me)
    C.collection.objects.link(o)
    o.location, o.rotation_euler = loc, rot
    select(o)
    return _new(o, material)


# ---------------------------------------------------------------- операции
def select(*objs):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    C.view_layer.objects.active = objs[0]


def apply_mods(o):
    select(o)
    for m in list(o.modifiers):
        bpy.ops.object.modifier_apply(modifier=m.name)


def join(objs, name=None):
    objs = [o for o in objs if o]
    select(*objs)
    bpy.ops.object.join()
    o = C.active_object
    if name:
        o.name = name
    return o


def tris(o):
    return sum(len(p.vertices) - 2 for p in o.data.polygons)


def decimate(o, target):
    t = tris(o)
    if t > target:
        mod = o.modifiers.new('dec', 'DECIMATE')
        mod.ratio = target / t
        apply_mods(o)
    return o


def blob(objs, material, voxel=0.012, target=6000, smooth=6, name='blob'):
    """Сплавить примитивы в одну гладкую «вылепленную» форму и ужать до target треугольников."""
    o = join(objs, name)
    o.data.materials.clear()
    o.data.materials.append(material)
    r = o.modifiers.new('remesh', 'REMESH')
    r.mode, r.voxel_size, r.adaptivity = 'VOXEL', voxel, 0
    s = o.modifiers.new('smooth', 'SMOOTH')
    s.factor, s.iterations = 0.6, smooth
    apply_mods(o)
    decimate(o, target)
    bpy.ops.object.shade_smooth()
    return o


def displace_noise(o, strength=0.02, scale=0.15):
    tex = bpy.data.textures.new('lumps', 'CLOUDS')
    tex.noise_scale = scale
    d = o.modifiers.new('disp', 'DISPLACE')
    d.texture, d.strength = tex, strength
    apply_mods(o)
    return o


def surface(o, origin, direction):
    """Точка и нормаль на поверхности o по лучу — для посадки глаз, рта, посыпки."""
    inv = o.matrix_world.inverted()
    ok, loc, nrm, _ = o.ray_cast(inv @ Vector(origin), (inv.to_3x3() @ Vector(direction)).normalized())
    if not ok:
        return None, None
    return o.matrix_world @ loc, (o.matrix_world.to_3x3() @ nrm).normalized()


# ---------------------------------------------------------------- лицо и тело
M_WHITE = lambda: mat('eye_white', '#FFFFFF', 0.2)
M_BLACK = lambda: mat('pupil', '#15131F', 0.15)


def eyes(body, center_z, spacing, r, look=(0, 0), center_x=0.0, pupil_color='#15131F', brows=None, lids=0.0):
    """Большие мультяшные глаза на поверхности body. look — сдвиг зрачка (x, z) в долях радиуса.
    brows — цвет бровей (или None). lids — опущенное веко (хитрый/сонный вид), 0..1."""
    parts = []
    for side in (-1, 1):
        x = center_x + side * spacing
        p, n = surface(body, (x, -3, center_z), (0, 1, 0))
        if p is None:
            continue
        c = p + n * (r * 0.35)
        w = sphere(c, (r, r * 0.75, r * 1.12), M_WHITE(), 24, 12)
        parts.append(w)
        pc = c + n * (r * 0.58) + Vector((look[0] * r * 0.35, 0, look[1] * r * 0.35))
        parts.append(sphere(pc, (r * 0.55, r * 0.3, r * 0.62), mat('pupil_' + pupil_color, pupil_color, 0.1), 20, 10))
        parts.append(sphere(pc + n * r * 0.22 + Vector((-0.25 * r, 0, 0.3 * r)), r * 0.16, M_WHITE(), 10, 6))
        if lids:
            parts.append(sphere(c + Vector((0, -r * 0.05, r * (1.1 - lids))), (r * 1.08, r * 0.8, r * 0.5),
                                mat('lid', '#2B2140', 0.5), 20, 10))
        if brows:
            b0 = c + Vector((-side * r * 0.9, -r * 0.25, r * 1.45))
            b1 = c + Vector((side * r * 0.9, -r * 0.25, r * 1.25))
            parts += limb(b0, b1, r * 0.16, mat('brow_' + brows, brows, 0.6))
    return parts


def mouth(body, z, w, h, x=0.0, tongue=True, teeth=False, color='#5A1027'):
    p, n = surface(body, (x, -3, z), (0, 1, 0))
    if p is None:
        return []
    c = p + n * 0.004
    parts = [sphere(c, (w, h * 0.6, h), mat('mouth_' + color, color, 0.4), 24, 12)]
    if tongue:
        parts.append(sphere(c + n * h * 0.3 + Vector((0, 0, -h * 0.45)), (w * 0.55, h * 0.4, h * 0.45),
                            mat('tongue', '#FF6F91', 0.35), 16, 8))
    if teeth:
        for s in (-1, 1):
            parts.append(box(c + n * h * 0.35 + Vector((s * w * 0.28, 0, h * 0.7)), (w * 0.28, h * 0.25, h * 0.4),
                             M_WHITE(), bevel=0.004))
    return parts


def cheeks(body, z, spacing, r, color='#FF7FA8'):
    parts = []
    for s in (-1, 1):
        p, n = surface(body, (s * spacing, -3, z), (0, 1, 0))
        if p is not None:
            parts.append(sphere(p + n * 0.002, (r, r * 0.25, r * 0.65), mat('cheek', color, 0.6), 16, 8))
    return parts


def sneaker(loc, side, main='#FFFFFF', accent='#FF4D4D', sole='#3A3A4A', size=1.0):
    """Кроссовок: слепленный верх + подошва + полоска. loc — точка щиколотки."""
    x, y, z = loc
    s = size
    up = [sphere((x, y - 0.05 * s, z - 0.02 * s), (0.075 * s, 0.13 * s, 0.065 * s), None),
          sphere((x, y + 0.03 * s, z + 0.01 * s), (0.07 * s, 0.08 * s, 0.075 * s), None)]
    upper = blob(up, mat('shoe_' + main, main, 0.5), voxel=0.008 * s, target=900, name='shoe')
    sol = box((x, y - 0.04 * s, z - 0.062 * s), (0.15 * s, 0.25 * s, 0.03 * s), mat('sole_' + sole, sole, 0.7),
              bevel=0.014 * s)
    stripe = sphere((x + side * 0.068 * s, y - 0.02 * s, z - 0.01 * s), (0.012 * s, 0.07 * s, 0.03 * s),
                    mat('shoe_acc_' + accent, accent, 0.4), 12, 6)
    lace = box((x, y - 0.09 * s, z + 0.035 * s), (0.07 * s, 0.05 * s, 0.015 * s), mat('shoe_acc_' + accent, accent),
               bevel=0.005 * s)
    return [upper, sol, stripe, lace]


def legs(hip_z, spacing, foot_z, color, shoe=('#FFFFFF', '#FF4D4D', '#3A3A4A'), r=0.045, hip_y=0.0):
    parts = []
    for s in (-1, 1):
        parts += limb((s * spacing, hip_y, hip_z), (s * spacing, 0.0, foot_z), r, mat('limb_' + color, color, 0.5))
        parts += sneaker((s * spacing, 0.0, foot_z), s, *shoe)
    return parts


def arm(shoulder, hand, color, glove=None, r=0.035, wave=False):
    m = mat('limb_' + color, color, 0.5)
    g = mat('glove_' + glove, glove, 0.45) if glove else m
    parts = limb(shoulder, hand, r, m, r * 0.9)
    h = Vector(hand)
    parts.append(sphere(h, r * 2.0, g, 16, 10))
    side = 1 if h.x > 0 else -1
    parts.append(sphere(h + Vector((-side * r * 1.1, -r * 1.3, r * 1.1 if wave else r * 0.3)), (r * 0.7, r * 0.7, r * 1.0), g,
                        12, 6))
    return parts


def sprinkles(body, count, colors, zmin, zmax, length=0.035, r=0.008, front_only=True):
    parts = []
    mats = [mat('spr_' + c, c, 0.3) for c in colors]
    tries = 0
    while len(parts) < count and tries < count * 20:
        tries += 1
        a = random.uniform(-math.pi * 0.95, math.pi * 0.95) if front_only else random.uniform(-math.pi, math.pi)
        z = random.uniform(zmin, zmax)
        d = Vector((math.sin(a), -math.cos(a), 0))
        p, n = surface(body, Vector((0, 0, z)) + d * 3, -d)
        if p is None or n.y > 0.3 and front_only:
            continue
        if any((p - q.location).length < length * 1.1 for q in parts):
            continue
        t = n.orthogonal().normalized()
        t.rotate(Matrix.Rotation(random.uniform(0, math.pi), 3, n))
        o = tube(p - t * length / 2 + n * r * 0.3, p + t * length / 2 + n * r * 0.3, r, random.choice(mats), verts=6)
        o.location = o.location  # keep
        parts.append(o)
    return parts


# ---------------------------------------------------------------- финализация, запекание, экспорт
def finalize(parts, name, max_tris=15000):
    o = join(parts, name)
    select(o)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    print(f'{name}: {tris(o)} tris до оптимизации')
    decimate(o, max_tris)
    # пивот — центр между ступнями на полу
    bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
    minz = min(v.z for v in bb)
    cx = (min(v.x for v in bb) + max(v.x for v in bb)) / 2
    cy = (min(v.y for v in bb) + max(v.y for v in bb)) / 2
    o.data.transform(Matrix.Translation((-cx, -cy, -minz)))
    o.location = (0, 0, 0)
    select(o)
    bpy.ops.object.shade_smooth()
    return o


def bake(o, out_dir, res=2048):
    """Все процедурные материалы → одна текстура BaseColor (один материал = один draw call в UEFN)."""
    select(o)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.004)
    bpy.ops.object.mode_set(mode='OBJECT')
    img = bpy.data.images.new(o.name + '_BaseColor', res, res)
    for m in o.data.materials:
        node = m.node_tree.nodes.new('ShaderNodeTexImage')
        node.image = img
        m.node_tree.nodes.active = node
    sc = bpy.context.scene
    sc.cycles.samples = 8
    sc.render.bake.margin = 12
    sc.render.bake.use_pass_direct = False
    sc.render.bake.use_pass_indirect = False
    sc.render.bake.use_pass_color = True
    bpy.ops.object.bake(type='DIFFUSE')
    path = os.path.join(out_dir, f'T_{o.name}_BaseColor.png')
    img.filepath_raw = path
    img.file_format = 'PNG'
    img.save()
    m = bpy.data.materials.new('M_' + o.name)
    m.use_nodes = True
    tex = m.node_tree.nodes.new('ShaderNodeTexImage')
    tex.image = img
    bsdf = m.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Roughness'].default_value = 0.5
    m.node_tree.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    o.data.materials.clear()
    o.data.materials.append(m)
    for p in o.data.polygons:
        p.material_index = 0
    return path


def export_fbx(o, out_dir):
    select(o)
    path = os.path.join(out_dir, f'SM_{o.name}.fbx')
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={'MESH'},
                             apply_unit_scale=True, apply_scale_options='FBX_SCALE_UNITS',
                             mesh_smooth_type='FACE', use_mesh_modifiers=True, path_mode='STRIP',
                             bake_anim=False)
    return path


def render_views(o, out_dir, angles=(0, 35, 145, 270), res=640, bg='#1E2548'):
    sc = bpy.context.scene
    sc.render.resolution_x = sc.render.resolution_y = res
    sc.cycles.samples = 48
    sc.cycles.use_denoising = True
    sc.view_settings.view_transform = 'Standard'
    world = bpy.data.worlds.new('w')
    sc.world = world
    world.use_nodes = True
    world.node_tree.nodes['Background'].inputs['Color'].default_value = hexcol(bg)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.6
    bpy.ops.mesh.primitive_circle_add(vertices=64, radius=3, fill_type='NGON', location=(0, 0, 0))
    ground = C.active_object
    ground.data.materials.append(mat('ground', '#2A3263', 0.8))
    bb = [Vector(c) for c in o.bound_box]
    h = max(v.z for v in bb)
    w = max(max(v.x for v in bb) - min(v.x for v in bb), h)
    for name, loc, energy, size in (('key', (-2.2, -2.8, 3.2), 420, 2.5), ('fill', (2.8, -1.8, 1.4), 140, 3),
                                    ('rim', (0.5, 3.0, 2.8), 450, 2)):
        light = bpy.data.lights.new(name, 'AREA')
        light.energy, light.size = energy, size
        lo = bpy.data.objects.new(name, light)
        sc.collection.objects.link(lo)
        lo.location = loc
        lo.rotation_euler = (Vector((0, 0, h / 2)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.data.lens = 50
    dist = max(w, h) * 2.3
    target = Vector((0, 0, h * 0.48))
    files = []
    for i, a in enumerate(angles):
        ang = math.radians(a)
        cam.location = target + Vector((math.sin(ang) * dist, -math.cos(ang) * dist, h * 0.45))
        cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
        f = os.path.join(out_dir, f'_view{i}.png')
        sc.render.filepath = f
        bpy.ops.render.render(write_still=True)
        files.append(f)
    return files
