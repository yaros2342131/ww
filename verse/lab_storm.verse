# Хайп-шторм — общая шкала всего лобби.
# Очки дают вылупления, удары киркой, скрещивание, собранные семьи и задания.
# Порог сам подстраивается: он равен очкам лобби за последние 12 минут (но не меньше 20 × игроков),
# поэтому шторм идёт примерно раз в 12–20 минут на любом этапе игры.
using { /Fortnite.com/Devices }
using { /Verse.org/Simulation }

storm_point := struct:
    Time:float = 0.0
    Points:float = 0.0

lab_storm_device := class(creative_device):
    @editable MeterBoard:billboard_device = billboard_device{}      # табло на башне шторма в хабе
    @editable StormEffects:[]vfx_spawner_device = array{}          # молнии, конфетти — включаются на шторм
    @editable StormMusic:audio_player_device = audio_player_device{}
    @editable FirstStormDelay:float = 120.0                         # первый шторм не раньше, чем через 2 мин после старта сервера

    var Manager:?lab_manager_device = false
    var Meter:float = 0.0
    var History:[]storm_point = array{}
    var Contrib:[player]float = map{}
    var Active:logic = false
    var EndsAt:float = 0.0
    var ReadyAt:float = 0.0
    var Threshold:float = 1.0

    Init(M:lab_manager_device):void =
        set Manager = option{M}
        for (V : StormEffects):
            V.Disable()
        set ReadyAt = GetSimulationElapsedTime() + FirstStormDelay

    IsActive()<transacts>:logic = Active

    Fill()<transacts>:float = if (Threshold > 0.0) then Min(1.0, Meter / Threshold) else 0.0

    TimeLeft():float = Max(0.0, EndsAt - GetSimulationElapsedTime())

    AddPoints(Who:?player, Pts:float):void =
        if (Pts <= 0.0):
            return
        set Meter += Pts
        set History += array{storm_point{Time := GetSimulationElapsedTime(), Points := Pts}}
        if (P := Who?):
            Old := if (V := Contrib[P]) then V else 0.0
            if (set Contrib[P] = Old + Pts) {}

    # «Хайп-бомба» (покупка за V-Bucks): +50% шкалы
    AddBomb():void = AddPoints(false, Max(Threshold, 1.0) * 0.5)

    Tick(PlayerCount:int):void =
        Now := GetSimulationElapsedTime()
        set History = for (H : History, H.Time >= Now - LabStormWindowSec): H
        var Sum:float = 0.0
        for (H : History):
            set Sum += H.Points
        set Threshold = Max(Max(1, PlayerCount) * LabStormFloorPerPlayer, Sum)
        if (Active?):
            if (Now >= EndsAt):
                Finish()
        else if (Now >= ReadyAt, Meter >= Threshold):
            Start(Now)
        UpdateBoard()

    Start(Now:float):void =
        set Active = true
        set EndsAt = Now + LabStormDurationSec
        set ReadyAt = EndsAt + LabStormCooldownSec
        Need := Threshold * LabStormContribShare
        Winners := for (P -> V : Contrib, V >= Need): P
        set Contrib = map{}
        set Meter = 0.0
        for (V : StormEffects):
            V.Enable()
        StormMusic.Play()
        if (M := Manager?):
            M.OnStormStart(Winners)

    Finish():void =
        set Active = false
        for (V : StormEffects):
            V.Disable()
        StormMusic.Stop()
        if (M := Manager?):
            M.OnStormEnd()

    Line():string =
        if (Active?):
            "ХАЙП-ШТОРМ! Доход x2 · ещё {FormatTime(TimeLeft())}"
        else:
            Pct := FloorInt(Fill() * 100.0)
            "Хайп [{ProgressBar(Fill(), 20)}] {Pct}%"

    UpdateBoard():void = MeterBoard.SetText(LabText(Line()))
