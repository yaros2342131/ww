# Интерфейс: HUD (всегда на экране) и меню-панели (Запас, Перерождение, Скрещивание …).
# Меню универсальное: заголовок + строки текста + кнопки. Каждая кнопка несёт код действия,
# который обрабатывает lab_manager_device.OnMenuAction — экраны собираются в lab_screens.verse.
# Эмодзи не используем: шрифт Fortnite их может не показать.
using { /Verse.org/Simulation }
using { /Verse.org/Colors }
using { /Fortnite.com/UI }
using { /UnrealEngine.com/Temporary/UI }
using { /UnrealEngine.com/Temporary/SpatialMath }

menu_button := struct:
    Label:string = ""
    Action:int = 0
    Arg:int = 0

menu_screen := struct:
    Title:string = ""
    Lines:[]string = array{}
    Buttons:[]menu_button = array{}

menu_click := class:
    Manager:lab_manager_device
    Player:player
    Action:int
    Arg:int

    OnClick(Message:widget_message):void =
        Manager.OnMenuAction(Player, Action, Arg)

# ---------------------------------------------------------------- HUD
lab_hud := class:
    Player:player
    CashText:text_block = text_block{DefaultTextColor := NamedColors.Gold}
    InfoText:text_block = text_block{DefaultTextColor := NamedColors.White}
    HandsText:text_block = text_block{DefaultTextColor := NamedColors.Cyan}
    HintText:text_block = text_block{DefaultTextColor := NamedColors.LightGray}
    StormText:text_block = text_block{DefaultTextColor := NamedColors.Orange}
    EventText:text_block = text_block{DefaultTextColor := NamedColors.HotPink}
    ToastBox:stack_box = stack_box{Orientation := orientation.Vertical}
    var Root:?canvas = false

    Show():void =
        Left := stack_box:
            Orientation := orientation.Vertical
            Slots := array:
                stack_box_slot{Widget := CashText, HorizontalAlignment := horizontal_alignment.Left}
                stack_box_slot{Widget := InfoText, HorizontalAlignment := horizontal_alignment.Left, Padding := margin{Top := 4.0}}
                stack_box_slot{Widget := HandsText, HorizontalAlignment := horizontal_alignment.Left, Padding := margin{Top := 4.0}}
                stack_box_slot{Widget := HintText, HorizontalAlignment := horizontal_alignment.Left, Padding := margin{Top := 8.0}}
        Top := stack_box:
            Orientation := orientation.Vertical
            Slots := array:
                stack_box_slot{Widget := StormText, HorizontalAlignment := horizontal_alignment.Center}
                stack_box_slot{Widget := EventText, HorizontalAlignment := horizontal_alignment.Center, Padding := margin{Top := 4.0}}
                stack_box_slot{Widget := ToastBox, HorizontalAlignment := horizontal_alignment.Center, Padding := margin{Top := 14.0}}
        C := canvas:
            Slots := array:
                canvas_slot:
                    Anchors := anchors{Minimum := vector2{X := 0.0, Y := 0.32}, Maximum := vector2{X := 0.0, Y := 0.32}}
                    Offsets := margin{Left := 24.0}
                    Alignment := vector2{X := 0.0, Y := 0.0}
                    SizeToContent := true
                    Widget := Left
                canvas_slot:
                    Anchors := anchors{Minimum := vector2{X := 0.5, Y := 0.0}, Maximum := vector2{X := 0.5, Y := 0.0}}
                    Offsets := margin{Top := 96.0}
                    Alignment := vector2{X := 0.5, Y := 0.0}
                    SizeToContent := true
                    Widget := Top
        if (UI := GetPlayerUI[Player]):
            UI.AddWidget(C)
            set Root = option{C}

    Hide():void =
        if (C := Root?, UI := GetPlayerUI[Player]):
            UI.RemoveWidget(C)
        set Root = false

    SetStats(Cash:string, Info:string, Hands:string, Hint:string):void =
        CashText.SetText(LabText(Cash))
        InfoText.SetText(LabText(Info))
        HandsText.SetText(LabText(Hands))
        HintText.SetText(LabText(Hint))

    SetStorm(Text:string):void = StormText.SetText(LabText(Text))
    SetEvent(Text:string):void = EventText.SetText(LabText(Text))

    # Всплывающее сообщение на 5 секунд
    Toast(Text:string):void =
        T := text_block{DefaultText := LabText(Text), DefaultTextColor := NamedColors.White}
        ToastBox.AddWidget(stack_box_slot{Widget := T, HorizontalAlignment := horizontal_alignment.Center})
        spawn{ RemoveLater(T) }

    RemoveLater(W:widget)<suspends>:void =
        Sleep(5.0)
        ToastBox.RemoveWidget(W)

# ---------------------------------------------------------------- меню
lab_menu := class:
    Player:player
    var Root:?canvas = false

    IsOpen()<transacts>:logic = if (Root?) then true else false

    Show(Manager:lab_manager_device, Screen:menu_screen):void =
        Close()
        Box := stack_box{Orientation := orientation.Vertical}
        Title := text_block{DefaultText := LabText(Screen.Title), DefaultTextColor := NamedColors.Gold}
        Box.AddWidget(stack_box_slot{Widget := Title, HorizontalAlignment := horizontal_alignment.Center, Padding := margin{Bottom := 12.0}})
        for (Line : Screen.Lines):
            Box.AddWidget(stack_box_slot{Widget := text_block{DefaultText := LabText(Line), DefaultTextColor := NamedColors.White}, HorizontalAlignment := horizontal_alignment.Left})
        # Кнопки по две в ряд
        var Row:stack_box = stack_box{Orientation := orientation.Horizontal}
        for (I -> B : Screen.Buttons):
            if (Mod[I, 2] = 0):
                set Row = stack_box{Orientation := orientation.Horizontal}
                Box.AddWidget(stack_box_slot{Widget := Row, HorizontalAlignment := horizontal_alignment.Center, Padding := margin{Top := 6.0}})
            Btn := button_quiet{DefaultText := LabText(B.Label)}
            Btn.OnClick().Subscribe(menu_click{Manager := Manager, Player := Player, Action := B.Action, Arg := B.Arg}.OnClick)
            Row.AddWidget(stack_box_slot{Widget := Btn, Padding := margin{Left := 6.0, Right := 6.0}})
        CloseBtn := button_loud{DefaultText := LabText("Закрыть")}
        CloseBtn.OnClick().Subscribe(menu_click{Manager := Manager, Player := Player, Action := Act_Close, Arg := 0}.OnClick)
        Box.AddWidget(stack_box_slot{Widget := CloseBtn, HorizontalAlignment := horizontal_alignment.Center, Padding := margin{Top := 16.0}})
        Panel := overlay:
            Slots := array:
                overlay_slot:
                    Widget := color_block{DefaultColor := NamedColors.Black, DefaultOpacity := 0.82, DefaultDesiredSize := vector2{X := 980.0, Y := 760.0}}
                    HorizontalAlignment := horizontal_alignment.Fill
                    VerticalAlignment := vertical_alignment.Fill
                overlay_slot:
                    Widget := Box
                    Padding := margin{Left := 32.0, Top := 24.0, Right := 32.0, Bottom := 24.0}
                    HorizontalAlignment := horizontal_alignment.Fill
                    VerticalAlignment := vertical_alignment.Top
        C := canvas:
            Slots := array:
                canvas_slot:
                    Anchors := anchors{Minimum := vector2{X := 0.5, Y := 0.5}, Maximum := vector2{X := 0.5, Y := 0.5}}
                    Alignment := vector2{X := 0.5, Y := 0.5}
                    SizeToContent := true
                    Widget := Panel
        if (UI := GetPlayerUI[Player]):
            UI.AddWidget(C, player_ui_slot{InputMode := ui_input_mode.All})
            set Root = option{C}

    Close():void =
        if (C := Root?, UI := GetPlayerUI[Player]):
            UI.RemoveWidget(C)
        set Root = false
