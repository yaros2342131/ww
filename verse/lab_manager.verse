# Главное устройство острова. Ставится одно на карту.
# Связывает участки, конвейер, шторм, станции хаба, HUD и меню; раз в секунду начисляет доход,
# раз в 20 секунд сохраняет прогресс.
using { /Fortnite.com/Devices }
using { /Fortnite.com/Characters }
using { /Fortnite.com/Playspaces }
using { /Verse.org/Simulation }
using { /Verse.org/Random }
using { /UnrealEngine.com/Temporary/SpatialMath }
using { /UnrealEngine.com/Temporary/Diagnostics }

# ---------------------------------------------------------------- коды действий меню
Act_Close:int = 0
Act_Main:int = 1
Act_Storage:int = 2        # Arg = страница
Act_Unit:int = 3           # Arg = Uid
Act_Place:int = 4
Act_Unplace:int = 5
Act_Upgrade:int = 6
Act_Sell:int = 7
Act_Companion:int = 8
Act_AutoArrange:int = 9
Act_Rebirth:int = 10
Act_DoRebirth:int = 11
Act_Super:int = 12
Act_DoSuper:int = 13
Act_Fusion:int = 14        # Arg = страница
Act_FusionPick:int = 15    # Arg = Uid
Act_FusionClear:int = 16
Act_FusionStart:int = 17
Act_Lucky:int = 18         # Arg = страница
Act_LuckyRoll:int = 19     # Arg = Uid
Act_Tours:int = 20
Act_TourStart:int = 21     # Arg = номер тура
Act_Shop:int = 22
Act_ShopBuy:int = 23       # Arg = номер товара
Act_Quests:int = 24
Act_QuestClaim:int = 25    # Arg = номер задания
Act_Dex:int = 26           # Arg = страница
Act_Offers:int = 27
Act_OfferBuy:int = 28      # Arg = номер оффера
Act_Home:int = 29

# Всё, что относится к одному игроку в текущей сессии
lab_session := class:
    Data:lab_player
    Hud:lab_hud
    Menu:lab_menu
    var CompanionProps:[]creative_prop = array{}
    var CompanionKey:[]int = array{}
    var LastHit:float = 0.0

eliminated_handler := class:
    Manager:lab_manager_device
    Player:player

    OnEliminated(Result:elimination_result):void = Manager.OnEliminated(Player, Result)

# Запасной вариант, если офферы за V-Bucks ещё не подключены (см. docs/brainrot-lab/04-verse.md)
purchase_hook := class<abstract>:
    RequestPurchase(Player:player, OfferIndex:int):void

lab_manager_device := class(creative_device):
    @editable Plots:[]lab_plot_device = array{}
    @editable Belt:lab_belt_device = lab_belt_device{}
    @editable Storm:lab_storm_device = lab_storm_device{}

    # Ассеты-пропсы. Порядок BrainrotProps — как в config/brainrot_lab_tycoon.json (brainrots)
    @editable BrainrotProps:[]creative_prop_asset = array{}
    @editable PedestalProps:[]creative_prop_asset = array{}   # 7: базовый … космический
    @editable CapsuleProps:[]creative_prop_asset = array{}    # 6: обычная, редкая, эпическая, легендарная, мифическая, иконная
    @editable AuraProps:[]creative_prop_asset = array{}       # 0–1: аура «Идеального»

    # Управление
    @editable MenuKey:input_trigger_device = input_trigger_device{}
    @editable FusionButton:button_device = button_device{}
    @editable LuckyButton:button_device = button_device{}
    @editable TourButton:button_device = button_device{}
    @editable ShopButton:button_device = button_device{}
    @editable OffersButton:button_device = button_device{}
    @editable DexButton:button_device = button_device{}
    @editable QuestButton:button_device = button_device{}
    @editable HomeButton:button_device = button_device{}

    # Лайв-опс
    @editable LaunchEpochSeconds:float = 0.0    # Unix-время запуска: от него считается неделя контента
    @editable ForceWeek:int = -1                # для теста: какую неделю контента включить (−1 = по дате)
    @editable CarryStealOnElimination:logic = false   # выбил игрока с капсулой — забрал капсулу

    var Sessions:[player]lab_session = map{}
    var PurchaseHook:?purchase_hook = false

    OnBegin<override>()<suspends>:void =
        for (I -> P : Plots):
            P.Init(Self)
        Belt.Init(Self)
        Storm.Init(Self)
        MenuKey.PressedEvent.Subscribe(OnMenuKey)
        FusionButton.InteractedWithEvent.Subscribe(OnFusionButton)
        LuckyButton.InteractedWithEvent.Subscribe(OnLuckyButton)
        TourButton.InteractedWithEvent.Subscribe(OnTourButton)
        ShopButton.InteractedWithEvent.Subscribe(OnShopButton)
        OffersButton.InteractedWithEvent.Subscribe(OnOffersButton)
        DexButton.InteractedWithEvent.Subscribe(OnDexButton)
        QuestButton.InteractedWithEvent.Subscribe(OnQuestButton)
        HomeButton.InteractedWithEvent.Subscribe(OnHomeButton)
        FusionButton.SetInteractionText(LabText("Скрещивание"))
        LuckyButton.SetInteractionText(LabText("Мем-автомат"))
        TourButton.SetInteractionText(LabText("Гастроли"))
        ShopButton.SetInteractionText(LabText("Хайп-магазин"))
        OffersButton.SetInteractionText(LabText("Магазин"))
        DexButton.SetInteractionText(LabText("Мемопедия"))
        QuestButton.SetInteractionText(LabText("Задания дня"))
        HomeButton.SetInteractionText(LabText("Домой"))
        GetPlayspace().PlayerAddedEvent().Subscribe(OnPlayerAdded)
        GetPlayspace().PlayerRemovedEvent().Subscribe(OnPlayerRemoved)
        for (P : GetPlayspace().GetPlayers()):
            OnPlayerAdded(P)
        spawn{ SaveLoop() }
        loop:
            Sleep(1.0)
            Tick()

    # ------------------------------------------------ время и ивенты
    CurrentWeek():int =
        if (ForceWeek >= 0):
            return ForceWeek
        if (LaunchEpochSeconds <= 0.0):
            return 0
        Max(0, FloorInt((LabNow() - LaunchEpochSeconds) / 604800.0))

    # Сколько часов прошло с начала субботнего ивента (0 … 168)
    HoursIntoMainEvent(Now:float)<transacts>:float =
        Days := Mod[LabWeekday(Now) - LabMainEventWeekday + 7, 7] or 0
        var Off:float = Days * 24.0 + LabHourUtc(Now) - LabMainEventStartHourUtc * 1.0
        if (Off < 0.0):
            set Off += 168.0
        Off

    MainEventActive(Now:float)<transacts><decides>:void = HoursIntoMainEvent(Now) < LabMainEventHours
    MiniEventActive(Now:float)<transacts><decides>:void = LabWeekday(Now) = LabMiniEventWeekday

    HatchEventMult():float =
        Now := LabNow()
        if (MainEventActive[Now]) then LabMainEventHatchMult else 1.0

    LikesEventMult():float =
        Now := LabNow()
        if (MiniEventActive[Now]) then LabMiniEventLikesMult else 1.0

    IncomeMult():float =
        Now := LabNow()
        StormMult := if (Storm.IsActive()?) then LabStormIncomeMult else 1.0
        EventMult := if (MainEventActive[Now]) then LabMainEventIncomeMult else 1.0
        StormMult * EventMult

    EventLine(Now:float):string =
        if (MainEventActive[Now]):
            Left := (LabMainEventHours - HoursIntoMainEvent(Now)) * 3600.0
            "СУББОТНИЙ ИВЕНТ: доход x2, вылупление x2 · ещё {FormatTime(Left)}"
        else if (MiniEventActive[Now]):
            "ЧЕТВЕРГ: Мем-пиньята каждые 30 минут, Лайки x2"
        else:
            Left := (168.0 - HoursIntoMainEvent(Now)) * 3600.0
            "До субботнего ивента: {FormatTime(Left)}"

    # ------------------------------------------------ игроки
    OnPlayerAdded(P:player):void =
        if (Sessions[P]):
            return
        Data := lab_player{Player := P}
        if (Saved := LabSaves[P]):
            Data.LoadFrom(Saved)
        else:
            Data.EnsureArrays()
        S := lab_session{Data := Data, Hud := lab_hud{Player := P}, Menu := lab_menu{Player := P}}
        if (set Sessions[P] = S) {}
        Week := CurrentWeek()
        Data.FixSlots()
        Data.RecomputeIncome(Week)
        Offline := Data.ApplyOffline(LabNow())
        AssignPlot(S)
        S.Hud.Show()
        if (Offline > 0.0):
            S.Hud.Toast("Пока тебя не было, брейнроты заработали {FormatNum(Offline)}")
        else:
            S.Hud.Toast("Добро пожаловать в Брейнрот Лабораторию! Купи капсулу на конвейере в центре")
        if (FC := P.GetFortCharacter[]):
            FC.EliminatedEvent().Subscribe(eliminated_handler{Manager := Self, Player := P}.OnEliminated)
        spawn{ CompanionLoop(S) }
        SavePlayer(S)

    OnPlayerRemoved(P:player):void =
        if (S := Sessions[P]):
            if (C := S.Data.Carrying?):
                set S.Data.Carrying = false
                S.Data.AddReserve(C)
            SavePlayer(S)
            if (Plot := Plots[S.Data.PlotIndex]):
                Plot.Release()
            for (Pr : S.CompanionProps):
                Pr.Dispose()
            S.Menu.Close()
            S.Hud.Hide()
        var Rest:[player]lab_session = map{}
        for (K -> V : Sessions, K <> P):
            if (set Rest[K] = V) {}
        set Sessions = Rest

    AssignPlot(S:lab_session):void =
        var Done:logic = false
        for (I -> Plot : Plots, not Done?, Plot.IsFree[]):
            Plot.Assign(S.Data, I)
            set Done = true
        if (not Done?):
            S.Hud.Toast("Все лаборатории заняты — подожди, пока кто-то выйдет")

    SavePlayer(S:lab_session):void =
        Save := S.Data.ToSave(LabNow())
        if (set LabSaves[S.Data.Player] = Save) {}

    SaveLoop()<suspends>:void =
        loop:
            Sleep(20.0)
            for (P -> S : Sessions):
                SavePlayer(S)

    # ------------------------------------------------ каждую секунду
    Tick():void =
        Now := LabNow()
        Week := CurrentWeek()
        Mult := IncomeMult()
        Storm.Tick(Sessions.Length)
        Belt.UpdateBoard(Week)
        StormText := Storm.Line()
        Event := EventLine(Now)
        for (P -> S : Sessions):
            D := S.Data
            Income := D.IncomePerSec(Mult)
            set D.Cash += Income
            set D.PlaySeconds += 1.0
            CheckTimers(S, Now, Week)
            UpdateHud(S, Income)
            S.Hud.SetStorm(StormText)
            S.Hud.SetEvent(Event)
            if (Plot := Plots[D.PlotIndex]):
                Plot.RefreshIncubators(Now)
                Plot.RefreshBoard(FormatNum(Income))

    UpdateHud(S:lab_session, Income:float):void =
        D := S.Data
        CashLine := "Кэш: {FormatNum(D.Cash)}   +{FormatNum(Income)}/с"
        Info := "Лайки: {D.Likes}   Кристаллы: {D.Crystals}   Перерождение: {D.Rebirth}"
        Hands := if (C := D.Carrying?) then "В руках: {BrainrotTitle(C.Id)} ({VariantName(C.Variant)}) — неси в инкубатор" else "Руки пустые · капсул в запасе: {D.Reserve.Length}"
        Hint := if (D.CanRebirth[]) then "Можно переродиться! Станция на участке" else "До перерождения: {FormatNum(Max(0.0, D.RebirthCost() - D.Cash))} · меню — клавиша"
        S.Hud.SetStats(CashLine, Info, Hands, Hint)

    # Инкубаторы, колбы скрещивания и гастроли, у которых вышло время
    CheckTimers(S:lab_session, Now:float, Week:int):void =
        D := S.Data
        for (I -> T : D.Incubators, T.Active?, T.EndsAt <= Now):
            D.SetIncubator(I, timer_rec{})
            Hatch(S, T.Kind, T.Variant, Week, true)
        for (I -> T : D.Fusions, T.Active?, T.EndsAt <= Now):
            D.SetFusion(I, timer_rec{})
            Hatch(S, T.Kind, T.Variant, Week, false)
        for (I -> T : D.Tours, T.Active?, T.EndsAt <= Now):
            D.SetTour(I, timer_rec{})
            FinishTour(S, I, Week)

    # ------------------------------------------------ вылупление
    Hatch(S:lab_session, Id:int, Variant:int, Week:int, FromIncubator:logic):void =
        D := S.Data
        var V:int = Variant
        if (FromIncubator?, V < VariantIdx_Rainbow, Chance(D.VariantUpChance())?):
            set V += 1
        Ideal := Chance(D.IdealChance())
        IsNew := logic{not ContainsInt(D.Discovered, Id)?}
        Rec := D.AddBrainrot(Id, V, Ideal, Week)
        set D.TotalHatched += 1
        Day := LabDay(LabNow())
        D.AddQuest(Quest_Hatch, 1, Day)
        if (RarityOf(Id) >= RarityIdx_Epic):
            D.AddQuest(Quest_HatchEpic, 1, Day)
        Storm.AddPoints(option{D.Player}, GetRarity(RarityOf(Id)).Hype * D.HypeMult())
        Title := "{BrainrotTitle(Id)} ({VariantName(V)})"
        if (Rec.Slot >= 0):
            S.Hud.Toast("{Title} вылупился и встал на подиум!")
        else:
            S.Hud.Toast("{Title} вылупился! Подиум полон — он в запасе")
        if (IsNew?):
            S.Hud.Toast("Новый вид в Мемопедии!")
        PlotNo := D.PlotIndex + 1
        if (Ideal?):
            AnnounceAll("ИДЕАЛЬНЫЙ {Title} вылупился в лаборатории #{PlotNo}!")
        else if (RarityOf(Id) >= RarityIdx_Mythic):
            AnnounceAll("{RarityName(Id)} {Title} вылупился в лаборатории #{PlotNo}!")
        CheckFamilies(S, Week)
        RefreshPlot(S)

    # Семья впервые собрана целиком — очки шторму и сообщение
    CheckFamilies(S:lab_session, Week:int):void =
        D := S.Data
        Ids := D.PodiumIds()
        for (F -> Fam : LabFamilies, F <> FamilyIdx_Icons, not ContainsInt(D.FamiliesDone, F)?, CountPresent(Fam.Members, Ids) = Fam.Members.Length):
            set D.FamiliesDone += array{F}
            Storm.AddPoints(option{D.Player}, LabStormFamilyPoints * D.HypeMult())
            AnnounceAll("Лаборатория #{D.PlotIndex + 1} собрала всю семью «{Fam.Name}»!")

    RefreshPlot(S:lab_session):void =
        if (Plot := Plots[S.Data.PlotIndex]):
            Plot.RefreshPodium()

    FinishTour(S:lab_session, I:int, Week:int):void =
        if (T := LabTours[I]):
            D := S.Data
            Likes := D.LikesGain(GetRandomInt(T.LikesMin, T.LikesMax), LikesEventMult())
            set D.Likes += Likes
            var Text:string = "Гастроли «{T.Name}» закончились: +{Likes} Лайков"
            if (Chance(T.CapsuleChance)?):
                Rarity := if (T.EpicPlus?) then PickWeighted(LabStormCapsuleWeights) else PickWeighted(for (R : LabRarities): R.Weight)
                Id := RandomBrainrot(Rarity, Week)
                D.AddReserve(capsule_rec{Id := Id, Variant := 0})
                set Text += " и капсула {BrainrotTitle(Id)} в запасе"
            S.Hud.Toast(Text)

    # ------------------------------------------------ конвейер и инкубаторы
    BeltPool(Rarity:int, Week:int)<transacts>:[]int =
        for (I -> B : LabBrainrots, B.Rarity = Rarity, B.Source = 0, B.Week <= Week): I

    # Случайный брейнрот с конвейера нужной редкости; если таких ещё нет — редкостью ниже
    RandomBrainrot(Rarity:int, Week:int):int =
        var R:int = Rarity
        loop:
            if (BeltPool(R, Week).Length > 0 or R <= 0):
                break
            set R -= 1
        Pool := BeltPool(R, Week)
        Pool[GetRandomInt(0, Max(0, Pool.Length - 1))] or 0

    TryBuyCapsule(Agent:agent, Id:int, Variant:int):logic =
        if (P := player[Agent], S := Sessions[P]):
            D := S.Data
            if (D.Carrying?):
                S.Hud.Toast("Руки заняты — сначала отнеси капсулу в инкубатор")
                return false
            Price := D.CapsulePrice(Id, Variant)
            if (D.Cash < Price):
                S.Hud.Toast("Не хватает Кэша: нужно {FormatNum(Price)}")
                return false
            set D.Cash -= Price
            var V:int = Variant
            # «Личный шторм» за V-Bucks: вариант не ниже купленного
            if (First := D.PersonalStorms[0]):
                set V = Max(V, First)
                set D.PersonalStorms = for (I -> X : D.PersonalStorms, I > 0): X
            # «Удача конвейера» из Хайп-магазина: +2% за уровень, что капсула станет на вариант выше
            if (V < VariantIdx_Rainbow, Chance(D.ShopLevel(Shop_BeltLuck) * 0.02)?):
                set V += 1
            set D.Carrying = option{capsule_rec{Id := Id, Variant := V}}
            D.AddQuest(Quest_BuyCapsule, 1, LabDay(LabNow()))
            S.Hud.Toast("Куплено: {BrainrotTitle(Id)} ({VariantName(V)}). Неси в свой инкубатор!")
            return true
        false

    IncubatorInteract(Plot:lab_plot_device, Agent:agent, Index:int):void =
        if (P := player[Agent], S := Sessions[P]):
            if (Owner := Plot.Owner?, Owner.Player = P):
                D := S.Data
                if (Index >= D.IncubatorCount()):
                    S.Hud.Toast("Этот инкубатор закрыт. Открой его в Хайп-магазине")
                else if (T := D.Incubators[Index], T.Active?):
                    Boost(S, Plot, Index)
                else:
                    Taken := D.TakeCapsule()
                    if (C := Taken?):
                        Sec := D.HatchSeconds(C.Id, HatchEventMult())
                        Now := LabNow()
                        D.SetIncubator(Index, timer_rec{Active := true, Kind := C.Id, Variant := C.Variant, EndsAt := Now + Sec, Total := Sec})
                        Plot.RefreshIncubators(Now)
                        S.Hud.Toast("Капсула в инкубаторе! Бей по нему киркой — вылупится быстрее")
                    else:
                        S.Hud.Toast("Нет капсулы: купи её на конвейере в центре")
            else:
                # чужой инкубатор: удар помогает хозяину, очки шторма — тебе
                Boost(S, Plot, Index)

    IncubatorHit(Plot:lab_plot_device, Agent:agent, Index:int):void =
        if (P := player[Agent], S := Sessions[P]):
            Boost(S, Plot, Index)

    Boost(Hitter:lab_session, Plot:lab_plot_device, Index:int):void =
        Now := GetSimulationElapsedTime()
        if (Now - Hitter.LastHit < 0.2):
            return
        set Hitter.LastHit = Now
        if (Owner := Plot.Owner?, T := Owner.Incubators[Index], T.Active?):
            HD := Hitter.Data
            Crit := Chance(HD.CritChance())
            Amount := if (Crit?) then LabHitSpeedup * HD.CritMult() else LabHitSpeedup
            Owner.SetIncubator(Index, timer_rec{Active := true, Kind := T.Kind, Variant := T.Variant, EndsAt := T.EndsAt - Amount, Total := T.Total})
            Storm.AddPoints(option{HD.Player}, LabStormHitPoints * HD.HypeMult())
            HD.AddQuest(Quest_PickaxeHit, 1, LabDay(LabNow()))
            if (Crit?):
                Hitter.Hud.Toast("КРИТ! Минус {FloorInt(Amount)} с")

    OnEliminated(Victim:player, Result:elimination_result):void =
        if (CarryStealOnElimination?, VS := Sessions[Victim], C := VS.Data.Carrying?):
            set VS.Data.Carrying = false
            var Stolen:logic = false
            # новичков первые 30 минут не грабим
            if (VS.Data.PlaySeconds >= 1800.0, KillerChar := Result.EliminatingCharacter?, KillerAgent := KillerChar.GetAgent[], Killer := player[KillerAgent], KS := Sessions[Killer], not KS.Data.Carrying?):
                set KS.Data.Carrying = option{C}
                set Stolen = true
                KS.Hud.Toast("Ты выбил капсулу: {BrainrotTitle(C.Id)}!")
                VS.Hud.Toast("У тебя выбили капсулу!")
            if (not Stolen?):
                VS.Data.AddReserve(C)

    # ------------------------------------------------ пропсы
    SpawnOne(Asset:creative_prop_asset, Pos:vector3, Rot:rotation):?creative_prop =
        Res := SpawnProp(Asset, Pos, Rot)
        Res(0)

    SpawnCapsuleProp(Rarity:int, Pos:vector3):?creative_prop =
        if (Asset := CapsuleProps[Rarity]) then SpawnOne(Asset, Pos, IdentityRotation()) else false

    SpawnPodiumProps(Id:int, Variant:int, Ideal:logic, Pos:vector3, Rot:rotation, Height:float):[]creative_prop =
        var Out:[]creative_prop = array{}
        Top := Pos + vector3{Z := Height}
        if (Asset := PedestalProps[Variant]):
            Spawned := SpawnOne(Asset, Pos, Rot)
            if (Pr := Spawned?):
                set Out += array{Pr}
        if (Asset := BrainrotProps[Id]):
            Spawned := SpawnOne(Asset, Top, Rot)
            if (Pr := Spawned?):
                set Out += array{Pr}
        if (Ideal?, Asset := AuraProps[0]):
            Spawned := SpawnOne(Asset, Top, Rot)
            if (Pr := Spawned?):
                set Out += array{Pr}
        Out

    # Компаньоны идут за игроком чуть сзади
    CompanionLoop(S:lab_session)<suspends>:void =
        P := S.Data.Player
        loop:
            if (not P.IsActive[]):
                break
            SyncCompanions(S)
            if (FC := P.GetFortCharacter[]):
                T := FC.GetTransform()
                for (I -> Pr : S.CompanionProps):
                    Side := if (I = 0) then 1.0 else -1.0
                    Target := T.Translation + T.Rotation.RotateVector(vector3{X := -160.0, Y := 120.0 * Side, Z := 0.0})
                    spawn{ MoveProp(Pr, Target, T.Rotation, 0.35) }
            Sleep(0.3)
        for (Pr : S.CompanionProps):
            Pr.Dispose()

    MoveProp(Pr:creative_prop, Pos:vector3, Rot:rotation, Time:float)<suspends>:void =
        if (Pr.IsValid[]):
            Pr.MoveTo(Pos, Rot, Time)

    SyncCompanions(S:lab_session):void =
        D := S.Data
        Key := for (Uid : D.Companions, R := D.FindByUid[Uid]): R.Id * 10 + R.Variant
        if (Key <> S.CompanionKey):
            for (Pr : S.CompanionProps):
                Pr.Dispose()
            set S.CompanionProps = array{}
            if (FC := D.Player.GetFortCharacter[]):
                T := FC.GetTransform()
                for (Uid : D.Companions, R := D.FindByUid[Uid], Asset := BrainrotProps[R.Id]):
                    Spawned := SpawnOne(Asset, T.Translation + vector3{X := -160.0}, T.Rotation)
                    if (Pr := Spawned?):
                        set S.CompanionProps += array{Pr}
            set S.CompanionKey = Key

    # ------------------------------------------------ сообщения
    AnnounceAll(Text:string):void =
        for (P -> S : Sessions):
            S.Hud.Toast(Text)

    OnStormStart(Winners:[]player):void =
        AnnounceAll("ХАЙП-ШТОРМ! 3 минуты: доход x2, конвейер быстрее, редкие капсулы чаще")
        Week := CurrentWeek()
        Day := LabDay(LabNow())
        for (P : Winners, S := Sessions[P]):
            Id := RandomBrainrot(PickWeighted(LabStormCapsuleWeights), Week)
            S.Data.AddReserve(capsule_rec{Id := Id, Variant := 0})
            S.Data.AddQuest(Quest_Storm, 1, Day)
            S.Hud.Toast("За вклад в шторм: капсула {BrainrotTitle(Id)} в запасе!")

    OnStormEnd():void = AnnounceAll("Шторм закончился. Копим хайп дальше!")

    # ------------------------------------------------ станции хаба и меню
    OnMenuKey(Agent:agent):void =
        if (P := player[Agent], S := Sessions[P]):
            if (S.Menu.IsOpen()?):
                S.Menu.Close()
            else:
                ShowScreen(S, Act_Main, 0)

    OnFusionButton(Agent:agent):void = OpenScreen(Agent, Act_Fusion, 0)
    OnLuckyButton(Agent:agent):void = OpenScreen(Agent, Act_Lucky, 0)
    OnTourButton(Agent:agent):void = OpenScreen(Agent, Act_Tours, 0)
    OnShopButton(Agent:agent):void = OpenScreen(Agent, Act_Shop, 0)
    OnOffersButton(Agent:agent):void = OpenScreen(Agent, Act_Offers, 0)
    OnDexButton(Agent:agent):void = OpenScreen(Agent, Act_Dex, 0)
    OnQuestButton(Agent:agent):void = OpenScreen(Agent, Act_Quests, 0)
    OnHomeButton(Agent:agent):void = TeleportHome(Agent)

    OpenScreen(Agent:agent, Action:int, Arg:int):void =
        if (P := player[Agent], S := Sessions[P]):
            ShowScreen(S, Action, Arg)

    TeleportHome(Agent:agent):void =
        if (P := player[Agent], S := Sessions[P], Plot := Plots[S.Data.PlotIndex]):
            Plot.TeleportHome(Agent)

    ShowScreen(S:lab_session, Action:int, Arg:int):void =
        D := S.Data
        Week := CurrentWeek()
        Now := LabNow()
        D.EnsureQuestDay(LabDay(Now))
        var Screen:menu_screen = MainScreen(D, Week)
        if (Action = Act_Storage):
            set Screen = StorageScreen(D, Arg, Week)
        else if (Action = Act_Unit):
            set Screen = UnitScreen(D, Arg, Week)
        else if (Action = Act_Rebirth):
            set Screen = RebirthScreen(D, Week)
        else if (Action = Act_Super):
            set Screen = SuperScreen(D, Week)
        else if (Action = Act_Fusion):
            set Screen = FusionScreen(D, Arg, Week, Now)
        else if (Action = Act_Lucky):
            set Screen = LuckyScreen(D, Arg, Week, LabDay(Now))
        else if (Action = Act_Tours):
            set Screen = ToursScreen(D, Now, D.IncomePerSec(1.0))
        else if (Action = Act_Shop):
            set Screen = ShopScreen(D)
        else if (Action = Act_Quests):
            set Screen = QuestScreen(D)
        else if (Action = Act_Dex):
            set Screen = DexScreen(D, Arg, Week)
        else if (Action = Act_Offers):
            set Screen = OffersScreen(Week)
        S.Menu.Show(Self, Screen)

    OnMenuAction(P:player, Action:int, Arg:int):void =
        if (S := Sessions[P]):
            D := S.Data
            Week := CurrentWeek()
            Now := LabNow()
            Day := LabDay(Now)
            if (Action = Act_Close):
                S.Menu.Close()
            else if (Action = Act_Home):
                S.Menu.Close()
                TeleportHome(P)
            else if (Action = Act_Place):
                Slot := D.FreeSlot()
                if (Slot < 0):
                    S.Hud.Toast("Подиум полон — сначала убери кого-нибудь")
                else if (R := D.FindByUid[Arg]):
                    D.ReplaceRec(WithSlot(R, Slot))
                    D.RecomputeIncome(Week)
                    CheckFamilies(S, Week)
                    RefreshPlot(S)
                ShowScreen(S, Act_Unit, Arg)
            else if (Action = Act_Unplace):
                if (R := D.FindByUid[Arg]):
                    D.ReplaceRec(WithSlot(R, -1))
                    D.RecomputeIncome(Week)
                    RefreshPlot(S)
                ShowScreen(S, Act_Unit, Arg)
            else if (Action = Act_Upgrade):
                if (R := D.FindByUid[Arg], D.CanUpgrade[R, Week]):
                    set D.Likes -= D.UpgradeCost(R)
                    D.ReplaceRec(WithVariant(R, R.Variant + 1))
                    D.RecomputeIncome(Week)
                    D.AddQuest(Quest_Upgrade, 1, Day)
                    RefreshPlot(S)
                    S.Hud.Toast("{BrainrotTitle(R.Id)} теперь {VariantName(R.Variant + 1)}!")
                ShowScreen(S, Act_Unit, Arg)
            else if (Action = Act_Sell):
                if (R := D.FindByUid[Arg]):
                    Likes := D.LikesGain(D.SellLikes(R), LikesEventMult())
                    set D.Cash += D.SellCash(R)
                    set D.Likes += Likes
                    D.RemoveUid(Arg, Week)
                    D.AddQuest(Quest_Sell, 1, Day)
                    RefreshPlot(S)
                    S.Hud.Toast("Продано: +{FormatNum(D.SellCash(R))} Кэша и {Likes} Лайков")
                ShowScreen(S, Act_Storage, 0)
            else if (Action = Act_Companion):
                if (ContainsInt(D.Companions, Arg)?):
                    set D.Companions = for (C : D.Companions, C <> Arg): C
                else if (D.Companions.Length < D.CompanionSlots()):
                    set D.Companions += array{Arg}
                else:
                    set D.Companions = (for (I -> C : D.Companions, I > 0): C) + array{Arg}
                ShowScreen(S, Act_Unit, Arg)
            else if (Action = Act_AutoArrange):
                D.AutoArrange(Week)
                CheckFamilies(S, Week)
                RefreshPlot(S)
                ShowScreen(S, Act_Storage, 0)
            else if (Action = Act_DoRebirth):
                if (D.CanRebirth[]):
                    D.DoRebirth(Week)
                    RefreshPlot(S)
                    AnnounceAll("Лаборатория #{D.PlotIndex + 1} переродилась! Перерождение {D.Rebirth}")
                ShowScreen(S, Act_Rebirth, 0)
            else if (Action = Act_DoSuper):
                if (D.CanSuper[Week]):
                    Gain := D.SuperCrystals()
                    D.DoSuper(Week)
                    RefreshPlot(S)
                    AnnounceAll("ВИРУСНЫЙ ВЗРЫВ в лаборатории #{D.PlotIndex + 1}! +{Gain} Хайп-кристаллов")
                ShowScreen(S, Act_Rebirth, 0)
            else if (Action = Act_FusionPick):
                if (ContainsInt(D.FusionPick, Arg)?):
                    set D.FusionPick = for (C : D.FusionPick, C <> Arg): C
                else if (D.FusionPick.Length < 3):
                    set D.FusionPick += array{Arg}
                ShowScreen(S, Act_Fusion, 0)
            else if (Action = Act_FusionClear):
                set D.FusionPick = array{}
                ShowScreen(S, Act_Fusion, 0)
            else if (Action = Act_FusionStart):
                StartFusion(S, Week, Now)
                ShowScreen(S, Act_Fusion, 0)
            else if (Action = Act_LuckyRoll):
                LuckyRoll(S, Arg, Week, Day)
                ShowScreen(S, Act_Lucky, 0)
            else if (Action = Act_TourStart):
                StartTour(S, Arg, Now)
                ShowScreen(S, Act_Tours, 0)
            else if (Action = Act_ShopBuy):
                BuyShopItem(S, Arg, Week)
                ShowScreen(S, Act_Shop, 0)
            else if (Action = Act_QuestClaim):
                ClaimQuest(S, Arg)
                ShowScreen(S, Act_Quests, 0)
            else if (Action = Act_OfferBuy):
                if (Hook := PurchaseHook?):
                    Hook.RequestPurchase(P, Arg)
                else:
                    S.Hud.Toast("Покупки за V-Bucks ещё не подключены (см. документацию)")
            else:
                ShowScreen(S, Action, Arg)

    StartFusion(S:lab_session, Week:int, Now:float):void =
        D := S.Data
        Preview := D.FusionPreview(Week)
        Slot := D.FreeFusion()
        Cost := D.FusionCost(Preview)
        if (not Preview.Ok?):
            S.Hud.Toast(Preview.Note)
        else if (Slot < 0):
            S.Hud.Toast("Все колбы заняты")
        else if (D.Cash < Cost):
            S.Hud.Toast("Не хватает Кэша: нужно {FormatNum(Cost)}")
        else:
            set D.Cash -= Cost
            for (Uid : D.FusionPick):
                D.RemoveUid(Uid, Week)
            set D.FusionPick = array{}
            Sec := Preview.Minutes * 60.0
            D.SetFusion(Slot, timer_rec{Active := true, Kind := Preview.Id, Variant := Preview.Variant, EndsAt := Now + Sec, Total := Sec})
            Storm.AddPoints(option{D.Player}, LabStormFusionPoints * D.HypeMult())
            D.AddQuest(Quest_Fusion, 1, LabDay(Now))
            RefreshPlot(S)
            if (Preview.Recipe >= 0, not ContainsInt(D.RecipesFound, Preview.Recipe)?):
                set D.RecipesFound += array{Preview.Recipe}
                AnnounceAll("Лаборатория #{D.PlotIndex + 1} открыла секретный рецепт: {BrainrotTitle(Preview.Id)}!")
            S.Hud.Toast("Скрещивание началось: {BrainrotTitle(Preview.Id)} через {FormatTime(Sec)}")

    LuckyRoll(S:lab_session, Uid:int, Week:int, Day:int):void =
        D := S.Data
        if (D.LuckyDay = Day):
            S.Hud.Toast("Мем-автомат уже крутили сегодня")
        else if (R := D.FindByUid[Uid], Next := LabVariants[R.Variant + 1], Next.Week <= Week, P := LabLuckyChance[R.Variant + 1]):
            set D.LuckyDay = Day
            if (Chance(P)?):
                D.ReplaceRec(WithVariant(R, R.Variant + 1))
                D.RecomputeIncome(Week)
                RefreshPlot(S)
                AnnounceAll("Мем-автомат улучшил {BrainrotTitle(R.Id)} до варианта «{Next.Name}»!")
            else:
                S.Hud.Toast("Не повезло. Приходи завтра!")

    StartTour(S:lab_session, I:int, Now:float):void =
        D := S.Data
        var Busy:logic = false
        for (T : D.Tours, T.Active?):
            set Busy = true
        Cost := D.TourCost(I, D.IncomePerSec(1.0))
        if (Busy?):
            S.Hud.Toast("Гастроли уже идут")
        else if (D.Cash < Cost):
            S.Hud.Toast("Не хватает Кэша: нужно {FormatNum(Cost)}")
        else if (Def := LabTours[I]):
            set D.Cash -= Cost
            Sec := D.TourSeconds(I)
            D.SetTour(I, timer_rec{Active := true, Kind := I, EndsAt := Now + Sec, Total := Sec})
            D.AddQuest(Quest_Tour, 1, LabDay(Now))
            S.Hud.Toast("Брейнроты уехали: «{Def.Name}». Вернутся через {FormatTime(Sec)}")

    BuyShopItem(S:lab_session, I:int, Week:int):void =
        D := S.Data
        if (It := LabHypeShop[I]):
            L := D.ShopLevel(I)
            if (L >= It.MaxLevel):
                S.Hud.Toast("Уже куплено")
            else if (D.Crystals < It.Cost):
                S.Hud.Toast("Нужно {It.Cost} Хайп-кристаллов")
            else:
                set D.Crystals -= It.Cost
                D.SetShopLevel(I, L + 1)
                D.RecomputeIncome(Week)
                RefreshPlot(S)
                S.Hud.Toast("Куплено: {It.Name}")

    ClaimQuest(S:lab_session, I:int):void =
        D := S.Data
        if (D.QuestReady[I]):
            if (set D.QuestClaimed[I] = true) {}
            Likes := D.LikesGain(LabQuestLikes[I] or 0, LikesEventMult())
            var Crystals:int = LabQuestCrystals[I] or 0
            if (D.ShopLevel(Shop_DailyCrystals) > 0):
                set Crystals += 1
            set D.Likes += Likes
            set D.Crystals += Crystals
            Storm.AddPoints(option{D.Player}, LabStormQuestPoints * D.HypeMult())
            S.Hud.Toast("Задание выполнено: +{Likes} Лайков, +{Crystals} кристаллов")

    # ------------------------------------------------ награды извне (ивенты, пиньята, покупки)
    GrantBrainrot(Agent:agent, Id:int, Variant:int, Reason:string):void =
        if (P := player[Agent], S := Sessions[P]):
            D := S.Data
            if (D.Owns(Id)?):
                set D.Crystals += 10
                S.Hud.Toast("{Reason}: у тебя уже есть {BrainrotTitle(Id)} — держи 10 кристаллов")
            else:
                D.AddBrainrot(Id, Variant, false, CurrentWeek())
                RefreshPlot(S)
                AnnounceAll("{Reason}: лаборатория #{D.PlotIndex + 1} получила {BrainrotTitle(Id)}!")

    GrantPinata(P:player):void =
        if (S := Sessions[P]):
            D := S.Data
            set D.Crystals += LabPinataCrystals
            Id := RandomBrainrot(PickWeighted(for (R : LabRarities): R.Weight), CurrentWeek())
            D.AddReserve(capsule_rec{Id := Id, Variant := VariantIdx_Rainbow})
            S.Hud.Toast("Пиньята: +{LabPinataCrystals} кристаллов и Радужная капсула {BrainrotTitle(Id)}!")

    # Вызывай после подтверждённой покупки оффера (см. docs/brainrot-lab/04-verse.md)
    GrantOffer(P:player, OfferIndex:int):void =
        if (S := Sessions[P], O := LabOffers[OfferIndex]):
            D := S.Data
            if (O.Key = "storm_rainbow"):
                set D.PersonalStorms += array{VariantIdx_Rainbow}
            else if (O.Key = "storm_lava"):
                set D.PersonalStorms += array{VariantIdx_Lava}
            else if (O.Key = "storm_viral"):
                set D.PersonalStorms += array{VariantIdx_Viral}
            else if (O.Key = "hype_bomb"):
                Storm.AddBomb()
                AnnounceAll("ХАЙП-БОМБА! Шкала шторма +50% для всего лобби")
            else if (O.Key = "lab_pack"):
                D.GrantUnlock(Unlock_LabPack)
                set D.PersonalStorms += array{VariantIdx_Rainbow, VariantIdx_Rainbow}
            else if (O.Key = "fusion_pack"):
                D.GrantUnlock(Unlock_FusionPack)
                set D.PersonalStorms += array{VariantIdx_Lava, VariantIdx_Lava, VariantIdx_Lava}
            S.Hud.Toast("Спасибо за покупку: {O.Name}!")
            SavePlayer(S)
