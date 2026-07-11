# maps.py 负责保存四张地图的数据和构造函数。
# 地图格子只表达“能不能走、是什么地形”，真正漂亮的建筑外观在 rendering.py 里画。
from config import MAP_COLS, MAP_ROWS

# 第一张地图的送达点名称，坐标格式为 (列, 行)。
DORM_NAMES = {
    (1, 8): "\u5357\u5149\u56ed\u533a",
    (6, 8): "\u8299\u84c9\u56ed\u533a",
    (18, 13): "\u5b66\u751f\u6d3b\u52a8\u4e2d\u5fc3",
    (24, 8): "\u7bee\u7403\u573a\u9001\u8fbe\u70b9",
}

# 第一张地图的取餐点名称，黄色 G 格子会从这些点里随机刷新。
PICKUP_NAMES = {
    (0, 0): "\u897f\u5317\u6821\u95e8\u53d6\u9910\u70b9",
    (12, 7): "\u8299\u84c9\u56ed\u65c1\u53d6\u9910\u70b9",
    (31, 0): "\u4e1c\u5317\u6821\u95e8\u53d6\u9910\u70b9",
}

CANTEENS = {}

# 地图上显示的区域文字标签，不一定参与任务，只用于让玩家看懂地点。
PLAYGROUND_LABELS = {
    (4, 8): "\u5357\u5149\u56ed\u533a",
    (8, 11): "\u8299\u84c9\u56ed\u533a",
    (15, 11): "\u7ade\u4e30\u9910\u5385",
    (15, 3): "\u8db3\u7403\u573a",
    (24, 4): "\u4e00\u671f\u64cd\u573a",
    (21, 11): "\u7bee\u7403\u573a",
    (28, 11): "\u7bee\u7403\u573a",
    (21, 16): "\u5b66\u751f\u6d3b\u52a8\u4e2d\u5fc3",
    (28, 16): "\u8299\u84c9\u6e56",
}


# 构造第一张地图：先全部填成障碍物，再逐步铺道路、操场、湖、取餐点和送达点。
def build_map():
    grid = [["B" for _ in range(MAP_COLS)] for _ in range(MAP_ROWS)]

    # 下面几个小工具函数可以用“格子坐标”快速画道路或矩形区域。
    def set_tile(x, y, value):
        if 0 <= x < MAP_COLS and 0 <= y < MAP_ROWS:
            grid[y][x] = value

    def hroad(y, x1, x2):
        for x in range(x1, x2 + 1):
            set_tile(x, y, "R")

    def vroad(x, y1, y2):
        for y in range(y1, y2 + 1):
            set_tile(x, y, "R")

    def rect(x1, y1, x2, y2, value):
        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1):
                set_tile(x, y, value)

    # 主路和支路：用横路、竖路把地图可通行区域连接起来。
    hroad(0, 0, 31)
    hroad(5, 0, 24)
    hroad(8, 0, 13)
    hroad(8, 18, 31)
    hroad(13, 0, 24)
    hroad(17, 0, 24)
    vroad(0, 0, 17)
    vroad(6, 5, 17)
    vroad(12, 5, 17)
    vroad(13, 0, 17)
    vroad(18, 0, 13)
    vroad(24, 8, 17)

    rect(14, 1, 16, 5, "F")
    rect(18, 1, 30, 7, "P")
    rect(18, 9, 23, 12, "K")
    rect(25, 9, 30, 12, "K")
    rect(25, 14, 31, 17, "L")
    rect(14, 6, 17, 8, "R")
    rect(14, 8, 17, 12, "R")
    rect(14, 9, 16, 11, "B")
    vroad(17, 8, 13)

    # 右侧区域的补充道路，让操场、湖边和篮球场之间可以连通。
    vroad(17, 2, 6)
    set_tile(17, 1, "R")
    vroad(31, 1, 7)
    vroad(31, 9, 13)
    hroad(13, 25, 31)
    vroad(24, 9, 13)

    for pos in DORM_NAMES:
        set_tile(*pos, "D")
    for pos in PICKUP_NAMES:
        set_tile(*pos, "G")
    for pos in [(0, 17), (13, 17), (24, 17)]:
        set_tile(*pos, "C")

    return ["".join(row) for row in grid]


# 第一张地图构造完成后保存成固定数据，游戏运行时直接读取。
MAP_ONE_DORM_NAMES = DORM_NAMES.copy()
MAP_ONE_PICKUP_NAMES = PICKUP_NAMES.copy()
MAP_ONE_LABELS = PLAYGROUND_LABELS.copy()
MAP_ONE_GRID = build_map()
MAP_ONE_PATROLS = [
    [(10, 0), (13, 0), (13, 5), (10, 5)],
    [(0, 13), (6, 13), (6, 17), (0, 17)],
    [(13, 0), (18, 0), (18, 8), (13, 8)],
    [(18, 13), (24, 13), (24, 8), (18, 8)],
]


# 构造第二张地图，主要包括湖畔区域、游泳馆、思源餐厅和航空航天学院。
def build_map_two():
    dorm_names = {
        (11, 4): "佘明培游泳馆",
        (24, 10): "\u822a\u7a7a\u822a\u5929\u5b66\u9662",
    }
    pickup_names = {
        (11, 15): "\u601d\u6e90\u9910\u5385\u53d6\u9910\u70b9",
    }
    labels = {
        (6, 4): "佘明培游泳馆",
        (8, 10): "\u7231\u79cb\u4f53\u80b2\u9986",
        (11, 15): "\u601d\u6e90\u9910\u5385",
        (20, 11): "\u822a\u7a7a\u822a\u5929\u5b66\u9662",
        (26, 2): "\u8299\u84c9\u6e56",
        (28, 12): "\u8299\u84c9\u6e56",
    }
    grid = [["R" for _ in range(MAP_COLS)] for _ in range(MAP_ROWS)]

    # 第二张地图默认是道路，再把湖、草地、建筑等区域覆盖上去。
    def set_tile(x, y, value):
        if 0 <= x < MAP_COLS and 0 <= y < MAP_ROWS:
            grid[y][x] = value

    def hroad(y, x1, x2):
        for x in range(x1, x2 + 1):
            set_tile(x, y, "R")

    def vroad(x, y1, y2):
        for y in range(y1, y2 + 1):
            set_tile(x, y, "R")

    def rect(x1, y1, x2, y2, value):
        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1):
                set_tile(x, y, value)

    rect(1, 0, 11, 1, "L")
    rect(14, 0, 23, 3, "L")
    rect(25, 0, 31, 3, "L")
    rect(25, 5, 31, 16, "L")
    rect(1, 2, 11, 5, "S")
    rect(1, 7, 11, 8, "S")
    rect(1, 11, 11, 12, "S")
    rect(1, 14, 5, 16, "S")
    rect(14, 5, 23, 6, "S")
    rect(14, 7, 16, 16, "S")
    rect(17, 15, 23, 16, "S")
    rect(17, 7, 24, 14, "R")
    rect(18, 8, 23, 13, "B")

    rect(3, 3, 9, 5, "B")
    rect(3, 7, 9, 12, "B")
    rect(6, 14, 9, 17, "B")
    rect(18, 8, 23, 13, "B")

    hroad(4, 10, 31)
    hroad(6, 0, 13)
    hroad(9, 0, 2)
    hroad(9, 10, 11)
    hroad(13, 0, 13)
    hroad(17, 0, 31)
    vroad(0, 0, 17)
    vroad(12, 0, 17)
    vroad(13, 0, 17)
    vroad(24, 0, 17)

    hroad(7, 17, 24)
    hroad(14, 17, 24)
    vroad(17, 7, 14)
    vroad(24, 7, 17)

    for pos in dorm_names:
        set_tile(*pos, "D")
    for pos in pickup_names:
        set_tile(*pos, "G")
    for pos in [(0, 0), (13, 0), (24, 0)]:
        set_tile(*pos, "C")

    patrols = [
        [(0, 6), (12, 6), (12, 9), (0, 9)],
        [(12, 13), (12, 17), (6, 17), (6, 13)],
        [(24, 9), (24, 13), (24, 17), (20, 17)],
        [(17, 17), (24, 17), (24, 13), (13, 13)],
    ]
    return ["".join(row) for row in grid], dorm_names, pickup_names, labels, patrols


MAP_TWO_GRID, MAP_TWO_DORM_NAMES, MAP_TWO_PICKUP_NAMES, MAP_TWO_LABELS, MAP_TWO_PATROLS = build_map_two()

# 构造第三张地图，主要包括映雪园区、国光园区、药学院、丰庭餐厅等区域。
def build_map_three():
    dorm_names = {
        (6, 4): "映雪园区",
        (5, 12): "国光园区",
        (13, 4): "快递服务中心",
        (25, 0): "药学院",
        (20, 11): "笃行园区",
        (30, 13): "丰庭园区",
    }
    pickup_names = {
        (28, 15): "丰庭餐厅取餐点",
    }
    labels = {
        (6, 4): "映雪园区",
        (5, 12): "国光园区",
        (25, 3): "药学院",
        (15, 11): "笃行园区",
        (23, 11): "笃行园区",
        (30, 11): "丰庭园区",
        (30, 15): "丰庭餐厅",
        (22, 15): "二期操场",
        (14, 15): "草坪",
        (14, 15): "篮球场",
    }
    grid = [["R" for _ in range(MAP_COLS)] for _ in range(MAP_ROWS)]

    # 第三张地图同样用这些工具函数批量设置格子。
    def set_tile(x, y, value):
        if 0 <= x < MAP_COLS and 0 <= y < MAP_ROWS:
            grid[y][x] = value

    def hroad(y, x1, x2):
        for x in range(x1, x2 + 1):
            set_tile(x, y, "R")

    def vroad(x, y1, y2):
        for y in range(y1, y2 + 1):
            set_tile(x, y, "R")

    def rect(x1, y1, x2, y2, value):
        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1):
                set_tile(x, y, value)

    rect(1, 0, 12, 0, "H")
    rect(1, 2, 1, 6, "H")
    rect(11, 1, 11, 6, "H")
    rect(1, 8, 12, 8, "H")
    rect(1, 9, 1, 16, "H")
    rect(12, 10, 12, 16, "H")
    rect(1, 16, 12, 16, "H")
    set_tile(12, 0, "R")
    set_tile(1, 8, "H")
    set_tile(1, 9, "R")
    set_tile(12, 13, "R")

    rect(14, 1, 22, 1, "S")
    rect(14, 2, 14, 2, "S")
    rect(18, 2, 22, 2, "S")
    rect(18, 3, 22, 5, "S")
    rect(14, 6, 28, 7, "S")
    rect(28, 1, 28, 6, "S")
    rect(30, 1, 31, 7, "S")
    rect(13, 14, 16, 16, "K")
    rect(18, 14, 27, 16, "P")

    rect(3, 2, 3, 3, "B"); rect(5, 2, 5, 3, "B"); rect(7, 2, 7, 3, "B"); rect(9, 2, 9, 3, "B")
    rect(3, 5, 3, 6, "B"); rect(5, 5, 5, 6, "B"); rect(7, 5, 7, 6, "B"); rect(9, 5, 9, 6, "B")
    rect(2, 10, 2, 11, "B"); rect(4, 10, 4, 11, "B"); rect(6, 10, 6, 11, "B"); rect(8, 10, 8, 11, "B"); rect(10, 10, 10, 11, "B")
    rect(2, 13, 2, 14, "B"); rect(4, 13, 4, 14, "B"); rect(6, 13, 6, 14, "B"); rect(8, 13, 8, 14, "B"); rect(10, 13, 10, 14, "B")

    rect(15, 2, 17, 6, "B")
    rect(23, 1, 27, 5, "B")
    rect(13, 10, 19, 12, "B")
    rect(21, 10, 27, 12, "B")
    rect(29, 10, 31, 12, "B")
    rect(29, 14, 31, 16, "B")

    for pos in dorm_names:
        set_tile(*pos, "D")
    for pos in pickup_names:
        set_tile(*pos, "G")
    for pos in [(0, 0), (13, 0), (31, 0)]:
        set_tile(*pos, "C")

    patrols = [
        [(13, 8), (28, 8), (28, 13), (13, 13)],
        [(29, 1), (31, 1), (31, 8), (29, 8)],
        [(2, 9), (11, 9), (11, 15), (2, 15)],
        [(14, 0), (30, 0), (30, 8), (14, 8)],
    ]
    return ["".join(row) for row in grid], dorm_names, pickup_names, labels, patrols

MAP_THREE_GRID, MAP_THREE_DORM_NAMES, MAP_THREE_PICKUP_NAMES, MAP_THREE_LABELS, MAP_THREE_PATROLS = build_map_three()

# 构造第四张地图，主要包括芙蓉餐厅、芙蓉湖、德旺图书馆和湖边楼群。
def build_map_four():
    dorm_names = {
        (3, 9): "5号楼",
        (7, 9): "文宣楼",
        (16, 8): "德旺图书馆",
        (24, 9): "坤銮楼",
        (30, 9): "学武楼",
    }
    pickup_names = {
        (0, 4): "芙蓉餐厅取餐点",
        (16, 17): "德旺广场取餐点",
    }
    labels = {
        (3, 4): "芙蓉餐厅",
        (3, 13): "5号楼",
        (7, 13): "文宣楼",
        (16, 8): "德旺图书馆",
        (24, 13): "坤銮楼",
        (30, 13): "学武楼",
        (15, 1): "芙蓉湖",
    }
    grid = [["R" for _ in range(MAP_COLS)] for _ in range(MAP_ROWS)]

    # 第四张地图以道路为底，再叠加湖、草地和不可通行建筑。
    def set_tile(x, y, value):
        if 0 <= x < MAP_COLS and 0 <= y < MAP_ROWS:
            grid[y][x] = value

    def hroad(y, x1, x2):
        for x in range(x1, x2 + 1):
            set_tile(x, y, "R")

    def vroad(x, y1, y2):
        for y in range(y1, y2 + 1):
            set_tile(x, y, "R")

    def rect(x1, y1, x2, y2, value):
        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1):
                set_tile(x, y, value)

    rect(1, 0, 7, 5, "S")
    rect(1, 6, 4, 6, "S")
    rect(1, 7, 6, 7, "S")
    set_tile(5, 5, "R")

    rect(8, 0, 21, 4, "L")
    rect(7, 1, 7, 4, "L")
    rect(6, 2, 6, 3, "L")
    rect(22, 1, 22, 4, "L")
    rect(23, 2, 23, 3, "L")
    rect(8, 5, 23, 5, "S")  # 一条
    set_tile(22, 0, "S")
    set_tile(23, 0, "S")
    set_tile(23, 1, "S")
    set_tile(23, 4, "S")

    rect(25, 0, 31, 7, "S")
    rect(27, 0, 31, 2, "L")
    rect(27, 3, 30, 3, "L")
    rect(27, 4, 29, 4, "L")
    rect(26, 1, 26, 3, "L")
    rect(25, 2, 25, 4, "L")
    set_tile(28, 5, "L")
    

    hroad(8, 0, 31)
    hroad(9, 0, 31)
    hroad(17, 0, 31)
    vroad(0, 0, 17)
    vroad(24, 0, 9)

    rect(1, 3, 4, 5, "B")
    rect(1, 10, 4, 15, "B")
    rect(6, 10, 9, 15, "B")
    rect(14, 9, 18, 14, "B")
    rect(22, 10, 25, 15, "B")
    rect(27, 10, 30, 15, "B")

    for pos in dorm_names:
        set_tile(*pos, "D")
    for pos in pickup_names:
        set_tile(*pos, "G")
    for pos in [(0, 0), (24, 0)]:
        set_tile(*pos, "C")

    patrols = [
        [(5, 8), (13, 8), (13, 17), (5, 17)],
        [(19, 8), (20, 8), (20, 17), (13, 17), (13, 8)],
        [(26, 8), (31, 8), (31, 17), (26, 17)],
        [(0, 8), (10, 8), (10, 17), (0, 17)],
    ]
    return ["".join(row) for row in grid], dorm_names, pickup_names, labels, patrols

MAP_FOUR_GRID, MAP_FOUR_DORM_NAMES, MAP_FOUR_PICKUP_NAMES, MAP_FOUR_LABELS, MAP_FOUR_PATROLS = build_map_four()

# 地图编号到中文名称的对应关系，用于 HUD 和切换地图时的提示。
MAP_NAMES = {0: "\u672c\u90e8\u4e3b\u6821\u533a", 1: "\u6e56\u7554\u6821\u533a", 2: "\u4e30\u5ead\u836f\u5b66\u533a", 3: "\u5fb7\u65fa\u8299\u84c9\u533a"}

# MAP_DATA 是游戏读取地图的总入口：每张图都有格子、点位、标签和丧尸巡逻路线。
MAP_DATA = {
    0: {
        "grid": MAP_ONE_GRID,
        "dorm_names": MAP_ONE_DORM_NAMES,
        "pickup_names": MAP_ONE_PICKUP_NAMES,
        "labels": {},
        "area_labels": MAP_ONE_LABELS,
        "patrols": MAP_ONE_PATROLS,
    },
    1: {
        "grid": MAP_TWO_GRID,
        "dorm_names": MAP_TWO_DORM_NAMES,
        "pickup_names": MAP_TWO_PICKUP_NAMES,
        "labels": {},
        "area_labels": MAP_TWO_LABELS,
        "patrols": MAP_TWO_PATROLS,
    },
    2: {
        "grid": MAP_THREE_GRID,
        "dorm_names": MAP_THREE_DORM_NAMES,
        "pickup_names": MAP_THREE_PICKUP_NAMES,
        "labels": {},
        "area_labels": MAP_THREE_LABELS,
        "patrols": MAP_THREE_PATROLS,
    },
    3: {
        "grid": MAP_FOUR_GRID,
        "dorm_names": MAP_FOUR_DORM_NAMES,
        "pickup_names": MAP_FOUR_PICKUP_NAMES,
        "labels": {},
        "area_labels": MAP_FOUR_LABELS,
        "patrols": MAP_FOUR_PATROLS,
    },}

# CONNECTIONS 定义地图之间的传送关系：
# 左边 key 是当前地图的传送格，value 是“目标地图编号”和“传过去后的出生格”。
CONNECTIONS = {
    0: {(0, 17): (1, (0, 1)), (13, 17): (1, (12, 1)), (24, 17): (1, (24, 1))},
    1: {
        (0, 0): (0, (0, 16)),
        (13, 0): (0, (13, 16)),
        (24, 0): (0, (24, 16)),
        (0, 17): (2, (0, 1)),
        (13, 17): (2, (13, 1)),
        (31, 4): (3, (24, 1)),
        (31, 17): (3, (0, 1)),
    },
    2: {
        (0, 0): (1, (0, 16)),
        (13, 0): (1, (13, 16)),
        (31, 0): (3, (0, 1)),
    },
    3: {
        (0, 0): (1, (30, 17)),
        (24, 0): (1, (30, 4)),
    },
}

