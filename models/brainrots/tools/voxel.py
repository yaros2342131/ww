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
    """Сетка вокселей. Рисуем в «дизайн-координатах»; k — во сколько раз внутренняя сетка детальнее
    (k=1 — пиксельный стиль, k=3 — для гладких моделей: круглые формы считаются на мелкой сетке)."""

    def __init__(self, size=(64, 48, 64), seed=1, k=1):
        self.k = k
        self.g = np.full(tuple(s * k for s in size), -1, dtype=np.int16)
        self.palette = []
        self.rnd = random.Random(seed)

    # ------------------------------------------------ палитра
    def c(self, hexcolor):
        hexcolor = hexcolor.upper()
        if hexcolor not in self.palette:
            self.palette.append(hexcolor)
            assert len(self.palette) <= PAL_PER_ROW * PAL_PER_ROW
        return self.palette.index(hexcolor)

    # ------------------------------------------------ рисование (дизайн-координаты)
    def _fine_box(self, x0, x1, y0, y1, z0, z1, col):
        X, Y, Z = self.g.shape
        x0, y0, z0 = max(0, x0), max(0, y0), max(0, z0)
        x1, y1, z1 = min(X, x1), min(Y, y1), min(Z, z1)
        if x0 < x1 and y0 < y1 and z0 < z1:
            self.g[x0:x1, y0:y1, z0:z1] = -1 if col is None else self.c(col)

    def set(self, x, y, z, col):
        k = self.k
        self._fine_box(x * k, (x + 1) * k, y * k, (y + 1) * k, z * k, (z + 1) * k, col)

    def get(self, x, y, z):
        k = self.k
        X, Y, Z = self.g.shape
        xf, yf, zf = x * k + k // 2, y * k + k // 2, z * k + k // 2
        if 0 <= xf < X and 0 <= yf < Y and 0 <= zf < Z:
            v = self.g[xf, yf, zf]
            return None if v < 0 else self.palette[v]
        return None

    def front_y(self, x, z):
        """Первый заполненный слой по лучу из -Y (дизайн-координаты)."""
        k = self.k
        col = self.g[x * k + k // 2, :, z * k + k // 2]
        hit = np.nonzero(col >= 0)[0]
        return None if len(hit) == 0 else int(hit[0]) // k

    def box(self, x0, x1, y0, y1, z0, z1, col):
        """Заполнить параллелепипед (границы включительно)."""
        k = self.k
        self._fine_box(min(x0, x1) * k, (max(x0, x1) + 1) * k, min(y0, y1) * k, (max(y0, y1) + 1) * k,
                       min(z0, z1) * k, (max(z0, z1) + 1) * k, col)

    def _region(self, lo, hi):
        """Срез мелкой сетки для дизайн-bbox + координаты центров мелких вокселей в дизайн-единицах."""
        k = self.k
        sl, coords = [], []
        for a, (l, h) in enumerate(zip(lo, hi)):
            f0 = max(0, int(math.floor(l * k)))
            f1 = min(self.g.shape[a], int(math.ceil(h * k)) + 1)
            sl.append(slice(f0, max(f0, f1)))
            coords.append((np.arange(f0, max(f0, f1)) + 0.5) / k)
        X, Y, Z = np.meshgrid(*coords, indexing='ij')
        return tuple(sl), X, Y, Z

    def shape(self, lo, hi, inside, col, only_empty=False):
        """Заполнить всё, где inside(X, Y, Z) истинно (numpy-массивы дизайн-координат)."""
        sl, X, Y, Z = self._region(lo, hi)
        if X.size == 0:
            return
        m = inside(X, Y, Z)
        if only_empty:
            m &= self.g[sl] < 0
        sub = self.g[sl]
        sub[m] = -1 if col is None else self.c(col)

    def paint(self, lo, hi, inside, col):
        """Перекрасить только уже заполненные воксели, где inside истинно (полоски, пятна)."""
        sl, X, Y, Z = self._region(lo, hi)
        if X.size == 0:
            return
        sub = self.g[sl]
        m = inside(X, Y, Z) & (sub >= 0)
        sub[m] = self.c(col)

    def ellipsoid(self, cx, cy, cz, rx, ry, rz, col, only_empty=False):
        self.shape((cx - rx, cy - ry, cz - rz), (cx + rx, cy + ry, cz + rz),
                   lambda X, Y, Z: ((X - cx) / rx) ** 2 + ((Y - cy) / ry) ** 2 + ((Z - cz) / rz) ** 2 <= 1,
                   col, only_empty)

    def cyl_z(self, cx, cy, z0, z1, rx, ry, col):
        self.shape((cx - rx, cy - ry, z0), (cx + rx, cy + ry, z1 + 1),
                   lambda X, Y, Z: (((X - cx) / rx) ** 2 + ((Y - cy) / ry) ** 2 <= 1) & (Z >= z0) & (Z < z1 + 1), col)

    def line(self, p0, p1, r, col, r1=None):
        """Капсула от p0 до p1 (конечности, бита). r1 — радиус на конце (конус)."""
        p0, p1 = np.array(p0, float), np.array(p1, float)
        r1 = r if r1 is None else r1
        d = p1 - p0
        L2 = max(1e-9, float(d @ d))
        rm = max(r, r1)
        lo, hi = np.minimum(p0, p1) - rm, np.maximum(p0, p1) + rm

        def inside(X, Y, Z):
            t = np.clip(((X - p0[0]) * d[0] + (Y - p0[1]) * d[1] + (Z - p0[2]) * d[2]) / L2, 0, 1)
            dx, dy, dz = X - (p0[0] + t * d[0]), Y - (p0[1] + t * d[1]), Z - (p0[2] + t * d[2])
            return dx * dx + dy * dy + dz * dz <= (r + (r1 - r) * t) ** 2

        self.shape(lo, hi, inside, col)

    def bitmap(self, rows, x0, z_top, y0, y1, colmap):
        """Нарисовать 2D-картинку (строки сверху вниз) на плоскости XZ, выдавив по Y от y0 до y1."""
        for r, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch in colmap:
                    self.box(x0 + i, x0 + i, y0, y1, z_top - r, z_top - r, colmap[ch])

    def noise(self, colors_from, variants, chance=0.3, grain=1):
        """Фактура: часть «зёрен» размером grain дизайн-вокселей цвета colors_from меняем на вариант."""
        idx = self.c(colors_from)
        vids = [self.c(v) for v in variants]
        g = self.k * grain
        shape = tuple(-(-s // g) for s in self.g.shape)
        rs = np.random.RandomState(self.rnd.randrange(1 << 30))
        pick = rs.randint(0, len(vids), shape)
        on = rs.random_sample(shape) < chance
        pick = np.repeat(np.repeat(np.repeat(pick, g, 0), g, 1), g, 2)[:self.g.shape[0], :self.g.shape[1], :self.g.shape[2]]
        on = np.repeat(np.repeat(np.repeat(on, g, 0), g, 1), g, 2)[:self.g.shape[0], :self.g.shape[1], :self.g.shape[2]]
        m = (self.g == idx) & on
        self.g[m] = np.array(vids, dtype=np.int16)[pick[m]]

    def top_layer(self, from_cols, col, lo, hi, thickness=1):
        """Перекрасить верхний слой (толщиной thickness дизайн-вокселей) фигуры в bbox — тень/спина."""
        ids = [self.c(c) for c in from_cols]
        sl, X, Y, Z = self._region(lo, hi)
        sub = self.g[sl]
        filled = sub >= 0
        t = thickness * self.k
        above = np.zeros_like(filled)
        for s in range(1, t + 1):
            sh = np.zeros_like(filled)
            sh[:, :, :-s] = filled[:, :, s:]
            above |= ~sh
        # воксель в верхнем слое, если на расстоянии < t над ним где-то пусто
        m = filled & above & np.isin(sub, ids)
        sub[m] = self.c(col)

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


# ------------------------------------------------------------------ гладкий режим
def _lin(h):
    return tuple(c for c in kit.hexcol(h))


def finalize_smooth(vox, name, out_dir, voxel_size, target_tris=15000, sigma=1.4, tex_res=2048):
    """Гладкая модель по воксельному рисунку:
    1) размываем «заполненность» сетки и строим поверхность marching cubes — ступеньки исчезают;
    2) каждой грани детальной копии даём цвет ближайшего вокселя (резкие границы цветов);
    3) лёгкую копию (target_tris) разворачиваем и запекаем на неё цвета с детальной — одна текстура."""
    from scipy.ndimage import gaussian_filter
    from skimage.measure import marching_cubes
    from mathutils import Matrix

    g = vox.g
    fine = voxel_size / vox.k
    pad = 4
    occ = np.pad((g >= 0).astype(np.float32), pad)
    field = gaussian_filter(occ, sigma)
    verts, faces, _, _ = marching_cubes(field, 0.5)
    verts -= pad

    # цвет граней: ищем заполненный воксель чуть внутри поверхности
    fc = verts[faces].mean(axis=1)
    fn = np.cross(verts[faces[:, 1]] - verts[faces[:, 0]], verts[faces[:, 2]] - verts[faces[:, 0]])
    fn /= np.linalg.norm(fn, axis=1, keepdims=True) + 1e-9
    shape = np.array(g.shape)

    def lookup(p):
        i = np.floor(p).astype(int)
        ok = np.all((i >= 0) & (i < shape), axis=1)
        out = np.full(len(p), -1, dtype=np.int16)
        out[ok] = g[i[ok, 0], i[ok, 1], i[ok, 2]]
        return out

    col = np.full(len(faces), -1, dtype=np.int16)
    for step in (0.6, 1.2, 2.0, 3.0):
        for sgn in (1, -1):
            need = col < 0
            if not need.any():
                break
            col[need] = lookup(fc[need] + sgn * fn[need] * step)
    if (col < 0).any():  # запасной вариант — поиск по окрестности
        offs = sorted(((dx, dy, dz) for dx in range(-3, 4) for dy in range(-3, 4) for dz in range(-3, 4)),
                      key=lambda o: o[0] ** 2 + o[1] ** 2 + o[2] ** 2)
        for o in offs:
            need = col < 0
            if not need.any():
                break
            col[need] = lookup(fc[need] + np.array(o))
    col[col < 0] = 0

    # детальная копия с цветами граней
    me = bpy.data.meshes.new(name + '_hi')
    me.from_pydata((verts * fine).tolist(), [], faces.tolist())
    me.update()
    attr = me.color_attributes.new('Col', 'FLOAT_COLOR', 'CORNER')
    pal = np.array([_lin(h) for h in vox.palette], dtype=np.float32)
    corner_face = np.repeat(np.arange(len(faces)), 3)
    attr.data.foreach_set('color', pal[col[corner_face]].ravel())
    hi = bpy.data.objects.new(name + '_hi', me)
    bpy.context.collection.objects.link(hi)
    kit.select(hi)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shade_smooth()
    mh = bpy.data.materials.new('M_hi')
    mh.use_nodes = True
    ca = mh.node_tree.nodes.new('ShaderNodeVertexColor')
    ca.layer_name = 'Col'
    mh.node_tree.links.new(ca.outputs['Color'], mh.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
    me.materials.append(mh)

    # лёгкая копия
    lo = hi.copy()
    lo.data = hi.data.copy()
    lo.name = name
    lo.data.name = name
    bpy.context.collection.objects.link(lo)
    lo.data.color_attributes.remove(lo.data.color_attributes['Col'])
    lo.data.materials.clear()
    kit.select(lo)
    sm = lo.modifiers.new('smooth', 'SMOOTH')
    sm.factor, sm.iterations = 0.5, 2
    kit.apply_mods(lo)
    kit.decimate(lo, target_tris)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.004)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shade_smooth()

    img = bpy.data.images.new(name + '_BaseColor', tex_res, tex_res)
    ml = bpy.data.materials.new('M_' + name)
    ml.use_nodes = True
    tn = ml.node_tree.nodes.new('ShaderNodeTexImage')
    tn.image = img
    ml.node_tree.nodes.active = tn
    bsdf = ml.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Roughness'].default_value = 0.5
    ml.node_tree.links.new(tn.outputs['Color'], bsdf.inputs['Base Color'])
    lo.data.materials.append(ml)

    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.samples = 4
    bk = sc.render.bake
    bk.use_selected_to_active = True
    bk.cage_extrusion = fine * 3
    bk.max_ray_distance = fine * 8
    bk.margin = 12
    bk.use_pass_direct = bk.use_pass_indirect = False
    bk.use_pass_color = True
    bpy.ops.object.select_all(action='DESELECT')
    hi.select_set(True)
    lo.select_set(True)
    bpy.context.view_layer.objects.active = lo
    bpy.ops.object.bake(type='DIFFUSE')
    tex_path = os.path.join(out_dir, f'T_{name}_BaseColor.png')
    img.filepath_raw = tex_path
    img.file_format = 'PNG'
    img.save()
    bpy.data.objects.remove(hi)
    bk.use_selected_to_active = False

    # пивот — центр основания
    bb = [Vector(c) for c in lo.bound_box]
    cx = (min(v.x for v in bb) + max(v.x for v in bb)) / 2
    cy = (min(v.y for v in bb) + max(v.y for v in bb)) / 2
    lo.data.transform(Matrix.Translation((-cx, -cy, -min(v.z for v in bb))))
    return lo, tex_path
