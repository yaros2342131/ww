"""Общие детали для брейнротов: глаза, рты, конечности, крылья, хвосты, плавники, узоры.
Все координаты — дизайн-воксели; лицо смотрит в -Y, пол — Z=0."""
import math
import random

import numpy as np

from voxel import Vox
from voxel_chars import BLACK, K, WHITE, sneaker

SIZE = 0.03  # метров на дизайн-воксель по умолчанию


def new(seed, size=(64, 52, 64)):
    return Vox(size, seed=seed, k=K)


def fy(v, x, z):
    """Y передней поверхности в точке (x, z); ищет рядом, если попали в пустоту."""
    xi, zi = int(round(x)), int(round(z))
    for d in range(0, 4):
        best = None
        for dx in range(-d, d + 1):
            for dz in range(-d, d + 1):
                y = v.front_y(xi + dx, zi + dz)
                if y is not None and (best is None or y < best):
                    best = y
        if best is not None:
            return best
    return 10


# ------------------------------------------------------------------ лицо
def eye3(v, cx, cy, cz, r=2.2, look=(0, 0), pupil=BLACK, white=WHITE, slit=False, lid=None, lid_amount=0.5,
         iris=None):
    """Глаз с центром (cx, cy, cz), смотрит в -Y. slit — вертикальный зрачок (рептилии),
    lid — цвет века (опущено на lid_amount), iris — цветная радужка."""
    rz = r * 1.1
    v.ellipsoid(cx, cy, cz, r, r * 0.75, rz, white)
    px, pz = cx + look[0] * r * 0.35, cz + look[1] * r * 0.35
    if iris:
        v.ellipsoid(px, cy - r * 0.55, pz, r * 0.62, r * 0.35, rz * 0.66, iris)
    pw = r * (0.22 if slit else 0.48)
    v.ellipsoid(px, cy - r * 0.68, pz, pw, r * 0.3, rz * (0.6 if slit else 0.52), pupil)
    v.ellipsoid(px - r * 0.2, cy - r * 0.9, pz + rz * 0.28, r * 0.17, r * 0.14, r * 0.17, WHITE)
    if lid:
        top = cz + rz * (1 - 2 * lid_amount)
        v.shape((cx - r - 1, cy - r - 1, top), (cx + r + 1, cy + r, cz + rz + 1),
                lambda X, Y, Z: (((X - cx) / (r * 1.12)) ** 2 + ((Y - cy + 0.25) / (r * 0.85)) ** 2
                                 + ((Z - cz) / (rz * 1.1)) ** 2 <= 1) & (Z >= top), lid)


def eye_at(v, cx, cz, r=2.2, **kw):
    """Глаз, посаженный на переднюю поверхность в точке (cx, cz)."""
    eye3(v, cx, fy(v, cx, cz) + r * 0.3, cz, r, **kw)


def eyes(v, cx, cz, gap, r=2.2, look=(0, 0), **kw):
    for s in (-1, 1):
        eye_at(v, cx + s * gap, cz, r, look=look, **kw)


def brow(v, x0, z0, x1, z1, col='#2B1B10', r=0.75):
    y = fy(v, (x0 + x1) / 2, (z0 + z1) / 2) - 0.8
    v.line((x0, y, z0), (x1, y, z1), r, col)


def smile(v, cx, cz, w, depth=1.5, col='#4A1020', r=0.6, open_=False, tongue='#FF6F91'):
    """Улыбка-дуга по поверхности; open_ — открытый рот."""
    if open_:
        y = fy(v, cx, cz)
        v.ellipsoid(cx, y + 0.3, cz, w / 2, 1.0, depth, col)
        if tongue:
            v.ellipsoid(cx, y - 0.1, cz - depth * 0.4, w * 0.25, 0.6, depth * 0.5, tongue)
        return
    pts = []
    for i in range(9):
        t = -1 + 2 * i / 8
        x, z = cx + t * w / 2, cz - depth * (1 - t * t)
        pts.append((x, fy(v, x, z) - 0.2, z))
    for a, b in zip(pts, pts[1:]):
        v.line(a, b, r, col)


def teeth(v, cx, cz, w, n=2, col=WHITE, h=1.3):
    for i in range(n):
        x = cx - w / 2 + w * (i + 0.5) / n
        y = fy(v, x, cz) - 0.3
        v.ellipsoid(x, y, cz - h / 2, w / n * 0.4, 0.6, h / 2, col)


def blush(v, cx, cz, gap, r=1.6, col='#FF8FB0'):
    for s in (-1, 1):
        x = cx + s * gap
        v.ellipsoid(x, fy(v, x, cz) + 0.35, cz, r, 0.6, r * 0.65, col)


def nose(v, cx, cz, r=1.3, col='#2A1A14'):
    v.ellipsoid(cx, fy(v, cx, cz) + 0.2, cz, r, r * 0.8, r * 0.75, col)


def whiskers(v, cx, cz, col='#FFFFFF', r=0.45, length=6):
    for s in (-1, 1):
        for dz in (-0.8, 0.8):
            x0 = cx + s * 2
            y = fy(v, x0, cz) - 0.5
            v.line((x0, y, cz + dz), (x0 + s * length, y - 0.5, cz + dz * 2.2), r, col)


# ------------------------------------------------------------------ формы
def poly(v, pts, r0, r1=None, col=None):
    """Изогнутая «колбаса» по точкам с плавно меняющимся радиусом r0 → r1."""
    r1 = r0 if r1 is None else r1
    n = len(pts) - 1
    for i in range(n):
        ra = r0 + (r1 - r0) * i / n
        rb = r0 + (r1 - r0) * (i + 1) / n
        v.line(pts[i], pts[i + 1], ra, col, r1=rb)


def tri(v, a, b, c, plane, lo, hi, col, paint=False):
    """Плоский треугольник в плоскости 'xz' / 'yz' / 'xy' толщиной lo..hi по третьей оси."""
    ax = {'xz': (0, 2, 1), 'yz': (1, 2, 0), 'xy': (0, 1, 2)}[plane]
    (ax0, az0), (bx0, bz0), (cx0, cz0) = a, b, c
    d = (bz0 - cz0) * (ax0 - cx0) + (cx0 - bx0) * (az0 - cz0)
    if abs(d) < 1e-9:
        return

    def inside(X, Y, Z):
        P = (X, Y, Z)
        U, W, T = P[ax[0]], P[ax[1]], P[ax[2]]
        l1 = ((bz0 - cz0) * (U - cx0) + (cx0 - bx0) * (W - cz0)) / d
        l2 = ((cz0 - az0) * (U - cx0) + (ax0 - cx0) * (W - cz0)) / d
        return (l1 >= 0) & (l2 >= 0) & (l1 + l2 <= 1) & (T >= lo) & (T < hi)

    us, ws = (ax0, bx0, cx0), (az0, bz0, cz0)
    lo3, hi3 = [0, 0, 0], [0, 0, 0]
    lo3[ax[0]], hi3[ax[0]] = min(us), max(us)
    lo3[ax[1]], hi3[ax[1]] = min(ws), max(ws)
    lo3[ax[2]], hi3[ax[2]] = lo, hi
    (v.paint if paint else v.shape)(tuple(lo3), tuple(hi3), inside, col)


def cone(v, p0, p1, r, col):
    v.line(p0, p1, r, col, r1=0.35)


def ellipsoid_paint(v, c, radii, col, cond=None):
    cx, cy, cz = c
    rx, ry, rz = radii
    v.paint((cx - rx, cy - ry, cz - rz), (cx + rx, cy + ry, cz + rz),
            lambda X, Y, Z: (((X - cx) / rx) ** 2 + ((Y - cy) / ry) ** 2 + ((Z - cz) / rz) ** 2 <= 1)
            & (cond(X, Y, Z) if cond else True), col)


def dots(v, c, radii, n, cols, r=0.8, seed=1, front=True, zmin=None, zmax=None, flat=True):
    """Точки (семечки, посыпка, пятна) на поверхности эллипсоида c/radii."""
    rnd = random.Random(seed)
    cx, cy, cz = c
    rx, ry, rz = radii
    placed = []
    tries = 0
    while len(placed) < n and tries < n * 40:
        tries += 1
        th = rnd.uniform(0, 2 * math.pi)
        ph = math.acos(rnd.uniform(-1, 1))
        dx, dy, dz = math.sin(ph) * math.cos(th), math.sin(ph) * math.sin(th), math.cos(ph)
        if front and dy > -0.15:
            continue
        p = (cx + dx * rx, cy + dy * ry, cz + dz * rz)
        if zmin is not None and p[2] < zmin or zmax is not None and p[2] > zmax:
            continue
        if any((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 + (p[2] - q[2]) ** 2 < (r * 2.6) ** 2 for q in placed):
            continue
        placed.append(p)
        col = rnd.choice(cols)
        if flat:
            v.ellipsoid(*p, r, r, r, col)
        else:
            q = (p[0] + rnd.uniform(-1.5, 1.5), p[1], p[2] + rnd.uniform(-1.5, 1.5))
            v.line(p, q, r * 0.6, col)
    return placed


# ------------------------------------------------------------------ конечности
def arm(v, p0, p1, r, col, hand=None, hand_r=None, p_mid=None):
    pts = [p0, p_mid, p1] if p_mid else [p0, p1]
    poly(v, pts, r, r * 0.9, col)
    v.ellipsoid(*p1, hand_r or r * 1.6, hand_r or r * 1.6, hand_r or r * 1.6, hand or col)


def legs2(v, xs, y, top, r, col, shoe=('#FFFFFF', '#E23B3B', '#2A2A33'), w=6, l=10):
    """Две ноги в кроссовках."""
    for x in xs:
        v.line((x, y, top), (x, y, 4), r, col)
        sneaker(v, int(round(x)), int(round(y)) + 4, 0, *shoe, w=w, l=l)


def legs4(v, pts, top, r, col, hoof=None, foot_r=None):
    """Четыре (или сколько угодно) лапы/ноги до пола с копытами или ступнями."""
    for x, y in pts:
        v.line((x, y, top), (x, y, 1.5), r, col)
        fr = foot_r or r * 1.15
        v.ellipsoid(x, y - 0.6, fr * 0.55, fr, fr * 1.1, fr * 0.6, hoof or col)


def feet_claws(v, x, y, r, col, claw='#F5F0E6'):
    v.ellipsoid(x, y - 1, 1.5, r * 1.3, r * 1.8, 1.6, col)
    for dx in (-1, 0, 1):
        v.ellipsoid(x + dx * r * 0.7, y - 1 - r * 1.7, 1.2, 0.6, 0.9, 0.6, claw)


def wing(v, root, sign, span, h, col, bone=None, y_th=1.4):
    """Крыло дракона/летучей мыши в плоскости XZ (за спиной): 3 «пальца» и перепонки между ними."""
    rx, ry, rz = root
    tips = [(rx + sign * span * 0.55, rz + h), (rx + sign * span, rz + h * 0.55),
            (rx + sign * span * 0.95, rz - h * 0.05), (rx + sign * span * 0.55, rz - h * 0.35)]
    for a, b in zip(tips, tips[1:]):
        mid = ((a[0] + b[0]) / 2 - sign * span * 0.06, (a[1] + b[1]) / 2 - h * 0.05)
        tri(v, (rx, rz), a, mid, 'xz', ry - y_th / 2, ry + y_th / 2, col)
        tri(v, (rx, rz), mid, b, 'xz', ry - y_th / 2, ry + y_th / 2, col)
    for t in tips[:3]:
        v.line((rx, ry, rz), (t[0], ry, t[1]), 0.8, bone or col, r1=0.45)


def fin_yz(v, base0, base1, tip, x0, x1, col):
    """Плавник/гребень в плоскости YZ (вдоль спины), точки (y, z)."""
    tri(v, base0, base1, tip, 'yz', x0, x1, col)
