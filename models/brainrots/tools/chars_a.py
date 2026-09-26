"""Брейнроты, группа A: Cocofanto Elefanto, драконы, самолёты и лесные."""
import math

import numpy as np

from parts import (SIZE, arm, blush, brow, cone, dots, ellipsoid_paint, eye3, eye_at, eyes, fin_yz, fy, legs2,
                   legs4, new, nose, poly, smile, teeth, tri, whiskers, wing)
from voxel import shade
from voxel_chars import BLACK, WHITE


def cocofanto():
    """Cocofanto Elefanto — кокос-слон: волосатый кокос, слоновья голова с ушами, хоботом и бивнями."""
    v = new(11)
    coco, coco_d, grey, grey_d, pink = '#6B4423', '#4A2E17', '#9AA3AE', '#7A838E', '#F3A3B8'
    v.ellipsoid(32, 28, 22, 15, 14, 14, coco)
    v.paint((16, 13, 7), (48, 43, 37),
            lambda X, Y, Z: np.sin(np.arctan2(Y - 28, X - 32) * 13 + Z * 0.45) > 0.55, coco_d)
    for dx in (-3, 3, 0):                       # «глазки» кокоса на макушке сзади
        v.ellipsoid(32 + dx, 36 + abs(dx) * 0.3, 34 - abs(dx) * 0.4, 1.4, 1.4, 1.2, coco_d)
    v.ellipsoid(32, 16, 34, 10, 9, 9, grey)     # голова слона
    for s in (-1, 1):                            # уши
        v.ellipsoid(32 + s * 12, 19, 35, 6.5, 1.8, 8, grey)
        v.ellipsoid(32 + s * 12, 17.6, 35, 4.8, 0.8, 6, pink)
    poly(v, [(32, 8, 31), (32, 5, 26), (32, 4, 20), (33, 4, 15), (35.5, 3, 12.5), (37.5, 3, 14.5)], 3.4, 1.4, grey)
    v.paint((25, 0, 10), (40, 12, 32), lambda X, Y, Z: (np.sin(Z * 1.6) > 0.7) & (Y < 9), grey_d)
    for s in (-1, 1):                            # бивни
        poly(v, [(32 + s * 4, 9, 29), (32 + s * 5.5, 5, 25), (32 + s * 5, 3, 21)], 1.3, 0.5, '#FFF8E7')
    eyes(v, 32, 38, 4.5, r=2.1, look=(0, -0.2))
    brow(v, 25.5, 41.5, 30, 42.5)
    brow(v, 34, 42.5, 38.5, 41.5)
    blush(v, 32, 33, 7)
    legs4(v, [(22, 22), (42, 22), (23, 34), (41, 34)], 12, 3.3, grey, hoof=grey_d, foot_r=3.6)
    for x, y in ((22, 22), (42, 22)):
        for dx in (-1.5, 0, 1.5):
            v.ellipsoid(x + dx, y - 3.6, 1.2, 0.8, 0.6, 0.8, '#FFF8E7')
    poly(v, [(32, 42, 20), (33, 46, 15), (34, 47, 11)], 0.9, 0.7, grey)
    v.ellipsoid(34, 47.5, 10, 1.4, 1.4, 1.6, coco_d)
    return v, SIZE


def dragon_cannelloni():
    """Dragon Cannelloni — красный дракон, тело — трубочка каннеллони с рикоттой и томатным соусом."""
    v = new(12, (72, 56, 68))
    pasta, pasta_d, red, red_d, cream, sauce = '#F0CF7A', '#D9AE52', '#D93A2B', '#A8261C', '#FFF3D6', '#C8261E'
    cx = 36
    wing(v, (cx - 7, 38, 36), -1, 24, 18, '#E8604F', bone=red_d)
    wing(v, (cx + 7, 38, 36), 1, 24, 18, '#E8604F', bone=red_d)
    poly(v, [(cx, 36, 16), (cx + 6, 44, 10), (cx + 14, 48, 7), (cx + 20, 46, 9)], 4.5, 1.2, red)
    tri(v, (cx + 18, 8), (cx + 25, 7), (cx + 22, 14), 'xz', 45, 47.5, red_d)
    for s in (-1, 1):
        v.line((cx + s * 5, 28, 16), (cx + s * 6, 26, 4), 3.4, red)
        v.ellipsoid(cx + s * 6, 23, 2, 4, 5, 2.2, red_d)
        for dx in (-1.5, 0, 1.5):
            v.ellipsoid(cx + s * 6 + dx, 18.5, 1.3, 0.7, 1, 0.7, cream)
    v.cyl_z(cx, 28, 14, 40, 10.5, 9.5, pasta)  # трубочка каннеллони
    v.paint((cx - 11, 18, 14), (cx + 11, 38, 41), lambda X, Y, Z: np.sin(Z * 1.3) > 0.65, pasta_d)
    v.ellipsoid(cx, 28, 40.5, 9.5, 8.5, 2.5, cream)  # рикотта на срезе
    v.paint((cx - 11, 18, 33), (cx + 11, 38, 44), lambda X, Y, Z: Z > 36.5 + np.sin(X * 1.1) * 1.8, sauce)
    for x, ln in ((cx - 6, 7), (cx - 1, 11), (cx + 4, 6), (cx + 7, 9)):
        y = fy(v, x, 34) + 0.3
        v.line((x, y, 36), (x, y - 0.2, 36 - ln), 1.0, sauce)
        v.ellipsoid(x, y - 0.2, 36 - ln, 1.4, 1.1, 1.5, sauce)
    v.ellipsoid(cx, 25, 49, 9, 8, 7, red)        # голова
    v.ellipsoid(cx, 16, 46.5, 6.5, 6, 4.5, red)  # морда
    v.ellipsoid(cx, 16, 44.5, 5.5, 5.5, 2.5, '#F28A6E')
    for s in (-1, 1):
        v.ellipsoid(cx + s * 2.2, 10.5, 48, 0.9, 0.7, 0.7, red_d)  # ноздри
        cone(v, (cx + s * 5, 27, 54), (cx + s * 8, 31, 62), 2.2, cream)
        cone(v, (cx + s * 8, 25, 49), (cx + s * 13, 28, 51), 1.6, red_d)
    eyes(v, cx, 51, 4.3, r=2.3, slit=True, iris='#FFD23F')
    brow(v, cx - 7, 54, cx - 2, 53, red_d, 0.9)
    brow(v, cx + 2, 53, cx + 7, 54, red_d, 0.9)
    smile(v, cx, 44.5, 8, 1.4, '#5A1020', 0.65)
    teeth(v, cx, 44, 6, n=3)
    for s in (-1, 1):
        arm(v, (cx + s * 10, 24, 30), (cx + s * 14, 18, 25), 1.8, red, hand=red_d, hand_r=2.2)
    for z in range(44, 60, 4):                   # гребень
        fin_yz(v, (30, z - 2), (33, z - 1), (34, z + 1.5), cx - 0.8, cx + 0.8, cream)
    return v, SIZE


def draghetto_gelato():
    """Draghetto Gelato — дракон-мороженое: шарики пломбира, хвост-вафельный рожок, вишенка на голове."""
    v = new(13)
    blue, blue_d, mint, pink, waffle, waffle_d, cream = ('#6EC6FF', '#3E8FD1', '#9CF2C5', '#FF9EC7',
                                                      '#D9A45B', '#A8742E', '#FFF3C4')
    cx = 32
    wing(v, (cx - 6, 34, 30), -1, 15, 12, '#BDE7FF', bone=blue_d)
    wing(v, (cx + 6, 34, 30), 1, 15, 12, '#BDE7FF', bone=blue_d)
    v.line((cx, 34, 12), (cx + 2, 50, 7), 5.5, waffle, r1=0.6)  # хвост-рожок
    v.paint((cx - 7, 28, 0), (cx + 9, 52, 20),
            lambda X, Y, Z: (np.abs(np.sin((Y + Z) * 0.9)) < 0.22) | (np.abs(np.sin((Y - Z) * 0.9)) < 0.22), waffle_d)
    for s in (-1, 1):
        v.line((cx + s * 5.5, 27, 10), (cx + s * 6, 25, 3), 3, blue)
        v.ellipsoid(cx + s * 6, 22.5, 1.8, 3.4, 4.5, 2, blue_d)
    v.ellipsoid(cx, 27, 17, 11, 10, 9, mint)     # шарик мяты
    v.paint((cx - 12, 16, 7), (cx + 12, 38, 14),
            lambda X, Y, Z: Z < 11.5 + np.sin(X * 0.9) * 1.6 + np.cos(Y * 0.8), shade(mint, -0.18))
    v.ellipsoid(cx, 26, 28.5, 9, 8.5, 7.5, pink)  # шарик клубники
    dots(v, (cx, 26, 28.5), (9, 8.5, 7.5), 16, ['#FFFFFF', '#FFD23F', '#7C5CFF', '#FF4D6D'], r=0.6, seed=4,
         flat=False)
    dots(v, (cx, 27, 17), (11, 10, 9), 12, ['#FFFFFF', '#FF4D6D', '#FFD23F'], r=0.6, seed=5, flat=False, zmin=12)
    v.ellipsoid(cx, 24, 39.5, 8, 7, 7, blue)      # голова
    v.ellipsoid(cx, 16.5, 37.5, 5.2, 4.5, 3.8, blue)
    v.ellipsoid(cx, 16.5, 36, 4.5, 4, 2, '#BDE7FF')
    for s in (-1, 1):
        v.ellipsoid(cx + s * 1.8, 12.3, 38.5, 0.7, 0.5, 0.6, blue_d)
        cone(v, (cx + s * 4.5, 25, 45), (cx + s * 6.5, 28, 51), 1.6, cream)
    v.ellipsoid(cx, 24, 47, 2.4, 2.4, 2.2, '#E0182D')  # вишенка
    v.line((cx, 24, 49), (cx + 1.5, 25, 52), 0.5, '#3E7B2A')
    eyes(v, cx, 41.5, 3.6, r=2.1, iris='#8C5CFF', look=(0, -0.2))
    blush(v, cx, 37.5, 6, r=1.3)
    smile(v, cx, 35.5, 5, 1.0, '#3A1030', 0.55)
    for s in (-1, 1):
        arm(v, (cx + s * 8, 24, 27), (cx + s * 12, 18, 22), 1.5, blue, hand=blue_d, hand_r=1.9)
    return v, SIZE


def drakonino_peperonino():
    """Drakonino Peperonino — дракон-перчик чили: огненный язык пламени, хвостик-кончик перца."""
    v = new(14)
    red, red_d, green, orange, yellow = '#E0261B', '#A8150E', '#3FA34D', '#FF7A1A', '#FFD23F'
    cx = 32
    wing(v, (cx - 6, 32, 34), -1, 17, 14, '#FF8A3D', bone=red_d)
    wing(v, (cx + 6, 32, 34), 1, 17, 14, '#FF8A3D', bone=red_d)
    poly(v, [(cx + 3, 46, 5), (cx + 2, 40, 7), (cx, 33, 12), (cx, 28, 20), (cx, 25, 30), (cx, 24, 39)], 1.2, 10, red)
    v.ellipsoid(cx, 24, 40, 10, 9, 8, red)
    v.paint((cx - 11, 14, 5), (cx + 11, 48, 50),
            lambda X, Y, Z: np.sin(np.arctan2(Y - 26, X - cx) * 6 + Z * 0.1) > 0.8, red_d)
    v.ellipsoid(cx, 24, 47.5, 7, 6, 2.2, green)  # чашечка
    for a in range(5):
        ang = a * 2 * math.pi / 5
        v.line((cx, 24, 47), (cx + math.cos(ang) * 8, 24 + math.sin(ang) * 7, 45), 1.2, green, r1=0.5)
    poly(v, [(cx, 24, 48), (cx + 1, 25, 52), (cx + 3, 26, 55), (cx + 5, 25, 56)], 1.6, 1.1, '#2E7D32')
    eyes(v, cx, 42, 4.2, r=2.2, slit=True, iris=yellow)
    brow(v, cx - 7, 45.5, cx - 2, 44, BLACK, 0.8)
    brow(v, cx + 2, 44, cx + 7, 45.5, BLACK, 0.8)
    y = fy(v, cx, 35)
    v.ellipsoid(cx, y + 0.5, 35, 3.6, 1.2, 2.6, '#4A0A0A')
    for i, (col, r) in enumerate(((orange, 3.2), (yellow, 2.2), (orange, 2.4), ('#FFF3A0', 1.4))):
        v.ellipsoid(cx + (i % 2) * 1.5 - 0.7, y - 2.5 - i * 2.4, 35 + i * 0.8, r, r * 0.9, r * 0.9, col)
    for s in (-1, 1):
        arm(v, (cx + s * 9, 24, 30), (cx + s * 13, 19, 25), 1.6, red, hand=red_d, hand_r=2)
    legs2(v, (cx - 4, cx + 4), 27, 10, 2.2, red, shoe=('#3FA34D', '#FFD23F', '#1E1E26'))
    return v, SIZE


def bombardiro():
    """Bombardiro Crocodilo — крокодил-бомбардировщик: зубастая морда, крылья, пропеллеры, бомбы."""
    v = new(15)
    green, green_d, belly, metal = '#4E8F3A', '#2F5E22', '#C9D98A', '#7A8490'
    cx = 32
    v.ellipsoid(cx, 30, 24, 9, 17, 8, green)         # фюзеляж
    v.paint((cx - 10, 12, 15), (cx + 10, 48, 21), lambda X, Y, Z: Z < 19.5, belly)
    v.ellipsoid(cx, 30, 23, 31, 6.5, 1.4, '#6E8F5A')  # крылья
    v.paint((0, 22, 20), (64, 38, 26), lambda X, Y, Z: np.abs(X - cx) > 26, '#E23B3B')
    v.ellipsoid(cx, 47, 26, 11, 3, 1.1, '#6E8F5A')
    fin_yz(v, (43, 26), (50, 26), (50, 38), cx - 0.9, cx + 0.9, '#6E8F5A')
    v.ellipsoid(cx, 12, 26, 7, 11, 5, green)          # морда
    v.ellipsoid(cx, 12, 22.2, 6.2, 10, 2.2, belly)
    for i in range(7):
        a = -1 + 2 * i / 6
        x = cx + a * 5.2
        yy = 12 - 9.5 * math.sqrt(max(0, 1 - a * a)) + 0.5
        v.ellipsoid(x, yy, 23.6, 0.55, 0.6, 1.1, WHITE)
    for s in (-1, 1):
        v.ellipsoid(cx + s * 2, 1.8, 27.5, 0.8, 0.6, 0.6, green_d)
        v.ellipsoid(cx + s * 3.6, 15, 31, 3, 3, 3, green)
        eye3(v, cx + s * 3.6, 12.8, 32, 2.1, slit=True, iris='#FFD23F', lid=green_d, lid_amount=0.35)
    for s in (-1, 1):                                 # двигатели и пропеллеры
        ex = cx + s * 15
        v.line((ex, 20, 23), (ex, 31, 23), 2.6, metal)
        v.ellipsoid(ex, 18.5, 23, 1.4, 1.2, 1.4, BLACK)
        v.ellipsoid(ex, 17.6, 23, 7, 0.6, 1.1, '#C9CFD8')
        v.ellipsoid(ex, 17.6, 23, 1.1, 0.6, 7, '#C9CFD8')
        v.ellipsoid(cx + s * 9, 30, 18.5, 1.8, 4.5, 1.8, '#2A2A33')  # бомбы
        v.ellipsoid(cx + s * 9, 35, 18.5, 1.9, 0.8, 1.9, '#E23B3B')
        v.line((cx + s * 5, 30, 18), (cx + s * 6, 29, 4), 2, green)
        v.ellipsoid(cx + s * 6, 26.5, 1.6, 2.6, 3.5, 1.6, green_d)
    return v, SIZE


def patapim():
    """Brr Brr Patapim — лесной дух-пень: длинный нос, листья на макушке, огромные босые ступни."""
    v = new(16)
    bark, bark_d, skin, leaf, leaf2 = '#8A5A33', '#5E3A1E', '#E8B98F', '#4CAF50', '#7BCB5C'
    cx = 32
    v.ellipsoid(cx, 25, 30, 10, 9, 14, bark)
    v.paint((cx - 11, 15, 15), (cx + 11, 35, 45),
            lambda X, Y, Z: np.sin(np.arctan2(Y - 25, X - cx) * 9 + np.sin(Z * 0.4)) > 0.75, bark_d)
    for i, (dx, dy, dz, r) in enumerate([(0, 0, 44, 6), (-5, 2, 42, 4.5), (5, 1, 42.5, 4.5), (-2, 5, 46, 4),
                                        (3, -2, 46.5, 3.8), (-7, 4, 39, 3.5), (7, 3, 39.5, 3.5)]):
        v.ellipsoid(cx + dx, 25 + dy, dz, r, r * 0.9, r * 0.8, leaf if i % 2 == 0 else leaf2)
    v.ellipsoid(cx, 14, 30, 3.2, 5.5, 6.5, '#B07A4A')   # нос
    v.ellipsoid(cx, 10, 25.5, 2.4, 2.4, 2.4, '#B07A4A')
    eyes(v, cx, 36, 4.3, r=2.6, look=(0.3, 0))
    brow(v, cx - 7.5, 39.8, cx - 2, 40.8, bark_d, 0.9)
    brow(v, cx + 2, 40.8, cx + 7.5, 39.8, bark_d, 0.9)
    smile(v, cx, 21, 6, 1.2, '#3A1A0A', 0.6)
    for s in (-1, 1):
        arm(v, (cx + s * 9, 25, 32), (cx + s * 16, 21, 16), 1.3, bark, hand=bark_d, hand_r=1.9,
            p_mid=(cx + s * 14, 23, 25))
        x = cx + s * 5
        v.line((x, 25, 17), (x, 24, 6), 1.8, bark)
        v.ellipsoid(x + s * 0.8, 18, 3, 4.6, 8.5, 3, skin)  # огромная ступня
        for t in range(5):
            v.ellipsoid(x + s * 0.8 + (t - 2) * 1.8, 10.3 + abs(t - 2) * 0.4, 2.4, 0.95, 1.2, 1.1, skin)
    return v, SIZE


def lirili():
    """Lirilì Larilà — слон-кактус в сандалиях: колючий зелёный кактус с цветком и слоновьей головой."""
    v = new(17)
    cac, cac_d, grey, grey_d, sandal = '#4FA54A', '#2F7A2E', '#9AA0A8', '#6E747C', '#8B5A2B'
    cx = 32
    v.cyl_z(cx, 25, 12, 38, 8.5, 8.5, cac)
    v.ellipsoid(cx, 25, 38, 8.5, 8.5, 3, cac)
    poly(v, [(cx - 8, 25, 25), (cx - 14, 25, 25), (cx - 15, 25, 34)], 3, 2.6, cac)
    poly(v, [(cx + 8, 25, 21), (cx + 14, 25, 21), (cx + 15, 25, 29)], 3, 2.6, cac)
    v.paint((cx - 19, 15, 12), (cx + 19, 35, 42),
            lambda X, Y, Z: np.sin(np.arctan2(Y - 25, X - cx) * 8) > 0.72, cac_d)
    dots(v, (cx, 25, 26), (8.6, 8.6, 12), 16, ['#F5F5DC'], r=0.5, seed=3)
    v.ellipsoid(cx, 22, 45, 8, 7, 7, grey)      # голова слона
    for s in (-1, 1):
        v.ellipsoid(cx + s * 9.5, 24, 46, 4.5, 1.5, 6, grey)
        v.ellipsoid(cx + s * 9.5, 22.8, 46, 3.2, 0.6, 4.5, '#F3A3B8')
    poly(v, [(cx, 15, 43), (cx, 13, 37), (cx + 1, 13, 32), (cx + 3.5, 14, 30)], 2.6, 1.4, grey)
    eyes(v, cx, 47.5, 3.6, r=1.9)
    blush(v, cx, 43.5, 5.8, r=1.2)
    for a in range(5):                          # цветок на макушке
        ang = a * 2 * math.pi / 5
        v.ellipsoid(cx + math.cos(ang) * 2.4, 22 + math.sin(ang) * 2.4, 52.5, 2, 2, 1.2, '#FF5FA2')
    v.ellipsoid(cx, 22, 53.3, 1.4, 1.4, 1, '#FFD23F')
    for s in (-1, 1):
        x = cx + s * 4
        v.line((x, 25, 13), (x, 25, 3.5), 2.4, grey)
        v.ellipsoid(x, 22, 1, 3.4, 5.5, 1, sandal)
        v.line((x - 3, 21, 2.8), (x + 3, 21, 2.8), 0.7, sandal)
    return v, SIZE


def cappuccino_assassino():
    """Cappuccino Assassino — стаканчик-ниндзя: маска, красная повязка, две катаны за спиной."""
    v = new(18)
    cup, coffee, foam, black, red, steel = '#F4F1EA', '#6B3E1F', '#E8CFA8', '#1E1E26', '#D7263D', '#C9CFD8'
    cx = 32
    for s in (-1, 1):                            # катаны за спиной крест-накрест
        v.line((cx - s * 12, 36, 12), (cx + s * 10, 36, 44), 0.8, steel)
        v.line((cx + s * 10, 36, 44), (cx + s * 13, 36, 49), 1.2, black)
        v.ellipsoid(cx + s * 9.5, 36, 43, 2, 1.2, 0.6, '#FFD23F')
    v.shape((cx - 12, 14, 12), (cx + 12, 36, 40),
            lambda X, Y, Z: ((X - cx) ** 2 + (Y - 25) ** 2) <= (8.5 + (Z - 12) * 0.1) ** 2, cup)
    v.paint((cx - 13, 13, 38), (cx + 13, 37, 40), lambda X, Y, Z: Z >= 38.8, coffee)
    v.paint((cx - 13, 13, 38), (cx + 13, 37, 40),
            lambda X, Y, Z: (Z >= 38.8) & (((X - cx) ** 2 + (Y - 25) ** 2) < 16), foam)
    poly(v, [(cx + 10, 25, 33), (cx + 15, 25, 32), (cx + 16, 25, 26), (cx + 15, 25, 20), (cx + 10, 25, 19)],
         1.6, 1.6, cup)
    v.paint((cx - 13, 13, 26), (cx + 13, 37, 33), lambda X, Y, Z: (Z > 26.5) & (Z < 32.5), black)
    v.paint((cx - 13, 13, 32), (cx + 13, 37, 35), lambda X, Y, Z: (Z >= 32.5) & (Z < 34.5), red)
    poly(v, [(cx + 6, 32, 33.5), (cx + 11, 38, 35), (cx + 16, 42, 33)], 0.9, 0.7, red)
    poly(v, [(cx + 6, 32, 33), (cx + 10, 39, 31), (cx + 14, 43, 29)], 0.9, 0.7, red)
    for s in (-1, 1):
        eye3(v, cx + s * 3.6, fy(v, cx + s * 3.6, 29.5) + 0.3, 29.5, 1.9, look=(-s * 0.2, 0), lid=black,
             lid_amount=0.35)
    brow(v, cx - 6.5, 32, cx - 1.5, 31, WHITE, 0.55)
    brow(v, cx + 1.5, 31, cx + 6.5, 32, WHITE, 0.55)
    for s in (-1, 1):
        arm(v, (cx + s * 9, 25, 24), (cx + s * 15, 20, 20), 1.5, black, hand=black, hand_r=2)
    legs2(v, (cx - 4, cx + 4), 25, 13, 2, black, shoe=(black, red, '#444450'))
    return v, SIZE


def ballerina():
    """Ballerina Cappuccina — балерина с головой-чашкой капучино, розовая пачка, руки над головой."""
    v = new(19)
    skin, tutu, tutu_d, cup, coffee, foam = '#F2C6A5', '#FFB3D1', '#FF8CB8', '#FFFFFF', '#7A4A26', '#EEDCC0'
    cx = 32
    for s in (-1, 1):
        v.line((cx + s * 2.3, 25, 18), (cx + s * 2.8, 25, 3.5), 1.1, skin)
        v.ellipsoid(cx + s * 2.8, 24, 2, 1.5, 2.6, 1.8, tutu_d)
        v.line((cx + s * 2.8 - 1, 23, 4.5), (cx + s * 2.8 + 1, 23, 4.5), 0.35, tutu_d)
    v.shape((cx - 13, 12, 16), (cx + 13, 38, 22),
            lambda X, Y, Z: ((X - cx) ** 2 + (Y - 25) ** 2 <= (12 + np.sin(np.arctan2(Y - 25, X - cx) * 12)) ** 2)
            & (np.abs(Z - 19 - 0.08 * np.sqrt((X - cx) ** 2 + (Y - 25) ** 2)) < 1.6), tutu)
    v.paint((cx - 13, 12, 16), (cx + 13, 38, 23), lambda X, Y, Z: Z > 20.3, tutu_d)
    v.ellipsoid(cx, 25, 25.5, 4.3, 3.8, 6, tutu)
    v.line((cx, 25, 30), (cx, 25, 33), 1.1, skin)
    for s in (-1, 1):
        poly(v, [(cx + s * 3.5, 25, 29.5), (cx + s * 9, 24, 36), (cx + s * 8.5, 24, 45), (cx + s * 3.2, 24, 50.5)],
             0.9, 0.8, skin)
        v.ellipsoid(cx + s * 2.4, 24, 51, 1.3, 1.2, 1.3, skin)
    v.shape((cx - 8, 17, 33), (cx + 8, 33, 43),
            lambda X, Y, Z: ((X - cx) ** 2 + (Y - 25) ** 2) <= (5.8 + (Z - 33) * 0.18) ** 2, cup)
    v.paint((cx - 9, 16, 42), (cx + 9, 34, 43), lambda X, Y, Z: Z >= 42, coffee)
    v.paint((cx - 9, 16, 42), (cx + 9, 34, 43), lambda X, Y, Z: (Z >= 42) & ((X - cx) ** 2 + (Y - 25) ** 2 < 10), foam)
    v.ellipsoid(cx, 25, 33, 7.5, 7.5, 0.8, cup)  # блюдце
    poly(v, [(cx + 6.5, 25, 41), (cx + 10, 25, 40), (cx + 10, 25, 36), (cx + 6.5, 25, 35)], 1, 1, cup)
    eyes(v, cx, 38.5, 2.6, r=1.5, look=(0, 0.2))
    for s in (-1, 1):
        for t in (-1, 0, 1):
            x = cx + s * 2.6 + t * 0.9
            y = fy(v, x, 40.3) - 0.3
            v.line((x, y, 40.3), (x + s * 0.4 + t * 0.4, y - 0.4, 41.6), 0.35, BLACK)
    blush(v, cx, 36.8, 4.2, r=1.1)
    smile(v, cx, 36.3, 2.8, 0.7, '#D7263D', 0.45)
    return v, SIZE


def chimpanzini():
    """Chimpanzini Bananini — шимпанзе, вылезающий из очищенного банана."""
    v = new(20)
    yel, yel_d, brown, face = '#FFD93B', '#E0A800', '#6B4A2E', '#E8C49A'
    cx = 32
    v.ellipsoid(cx, 25, 19, 9, 9, 13, yel)
    v.ellipsoid(cx, 25, 6.5, 2.5, 2.5, 2, '#5E3A1E')
    for s, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):  # лепестки кожуры
        dx = s * 8 if s else 0
        yy = 25 + dy * 8
        tip = (cx + s * 15 if s else cx, 25 + dy * 14, 16)
        poly(v, [(cx + dx, yy, 29), (cx + dx * 1.35, 25 + dy * 11, 25), tip], 3.2, 1.6, yel)
    v.paint((cx - 10, 15, 5), (cx + 10, 35, 33),
            lambda X, Y, Z: np.abs(np.sin(np.arctan2(Y - 25, X - cx) * 2.5)) < 0.08, yel_d)  # грани банана
    v.ellipsoid(cx, 25, 31, 8, 7, 7, brown)
    v.ellipsoid(cx, 24, 42, 7, 6.5, 6.5, brown)
    v.ellipsoid(cx, 19, 41, 5.5, 3, 5, face)
    for s in (-1, 1):
        v.ellipsoid(cx + s * 7.3, 24, 43, 2.2, 1.5, 2.6, face)
    eyes(v, cx, 43.5, 2.3, r=1.6)
    nose(v, cx - 0.8, 40.5, 0.5)
    nose(v, cx + 0.8, 40.5, 0.5)
    smile(v, cx, 39, 5, 1.4, '#3A1A0A', 0.55, open_=True)
    teeth(v, cx, 39, 3.5, n=2)
    arm(v, (cx - 7, 25, 33), (cx - 14, 20, 42), 1.6, brown, hand=face, hand_r=2, p_mid=(cx - 12, 23, 35))
    arm(v, (cx + 7, 25, 33), (cx + 13, 19, 29), 1.6, brown, hand=face, hand_r=2)
    poly(v, [(cx + 13, 16, 34), (cx + 14, 16, 29), (cx + 12, 17, 25)], 1.6, 1.2, yel)  # мини-банан в руке
    for s in (-1, 1):
        v.line((cx + s * 4, 25, 8), (cx + s * 4.5, 24, 3), 2, brown)
        v.ellipsoid(cx + s * 4.5, 22, 1.6, 2.6, 4, 1.6, face)
    return v, SIZE


def trippi_troppi():
    """Trippi Troppi — креветка с кошачьей головой: розовый сегментированный хвост, усы-антенны."""
    v = new(21)
    shrimp, shrimp_d, cat, cat_d = '#FF8A5C', '#E0603A', '#FFD6A5', '#F2A65A'
    cx = 32
    poly(v, [(cx, 22, 30), (cx, 28, 25), (cx, 33, 18), (cx, 33, 11), (cx, 29, 6), (cx, 24, 6)], 8, 3.5, shrimp)
    v.paint((cx - 9, 12, 0), (cx + 9, 44, 40), lambda X, Y, Z: np.sin((Z + Y * 0.6) * 1.1) > 0.7, shrimp_d)
    tri(v, (cx - 5, 3), (cx + 5, 3), (cx, 8), 'xz', 18, 21, shrimp_d)
    for i in range(4):                           # лапки
        for s in (-1, 1):
            v.line((cx + s * 4, 26 + i * 2.2, 14 + i * 1.5), (cx + s * 7, 24 + i * 2.2, 1.5), 0.8, shrimp_d)
    v.ellipsoid(cx, 19, 38, 8, 7, 7, cat)
    for s in (-1, 1):
        tri(v, (cx + s * 3, 43), (cx + s * 8, 42), (cx + s * 7, 49), 'xz', 18, 21, cat)
        tri(v, (cx + s * 4, 43.5), (cx + s * 7.2, 43), (cx + s * 6.6, 47.5), 'xz', 17.3, 18, '#FF9EB5')
        poly(v, [(cx + s * 2, 17, 44), (cx + s * 5, 12, 51), (cx + s * 10, 11, 56)], 0.6, 0.45, shrimp_d)
    v.paint((cx - 9, 11, 31), (cx + 9, 27, 46), lambda X, Y, Z: (np.sin(X * 1.4) > 0.8) & (Z > 42), cat_d)
    eyes(v, cx, 39.5, 3.3, r=2.1, iris='#7CD13B', slit=True)
    nose(v, cx, 36.8, 0.8, '#FF6F91')
    smile(v, cx, 35.5, 3.5, 0.8, '#5A2020', 0.45)
    whiskers(v, cx, 36.5)
    return v, SIZE


def boneca():
    """Boneca Ambalabu — лягушка на автомобильной покрышке, с человеческими ногами в кроссовках."""
    v = new(22)
    tire, tire_d, rim, frog, frog_d = '#26262B', '#3A3A42', '#B0B4BC', '#6CC24A', '#4A9A32'
    cx, cz = 32, 25
    v.shape((cx - 13, 18, cz - 13), (cx + 13, 31, cz + 13),
            lambda X, Y, Z: ((X - cx) ** 2 + (Z - cz) ** 2 <= 144) & ((X - cx) ** 2 + (Z - cz) ** 2 >= 30)
            & (Y >= 18) & (Y < 31), tire)
    v.paint((cx - 13, 17, cz - 13), (cx + 13, 32, cz + 13),
            lambda X, Y, Z: (np.sin(np.arctan2(Z - cz, X - cx) * 18) > 0.3) & ((X - cx) ** 2 + (Z - cz) ** 2 > 110),
            tire_d)
    v.shape((cx - 6, 21, cz - 6), (cx + 6, 28, cz + 6),
            lambda X, Y, Z: (X - cx) ** 2 + (Z - cz) ** 2 <= 36, rim)
    for a in range(5):
        ang = a * 2 * math.pi / 5
        v.ellipsoid(cx + math.cos(ang) * 3, 20.5, cz + math.sin(ang) * 3, 0.8, 0.6, 0.8, '#5A5F6E')
    v.ellipsoid(cx, 23, 42, 9.5, 8, 6.5, frog)
    v.paint((cx - 10, 14, 35), (cx + 10, 32, 49), lambda X, Y, Z: Z < 39.5, '#C8E6A0')
    for s in (-1, 1):
        v.ellipsoid(cx + s * 5, 19, 47, 3.2, 3.2, 3.2, frog)
        eye3(v, cx + s * 5, 17, 47.5, 2.4, lid=frog_d, lid_amount=0.3, iris='#FFB300')
    smile(v, cx, 40.5, 11, 1.2, '#2E5E1E', 0.7)
    blush(v, cx, 40, 7, r=1.3)
    for s in (-1, 1):
        arm(v, (cx + s * 8, 22, 40), (cx + s * 14, 19, 36), 1.3, frog, hand=frog_d, hand_r=1.9)
    legs2(v, (cx - 4.5, cx + 4.5), 25, 13, 2.1, '#F2C6A5', shoe=('#FFFFFF', '#4A9A32', '#26262B'))
    return v, SIZE


def bombombini():
    """Bombombini Gusini — гусь-реактивный истребитель: треугольные крылья, ракеты, реактивное пламя."""
    v = new(23)
    white, grey, orange, jet = '#F5F7FA', '#9AA3B0', '#FF9A1F', '#5A6270'
    cx = 32
    v.ellipsoid(cx, 30, 22, 8, 15, 8, white)
    tri(v, (cx - 27, 21), (cx + 27, 21), (cx, 24), 'xz', 26, 36, grey)
    v.shape((0, 20, 20), (64, 42, 24),
            lambda X, Y, Z: (np.abs(X - cx) < 27 - (Y - 22) * 0.2 - np.abs(X - cx) * 0) & (np.abs(Z - 22) < 1.1)
            & (Y > 24 + np.abs(X - cx) * 0.5) & (Y < 38), grey)
    for s in (-1, 1):
        v.ellipsoid(cx + s * 15, 34, 19.5, 1.4, 5, 1.4, WHITE)
        v.ellipsoid(cx + s * 15, 28.5, 19.5, 1.2, 1.2, 1.2, '#E23B3B')
        v.line((cx + s * 4, 42, 22), (cx + s * 4, 46, 22), 2.6, jet)
        v.ellipsoid(cx + s * 4, 48.5, 22, 2, 2.5, 2, orange)
        v.ellipsoid(cx + s * 4, 50.5, 22, 1.2, 1.5, 1.2, '#FFE45C')
    fin_yz(v, (40, 28), (46, 28), (46, 37), cx - 0.8, cx + 0.8, grey)
    poly(v, [(cx, 21, 27), (cx, 17, 33), (cx, 16, 37)], 3.6, 3, white)
    v.ellipsoid(cx, 15, 40, 5, 5, 4.5, white)
    v.ellipsoid(cx, 9.5, 39, 2.5, 4, 1.6, orange)
    v.ellipsoid(cx, 9.5, 38, 2.2, 3.5, 0.9, '#E07A00')
    eyes(v, cx, 41.5, 2.5, r=1.4)
    v.ellipsoid(cx, 15, 43.5, 5.2, 5.2, 1.4, '#3E7B2A')   # лётный шлем
    for s in (-1, 1):
        v.ellipsoid(cx + s * 2.6, 11.5, 43.5, 1.8, 0.8, 1.3, '#46D6FF')
        v.line((cx + s * 4, 30, 16), (cx + s * 4, 30, 3), 1.2, orange)
        v.ellipsoid(cx + s * 4, 27, 1.2, 3, 4.5, 1.2, orange)
    return v, SIZE


CHARS_A = {
    'Cocofanto_Elefanto': ('Cocofanto Elefanto', cocofanto),
    'Dragon_Cannelloni': ('Dragon Cannelloni', dragon_cannelloni),
    'Draghetto_Gelato': ('Draghetto Gelato', draghetto_gelato),
    'Drakonino_Peperonino': ('Drakonino Peperonino', drakonino_peperonino),
    'Bombardiro_Crocodilo': ('Bombardiro Crocodilo', bombardiro),
    'Brr_Brr_Patapim': ('Brr Brr Patapim', patapim),
    'Lirili_Larila': ('Lirilì Larilà', lirili),
    'Cappuccino_Assassino': ('Cappuccino Assassino', cappuccino_assassino),
    'Ballerina_Cappuccina': ('Ballerina Cappuccina', ballerina),
    'Chimpanzini_Bananini': ('Chimpanzini Bananini', chimpanzini),
    'Trippi_Troppi': ('Trippi Troppi', trippi_troppi),
    'Boneca_Ambalabu': ('Boneca Ambalabu', boneca),
    'Bombombini_Gusini': ('Bombombini Gusini', bombombini),
}
