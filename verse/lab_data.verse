# АВТОГЕНЕРАЦИЯ — не править руками.
# Источник: config/brainrot_lab_tycoon.json, генератор: tools/gen_verse_data.py

rarity_def := struct:
    Name:string = ""
    Income:float = 0.0
    Payback:float = 0.0
    Hatch:float = 0.0
    Weight:float = 0.0
    SellLikes:int = 0

variant_def := struct:
    Name:string = ""
    Mult:float = 1.0
    BeltChance:float = 0.0
    Week:int = 0

brainrot_def := struct:
    Key:string = ""
    Title:string = ""
    Rarity:int = 0
    Family:int = 0
    Source:int = 0
    Week:int = 0

family_def := struct:
    Name:string = ""
    Perk:int = 0
    Members:[]int = array{}

combo_def := struct:
    Name:string = ""
    Bonus:float = 0.0
    Members:[]int = array{}
    Week:int = 0

recipe_def := struct:
    Result:int = 0
    Inputs:[]int = array{}
    Hint:string = ""

rebirth_req := struct:
    Ids:[]int = array{}
    Variants:[]int = array{}

shop_def := struct:
    Key:string = ""
    Name:string = ""
    Cost:int = 0
    MaxLevel:int = 1

tour_def := struct:
    Name:string = ""
    Minutes:float = 0.0
    CostIncomeMin:float = 0.0
    LikesMin:int = 0
    LikesMax:int = 0
    CapsuleChance:float = 0.0
    EpicPlus:logic = false

quest_def := struct:
    Kind:int = 0
    Target:int = 0

offer_def := struct:
    Key:string = ""
    Name:string = ""
    Price:int = 0
    Effect:string = ""
    Week:int = 0

# Редкости
RarityIdx_Common:int = 0
RarityIdx_Rare:int = 1
RarityIdx_Epic:int = 2
RarityIdx_Legendary:int = 3
RarityIdx_Mythic:int = 4
RarityIdx_Iconic:int = 5
# Варианты
VariantIdx_Base:int = 0
VariantIdx_Gold:int = 1
VariantIdx_Diamond:int = 2
VariantIdx_Rainbow:int = 3
VariantIdx_Lava:int = 4
VariantIdx_Viral:int = 5
VariantIdx_Cosmic:int = 6
# Перки компаньонов
Perk_HatchSpeed:int = 0
Perk_PickaxeCrit:int = 1
Perk_BeltDiscount:int = 2
Perk_LikesBonus:int = 3
Perk_VariantUp:int = 4
Perk_CashBonus:int = 5
Perk_OfflineBonus:int = 6
Perk_TourSpeed:int = 7
Perk_FusionSpeed:int = 8
Perk_JunkBonus:int = 9
Perk_IdealLuck:int = 10
Perk_Unique:int = 11
# Типы ежедневных заданий
Quest_Hatch:int = 0
Quest_BuyCapsule:int = 1
Quest_PickaxeHit:int = 2
Quest_Sell:int = 3
Quest_Junk:int = 4
Quest_Tour:int = 5
Quest_Upgrade:int = 6
Quest_HatchEpic:int = 7
Quest_Fusion:int = 8
Quest_Like:int = 9
# Источник брейнрота: 0 конвейер, 1 скрещивание, 2 ивент

LabRarities:[]rarity_def = array:
    rarity_def{Name := "Обычный", Income := 5.0, Payback := 120.0, Hatch := 10.0, Weight := 55.0, SellLikes := 1}
    rarity_def{Name := "Редкий", Income := 40.0, Payback := 240.0, Hatch := 30.0, Weight := 28.0, SellLikes := 4}
    rarity_def{Name := "Эпический", Income := 250.0, Payback := 480.0, Hatch := 60.0, Weight := 12.0, SellLikes := 15}
    rarity_def{Name := "Легендарный", Income := 1500.0, Payback := 900.0, Hatch := 120.0, Weight := 4.5, SellLikes := 60}
    rarity_def{Name := "Мифический", Income := 10000.0, Payback := 1800.0, Hatch := 300.0, Weight := 0.5, SellLikes := 250}
    rarity_def{Name := "Икона", Income := 25000.0, Payback := 0.0, Hatch := 300.0, Weight := 0.0, SellLikes := 0}

LabVariants:[]variant_def = array:
    variant_def{Name := "Базовый", Mult := 1.0, BeltChance := 0.0, Week := 0}
    variant_def{Name := "Золотой", Mult := 2.0, BeltChance := 0.05, Week := 0}
    variant_def{Name := "Алмазный", Mult := 4.0, BeltChance := 0.01, Week := 0}
    variant_def{Name := "Радужный", Mult := 8.0, BeltChance := 0.002, Week := 0}
    variant_def{Name := "Лавовый", Mult := 20.0, BeltChance := 0.0, Week := 5}
    variant_def{Name := "Вирусный", Mult := 50.0, BeltChance := 0.0, Week := 7}
    variant_def{Name := "Космический", Mult := 120.0, BeltChance := 0.0, Week := 10}

# Порядок совпадает с массивом BrainrotProps у lab_manager_device
LabBrainrots:[]brainrot_def = array:
    brainrot_def{Key := "Noobini_Pizzanini", Title := "Noobini Pizzanini", Rarity := 0, Family := 5, Source := 0, Week := 0}
    brainrot_def{Key := "Tim_Cheese", Title := "Tim Cheese", Rarity := 0, Family := 5, Source := 0, Week := 0}
    brainrot_def{Key := "Pipi_Kiwi", Title := "Pipi Kiwi", Rarity := 0, Family := 6, Source := 0, Week := 0}
    brainrot_def{Key := "Trippi_Troppi", Title := "Trippi Troppi", Rarity := 0, Family := 4, Source := 0, Week := 0}
    brainrot_def{Key := "Boneca_Ambalabu", Title := "Boneca Ambalabu", Rarity := 0, Family := 10, Source := 0, Week := 0}
    brainrot_def{Key := "Pandaccini_Bananini", Title := "Pandaccini Bananini", Rarity := 0, Family := 3, Source := 0, Week := 0}
    brainrot_def{Key := "Salamino_Penguino", Title := "Salamino Penguino", Rarity := 0, Family := 5, Source := 0, Week := 0}
    brainrot_def{Key := "Bananita_Dolphinita", Title := "Bananita Dolphinita", Rarity := 0, Family := 4, Source := 0, Week := 0}
    brainrot_def{Key := "Chimpanzini_Bananini", Title := "Chimpanzini Bananini", Rarity := 1, Family := 3, Source := 0, Week := 0}
    brainrot_def{Key := "Spioniro_Golubiro", Title := "Spioniro Golubiro", Rarity := 1, Family := 10, Source := 0, Week := 0}
    brainrot_def{Key := "Talpa_Di_Ferro", Title := "Talpa Di Ferro", Rarity := 1, Family := 8, Source := 0, Week := 0}
    brainrot_def{Key := "Glorbo_Fruttodrillo", Title := "Glorbo Fruttodrillo", Rarity := 1, Family := 6, Source := 0, Week := 0}
    brainrot_def{Key := "Blueberrinni_Octopussini", Title := "Blueberrinni Octopussini", Rarity := 1, Family := 4, Source := 0, Week := 0}
    brainrot_def{Key := "Burbaloni_Luliloli", Title := "Burbaloni Luliloli", Rarity := 1, Family := 3, Source := 0, Week := 0}
    brainrot_def{Key := "Cacto_Hipopotamo", Title := "Cacto Hipopotamo", Rarity := 1, Family := 7, Source := 0, Week := 0}
    brainrot_def{Key := "Strawberrelli_Flamingelli", Title := "Strawberrelli Flamingelli", Rarity := 1, Family := 6, Source := 0, Week := 0}
    brainrot_def{Key := "Cappuccino_Assassino", Title := "Cappuccino Assassino", Rarity := 2, Family := 0, Source := 0, Week := 0}
    brainrot_def{Key := "Ballerina_Cappuccina", Title := "Ballerina Cappuccina", Rarity := 2, Family := 0, Source := 0, Week := 0}
    brainrot_def{Key := "Brr_Brr_Patapim", Title := "Brr Brr Patapim", Rarity := 2, Family := 3, Source := 0, Week := 0}
    brainrot_def{Key := "Orangutini_Ananassini", Title := "Orangutini Ananassini", Rarity := 2, Family := 3, Source := 0, Week := 0}
    brainrot_def{Key := "Graipuss_Medussi", Title := "Graipuss Medussi", Rarity := 2, Family := 4, Source := 0, Week := 0}
    brainrot_def{Key := "Rhino_Toasterino", Title := "Rhino Toasterino", Rarity := 2, Family := 8, Source := 0, Week := 0}
    brainrot_def{Key := "Frigo_Camelo", Title := "Frigo Camelo", Rarity := 2, Family := 8, Source := 1, Week := 3}
    brainrot_def{Key := "Trulimero_Trulicina", Title := "Trulimero Trulicina", Rarity := 2, Family := 4, Source := 1, Week := 3}
    brainrot_def{Key := "Bombardiro_Crocodilo", Title := "Bombardiro Crocodilo", Rarity := 3, Family := 2, Source := 0, Week := 0}
    brainrot_def{Key := "Lirili_Larila", Title := "Lirilì Larilà", Rarity := 3, Family := 7, Source := 0, Week := 0}
    brainrot_def{Key := "Espresso_Signora", Title := "Espresso Signora", Rarity := 3, Family := 0, Source := 0, Week := 0}
    brainrot_def{Key := "Bombombini_Gusini", Title := "Bombombini Gusini", Rarity := 3, Family := 2, Source := 0, Week := 1}
    brainrot_def{Key := "Spaghetti_Tualetti", Title := "Spaghetti Tualetti", Rarity := 3, Family := 5, Source := 1, Week := 3}
    brainrot_def{Key := "Chef_Crabracadabra", Title := "Chef Crabracadabra", Rarity := 3, Family := 4, Source := 1, Week := 3}
    brainrot_def{Key := "Cocofanto_Elefanto", Title := "Cocofanto Elefanto", Rarity := 3, Family := 7, Source := 1, Week := 3}
    brainrot_def{Key := "Dragon_Cannelloni", Title := "Dragon Cannelloni", Rarity := 4, Family := 1, Source := 0, Week := 2}
    brainrot_def{Key := "Draghetto_Gelato", Title := "Draghetto Gelato", Rarity := 4, Family := 1, Source := 0, Week := 4}
    brainrot_def{Key := "Drakonino_Peperonino", Title := "Drakonino Peperonino", Rarity := 4, Family := 1, Source := 0, Week := 6}
    brainrot_def{Key := "Girafa_Celestre", Title := "Girafa Celestre", Rarity := 4, Family := 9, Source := 0, Week := 8}
    brainrot_def{Key := "Svinina_Bombardino", Title := "Svinina Bombardino", Rarity := 4, Family := 2, Source := 1, Week := 3}
    brainrot_def{Key := "La_Vacca_Saturno_Saturnita", Title := "La Vacca Saturno Saturnita", Rarity := 4, Family := 9, Source := 1, Week := 8}
    brainrot_def{Key := "Tung_Tung_Tung_Sahur", Title := "Тунг Тунг Тунг Сахур", Rarity := 5, Family := 11, Source := 2, Week := 1}
    brainrot_def{Key := "Tralalero_Tralala", Title := "Тралалеро Тралала", Rarity := 5, Family := 11, Source := 2, Week := 4}
    brainrot_def{Key := "SixSeven_67", Title := "67 (Six Seven)", Rarity := 5, Family := 11, Source := 2, Week := 7}

BrainrotIdx_TungTungTungSahur:int = 37
BrainrotIdx_TralaleroTralala:int = 38
BrainrotIdx_SixSeven67:int = 39

LabFamilies:[]family_def = array:
    family_def{Name := "Кофейня", Perk := 0, Members := array{17, 16, 26}}
    family_def{Name := "Драконы", Perk := 1, Members := array{31, 32, 33}}
    family_def{Name := "Авиация", Perk := 2, Members := array{24, 27, 35}}
    family_def{Name := "Джунгли", Perk := 3, Members := array{8, 5, 19, 18, 13}}
    family_def{Name := "Океан", Perk := 4, Members := array{7, 12, 20, 29, 3, 23}}
    family_def{Name := "Кухня", Perk := 5, Members := array{28, 6, 0, 1}}
    family_def{Name := "Фрукты", Perk := 6, Members := array{15, 11, 2}}
    family_def{Name := "Саванна", Perk := 7, Members := array{14, 25, 30}}
    family_def{Name := "Техника", Perk := 8, Members := array{21, 22, 10}}
    family_def{Name := "Космос", Perk := 9, Members := array{34, 36}}
    family_def{Name := "Улица", Perk := 10, Members := array{4, 9}}
    family_def{Name := "Иконы", Perk := 11, Members := array{37, 38, 39}}
FamilyIdx_Icons:int = 11

LabCombos:[]combo_def = array:
    combo_def{Name := "Ужин с драконом", Bonus := 0.3, Members := array{31, 0, 26}, Week := 2}
    combo_def{Name := "Итальянский обед", Bonus := 0.3, Members := array{28, 6, 26}, Week := 3}
    combo_def{Name := "Воздушный налёт", Bonus := 0.3, Members := array{24, 27, 9}, Week := 1}
    combo_def{Name := "Кошки-мышки", Bonus := 0.3, Members := array{3, 23, 1}, Week := 3}
    combo_def{Name := "Банановый рай", Bonus := 0.3, Members := array{8, 5, 7}, Week := 0}

# Бонус семьи по числу разных членов на подиуме (индекс = число)
LabFamilyBonusByCount:[]float = array{0.0, 0.0, 0.1, 0.25, 0.4}
LabFamilyFullExtra:float = 0.15

LabRecipes:[]recipe_def = array:
    recipe_def{Result := 28, Inputs := array{0, 6, 1}, Hint := "Вся кухня за одним столом"}
    recipe_def{Result := 22, Inputs := array{21, 10, 14}, Hint := "Техника в пустыне"}
    recipe_def{Result := 23, Inputs := array{3, 7, 12}, Hint := "Кот ушёл в море"}
    recipe_def{Result := 29, Inputs := array{20, 12, 0}, Hint := "Океан на кухне"}
    recipe_def{Result := 30, Inputs := array{25, 13, 14}, Hint := "Слон, кокос и колючки"}
    recipe_def{Result := 35, Inputs := array{24, 27, 6}, Hint := "Авиация и колбаса"}
    recipe_def{Result := 36, Inputs := array{34, 27, 1}, Hint := "Корова, луна и сыр"}

# Требования перерождений 1..35: индекс массива = уровень − 1
LabRebirthReqs:[]rebirth_req = array:
    rebirth_req{Ids := array{0, 1, 2}, Variants := array{0, 0, 0}}
    rebirth_req{Ids := array{3, 4, 5}, Variants := array{0, 0, 0}}
    rebirth_req{Ids := array{6, 7, 8}, Variants := array{0, 0, 0}}
    rebirth_req{Ids := array{9, 10, 0}, Variants := array{0, 0, 1}}
    rebirth_req{Ids := array{11, 12, 13}, Variants := array{0, 0, 0}}
    rebirth_req{Ids := array{14, 15, 1}, Variants := array{0, 0, 1}}
    rebirth_req{Ids := array{16, 17, 2}, Variants := array{0, 0, 2}}
    rebirth_req{Ids := array{18, 19, 8}, Variants := array{0, 0, 1}}
    rebirth_req{Ids := array{20, 21, 12}, Variants := array{0, 0, 1}}
    rebirth_req{Ids := array{24, 16, 3}, Variants := array{0, 1, 3}}
    rebirth_req{Ids := array{25, 26, 17}, Variants := array{0, 0, 1}}
    rebirth_req{Ids := array{24, 25, 26}, Variants := array{1, 1, 1}}
    rebirth_req{Ids := array{18, 19, 20}, Variants := array{1, 1, 1}}
    rebirth_req{Ids := array{21, 15, 14}, Variants := array{1, 2, 2}}
    rebirth_req{Ids := array{24, 16, 11}, Variants := array{2, 2, 2}}
    rebirth_req{Ids := array{25, 17, 13}, Variants := array{2, 2, 3}}
    rebirth_req{Ids := array{26, 18, 9}, Variants := array{2, 2, 3}}
    rebirth_req{Ids := array{24, 19, 10}, Variants := array{3, 2, 3}}
    rebirth_req{Ids := array{25, 20, 8}, Variants := array{3, 2, 3}}
    rebirth_req{Ids := array{26, 21, 12}, Variants := array{3, 2, 3}}
    rebirth_req{Ids := array{27, 16, 15}, Variants := array{1, 3, 3}}
    rebirth_req{Ids := array{28, 17, 11}, Variants := array{0, 3, 3}}
    rebirth_req{Ids := array{29, 22, 23}, Variants := array{0, 1, 1}}
    rebirth_req{Ids := array{30, 27, 18}, Variants := array{0, 2, 3}}
    rebirth_req{Ids := array{31, 28, 19}, Variants := array{0, 1, 3}}
    rebirth_req{Ids := array{35, 29, 20}, Variants := array{0, 1, 3}}
    rebirth_req{Ids := array{32, 30, 21}, Variants := array{0, 1, 3}}
    rebirth_req{Ids := array{31, 24, 22}, Variants := array{1, 4, 2}}
    rebirth_req{Ids := array{33, 25, 23}, Variants := array{0, 4, 2}}
    rebirth_req{Ids := array{32, 26, 35}, Variants := array{1, 4, 1}}
    rebirth_req{Ids := array{34, 24, 30}, Variants := array{0, 5, 2}}
    rebirth_req{Ids := array{36, 33, 29}, Variants := array{0, 1, 4}}
    rebirth_req{Ids := array{31, 34, 25}, Variants := array{2, 1, 5}}
    rebirth_req{Ids := array{32, 35, 26}, Variants := array{2, 2, 5}}
    rebirth_req{Ids := array{36, 33, 24}, Variants := array{1, 2, 6}}

# Цена улучшения в Лайках: [редкость][текущий вариант] → переход на следующий
LabUpgradeCosts:[][]int = array:
    array{5, 10, 25, 65, 125, 225}
    array{20, 50, 150, 270, 400, 700}
    array{100, 300, 1000, 2640, 4500, 7000}
    array{400, 1200, 4000, 8500, 14000, 22000}
    array{1500, 4500, 15000, 35000, 60000, 90000}
    array{}

LabHypeShop:[]shop_def = array:
    shop_def{Key := "second_companion", Name := "2-й компаньон", Cost := 300, MaxLevel := 1}
    shop_def{Key := "daily_crystals", Name := "Кристалл за каждое ежедневное", Cost := 200, MaxLevel := 1}
    shop_def{Key := "reserve_plus", Name := "Запас капсул +5", Cost := 150, MaxLevel := 2}
    shop_def{Key := "extra_incubator", Name := "+1 инкубатор", Cost := 250, MaxLevel := 2}
    shop_def{Key := "belt_luck", Name := "Удача конвейера +10%", Cost := 400, MaxLevel := 5}
    shop_def{Key := "hatch_speed", Name := "Скорость вылупления +10%", Cost := 150, MaxLevel := 5}
    shop_def{Key := "pickaxe_crit", Name := "Крит кирки +5%", Cost := 150, MaxLevel := 5}
    shop_def{Key := "ideal_charm", Name := "Талисман Идеального (шанс ×2)", Cost := 500, MaxLevel := 1}
    shop_def{Key := "offline_cap", Name := "Лимит офлайн-дохода +4 ч", Cost := 200, MaxLevel := 3}
Shop_SecondCompanion:int = 0
Shop_DailyCrystals:int = 1
Shop_ReservePlus:int = 2
Shop_ExtraIncubator:int = 3
Shop_BeltLuck:int = 4
Shop_HatchSpeed:int = 5
Shop_PickaxeCrit:int = 6
Shop_IdealCharm:int = 7
Shop_OfflineCap:int = 8

LabTours:[]tour_def = array:
    tour_def{Name := "Гастроли по району", Minutes := 15.0, CostIncomeMin := 5.0, LikesMin := 10, LikesMax := 30, CapsuleChance := 0.0, EpicPlus := false}
    tour_def{Name := "Тур по Италии", Minutes := 60.0, CostIncomeMin := 15.0, LikesMin := 40, LikesMax := 100, CapsuleChance := 0.25, EpicPlus := false}
    tour_def{Name := "Европейское турне", Minutes := 240.0, CostIncomeMin := 45.0, LikesMin := 150, LikesMax := 350, CapsuleChance := 0.6, EpicPlus := false}
    tour_def{Name := "Мировой тур (на ночь)", Minutes := 480.0, CostIncomeMin := 90.0, LikesMin := 300, LikesMax := 700, CapsuleChance := 1.0, EpicPlus := true}

LabQuestsEasy:[]quest_def = array:
    quest_def{Kind := 0, Target := 5}
    quest_def{Kind := 1, Target := 5}
    quest_def{Kind := 9, Target := 2}
    quest_def{Kind := 2, Target := 100}
    quest_def{Kind := 3, Target := 3}
LabQuestsMedium:[]quest_def = array:
    quest_def{Kind := 0, Target := 20}
    quest_def{Kind := 4, Target := 2}
    quest_def{Kind := 5, Target := 1}
    quest_def{Kind := 6, Target := 1}
    quest_def{Kind := 2, Target := 400}
LabQuestsHard:[]quest_def = array:
    quest_def{Kind := 7, Target := 3}
    quest_def{Kind := 4, Target := 5}
    quest_def{Kind := 8, Target := 1}
    quest_def{Kind := 0, Target := 60}
LabQuestLikes:[]int = array{20, 60, 150}
LabQuestCrystals:[]int = array{0, 0, 1}

LabOffers:[]offer_def = array:
    offer_def{Key := "surge_rainbow", Name := "Сёрдж: Радужный", Price := 200, Effect := "следующая твоя капсула с конвейера — Радужная", Week := 0}
    offer_def{Key := "surge_lava", Name := "Сёрдж: Лавовый", Price := 300, Effect := "следующая твоя капсула — Лавовая", Week := 5}
    offer_def{Key := "surge_viral", Name := "Сёрдж: Вирусный", Price := 400, Effect := "следующая твоя капсула — Вирусная", Week := 7}
    offer_def{Key := "hat", Name := "Шляпа для брейнрота", Price := 250, Effect := "косметика", Week := 0}
    offer_def{Key := "plot_paint", Name := "Покраска участка", Price := 300, Effect := "косметика", Week := 0}
    offer_def{Key := "lab_pack", Name := "Набор лаборанта", Price := 1200, Effect := "+1 инкубатор навсегда и 2 Радужных сёрджа; инкубатор есть и за кристаллы", Week := 0}
    offer_def{Key := "fusion_pack", Name := "Набор скрещивания", Price := 1800, Effect := "скрещивание ×2 быстрее навсегда, 2-й стол скрещивания, 3 Лавовых сёрджа", Week := 3}

# Мем-автомат: шанс перейти на вариант с индексом i (0 не используется)
LabLuckyChance:[]float = array{0.0, 0.5, 0.3, 0.15, 0.07, 0.03, 0.01}

# Скаляры
LabStartCash:float = 1000.0
LabSellCashShare:float = 0.3
LabReserveMax:int = 10
LabMaxPlayers:int = 8
LabRebirthFirstCost:float = 10000.0
LabRebirthGrowth:float = 2.1
LabRebirthIncomeMult:float = 1.2
LabRebirthLevels:int = 35
LabSlotsStart:int = 8
LabSlotsPerLevel:int = 1
LabSlotsMax:int = 30
LabSuperFromWeek:int = 5
LabSuperUnlockRebirth:int = 12
LabCrystalsAt12:float = 11.0
LabCrystalsAt35:float = 379.0
LabSuperIncomeMult:float = 1.25
LabIdealChance:float = 0.005
LabIdealBonus:float = 0.01
LabOfflineRate:float = 0.25
LabOfflineCapHours:float = 8.0
LabBeltStepSec:float = 4.0
LabGuaranteedLegendarySec:float = 600.0
LabGuaranteedRainbowSec:float = 1800.0
LabGuaranteedMythicSec:float = 3600.0
LabGuaranteedMythicWeek:int = 2
LabGuaranteedLavaSec:float = 10800.0
LabGuaranteedLavaWeek:int = 5
LabIncubatorsStart:int = 2
LabIncubatorsMax:int = 4
LabHitSpeedup:float = 0.5
LabCritChance:float = 0.05
LabCritMult:float = 5.0
LabJunkRespawnSec:float = 45.0
LabJunkHits:int = 5
LabSpicyWeek:int = 6
LabSpicyRespawnMult:float = 0.5
LabSpicyLavaWeight:float = 20.0
LabOwnerLikes:int = 20
LabGuestLikes:int = 10
LabFusionUnlockRebirth:int = 3
LabFusionWeek:int = 3
LabFusionVariantMin:float = 2.0
LabFusionEpicMin:float = 5.0
LabFusionLegendaryMin:float = 15.0
LabFusionMythicMin:float = 45.0
LabFusionCostMult:float = 2.0
LabCompanionSlotsStart:int = 1
LabMainEventWeekday:int = 6
LabMainEventStartHourUtc:int = 20
LabMainEventHours:float = 24.0
LabMainEventIncomeMult:float = 2.0
LabMainEventHatchMult:float = 2.0
LabMiniEventWeekday:int = 4
LabMiniEventLikesMult:float = 2.0
LabPinataEverySec:float = 1800.0
LabPinataHitsPerPlayer:int = 60
LabPinataCrystals:int = 5

# Веса редкости для наград «Эпик или выше» (гастроли на ночь)
LabEpicPlusWeights:[]float = array{0.0, 0.0, 70.0, 25.0, 5.0, 0.0}
# Мем-мусор: вес, вариант сёрджа, неделя появления (по порядку видов)
LabJunkNames:[]string = array{"Золотой мем-мусор", "Радужный мем-мусор", "Лавовый мем-мусор"}
LabJunkWeights:[]float = array{70.0, 25.0, 5.0}
LabJunkVariant:[]int = array{1, 3, 4}
LabJunkWeek:[]int = array{0, 0, 5}
# Кристаллы за «Вирусный взрыв»: индекс = перерождение − 12
LabSuperCrystals:[]int = array{11, 13, 15, 17, 20, 24, 28, 32, 38, 44, 51, 60, 70, 81, 95, 111, 129, 151, 176, 205, 239, 279, 325, 379}
# Сила перка компаньона по редкости
LabCompanionPerk:[]float = array{0.05, 0.1, 0.15, 0.25, 0.4, 0.4}
