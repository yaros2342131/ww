"""Воксельные брейнроты: модель рисуется кубиками в сетке, затем greedy meshing склеивает
соседние грани одного цвета в большие прямоугольники → мало треугольников, чёткий пиксельный вид.
Цвета — текстура-палитра 64×64 (блок 4×4 px на цвет), один материал на модель.

Оси: x — вправо, y — вглубь (лицо смотрит в -Y), z — вверх. Координаты в вокселях.
"""
import math
import os
import random

import numpy as np

import kit
import bpy
from mathutils import Vector

PAL_SIZE, PAL_BLOCK = 64, 4
PAL_PER_ROW = PAL_SIZE // PAL_BLOCK


def rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def shade(h, k):
    """Светлее (k>0) или темнее (k<0) цвет в sRGB."""
    r, g, b = rgb(h)
    if k >= 0:
        r, g, b = (int(c + (255 - c) * k) for c in (r, g, b))
    else:
        r, g, b = (int(c * (1 + k)) for c in (r, g, b))
    return '#%02X%02X%02X' % (r, g, b)


class Vox:
    def __init__(self, size=(64, 48, 64), seed=1):
        self.g = np.full(size, -1, dtype=np.int16)
        self.palette = []
        self.rnd = random.Random(seed)

    # ------------------------------------------------ палитра
    def c(self, hexcolor):
        hexcolor = hexcolor.upper()
        if hexcolor not in self.palette:
            self.palette.append(hexcolor)
            assert len(self.palette) <= PAL_PER_ROW * PAL_PER_ROW
        return self.palette.index(hexcolor)

    # ------------------------------------------------ рисование
    def set(self, x, y, z, col):
        X, Y, Z = self.g.shape
        if 0 <= x < X and 0 <= y < Y and 0 <= z < Z:
            self.g[x, y, z] = -1 if col is None else self.c(col)

    def get(self, x, y, z):
        X, Y, Z = self.g.shape
        if 0 <= x < X and 0 <= y < Y and 0 <= z < Z:
            v = self.g[x, y, z]
            return None if v < 0 else self.palette[v]
        return None

    def box(self, x0, x1, y0, y1, z0, z1, col):
        """Заполнить параллелепипед (границы включительно)."""
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                for z in range(min(z0, z1), max(z0, z1) + 1):
                    self.set(x, y, z, col)

    def ellipsoid(self, cx, cy, cz, rx, ry, rz, col, only_empty=False):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
                for z in range(int(cz - rz) - 1, int(cz + rz) + 2):
                    if ((x + .5 - cx) / rx) ** 2 + ((y + .5 - cy) / ry) ** 2 + ((z + .5 - cz) / rz) ** 2 <= 1:
                        if not only_empty or self.get(x, y, z) is None:
                            self.set(x, y, z, col)

    def cyl_z(self, cx, cy, z0, z1, rx, ry, col):
        for z in range(z0, z1 + 1):
            for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
                for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
                    if ((x + .5 - cx) / rx) ** 2 + ((y + .5 - cy) / ry) ** 2 <= 1:
                        self.set(x, y, z, col)

    def line(self, p0, p1, r, col):
        """Толстая линия (конечности, бита) — цепочка сфер радиуса r."""
        p0, p1 = np.array(p0, float), np.array(p1, float)
        n = int(np.linalg.norm(p1 - p0) * 2) + 1
        for i in range(n + 1):
            p = p0 + (p1 - p0) * i / n
            self.ellipsoid(*p, r, r, r, col)

    def bitmap(self, rows, x0, z_top, y0, y1, colmap):
        """Нарисовать 2D-картинку (строки сверху вниз) на плоскости XZ, выдавив по Y от y0 до y1.
        colmap: символ → цвет ('.' и ' ' — пусто)."""
        for r, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch in colmap:
                    for y in range(y0, y1 + 1):
                        self.set(x0 + i, y, z_top - r, colmap[ch])

    def face_bitmap(self, rows, x0, z_top, colmap, depth=1):
        """Нарисовать лицо поверх фронтальной поверхности: для каждого пикселя ищем первый
        заполненный воксель по лучу из -Y и перекрашиваем его (и depth-1 глубже)."""
        for r, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch not in colmap:
                    continue
                x, z = x0 + i, z_top - r
                for y in range(self.g.shape[1]):
                    if self.g[x, y, z] >= 0:
                        for d in range(depth):
                            self.set(x, y + d, z, colmap[ch])
                        break

    def noise(self, colors_from, variants, chance=0.3):
        """Пиксельная фактура: часть вокселей цвета colors_from меняем на случайный вариант."""
        idx = self.c(colors_from)
        vids = [self.c(v) for v in variants]
        for pos in zip(*np.nonzero(self.g == idx)):
            if self.rnd.random() < chance:
                self.g[pos] = self.rnd.choice(vids)

    def replace(self, a, b, where=None):
        ia = self.c(a)
        ib = self.c(b)
        mask = self.g == ia
        if where is not None:
            X, Y, Z = np.indices(self.g.shape)
            mask &= where(X, Y, Z)
        self.g[mask] = ib

    def mirror_x(self, cx):
        """Отзеркалить левую половину (x < cx) на правую — симметричные персонажи рисуем наполовину."""
        X = self.g.shape[0]
        for x in range(0, cx):
            xm = 2 * cx - 1 - x
            if 0 <= xm < X:
                self.g[xm] = self.g[x]

    # ------------------------------------------------ меш
    def greedy_quads(self):
        g = self.g
        dims = g.shape
        quads = []  # (4 вершины, цвет, нормаль)
        for d in range(3):
            u, v = (d + 1) % 3, (d + 2) % 3
            for sign in (-1, 1):
                for k in range(dims[d]):
                    # маска: воксель на слое k заполнен, сосед по нормали пуст
                    sl = [slice(None)] * 3
                    sl[d] = k
                    cur = g[tuple(sl)]
                    nk = k + sign
                    if 0 <= nk < dims[d]:
                        sl2 = [slice(None)] * 3
                        sl2[d] = nk
                        nb = g[tuple(sl2)]
                        mask = np.where(nb < 0, cur, -1)
                    else:
                        mask = cur.copy()
                    # после среза по оси d порядок осей: оставшиеся по возрастанию
                    axes = [a for a in range(3) if a != d]
                    if axes != [u, v]:
                        mask = mask.T  # привести к порядку (u, v)
                    mask = mask.copy()
                    U, V = mask.shape
                    for i in range(U):
                        j = 0
                        while j < V:
                            col = mask[i, j]
                            if col < 0:
                                j += 1
                                continue
                            w = 1
                            while j + w < V and mask[i, j + w] == col:
                                w += 1
                            h = 1
                            while i + h < U and np.all(mask[i + h, j:j + w] == col):
                                h += 1
                            mask[i:i + h, j:j + w] = -1
                            plane = k + (1 if sign > 0 else 0)
                            corners = []
                            for du, dv in ((0, 0), (h, 0), (h, w), (0, w)):
                                p = [0, 0, 0]
                                p[d], p[u], p[v] = plane, i + du, j + dv
                                corners.append(p)
                            n = [0, 0, 0]
                            n[d] = sign
                            quads.append((corners, int(col), n))
                            j += w
        return quads

    def to_object(self, name, voxel_size):
        quads = self.greedy_quads()
        verts, faces, uvs = [], [], []
        for corners, col, n in quads:
            a, b, c_ = (Vector(corners[i]) for i in range(3))
            if (b - a).cross(c_ - a).dot(Vector(n)) < 0:
                corners = corners[::-1]
            base = len(verts)
            verts += [tuple(x * voxel_size for x in p) for p in corners]
            faces.append((base, base + 1, base + 2, base + 3))
            cx = (col % PAL_PER_ROW) * PAL_BLOCK + PAL_BLOCK / 2
            cy = (col // PAL_PER_ROW) * PAL_BLOCK + PAL_BLOCK / 2
            uvs.append((cx / PAL_SIZE, 1 - cy / PAL_SIZE))
        me = bpy.data.meshes.new(name)
        me.from_pydata(verts, [], faces)
        me.update()
        uv = me.uv_layers.new(name='UVMap')
        for poly, uvc in zip(me.polygons, uvs):
            for li in poly.loop_indices:
                uv.data[li].uv = uvc
        # склеить совпадающие вершины внутри одного цвета нельзя (разные UV) — оставляем «жёсткие» кубы
        o = bpy.data.objects.new(name, me)
        bpy.context.collection.objects.link(o)
        return o

    def save_palette(self, path):
        from PIL import Image
        im = Image.new('RGB', (PAL_SIZE, PAL_SIZE), (255, 0, 255))
        for i, h in enumerate(self.palette):
            x0, y0 = (i % PAL_PER_ROW) * PAL_BLOCK, (i // PAL_PER_ROW) * PAL_BLOCK
            for x in range(x0, x0 + PAL_BLOCK):
                for y in range(y0, y0 + PAL_BLOCK):
                    im.putpixel((x, y), rgb(h))
        im.save(path)


def finalize(vox, name, out_dir, voxel_size):
    """Меш + палитра + материал; пивот — центр основания."""
    o = vox.to_object(name, voxel_size)
    kit.select(o)
    bb = [Vector(c) for c in o.bound_box]
    cx = (min(v.x for v in bb) + max(v.x for v in bb)) / 2
    cy = (min(v.y for v in bb) + max(v.y for v in bb)) / 2
    minz = min(v.z for v in bb)
    from mathutils import Matrix
    o.data.transform(Matrix.Translation((-cx, -cy, -minz)))
    tex_path = os.path.join(out_dir, f'T_{name}_Palette.png')
    vox.save_palette(tex_path)
    img = bpy.data.images.load(tex_path)
    m = bpy.data.materials.new('M_' + name)
    m.use_nodes = True
    t = m.node_tree.nodes.new('ShaderNodeTexImage')
    t.image = img
    t.interpolation = 'Closest'
    bsdf = m.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Roughness'].default_value = 0.6
    m.node_tree.links.new(t.outputs['Color'], bsdf.inputs['Base Color'])
    o.data.materials.append(m)
    return o, tex_path
