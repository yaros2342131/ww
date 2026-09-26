"""Брейнроты, группа B: животные-предметы и фрукты."""
import math

import numpy as np

from parts import (SIZE, arm, blush, brow, cone, dots, eye3, eye_at, eyes, fin_yz, fy, legs2, legs4, new, nose,
                   poly, smile, teeth, tri, whiskers)
from voxel import shade
from voxel_chars import BLACK, WHITE


def vacca_saturno():
    """La Vacca Saturno Saturnita — корова-планета Сатурн: полосатый шар с кольцом и коровьей головой."""
    v = new(31)
    planet, band1, band2, ring, ring2 = '#E8B86B', '#D69A4A', '#F2D29A', '#C9A7E8', '#9C7AD6'
    cow, spot, muzzle = '#FFFFFF', '#1E1E26', '#FFB3C1'
    cx, cy, cz = 32, 28, 27
    v.ellipsoid(cx, cy, cz, 13, 13, 13, planet)
    v.paint((cx - 14, cy - 14, cz - 14), (cx + 14, cy + 14, cz + 14),
            lambda X, Y, Z: np.sin((Z - cz) * 0.9 + (X - cx) * 0.12) > 0.55, band1)
    v.paint((cx - 14, cy - 14, cz - 14), (cx + 14, cy + 14, cz + 14),
            lambda X, Y, Z: np.sin((Z - cz) * 0.9 + (X - cx) * 0.12) < -0.8, band2)
    v.shape((cx - 24, cy - 24, cz - 9), (cx + 24, cy + 24, cz + 9),
            lambda X, Y, Z: (np.abs(Z - cz - 0.28 * (X - cx)) < 0.9)
            & ((X - cx) ** 2 + (Y - cy) ** 2 >= 16 ** 2) & ((X - cx) ** 2 + (Y - cy) ** 2 <= 23 ** 2), ring)
    v.paint((cx - 24, cy - 24, cz - 9), (cx + 24, cy + 24, cz + 9),
            lambda X, Y, Z: np.abs(np.sqrt((X - cx) ** 2 + (Y - cy) ** 2) - 19.5) < 0.9, ring2)
    legs4(v, [(24, 22), (40, 22), (25, 34), (39, 34)], 17, 2.6, cow, hoof=spot, foot_r=2.8)
    v.ellipsoid(cx, 13, 32, 7, 6, 6.5, cow)
    for sx, sz, r in ((-4, 36, 2.6), (4.5, 30, 2.2)):
        v.paint((cx + sx - r, 0, sz - r), (cx + sx + r, 20, sz + r),
                lambda X, Y, Z, sx=sx, sz=sz, r=r: (X - cx - sx) ** 2 + (Z - sz) ** 2 < r * r, spot)
    v.ellipsoid(cx, 8, 28.5, 5.2, 3, 3.4, muzzle)
    for s in (-1, 1):
        v.ellipsoid(cx + s * 2, 5.2, 28.8, 0.8, 0.5, 1.0, '#A0405A')
        cone(v, (cx + s * 4, 14, 37.5), (cx + s * 7, 15, 41.5), 1.2, '#F5E6C8')
        v.ellipsoid(cx + s * 8, 14, 35, 3, 1.2, 1.6, cow)
    eyes(v, cx, 34.5, 3, r=1.8, look=(0, 0.2))
    poly(v, [(cx, 40, 22), (cx + 2, 44, 16), (cx + 3, 45, 11)], 0.7, 0.6, cow)
    v.ellipsoid(cx + 3, 45.3, 10, 1.4, 1.4, 1.8, spot)
    return v, SIZE


def frigo_camelo():
    """Frigo Camelo — верблюд-холодильник: белый холодильник с ручками и магнитами, горб, длинная шея."""
    v = new(32)
    fridge, handle, camel, camel_d = '#EEF2F6', '#A0A8B4', '#D2A56B', '#A8783E'
    cx = 32
    v.box(22, 42, 18, 32, 12, 40, fridge)
    v.paint((20, 16, 29), (44, 34, 31), lambda X, Y, Z: (Z > 29.2) & (Z < 29.9), '#7A828E')
    for z0, z1 in ((32, 38), (21, 27)):
        v.line((24.5, 16.6, z0), (24.5, 16.6, z1), 0.7, handle)
    for x, z, c in ((34, 35, '#FF5FA2'), (38, 33, '#46D6FF'), (36, 24, '#FFD23F'), (30, 22, '#7CFF6B')):
        v.ellipsoid(x, 17.2, z, 1.2, 0.6, 1.2, c)
    v.ellipsoid(cx, 26, 42, 7, 6, 5, camel)       # горб
    poly(v, [(cx, 22, 40), (cx, 19, 47), (cx, 15, 51)], 3.2, 2.8, camel)
    v.ellipsoid(cx, 11, 52, 4.5, 6, 4, camel)
    v.ellipsoid(cx, 6.5, 51, 3.4, 2.4, 2.8, shade(camel, 0.2))
    for s in (-1, 1):
        v.ellipsoid(cx + s * 1.3, 4.3, 51.5, 0.5, 0.4, 0.6, camel_d)
        v.ellipsoid(cx + s * 4, 13, 55.5, 1.3, 0.9, 1.8, camel)
    eyes(v, cx, 54, 2.4, r=1.5, lid=camel_d, lid_amount=0.45)
    smile(v, cx, 49, 3, 0.6, '#5A3A1A', 0.45)
    legs4(v, [(24.5, 20.5), (39.5, 20.5), (24.5, 30), (39.5, 30)], 13, 1.8, camel, hoof='#3A2A1A', foot_r=2.2)
    poly(v, [(cx, 32.5, 30), (cx + 1, 36, 26), (cx + 1, 37, 22)], 0.6, 0.5, camel)
    return v, SIZE


def tim_cheese():
    """Tim Cheese — мышонок-сыр: треугольный кусок сыра с дырками, серые уши и хвостик."""
    v = new(33)
    cheese, cheese_d, grey, pinkc = '#FFD23F', '#E0A92A', '#9AA0AA', '#FF9EB5'
    cx = 32
    tri(v, (16, 12), (48, 12), (33, 40), 'xz', 17, 31, cheese)
    v.shape((14, 16, 10), (50, 32, 14), lambda X, Y, Z: (X > 16.5 - (Z - 12) * 0) & (X < 47.5) & (Y >= 17) & (Y < 31)
            & (Z >= 12), cheese)
    for x, z, r in ((24, 18, 2.2), (37, 17, 1.8), (30, 25, 1.4), (41, 23, 1.2), (21, 14.5, 1.1), (33, 32, 1.3)):
        v.ellipsoid(x, 16.5, z, r, 1.6, r, None)
        v.ellipsoid(x, 17.8, z, r * 0.9, 0.7, r * 0.9, cheese_d)
    for x, z, r in ((20, 20, 1.5), (44, 16, 1.6), (36, 28, 1.2)):  # дырки сзади и сбоку
        v.ellipsoid(x, 31.5, z, r, 1.5, r, None)
    for s in (-1, 1):
        v.ellipsoid(33 + s * 6, 22, 40.5, 4.5, 1.5, 4.5, grey)
        v.ellipsoid(33 + s * 6, 20.8, 40.5, 3.2, 0.6, 3.2, pinkc)
    eyes(v, 33, 29.5, 3.2, r=1.9)
    nose(v, 33, 26.2, 1.2, pinkc)
    whiskers(v, 33, 26, '#6E6E6E', 0.4, 5)
    v.ellipsoid(33, fy(v, 33, 24) - 0.2, 23.8, 1.4, 0.6, 1.3, WHITE)
    v.line((33, fy(v, 33, 24) - 0.6, 24.5), (33, fy(v, 33, 24) - 0.6, 23), 0.2, grey)
    for s in (-1, 1):
        arm(v, (33 + s * 11, 24, 20), (33 + s * 16, 19, 16), 1.2, grey, hand=pinkc, hand_r=1.6)
        v.line((33 + s * 5, 24, 12), (33 + s * 5, 24, 3), 1.6, grey)
        v.ellipsoid(33 + s * 5, 21.5, 1.4, 2.2, 3.4, 1.4, pinkc)
    poly(v, [(40, 31, 14), (46, 38, 13), (51, 42, 18), (52, 42, 25)], 0.9, 0.6, pinkc)
    return v, SIZE


def svinina():
    """Svinina Bombardino — свинья-бомба: круглый розовый шар с фитилём, пятачок, хвостик-пружинка."""
    v = new(34)
    pig, pig_d, cap, fuse = '#FF9EB5', '#FF7FA0', '#5A5F6E', '#C9A66B'
    cx = 32
    legs4(v, [(25, 19), (39, 19), (25, 31), (39, 31)], 9, 2.6, pig, hoof=pig_d, foot_r=2.6)
    v.ellipsoid(cx, 25, 22, 14, 14, 14, pig)
    v.cyl_z(cx, 25, 34, 38, 4, 4, cap)
    v.ellipsoid(cx, 25, 38, 4, 4, 1, shade(cap, 0.15))
    poly(v, [(cx, 25, 38), (cx + 2, 26, 42), (cx + 4, 25, 45)], 0.8, 0.7, fuse)
    v.ellipsoid(cx + 4.3, 25, 46, 1.6, 1.6, 1.6, '#FF7A1A')
    v.ellipsoid(cx + 4.3, 24.5, 46.6, 0.9, 0.9, 0.9, '#FFE45C')
    for a in range(6):
        ang = a * math.pi / 3
        v.line((cx + 4.3, 25, 46), (cx + 4.3 + math.cos(ang) * 3, 24.5, 46 + math.sin(ang) * 3), 0.3, '#FFD23F')
    v.ellipsoid(cx, 11.5, 20, 4.8, 2.6, 3.6, pig_d)
    for s in (-1, 1):
        v.ellipsoid(cx + s * 1.8, 9.2, 20, 0.9, 0.6, 1.3, '#A0405A')
        tri(v, (cx + s * 4, 32), (cx + s * 10, 31), (cx + s * 9, 38), 'xz', 15, 17.5, pig)
    eyes(v, cx, 27, 5, r=2.1, look=(0, -0.2))
    brow(v, cx - 8, 30.5, cx - 3, 29.5, '#A0405A', 0.7)
    brow(v, cx + 3, 29.5, cx + 8, 30.5, '#A0405A', 0.7)
    smile(v, cx, 16, 6, 1.2, '#7A2040', 0.55)
    blush(v, cx, 21, 8.5, r=1.8)
    pts = [(cx + math.cos(t) * 1.6, 39 + t * 0.4, 24 + math.sin(t) * 1.6) for t in np.linspace(0, 4 * math.pi, 9)]
    poly(v, pts, 0.7, 0.6, pig_d)
    return v, SIZE


def orangutini():
    """Orangutini Ananassini — орангутан-ананас: ромбовая кожура, зелёный хохолок, длинные руки."""
    v = new(35)
    pine, pine_d, leaf, ora, face = '#F2B233', '#C98A1F', '#3FA34D', '#C4622D', '#E8B894'
    cx = 32
    v.ellipsoid(cx, 25, 22, 10, 9, 13, pine)
    v.paint((cx - 11, 15, 8), (cx + 11, 35, 36),
            lambda X, Y, Z: (np.abs(np.sin((np.arctan2(Y - 25, X - cx) * 5 + Z * 0.5))) < 0.25)
            | (np.abs(np.sin((np.arctan2(Y - 25, X - cx) * 5 - Z * 0.5))) < 0.25), pine_d)
    v.ellipsoid(cx, 24, 38, 7.5, 6.5, 6.5, ora)
    v.ellipsoid(cx, 18.5, 37, 5.5, 3, 5, face)
    for i in range(7):
        ang = -math.pi / 2 + (i - 3) * 0.35
        tip = (cx + math.cos(ang + math.pi / 2) * 0 + (i - 3) * 2.2, 25 + (abs(i - 3) - 1.5) * 0.8, 51 - abs(i - 3) * 1.8)
        cone(v, (cx + (i - 3) * 0.8, 24.5, 43), tip, 1.9, leaf if i % 2 else shade(leaf, 0.2))
    for s in (-1, 1):
        v.ellipsoid(cx + s * 7, 24.5, 39, 1.8, 1.4, 2.2, face)
    eyes(v, cx, 39.5, 2.3, r=1.4)
    nose(v, cx - 0.7, 36.5, 0.45)
    nose(v, cx + 0.7, 36.5, 0.45)
    smile(v, cx, 35, 5.5, 1.3, '#3A1A0A', 0.55, open_=True)
    for s in (-1, 1):
        arm(v, (cx + s * 8, 25, 29), (cx + s * 15, 22, 3), 2, ora, hand=face, hand_r=2.4, p_mid=(cx + s * 14, 24, 17))
        v.line((cx + s * 4, 25, 10), (cx + s * 4.5, 24, 3), 2.2, ora)
        v.ellipsoid(cx + s * 4.5, 22, 1.5, 2.6, 4, 1.5, face)
    return v, SIZE


def glorbo():
    """Glorbo Fruttodrillo — крокодил-арбуз: полосатый арбуз с красной мякотью сверху и зубастой мордой."""
    v = new(36)
    g1, g2, flesh, croc, croc_d = '#2E7D32', '#6CC24A', '#FF4D5E', '#4E8F3A', '#2F5E22'
    cx = 32
    v.ellipsoid(cx, 29, 20, 13, 14, 12, g2)
    v.paint((cx - 14, 14, 7), (cx + 14, 44, 33),
            lambda X, Y, Z: np.sin(np.arctan2(Y - 29, X - cx) * 8 + (Z - 20) * 0.15) > 0.2, g1)
    v.paint((cx - 14, 14, 25), (cx + 14, 44, 33), lambda X, Y, Z: Z > 28.5, flesh)
    v.paint((cx - 14, 14, 25), (cx + 14, 44, 33), lambda X, Y, Z: (Z > 27.3) & (Z <= 28.5), '#F5F5DC')
    for a in range(9):
        ang = a * 2 * math.pi / 9
        r = 6 + (a % 3) * 1.5
        v.ellipsoid(cx + math.cos(ang) * r, 29 + math.sin(ang) * r, 31.5, 0.6, 0.9, 0.5, BLACK)
    v.ellipsoid(cx, 11, 21, 7, 10, 4.5, croc)
    v.ellipsoid(cx, 11, 18.2, 6.4, 9.5, 2, '#C9D98A')
    for i in range(7):
        a = -1 + 2 * i / 6
        v.ellipsoid(cx + a * 5.4, 11 - 9 * math.sqrt(max(0, 1 - a * a)) + 0.6, 19.4, 0.5, 0.55, 1.0, WHITE)
    for s in (-1, 1):
        v.ellipsoid(cx + s * 1.8, 1.8, 22.5, 0.7, 0.5, 0.6, croc_d)
        v.ellipsoid(cx + s * 3.6, 16, 25, 2.8, 2.8, 2.8, croc)
        eye3(v, cx + s * 3.6, 14, 26, 2, slit=True, iris='#FFD23F')
    for x, y in ((21, 22), (43, 22), (21, 36), (43, 36)):
        v.line((x, y, 12), (x + (x - cx) * 0.15, y, 2), 2.4, croc)
        v.ellipsoid(x + (x - cx) * 0.15, y - 1.5, 1.4, 2.8, 3.6, 1.4, croc_d)
    poly(v, [(cx, 42, 14), (cx + 2, 47, 10), (cx + 5, 49, 7)], 3, 1, croc)
    return v, SIZE


def burbaloni():
    """Burbaloni Luliloli — капибара в половинке кокоса, с мандаринкой на голове."""
    v = new(37)
    shell, flesh, capy, capy_d, orange = '#6B4423', '#FFF6E5', '#9C6B45', '#6E4A2E', '#FF9F1C'
    cx = 32
    v.ellipsoid(cx, 26, 15, 15, 15, 13, shell)
    v.ellipsoid(cx, 26, 15, 14, 14, 12, flesh)
    v.ellipsoid(cx, 26, 15, 13, 13, 11, None)
    v.box(10, 54, 4, 48, 17, 40, None)
    v.paint((cx - 16, 10, 2), (cx + 16, 42, 17), lambda X, Y, Z: np.sin(np.arctan2(Y - 26, X - cx) * 14 + Z * 0.5)
            > 0.7, shade(shell, -0.25))
    v.ellipsoid(cx, 27, 18, 9, 10, 8, capy)
    v.ellipsoid(cx, 16, 25, 6.5, 7, 5.5, capy)
    v.ellipsoid(cx, 10.5, 24, 4.8, 2.4, 3.8, capy_d)
    for s in (-1, 1):
        v.ellipsoid(cx + s * 1.4, 8.4, 25, 0.7, 0.5, 0.5, BLACK)
        v.ellipsoid(cx + s * 5, 18, 30, 1.4, 1, 1.4, capy_d)
        eye3(v, cx + s * 3.6, fy(v, cx + s * 3.6, 28) + 0.4, 28, 1.3, lid=capy_d, lid_amount=0.55)
        arm(v, (cx + s * 7, 20, 18), (cx + s * 12, 16, 17.5), 1.5, capy, hand=capy_d, hand_r=1.6)
    smile(v, cx, 22, 2.5, 0.6, BLACK, 0.4)
    v.ellipsoid(cx, 16, 32.5, 3.2, 3.2, 2.8, orange)
    v.ellipsoid(cx + 0.8, 16.5, 35.3, 1.2, 0.6, 0.5, '#3FA34D')
    return v, SIZE


def espresso_signora():
    """Espresso Signora — синьора-эспрессо: голова-чашечка на блюдце, пенка-причёска, красное платье."""
    v = new(38)
    skin, dress, cup, coffee, pearl = '#F2C6A5', '#D7263D', '#FFFFFF', '#6B3E1F', '#F5F0E6'
    cx = 32
    for s in (-1, 1):
        v.line((cx + s * 2.5, 25, 13), (cx + s * 2.8, 25, 3.5), 1.1, skin)
        v.ellipsoid(cx + s * 2.8, 23.5, 2, 1.6, 3, 1.4, dress)
        v.line((cx + s * 2.8, 26, 2.5), (cx + s * 2.8, 26, 0.5), 0.45, dress)
    v.shape((cx - 12, 13, 11), (cx + 12, 37, 33),
            lambda X, Y, Z: ((X - cx) ** 2 + (Y - 25) ** 2) <= (4.5 + (31 - Z) * 0.33) ** 2, dress)
    dots(v, (cx, 25, 22), (8, 8, 9), 14, [WHITE], r=0.6, seed=8, zmin=13, zmax=30)
    v.line((cx, 25, 32), (cx, 25, 35), 1.3, skin)
    for a in range(10):
        ang = a * 2 * math.pi / 10
        v.ellipsoid(cx + math.cos(ang) * 2.2, 25 + math.sin(ang) * 2.2, 32.6, 0.65, 0.65, 0.65, pearl)
    for s in (-1, 1):
        arm(v, (cx + s * 4.5, 25, 30), (cx + s * 9, 21, 22), 0.9, skin, hand=skin, hand_r=1.1)
    v.box(cx + 8, cx + 12, 20, 22, 17, 20, '#1E1E26')  # сумочка
    poly(v, [(cx + 8.5, 21, 20.5), (cx + 9.5, 21, 22.5), (cx + 11.5, 21, 20.5)], 0.35, 0.35, '#FFD23F')
    v.ellipsoid(cx, 25, 35, 7.5, 7.5, 0.8, cup)
    v.shape((cx - 7, 18, 35), (cx + 7, 32, 43),
            lambda X, Y, Z: ((X - cx) ** 2 + (Y - 25) ** 2) <= (5 + (Z - 35) * 0.2) ** 2, cup)
    poly(v, [(cx + 5.5, 25, 41), (cx + 8.5, 25, 40), (cx + 8.5, 25, 37), (cx + 5.5, 25, 36.5)], 0.9, 0.9, cup)
    v.ellipsoid(cx, 25, 43.3, 6.6, 6.6, 2.2, coffee)
    v.ellipsoid(cx, 27, 46.5, 3.5, 3.5, 3.2, coffee)
    v.ellipsoid(cx, 25, 44.3, 5, 5, 1.2, '#D9B48A')
    eyes(v, cx, 39.5, 2.4, r=1.4, lid='#7A4AA0', lid_amount=0.3)
    for s in (-1, 1):
        for t in (-1, 0, 1):
            x = cx + s * 2.4 + t * 0.8
            y = fy(v, x, 41.3) - 0.3
            v.line((x, y, 41.2), (x + s * 0.3 + t * 0.4, y - 0.4, 42.5), 0.3, BLACK)
    v.ellipsoid(cx, fy(v, cx, 37) - 0.1, 37, 1.6, 0.6, 0.8, '#C8102E')
    blush(v, cx, 38, 3.8, r=1)
    return v, SIZE


def pipi_kiwi():
    """Pipi Kiwi — птичка-киви: мохнатый коричневый шар с долькой киви на пузе и длинным клювом."""
    v = new(39)
    fur, fur_d, kiwi, kiwi_c, beak = '#8B6A3E', '#6B4E2A', '#8CC63F', '#E6F5B0', '#D9B27A'
    cx, cy, cz = 32, 26, 20
    for s in (-1, 1):
        v.line((cx + s * 4, cy, 9), (cx + s * 4.5, cy - 1, 2), 0.9, beak)
        for a in (-0.6, 0, 0.6):
            v.line((cx + s * 4.5, cy - 1, 1.2), (cx + s * 4.5 + math.sin(a) * 3, cy - 1 - math.cos(a) * 3, 0.8),
                   0.5, beak)
    v.ellipsoid(cx, cy, cz, 12, 12, 12, fur)
    v.paint((cx - 13, cy - 13, cz - 13), (cx + 13, cy + 13, cz + 13),
            lambda X, Y, Z: np.sin(X * 1.7 + Z * 0.9) * np.sin(Y * 1.3 - Z * 1.1) > 0.45, fur_d)
    v.paint((cx - 13, cy - 13, cz - 13), (cx + 13, cy - 4, cz + 13),
            lambda X, Y, Z: (Y < cy - 7) & ((X - cx) ** 2 + (Z - cz + 2) ** 2 < 70), kiwi)
    v.paint((cx - 13, cy - 13, cz - 13), (cx + 13, cy - 4, cz + 13),
            lambda X, Y, Z: (Y < cy - 7) & ((X - cx) ** 2 + (Z - cz + 2) ** 2 < 10), kiwi_c)
    v.paint((cx - 13, cy - 13, cz - 13), (cx + 13, cy - 4, cz + 13),
            lambda X, Y, Z: (Y < cy - 7) & ((X - cx) ** 2 + (Z - cz + 2) ** 2 >= 62) & ((X - cx) ** 2 + (Z - cz + 2) ** 2 < 70),
            '#5E8F2A')
    for a in range(12):
        ang = a * 2 * math.pi / 12
        x, z = cx + math.cos(ang) * 4.6, cz - 2 + math.sin(ang) * 4.6
        v.ellipsoid(x, fy(v, x, z) + 0.2, z, 0.5, 0.4, 0.8, BLACK)
    v.ellipsoid(cx, 19, 33, 5.5, 5.5, 5, fur)
    poly(v, [(cx, 13.5, 32.5), (cx, 9, 30), (cx, 6, 26)], 1.2, 0.6, beak)
    eyes(v, cx, 34.5, 2.6, r=1.3)
    blush(v, cx, 31.5, 3.8, r=1)
    return v, SIZE


def noobini_pizzanini():
    """Noobini Pizzanini — кусок пиццы: корочка сверху, сыр с подтёками, пепперони, большие глаза."""
    v = new(40)
    cheese, crust, crust_d, pep, skin = '#FFD166', '#C68A4E', '#9C6532', '#D7263D', '#FFD166'
    cx = 32
    tri(v, (17, 46), (47, 46), (32, 12), 'xz', 21, 27, cheese)
    poly(v, [(16, 24, 46), (24, 24, 47.5), (32, 24, 48), (40, 24, 47.5), (48, 24, 46)], 3.2, 3.2, crust)
    v.paint((12, 18, 42), (52, 30, 52), lambda X, Y, Z: np.sin(X * 1.3) * np.sin(Z * 2.1) > 0.6, crust_d)
    for x, z in ((24, 40), (38, 41), (32, 30), (28, 22), (38, 30)):
        v.ellipsoid(x, 20.5, z, 2.6, 0.7, 2.6, pep)
        v.ellipsoid(x - 0.8, 20.1, z + 0.8, 0.5, 0.3, 0.5, '#A0101E')
    for x, ln in ((21, 4), (26, 6), (35, 5), (42, 3)):
        z0 = 12 + (abs(x - 32) / 15) * 34 * 0 + (46 - 12) * (abs(x - 32) / 15)
        v.line((x, 21.5, z0 + 1), (x, 21.3, z0 - ln), 0.9, cheese)
        v.ellipsoid(x, 21.3, z0 - ln, 1.2, 1, 1.3, cheese)
    eyes(v, cx, 35.5, 3.6, r=2.2, look=(0.3, 0))
    smile(v, cx, 27.5, 5, 1.3, '#5A1020', 0.55, open_=True)
    for s in (-1, 1):
        arm(v, (cx + s * 10, 24, 34), (cx + s * 16, 20, 27), 1.3, crust, hand=WHITE, hand_r=1.9)
    legs2(v, (cx - 3.5, cx + 3.5), 24, 16, 1.7, crust, shoe=('#FFFFFF', '#D7263D', '#26262B'), w=5, l=9)
    return v, SIZE


def graipuss():
    """Graipuss Medussi — медуза из винограда: купол из виноградин, листик, извилистые щупальца."""
    v = new(41)
    grape, grape2, grape3, tent, leaf = '#7B3FA0', '#9B59C8', '#5E2D82', '#C79BE8', '#3FA34D'
    cx, cy, cz = 32, 25, 32
    v.ellipsoid(cx, cy, cz, 10, 10, 8, grape3)
    pts = []
    for layer, (zz, rr, n) in enumerate(((cz + 6, 3.5, 5), (cz + 2, 8, 9), (cz - 2.5, 9.5, 12))):
        for i in range(n):
            ang = i * 2 * math.pi / n + layer * 0.4
            pts.append((cx + math.cos(ang) * rr, cy + math.sin(ang) * rr, zz))
    pts.append((cx, cy, cz + 9))
    for i, p in enumerate(pts):
        v.ellipsoid(*p, 3.4, 3.4, 3.4, (grape, grape2, grape3)[i % 3])
    v.line((cx, cy, cz + 11), (cx + 1, cy + 1, cz + 15), 0.8, '#6B4A2E')
    v.ellipsoid(cx + 3, cy + 1, cz + 14, 3, 1.2, 1.8, leaf)
    for i in range(8):
        ang = i * 2 * math.pi / 8 + 0.2
        r0 = 7.5
        pts2 = []
        for t in np.linspace(0, 1, 6):
            rr = r0 + t * 3
            wob = math.sin(t * 7 + i) * 1.8
            pts2.append((cx + math.cos(ang) * rr + math.cos(ang + 1.57) * wob,
                         cy + math.sin(ang) * rr + math.sin(ang + 1.57) * wob, cz - 5 - t * (cz - 6.5)))
        poly(v, pts2, 1.6, 0.8, tent)
    y = cy - 10
    for s in (-1, 1):
        eye3(v, cx + s * 3.6, y - 0.5, cz - 1.5, 2.1, look=(0, -0.2))
    v.ellipsoid(cx, y - 0.2, cz - 5.8, 1.6, 0.8, 1.0, '#3A1030')
    blush(v, cx, cz - 4.5, 6.5, r=1.2)
    return v, SIZE


def chef_crab():
    """Chef Crabracadabra — краб-повар-фокусник: колпак, усы, глаза на стебельках, волшебная палочка."""
    v = new(42)
    red, red_d, hat, stick = '#E8452C', '#B8301C', '#FFFFFF', '#1E1E26'
    cx = 32
    for i, dy in enumerate((-3, 0, 3)):
        for s in (-1, 1):
            poly(v, [(cx + s * 10, 25 + dy, 16), (cx + s * 16, 25 + dy, 12), (cx + s * 18, 25 + dy, 1.5)], 1.1, 0.8, red_d)
    v.ellipsoid(cx, 25, 19, 14, 10, 8, red)
    v.paint((cx - 15, 14, 11), (cx + 15, 36, 28), lambda X, Y, Z: Z < 15.5, shade(red, 0.25))
    v.cyl_z(cx, 28, 25, 33, 5, 5, hat)
    for dx, dz in ((0, 36), (-3.5, 34.5), (3.5, 34.5), (0, 33.5)):
        v.ellipsoid(cx + dx, 28, dz, 4, 4, 3.4, hat)
    for s in (-1, 1):
        v.line((cx + s * 4, 20, 25), (cx + s * 5, 18, 31), 1, red)
        eye3(v, cx + s * 5, 17, 32.5, 2.2, look=(-s * 0.2, 0))
        poly(v, [(cx + s * 12, 22, 20), (cx + s * 17, 18, 25), (cx + s * 20, 16, 27)], 2, 1.8, red)
        v.ellipsoid(cx + s * 22, 14.5, 29.5, 3.2, 2.4, 2.4, red)
        v.ellipsoid(cx + s * 22.5, 14.5, 25.5, 2.8, 2, 1.6, red_d)
    y = fy(v, cx, 20)
    for s in (-1, 1):
        poly(v, [(cx, y - 0.6, 20), (cx + s * 3, y - 0.3, 19.3), (cx + s * 5, y + 0.3, 20.3)], 0.9, 0.6, BLACK)
    smile(v, cx, 17.6, 4, 0.8, '#5A1020', 0.5)
    v.line((cx + 22, 12, 30), (cx + 25, 9, 40), 0.7, stick)
    v.ellipsoid(cx + 25.3, 8.7, 41, 0.9, 0.9, 1.1, WHITE)
    for a in range(5):
        ang = a * 2 * math.pi / 5 + 0.3
        v.line((cx + 25.3, 8.5, 43.5), (cx + 25.3 + math.cos(ang) * 2.2, 8.5, 43.5 + math.sin(ang) * 2.2), 0.6, '#FFD23F')
    return v, SIZE


CHARS_B = {
    'La_Vacca_Saturno_Saturnita': ('La Vacca Saturno Saturnita', vacca_saturno),
    'Frigo_Camelo': ('Frigo Camelo', frigo_camelo),
    'Tim_Cheese': ('Tim Cheese', tim_cheese),
    'Svinina_Bombardino': ('Svinina Bombardino', svinina),
    'Orangutini_Ananassini': ('Orangutini Ananassini', orangutini),
    'Glorbo_Fruttodrillo': ('Glorbo Fruttodrillo', glorbo),
    'Burbaloni_Luliloli': ('Burbaloni Luliloli', burbaloni),
    'Espresso_Signora': ('Espresso Signora', espresso_signora),
    'Pipi_Kiwi': ('Pipi Kiwi', pipi_kiwi),
    'Noobini_Pizzanini': ('Noobini Pizzanini', noobini_pizzanini),
    'Graipuss_Medussi': ('Graipuss Medussi', graipuss),
    'Chef_Crabracadabra': ('Chef Crabracadabra', chef_crab),
}
