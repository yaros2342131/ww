# Участок игрока. Устройство ставится в центр участка лицом к подиуму.
# Места подиума считаются сеткой от позиции устройства (PodiumOffset, PodiumColumns, PodiumSpacing),
# поэтому 30 мест не надо расставлять руками: на них Verse сам ставит постамент и брейнрота.
using { /Fortnite.com/Devices }
using { /Verse.org/Simulation }
using { /UnrealEngine.com/Temporary/SpatialMath }

# Один инкубатор: кнопка у его «двери», табло над ним и манипулятор пропа для ударов киркой
incubator_slot := class<concrete>:
    @editable Button:button_device = button_device{}
    @editable Board:billboard_device = billboard_device{}
    @editable Hits:prop_manipulator_device = prop_manipulator_device{}
    # Где висит капсула относительно кнопки (в сантиметрах)
    @editable CapsuleOffset:vector3 = vector3{X := 0.0, Y := 0.0, Z := 110.0}

incubator_handler := class:
    Plot:lab_plot_device
    Index:int

    OnInteract(Agent:agent):void = Plot.OnIncubatorInteract(Agent, Index)
    OnHit(Agent:agent):void = Plot.OnIncubatorHit(Agent, Index)

# Что сейчас стоит на одном месте подиума
podium_view := class:
    var Uid:int = -1
    var Variant:int = -1
    var Props:[]creative_prop = array{}

NoProp:?creative_prop = false

lab_plot_device := class(creative_device):
    @editable PlotNumber:int = 1
    @editable HomeTeleporter:teleporter_device = teleporter_device{}
    @editable OwnerBoard:billboard_device = billboard_device{}
    @editable Incubators:[]incubator_slot = array{}
    @editable MenuButton:button_device = button_device{}        # «Лаборатория» — главное меню
    @editable RebirthButton:button_device = button_device{}     # станция перерождения
    @editable PodiumColumns:int = 6
    @editable PodiumSpacing:float = 260.0
    # Смещение первого места подиума от устройства: X — вперёд, Y — вправо, Z — вверх
    @editable PodiumOffset:vector3 = vector3{X := 500.0, Y := -650.0, Z := 0.0}
    @editable PedestalHeight:float = 35.0

    var Manager:?lab_manager_device = false
    var Owner:?lab_player = false
    var Views:[]podium_view = array{}
    var IncubatorProps:[]?creative_prop = array{}
    var IncubatorShown:[]int = array{}

    Init(M:lab_manager_device):void =
        set Manager = option{M}
        set Views = for (I := 1..LabSlotsMax): podium_view{}
        set IncubatorProps = for (I := 1..Incubators.Length): NoProp
        set IncubatorShown = for (I := 1..Incubators.Length): -1
        for (I -> Slot : Incubators):
            H := incubator_handler{Plot := Self, Index := I}
            Slot.Button.InteractedWithEvent.Subscribe(H.OnInteract)
            Slot.Hits.DamagedEvent.Subscribe(H.OnHit)
        MenuButton.InteractedWithEvent.Subscribe(OnMenuButton)
        RebirthButton.InteractedWithEvent.Subscribe(OnRebirthButton)
        MenuButton.SetInteractionText(LabText("Лаборатория"))
        RebirthButton.SetInteractionText(LabText("Перерождение"))
        Release()

    IsFree()<transacts><decides>:void = not Owner?

    Assign(P:lab_player, Index:int):void =
        set Owner = option{P}
        set P.PlotIndex = Index
        HomeTeleporter.Teleport(P.Player)
        RefreshPodium()
        RefreshIncubators(LabNow())

    Release():void =
        for (V : Views):
            ClearView(V)
        for (I -> Slot : Incubators):
            ShowCapsule(I, -1)
            Slot.Board.SetText(LabText("—"))
        set Owner = false
        OwnerBoard.SetText(LabText("Свободная лаборатория #{PlotNumber}"))

    TeleportHome(A:agent):void = HomeTeleporter.Teleport(A)

    OnMenuButton(Agent:agent):void =
        if (M := Manager?):
            M.OpenScreen(Agent, Act_Main, 0)

    OnRebirthButton(Agent:agent):void =
        if (M := Manager?):
            M.OpenScreen(Agent, Act_Rebirth, 0)

    OnIncubatorInteract(Agent:agent, Index:int):void =
        if (M := Manager?):
            M.IncubatorInteract(Self, Agent, Index)

    OnIncubatorHit(Agent:agent, Index:int):void =
        if (M := Manager?):
            M.IncubatorHit(Self, Agent, Index)

    # ------------------------------------------------ подиум
    SlotPosition(Slot:int):vector3 =
        Col := Mod[Slot, PodiumColumns] or 0
        Row := Quotient[Slot, PodiumColumns] or 0
        T := GetTransform()
        Local := vector3{X := PodiumOffset.X + Row * PodiumSpacing, Y := PodiumOffset.Y + Col * PodiumSpacing, Z := PodiumOffset.Z}
        T.Translation + T.Rotation.RotateVector(Local)

    ClearView(V:podium_view):void =
        for (Pr : V.Props):
            Pr.Dispose()
        set V.Props = array{}
        set V.Uid = -1
        set V.Variant = -1

    # Пересобирает только те места, где что-то поменялось
    RefreshPodium():void =
        if (M := Manager?, P := Owner?):
            for (S -> V : Views):
                var WantUid:int = -1
                var WantVar:int = -1
                var WantId:int = -1
                var WantIdeal:logic = false
                for (R : P.Brainrots, R.Slot = S):
                    set WantUid = R.Uid
                    set WantVar = R.Variant
                    set WantId = R.Id
                    set WantIdeal = R.Ideal
                if (WantUid <> V.Uid or WantVar <> V.Variant):
                    ClearView(V)
                    if (WantUid >= 0):
                        set V.Props = M.SpawnPodiumProps(WantId, WantVar, WantIdeal, SlotPosition(S), GetTransform().Rotation, PedestalHeight)
                    set V.Uid = WantUid
                    set V.Variant = WantVar

    # ------------------------------------------------ инкубаторы
    ShowCapsule(Index:int, Id:int):void =
        if (Shown := IncubatorShown[Index], Shown <> Id):
            if (Old := IncubatorProps[Index], Pr := Old?):
                Pr.Dispose()
            if (set IncubatorProps[Index] = NoProp) {}
            if (set IncubatorShown[Index] = Id) {}
            if (Slot := Incubators[Index]):
                if (Id >= 0):
                    Slot.Button.SetInteractionText(LabText("Ударить (ускорить)"))
                    if (M := Manager?):
                        Pos := Slot.Button.GetTransform().Translation + Slot.CapsuleOffset
                        New := M.SpawnCapsuleProp(RarityOf(Id), Pos)
                        if (set IncubatorProps[Index] = New) {}
                else:
                    Slot.Button.SetInteractionText(LabText("Положить капсулу"))

    RefreshIncubators(Now:float):void =
        if (P := Owner?):
            for (I -> Slot : Incubators):
                var Text:string = "Пусто — положи капсулу"
                var ShowId:int = -1
                if (I >= P.IncubatorCount()):
                    set Text = "Закрыто — открывается в Хайп-магазине"
                else if (T := P.Incubators[I], T.Active?):
                    set ShowId = T.Kind
                    Left := Max(0.0, T.EndsAt - Now)
                    set Text = "{BrainrotTitle(T.Kind)} ({VariantName(T.Variant)}) · {FormatTime(Left)}"
                Slot.Board.SetText(LabText(Text))
                ShowCapsule(I, ShowId)

    RefreshBoard(IncomeText:string):void =
        if (P := Owner?):
            OwnerBoard.SetText(LabText("Лаборатория #{PlotNumber} · {IncomeText}/с · Перерождение {P.Rebirth}"))
