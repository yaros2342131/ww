# 4. Verse: код тайкуна и сборка в UEFN

Код лежит в [`verse/`](../../verse). Это полный тайкун: экономика, сохранение, конвейер, инкубаторы,
подиум, семьи и комбо, шторм, скрещивание, гастроли, задания, Мем-автомат, компаньоны, ивенты,
HUD и меню.

> **Важно.** Код написан по документации Verse API, но **не собирался в UEFN**: в окружении, где
> он писался, UEFN нет. Он прошёл статическую проверку (все константы и методы определены,
> функции с побочными эффектами не вызываются внутри условий `if` и `<transacts>`-функций).
> Первая сборка в UEFN почти наверняка покажет несколько ошибок. Самые вероятные места — в
> разделе 4.6.

## 4.1 Файлы

| Файл | Что внутри |
|---|---|
| `lab_data.verse` | **генерируется** из конфига: редкости, варианты, 40 брейнротов, семьи, комбо, рецепты, 35 перерождений, цены, магазин, гастроли, задания, все числа |
| `lab_util.verse` | текст → message, формат чисел (1.2K, 3.4M), время, случайность, календарь UTC |
| `lab_save.verse` | сохранение: `lab_save` (persistable) и `weak_map(player, lab_save)` |
| `lab_player.verse` | игрок в сессии и вся экономика: доход, бонусы семей и комбо, цены, перерождения, улучшения, скрещивание, гастроли, задания, офлайн-доход |
| `lab_plot.verse` | `lab_plot_device` — участок: подиум сеткой, инкубаторы, табличка, телепорт домой |
| `lab_belt.verse` | `lab_belt_device` — конвейер с окнами покупки, гарантии и табло |
| `lab_storm.verse` | `lab_storm_device` — Хайп-шторм: шкала лобби, адаптивный порог, эффекты |
| `lab_ui.verse` | HUD и универсальное меню «строки + кнопки» |
| `lab_screens.verse` | все экраны меню |
| `lab_manager.verse` | `lab_manager_device` — главный: игроки, тик дохода, покупки, инкубаторы, вылупление, меню, награды |
| `lab_events.verse` | Мем-пиньята, «собери и принеси», награда на финише паркура |

Числа меняются так:
1. Правишь `config/brainrot_lab_tycoon.json`.
2. Запускаешь `python tools/gen_verse_data.py`.
3. Копируешь `verse/lab_data.verse` в проект.

Темп после правки проверяет `python tools/economy_sim.py`.

## 4.2 Как устроено

```
lab_manager_device ──┬── lab_plot_device × 8 ── инкубаторы (кнопка + табло + манипулятор пропа)
  Tick() раз в 1 с   │                          подиум: SpawnProp постамента и брейнрота
  SaveLoop() 20 с    ├── lab_belt_device ─────── 12 окон-кнопок, капсулы SpawnProp + MoveTo
                     ├── lab_storm_device ────── табло, VFX, музыка
  Sessions[player] ──┤   lab_session: lab_player (данные) + lab_hud + lab_menu + компаньоны
                     └── станции хаба (кнопки) и клавиша меню (input_trigger_device)
lab_pinata_device, lab_collect_event_device, lab_finish_reward_device → Manager.Grant*()
```

- Данные игрока живут в `lab_player`. В `weak_map` они сохраняются раз в 20 с, после покупки
  за V-Bucks и при выходе.
- Время двух видов:
  - реальное (`GetSecondsSinceEpoch`, функция `LabNow()`): инкубаторы, скрещивание, гастроли,
    офлайн-доход, ивенты, неделя контента;
  - время сервера (`GetSimulationElapsedTime`): конвейер, шторм, пиньята.
- Меню — одна панель: заголовок, строки, кнопки. У каждой кнопки код действия `Act_*` и аргумент.
  Нажатие → `OnMenuAction` → действие → экран перерисовывается.

## 4.3 Установка в UEFN — по шагам

1. **Проект.** UEFN → New Project → пустой остров (Blank). Island Settings:
   - Max Players 8;
   - строительство выключено;
   - урон по игрокам выключен (PvP включай, только если ставишь `CarryStealOnElimination`);
   - возрождение включено;
   - стартовый инвентарь — только кирка;
   - Join in Progress — Spawn.
2. **Модели.** Импортируй `models/brainrots/Brainrots_UEFN.zip` (40 брейнротов) и
   `models/lab_props/LabProps_UEFN.zip` (пропсы лаборатории), как написано в README внутри
   архивов.
3. **Creative Prop-ы.** Для `SpawnProp` нужен не меш, а проп. Для каждого меша создай
   Blueprint-класс с родителем Creative Prop (BuildingProp) и укажи в нём меш. Названия пунктов
   меню зависят от версии UEFN — ориентир в документации Epic «Spawning props with Verse». Нужны:
   - 40 брейнротов;
   - 7 постаментов;
   - 6 капсул;
   - аура «Идеального».
4. **Код.** Скопируй все файлы из `verse/` в папку Verse проекта (Verse Explorer → папка
   проекта), затем Verse → Build Verse Code. Ошибки исправляй по разделу 4.6.
5. **Устройства.** Перетащи на карту из Content Browser → Creative Devices → свои Verse-устройства:
   - 1 × `lab_manager_device`, 1 × `lab_belt_device`, 1 × `lab_storm_device`;
   - 8 × `lab_plot_device` (по одному в центр каждого участка, стрелкой к хабу, PlotNumber 1…8);
   - 1 × `lab_pinata_device`;
   - 2 × `lab_collect_event_device` (Сахур — неделя 1; 67 — неделя 7, RewardKey `SixSeven_67`);
   - 1 × `lab_finish_reward_device` (Тралалеро, неделя 4).
6. **Стандартные устройства** — по списку из [03-assets.md](03-assets.md#32-устройства).
7. **Связи** — раздел 4.4.
8. **Тест** — раздел 4.5. Потом Publish → приватная версия → тест с друзьями → публикация.

## 4.4 Что куда подключить (@editable)

**`lab_manager_device`**

| Поле | Что указать |
|---|---|
| Plots | 8 `lab_plot_device` в порядке #1…#8 |
| Belt / Storm | устройства конвейера и шторма |
| BrainrotProps | **40** Creative Prop-ов брейнротов строго в порядке таблицы в 01-mechanics.md (индекс 0 = Noobini Pizzanini … 39 = 67) |
| PedestalProps | 7: Base, Gold, Diamond, Rainbow, Lava, Viral, Cosmic |
| CapsuleProps | 6: Common, Rare, Epic, Legendary, Mythic, Iconic |
| AuraProps | 1: IdealAura |
| MenuKey | Input Trigger device (клавиша меню) |
| FusionButton, LuckyButton, TourButton, ShopButton, OffersButton, DexButton, QuestButton, HomeButton | кнопки станций хаба |
| LaunchEpochSeconds | Unix-время запуска: например, 1794686400 = суббота 14.11.2026 20:00 UTC (старт первого субботнего ивента). Посчитать: `python3 -c "import datetime as d; print(int(d.datetime(2026,11,14,20,tzinfo=d.timezone.utc).timestamp()))"` |
| ForceWeek | −1 в релизе; 0…10 — чтобы проверить контент нужной недели |
| CarryStealOnElimination | false (включи, если нужно лёгкое PvP) |

**`lab_plot_device` (на каждом участке)**

| Поле | Что указать |
|---|---|
| PlotNumber | 1…8 |
| HomeTeleporter | телепорт у входа на участок |
| OwnerBoard | табличка участка (billboard) |
| Incubators | 4 элемента: Button (у дверцы), Board (над инкубатором), Hits (манипулятор на пропе инкубатора), CapsuleOffset (по умолчанию 110 см вверх) |
| MenuButton | кнопка «Лаборатория» у двери |
| RebirthButton | кнопка на алтаре перерождения |
| PodiumColumns / PodiumSpacing / PodiumOffset / PedestalHeight | 6 / 260 / (500, −650, 0) / 35 — меняй, если подиум не влезает |

**`lab_belt_device`**: Windows — 12 кнопок от портала к концу ленты, TimerBoard — табло над
порталом, CapsuleLift 60, MoveSeconds 0,8.

**`lab_storm_device`**: MeterBoard — табло на башне, StormEffects — VFX Spawner-ы (выключены на
старте), StormMusic — Audio Player.

**`lab_pinata_device`**: Manager, PinataProp (проп пиньяты на карте), Hits (манипулятор на этом
пропе), HitButton, Board, ConfettiVFX, ForceActive (для теста).

**`lab_collect_event_device`**: Manager, Pickups (кнопки у поленьев), Deliver (кнопка у
тотема), Board, Need 10, RewardKey `Tung_Tung_Tung_Sahur`, FromWeek 1, EventName.

**`lab_finish_reward_device`**: Manager, Finish (кнопка на вершине), RewardKey
`Tralalero_Tralala`, FromWeek 4.

## 4.5 Проверка перед публикацией

- [ ] Вход: игрока телепортирует на свободный участок, HUD показывает Кэш 1 000.
- [ ] Конвейер: капсулы едут, у окон подпись с ценой, покупка списывает Кэш, в HUD «В руках».
- [ ] Инкубатор: E кладёт капсулу, табло тикает, удар киркой ускоряет (или E, если манипулятор не
      ловит урон), брейнрот встаёт на подиум с постаментом.
- [ ] Доход идёт каждую секунду, табличка участка показывает доход.
- [ ] Меню по клавише: Запас, карточка, улучшение, продажа, компаньон ходит за игроком.
- [ ] Перерождение 1 (Noobini, Tim Cheese, Pipi Kiwi): Кэш сгорает, +1 место.
- [ ] Выйти и зайти: всё на месте, есть сообщение об офлайн-доходе.
- [ ] Шторм: при 2+ игроках шкала растёт, через ~15 мин шторм, эффекты и музыка, капсулы
      вкладчикам.
- [ ] `ForceWeek = 3`: скрещивание по рецепту Noobini + Salamino + Tim Cheese → Spaghetti
      Tualetti.
- [ ] `ForceWeek = 5`: «Вирусный взрыв» с R12 и Радужной легендаркой.
- [ ] `ForceActive` пиньяты: появляется, ломается, награды приходят.
- [ ] 8 игроков одновременно: нет просадок FPS, память острова в норме.

## 4.6 Где скорее всего будут ошибки компиляции и как чинить

| Место | Что может не совпасть | Как чинить |
|---|---|---|
| `LabNow()` в `lab_util.verse` | модуль или эффекты `GetSecondsSinceEpoch` | добавить `using` из подсказки компилятора; все вызовы идут через одну функцию |
| `LabSaves` в `lab_save.verse` | ограничения persistable (значения по умолчанию у struct, `[]logic`) | заменить `[]logic` на `[]int` (0/1), поля не удалять |
| Поля и методы UI (`DefaultTextColor`, `color_block`, `button_quiet`) | имена в твоей версии | Verse Explorer → digest `/UnrealEngine.com/Temporary/UI` |
| `NamedColors.LightGray` и другие цвета | имя цвета | заменить на `NamedColors.White` |
| `set Map[Key] = …` внутри `if (…) {}` | компилятор может потребовать или запретить `if` | убрать или добавить обёртку `if (…) {}` |
| `Pr.MoveTo(...)` без использования результата | предупреждение | игнорировать или `_Result := Pr.MoveTo(...)` |
| `int * float` (например, `Row * PodiumSpacing`) | если оператор не определён | писать `(Row * 1.0) * PodiumSpacing` |
| `prop_manipulator_device.DamagedEvent` | событие не приходит, если проп неуязвим | включить урон по пропу с большим запасом прочности; кнопка E всё равно ускоряет |
| `SpawnProp` | лимит пропов, спавн в полу | проверить Z (`PedestalHeight`, `CapsuleLift`), не спавнить больше нужного |

Если ошибок много, собирай по одному файлу, в этом порядке:
`lab_data` → `lab_util` → `lab_save` → `lab_player` → `lab_ui` → `lab_screens` → `lab_plot` →
`lab_belt` → `lab_storm` → `lab_manager` → `lab_events`. Остальные на время убирай в `.txt`.

## 4.7 Покупки за V-Bucks (In-Island Transactions)

1. Creator Portal → монетизация острова → включи In-Island Transactions.
2. Опиши товары и офферы (entitlement + entitlement_offer) из таблицы 1.21, модуль
   `/Fortnite.com/Marketplace`. Удобно начать с шаблона «In-Island Transactions Device Template»
   в Project Browser UEFN.
3. Покупка: `BuyOffer(Player, Offer)` из своей кнопки или стандартная витрина
   `ShowOffersDialog`.
4. Выдавать товар — **по событию изменения entitlement** (`GetEntitlementChangedEvent`), а не
   по результату `BuyOffer`: так советует Epic.
5. В обработчике вызови `Manager.GrantOffer(Player, НомерОффера)`: номер — индекс в `LabOffers`
   (0 = Личный шторм Радужный … 7 = Набор скрещивания). Выдача наград уже написана.
6. Для кнопки «Купить» в меню: создай класс-наследник `purchase_hook` с методом
   `RequestPurchase(Player, OfferIndex)`, который вызывает `BuyOffer`, и присвой его
   `Manager.PurchaseHook`.
7. Постоянные покупки (наборы) при входе игрока сверяй через `GetPurchasedEntitlements` и
   восстанавливай только флаг: `S.Data.GrantUnlock(Unlock_LabPack)` или
   `S.Data.GrantUnlock(Unlock_FusionPack)`. Расходники (штормы) повторно не выдавай.

Случайных товаров нет, поэтому `PaidRandomItem` не нужен. Если добавишь случайный — ставь
`PaidRandomItem = true` и показывай шансы до покупки.
