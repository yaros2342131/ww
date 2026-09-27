# Игрок во время сессии и вся экономика: доход, семьи и комбо, цены, перерождения, улучшения,
# скрещивание, гастроли, задания. Здесь нет устройств и UI — только данные и расчёты.
using { /Verse.org/Simulation }
using { /Verse.org/Random }

# ---------------------------------------------------------------- справочники
GetDef(Id:int)<transacts>:brainrot_def = if (D := LabBrainrots[Id]) then D else brainrot_def{}
GetRarity(R:int)<transacts>:rarity_def = if (D := LabRarities[R]) then D else rarity_def{}
GetVariant(V:int)<transacts>:variant_def = if (D := LabVariants[V]) then D else variant_def{}
RarityOf(Id:int)<transacts>:int = GetDef(Id).Rarity
BrainrotTitle(Id:int)<transacts>:string = GetDef(Id).Title
VariantName(V:int)<transacts>:string = GetVariant(V).Name
RarityName(Id:int)<transacts>:string = GetRarity(RarityOf(Id)).Name
FamilyName(Id:int)<transacts>:string = if (F := LabFamilies[GetDef(Id).Family]) then F.Name else ""

BaseUnitIncome(Id:int, Variant:int)<transacts>:float =
    GetRarity(RarityOf(Id)).Income * GetVariant(Variant).Mult

BaseCapsulePrice(Id:int, Variant:int)<transacts>:float =
    Rar := GetRarity(RarityOf(Id))
    Rar.Income * Rar.Payback * GetVariant(Variant).Mult

# Бонус семьи и особых комбо для одного брейнрота, если на подиуме стоят Ids
UnitBonus(Id:int, Ids:[]int, Week:int)<transacts>:float =
    D := GetDef(Id)
    var Bonus:float = 0.0
    if (D.Family <> FamilyIdx_Icons, Fam := LabFamilies[D.Family]):
        Count := CountPresent(Fam.Members, Ids)
        if (B := LabFamilyBonusByCount[Min(Count, 4)]):
            set Bonus += B
        if (Count >= 2, Count >= Fam.Members.Length):
            set Bonus += LabFamilyFullExtra
    for (Cb : LabCombos, Cb.Week <= Week, ContainsInt(Cb.Members, Id)?, CountPresent(Cb.Members, Ids) = Cb.Members.Length):
        set Bonus += Cb.Bonus
    Bonus

PickQuest(Pool:[]quest_def, Day:int)<transacts>:quest_def =
    if (Q := Pool[Mod[Day, Pool.Length] or 0]) then Q else quest_def{}

QuestTitle(Q:quest_def)<transacts>:string =
    N := Q.Target
    if (Q.Kind = Quest_Hatch):
        "Выведи {N} брейнротов"
    else if (Q.Kind = Quest_BuyCapsule):
        "Купи {N} капсул на конвейере"
    else if (Q.Kind = Quest_PickaxeHit):
        "Сделай {N} ударов по инкубаторам"
    else if (Q.Kind = Quest_Sell):
        "Продай {N} брейнротов"
    else if (Q.Kind = Quest_Storm):
        "Поучаствуй в Хайп-шторме ({N})"
    else if (Q.Kind = Quest_Tour):
        "Отправь брейнротов на гастроли ({N})"
    else if (Q.Kind = Quest_Upgrade):
        "Улучши вариант брейнрота ({N})"
    else if (Q.Kind = Quest_HatchEpic):
        "Выведи {N} Эпических или выше"
    else:
        "Скрести брейнротов ({N})"

WithSlot(R:brainrot_rec, S:int)<transacts>:brainrot_rec =
    brainrot_rec{Uid := R.Uid, Id := R.Id, Variant := R.Variant, Ideal := R.Ideal, Slot := S}

WithVariant(R:brainrot_rec, V:int)<transacts>:brainrot_rec =
    brainrot_rec{Uid := R.Uid, Id := R.Id, Variant := V, Ideal := R.Ideal, Slot := R.Slot}

fusion_preview := struct:
    Ok:logic = false
    Id:int = 0
    Variant:int = 0
    Recipe:int = -1
    Minutes:float = 0.0
    Note:string = ""

# Флаги покупок за V-Bucks (хранятся в ShopLevels после Хайп-магазина, см. UnlockSlot)
Unlock_FusionPack:int = 0
Unlock_LabPack:int = 1

# ---------------------------------------------------------------- игрок
lab_player := class:
    Player:player

    # сохраняемое
    var Cash:float = LabStartCash
    var Likes:int = 0
    var Crystals:int = 0
    var Rebirth:int = 0
    var SuperRebirths:int = 0
    var NextUid:int = 1
    var Brainrots:[]brainrot_rec = array{}
    var Reserve:[]capsule_rec = array{}
    var Carrying:?capsule_rec = false
    var Incubators:[]timer_rec = array{}
    var Fusions:[]timer_rec = array{}
    var Tours:[]timer_rec = array{}
    var Discovered:[]int = array{}
    var IdealFound:[]int = array{}
    var RecipesFound:[]int = array{}
    var FamiliesDone:[]int = array{}
    var ShopLevels:[]int = array{}
    var Companions:[]int = array{}
    var PersonalStorms:[]int = array{}
    var LastSeen:float = 0.0
    var PlaySeconds:float = 0.0
    var QuestDay:int = -1
    var QuestProgress:[]int = array{}
    var QuestClaimed:[]logic = array{}
    var LuckyDay:int = -1
    var TotalHatched:int = 0

    # только на время сессии
    var PlotIndex:int = -1
    var BaseIncome:float = 0.0       # доход подиума с бонусами семей и комбо, без глобальных множителей
    var FusionPick:[]int = array{}   # выбранные для скрещивания Uid

    # ------------------------------------------------ загрузка и сохранение
    LoadFrom(S:lab_save):void =
        set Cash = S.Cash
        set Likes = S.Likes
        set Crystals = S.Crystals
        set Rebirth = S.Rebirth
        set SuperRebirths = S.SuperRebirths
        set NextUid = S.NextUid
        set Brainrots = S.Brainrots
        set Reserve = S.Reserve
        set Carrying = if (C := S.Carrying[0]) then option{C} else false
        set Incubators = S.Incubators
        set Fusions = S.Fusions
        set Tours = S.Tours
        set Discovered = S.Discovered
        set IdealFound = S.IdealFound
        set RecipesFound = S.RecipesFound
        set FamiliesDone = S.FamiliesDone
        set ShopLevels = S.ShopLevels
        set Companions = S.Companions
        set PersonalStorms = S.PersonalStorms
        set LastSeen = S.LastSeen
        set PlaySeconds = S.PlaySeconds
        set QuestDay = S.QuestDay
        set QuestProgress = S.QuestProgress
        set QuestClaimed = S.QuestClaimed
        set LuckyDay = S.LuckyDay
        set TotalHatched = S.TotalHatched
        EnsureArrays()

    ToSave(Now:float):lab_save =
        lab_save:
            Version := 1
            Cash := Self.Cash
            Likes := Self.Likes
            Crystals := Self.Crystals
            Rebirth := Self.Rebirth
            SuperRebirths := Self.SuperRebirths
            NextUid := Self.NextUid
            Brainrots := Self.Brainrots
            Reserve := Self.Reserve
            Carrying := if (C := Self.Carrying?) then array{C} else array{}
            Incubators := Self.Incubators
            Fusions := Self.Fusions
            Tours := Self.Tours
            Discovered := Self.Discovered
            IdealFound := Self.IdealFound
            RecipesFound := Self.RecipesFound
            FamiliesDone := Self.FamiliesDone
            ShopLevels := Self.ShopLevels
            Companions := Self.Companions
            PersonalStorms := Self.PersonalStorms
            LastSeen := Now
            PlaySeconds := Self.PlaySeconds
            QuestDay := Self.QuestDay
            QuestProgress := Self.QuestProgress
            QuestClaimed := Self.QuestClaimed
            LuckyDay := Self.LuckyDay
            TotalHatched := Self.TotalHatched

    # Таймеров и уровней магазина всегда столько, сколько может понадобиться
    EnsureArrays():void =
        loop:
            if (Incubators.Length >= LabIncubatorsMax):
                break
            set Incubators += array{timer_rec{}}
        loop:
            if (Fusions.Length >= 2):
                break
            set Fusions += array{timer_rec{}}
        loop:
            if (Tours.Length >= LabTours.Length):
                break
            set Tours += array{timer_rec{}}
        loop:
            if (ShopLevels.Length >= LabHypeShop.Length + 2):
                break
            set ShopLevels += array{0}

    # ------------------------------------------------ простые счётчики
    ShopLevel(I:int)<transacts>:int = if (L := ShopLevels[I]) then L else 0
    SetShopLevel(I:int, L:int):void = if (set ShopLevels[I] = L) {}

    # Покупки за V-Bucks хранятся после уровней Хайп-магазина
    HasUnlock(U:int)<transacts>:logic = logic{ShopLevel(LabHypeShop.Length + U) > 0}
    GrantUnlock(U:int):void = SetShopLevel(LabHypeShop.Length + U, 1)

    SlotCount()<transacts>:int = Min(LabSlotsMax, LabSlotsStart + Rebirth * LabSlotsPerLevel)
    IncubatorCount()<transacts>:int =
        Pack := if (HasUnlock(Unlock_LabPack)?) then 1 else 0
        Min(LabIncubatorsMax, LabIncubatorsStart + ShopLevel(Shop_ExtraIncubator) + Pack)
    CompanionSlots()<transacts>:int = Min(2, LabCompanionSlotsStart + ShopLevel(Shop_SecondCompanion))
    FusionSlots()<transacts>:int = if (HasUnlock(Unlock_FusionPack)?) then 2 else 1

    # ------------------------------------------------ брейнроты
    FindByUid(Uid:int)<transacts><decides>:brainrot_rec =
        var Found:?brainrot_rec = false
        for (R : Brainrots, R.Uid = Uid):
            set Found = option{R}
        Found?

    PodiumIds()<transacts>:[]int = for (R : Brainrots, R.Slot >= 0): R.Id

    SlotUsed(S:int)<transacts>:logic =
        var Used:logic = false
        for (R : Brainrots, R.Slot = S):
            set Used = true
        Used

    FreeSlot()<transacts>:int =
        var Result:int = -1
        for (S := 0..SlotCount() - 1, Result < 0, not SlotUsed(S)?):
            set Result = S
        Result

    HasAtLeast(Id:int, MinVariant:int)<transacts>:logic =
        var Ok:logic = false
        for (R : Brainrots, R.Id = Id, R.Variant >= MinVariant):
            set Ok = true
        Ok

    Owns(Id:int)<transacts>:logic = HasAtLeast(Id, 0)

    ReplaceRec(New:brainrot_rec):void =
        set Brainrots = for (R : Brainrots): if (R.Uid = New.Uid) then New else R

    AddBrainrot(Id:int, Variant:int, Ideal:logic, Week:int):brainrot_rec =
        Rec := brainrot_rec{Uid := NextUid, Id := Id, Variant := Variant, Ideal := Ideal, Slot := FreeSlot()}
        set NextUid += 1
        set Brainrots += array{Rec}
        if (not ContainsInt(Discovered, Id)?):
            set Discovered += array{Id}
        if (Ideal?, not ContainsInt(IdealFound, Id)?):
            set IdealFound += array{Id}
        RecomputeIncome(Week)
        Rec

    RemoveUid(Uid:int, Week:int):void =
        set Brainrots = for (R : Brainrots, R.Uid <> Uid): R
        set Companions = for (C : Companions, C <> Uid): C
        set FusionPick = for (C : FusionPick, C <> Uid): C
        RecomputeIncome(Week)

    # После супер-перерождения слотов меньше — лишние уходят в запас
    FixSlots():void =
        Limit := SlotCount()
        set Brainrots = for (R : Brainrots): if (R.Slot >= Limit) then WithSlot(R, -1) else R

    # Жадная расстановка: самые доходные — на подиум
    AutoArrange(Week:int):void =
        set Brainrots = for (R : Brainrots): WithSlot(R, -1)
        for (S := 0..SlotCount() - 1):
            var BestUid:int = -1
            var BestVal:float = -1.0
            for (R : Brainrots, R.Slot < 0):
                V := BaseUnitIncome(R.Id, R.Variant)
                if (V > BestVal):
                    set BestVal = V
                    set BestUid = R.Uid
            if (B := FindByUid[BestUid]):
                ReplaceRec(WithSlot(B, S))
        RecomputeIncome(Week)

    # ------------------------------------------------ доход
    RecomputeIncome(Week:int):void =
        Ids := PodiumIds()
        var Total:float = 0.0
        for (R : Brainrots, R.Slot >= 0):
            set Total += BaseUnitIncome(R.Id, R.Variant) * (1.0 + UnitBonus(R.Id, Ids, Week))
        set BaseIncome = Total

    UnitIncome(R:brainrot_rec, Week:int)<transacts>:float =
        BaseUnitIncome(R.Id, R.Variant) * (1.0 + UnitBonus(R.Id, PodiumIds(), Week)) * GlobalMult()

    HasCompanion(Id:int)<transacts>:logic =
        var Has:logic = false
        for (Uid : Companions, R := FindByUid[Uid], R.Id = Id):
            set Has = true
        Has

    # Сумма перка по всем компаньонам: сила по редкости × (1 + 0.1 × вариант)
    CompanionPerk(Perk:int)<transacts>:float =
        var Sum:float = 0.0
        for (Uid : Companions, R := FindByUid[Uid], D := LabBrainrots[R.Id], Fam := LabFamilies[D.Family], Fam.Perk = Perk, P := LabCompanionPerk[D.Rarity]):
            set Sum += P * (1.0 + R.Variant * 0.1)
        Sum

    GlobalMult()<transacts>:float =
        var M:float = PowInt(LabRebirthIncomeMult, Rebirth) * PowInt(LabSuperIncomeMult, SuperRebirths)
        set M *= 1.0 + IdealFound.Length * LabIdealBonus
        set M *= 1.0 + CompanionPerk(Perk_CashBonus)
        if (HasCompanion(BrainrotIdx_SixSeven67)?):
            set M *= 1.067
        M

    IncomePerSec(Mult:float)<transacts>:float = BaseIncome * GlobalMult() * Mult

    CapsulePrice(Id:int, Variant:int)<transacts>:float =
        Discount := Min(0.4, CompanionPerk(Perk_BeltDiscount))
        BaseCapsulePrice(Id, Variant) * (1.0 - Discount)

    # Лайки с учётом перка Джунглей и множителя ивента
    LikesGain(Base:int, EventMult:float)<transacts>:int =
        FloorInt(Base * (1.0 + CompanionPerk(Perk_LikesBonus)) * EventMult)

    HypeMult()<transacts>:float =
        Icon := if (HasCompanion(BrainrotIdx_TralaleroTralala)?) then 0.25 else 0.0
        1.0 + CompanionPerk(Perk_HypeBonus) + Icon

    # ------------------------------------------------ вылупление
    HatchSeconds(Id:int, EventMult:float)<transacts>:float =
        Speed := Min(0.6, CompanionPerk(Perk_HatchSpeed) + ShopLevel(Shop_HatchSpeed) * 0.1)
        GetRarity(RarityOf(Id)).Hatch * (1.0 - Speed) / EventMult

    CritChance()<transacts>:float =
        Icon := if (HasCompanion(BrainrotIdx_TungTungTungSahur)?) then 0.5 * LabCritChance else 0.0
        LabCritChance + CompanionPerk(Perk_PickaxeCrit) + ShopLevel(Shop_PickaxeCrit) * 0.05 + Icon

    CritMult()<transacts>:float =
        if (HasCompanion(BrainrotIdx_TungTungTungSahur)?) then LabCritMult * 1.5 else LabCritMult

    VariantUpChance()<transacts>:float =
        Icon := if (HasCompanion(BrainrotIdx_TralaleroTralala)?) then 0.1 else 0.0
        CompanionPerk(Perk_VariantUp) + Icon

    IdealChance()<transacts>:float =
        Charm := if (ShopLevel(Shop_IdealCharm) > 0) then 2.0 else 1.0
        LabIdealChance * Charm * (1.0 + CompanionPerk(Perk_IdealLuck))

    # Следующая капсула для инкубатора: сначала из рук, потом из запаса
    TakeCapsule():?capsule_rec =
        if (C := Carrying?):
            set Carrying = false
            return option{C}
        if (First := Reserve[0]):
            set Reserve = for (I -> R : Reserve, I > 0): R
            return option{First}
        false

    # Запас капсул ограничен; лишняя капсула превращается в Лайки
    AddReserve(C:capsule_rec):void =
        if (Reserve.Length < LabReserveMax + ShopLevel(Shop_ReservePlus) * 5):
            set Reserve += array{C}
        else:
            set Likes += GetRarity(RarityOf(C.Id)).SellLikes * 2

    SetIncubator(I:int, T:timer_rec):void = if (set Incubators[I] = T) {}
    SetFusion(I:int, T:timer_rec):void = if (set Fusions[I] = T) {}
    SetTour(I:int, T:timer_rec):void = if (set Tours[I] = T) {}

    # ------------------------------------------------ перерождения
    RebirthCost()<transacts>:float = LabRebirthFirstCost * PowInt(LabRebirthGrowth, Rebirth)

    # После каждого «Вирусного взрыва» требуемый вариант выше на 1
    ReqVariant(V:int)<transacts>:int = Min(VariantIdx_Cosmic, V + SuperRebirths)

    NextReq()<transacts>:rebirth_req = if (R := LabRebirthReqs[Rebirth]) then R else rebirth_req{}

    MissingReqs()<transacts>:int =
        Req := NextReq()
        var Missing:int = 0
        for (I -> Id : Req.Ids, V := Req.Variants[I], not HasAtLeast(Id, ReqVariant(V))?):
            set Missing += 1
        Missing

    CanRebirth()<transacts><decides>:void =
        Rebirth < LabRebirthLevels
        Cash >= RebirthCost()
        MissingReqs() = 0

    DoRebirth(Week:int):void =
        set Cash = 0.0
        set Rebirth += 1
        RecomputeIncome(Week)

    HasRainbowLegendary()<transacts>:logic =
        var Has:logic = false
        for (R : Brainrots, RarityOf(R.Id) >= RarityIdx_Legendary, R.Variant >= VariantIdx_Rainbow):
            set Has = true
        Has

    CanSuper(Week:int)<transacts><decides>:void =
        Week >= LabSuperFromWeek
        Rebirth >= LabSuperUnlockRebirth
        HasRainbowLegendary()?

    SuperCrystals()<transacts>:int =
        if (C := LabSuperCrystals[Min(Rebirth, LabRebirthLevels) - LabSuperUnlockRebirth]) then C else 0

    DoSuper(Week:int):void =
        set Crystals += SuperCrystals()
        set SuperRebirths += 1
        set Rebirth = 0
        set Cash = LabStartCash
        FixSlots()
        RecomputeIncome(Week)

    # ------------------------------------------------ улучшение, продажа
    UpgradeCost(R:brainrot_rec)<transacts>:int =
        if (Row := LabUpgradeCosts[RarityOf(R.Id)], C := Row[R.Variant]) then C else -1

    CanUpgrade(R:brainrot_rec, Week:int)<transacts><decides>:void =
        C := UpgradeCost(R)
        C > 0
        Likes >= C
        V := LabVariants[R.Variant + 1]
        V.Week <= Week

    SellCash(R:brainrot_rec)<transacts>:float = BaseCapsulePrice(R.Id, R.Variant) * LabSellCashShare
    SellLikes(R:brainrot_rec)<transacts>:int = GetRarity(RarityOf(R.Id)).SellLikes * (R.Variant + 1)

    # ------------------------------------------------ скрещивание
    FusionPreview(Week:int)<transacts>:fusion_preview =
        if (FusionPick.Length <> 3):
            return fusion_preview{Note := "Выбери 3 брейнрота ({FusionPick.Length}/3)"}
        if (U0 := FusionPick[0], U1 := FusionPick[1], U2 := FusionPick[2], A := FindByUid[U0], B := FindByUid[U1], C := FindByUid[U2]):
            PackSpeed := if (HasUnlock(Unlock_FusionPack)?) then 0.5 else 0.0
            Speed := Min(0.6, CompanionPerk(Perk_FusionSpeed) + PackSpeed)
            if (A.Id = B.Id, B.Id = C.Id, A.Variant = B.Variant, B.Variant = C.Variant):
                Next := A.Variant + 1
                if (V := LabVariants[Next], V.Week <= Week):
                    Minutes := LabFusionVariantMin * (1.0 - Speed)
                    Note := "3 одинаковых → {BrainrotTitle(A.Id)} ({V.Name})"
                    return fusion_preview{Ok := true, Id := A.Id, Variant := Next, Minutes := Minutes, Note := Note}
                return fusion_preview{Note := "Следующий вариант пока закрыт"}
            Ids := array{A.Id, B.Id, C.Id}
            var Found:int = -1
            for (I -> Rc : LabRecipes, Found < 0, GetDef(Rc.Result).Week <= Week, CountPresent(Rc.Inputs, Ids) = 3):
                set Found = I
            if (Rc := LabRecipes[Found]):
                MinVar := Min(A.Variant, Min(B.Variant, C.Variant))
                R := RarityOf(Rc.Result)
                var Base:float = LabFusionEpicMin
                if (R >= RarityIdx_Legendary):
                    set Base = LabFusionLegendaryMin
                if (R >= RarityIdx_Mythic):
                    set Base = LabFusionMythicMin
                Minutes := Base * (1.0 - Speed)
                Note := "Секретный рецепт: {BrainrotTitle(Rc.Result)}!"
                return fusion_preview{Ok := true, Id := Rc.Result, Variant := MinVar, Recipe := Found, Minutes := Minutes, Note := Note}
            return fusion_preview{Note := "Такой комбинации нет. Подсказки — в Мемопедии"}
        fusion_preview{Note := "Выбери 3 брейнрота"}

    FusionCost(P:fusion_preview)<transacts>:float = LabFusionCostMult * BaseCapsulePrice(P.Id, 0)

    FreeFusion()<transacts>:int =
        var Result:int = -1
        for (I -> T : Fusions, Result < 0, I < FusionSlots(), not T.Active?):
            set Result = I
        Result

    # ------------------------------------------------ гастроли
    TourCost(I:int, IncomeNow:float)<transacts>:float =
        if (T := LabTours[I]) then Max(100.0, IncomeNow * T.CostIncomeMin * 60.0) else 0.0

    TourSeconds(I:int)<transacts>:float =
        Speed := Min(0.5, CompanionPerk(Perk_TourSpeed))
        if (T := LabTours[I]) then T.Minutes * 60.0 * (1.0 - Speed) else 0.0

    # ------------------------------------------------ офлайн-доход
    ApplyOffline(Now:float):float =
        if (LastSeen <= 0.0 or Now <= LastSeen):
            return 0.0
        Cap := (LabOfflineCapHours + ShopLevel(Shop_OfflineCap) * 4.0) * 3600.0
        Away := Min(Now - LastSeen, Cap)
        Rate := LabOfflineRate * (1.0 + CompanionPerk(Perk_OfflineBonus))
        Gain := BaseIncome * GlobalMult() * Rate * Away
        set Cash += Gain
        Gain

    # ------------------------------------------------ ежедневные задания
    TodayQuests()<transacts>:[]quest_def =
        array{PickQuest(LabQuestsEasy, QuestDay), PickQuest(LabQuestsMedium, QuestDay), PickQuest(LabQuestsHard, QuestDay)}

    EnsureQuestDay(Day:int):void =
        if (QuestDay <> Day or QuestProgress.Length <> 3 or QuestClaimed.Length <> 3):
            set QuestDay = Day
            set QuestProgress = array{0, 0, 0}
            set QuestClaimed = array{false, false, false}

    AddQuest(Kind:int, Amount:int, Day:int):void =
        EnsureQuestDay(Day)
        Qs := TodayQuests()
        set QuestProgress = for (I -> P : QuestProgress):
            if (Q := Qs[I], Q.Kind = Kind) then P + Amount else P

    QuestReady(I:int)<transacts><decides>:void =
        Q := TodayQuests()[I]
        P := QuestProgress[I]
        P >= Q.Target
        Claimed := QuestClaimed[I]
        not Claimed?
