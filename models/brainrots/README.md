# Брейнроты Космо Пекарни — модели для UEFN

Пилот: 3 из 40 персонажей. Статичные меши для подставок в тайкуне.

| Персонаж | Треугольники | Размер (Ш×Г×В) | Превью |
|---|---|---|---|
| Круассанино Астронавтино | 19 534 | 124×78×116 см | [preview](Croissantino_Astronautino/preview.png) |
| Пончикелло Бомбардино | 20 000 | 190×55×125 см | [preview](Ponchikello_Bombardino/preview.png) |
| Кексолино Метеорино | 20 000 | 109×78×140 см | [preview](Keksolino_Meteorino/preview.png) |

Каждая папка: `SM_<Имя>.fbx` (меш), `T_<Имя>_BaseColor.png` (текстура 2048², вся окраска запечена),
`preview.png`, `info.json`. Один материал на модель — один draw call.
Пивот — между ступнями на полу, лицо смотрит вперёд.

## Импорт в UEFN
1. Content Browser → **Import** → выбрать FBX и PNG.
2. В окне импорта FBX: **Static Mesh**, `Skeletal Mesh` выключен, `Combine Meshes` включён,
   `Import Materials` / `Import Textures` включены.
3. Если текстура не подключилась сама: откройте материал → `Texture Sample` с `T_..._BaseColor` → **Base Color**.
   Roughness ≈ 0.5.
4. Откройте меш → **LOD Settings**: `Number of LODs = 3` → Apply (авто-LOD: ~50% / 25% / 12%).
   Это важно, когда в кадре много брейнротов.
5. Коллизия: в редакторе меша `Collision → Add Box/Capsule Simplified Collision`.
6. Покачивание и вращение на подставке — через Verse (`TeleportTo` / `MoveTo` с анимацией по времени).

Бюджет: 20k треугольников на модель (лимит 30k). Если на карте одновременно видно больше 15–20 брейнротов,
в Build Settings поставьте `Max Texture Size = 1024`.

## Пересборка / новые персонажи
Генератор процедурный (Blender 4.2 как Python-модуль):
```
pip install bpy==4.2.0 pillow      # Python 3.11
python tools/build.py              # все персонажи
python tools/build.py Keksolino_Meteorino
```
`tools/kit.py` — детали (глаза, рты, конечности, кроссовки, запекание, экспорт),
`tools/characters.py` — персонажи. Новый брейнрот = новая функция в `characters.py`.
