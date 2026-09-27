# Общие помощники: текст, числа, время, случайность.
using { /Verse.org/Simulation }
using { /Verse.org/Random }

# Строка → message (для UI, табло и кнопок)
LabText<localizes>(S:string):message = "{S}"

# Реальное время Unix (секунды с 1970 UTC): офлайн-доход, таймеры, расписание ивентов.
# Все вызовы времени идут через эту функцию — если API поменяется, править одно место.
LabNow():float = GetSecondsSinceEpoch()

FloorInt(V:float)<transacts>:int =
    if (R := Floor[V]) then R else 0

# Возведение в целую степень (множители перерождений, цены)
PowInt(Base:float, N:int)<transacts>:float =
    var R:float = 1.0
    for (I := 1..N):
        set R *= Base
    R

LabSuffixes:[]string = array{"", "K", "M", "B", "T", "Qa", "Qi", "Sx", "Sp", "Oc"}

# 1234567 → "1.2M"
FormatNum(Value:float)<transacts>:string =
    var V:float = Value
    var I:int = 0
    loop:
        if (V < 1000.0 or I >= LabSuffixes.Length - 1):
            break
        set V = V / 1000.0
        set I += 1
    Suffix := LabSuffixes[I] or ""
    if (I = 0):
        "{FloorInt(V)}"
    else:
        Tenths := FloorInt(V * 10.0)
        Whole := Quotient[Tenths, 10] or 0
        Frac := Mod[Tenths, 10] or 0
        if (Whole >= 100 or Frac = 0) then "{Whole}{Suffix}" else "{Whole}.{Frac}{Suffix}"

# 3725 → "1:02:05", 65 → "1:05"
FormatTime(Seconds:float)<transacts>:string =
    S := Max(0, FloorInt(Seconds))
    H := Quotient[S, 3600] or 0
    Rest := Mod[S, 3600] or 0
    M := Quotient[Rest, 60] or 0
    Sec := Mod[Rest, 60] or 0
    SecPad := if (Sec < 10) then "0" else ""
    if (H > 0):
        MinPad := if (M < 10) then "0" else ""
        "{H}:{MinPad}{M}:{SecPad}{Sec}"
    else:
        "{M}:{SecPad}{Sec}"

# Текстовая полоска прогресса: "|||||.....", Filled от 0 до 1
ProgressBar(Filled:float, Width:int)<transacts>:string =
    N := Max(0, Min(Width, FloorInt(Filled * (Width * 1.0))))
    var Out:string = ""
    for (I := 1..Width):
        set Out += if (I <= N) then "|" else "."
    Out

Chance(P:float)<transacts>:logic = logic{GetRandomFloat(0.0, 1.0) < P}

# Индекс по весам (веса ≥ 0). Если все веса нулевые — 0.
PickWeighted(Weights:[]float)<transacts>:int =
    var Total:float = 0.0
    for (W : Weights):
        set Total += W
    if (Total <= 0.0):
        return 0
    var R:float = GetRandomFloat(0.0, Total)
    var Result:int = -1
    for (I -> W : Weights, Result < 0):
        if (R < W):
            set Result = I
        else:
            set R -= W
    if (Result < 0) then Weights.Length - 1 else Result

# Календарь (UTC). 1 января 1970 — четверг, поэтому +4: 0 = воскресенье … 6 = суббота.
LabDay(Now:float)<transacts>:int = FloorInt(Now / 86400.0)
LabWeekday(Now:float)<transacts>:int = Mod[LabDay(Now) + 4, 7] or 0
LabHourUtc(Now:float)<transacts>:float = (Now - LabDay(Now) * 86400.0) / 3600.0

ContainsInt(Arr:[]int, V:int)<transacts>:logic =
    var Found:logic = false
    for (X : Arr, X = V):
        set Found = true
    Found

CountPresent(Members:[]int, Ids:[]int)<transacts>:int =
    var N:int = 0
    for (M : Members, ContainsInt(Ids, M)?):
        set N += 1
    N
