"""Пропсы «Брейнрот Лаборатории»: капсулы, постаменты вариантов, инкубатор, конвейер, портал, станции хаба, декор.

    python models/lab_props/tools/build_props.py            # все пропсы + пакет LabProps_UEFN.zip
    python models/lab_props/tools/build_props.py Incubator  # один
Нужен Python 3.11 с bpy 4.2 (pip install bpy==4.2.0 pillow numpy).
Каждый проп: одна текстура BaseColor (всё запекается), пивот — центр основания, лицом по +X, сантиметры,
коллизия UCX внутри FBX. Детали кит-а (примитивы, запекание, экспорт) — models/brainrots/tools/kit.py.
"""
import json
import math
import os
import shutil
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, os.path.abspath(os.path.join(ROOT, '..', 'brainrots', 'tools')))
import kit  # noqa: E402
import bmesh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from kit import box, cyl, mat, mat_proc, sphere, star, torus, tube  # noqa: E402

TEX = 1024
HULL_TRIS = 80

RARITY = {  # цвет корпуса капсулы по редкости
    'Common': ('#E9EDF5', '#9AA3B5'),
    'Rare': ('#4FA8FF', '#1D5FB8'),
    'Epic': ('#B26BFF', '#6A2BC2'),
    'Legendary': ('#FFC83D', '#D98A00'),
    'Mythic': ('#FF4F7B', '#B0123F'),
    'Iconic': ('#39F2E0', '#0E9E92'),
}
VARIANTS = ['Base', 'Gold', 'Diamond', 'Rainbow', 'Lava', 'Viral', 'Cosmic']


def variant_mat(v):
    """Материал верха постамента по варианту брейнрота."""
    if v == 'Base':
        return mat('pd_base', '#E6E8EF', 0.5)
    if v == 'Gold':
        return mat_proc('pd_gold', [(0.0, '#B8860B'), (0.5, '#FFD54A'), (1.0, '#FFF1A8')], 'noise', 3, 2, 0.25)
    if v == 'Diamond':
        return mat_proc('pd_diamond', [(0.0, '#7FE7FF'), (0.5, '#D8FBFF'), (1.0, '#FFFFFF')], 'voronoi', 5, 2, 0.1)
    if v == 'Rainbow':
        return mat_proc('pd_rainbow', [(0.0, '#FF3B3B'), (0.2, '#FF9F1C'), (0.4, '#FFE53B'), (0.6, '#3BFF6E'),
                                       (0.8, '#3B8BFF'), (1.0, '#B23BFF')], 'wave', 2, 1, 0.35)
    if v == 'Lava':
        return mat_proc('pd_lava', [(0.0, '#1A0A05'), (0.55, '#2B120A'), (0.62, '#FF5A00'), (1.0, '#FFD200')],
                        'voronoi', 4, 2, 0.6)
    if v == 'Viral':
        return mat_proc('pd_viral', [(0.0, '#39FF14'), (0.5, '#00E5A8'), (1.0, '#FF2BD6')], 'noise', 4, 3, 0.3)
    return mat_proc('pd_cosmic', [(0.0, '#0B0620'), (0.8, '#2A0F5C'), (0.92, '#7A4DFF'), (1.0, '#FFFFFF')],
                    'noise', 25, 1, 0.4)


# ---------------------------------------------------------------- лаборатория
def capsule(rarity):
    shell, band = RARITY[rarity]
    m_shell, m_band = mat('cap_' + rarity, shell, 0.15), mat('band_' + rarity, band, 0.35)
    m_metal = mat('metal', '#C9CED8', 0.3)
    p = [cyl((0, 0, 0.36), 0.2, 0.36, m_shell, 32), sphere((0, 0, 0.54), (0.2, 0.2, 0.16), m_shell, 32, 12),
         sphere((0, 0, 0.18), (0.2, 0.2, 0.16), m_shell, 32, 12),
         torus((0, 0, 0.26), 0.205, 0.025, m_band), torus((0, 0, 0.46), 0.205, 0.025, m_band),
         cyl((0, 0, 0.06), 0.16, 0.12, m_metal, 24), cyl((0, 0, 0.72), 0.03, 0.12, m_metal, 12),
         sphere((0, 0, 0.8), 0.045, m_band, 16, 8)]
    # «?» из точки и дуги на лицевой стороне
    m_q = mat('q_' + rarity, '#FFFFFF', 0.2)
    p += [sphere((0, -0.2, 0.3), 0.03, m_q, 12, 6)]
    for i in range(7):
        a = math.pi * (1.1 - i * 0.22)
        p.append(sphere((0.07 * math.cos(a), -0.195, 0.44 + 0.07 * math.sin(a)), 0.026, m_q, 10, 5))
    return p


def pedestal(v):
    m_top = variant_mat(v)
    m_side = mat('pd_side', '#2B2F45', 0.5)
    m_trim = mat('pd_trim', '#D9DEE8', 0.3)
    return [cyl((0, 0, 0.12), 0.62, 0.24, m_side, 48), cyl((0, 0, 0.28), 0.58, 0.08, m_top, 48),
            torus((0, 0, 0.245), 0.6, 0.03, m_trim, maj=48), cyl((0, 0, 0.01), 0.66, 0.02, m_side, 48)]


def incubator():
    m_base, m_glass = mat('inc_base', '#3A4060', 0.4), mat('inc_glass', '#BFF6FF', 0.05)
    m_pipe, m_lamp = mat('inc_pipe', '#C9CED8', 0.3), mat('inc_lamp', '#7CFF6B', 0.2)
    m_panel = mat('inc_panel', '#1B1F33', 0.4)
    p = [cyl((0, 0, 0.2), 0.75, 0.4, m_base, 40), torus((0, 0, 0.4), 0.72, 0.05, m_pipe, maj=40),
         cyl((0, 0, 1.05), 0.6, 1.3, m_glass, 40), sphere((0, 0, 1.7), (0.6, 0.6, 0.35), m_glass, 40, 14),
         cyl((0, 0, 2.02), 0.25, 0.12, m_base, 24), sphere((0, 0, 2.14), 0.13, m_lamp, 16, 8)]
    for a in range(4):
        ang = math.pi / 4 + a * math.pi / 2
        x, y = 0.66 * math.cos(ang), 0.66 * math.sin(ang)
        p.append(tube((x, y, 0.4), (x * 0.92, y * 0.92, 1.85), 0.045, m_pipe))
    p += [box((0, -0.82, 0.55), (0.5, 0.12, 0.35), m_panel, 0.02),
          sphere((-0.12, -0.89, 0.6), 0.05, mat('btn_r', '#FF4F4F', 0.3), 12, 6),
          sphere((0.12, -0.89, 0.6), 0.05, m_lamp, 12, 6)]
    return p


def conveyor():
    m_frame, m_carpet = mat('cv_frame', '#3A4060', 0.4), mat('cv_carpet', '#C8102E', 0.8)
    m_gold, m_roll = mat('cv_gold', '#FFC83D', 0.3), mat('cv_roll', '#9AA3B5', 0.3)
    p = [box((0, 0, 0.3), (3.0, 1.4, 0.3), m_frame, 0.04), box((0, 0, 0.47), (3.0, 1.1, 0.04), m_carpet, 0.01),
         box((0, 0.62, 0.52), (3.0, 0.08, 0.1), m_gold, 0.02), box((0, -0.62, 0.52), (3.0, 0.08, 0.1), m_gold, 0.02)]
    for i in range(6):
        x = -1.25 + i * 0.5
        p.append(cyl((x, 0, 0.2), 0.08, 1.3, m_roll, 16, rot=(math.pi / 2, 0, 0)))
    for x in (-1.3, 1.3):
        for y in (-0.55, 0.55):
            p.append(box((x, y, 0.08), (0.15, 0.15, 0.16), m_frame, 0.02))
    return p


def portal():
    m_stone, m_trim = mat('pt_stone', '#E8D9B5', 0.7), mat('pt_trim', '#C8102E', 0.5)
    m_swirl = mat_proc('pt_swirl', [(0.0, '#2BFF88'), (0.35, '#7A2BFF'), (0.7, '#FF2BD6'), (1.0, '#2BFF88')],
                       'wave', 0.35, 3, 0.2)
    p = [box((-2.1, 0, 2.0), (0.8, 1.0, 4.0), m_stone, 0.06), box((2.1, 0, 2.0), (0.8, 1.0, 4.0), m_stone, 0.06),
         torus((0, 0, 4.0), 2.1, 0.42, m_stone, rot=(math.pi / 2, 0, 0), maj=48),
         torus((0, -0.45, 4.0), 2.1, 0.08, m_trim, rot=(math.pi / 2, 0, 0), maj=48),
         cyl((0, 0, 3.4), 1.75, 0.2, m_swirl, 48, rot=(math.pi / 2, 0, 0)),
         box((0, 0, 0.1), (5.4, 1.4, 0.2), m_stone, 0.04)]
    return p


def fusion_table():
    m_wood, m_metal = mat('ft_wood', '#6B4226', 0.6), mat('ft_metal', '#C9CED8', 0.3)
    m_glass, m_goo = mat('ft_glass', '#D8FBFF', 0.05), mat('ft_goo', '#7CFF6B', 0.2)
    p = [box((0, 0, 0.9), (3.2, 1.4, 0.12), m_wood, 0.03)]
    for x in (-1.45, 1.45):
        for y in (-0.55, 0.55):
            p.append(box((x, y, 0.42), (0.12, 0.12, 0.84), m_metal, 0.02))
    for x in (-1.0, 0.0, 1.0):
        p += [cyl((x, -0.25, 1.02), 0.32, 0.12, m_metal, 32), cyl((x, -0.25, 1.06), 0.27, 0.06, m_goo, 32)]
    p += [cyl((0, 0.35, 1.8), 0.35, 1.5, m_glass, 32), cyl((0, 0.35, 1.5), 0.3, 0.8, m_goo, 32),
          cyl((0, 0.35, 2.6), 0.4, 0.12, m_metal, 32), cyl((0, 0.35, 0.98), 0.4, 0.08, m_metal, 32)]
    for x in (-1.0, 1.0):
        p.append(tube((x, -0.25, 1.1), (x * 0.35, 0.35, 2.4), 0.04, m_metal))
    return p


def meme_machine():
    m_body, m_screen = mat('mm_body', '#FF4F7B', 0.35), mat('mm_screen', '#1B1F33', 0.2)
    m_btn, m_gold = mat('mm_btn', '#FFC83D', 0.3), mat('mm_gold', '#FFE58A', 0.3)
    p = [box((0, 0, 1.05), (1.3, 0.9, 2.1), m_body, 0.08), box((0, -0.46, 1.45), (0.95, 0.04, 0.7), m_screen, 0.02),
         sphere((0, -0.5, 0.75), (0.28, 0.12, 0.28), m_btn, 32, 12), box((0, 0, 2.2), (1.4, 1.0, 0.2), m_gold, 0.05),
         star((0, -0.5, 2.55), 0.35, 0.16, 0.12, m_btn)]
    return p


def tour_bus():
    m_body, m_win = mat('bus_body', '#FFC83D', 0.4), mat('bus_win', '#9FE3FF', 0.1)
    m_tire, m_stripe = mat('bus_tire', '#1B1B22', 0.8), mat('bus_stripe', '#C8102E', 0.4)
    p = [box((0, 0, 1.45), (5.6, 2.3, 2.3), m_body, 0.18), box((0, 0, 1.15), (5.64, 2.34, 0.18), m_stripe, 0.03)]
    for i in range(5):
        p.append(box((-2.0 + i * 0.95, -1.16, 1.9), (0.75, 0.04, 0.7), m_win, 0.02))
        p.append(box((-2.0 + i * 0.95, 1.16, 1.9), (0.75, 0.04, 0.7), m_win, 0.02))
    p.append(box((2.81, 0, 1.9), (0.04, 1.9, 0.8), m_win, 0.02))
    for x in (-1.8, 1.8):
        for y in (-1.1, 1.1):
            p.append(cyl((x, y, 0.45), 0.45, 0.35, m_tire, 24, rot=(math.pi / 2, 0, 0)))
    p.append(box((0, 0, 2.75), (3.0, 1.6, 0.3), m_stripe, 0.05))
    return p


def pinata():
    m = mat_proc('pn_stripes', [(0.0, '#FF4F7B'), (0.25, '#FFC83D'), (0.5, '#39F2E0'), (0.75, '#B26BFF'),
                                 (1.0, '#FF4F7B')], 'wave', 4, 1, 0.6)
    p = [sphere((0, 0, 1.2), 0.55, m, 32, 16)]
    for i in range(6):
        a = i * math.pi / 3
        d = Vector((math.cos(a), 0.0, math.sin(a)))
        p.append(tube((0, 0, 1.2), tuple(Vector((0, 0, 1.2)) + d * 1.0), 0.28, m, 16, r2=0.02))
    p.append(tube((0, 0, 1.75), (0, 0, 2.6), 0.02, mat('rope', '#E8D9B5', 0.8)))
    return p


def hype_tower():
    m_col, m_ring = mat('ht_col', '#2B2F45', 0.4), mat('ht_ring', '#39F2E0', 0.2)
    m_bolt = mat('ht_bolt', '#FFC83D', 0.3)
    p = [cyl((0, 0, 0.3), 1.2, 0.6, m_col, 40), cyl((0, 0, 4.0), 0.55, 7.0, m_col, 32)]
    for i in range(10):
        p.append(torus((0, 0, 1.0 + i * 0.65), 0.6, 0.06, m_ring, maj=32))
    p += [sphere((0, 0, 7.8), 0.6, m_ring, 32, 14), star((0, 0, 8.9), 0.8, 0.35, 0.2, m_bolt, points=4)]
    return p


def totem():
    m_log, m_ring = mat_proc('tt_log', [(0.0, '#6B4226'), (0.6, '#8B5A33'), (1.0, '#A8743F')], 'wave', 6, 3, 0.8), \
        mat('tt_ring', '#3B2413', 0.8)
    p = [cyl((0, 0, 1.75), 0.55, 3.5, m_log, 32), cyl((0, 0, 3.55), 0.5, 0.1, m_ring, 32)]
    m_eye, m_pupil = mat('tt_eye', '#FFFFFF', 0.3), mat('tt_pupil', '#15131F', 0.2)
    for z in (1.0, 2.6):
        for s in (-1, 1):
            p += [sphere((s * 0.2, -0.5, z + 0.25), (0.15, 0.08, 0.18), m_eye, 16, 8),
                  sphere((s * 0.2, -0.57, z + 0.25), (0.07, 0.04, 0.09), m_pupil, 12, 6)]
        p.append(box((0, -0.53, z - 0.05), (0.4, 0.06, 0.1), mat('tt_mouth', '#3B2413', 0.8), 0.02))
    p.append(tube((0.55, 0, 1.2), (0.95, -0.2, 2.7), 0.08, mat('tt_bat', '#C89B6D', 0.6), r2=0.14))
    return p


def rebirth_altar():
    m_stone = mat('ra_stone', '#E8E2FF', 0.5)
    m_swirl = mat_proc('ra_swirl', [(0.0, '#7A2BFF'), (0.5, '#FF2BD6'), (1.0, '#39F2E0')], 'wave', 2, 4, 0.2)
    p = [cyl((0, 0, 0.15), 1.4, 0.3, m_stone, 48), cyl((0, 0, 0.33), 1.2, 0.06, m_swirl, 48),
         torus((0, 0, 0.3), 1.35, 0.05, mat('ra_gold', '#FFC83D', 0.3), maj=48)]
    for i in range(4):
        a = i * math.pi / 2 + math.pi / 4
        x, y = 1.2 * math.cos(a), 1.2 * math.sin(a)
        p += [cyl((x, y, 0.9), 0.1, 1.2, m_stone, 16), sphere((x, y, 1.6), 0.16, m_swirl, 16, 8)]
    return p


def ideal_aura():
    m = mat('aura', '#FFE58A', 0.2)
    p = [torus((0, 0, 1.9), 0.4, 0.05, m, maj=40)]
    for i in range(6):
        a = i * math.pi / 3
        p.append(star((0.75 * math.cos(a), 0.75 * math.sin(a), 0.6 + 0.2 * (i % 3)), 0.1, 0.045, 0.03, m))
    return p


# ---------------------------------------------------------------- декор
def street_lamp():
    m_iron, m_glass = mat('sl_iron', '#1B1B22', 0.5), mat('sl_glass', '#FFE9A8', 0.1)
    return [cyl((0, 0, 0.1), 0.25, 0.2, m_iron, 16), cyl((0, 0, 1.9), 0.06, 3.6, m_iron, 12),
            tube((0, 0, 3.6), (0.5, 0, 3.8), 0.04, m_iron), cyl((0.55, 0, 3.55), 0.18, 0.4, m_glass, 12),
            cyl((0.55, 0, 3.8), 0.25, 0.1, m_iron, 12, r2=0.05)]


def cafe_umbrella():
    m_red, m_white = mat('cu_red', '#C8102E', 0.6), mat('cu_white', '#F4F1EA', 0.6)
    m_wood = mat('cu_wood', '#8B5A33', 0.6)
    p = [cyl((0, 0, 1.3), 0.04, 2.6, m_wood, 12), cyl((0, 0, 2.45), 1.4, 0.5, m_red, 16, r2=0.05),
         cyl((0, 0, 0.75), 0.55, 0.05, m_white, 32), cyl((0, 0, 0.37), 0.05, 0.74, m_wood, 12)]
    for i in range(3):
        a = i * 2 * math.pi / 3
        x, y = 1.0 * math.cos(a), 1.0 * math.sin(a)
        p += [box((x, y, 0.45), (0.45, 0.45, 0.06), m_white, 0.02), box((x, y, 0.22), (0.06, 0.06, 0.44), m_wood, 0.01)]
    return p


def lemon_tree():
    m_pot, m_trunk = mat('lt_pot', '#C8643B', 0.7), mat('lt_trunk', '#6B4226', 0.7)
    m_leaf = mat_proc('lt_leaf', [(0.0, '#2E7D32'), (1.0, '#66BB6A')], 'noise', 8, 3, 0.7)
    m_lemon = mat('lt_lemon', '#FFE53B', 0.4)
    p = [cyl((0, 0, 0.35), 0.45, 0.7, m_pot, 24, r2=0.55), cyl((0, 0, 1.2), 0.07, 1.2, m_trunk, 12),
         sphere((0, 0, 2.0), 0.75, m_leaf, 24, 12)]
    for i in range(8):
        a = i * math.pi / 4
        p.append(sphere((0.62 * math.cos(a), 0.62 * math.sin(a), 1.8 + 0.3 * (i % 2)), (0.09, 0.09, 0.12), m_lemon, 12, 6))
    return p


def cappuccino_fountain():
    m_cup, m_saucer = mat('cf_cup', '#F4F1EA', 0.3), mat('cf_saucer', '#E0DCD2', 0.3)
    m_coffee = mat_proc('cf_foam', [(0.0, '#6F4A2E'), (0.6, '#C8A27A'), (1.0, '#F4E3C8')], 'wave', 1.5, 2, 0.5)
    return [cyl((0, 0, 0.15), 2.6, 0.3, m_saucer, 48), cyl((0, 0, 1.3), 1.9, 2.0, m_cup, 48, r2=1.5),
            cyl((0, 0, 2.28), 1.82, 0.06, m_coffee, 48), torus((2.1, 0, 1.4), 0.55, 0.15, m_cup, rot=(math.pi / 2, 0, 0)),
            sphere((0, 0, 2.6), (0.8, 0.8, 0.35), m_coffee, 32, 12)]


def sign_board():
    m_wood, m_board = mat('sb_wood', '#8B5A33', 0.7), mat('sb_board', '#1B1F33', 0.5)
    return [box((-1.4, 0, 1.2), (0.15, 0.15, 2.4), m_wood, 0.02), box((1.4, 0, 1.2), (0.15, 0.15, 2.4), m_wood, 0.02),
            box((0, 0, 1.8), (2.9, 0.12, 1.2), m_wood, 0.03), box((0, -0.07, 1.8), (2.7, 0.04, 1.0), m_board, 0.01)]


JUNK = {  # мем-мусор: цвет «сияния» кучи по виду
    'Gold': ('#FFD54A', '#B8860B'),
    'Rainbow': ('#FF4FD8', '#3B8BFF'),
    'Lava': ('#FF5A00', '#2B120A'),
}


def junk_pile(kind):
    """Куча мем-мусора: коробки из-под пиццы, банки, мятые листки, сверху светящийся осколок."""
    glow, dark = JUNK[kind]
    m_box, m_can = mat('jp_box', '#C8A27A', 0.8), mat('jp_can', '#9AA3B5', 0.3)
    m_paper, m_glow = mat('jp_paper', '#F4F1EA', 0.7), mat('jp_glow_' + kind, glow, 0.15)
    m_dark = mat('jp_dark_' + kind, dark, 0.5)
    p = [sphere((0, 0, 0.18), (0.7, 0.6, 0.28), m_dark, 24, 10)]
    for i, (x, y, z, r) in enumerate(((-0.3, -0.1, 0.35, 0.3), (0.28, 0.12, 0.33, -0.4), (0.0, 0.25, 0.42, 0.9))):
        p.append(box((x, y, z), (0.42, 0.42, 0.07), m_box, 0.01, rot=(0.2, 0.1, r)))
    for x, y in ((0.35, -0.3), (-0.4, 0.3), (0.1, -0.42)):
        p.append(cyl((x, y, 0.12), 0.07, 0.2, m_can, 12, rot=(1.2, 0, x * 3)))
    for x, y in ((-0.1, -0.35), (0.45, 0.25)):
        p.append(sphere((x, y, 0.2), 0.1, m_paper, 10, 6))
    p += [star((0, 0, 0.72), 0.2, 0.09, 0.08, m_glow, points=5), sphere((0, 0, 0.55), 0.09, m_glow, 12, 6)]
    return p


def like_heart():
    """Табличка «Лайкнуть лабораторию»: сердце на стойке."""
    m_red, m_pole, m_base = mat('lh_red', '#FF4F7B', 0.3), mat('lh_pole', '#C9CED8', 0.3), mat('lh_base', '#3A4060', 0.5)
    p = [cyl((0, 0, 0.05), 0.35, 0.1, m_base, 24), cyl((0, 0, 0.7), 0.04, 1.3, m_pole, 12),
         sphere((-0.17, 0, 1.55), (0.22, 0.1, 0.22), m_red, 20, 10), sphere((0.17, 0, 1.55), (0.22, 0.1, 0.22), m_red, 20, 10),
         cyl((0, 0, 1.36), 0.3, 0.36, m_red, 4, rot=(math.pi, 0, math.pi / 4), r2=0.0)]
    return p


PROPS = {
    'Incubator': (incubator, 9000),
    'ConveyorSegment': (conveyor, 5000),
    'MemePortal': (portal, 9000),
    'FusionTable': (fusion_table, 9000),
    'MemeMachine': (meme_machine, 6000),
    'TourBus': (tour_bus, 6000),
    'Pinata': (pinata, 6000),
    'HypeTower': (hype_tower, 12000),
    'SahurTotem': (totem, 6000),
    'RebirthAltar': (rebirth_altar, 8000),
    'IdealAura': (ideal_aura, 3000),
    'StreetLamp': (street_lamp, 2000),
    'CafeUmbrella': (cafe_umbrella, 4000),
    'LemonTree': (lemon_tree, 6000),
    'CappuccinoFountain': (cappuccino_fountain, 9000),
    'SignBoard': (sign_board, 2000),
}
for _r in RARITY:
    PROPS[f'Capsule_{_r}'] = ((lambda r=_r: capsule(r)), 6000)
for _k in JUNK:
    PROPS[f'JunkPile_{_k}'] = ((lambda k=_k: junk_pile(k)), 4000)
PROPS['LikeHeart'] = (like_heart, 3000)
for _v in VARIANTS:
    PROPS[f'Pedestal_{_v}'] = ((lambda v=_v: pedestal(v)), 4000)


def build(name):
    fn, max_tris = PROPS[name]
    out = os.path.join(ROOT, name)
    os.makedirs(out, exist_ok=True)
    kit.reset()
    obj = kit.finalize(fn(), name, max_tris=max_tris)
    kit.bake(obj, out, res=TEX)
    obj.data.transform(Matrix.Rotation(math.radians(90), 4, 'Z'))  # лицо -Y → +X (как в UEFN)
    dims = obj.dimensions.copy()
    views = kit.render_views(obj, out, angles=(125, 235), res=480)
    ims = [Image.open(f) for f in views]
    w, h = ims[0].size
    sheet = Image.new('RGB', (w * len(ims), h + 44), (20, 24, 50))
    for i, im in enumerate(ims):
        sheet.paste(im, (i * w, 44))
        os.remove(views[i])
    try:
        font = ImageFont.truetype('DejaVuSans-Bold.ttf', 22)
    except OSError:
        font = ImageFont.load_default()
    ImageDraw.Draw(sheet).text((12, 9), f'{name} · {kit.tris(obj)} tris · {dims.z * 100:.0f} см', fill=(255, 255, 255),
                               font=font)
    sheet.save(os.path.join(out, 'preview.png'))
    info = {'name': name, 'tris': kit.tris(obj), 'size_cm': [round(d * 100) for d in dims],
            'fbx': f'SM_{name}.fbx', 'texture': f'T_{name}_BaseColor.png'}
    json.dump(info, open(os.path.join(out, 'info.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    obj.name = obj.data.name = 'SM_' + name
    hull = collision(obj)
    export([obj, hull], os.path.join(out, f'SM_{name}.fbx'), embed=True)
    print('BUILT', info)
    return info


def collision(obj):
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
    bpy.ops.mesh.convex_hull()
    bpy.ops.object.mode_set(mode='OBJECT')
    return hull


def export(objs, path, embed=True):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={'MESH'}, apply_unit_scale=True,
                             apply_scale_options='FBX_SCALE_UNITS', mesh_smooth_type='FACE',
                             path_mode='COPY' if embed else 'STRIP', embed_textures=embed, bake_anim=False,
                             axis_forward='-Z', axis_up='Y')


README = """Пропсы Брейнрот Лаборатории для UEFN — {n} шт.

Импорт: Content Browser → папка LabProps → Import → Meshes/SM_*.fbx (текстуры встроены).
В окне FBX: Static Mesh, Combine Meshes — ВЫКЛ, Auto Generate Collision — ВЫКЛ (UCX внутри).
Сантиметры, пивот — центр основания, лицом по +X.

Для Verse (SpawnProp) каждому мешу нужен Creative Prop: ПКМ по мешу → создать Blueprint-класс
на базе Creative Prop (BuildingProp) — такой ассет попадает в @editable-массивы lab_manager_device.
Кучи мем-мусора (JunkPile_Gold/Rainbow/Lava) ставятся руками в одну точку для каждой кучи
и указываются в lab_junk_device → Piles → Props (Золотой, Радужный, Лавовый).
Порядок массивов: CapsuleProps = Common, Rare, Epic, Legendary, Mythic, Iconic;
PedestalProps = Base, Gold, Diamond, Rainbow, Lava, Viral, Cosmic; AuraProps = IdealAura.

Подробно: docs/brainrot-lab/03-assets.md
"""


def pack(names):
    stage = os.path.join(ROOT, '_pack')
    shutil.rmtree(stage, ignore_errors=True)
    for d in ('Meshes', 'Previews'):
        os.makedirs(os.path.join(stage, d))
    for n in names:
        shutil.copy(os.path.join(ROOT, n, f'SM_{n}.fbx'), os.path.join(stage, 'Meshes'))
        im = Image.open(os.path.join(ROOT, n, 'preview.png')).convert('RGB')
        im.save(os.path.join(stage, 'Previews', n + '.jpg'), quality=85)
    open(os.path.join(stage, 'README_UEFN.txt'), 'w', encoding='utf-8').write(README.format(n=len(names)))
    zpath = os.path.join(ROOT, 'LabProps_UEFN.zip')
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
        for base, _, files in os.walk(stage):
            for fn in files:
                full = os.path.join(base, fn)
                z.write(full, os.path.join('LabProps_UEFN', os.path.relpath(full, stage)))
    shutil.rmtree(stage)
    print('ZIP', zpath, round(os.path.getsize(zpath) / 1e6, 1), 'MB')


if __name__ == '__main__':
    names = [a for a in sys.argv[1:] if not a.startswith('-')] or list(PROPS)
    infos = [build(n) for n in names]
    if len(names) == len(PROPS) or '--pack' in sys.argv:
        pack([n for n in PROPS if os.path.isfile(os.path.join(ROOT, n, 'info.json'))])
