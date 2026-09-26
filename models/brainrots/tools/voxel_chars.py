"""Классические брейнроты в воксельном стиле. Каждая функция возвращает (Vox, размер вокселя в метрах)."""
import math

from voxel import Vox, shade

WHITE, BLACK = '#FFFFFF', '#15131C'


# ------------------------------------------------------------------ общие детали
def front_y(v, x, z):
    for y in range(v.g.shape[1]):
        if v.g[x, y, z] >= 0:
            return y
    return None


def eye(v, x, z, w=4, h=5, look=(0, 0), pupil=2, depth_out=1, white=WHITE):
    """Глаз, выступающий из передней поверхности: белок w×h, зрачок pupil×pupil, блик."""
    ys = [front_y(v, xx, zz) for xx in range(x, x + w) for zz in range(z - h + 1, z + 1)]
    ys = [y for y in ys if y is not None]
    y = min(ys) - depth_out
    v.box(x, x + w - 1, y, y + depth_out, z - h + 1, z, white)
    px = x + (w - pupil) // 2 + look[0]
    pz = z - (h - pupil) // 2 + look[1]
    v.box(px, px + pupil - 1, y - 1, y - 1, pz - pupil + 1, pz, BLACK)
    v.set(px, y - 1, pz, WHITE)  # блик


def outline(v, col, dark):
    """Затемнить края фигуры цвета col (как обводка в пиксель-арте)."""
    import numpy as np
    idx = v.c(col)
    g = v.g
    filled = g >= 0
    edge = np.zeros_like(filled)
    for axis in (0, 2):
        for s in (-1, 1):
            nb = np.roll(filled, s, axis=axis)
            if s == 1:
                sl = [slice(None)] * 3
                sl[axis] = 0
                nb[tuple(sl)] = False
            else:
                sl = [slice(None)] * 3
                sl[axis] = -1
                nb[tuple(sl)] = False
            edge |= filled & ~nb
    g[(g == idx) & edge] = v.c(dark)


def sneaker(v, x, y, z, main='#FFFFFF', accent='#2E6BFF', sole='#2A2A33', w=5, l=9):
    """Кроссовок: носок смотрит в -Y. (x, y, z) — центр пятки на полу."""
    x0 = x - w // 2
    v.box(x0, x0 + w - 1, y - l + 1, y, z, z, sole)                 # подошва
    v.box(x0, x0 + w - 1, y - l + 1, y, z + 1, z + 2, main)         # низ
    v.box(x0, x0 + w - 1, y - 3, y, z + 3, z + 4, main)             # задник/щиколотка
    v.box(x0, x0 + w - 1, y - l + 1, y - l + 2, z + 1, z + 1, sole)  # носок-резина
    v.box(x0 - 1, x0 - 1, y - l + 3, y - 1, z + 2, z + 2, accent)    # полоска слева
    v.box(x0 + w, x0 + w, y - l + 3, y - 1, z + 2, z + 2, accent)    # и справа
    v.box(x0 + 1, x0 + w - 2, y - 4, y - 3, z + 3, z + 3, accent)    # шнурки


# ------------------------------------------------------------------ 67
def digit_bitmap(ch, W=15, H=26, s=6):
    g = [[False] * W for _ in range(H)]

    def fill(x0, x1, r0, r1):
        for r in range(r0, r1 + 1):
            for x in range(x0, x1 + 1):
                if 0 <= r < H and 0 <= x < W:
                    g[r][x] = True

    if ch == '6':
        fill(0, s - 1, 1, H - 2)                  # левая стойка
        fill(1, W - 2, 0, s - 1)                  # верхняя перекладина
        fill(W - s, W - 1, 1, s + 1)              # крючок справа сверху
        fill(1, W - 2, H - 15, H - 15 + s - 1)    # верх петли
        fill(W - s, W - 1, H - 14, H - 2)         # правая стенка петли
        fill(1, W - 2, H - s, H - 1)              # низ (между ними — дырка 3×3)
    else:  # '7'
        fill(0, W - 1, 0, s - 1)
        for r in range(s, H):
            t = (r - s) / (H - 1 - s)
            xc = (W - 1 - s / 2) - t * (W - s - 3)
            fill(int(round(xc - s / 2)), int(round(xc + s / 2 - 1)), r, r)
    for r, x in ((0, 0), (0, W - 1), (H - 1, 0), (H - 1, W - 1)):
        g[r][x] = False
    return [''.join('#' if c else '.' for c in row) for row in g]


def six_seven():
    """67 — цифры 6 и 7 с глазами, руки в жесте «six-seven» (одна ладонь выше, другая ниже)."""
    v = Vox((62, 30, 56))
    main, dark, light = '#2EC5FF', '#1379C9', '#9BE8FF'
    y0, y1 = 10, 18
    ztop = 39
    x6, x7 = 10, 27
    v.bitmap(digit_bitmap('6'), x6, ztop, y0, y1, {'#': main})
    v.bitmap(digit_bitmap('7'), x7, ztop, y0, y1, {'#': main})
    outline(v, main, dark)
    for x0 in (x6, x7):
        v.box(x0 + 1, x0 + 13, y0, y0, ztop, ztop, light)
    eye(v, x6 + 2, ztop - 1, w=4, h=5, look=(1, 0))
    eye(v, x6 + 8, ztop - 1, w=4, h=5, look=(1, 0))
    eye(v, x7 + 3, ztop - 1, w=4, h=5, look=(-1, 0))
    eye(v, x7 + 9, ztop - 1, w=4, h=5, look=(-1, 0))
    my = front_y(v, x6 + 7, ztop - 23) - 1
    v.box(x6 + 3, x6 + 11, my, my, ztop - 22, ztop - 22, '#5A1027')
    v.box(x6 + 4, x6 + 10, my, my, ztop - 23, ztop - 23, '#5A1027')
    v.box(x6 + 5, x6 + 9, my, my, ztop - 24, ztop - 24, '#FF6F91')
    # руки: 6 — ладонь вверх слева, 7 — ладонь вниз справа
    v.line((x6, 14, 30), (3, 14, 36), 1.7, main)
    v.ellipsoid(2.5, 14, 37.5, 3, 2.8, 2.4, WHITE)
    v.line((x7 + 15, 14, 33), (51, 14, 26), 1.7, main)
    v.ellipsoid(52, 14, 25, 3, 2.8, 2.4, WHITE)
    for x in (x6 + 7, x7 + 5):
        v.line((x, 14, 15), (x, 14, 4), 1.9, main)
        sneaker(v, x, 18, 0, main=WHITE, accent=main, w=6, l=10)
    return v, 0.035


# ------------------------------------------------------------------ Тунг Тунг Тунг Сахур
def tung_sahur():
    """Тунг Тунг Тунг Сахур — деревянное бревно с огромными глазами и бейсбольной битой."""
    v = Vox((60, 30, 64), seed=3)
    wood, bark_d, top = '#C68A4E', '#9C6532', '#E3B77F'
    cx, cy = 22, 13
    v.cyl_z(cx, cy, 12, 44, 8.5, 7.5, wood)
    v.noise(wood, [shade(wood, -0.08), shade(wood, 0.07)], chance=0.35)
    # вертикальные волокна коры
    for x in range(cx - 9, cx + 10):
        if x % 4 == 0:
            for z in range(12, 45):
                if (z * 7 + x) % 11 < 8:
                    for y in range(v.g.shape[1]):
                        if v.g[x, y, z] >= 0:
                            v.set(x, y, z, bark_d)
                            break
    # годичные кольца на срезе сверху
    for x in range(cx - 9, cx + 10):
        for y in range(cy - 9, cy + 10):
            if v.get(x, y, 44):
                r = math.hypot((x + .5 - cx) / 8.5, (y + .5 - cy) / 7.5)
                v.set(x, y, 44, bark_d if r > 0.85 or int(r * 6) % 2 else top)
    # лицо: огромные глаза-блюдца, густые брови, маленький рот
    eye(v, 14, 37, w=6, h=6, pupil=2, look=(1, 0))
    eye(v, 23, 37, w=6, h=6, pupil=2, look=(-1, 0))
    for x0, slope in ((14, 1), (23, -1)):
        yb = front_y(v, x0 + 2, 39) - 1
        for i in range(6):
            v.box(x0 + i, x0 + i, yb, yb, 39 + (i * slope) // 3 + (1 if slope < 0 else 0),
                  40 + (i * slope) // 3 + (1 if slope < 0 else 0), '#3A2412')
    my = front_y(v, 22, 26) - 1
    v.box(19, 25, my, my, 26, 26, '#3A2412')
    # руки-палки; правая держит биту над головой
    limb = shade(wood, -0.05)
    v.line((13, cy, 30), (7, cy - 1, 20), 1.3, limb)
    v.ellipsoid(6.5, cy - 1, 19, 2, 2, 2, limb)
    v.line((31, cy, 32), (37, cy - 1, 40), 1.3, limb)
    v.ellipsoid(37.5, cy - 1, 41, 2, 2, 2, limb)
    bat = '#E8C890'
    n = 18
    for i in range(n + 1):
        t = i / n
        p = (37 + t * 9, cy - 1 - t * 1, 40 + t * 20)
        v.ellipsoid(*p, 1.1 + 1.6 * t, 1.1 + 1.6 * t, 1.1 + 1.6 * t, bat)
    v.ellipsoid(37, cy - 1, 39, 1.8, 1.8, 1.0, shade(bat, -0.25))  # набалдашник
    # ноги-палки и ступни
    for x in (18, 26):
        v.line((x, cy, 13), (x, cy, 3), 1.4, limb)
        v.box(x - 2, x + 2, cy - 4, cy + 1, 0, 2, shade(wood, -0.15))
    return v, 0.028


# ------------------------------------------------------------------ Тралалеро Тралала
def tralalero():
    """Тралалеро Тралала — акула на трёх ногах в синих кроссовках."""
    v = Vox((64, 28, 50), seed=5)
    skin, belly, dark = '#5E8FC7', '#EEF3F8', '#3B6597'
    cx, cy, cz = 32, 13, 27
    # тело: вытянутый эллипсоид, нос заострён (сужаем переднюю часть)
    for x in range(8, 58):
        t = (x - 8) / 50
        # профиль: заострённый нос → самое толстое место на трети длины → сужение к хвосту
        prof = math.sin(math.pi / 2 * t / 0.35) ** 0.6 if t < 0.35 else 1 - 0.72 * ((t - 0.35) / 0.65) ** 1.4
        ry, rz = 8.5 * prof, 9.5 * prof
        zc = cz + (1.5 if t < 0.3 else 0)
        for y in range(0, 28):
            for z in range(10, 45):
                if ((y + .5 - cy) / max(ry, .5)) ** 2 + ((z + .5 - zc) / max(rz, .5)) ** 2 <= 1:
                    v.set(x, y, z, belly if z < zc - 2.5 else skin)
    # затемнение спины
    for x in range(8, 58):
        for y in range(28):
            for z in range(44, 20, -1):
                if v.get(x, y, z):
                    v.set(x, y, z, dark)
                    break
    # спинной плавник
    for i in range(10):
        v.box(28 + i // 2, 36 - i // 3, cy - 1, cy + 1, 36 + i, 36 + i, dark)
    # хвост-полумесяц
    for i in range(12):
        v.box(56 + i // 3, 58 + i // 3, cy - 1, cy + 1, 28 + i, 28 + i, dark)
        v.box(56 + i // 4, 58 + i // 4, cy - 1, cy + 1, 26 - i // 2, 26 - i // 2, skin)
    # грудные плавники
    for s in (-1, 1):
        y = cy + s * 9
        for i in range(6):
            v.box(22 + i, 24 + i, y + s * (i // 3), y + s * (i // 3), 22 - i, 22 - i, skin)
    # глаза с двух сторон, пасть с зубами
    for y, s in ((cy - 7, -1), (cy + 7, 1)):
        for yy in (y, y + s):
            v.box(15, 17, yy + s, yy + s, 30, 32, WHITE)
        v.box(15, 16, y + 2 * s, y + 2 * s, 30, 31, BLACK)
        v.set(16, y + 2 * s, 31, WHITE)
    for x in range(9, 21):
        for y in range(28):
            if v.get(x, y, 23):
                v.set(x, y, 23, '#5A1027')
                if x % 2 == 0:
                    v.set(x, y, 24, WHITE)
    # три ноги в кроссовках
    for x in (20, 32, 44):
        v.line((x, cy, 18), (x, cy, 4), 1.8, skin)
        sneaker(v, x, cy + 4, 0, main='#2E6BFF', accent=WHITE, sole=WHITE)
    return v, 0.03


VOX_CHARACTERS = {
    'SixSeven_67': ('67 (Six Seven)', six_seven),
    'Tung_Tung_Tung_Sahur': ('Тунг Тунг Тунг Сахур', tung_sahur),
    'Tralalero_Tralala': ('Тралалеро Тралала', tralalero),
}
