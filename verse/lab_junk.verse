# Мем-мусор — аналог Chopper из Droid Tycoon.
# На пьяцце появляются кучи мем-мусора. Кучу бьют (E или киркой) — после нескольких ударов мусор в руках.
# Мусор несут Сахуру у портала — и ближайшая капсула на конвейере становится Золотой, Радужной или
# Лавовой. Купить её может любой игрок.
using { /Fortnite.com/Devices }
using { /Verse.org/Simulation }
using { /Verse.org/Random }

# Одна точка, где появляется куча. Props — пропы кучи по видам мусора в порядке LabJunkNames
# (Золотой, Радужный, Лавовый); все стоят в одной точке, Verse показывает нужный.
junk_pile := class<concrete>:
    @editable Button:button_device = button_device{}
    @editable Hits:prop_manipulator_device = prop_manipulator_device{}
    @editable Props:[]creative_prop = array{}
    var Kind:int = -1          # −1 = кучи сейчас нет
    var HitsLeft:int = 0
    var RespawnAt:float = 0.0

junk_handler := class:
    Device:lab_junk_device
    Index:int

    OnHit(Agent:agent):void = Device.HitPile(Agent, Index)

lab_junk_device := class(creative_device):
    @editable Manager:lab_manager_device = lab_manager_device{}
    @editable Piles:[]junk_pile = array{}
    @editable Collector:button_device = button_device{}     # у тотема Сахура: «Сдать мем-мусор»
    @editable Board:billboard_device = billboard_device{}

    OnBegin<override>()<suspends>:void =
        for (I -> P : Piles):
            H := junk_handler{Device := Self, Index := I}
            P.Button.InteractedWithEvent.Subscribe(H.OnHit)
            P.Hits.DamagedEvent.Subscribe(H.OnHit)
            HideProps(P)
            P.Button.SetInteractionText(LabText("Пусто"))
            set P.RespawnAt = GetSimulationElapsedTime() + GetRandomFloat(2.0, 20.0)
        Collector.InteractedWithEvent.Subscribe(OnDeliver)
        Collector.SetInteractionText(LabText("Сдать мем-мусор Сахуру"))
        loop:
            Sleep(1.0)
            Now := GetSimulationElapsedTime()
            for (P : Piles, P.Kind < 0, Now >= P.RespawnAt):
                SpawnPile(P)
            Active := for (P : Piles, P.Kind >= 0): P
            Board.SetText(LabText("Сахур собирает мем-мусор · куч на площади: {Active.Length}"))

    HideProps(P:junk_pile):void =
        for (Pr : P.Props):
            Pr.Hide()

    SpawnPile(P:junk_pile):void =
        Week := Manager.CurrentWeek()
        Spicy := Manager.IsSpicy()
        var Weights:[]float = array{}
        for (I -> W : LabJunkWeights):
            var Val:float = W
            if (Wk := LabJunkWeek[I], Wk > Week):
                set Val = 0.0
            else if (Spicy?, V := LabJunkVariant[I], V = VariantIdx_Lava):
                set Val = LabSpicyLavaWeight
            set Weights += array{Val}
        set P.Kind = PickWeighted(Weights)
        set P.HitsLeft = LabJunkHits
        for (I -> Pr : P.Props):
            if (I = P.Kind) then Pr.Show() else Pr.Hide()
        UpdateText(P)

    UpdateText(P:junk_pile):void =
        if (Name := LabJunkNames[P.Kind]):
            P.Button.SetInteractionText(LabText("Бить: {Name} (ещё {P.HitsLeft})"))

    HitPile(Agent:agent, Index:int):void =
        if (P := Piles[Index], P.Kind >= 0):
            set P.HitsLeft -= 1
            if (P.HitsLeft > 0):
                UpdateText(P)
            else:
                Taken := Manager.PickUpJunk(Agent, P.Kind)
                if (Taken?):
                    set P.Kind = -1
                    HideProps(P)
                    P.Button.SetInteractionText(LabText("Пусто"))
                    Spicy := Manager.IsSpicy()
                    Mult := if (Spicy?) then LabSpicyRespawnMult else 1.0
                    set P.RespawnAt = GetSimulationElapsedTime() + LabJunkRespawnSec * Mult
                else:
                    # руки заняты мусором — куча ждёт одного удара
                    set P.HitsLeft = 1
                    UpdateText(P)

    OnDeliver(Agent:agent):void = Manager.DeliverJunk(Agent)
