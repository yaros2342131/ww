"""Брейнроты, группа C."""
import math

import numpy as np

from parts import (SIZE, arm, blush, brow, cone, dots, eye3, eye_at, eyes, fin_yz, fy, legs2, legs4, new, nose,
                   poly, smile, teeth, tri, whiskers)
from voxel import shade
from voxel_chars import BLACK, WHITE


def talpa():
    """Talpa Di Ferro — крот с железным буром на голове, розовым носом и лапами-лопатами."""
    v = new(51)
    fur, fur_d, steel, steel_d, pinkc, gold = '#6E5A4E', '#4E3F36', '#B8C0CC', '#7E8896', '#FF8FA3', '#E8B83A'
    cx = 32
    v.ellipsoid(cx, 25, 22, 11, 10, 14, fur)
    v.paint((cx - 12, 14, 7), (cx + 12, 36, 37), lambda X, Y, Z: (Y < 19) & (Z < 24), shade(fur, 0.15))
    v.cyl_z(cx, 25, 33, 36, 7, 7, gold)
    v.line((cx, 25, 36), (cx, 25, 53), 6.5, steel, r1=0.4)
    v.paint((cx - 8, 17, 35), (cx + 8, 33, 54),
            lambda X, Y, Z: np.sin(np.arctan2(Y - 25, X - cx) + Z * 0.9) > 0.45, steel_d)
    v.ellipsoid(cx, 12.5, 25, 2.6, 2, 2.2, pinkc)
    for s in (-1, 1):
        eye3(v, cx + s * 3.5, fy(v, cx + s * 3.5, 29) + 0.2, 29, 1.2, look=(0, 0))
        v.ellipsoid(cx + s * 13, 16, 21, 4.2, 2.6, 3.2, pinkc)       # лапы-лопаты
        for t in (-1, 0, 1):
            v.line((cx + s * 13 + t * 1.8, 14, 19), (cx + s * 13 + t * 2.4, 12, 16.5), 0.55, '#F5F0E6')
        v.line((cx + s * 10, 25, 22), (cx + s * 12.5, 18, 21), 1.8, fur)
        v.line((cx + s * 5, 25, 9), (cx + s * 5, 24, 3), 2.2, fur)
        v.ellipsoid(cx + s * 5, 21.5, 1.5, 2.8, 4, 1.5, pinkc)
    whiskers(v, cx, 25, '#2A2A2A', 0.35, 5)
    teeth(v, cx, 22, 2.6, n=2, h=1.8)
    return v, SIZE


def rhino_toasterino():
    """Rhino Toasterino — носорог-тостер: хромированный тостер с тостами, голова носорога с рогом."""
    v = new(52)
    chrome, chrome_d, toast, toast_d, rhino, rhino_d = '#C9CFD8', '#8E96A3', '#E3A857', '#B87A33', '#8A8F99', '#5E636C'
    cx = 32
    v.box(21, 43, 20, 36, 12, 32, chrome)
    v.paint((19, 18, 10), (45, 38, 34), lambda X, Y, Z: (Z > 27.5) & (Z < 28.5), chrome_d)
    for y0 in (24, 30):
        v.box(25, 39, y0, y0 + 2, 29, 33, None)
        v.box(26, 38, y0, y0 + 2, 26, 36, toast)
        v.paint((25, y0 - 1, 34), (39, y0 + 3, 37), lambda X, Y, Z: Z > 34.8, toast_d)
    v.box(44, 45, 26, 29, 18, 27, chrome_d)
    v.box(44, 46, 26, 29, 25, 27, BLACK)
    v.ellipsoid(cx, 14, 24, 7.5, 7.5, 6.5, rhino)
    v.ellipsoid(cx, 8, 22, 5.5, 3.5, 4.5, rhino)
    cone(v, (cx, 6, 25), (cx, 2.5, 34), 2.4, '#F5E6C8')
    cone(v, (cx, 9, 28), (cx, 7.5, 31.5), 1.4, '#F5E6C8')
    for s in (-1, 1):
        v.ellipsoid(cx + s * 1.8, 4.8, 21, 0.6, 0.5, 0.8, rhino_d)
        eye3(v, cx + s * 4.2, fy(v, cx + s * 4.2, 27) + 0.3, 27, 1.3, lid=rhino_d, lid_amount=0.35)
        tri(v, (cx + s * 4, 29), (cx + s * 7.5, 28.5), (cx + s * 7, 33), 'xz', 16, 18, rhino)
    smile(v, cx, 20, 4, 0.6, rhino_d, 0.45)
    legs4(v, [(24, 23), (40, 23), (24, 33), (40, 33)], 13, 2.6, rhino, hoof=rhino_d, foot_r=2.8)
    return v, SIZE


def blueberrinni():
    """Blueberrinni Octopussini — осьминог-черника: тёмно-синяя ягода с «короной» и восемью щупальцами."""
    v = new(53)
    berry, bloom, crown, tent = '#3B4BB5', '#6A7BE0', '#1E2A70', '#5566D0'
    cx, cy, cz = 32, 25, 25
    for i in range(8):
        ang = i * 2 * math.pi / 8 + 0.4
        pts = []
        for t in np.linspace(0, 1, 7):
            rr = 7 + t * 9
            z = cz - 6 - t * 14 + (t ** 3) * 8
            pts.append((cx + math.cos(ang + t * 0.8) * rr, cy + math.sin(ang + t * 0.8) * rr, max(1.5, z)))
        poly(v, pts, 2.6, 0.9, tent)
    v.ellipsoid(cx, cy, cz, 12, 12, 11.5, berry)
    v.paint((cx - 13, cy - 13, cz - 13), (cx + 13, cy + 13, cz + 13),
            lambda X, Y, Z: np.sin(X * 0.7 + Z * 0.5) * np.sin(Y * 0.6 - Z * 0.4) > 0.55, bloom)
    for a in range(5):
        ang = a * 2 * math.pi / 5
        tri(v, (cx, cy), (cx + math.cos(ang - 0.35) * 5, cy + math.sin(ang - 0.35) * 5),
            (cx + math.cos(ang) * 6.5, cy + math.sin(ang) * 6.5), 'xy', cz + 10.5, cz + 12.3, crown)
    v.ellipsoid(cx, cy, cz + 11, 2.2, 2.2, 1.2, crown)
    eyes(v, cx, cz + 2, 4.2, r=2.6, look=(0, -0.2))
    blush(v, cx, cz - 2.5, 7, r=1.5)
    smile(v, cx, cz - 3.5, 4, 1.1, '#1A1040', 0.55)
    return v, SIZE


def girafa_celestre():
    """Girafa Celestre — жираф-космонавт: белый скафандр, ранец, пятнистая шея и рожки."""
    v = new(54)
    suit, suit_d, gir, spot, visor = '#F2F4FA', '#B8C0D6', '#F4C542', '#A0622D', '#46D6FF'
    cx = 32
    v.box(cx - 5, cx + 5, 30, 34, 15, 29, suit_d)       # ранец
    v.ellipsoid(cx, 25, 22, 8.5, 7.5, 10, suit)
    v.ellipsoid(cx, fy(v, cx, 25) + 0.6, 25, 2.4, 0.7, 2.4, '#2E6BFF')
    v.ellipsoid(cx, fy(v, cx, 25) + 0.1, 25, 1.2, 0.5, 1.2, WHITE)
    v.cyl_z(cx, 24, 30.5, 33, 5, 5, suit_d)
    poly(v, [(cx, 24, 31), (cx, 23, 38), (cx, 21, 46)], 3.5, 3, gir)
    v.paint((cx - 5, 17, 32), (cx + 5, 29, 48),
            lambda X, Y, Z: np.sin(X * 1.3 + Z * 0.8) * np.sin(Y * 1.1 + Z * 1.2) > 0.4, spot)
    v.ellipsoid(cx, 18, 49, 4.5, 6, 4, gir)
    v.ellipsoid(cx, 13, 47.8, 3.4, 2.4, 2.6, '#F7DCA0')
    for s in (-1, 1):
        v.ellipsoid(cx + s * 1.3, 10.8, 48.4, 0.5, 0.4, 0.5, spot)
        v.line((cx + s * 1.8, 20, 52), (cx + s * 2.2, 20.5, 56), 0.7, gir)
        v.ellipsoid(cx + s * 2.2, 20.5, 56.5, 1.1, 1.1, 1.1, spot)
        v.ellipsoid(cx + s * 5.2, 20, 51, 1.8, 0.8, 1, gir)
    eyes(v, cx, 51, 2.5, r=1.3, look=(0, 0.2))
    smile(v, cx, 46.6, 2.2, 0.5, spot, 0.35)
    for s in (-1, 1):
        arm(v, (cx + s * 7.5, 25, 27), (cx + s * 12, 19, 20), 1.8, suit, hand=suit_d, hand_r=2.2)
        v.ellipsoid(cx + s * 12, 18, 23.5, 2, 1, 1, visor)
    legs2(v, (cx - 4, cx + 4), 25, 13, 2.3, suit, shoe=(suit_d, '#2E6BFF', '#5A5F6E'))
    return v, SIZE


def cacto_hipopotamo():
    """Cacto Hipopotamo — бегемот-кактус: зелёный ребристый, с колючками, розовым цветком и огромной пастью."""
    v = new(55)
    cac, cac_d, mouth, pinkc = '#5BAA4A', '#3A7A2E', '#8A1E3A', '#FF5FA2'
    cx = 32
    legs4(v, [(23, 25), (41, 25), (23, 38), (41, 38)], 12, 3.2, cac, hoof=cac_d, foot_r=3.4)
    v.ellipsoid(cx, 30, 20, 13, 14, 11, cac)
    v.paint((cx - 14, 15, 8), (cx + 14, 45, 32),
            lambda X, Y, Z: np.sin(np.arctan2(Z - 20, X - cx) * 9) > 0.7, cac_d)
    v.ellipsoid(cx, 13, 24, 10, 8, 8, shade(cac, 0.12))
    v.ellipsoid(cx, 5.5, 20.5, 7, 2.2, 3.4, mouth)
    v.ellipsoid(cx, 5, 19, 4, 1.2, 1.4, '#FF6F91')
    for s in (-1, 1):
        v.ellipsoid(cx + s * 4, 4.5, 23.4, 1.1, 0.9, 1.6, WHITE)
        v.ellipsoid(cx + s * 3, 7, 29.5, 1, 0.8, 0.8, cac_d)
        v.ellipsoid(cx + s * 5, 14, 31, 2.6, 2.6, 2.4, shade(cac, 0.12))
        eye3(v, cx + s * 5, 12, 31.8, 1.8, look=(0, 0))
        v.ellipsoid(cx + s * 8.5, 17, 32, 1.6, 1, 1.4, cac)
    dots(v, (cx, 30, 20), (13, 14, 11), 20, ['#F5F5DC'], r=0.45, seed=9, front=False, zmin=16)
    for a in range(6):
        ang = a * 2 * math.pi / 6
        v.ellipsoid(cx + math.cos(ang) * 2.2, 30 + math.sin(ang) * 2.2, 31.5, 1.8, 1.8, 1.1, pinkc)
    v.ellipsoid(cx, 30, 32.2, 1.2, 1.2, 0.8, '#FFD23F')
    return v, SIZE


def strawberrelli():
    """Strawberrelli Flamingelli — фламинго-клубника: клубничное тело с семечками, розовая шея и одна нога."""
    v = new(56)
    straw, seed_c, leaf, pinkf, pink_d = '#E8384F', '#FFE08A', '#3FA34D', '#FF8CB3', '#E0668F'
    cx = 32
    v.line((cx - 2, 26, 20), (cx - 2, 26, 1.5), 0.9, pinkf)
    v.ellipsoid(cx - 2, 24, 1, 2, 3, 0.8, pink_d)
    poly(v, [(cx + 2, 26, 20), (cx + 5, 24, 13), (cx + 1, 25, 11)], 0.9, 0.8, pinkf)
    v.shape((cx - 11, 15, 17), (cx + 11, 37, 42),
            lambda X, Y, Z: ((X - cx) / (5 + (Z - 17) * 0.24)) ** 2 + ((Y - 26) / (4.5 + (Z - 17) * 0.22)) ** 2
            + ((Z - 31) / 11) ** 8 <= 1, straw)
    dots(v, (cx, 26, 30), (8.8, 8.3, 11), 26, [seed_c], r=0.5, seed=10, front=False, zmin=19, zmax=39)
    for a in range(6):
        ang = a * 2 * math.pi / 6
        tri(v, (cx, 26), (cx + math.cos(ang - 0.4) * 5, 26 + math.sin(ang - 0.4) * 5),
            (cx + math.cos(ang) * 8, 26 + math.sin(ang) * 8), 'xy', 40.5, 41.8, leaf)
    for s in (-1, 1):
        v.ellipsoid(cx + s * 9, 27, 31, 1.6, 5, 4, pinkf)
    poly(v, [(cx, 22, 38), (cx, 18, 44), (cx, 20, 50), (cx, 17, 55)], 1.8, 1.6, pinkf)
    v.ellipsoid(cx, 15, 56, 3.4, 4.2, 3, pinkf)
    poly(v, [(cx, 11.5, 56), (cx, 9, 54.5), (cx, 8, 52)], 1.3, 0.7, WHITE)
    v.ellipsoid(cx, 7.9, 51.5, 0.8, 0.8, 0.9, BLACK)
    eyes(v, cx, 57, 2.3, r=1.2, lid=pink_d, lid_amount=0.3)
    return v, SIZE


def trulimero():
    """Trulimero Trulicina — золотая рыбка с кошачьей мордой и человеческими ногами в кроссовках."""
    v = new(57)
    fish, fish_d, cat, fin = '#FF9F1C', '#E07A00', '#FFE3B3', '#FFC266'
    cx = 32
    legs2(v, (cx - 4, cx + 4), 27, 16, 2, '#F2C6A5', shoe=('#FFFFFF', '#FF9F1C', '#26262B'))
    v.ellipsoid(cx, 27, 26, 10, 14, 9.5, fish)
    v.paint((cx - 11, 12, 16), (cx + 11, 42, 36),
            lambda X, Y, Z: (np.abs(np.sin(Y * 0.9 + np.abs(Z - 26) * 0.6)) < 0.18) & (Y > 18), fish_d)
    tri(v, (38, 26), (49, 18), (49, 34), 'yz', cx - 0.9, cx + 0.9, fin)
    tri(v, (22, 34), (33, 34), (29, 40), 'yz', cx - 0.8, cx + 0.8, fin)
    for s in (-1, 1):
        v.ellipsoid(cx + s * 10, 26, 22, 1.4, 4, 2.4, fin)
    v.ellipsoid(cx, 14, 28, 7.5, 6, 6.5, cat)
    for s in (-1, 1):
        tri(v, (cx + s * 2.5, 32.5), (cx + s * 7.5, 31.5), (cx + s * 6.5, 38.5), 'xz', 13, 16, cat)
        tri(v, (cx + s * 3.5, 33), (cx + s * 6.8, 32.5), (cx + s * 6.2, 37), 'xz', 12.3, 13.1, '#FF9EB5')
    eyes(v, cx, 30, 3.2, r=2, iris='#2FA4FF', slit=True)
    nose(v, cx, 27, 0.8, '#FF6F91')
    smile(v, cx, 25.8, 3.4, 0.8, '#5A2020', 0.45)
    whiskers(v, cx, 26.8, '#8A6A4A', 0.35)
    return v, SIZE


def pandaccini():
    """Pandaccini Bananini — панда с огромным бананом в лапах, как с телефоном."""
    v = new(58)
    white, black, yel, yel_d = '#F7F7F7', '#1E1E26', '#FFD93B', '#6B4A2E'
    cx = 32
    for s in (-1, 1):
        v.ellipsoid(cx + s * 7, 22, 5, 4, 5.5, 4, black)
        v.ellipsoid(cx + s * 7, 17, 5, 2.2, 0.8, 2.2, '#FF9EB5')
    v.ellipsoid(cx, 26, 17, 11.5, 10.5, 12, white)
    v.paint((cx - 12, 15, 22), (cx + 12, 37, 30), lambda X, Y, Z: Z > 23, black)
    v.ellipsoid(cx, 24, 35, 9, 8, 8, white)
    for s in (-1, 1):
        v.ellipsoid(cx + s * 7.5, 25, 42, 3, 2, 3, black)
        v.ellipsoid(cx + s * 3.6, fy(v, cx + s * 3.6, 36) + 0.5, 36, 2.6, 1, 3.2, black)
        eye3(v, cx + s * 3.6, fy(v, cx + s * 3.6, 36.5) - 0.2, 36.5, 1.4, look=(0.2 * -s, 0))
    nose(v, cx, 32.5, 1.2, black)
    smile(v, cx, 31.2, 3, 0.7, black, 0.4)
    blush(v, cx, 32.5, 6, r=1.3)
    for s in (-1, 1):
        arm(v, (cx + s * 9, 24, 24), (cx + s * 5, 14, 22), 2.4, black, hand=black, hand_r=2.8)
    poly(v, [(cx - 11, 12, 18), (cx - 5, 11, 22.5), (cx + 3, 11, 25), (cx + 11, 12, 24)], 2.6, 2.2, yel)
    v.ellipsoid(cx - 11.5, 12, 17.5, 1, 1, 1, yel_d)
    v.ellipsoid(cx + 11.8, 12, 24, 1, 1, 1, yel_d)
    return v, SIZE


def salamino_penguino():
    """Salamino Penguino — пингвин-салями: колбаска с кусочками сала, перетянутая шпагатом, клюв и ласты."""
    v = new(59)
    sal, fat, twine, black, orange = '#A8323E', '#F5E1D6', '#D9C49A', '#1E1E26', '#FF9F1C'
    cx = 32
    for s in (-1, 1):
        v.ellipsoid(cx + s * 4, 21, 1.2, 2.8, 4.5, 1.2, orange)
        v.line((cx + s * 4, 24, 8), (cx + s * 4, 22, 1.5), 1.4, orange)   # ножки
    v.ellipsoid(cx, 25, 22, 9, 8, 17, sal)
    dots(v, (cx, 25, 20), (9, 8, 14), 30, [fat, shade(fat, -0.1)], r=0.8, seed=11, front=False, zmax=32)
    v.paint((cx - 10, 16, 5), (cx + 10, 34, 40), lambda X, Y, Z: np.abs(np.sin(Z * 0.55)) < 0.12, twine)
    v.paint((cx - 10, 16, 32), (cx + 10, 34, 42), lambda X, Y, Z: Z > 33, black)
    v.paint((cx - 10, 16, 30), (cx + 10, 22, 40),
            lambda X, Y, Z: (Y < 20) & ((X - cx) ** 2 / 30 + (Z - 34) ** 2 / 18 < 1), WHITE)
    v.ellipsoid(cx, fy(v, cx, 33) - 1.2, 33, 2.2, 2.6, 1.3, orange)
    eyes(v, cx, 35.5, 2.8, r=1.5)
    blush(v, cx, 32.5, 4.8, r=1.1)
    for s in (-1, 1):
        poly(v, [(cx + s * 8, 25, 28), (cx + s * 12, 24, 22), (cx + s * 13, 23, 16)], 2, 1.2, black)
    v.line((cx, 25, 41), (cx, 25, 44), 0.5, twine)
    return v, SIZE


def bananita_dolphinita():
    """Bananita Dolphinita — дельфин-банан: жёлтое изогнутое тело, серо-голубая голова и хвост-плавник."""
    v = new(60)
    yel, yel_d, dol, dol_d = '#FFD93B', '#C9A21A', '#6C9BD2', '#4A78B0'
    cx = 32
    tri(v, (cx - 9, 1), (cx + 9, 1), (cx, 6), 'xz', 28, 31, dol)
    tri(v, (cx - 9, 1), (cx - 4, 1), (cx - 11, 5), 'xz', 28, 31, dol)
    tri(v, (cx + 9, 1), (cx + 4, 1), (cx + 11, 5), 'xz', 28, 31, dol)
    poly(v, [(cx, 30, 5), (cx, 27, 12), (cx, 24, 22), (cx, 24, 33), (cx, 25, 41)], 3, 8.5, yel)
    v.paint((cx - 10, 14, 4), (cx + 10, 36, 46),
            lambda X, Y, Z: np.abs(np.sin(np.arctan2(Y - 25, X - cx) * 2.5)) < 0.1, yel_d)
    v.ellipsoid(cx, 22, 45, 7, 7.5, 6.5, dol)
    v.ellipsoid(cx, 13, 43.5, 3.2, 5, 2.6, dol)
    v.paint((cx - 8, 8, 38), (cx + 8, 30, 46),
            lambda X, Y, Z: (Z < 42.5) & (Y < 21) & (((X - cx) / 7) ** 2 + ((Y - 22) / 7.5) ** 2 + ((Z - 45) / 6.5) ** 2 <= 1.15
                                                | (((X - cx) / 3.2) ** 2 + ((Y - 13) / 5) ** 2 + ((Z - 43.5) / 2.6) ** 2 <= 1.15)),
            shade(dol, 0.3))
    fin_yz(v, (27, 44), (33, 42), (33, 53), cx - 0.9, cx + 0.9, dol_d)
    for s in (-1, 1):
        tri(v, (cx + s * 7, 30), (cx + s * 7, 24), (cx + s * 14, 23), 'xz', 24, 26.5, dol)
    eyes(v, cx, 47.5, 3.3, r=1.7, look=(0, 0.1))
    smile(v, cx, 42.8, 4.5, 0.8, dol_d, 0.5)
    blush(v, cx, 44, 5.6, r=1)
    return v, SIZE


def spaghetti_tualetti():
    """Spaghetti Tualetti — унитаз со спагетти вместо волос, фрикаделькой и томатным соусом."""
    v = new(61)
    porc, porc_d, pasta, sauce, meat = '#F4F6FA', '#C9CFD8', '#F2D48A', '#C8261E', '#7A3E1E'
    cx = 32
    v.cyl_z(cx, 27, 0, 10, 5.5, 5, porc)
    v.ellipsoid(cx, 25, 15, 11, 12, 6.5, porc)
    v.ellipsoid(cx, 24, 18, 8.5, 9.5, 4, None)
    v.box(18, 46, 10, 40, 19, 25, None)
    v.shape((cx - 12, 12, 17), (cx + 12, 38, 20),
            lambda X, Y, Z: ((X - cx) / 11) ** 2 + ((Y - 25) / 12) ** 2 <= 1, porc_d)
    v.ellipsoid(cx, 24, 18, 8.3, 9.3, 1.5, None)
    v.box(23, 41, 34, 40, 16, 38, porc)
    v.box(22, 42, 33, 41, 38, 40, porc_d)
    v.ellipsoid(cx + 6, 33, 36, 1.4, 0.8, 1, '#A0A8B4')
    rnd = np.random.RandomState(3)
    for i in range(16):
        ang = rnd.uniform(-math.pi, 0.2)
        r0 = rnd.uniform(0, 5)
        p0 = (cx + math.cos(ang) * r0, 24 + math.sin(ang) * r0, 18)
        edge = (cx + math.cos(ang) * 10.5, 24 + math.sin(ang) * 11.5, 20)
        end = (cx + math.cos(ang) * 12, 24 + math.sin(ang) * 13, 20 - rnd.uniform(4, 10))
        poly(v, [p0, (p0[0], p0[1], 21), edge, end], 0.75, 0.7, pasta)
    v.ellipsoid(cx, 24, 20, 8, 9, 2.2, pasta)
    v.ellipsoid(cx - 1, 23, 22.5, 4, 4, 1.5, sauce)
    v.ellipsoid(cx, 23, 24.5, 2.8, 2.8, 2.6, meat)
    v.ellipsoid(cx + 1.5, 22, 27.2, 1, 1, 0.8, '#3FA34D')
    eye3(v, cx - 3.6, 32.2, 31, 2, look=(0, -0.3))
    eye3(v, cx + 3.6, 32.2, 31, 2, look=(0, -0.3))
    v.ellipsoid(cx, 32.6, 26.5, 2.8, 0.8, 1.2, '#5A1020')
    blush(v, cx, 27.5, 6, r=1.2)
    return v, SIZE


def spioniro_golubiro():
    """Spioniro Golubiro — голубь-шпион: солнечные очки, шляпа-федора, переливчатая шея."""
    v = new(62)
    grey, grey_l, grey_d, green, purple, orange = '#8C95A5', '#B8C0CC', '#5E6878', '#3FA37A', '#7A4FB0', '#FF7A45'
    cx = 32
    for s in (-1, 1):
        v.line((cx + s * 3.5, 26, 11), (cx + s * 3.5, 25, 2), 0.8, orange)
        for a in (-0.6, 0, 0.6):
            v.line((cx + s * 3.5, 25, 1), (cx + s * 3.5 + math.sin(a) * 2.5, 25 - math.cos(a) * 2.5, 0.8), 0.45, orange)
    v.ellipsoid(cx, 27, 20, 10, 12, 10.5, grey)
    v.paint((cx - 11, 14, 9), (cx + 11, 40, 31), lambda X, Y, Z: (Y < 22) & (Z < 22), grey_l)
    for s in (-1, 1):
        v.ellipsoid(cx + s * 9, 29, 21, 2.2, 9, 6, grey_d)
        v.paint((cx + s * 9 - 3, 20, 14), (cx + s * 9 + 3, 38, 28),
                lambda X, Y, Z: (np.abs(Y - 30) < 0.8) | (np.abs(Y - 33) < 0.8), BLACK)
    v.ellipsoid(cx, 22, 30, 6.5, 6.5, 4, green)
    v.paint((cx - 7, 15, 26), (cx + 7, 29, 34), lambda X, Y, Z: np.sin(X * 0.9 + Z * 1.1) > 0.2, purple)
    v.ellipsoid(cx, 20, 36, 6, 6, 5.5, grey)
    v.ellipsoid(cx, 13.5, 35, 1.6, 2.6, 1.3, '#3A3A42')
    v.ellipsoid(cx, 15.5, 36, 1.2, 1, 0.8, WHITE)
    y = fy(v, cx, 37.5)
    for s in (-1, 1):
        v.ellipsoid(cx + s * 2.8, y - 0.2, 37.5, 2.5, 0.8, 1.8, BLACK)
        v.ellipsoid(cx + s * 2.3, y - 0.9, 38.2, 0.6, 0.3, 0.4, '#9CA8FF')
    v.line((cx - 0.8, y - 0.5, 38), (cx + 0.8, y - 0.5, 38), 0.4, BLACK)
    v.ellipsoid(cx, 20, 41, 7.5, 7.5, 0.9, '#4A3A2A')
    v.cyl_z(cx, 20, 41, 45, 4.5, 4.5, '#4A3A2A')
    v.ellipsoid(cx, 20, 45, 4.5, 4.5, 1, '#4A3A2A')
    v.paint((cx - 5, 15, 41), (cx + 5, 25, 43), lambda X, Y, Z: Z < 42.8, BLACK)
    smile(v, cx, 32.5, 2.4, 0.5, BLACK, 0.35)
    return v, SIZE


CHARS_C = {
    'Talpa_Di_Ferro': ('Talpa Di Ferro', talpa),
    'Rhino_Toasterino': ('Rhino Toasterino', rhino_toasterino),
    'Blueberrinni_Octopussini': ('Blueberrinni Octopussini', blueberrinni),
    'Girafa_Celestre': ('Girafa Celestre', girafa_celestre),
    'Cacto_Hipopotamo': ('Cacto Hipopotamo', cacto_hipopotamo),
    'Strawberrelli_Flamingelli': ('Strawberrelli Flamingelli', strawberrelli),
    'Trulimero_Trulicina': ('Trulimero Trulicina', trulimero),
    'Pandaccini_Bananini': ('Pandaccini Bananini', pandaccini),
    'Salamino_Penguino': ('Salamino Penguino', salamino_penguino),
    'Bananita_Dolphinita': ('Bananita Dolphinita', bananita_dolphinita),
    'Spaghetti_Tualetti': ('Spaghetti Tualetti', spaghetti_tualetti),
    'Spioniro_Golubiro': ('Spioniro Golubiro', spioniro_golubiro),
}
