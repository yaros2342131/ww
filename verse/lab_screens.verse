# Экраны меню. Каждая функция возвращает menu_screen: заголовок, строки и кнопки с кодами действий.
# Сами действия выполняет lab_manager_device.OnMenuAction.
using { /Verse.org/Simulation }

LabPageSize:int = 8

UnitLabel(D:lab_player, R:brainrot_rec, Week:int)<transacts>:string =
    Where := if (R.Slot >= 0) then " [подиум]" else ""
    Comp := if (ContainsInt(D.Companions, R.Uid)?) then " [компаньон]" else ""
    Ideal := if (R.Ideal?) then " ИДЕАЛЬНЫЙ" else ""
    "{BrainrotTitle(R.Id)} · {VariantName(R.Variant)}{Ideal} · {FormatNum(D.UnitIncome(R, Week))}/с{Where}{Comp}"

PageButtons(Action:int, Page:int, Total:int)<transacts>:[]menu_button =
    var Out:[]menu_button = array{}
    if (Page > 0):
        set Out += array{menu_button{Label := "< Назад", Action := Action, Arg := Page - 1}}
    if ((Page + 1) * LabPageSize < Total):
        set Out += array{menu_button{Label := "Далее >", Action := Action, Arg := Page + 1}}
    Out

# Сначала те, кто на подиуме, потом запас
SortedBrainrots(D:lab_player)<transacts>:[]brainrot_rec =
    (for (R : D.Brainrots, R.Slot >= 0): R) + (for (R : D.Brainrots, R.Slot < 0): R)

PageOf(All:[]brainrot_rec, Page:int)<transacts>:[]brainrot_rec =
    for (I -> R : All, I >= Page * LabPageSize, I < (Page + 1) * LabPageSize): R

PerkText(Perk:int)<transacts>:string =
    if (Perk = Perk_HatchSpeed):
        "быстрее вылупление"
    else if (Perk = Perk_PickaxeCrit):
        "шанс крита кирки"
    else if (Perk = Perk_BeltDiscount):
        "скидка на капсулы"
    else if (Perk = Perk_LikesBonus):
        "больше Лайков"
    else if (Perk = Perk_VariantUp):
        "шанс вылупиться на вариант выше"
    else if (Perk = Perk_CashBonus):
        "больше Кэша"
    else if (Perk = Perk_OfflineBonus):
        "больше офлайн-дохода"
    else if (Perk = Perk_TourSpeed):
        "быстрее гастроли"
    else if (Perk = Perk_FusionSpeed):
        "быстрее скрещивание"
    else if (Perk = Perk_HypeBonus):
        "больше очков Хайпа"
    else if (Perk = Perk_IdealLuck):
        "шанс Идеального"
    else:
        "особый перк иконы"

# ---------------------------------------------------------------- главное меню
MainScreen(D:lab_player, Week:int)<transacts>:menu_screen =
    OnPodium := for (R : D.Brainrots, R.Slot >= 0): R
    menu_screen:
        Title := "БРЕЙНРОТ ЛАБОРАТОРИЯ"
        Lines := array:
            "Кэш: {FormatNum(D.Cash)} · Лайки: {D.Likes} · Кристаллы: {D.Crystals}"
            "Перерождение: {D.Rebirth} · Вирусных взрывов: {D.SuperRebirths}"
            "Брейнротов: {D.Brainrots.Length} · на подиуме {OnPodium.Length}/{D.SlotCount()} · Мемопедия {D.Discovered.Length}/{LabBrainrots.Length}"
            "Скрещивание, Мем-автомат и Гастроли — у станций в центре карты"
        Buttons := array:
            menu_button{Label := "Запас и подиум", Action := Act_Storage, Arg := 0}
            menu_button{Label := "Перерождение", Action := Act_Rebirth, Arg := 0}
            menu_button{Label := "Задания дня", Action := Act_Quests, Arg := 0}
            menu_button{Label := "Мемопедия", Action := Act_Dex, Arg := 0}
            menu_button{Label := "Хайп-магазин", Action := Act_Shop, Arg := 0}
            menu_button{Label := "Магазин (V-Bucks)", Action := Act_Offers, Arg := 0}
            menu_button{Label := "Лучшая расстановка", Action := Act_AutoArrange, Arg := 0}
            menu_button{Label := "Домой", Action := Act_Home, Arg := 0}

# ---------------------------------------------------------------- запас
StorageScreen(D:lab_player, Page:int, Week:int)<transacts>:menu_screen =
    All := SortedBrainrots(D)
    Items := for (R : PageOf(All, Page)):
        menu_button{Label := UnitLabel(D, R, Week), Action := Act_Unit, Arg := R.Uid}
    Nav := PageButtons(Act_Storage, Page, All.Length)
    Extra := array{menu_button{Label := "Лучшая расстановка", Action := Act_AutoArrange, Arg := 0}, menu_button{Label := "Меню", Action := Act_Main, Arg := 0}}
    menu_screen:
        Title := "ЗАПАС И ПОДИУМ · стр. {Page + 1}"
        Lines := array:
            "Мест на подиуме: {D.SlotCount()} · брейнротов всего: {All.Length}"
            "Нажми на брейнрота: поставить, улучшить, продать, взять в компаньоны"
        Buttons := Items + Nav + Extra

UnitScreen(D:lab_player, Uid:int, Week:int)<transacts>:menu_screen =
    if (R := D.FindByUid[Uid]):
        Def := GetDef(R.Id)
        PerkLine := if (Fam := LabFamilies[Def.Family]) then "Как компаньон: {PerkText(Fam.Perk)}" else ""
        Cost := D.UpgradeCost(R)
        var Buttons:[]menu_button = array{}
        if (R.Slot >= 0):
            set Buttons += array{menu_button{Label := "Убрать с подиума", Action := Act_Unplace, Arg := Uid}}
        else:
            set Buttons += array{menu_button{Label := "На подиум", Action := Act_Place, Arg := Uid}}
        if (D.CanUpgrade[R, Week]):
            set Buttons += array{menu_button{Label := "Улучшить за {Cost} Лайков", Action := Act_Upgrade, Arg := Uid}}
        set Buttons += array{menu_button{Label := "Продать: +{FormatNum(D.SellCash(R))} и {D.SellLikes(R)} Лайков", Action := Act_Sell, Arg := Uid}}
        CompLabel := if (ContainsInt(D.Companions, Uid)?) then "Отпустить компаньона" else "Взять в компаньоны"
        set Buttons += array{menu_button{Label := CompLabel, Action := Act_Companion, Arg := Uid}}
        set Buttons += array{menu_button{Label := "< Запас", Action := Act_Storage, Arg := 0}}
        UpgradeLine := if (Cost > 0) then "Следующий вариант: {Cost} Лайков (у тебя {D.Likes})" else "Максимальный вариант"
        menu_screen:
            Title := "{Def.Title}"
            Lines := array:
                "{RarityName(R.Id)} · {VariantName(R.Variant)} · семья {FamilyName(R.Id)}"
                "Доход: {FormatNum(D.UnitIncome(R, Week))}/с"
                UpgradeLine
                PerkLine
            Buttons := Buttons
    else:
        StorageScreen(D, 0, Week)

# ---------------------------------------------------------------- перерождение
RebirthScreen(D:lab_player, Week:int)<transacts>:menu_screen =
    var Lines:[]string = array{}
    var Buttons:[]menu_button = array{}
    if (D.Rebirth >= LabRebirthLevels):
        set Lines += array{"Все {LabRebirthLevels} перерождений пройдены!", "Дальше — Вирусный взрыв"}
    else:
        Req := D.NextReq()
        set Lines += array{"Цена: {FormatNum(D.RebirthCost())} (у тебя {FormatNum(D.Cash)})", "Нужны брейнроты (вариант не ниже):"}
        for (I -> Id : Req.Ids, V := Req.Variants[I]):
            Need := D.ReqVariant(V)
            Mark := if (D.HasAtLeast(Id, Need)?) then "[+]" else "[ ]"
            set Lines += array{"  {Mark} {BrainrotTitle(Id)} — {VariantName(Need)}"}
        Bonus := FloorInt((LabRebirthIncomeMult - 1.0) * 100.0 + 0.5)
        set Lines += array{"Награда: +{Bonus}% ко всему доходу, +1 место на подиуме. Кэш сгорит, брейнроты останутся"}
        if (D.CanRebirth[]):
            set Buttons += array{menu_button{Label := "ПЕРЕРОДИТЬСЯ", Action := Act_DoRebirth, Arg := 0}}
    if (D.Rebirth >= LabSuperUnlockRebirth):
        set Buttons += array{menu_button{Label := "Вирусный взрыв", Action := Act_Super, Arg := 0}}
    set Buttons += array{menu_button{Label := "Меню", Action := Act_Main, Arg := 0}}
    menu_screen{Title := "ПЕРЕРОЖДЕНИЕ {D.Rebirth} -> {D.Rebirth + 1}", Lines := Lines, Buttons := Buttons}

SuperScreen(D:lab_player, Week:int)<transacts>:menu_screen =
    var Lines:[]string = array{"Сбросит перерождения и Кэш. Брейнроты, Лайки и кристаллы останутся."}
    Bonus := FloorInt((LabSuperIncomeMult - 1.0) * 100.0 + 0.5)
    set Lines += array{"Получишь {D.SuperCrystals()} Хайп-кристаллов и навсегда +{Bonus}% дохода"}
    set Lines += array{"Требования перерождений станут на вариант выше"}
    if (Week < LabSuperFromWeek):
        set Lines += array{"Откроется с {LabSuperFromWeek}-й недели после запуска"}
    else if (not D.HasRainbowLegendary()?):
        set Lines += array{"Нужен хотя бы один Радужный легендарный брейнрот"}
    var Buttons:[]menu_button = array{}
    if (D.CanSuper[Week]):
        set Buttons += array{menu_button{Label := "ВЗОРВАТЬ!", Action := Act_DoSuper, Arg := 0}}
    set Buttons += array{menu_button{Label := "< Перерождение", Action := Act_Rebirth, Arg := 0}}
    menu_screen{Title := "ВИРУСНЫЙ ВЗРЫВ", Lines := Lines, Buttons := Buttons}

# ---------------------------------------------------------------- скрещивание
FusionScreen(D:lab_player, Page:int, Week:int, Now:float)<transacts>:menu_screen =
    var Lines:[]string = array{}
    var Buttons:[]menu_button = array{}
    if (Week < LabFusionWeek):
        set Lines += array{"Лаборатория скрещивания откроется на {LabFusionWeek}-й неделе после запуска"}
    else if (D.Rebirth < LabFusionUnlockRebirth):
        set Lines += array{"Нужно перерождение {LabFusionUnlockRebirth}"}
    else:
        for (T : D.Fusions, T.Active?):
            set Lines += array{"В колбе: {BrainrotTitle(T.Kind)} ({VariantName(T.Variant)}) · {FormatTime(T.EndsAt - Now)}"}
        P := D.FusionPreview(Week)
        set Lines += array{P.Note}
        if (P.Ok?):
            set Lines += array{"Цена: {FormatNum(D.FusionCost(P))} · время {FormatTime(P.Minutes * 60.0)}"}
            if (D.FreeFusion() >= 0):
                set Buttons += array{menu_button{Label := "СКРЕСТИТЬ", Action := Act_FusionStart, Arg := 0}}
            else:
                set Lines += array{"Все колбы заняты"}
        All := SortedBrainrots(D)
        for (R : PageOf(All, Page)):
            Mark := if (ContainsInt(D.FusionPick, R.Uid)?) then "[x] " else "[ ] "
            set Buttons += array{menu_button{Label := "{Mark}{BrainrotTitle(R.Id)} · {VariantName(R.Variant)}", Action := Act_FusionPick, Arg := R.Uid}}
        set Buttons += PageButtons(Act_Fusion, Page, All.Length)
        set Buttons += array{menu_button{Label := "Сбросить выбор", Action := Act_FusionClear, Arg := 0}}
    menu_screen{Title := "СКРЕЩИВАНИЕ", Lines := Lines, Buttons := Buttons}

# ---------------------------------------------------------------- мем-автомат
LuckyScreen(D:lab_player, Page:int, Week:int, Day:int)<transacts>:menu_screen =
    var Lines:[]string = array{}
    var Buttons:[]menu_button = array{}
    if (D.LuckyDay = Day):
        set Lines += array{"Сегодня автомат уже крутили. Приходи завтра!"}
    else:
        set Lines += array{"Раз в день бесплатно: выбери брейнрота и попробуй поднять его вариант."}
        set Lines += array{"Не повезло — ничего не теряешь."}
        All := SortedBrainrots(D)
        for (R : PageOf(All, Page), Next := LabVariants[R.Variant + 1], Next.Week <= Week, P := LabLuckyChance[R.Variant + 1]):
            Pct := FloorInt(P * 100.0)
            set Buttons += array{menu_button{Label := "{BrainrotTitle(R.Id)} -> {Next.Name} ({Pct}%)", Action := Act_LuckyRoll, Arg := R.Uid}}
        set Buttons += PageButtons(Act_Lucky, Page, All.Length)
    menu_screen{Title := "МЕМ-АВТОМАТ", Lines := Lines, Buttons := Buttons}

# ---------------------------------------------------------------- гастроли
ToursScreen(D:lab_player, Now:float, IncomeNow:float)<transacts>:menu_screen =
    var Lines:[]string = array{"Брейнроты едут на концерты и привозят Лайки и капсулы. Одни гастроли за раз."}
    var Busy:logic = false
    for (I -> T : D.Tours, T.Active?, Def := LabTours[I]):
        set Busy = true
        set Lines += array{"В пути: {Def.Name} · {FormatTime(T.EndsAt - Now)}"}
    var Buttons:[]menu_button = array{}
    if (not Busy?):
        for (I -> Def : LabTours):
            set Buttons += array{menu_button{Label := "{Def.Name} · {FormatTime(D.TourSeconds(I))} · {FormatNum(D.TourCost(I, IncomeNow))}", Action := Act_TourStart, Arg := I}}
    menu_screen{Title := "ГАСТРОЛИ", Lines := Lines, Buttons := Buttons}

# ---------------------------------------------------------------- хайп-магазин
ShopScreen(D:lab_player)<transacts>:menu_screen =
    Buttons := for (I -> It : LabHypeShop):
        L := D.ShopLevel(I)
        Label := if (L >= It.MaxLevel) then "{It.Name} — куплено" else "{It.Name} · ур. {L}/{It.MaxLevel} · {It.Cost} кр."
        menu_button{Label := Label, Action := Act_ShopBuy, Arg := I}
    menu_screen:
        Title := "ХАЙП-МАГАЗИН"
        Lines := array{"Хайп-кристаллы: {D.Crystals}. Покупки вечные — остаются после Вирусного взрыва."}
        Buttons := Buttons + array{menu_button{Label := "Меню", Action := Act_Main, Arg := 0}}

# ---------------------------------------------------------------- задания
QuestScreen(D:lab_player)<transacts>:menu_screen =
    Qs := D.TodayQuests()
    Names := array{"Лёгкое", "Среднее", "Сложное"}
    var Lines:[]string = array{"Новые задания каждый день в 00:00 UTC. Сложное даёт Хайп-кристалл."}
    var Buttons:[]menu_button = array{}
    for (I -> Q : Qs, P := D.QuestProgress[I], C := D.QuestClaimed[I], Name := Names[I]):
        Done := if (C?) then " — получено" else ""
        set Lines += array{"{Name}: {QuestTitle(Q)} · {Min(P, Q.Target)}/{Q.Target}{Done}"}
        if (D.QuestReady[I]):
            Likes := LabQuestLikes[I] or 0
            set Buttons += array{menu_button{Label := "Забрать: {Name} (+{Likes} Лайков)", Action := Act_QuestClaim, Arg := I}}
    set Buttons += array{menu_button{Label := "Меню", Action := Act_Main, Arg := 0}}
    menu_screen{Title := "ЗАДАНИЯ ДНЯ", Lines := Lines, Buttons := Buttons}

# ---------------------------------------------------------------- мемопедия
DexScreen(D:lab_player, Page:int, Week:int)<transacts>:menu_screen =
    Size := 10
    var Lines:[]string = array{"Открыто {D.Discovered.Length} из {LabBrainrots.Length} · Идеальных {D.IdealFound.Length}"}
    for (I -> Def : LabBrainrots, I >= Page * Size, I < (Page + 1) * Size):
        Fam := if (F := LabFamilies[Def.Family]) then F.Name else ""
        Rar := GetRarity(Def.Rarity).Name
        if (ContainsInt(D.Discovered, I)?):
            Ideal := if (ContainsInt(D.IdealFound, I)?) then " · есть Идеальный" else ""
            set Lines += array{"{Def.Title} — {Fam} — {Rar}{Ideal}"}
        else if (Def.Week > Week):
            set Lines += array{"??? — скоро"}
        else:
            var Hint:string = ""
            for (Rc : LabRecipes, Rc.Result = I):
                set Hint = " · рецепт: «{Rc.Hint}»"
            Where := if (Def.Source = 2) then " · только на ивенте" else ""
            set Lines += array{"??? — {Fam} — {Rar}{Hint}{Where}"}
    var Buttons:[]menu_button = array{}
    if (Page > 0):
        set Buttons += array{menu_button{Label := "< Назад", Action := Act_Dex, Arg := Page - 1}}
    if ((Page + 1) * Size < LabBrainrots.Length):
        set Buttons += array{menu_button{Label := "Далее >", Action := Act_Dex, Arg := Page + 1}}
    set Buttons += array{menu_button{Label := "Меню", Action := Act_Main, Arg := 0}}
    menu_screen{Title := "МЕМОПЕДИЯ · стр. {Page + 1}", Lines := Lines, Buttons := Buttons}

# ---------------------------------------------------------------- магазин V-Bucks
OffersScreen(Week:int)<transacts>:menu_screen =
    Buttons := for (I -> O : LabOffers, O.Week <= Week):
        menu_button{Label := "{O.Name} — {O.Price} V-Bucks", Action := Act_OfferBuy, Arg := I}
    Lines := for (O : LabOffers, O.Week <= Week): "{O.Name}: {O.Effect}"
    menu_screen:
        Title := "МАГАЗИН"
        Lines := array{"Все товары действуют только на этом острове. Всё, что даёт силу, можно получить и игрой."} + Lines
        Buttons := Buttons + array{menu_button{Label := "Меню", Action := Act_Main, Arg := 0}}
