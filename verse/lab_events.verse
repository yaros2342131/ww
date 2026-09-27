# Ивентовые устройства: Мем-пиньята (четверг), «собери и принеси» (иконы), награда на финише паркура.
using { /Fortnite.com/Devices }
using { /Verse.org/Simulation }

# ---------------------------------------------------------------- Мем-пиньята
# Проп пиньяты стоит в хабе. По четвергам (UTC) каждые 30 минут пиньята появляется; её бьют киркой
# (prop_manipulator_device на пропе) или кнопкой. Сломали — все, кто бил, получают награду.
lab_pinata_device := class(creative_device):
    @editable Manager:lab_manager_device = lab_manager_device{}
    @editable PinataProp:creative_prop = creative_prop{}
    @editable Hits:prop_manipulator_device = prop_manipulator_device{}
    @editable HitButton:button_device = button_device{}
    @editable Board:billboard_device = billboard_device{}
    @editable ConfettiVFX:vfx_spawner_device = vfx_spawner_device{}
    @editable ForceActive:logic = false          # включить в любой день (для теста)

    var Alive:logic = false
    var HitsLeft:int = 0
    var Hitters:[]player = array{}
    var NextSpawn:float = 0.0

    OnBegin<override>()<suspends>:void =
        Hits.DamagedEvent.Subscribe(OnHit)
        HitButton.InteractedWithEvent.Subscribe(OnHit)
        HitButton.SetInteractionText(LabText("Ударить пиньяту"))
        PinataProp.Hide()
        HitButton.Disable()
        loop:
            Sleep(1.0)
            Now := LabNow()
            Sim := GetSimulationElapsedTime()
            Active := if (ForceActive?) then true else logic{Manager.MiniEventActive[Now]}
            if (not Alive?, Active?, Sim >= NextSpawn):
                Spawn()
            if (Alive?):
                Board.SetText(LabText("МЕМ-ПИНЬЯТА: осталось {HitsLeft} ударов"))
            else if (Active?):
                Board.SetText(LabText("Мем-пиньята появится через {FormatTime(NextSpawn - Sim)}"))
            else:
                Board.SetText(LabText("Мем-пиньята — по четвергам каждые 30 минут"))

    Spawn():void =
        Players := Max(1, GetPlayspace().GetPlayers().Length)
        set HitsLeft = LabPinataHitsPerPlayer * Players
        set Hitters = array{}
        set Alive = true
        PinataProp.Show()
        HitButton.Enable()
        Manager.AnnounceAll("МЕМ-ПИНЬЯТА в центре! Бей её киркой — награда всем, кто ударил")

    OnHit(Agent:agent):void =
        if (Alive?, P := player[Agent]):
            if (not Hitters.Find[P]):
                set Hitters += array{P}
            set HitsLeft -= 1
            if (HitsLeft <= 0):
                Break()

    Break():void =
        set Alive = false
        set NextSpawn = GetSimulationElapsedTime() + LabPinataEverySec
        PinataProp.Hide()
        HitButton.Disable()
        ConfettiVFX.Disable()
        ConfettiVFX.Enable()
        for (P : Hitters):
            Manager.GrantPinata(P)
        Manager.AnnounceAll("Пиньята разбита! Награду получили {Hitters.Length} лаборантов")

# ---------------------------------------------------------------- «Собери и принеси»
# Пример — ивент «Тунг-Тунг-Сахур»: по карте разложены поленья (кнопки у пропов-поленьев), игрок
# собирает Need штук и несёт к тотему — получает икону. Работает в дни, когда включён субботний ивент
# и уже наступила неделя FromWeek.
collect_handler := class:
    Device:lab_collect_event_device
    Index:int

    OnInteract(Agent:agent):void = Device.OnPickup(Agent, Index)

lab_collect_event_device := class(creative_device):
    @editable Manager:lab_manager_device = lab_manager_device{}
    @editable Pickups:[]button_device = array{}
    @editable Deliver:button_device = button_device{}
    @editable Board:billboard_device = billboard_device{}
    @editable Need:int = 10
    @editable RewardKey:string = "Tung_Tung_Tung_Sahur"   # папка модели брейнрота из config
    @editable FromWeek:int = 1
    @editable EventName:string = "Тунг-Тунг-Сахур"
    @editable OnlyDuringMainEvent:logic = true

    var Collected:[player][]int = map{}

    OnBegin<override>()<suspends>:void =
        for (I -> B : Pickups):
            B.InteractedWithEvent.Subscribe(collect_handler{Device := Self, Index := I}.OnInteract)
            B.SetInteractionText(LabText("Подобрать"))
        Deliver.InteractedWithEvent.Subscribe(OnDeliver)
        Deliver.SetInteractionText(LabText("Сдать находки"))
        loop:
            Sleep(2.0)
            On := IsOn()
            if (On?):
                Board.SetText(LabText("{EventName}: собери {Need} штук по карте и принеси сюда"))
            else:
                Board.SetText(LabText("{EventName} — скоро"))

    IsOn():logic =
        Week := Manager.CurrentWeek()
        Now := LabNow()
        if (Week < FromWeek):
            return false
        if (OnlyDuringMainEvent?):
            return logic{Manager.MainEventActive[Now]}
        true

    RewardId():int =
        var Id:int = -1
        for (I -> B : LabBrainrots, B.Key = RewardKey):
            set Id = I
        Id

    OnPickup(Agent:agent, Index:int):void =
        On := IsOn()
        if (On?, P := player[Agent]):
            Have := if (L := Collected[P]) then L else array{}
            if (not Have.Find[Index]):
                New := Have + array{Index}
                if (set Collected[P] = New) {}
                if (S := Manager.Sessions[P]):
                    S.Hud.Toast("{EventName}: {Min(New.Length, Need)}/{Need}")

    OnDeliver(Agent:agent):void =
        On := IsOn()
        if (On?, P := player[Agent], L := Collected[P]):
            if (L.Length >= Need):
                Id := RewardId()
                if (Id >= 0):
                    Manager.GrantBrainrot(Agent, Id, 0, EventName)
                if (set Collected[P] = array{}) {}
            else if (S := Manager.Sessions[P]):
                S.Hud.Toast("Нужно ещё {Need - L.Length}")

# ---------------------------------------------------------------- Награда на финише
# Пример — «Акулий забег»: кнопка на вершине паркура выдаёт Tralalero Tralala.
lab_finish_reward_device := class(creative_device):
    @editable Manager:lab_manager_device = lab_manager_device{}
    @editable Finish:button_device = button_device{}
    @editable RewardKey:string = "Tralalero_Tralala"
    @editable FromWeek:int = 4
    @editable EventName:string = "Акулий забег"
    @editable OnlyDuringMainEvent:logic = true

    OnBegin<override>()<suspends>:void =
        Finish.InteractedWithEvent.Subscribe(OnFinish)
        Finish.SetInteractionText(LabText("Забрать награду"))

    OnFinish(Agent:agent):void =
        Week := Manager.CurrentWeek()
        Now := LabNow()
        Open := if (OnlyDuringMainEvent?) then logic{Manager.MainEventActive[Now]} else true
        if (Week >= FromWeek, Open?):
            var Id:int = -1
            for (I -> B : LabBrainrots, B.Key = RewardKey):
                set Id = I
            if (Id >= 0):
                Manager.GrantBrainrot(Agent, Id, 0, EventName)
