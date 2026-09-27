# Конвейер «Красная дорожка». Капсулы едут шагами: каждые 4 с (в шторм — 2 с) все сдвигаются на одно
# «окно». Окно — это button_device вдоль ленты: игрок подходит и нажимает «Купить».
# Порядок окон в массиве Windows — от портала к концу ленты.
using { /Fortnite.com/Devices }
using { /Verse.org/Simulation }
using { /Verse.org/Random }
using { /UnrealEngine.com/Temporary/SpatialMath }

belt_capsule := class:
    Id:int
    Variant:int
    var Prop:?creative_prop = false

belt_window_handler := class:
    Belt:lab_belt_device
    Index:int

    OnInteract(Agent:agent):void = Belt.OnWindow(Agent, Index)

NoCapsule:?belt_capsule = false

lab_belt_device := class(creative_device):
    @editable Windows:[]button_device = array{}
    @editable TimerBoard:billboard_device = billboard_device{}
    @editable CapsuleLift:float = 60.0      # высота капсулы над кнопкой окна, см
    @editable MoveSeconds:float = 0.8       # сколько капсула едет между окнами

    var Manager:?lab_manager_device = false
    var Slots:[]?belt_capsule = array{}
    var NextLegendary:float = 0.0
    var NextRainbow:float = 0.0
    var NextMythic:float = 0.0
    var NextLava:float = 0.0

    Init(M:lab_manager_device):void =
        set Manager = option{M}
        set Slots = for (W : Windows): NoCapsule
        for (I -> W : Windows):
            W.InteractedWithEvent.Subscribe(belt_window_handler{Belt := Self, Index := I}.OnInteract)
            W.SetInteractionText(LabText("Капсула едет…"))
        T := GetSimulationElapsedTime()
        set NextLegendary = T + LabGuaranteedLegendarySec
        set NextRainbow = T + LabGuaranteedRainbowSec
        set NextMythic = T + LabGuaranteedMythicSec
        set NextLava = T + LabGuaranteedLavaSec
        spawn{ Run() }

    Run()<suspends>:void =
        loop:
            Step()
            Sleep(StepSeconds())

    StepSeconds():float =
        if (M := Manager?, M.Storm.IsActive()?) then LabStormBeltStepSec else LabBeltStepSec

    WindowPos(I:int):vector3 =
        if (W := Windows[I]) then W.GetTransform().Translation + vector3{Z := CapsuleLift} else vector3{}

    Step():void =
        if (M := Manager?, Slots.Length > 0):
            # последняя капсула уезжает обратно в портал
            if (Last := Slots[Slots.Length - 1], C := Last?, Pr := C.Prop?):
                Pr.Dispose()
            New := RollCapsule(M)
            set New.Prop = M.SpawnCapsuleProp(RarityOf(New.Id), WindowPos(0))
            var Shifted:[]?belt_capsule = array{option{New}}
            for (I := 0..Slots.Length - 2):
                set Shifted += array{Slots[I] or NoCapsule}
            set Slots = Shifted
            for (I -> Entry : Slots, I > 0, C := Entry?, Pr := C.Prop?):
                spawn{ MoveCapsule(Pr, WindowPos(I)) }
            RefreshTexts(M)

    MoveCapsule(Pr:creative_prop, Pos:vector3)<suspends>:void =
        if (Pr.IsValid[]):
            Pr.MoveTo(Pos, IdentityRotation(), MoveSeconds)

    RollVariant():int =
        X := GetRandomFloat(0.0, 1.0)
        if (Rb := LabVariants[VariantIdx_Rainbow], Dm := LabVariants[VariantIdx_Diamond], Gd := LabVariants[VariantIdx_Gold]):
            if (X < Rb.BeltChance):
                VariantIdx_Rainbow
            else if (X < Rb.BeltChance + Dm.BeltChance):
                VariantIdx_Diamond
            else if (X < Rb.BeltChance + Dm.BeltChance + Gd.BeltChance):
                VariantIdx_Gold
            else:
                0
        else:
            0

    RollCapsule(M:lab_manager_device):belt_capsule =
        Week := M.CurrentWeek()
        Now := GetSimulationElapsedTime()
        InStorm := M.Storm.IsActive()
        Weights := for (R -> Def : LabRarities):
            StormMult := if (InStorm?, Mu := LabStormWeightMult[R]) then Mu else 1.0
            if (R < RarityIdx_Iconic) then Def.Weight * StormMult else 0.0
        var Rarity:int = PickWeighted(Weights)
        var Variant:int = RollVariant()
        # гарантии по таймерам (их показывает табло)
        if (Now >= NextLegendary):
            set NextLegendary = Now + LabGuaranteedLegendarySec
            set Rarity = Max(Rarity, RarityIdx_Legendary)
        if (Week >= LabGuaranteedMythicWeek, Now >= NextMythic):
            set NextMythic = Now + LabGuaranteedMythicSec
            set Rarity = RarityIdx_Mythic
        if (Now >= NextRainbow):
            set NextRainbow = Now + LabGuaranteedRainbowSec
            set Variant = Max(Variant, VariantIdx_Rainbow)
        if (Week >= LabGuaranteedLavaWeek, Now >= NextLava):
            set NextLava = Now + LabGuaranteedLavaSec
            set Variant = Max(Variant, VariantIdx_Lava)
        Id := M.RandomBrainrot(Rarity, Week)
        C := belt_capsule{Id := Id, Variant := Variant}
        if (RarityOf(Id) >= RarityIdx_Legendary or Variant >= VariantIdx_Rainbow):
            M.AnnounceAll("На конвейере: {BrainrotTitle(Id)} — {RarityName(Id)}, {VariantName(Variant)}!")
        C

    OnWindow(Agent:agent, Index:int):void =
        if (M := Manager?, Entry := Slots[Index], C := Entry?):
            Bought := M.TryBuyCapsule(Agent, C.Id, C.Variant)
            if (Bought?):
                if (Pr := C.Prop?):
                    Pr.Dispose()
                if (set Slots[Index] = NoCapsule) {}
                RefreshTexts(M)

    RefreshTexts(M:lab_manager_device):void =
        for (I -> W : Windows):
            if (Entry := Slots[I], C := Entry?):
                Price := FormatNum(BaseCapsulePrice(C.Id, C.Variant))
                W.SetInteractionText(LabText("Купить {BrainrotTitle(C.Id)} ({VariantName(C.Variant)}) — {Price}"))
            else:
                W.SetInteractionText(LabText("Пусто"))

    UpdateBoard(Week:int):void =
        Now := GetSimulationElapsedTime()
        var Text:string = "Легендарная через {FormatTime(NextLegendary - Now)} | Радужная через {FormatTime(NextRainbow - Now)}"
        if (Week >= LabGuaranteedMythicWeek):
            set Text += " | Мифик через {FormatTime(NextMythic - Now)}"
        if (Week >= LabGuaranteedLavaWeek):
            set Text += " | Лавовая через {FormatTime(NextLava - Now)}"
        TimerBoard.SetText(LabText(Text))
