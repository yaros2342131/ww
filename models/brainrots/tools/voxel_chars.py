"""Классические брейнроты в воксельном стиле. Каждая функция возвращает (Vox, размер вокселя в метрах)."""
import math

from voxel import Vox, shade

WHITE, BLACK = '#FFFFFF', '#15131C'


# ------------------------------------------------------------------ общие детали
K = 3  # детализация сетки: 1 — пиксельный стиль, 3 — для гладких моделей


def front_y(v, x, z):
    return v.front_y(x, z)


def eye(v, x, z, w=4, h=5, look=(0, 0), pupil=2, depth_out=1, white=WHITE):
    """Круглый глаз, выступающий из передней поверхности: белок w×h, зрачок, блик.
    (x, z) — левый верхний угол глаза в дизайн-координатах."""
    ys = [front_y(v, xx, zz) for xx in range(x, x + w) for zz in range(z - h + 1, z + 1)]
    ys = [y for y in ys if y is not None]
    y = min(ys)
    cx, cz = x + w / 2, z - h / 2 + 1
    v.ellipsoid(cx, y + 0.6, cz, w / 2 + 0.2, 1.3 + depth_out * 0.4, h / 2 + 0.2, white)
    px, pz = cx + look[0] * 0.6, cz + look[1] * 0.6
    v.ellipsoid(px, y - 0.55, pz, pupil / 2 + 0.25, 0.7, pupil / 2 + 0.4, BLACK)
    v.ellipsoid(px - 0.35, y - 0.9, pz + 0.45, 0.4, 0.4, 0.4, WHITE)  # блик


def mouth(v, cx, cz, w, h, color='#5A1027', tongue='#FF6F91'):
    """Открытый рот-улыбка на передней поверхности."""
    y = min(yy for yy in (front_y(v, int(cx + dx), int(cz)) for dx in (-1, 0, 1)) if yy is not None)
    v.ellipsoid(cx, y + 0.3, cz, w / 2, 0.9, h / 2, color)
    if tongue:
        v.ellipsoid(cx, y - 0.1, cz - h * 0.2, w * 0.28, 0.6, h * 0.28, tongue)


def outline(v, col, dark):
    """Затемнить края фигуры цвета col (толщина — один дизайн-воксель)."""
    import numpy as np
    idx = v.c(col)
    g = v.g
    filled = g >= 0
    edge = np.zeros_like(filled)
    for axis in (0, 2):
        for s in range(1, v.k + 1):
            for sign in (-1, 1):
                nb = np.zeros_like(filled)
                src = [slice(None)] * 3
                dst = [slice(None)] * 3
                if sign > 0:
                    src[axis], dst[axis] = slice(s, None), slice(None, -s)
                else:
                    src[axis], dst[axis] = slice(None, -s), slice(s, None)
                nb[tuple(dst)] = filled[tuple(src)]
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


def stroke2d(v, pts, r, y0, y1, col):
    """Плоский штрих-«шрифт» по ломаной pts (точки x, z) толщиной 2r, выдавленный по Y от y0 до y1."""
    import numpy as np
    for (ax, az), (bx, bz) in zip(pts, pts[1:]):
        dx, dz = bx - ax, bz - az
        L2 = max(1e-9, dx * dx + dz * dz)

        def inside(X, Y, Z, ax=ax, az=az, dx=dx, dz=dz, L2=L2):
            t = np.clip(((X - ax) * dx + (Z - az) * dz) / L2, 0, 1)
            return ((X - ax - t * dx) ** 2 + (Z - az - t * dz) ** 2 <= r * r) & (Y >= y0) & (Y < y1)

        v.shape((min(ax, bx) - r, y0, min(az, bz) - r), (max(ax, bx) + r, y1, max(az, bz) + r), inside, col)


def ring2d(v, cx, cz, rx, rz, t, y0, y1, col):
    """Плоское кольцо-петля (эллипс толщиной t), выдавленное по Y."""
    v.shape((cx - rx, y0, cz - rz), (cx + rx, y1, cz + rz),
            lambda X, Y, Z: (((X - cx) / rx) ** 2 + ((Z - cz) / rz) ** 2 <= 1)
            & (((X - cx) / (rx - t)) ** 2 + ((Z - cz) / (rz - t)) ** 2 > 1) & (Y >= y0) & (Y < y1), col)


def six_seven():
    """67 — цифры 6 и 7 с глазами, руки в жесте «six-seven» (одна ладонь выше, другая ниже)."""
    import math as m
    v = Vox((62, 30, 56), k=K)
    main, dark = '#2EC5FF', '#1379C9'
    y0, y1 = 10, 19
    # «6»: петля + стойка, уходящая дугой вправо-вверх
    ring2d(v, 17.5, 20.5, 7.5, 6.8, 5.0, y0, y1, main)
    arc = [(12.9, 20.5), (12.9, 28.5)] + [(17.8 - 5.0 * m.cos(a), 30.5 + 5.6 * m.sin(a))
                                          for a in (0.25, 0.7, 1.15, 1.6, 2.05, 2.5)]
    stroke2d(v, arc, 2.9, y0, y1, main)
    # «7»: перекладина + наклонная ножка
    stroke2d(v, [(29.5, 36.2), (41.0, 36.2), (32.0, 16.8)], 3.0, y0, y1, main)
    outline(v, main, dark)
    eye(v, 14, 38, w=4, h=5, look=(1, 0))
    eye(v, 19, 38, w=4, h=5, look=(1, 0))
    eye(v, 30, 38, w=4, h=5, look=(-1, 0))
    eye(v, 35, 38, w=4, h=5, look=(-1, 0))
    mouth(v, 17.5, 16.2, 7.5, 3.2)
    # руки: 6 — ладонь вверх слева, 7 — ладонь вниз справа
    v.line((11, 14, 28), (3, 14, 36), 1.7, main)
    v.ellipsoid(2.5, 14, 37.5, 3, 2.8, 2.4, WHITE)
    v.line((43, 14, 35), (51, 14, 27), 1.7, main)
    v.ellipsoid(52, 14, 26, 3, 2.8, 2.4, WHITE)
    for x in (17, 32):
        v.line((x, 14, 15), (x, 14, 4), 1.9, main)
        sneaker(v, x, 18, 0, main=WHITE, accent=main, w=6, l=10)
    return v, 0.035


# ------------------------------------------------------------------ Тунг Тунг Тунг Сахур
def tung_sahur():
    """Тунг Тунг Тунг Сахур — деревянное бревно с огромными глазами и бейсбольной битой."""
    v = Vox((60, 30, 64), seed=3, k=K)
    wood, bark_d, top = '#C68A4E', '#9C6532', '#E3B77F'
    cx, cy = 22, 13
    import numpy as np
    v.cyl_z(cx, cy, 12, 44, 8.5, 7.5, wood)
    # продольные борозды коры: полосы по углу, чуть извилистые по высоте
    v.shape((cx - 9, cy - 8, 12), (cx + 9, cy + 8, 44),
            lambda X, Y, Z: (np.sin(np.arctan2(Y - cy, X - cx) * 11 + np.sin(Z * 0.35) * 0.8) > 0.72)
            & (((X - cx) / 8.5) ** 2 + ((Y - cy) / 7.5) ** 2 <= 1), bark_d)
    v.shape((cx - 9, cy - 8, 12), (cx + 9, cy + 8, 44),
            lambda X, Y, Z: (np.sin(np.arctan2(Y - cy, X - cx) * 5 + Z * 0.21) > 0.93)
            & (((X - cx) / 8.5) ** 2 + ((Y - cy) / 7.5) ** 2 <= 1), shade(wood, 0.12))
    # годичные кольца на срезе сверху
    v.shape((cx - 9, cy - 8, 44), (cx + 9, cy + 8, 45),
            lambda X, Y, Z: (((X - cx) / 8.5) ** 2 + ((Y - cy) / 7.5) ** 2 <= 1) & (Z >= 44), top)
    v.shape((cx - 9, cy - 8, 44), (cx + 9, cy + 8, 45),
            lambda X, Y, Z: (np.sin(np.sqrt(((X - cx) / 8.5) ** 2 + ((Y - cy) / 7.5) ** 2) * 19) > 0.55) & (Z >= 44)
            & (((X - cx) / 8.5) ** 2 + ((Y - cy) / 7.5) ** 2 <= 1), shade(top, -0.2))
    # лицо: огромные глаза-блюдца, густые брови, маленький рот
    eye(v, 14, 37, w=6, h=6, pupil=2, look=(1, 0))
    eye(v, 23, 37, w=6, h=6, pupil=2, look=(-1, 0))
    for x0, x1, zl, zr in ((13.5, 20, 39.2, 40.6), (22.5, 29, 40.6, 39.2)):
        yb = front_y(v, int((x0 + x1) / 2), 40) - 0.6
        v.line((x0, yb, zl), (x1, yb, zr), 0.85, '#3A2412')
    my = front_y(v, 22, 26)
    v.line((19.5, my - 0.2, 26.5), (25.5, my - 0.2, 26.5), 0.7, '#3A2412')
    # руки-палки; правая держит биту над головой
    limb = shade(wood, -0.05)
    v.line((13, cy, 30), (7, cy - 1, 20), 1.3, limb)
    v.ellipsoid(6.5, cy - 1, 19, 2, 2, 2, limb)
    v.line((31, cy, 32), (37, cy - 1, 40), 1.3, limb)
    v.ellipsoid(37.5, cy - 1, 41, 2, 2, 2, limb)
    bat = '#E8C890'
    v.line((37, cy - 1, 40), (46, cy - 2, 60), 1.1, bat, r1=2.8)
    v.ellipsoid(37, cy - 1, 39, 1.8, 1.8, 1.0, shade(bat, -0.25))  # набалдашник
    # ноги-палки и ступни
    for x in (18, 26):
        v.line((x, cy, 13), (x, cy, 3), 1.4, limb)
        v.box(x - 2, x + 2, cy - 4, cy + 1, 0, 2, shade(wood, -0.15))
    return v, 0.028


# ------------------------------------------------------------------ Тралалеро Тралала
def tralalero():
    """Тралалеро Тралала — акула на трёх ногах в синих кроссовках."""
    v = Vox((64, 28, 50), seed=5, k=K)
    skin, belly, dark = '#5E8FC7', '#EEF3F8', '#3B6597'
    cx, cy, cz = 32, 13, 27
    # тело: профиль — заострённый нос → самое толстое место на трети длины → сужение к хвосту
    import numpy as np

    def prof(X):
        t = np.clip((X - 8) / 50, 0, 1)
        return np.where(t < 0.35, np.sin(np.pi / 2 * t / 0.35) ** 0.6, 1 - 0.72 * ((t - 0.35) / 0.65) ** 1.4)

    def body(X, Y, Z):
        p = np.maximum(prof(X), 0.02)
        zc = cz + np.where(X < 23, 1.5, 0)
        return (((Y - cy) / (8.5 * p)) ** 2 + ((Z - zc) / (9.5 * p)) ** 2 <= 1) & (X >= 8) & (X < 58)

    def zc_of(X):
        return cz + np.where(X < 23, 1.5, 0)

    v.shape((8, 0, 10), (58, 28, 45), body, skin)
    # спина темнее, брюхо белое — границы по плавным кривым
    v.shape((8, 0, 10), (58, 28, 45),
            lambda X, Y, Z: body(X, Y, Z) & (Z - zc_of(X) > 9.5 * prof(X) * (0.38 + 0.1 * np.sin(X * 0.4))), dark)
    v.shape((8, 0, 10), (58, 28, 45), lambda X, Y, Z: body(X, Y, Z) & (Z - zc_of(X) < -9.5 * prof(X) * 0.3), belly)

    def tri(ax, az, bx, bz, qx, qz, y0, y1, col):
        """Плоский треугольник (плавник) в плоскости XZ, толщина по Y."""
        def inside(X, Y, Z):
            d = (bz - qz) * (ax - qx) + (qx - bx) * (az - qz)
            l1 = ((bz - qz) * (X - qx) + (qx - bx) * (Z - qz)) / d
            l2 = ((qz - az) * (X - qx) + (ax - qx) * (Z - qz)) / d
            return (l1 >= 0) & (l2 >= 0) & (l1 + l2 <= 1) & (Y >= y0) & (Y < y1)
        v.shape((min(ax, bx, qx), y0, min(az, bz, qz)), (max(ax, bx, qx), y1, max(az, bz, qz)), inside, col)

    tri(26, 33, 39, 33, 31, 47, cy - 1.2, cy + 1.2, dark)          # спинной плавник
    tri(53, 30, 57, 24, 62, 41, cy - 1.2, cy + 1.2, dark)          # хвост — верхняя лопасть
    tri(53, 28, 57, 24, 61, 16, cy - 1.2, cy + 1.2, skin)          # нижняя лопасть
    for sd in (-1, 1):                                             # грудные плавники
        v.line((22, cy + sd * 6, 22), (28, cy + sd * 11, 17), 1.3, skin, r1=0.5)
    # глаза по бокам головы
    for sd in (-1, 1):
        v.ellipsoid(16, cy + sd * 6.2, 31, 1.7, 1.1, 1.7, WHITE)
        v.ellipsoid(15.6, cy + sd * 7.0, 31.2, 0.9, 0.6, 1.0, BLACK)
        v.ellipsoid(15.2, cy + sd * 7.4, 31.7, 0.35, 0.3, 0.35, WHITE)
    # пасть с зубами: плавная линия вокруг морды
    mz = lambda X: cz - 3.2 + 0.12 * (X - 9)
    v.shape((8, 0, 18), (21, 28, 30), lambda X, Y, Z: body(X, Y, Z) & (np.abs(Z - mz(X)) < 0.7), '#5A1027')
    v.shape((8, 0, 18), (21, 28, 30), lambda X, Y, Z: body(X, Y, Z) & (Z - mz(X) >= 0.7) & (Z - mz(X) < 1.7)
            & ((Z - mz(X) - 0.7) < 1.0 - np.abs(((X * 1.4) % 2) - 1) * 1.0), WHITE)
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
