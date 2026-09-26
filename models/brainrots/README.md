# Брейнроты — воксельные модели для UEFN

Классические мем-брейнроты в пиксельном (воксельном) стиле. Пилот: 3 из 40. Статичные меши для подставок в тайкуне.

| Персонаж | Треугольники | Размер (Ш×Г×В) | Превью |
|---|---|---|---|
| 67 (Six Seven) | 1 484 | 192×39×140 см | [preview](SixSeven_67/preview.png) |
| Тралалеро Тралала | 3 240 | 162×63×138 см | [preview](Tralalero_Tralala/preview.png) |
| Тунг Тунг Тунг Сахур | 3 156 | 123×45×176 см | [preview](Tung_Tung_Tung_Sahur/preview.png) |

Каждая папка: `SM_<Имя>.fbx` (меш), `T_<Имя>_Palette.png` (палитра 64×64), `preview.png`, `info.json`.
Один материал на модель. Пивот — центр основания на полу, лицо смотрит вперёд.
Треугольников в 5–15 раз меньше лимита: грани одного цвета склеены в большие прямоугольники,
поэтому 40 брейнротов на карте одновременно — не проблема даже для Switch и мобильных.

## Импорт в UEFN
1. Content Browser → **Import** → FBX и PNG. В окне FBX: **Static Mesh**, `Skeletal Mesh` выключен,
   `Combine Meshes` включён.
2. Откройте текстуру `T_..._Palette`: **Filter = Nearest**, **Mip Gen Settings = NoMipmaps**,
   **Compression = UserInterface2D (RGBA)** или `VectorDisplacementmap` — иначе цвета на стыках «поплывут».
3. Если материал не подключился сам: `Texture Sample` с палитрой → **Base Color**, Roughness ≈ 0.6.
4. Коллизия: в редакторе меша `Collision → Add Box Simplified Collision`.
5. LOD не нужен — меши и так лёгкие.
6. Покачивание и вращение на подставке — через Verse.

## Пересборка / новые персонажи
```
pip install bpy==4.2.0 pillow numpy      # Python 3.11
python tools/build.py                    # все персонажи
python tools/build.py SixSeven_67
```
- `tools/voxel.py` — воксельный движок: рисование кубиками (box, ellipsoid, line, bitmap), greedy-меш, палитра.
- `tools/voxel_chars.py` — персонажи. Новый брейнрот = новая функция + строка в `VOX_CHARACTERS`.
- `tools/kit.py` — экспорт FBX и превью-рендер.
