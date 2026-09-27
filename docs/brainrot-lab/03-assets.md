# 3. Модели и устройства

## 3.1 Модели

### Брейнроты — 40 шт. (уже готовы)

- Пакет: [`models/brainrots/Brainrots_UEFN.zip`](../../models/brainrots/Brainrots_UEFN.zip), описание — в
  [`models/brainrots/README.md`](../../models/brainrots/README.md).
- Характеристики: 15 000 треугольников, 1 материал, текстура 1024², коллизия UCX, пивот на полу,
  лицом по +X.
- Где используются: на подиуме (над постаментом), как компаньоны за игроком и в Мемопедии.
- **Порядок в `BrainrotProps`** (индексы 0–39) — как в таблице раздела 1.3 в
  [01-mechanics.md](01-mechanics.md), не как в README моделей.
- **Производительность**: в каждом меше включи Nanite (Static Mesh Editor → Nanite Settings →
  Enable Nanite Support). Если Nanite не подходит — LOD: Number of LODs = 3, Apply.

### Пропсы лаборатории — 29 шт. (сгенерированы)

- Пакет: [`models/lab_props/LabProps_UEFN.zip`](../../models/lab_props/LabProps_UEFN.zip).
- Генератор: `python models/lab_props/tools/build_props.py` (Blender-Python 4.2, тот же `kit.py`, что у
  брейнротов).
- В каждом FBX встроенная текстура и коллизия UCX. Пивот — центр основания, лицом по +X,
  сантиметры.

| Проп | Треуг. | Размер, см (Ш×Г×В) | Где и зачем |
|---|---|---|---|
| [Capsule_Common](../../models/lab_props/Capsule_Common/preview.png) | 4108 | 46×46×85 | капсула на конвейере и в инкубаторе → CapsuleProps[0] |
| [Capsule_Rare](../../models/lab_props/Capsule_Rare/preview.png) | 4108 | 46×46×85 | → CapsuleProps[1] |
| [Capsule_Epic](../../models/lab_props/Capsule_Epic/preview.png) | 4108 | 46×46×85 | → CapsuleProps[2] |
| [Capsule_Legendary](../../models/lab_props/Capsule_Legendary/preview.png) | 4108 | 46×46×85 | → CapsuleProps[3] |
| [Capsule_Mythic](../../models/lab_props/Capsule_Mythic/preview.png) | 4108 | 46×46×85 | → CapsuleProps[4] |
| [Capsule_Iconic](../../models/lab_props/Capsule_Iconic/preview.png) | 4108 | 46×46×85 | иконы и штормовые → CapsuleProps[5] |
| [Pedestal_Base](../../models/lab_props/Pedestal_Base/preview.png) | 1716 | 132×132×32 | постамент на подиуме → PedestalProps[0] |
| [Pedestal_Gold](../../models/lab_props/Pedestal_Gold/preview.png) | 1716 | 132×132×32 | → PedestalProps[1] |
| [Pedestal_Diamond](../../models/lab_props/Pedestal_Diamond/preview.png) | 1716 | 132×132×32 | → PedestalProps[2] |
| [Pedestal_Rainbow](../../models/lab_props/Pedestal_Rainbow/preview.png) | 1716 | 132×132×32 | → PedestalProps[3] |
| [Pedestal_Lava](../../models/lab_props/Pedestal_Lava/preview.png) | 1716 | 132×132×32 | → PedestalProps[4] |
| [Pedestal_Viral](../../models/lab_props/Pedestal_Viral/preview.png) | 1716 | 132×132×32 | → PedestalProps[5] |
| [Pedestal_Cosmic](../../models/lab_props/Pedestal_Cosmic/preview.png) | 1716 | 132×132×32 | → PedestalProps[6] |
| [IdealAura](../../models/lab_props/IdealAura/preview.png) | 1200 | 169×136×143 | аура «Идеального» → AuraProps[0] |
| [Incubator](../../models/lab_props/Incubator/preview.png) | 3232 | 154×171×227 | 4 на каждом участке (ставишь руками) + prop_manipulator на нём |
| [ConveyorSegment](../../models/lab_props/ConveyorSegment/preview.png) | 1864 | 300×140×57 | 12 подряд = конвейер 36 м |
| [MemePortal](../../models/lab_props/MemePortal/preview.png) | 3056 | 540×140×652 | начало конвейера, центр хаба |
| [FusionTable](../../models/lab_props/FusionTable/preview.png) | 2268 | 320×145×266 | станция скрещивания + кнопка |
| [MemeMachine](../../models/lab_props/MemeMachine/preview.png) | 1308 | 140×112×290 | станция Мем-автомата + кнопка |
| [TourBus](../../models/lab_props/TourBus/preview.png) | 3000 | 565×255×290 | станция гастролей + кнопка |
| [Pinata](../../models/lab_props/Pinata/preview.png) | 1364 | 200×110×228 | пиньята по четвергам → PinataProp у lab_pinata_device |
| [HypeTower](../../models/lab_props/HypeTower/preview.png) | 8824 | 240×240×970 | башня шторма: табло + VFX |
| [SahurTotem](../../models/lab_props/SahurTotem/preview.png) | 2044 | 164×116×360 | ивент недели 1, кнопка «Сдать находки» |
| [RebirthAltar](../../models/lab_props/RebirthAltar/preview.png) | 2664 | 280×280×176 | на каждом участке + кнопка перерождения |
| [StreetLamp](../../models/lab_props/StreetLamp/preview.png) | 236 | 105×50×385 | декор: хаб и дороги |
| [CafeUmbrella](../../models/lab_props/CafeUmbrella/preview.png) | 1400 | 280×280×270 | декор: хаб |
| [LemonTree](../../models/lab_props/LemonTree/preview.png) | 1624 | 150×150×275 | декор: хаб и участки |
| [CappuccinoFountain](../../models/lab_props/CappuccinoFountain/preview.png) | 2036 | 540×520×295 | центральный декор хаба |
| [SignBoard](../../models/lab_props/SignBoard/preview.png) | 752 | 295×17×240 | рамка под табло станций и участков |

Превью всех пропсов — в папке каждого пропа (`preview.png`).

### Creative Prop для Verse

`SpawnProp` спавнит только Creative Prop-ы. Для каждого меша, который ставит Verse (40 брейнротов,
7 постаментов, 6 капсул, аура):
1. Импортируй FBX.
2. Создай Blueprint-класс с родителем **Creative Prop** (BuildingProp) и укажи в нём Static Mesh.
3. Build Verse Code — после этого проп появится в списке `creative_prop_asset` у полей
   `lab_manager_device`.

Название пункта меню зависит от версии UEFN, ориентир — документация Epic «Spawning props with
Verse». Всё остальное (инкубаторы, конвейер, портал, декор) ставится на карту руками как обычные
пропы.

### Из галерей Fortnite

| Что | Для чего |
|---|---|
| Дома, стены, крыши в средиземноморском / «курортном» стиле (штукатурка, терракота) | здания лабораторий на участках, киоски хаба |
| Брусчатка, плитка, бордюры | пьяцца и дороги-«виа» |
| Кипарисы, цветы, клумбы | дороги и участки |
| Пирсы, лодки, скалы | край острова |
| Бархатные столбики с канатом | вдоль красной дорожки |
| Текстовые пропы-буквы | вывеска «MEMI» у портала, «Laboratorio» на зданиях |
| Бревно | поленья для ивента Сахура |
| Платформы, батуты | паркур «Акулья башня» |

Ищи в Content Browser по словам стиля: названия галерей меняются от сезона к сезону.

---

## 3.2 Устройства

### Хаб (по одному)

| Устройство | Кол-во | Настройки |
|---|---|---|
| `lab_manager_device` (Verse) | 1 | см. 04-verse.md, раздел 4.4 |
| `lab_belt_device` (Verse) | 1 | Windows = 12 кнопок |
| `lab_storm_device` (Verse) | 1 | табло, VFX, музыка |
| `lab_pinata_device` (Verse) | 1 | проп пиньяты, манипулятор, кнопка, табло, VFX |
| `lab_collect_event_device` (Verse) | 2 | Сахур (неделя 1), 67 (неделя 7) |
| `lab_finish_reward_device` (Verse) | 1 | Тралалеро (неделя 4) |
| Button (окна конвейера) | 12 | время взаимодействия 0; модель кнопки скрыта (видна капсула); радиус взаимодействия ~2 м; текст ставит Verse |
| Button (станции) | 8 | Скрещивание, Мем-автомат, Гастроли, Хайп-магазин, Магазин, Мемопедия, Задания, Домой |
| Billboard | 3 + 2 | табло гарантий над порталом, Хайп-метр на башне, пиньята; табло ивентов у тотема и башни |
| VFX Spawner | 3–6 | молнии и конфетти шторма над хабом и башней, выключены на старте; конфетти пиньяты; вихрь портала — постоянный |
| Audio Player | 2–3 | музыка шторма (не на старте), фоновая музыка хаба |
| Input Trigger | 1 | клавиша меню; поле `MenuKey` |
| Player Spawner | 8 | на пьяцце у спавна |
| Prop Manipulator | 1 | на пропе пиньяты: урон по пропу проходит, проп не ломается |
| HUD Controller | 1 | скрыть строительство и материалы, оставить здоровье и карту |
| Item Granter / стартовый инвентарь | 1 | только кирка; для PvP — «Стойка с оружием» на участке |
| Button (поленья, ивент) | 10–15 | у каждого бревна, текст «Подобрать» ставит Verse |
| Button (финиш паркура) | 1 | на вершине Акульей башни |

### Каждый участок (× 8)

| Устройство | Кол-во | Настройки |
|---|---|---|
| `lab_plot_device` (Verse) | 1 | в центре, стрелкой к хабу, PlotNumber 1…8 |
| Teleporter | 1 | точка «дом» у входа; телепорт вызывает Verse, вход в сам телепорт не нужен |
| Button (инкубаторы) | 4 | перед дверцей каждого `SM_Incubator` |
| Billboard (инкубаторы) | 4 | над инкубаторами, 2,6 м |
| Prop Manipulator (инкубаторы) | 4 | на пропе инкубатора: урон проходит, чтобы пришло `DamagedEvent`, но проп не ломается |
| Button «Лаборатория» | 1 | у двери здания |
| Button «Перерождение» | 1 | на `SM_RebirthAltar` |
| Billboard участка | 1 | над входом: «Лаборатория #N · доход · перерождение» |

Итого: около 136 устройств на участках и около 60 в хабе.

### Настройки острова (Island Settings)

| Параметр | Значение |
|---|---|
| Max Players | 8 |
| Строительство и редактирование | выкл |
| Урон по игрокам | выкл (вкл только для режима `CarryStealOnElimination`) |
| Урон по окружению | выкл, кроме пропов с манипуляторами |
| Добыча материалов киркой | выкл (иначе игроки фармят материалы с инкубаторов) |
| Возрождение | вкл, 1–2 с, на свой участок |
| Join in Progress | Spawn |
| Время суток | день, фиксированное |
| Сохранение | Verse persistence работает в опубликованных и приватных версиях; в редакторе при каждом запуске данные могут начинаться с нуля — это нормально |
