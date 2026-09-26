"""Персонажи-брейнроты Космо Пекарни. Каждая функция строит части и возвращает список объектов.
Лицо смотрит в -Y, ноги на Z=0, рост ~1.0–1.4 м."""
import math

from mathutils import Vector

import kit
from kit import (arm, blob, box, cheeks, cyl, displace_noise, eyes, ico, legs, limb, mat, mat_proc,
                 mouth, sphere, sprinkles, star, surface, torus, tube)


def croissantino():
    """Круассанино Астронавтино — круассан-космонавт с антенной-звездой и реактивным ранцем."""
    zc = 0.58
    crust = mat_proc('croissant_crust', [(0.0, '#9C4F12'), (0.35, '#C8741F'), (0.6, '#E39A38'), (1.0, '#F4C266')],
                     driver='noise', scale=9, detail=8, rough=0.35, cavity='#6B3208')
    segs = []
    n = 7
    for i in range(n):
        a = -1 + 2 * i / (n - 1)
        ang = a * math.radians(62)
        R = 0.4
        x, y = R * math.sin(ang), R * (1 - math.cos(ang)) * 0.7
        z = zc - 0.26 * a * a  # рожки круассана уходят вниз
        s = 0.27 * (1 - 0.72 * a * a) + 0.04
        segs.append(sphere((x, y, z), (s * 0.6, s * 0.9, s * 0.95), None, 24, 12, rot=(0, math.radians(18) * a, ang)))
    # кончики-рожки
    for sd in (-1, 1):
        segs.append(sphere((sd * 0.45, 0.12, zc - 0.33), (0.07, 0.06, 0.06), None, 16, 8))
    body = blob(segs, crust, voxel=0.009, target=8000, smooth=3, name='body')

    suit = '#F2F4FA'
    p = []
    p += eyes(body, zc + 0.07, 0.1, 0.07, look=(0.1, 0.1), brows='#7A3A10')
    p += mouth(body, zc - 0.06, 0.07, 0.045, teeth=True)
    p += cheeks(body, zc - 0.015, 0.17, 0.035)
    # руки в белом скафандре с оранжевыми перчатками
    p += arm((-0.34, 0.05, zc - 0.02), (-0.56, -0.1, zc + 0.2), suit, glove='#FF8A1F', r=0.04, wave=True)
    p += arm((0.34, 0.05, zc - 0.02), (0.52, -0.12, zc - 0.2), suit, glove='#FF8A1F', r=0.04)
    p += legs(zc - 0.12, 0.11, 0.1, suit, shoe=('#F2F4FA', '#FF8A1F', '#4A4F63'), r=0.05)
    # антенна со звездой
    p += limb((0, 0.02, zc + 0.2), (0.03, 0.04, zc + 0.46), 0.012, mat('metal', '#B8C0D6', 0.3))
    p.append(star((0.03, 0.04, zc + 0.52), 0.075, 0.034, 0.03, mat('star', '#FFD23F', 0.25)))
    # реактивный ранец
    pack = mat('jetpack', '#6F7AA6', 0.4)
    p.append(kit.box((0, 0.36, zc + 0.02), (0.3, 0.12, 0.26), pack, bevel=0.035))
    for s in (-1, 1):
        p.append(cyl((s * 0.08, 0.43, zc - 0.08), 0.045, 0.14, mat('nozzle', '#3C4260', 0.3)))
        p.append(cyl((s * 0.08, 0.43, zc - 0.2), 0.04, 0.12, mat('flame_o', '#FF7A1A', 0.6), r2=0.0, rot=(math.pi, 0, 0)))
        p.append(cyl((s * 0.08, 0.43, zc - 0.18), 0.025, 0.08, mat('flame_y', '#FFE45C', 0.6), r2=0.0, rot=(math.pi, 0, 0)))
    p.append(sphere((0, 0.3, zc + 0.02), (0.05, 0.02, 0.05), mat('badge', '#FF4D6D', 0.3), 16, 8))
    return [body] + p


def ponchikello():
    """Пончикелло Бомбардино — пончик-самолёт: пропеллер в дырке, крылья, лётные очки."""
    zc = 0.66
    R, r = 0.3, 0.155
    dough = mat_proc('donut_dough', [(0.0, '#C98A4B'), (0.6, '#E2AE6C'), (1.0, '#F0C98E')],
                     scale=7, detail=5, rough=0.55, cavity='#9A6232')
    ring = kit.torus((0, 0, zc), R, r, None, rot=(math.pi / 2, 0, 0), maj=48, mnr=20)
    body = blob([ring], dough, voxel=0.01, target=5000, name='donut')

    # глазурь: передняя половина тора с волнистым краем-подтёками
    glaze_m = mat_proc('glaze_pink', [(0.0, '#FF5FA2'), (1.0, '#FF8CC0')], scale=3, rough=0.2)
    g = kit.torus((0, 0, zc), R, r * 1.07, glaze_m, rot=(math.pi / 2, 0, 0), maj=64, mnr=24)
    import bmesh as _bm
    bm = _bm.new()
    bm.from_mesh(g.data)
    kill = []
    for v in bm.verts:
        ang = math.atan2(v.co.z - zc, v.co.x)
        edge = 0.02 + 0.035 * math.sin(ang * 9) + 0.015 * math.sin(ang * 23)
        if v.co.y > edge:
            kill.append(v)
    _bm.ops.delete(bm, geom=kill, context='VERTS')
    bm.to_mesh(g.data)
    bm.free()
    sol = g.modifiers.new('solid', 'SOLIDIFY')
    sol.thickness = 0.012
    kit.apply_mods(g)
    kit.select(g)
    import bpy
    bpy.ops.object.shade_smooth()
    p = [g]
    p += sprinkles(g, 45, ['#FFFFFF', '#FFD23F', '#4DD0FF', '#7CFF6B', '#B07CFF'], zc - 0.1, zc + 0.45,
                   length=0.04, r=0.009)
    # лицо на верхней дуге, рот — на нижней
    p += eyes(g, zc + 0.3, 0.1, 0.065, look=(0, -0.1), brows='#5A2D0C')
    p += mouth(g, zc - 0.33, 0.085, 0.05, teeth=False)
    p += cheeks(g, zc + 0.2, 0.2, 0.03, color='#FF3D7F')
    # лётные очки на «лбу»
    frame = mat('goggle_frame', '#7A4A24', 0.5)
    lens = mat('goggle_lens', '#46D6FF', 0.1)
    for s in (-1, 1):
        p.append(kit.torus((s * 0.09, -0.1, zc + 0.43), 0.05, 0.016, frame, rot=(math.radians(70), 0, 0), maj=24, mnr=8))
        p.append(sphere((s * 0.09, -0.105, zc + 0.43), (0.045, 0.015, 0.045), lens, 16, 8, rot=(math.radians(-20), 0, 0)))
    p.append(tube((-0.16, -0.06, zc + 0.43), (0.16, -0.06, zc + 0.43), 0.012, frame))
    # пропеллер в дырке
    red = mat('plane_red', '#E8363D', 0.35)
    white = mat('plane_white', '#F5F5F5', 0.35)
    p.append(cyl((0, -0.06, zc), 0.06, 0.12, red, rot=(math.pi / 2, 0, 0), r2=0.01))
    for k in range(3):
        a = k * 2 * math.pi / 3 + 0.3
        c = Vector((math.cos(a) * 0.1, -0.08, zc + math.sin(a) * 0.1))
        p.append(sphere(c, (0.1, 0.012, 0.028), mat('blade', '#D9DDE8', 0.3), 16, 8, rot=(0, -a, 0)))
    # крылья с белыми кончиками и хвост
    for s in (-1, 1):
        p.append(box((s * 0.68, 0.03, zc), (0.46, 0.28, 0.045), red, bevel=0.018, rot=(0, s * math.radians(-8), 0)))
        p.append(box((s * 0.92, 0.03, zc - 0.035), (0.06, 0.28, 0.05), white, bevel=0.018))
        p.append(star((s * 0.62, -0.085, zc + 0.02), 0.045, 0.02, 0.012, white, rot=(math.pi / 2, 0, 0)))
    p.append(box((0, 0.2, zc + 0.5), (0.03, 0.16, 0.16), red, bevel=0.012, rot=(math.radians(-25), 0, 0)))
    p += legs(zc - 0.4, 0.12, 0.1, '#E2AE6C', shoe=('#E8363D', '#FFFFFF', '#2E2E3A'), r=0.04)
    return [body] + p


def keksolino():
    """Кексолино Метеорино — кекс, в которого врезался метеорит: пылающий камень в креме."""
    wrap_m = mat_proc('cup_wrapper', [(0.0, '#34BFAF'), (1.0, '#7EE8DA')], driver='wave', scale=2, rough=0.5,
                      cavity='#1F7F74')
    import bpy
    # рифлёная бумажная формочка
    bpy.ops.mesh.primitive_cone_add(vertices=64, radius1=0.24, radius2=0.33, depth=0.36, location=(0, 0, 0.5))
    w = kit.C.active_object
    for v in w.data.vertices:
        ang = math.atan2(v.co.y, v.co.x)
        k = 1 + 0.035 * math.cos(ang * 32)
        v.co.x *= k
        v.co.y *= k
    w.data.materials.append(wrap_m)
    bev = w.modifiers.new('bev', 'BEVEL')
    bev.width, bev.segments = 0.02, 2
    kit.apply_mods(w)
    kit.select(w)
    bpy.ops.object.shade_smooth()
    # крем-завиток
    cream = mat_proc('cream_lilac', [(0.0, '#9B6AE8'), (0.5, '#B98AF0'), (1.0, '#D9B8FF')], scale=4,
                     rough=0.3, cavity='#6B3FB8')
    layers = [kit.torus((0, 0, 0.73), 0.27, 0.11, None), kit.torus((0.01, 0, 0.84), 0.2, 0.1, None),
              kit.torus((0.015, 0, 0.94), 0.13, 0.085, None), sphere((0.02, 0, 1.02), (0.09, 0.09, 0.1), None),
              sphere((0, 0, 0.76), (0.28, 0.28, 0.12), None)]
    body = blob(layers, cream, voxel=0.01, target=6000, name='cream')
    p = [w]
    p += eyes(body, 0.8, 0.105, 0.07, look=(0.15, 0.25), brows='#4B2A7A')
    p += mouth(w, 0.6, 0.09, 0.055, teeth=True)
    p += cheeks(body, 0.735, 0.2, 0.032)
    p += sprinkles(body, 25, ['#FFFFFF', '#FFD23F', '#FF5F8F'], 0.8, 1.05, length=0.032, r=0.008)
    # метеорит в макушке + огненный хвост
    rock = ico((0.07, 0.03, 1.12), 0.11, mat_proc('meteor', [(0.0, '#FF6A00'), (0.08, '#FFB21A'), (0.12, '#4B4150'),
                                                          (1.0, '#6E6378')], driver='voronoi', scale=9, rough=0.7),
               subdiv=3)
    displace_noise(rock, 0.035, 0.08)
    p.append(rock)
    # пламя: языки огня вокруг метеорита, отклонённые назад (будто он только что упал)
    center = Vector((0.07, 0.03, 1.12))
    back = Vector((0.15, 0.55, 0.0))
    for k in range(7):
        a = k * 2 * math.pi / 7
        radial = Vector((math.cos(a), math.sin(a) * 0.8, 0))
        root = center + radial * 0.085 + Vector((0, 0, 0.02))
        up = (Vector((0, 0, 1.0)) + back + radial * 0.35).normalized()
        ln = 0.2 + 0.08 * ((k * 3) % 4) / 3
        col = ('#FF5A1F', '#FFB21A', '#FF8A1A')[k % 3]
        puffs = [sphere(root + up * ln * t + radial * 0.02 * math.sin(t * 6), (0.05 * (1 - t) + 0.008), None, 16, 8)
                 for t in (0.0, 0.3, 0.55, 0.78, 1.0)]
        p.append(blob(puffs, mat('fire_' + col, col, 0.6), voxel=0.007, target=500, smooth=4, name='flame'))
    p.append(sphere(center + Vector((0, 0.02, 0.06)), (0.09, 0.09, 0.07), mat('fire_core', '#FFE45C', 0.6), 16, 8))
    p += arm((-0.28, 0.0, 0.58), (-0.5, -0.12, 0.72), '#34BFAF', glove='#FFFFFF', r=0.035, wave=True)
    p += arm((0.28, 0.0, 0.58), (0.45, -0.14, 0.42), '#34BFAF', glove='#FFFFFF', r=0.035)
    p += legs(0.34, 0.1, 0.1, '#34BFAF', shoe=('#9B6AE8', '#FFD23F', '#2E2E3A'), r=0.038)
    return [body] + p


CHARACTERS = {
    'Croissantino_Astronautino': ('Круассанино Астронавтино', croissantino),
    'Ponchikello_Bombardino': ('Пончикелло Бомбардино', ponchikello),
    'Keksolino_Meteorino': ('Кексолино Метеорино', keksolino),
}
