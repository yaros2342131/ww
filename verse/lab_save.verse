# Сохранение прогресса между сессиями (Verse persistence).
# Лимиты Epic: не больше 4 постоянных weak_map на остров, запись игрока — до 256 КБ.
# Правило: поля только ДОБАВЛЯТЬ со значением по умолчанию. Удалить поле или сменить его тип —
# значит сломать сохранения всех игроков.
using { /Verse.org/Simulation }

# Один брейнрот игрока
brainrot_rec := struct<persistable>:
    Uid:int = 0            # уникальный номер внутри игрока (для компаньонов и меню)
    Id:int = 0             # индекс в LabBrainrots
    Variant:int = 0        # индекс в LabVariants
    Ideal:logic = false    # «Идеальный»
    Slot:int = -1          # место на подиуме; −1 = в запасе

# Капсула: в руках, в запасе, в инкубаторе
capsule_rec := struct<persistable>:
    Id:int = 0
    Variant:int = 0

# Таймер: инкубатор, стол скрещивания, гастроли
timer_rec := struct<persistable>:
    Active:logic = false
    Kind:int = 0           # инкубатор/скрещивание: id брейнрота; гастроли: номер тура
    Variant:int = 0
    EndsAt:float = 0.0     # Unix-время окончания
    Total:float = 0.0      # полная длительность, для полоски прогресса

lab_save := class<final><persistable>:
    Version:int = 1
    Cash:float = 0.0
    Likes:int = 0
    Crystals:int = 0
    Rebirth:int = 0
    SuperRebirths:int = 0
    NextUid:int = 1
    Brainrots:[]brainrot_rec = array{}
    Reserve:[]capsule_rec = array{}
    Carrying:[]capsule_rec = array{}      # 0 или 1 элемент: капсула в руках
    Incubators:[]timer_rec = array{}
    Fusions:[]timer_rec = array{}
    Tours:[]timer_rec = array{}
    Discovered:[]int = array{}            # id, которые игрок хоть раз выводил (Мемопедия)
    IdealFound:[]int = array{}            # id, у которых был «Идеальный»
    RecipesFound:[]int = array{}          # индексы открытых секретных рецептов
    FamiliesDone:[]int = array{}          # семьи, которые уже собирались целиком (объявление один раз)
    ShopLevels:[]int = array{}            # уровни покупок Хайп-магазина
    Companions:[]int = array{}            # Uid брейнротов-компаньонов
    PersonalSurges:[]int = array{}        # купленные «сёрджи»: индекс варианта
    LastSeen:float = 0.0
    PlaySeconds:float = 0.0
    QuestDay:int = -1
    QuestProgress:[]int = array{}
    QuestClaimed:[]logic = array{}
    LuckyDay:int = -1
    TotalHatched:int = 0
    LikeDay:int = -1                      # день (UTC), к которому относится LikedPlots
    LikedPlots:[]int = array{}            # номера участков, которые игрок лайкнул сегодня

var LabSaves:weak_map(player, lab_save) = map{}
