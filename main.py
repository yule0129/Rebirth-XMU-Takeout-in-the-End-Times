import math
import random
import time
from pathlib import Path

import pygame

pygame.init()
pygame.display.set_caption("重生之我在末日厦大送外卖")

TILE = 32
HUD = 108
FPS = 60
ORDER_LIMIT = 48
PLAYER_SPEED = 230
RAIN_SPEED = 150
ZOMBIE_SPEED = 78
ZOMBIE_CHASE_SPEED = 110
PLAYER_RADIUS = 10
PLAYER_SPRITE_SIZE = 54
PLAYER_ANIMATION_FPS = 10
PLAYER_HURT_DURATION = 0.9
PLAYER_DIE_DURATION = 1.15
ZOMBIE_RADIUS = 10
ZOMBIE_SPRITE_SIZE = 44
ZOMBIE_ANIMATION_FPS = 7
MAP_COLS = 32
MAP_ROWS = 18
START_TILE = (4, 0)

# R=粉色路线 B=黑色障碍 L=蓝色芙蓉湖/不可通行 G=黄色取餐点 D=红色送达点
# P=深绿色操场，可通行 F=浅绿色足球场，可通行 K=土黄色篮球场，可通行
WALKABLE = {"R", "G", "D", "P", "F", "K", "S", "C"}

DORM_NAMES = {
    (1, 8): "\u5357\u5149\u56ed\u533a",
    (6, 8): "\u8299\u84c9\u56ed\u533a",
    (17, 13): "\u5b66\u751f\u6d3b\u52a8\u4e2d\u5fc3",
    (24, 9): "\u7bee\u7403\u573a\u9001\u8fbe\u70b9",
}

PICKUP_NAMES = {
    (1, 0): "\u897f\u5317\u6821\u95e8\u53d6\u9910\u70b9",
    (12, 7): "\u8299\u84c9\u56ed\u65c1\u53d6\u9910\u70b9",
    (30, 0): "\u4e1c\u5317\u6821\u95e8\u53d6\u9910\u70b9",
}

CANTEENS = {}

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


def build_map():
    grid = [["R" for _ in range(MAP_COLS)] for _ in range(MAP_ROWS)]

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

    # ?????????????????????????????
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
    hroad(8, 12, 18)
    hroad(9, 12, 18)
    vroad(17, 8, 13)
    set_tile(17, 9, "K")
    set_tile(17, 10, "K")

    # ?????????????
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


def build_map_two():
    dorm_names = {
        (11, 4): "余明培游泳馆",
        (24, 10): "\u822a\u7a7a\u822a\u5929\u5b66\u9662",
    }
    pickup_names = {
        (11, 15): "\u601d\u6e90\u9910\u5385\u53d6\u9910\u70b9",
    }
    labels = {
        (6, 4): "余明培游泳馆",
        (8, 10): "\u7231\u79cb\u4f53\u80b2\u9986",
        (11, 15): "\u601d\u6e90\u9910\u5385",
        (20, 11): "\u822a\u7a7a\u822a\u5929\u5b66\u9662",
        (26, 2): "\u8299\u84c9\u6e56",
        (28, 12): "\u8299\u84c9\u6e56",
    }
    grid = [["B" for _ in range(MAP_COLS)] for _ in range(MAP_ROWS)]

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
    rect(1, 11, 5, 17, "S")
    rect(14, 5, 23, 6, "S")
    rect(14, 7, 16, 16, "S")
    rect(17, 15, 23, 16, "S")

    rect(3, 3, 9, 5, "B")
    rect(3, 7, 9, 12, "B")
    rect(6, 14, 9, 17, "B")
    rect(18, 8, 23, 13, "B")

    hroad(4, 0, 31)
    hroad(6, 0, 24)
    hroad(9, 0, 17)
    hroad(13, 0, 24)
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
        (15, 17): "德旺广场取餐点",
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

    rect(1, 0, 7, 7, "S")
    rect(8, 0, 23, 5, "L")
    rect(24, 0, 26, 5, "S")
    rect(27, 0, 31, 5, "L")
    rect(1, 6, 5, 7, "S")
    rect(6, 6, 23, 6, "S")
    rect(25, 6, 31, 7, "S")

    hroad(0, 0, 31)
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
MAP_NAMES = {0: "\u672c\u90e8\u4e3b\u6821\u533a", 1: "\u6e56\u7554\u6821\u533a", 2: "\u4e30\u5ead\u836f\u5b66\u533a", 3: "\u5fb7\u65fa\u8299\u84c9\u533a"}
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

current_map_id = 0
GAME_MAP = MAP_DATA[current_map_id]["grid"]
DORM_NAMES = MAP_DATA[current_map_id]["dorm_names"]
PICKUP_NAMES = MAP_DATA[current_map_id]["pickup_names"]
PLAYGROUND_LABELS = MAP_DATA[current_map_id]["labels"]
ROWS = len(GAME_MAP)
COLS = len(GAME_MAP[0])
WIDTH = COLS * TILE
HEIGHT = HUD + ROWS * TILE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

LABELS = {}
LABELS.update(DORM_NAMES)
LABELS.update(PICKUP_NAMES)
LABELS.update(CANTEENS)
LABELS.update(PLAYGROUND_LABELS)
PICKUPS = list(PICKUP_NAMES.keys())
DORMS = list(DORM_NAMES.keys())
ZOMBIE_PATROLS = MAP_DATA[current_map_id]["patrols"]
def font(size, bold=False):
    font_paths = [
        r"C:\Windows\Fonts\msyhbd.ttc" if bold else r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\simhei.ttf",
    ]
    for path in font_paths:
        try:
            if Path(path).exists():
                return pygame.font.Font(path, size)
        except Exception:
            pass
    for name in ["Microsoft YaHei", "SimHei", "SimSun", "Arial"]:
        try:
            f = pygame.font.SysFont(name, size, bold=bold)
            if f:
                return f
        except Exception:
            pass
    return pygame.font.Font(None, size)

FONT_TITLE = font(26, True)
FONT = font(21)
FONT_BOLD = font(21, True)
FONT_SMALL = font(16)
FONT_MINI = font(12)
FONT_BIG = font(44, True)


def remove_light_background(surface):
    sprite = surface.convert_alpha()
    width, height = sprite.get_size()
    pixels = pygame.PixelArray(sprite)
    queue = []
    visited = set()

    def is_background(px, py):
        r, g, b, a = sprite.unmap_rgb(pixels[px, py])
        if a == 0:
            return True
        return r >= 225 and g >= 225 and b >= 225 and max(r, g, b) - min(r, g, b) <= 34

    for x in range(width):
        queue.append((x, 0))
        queue.append((x, height - 1))
    for y in range(height):
        queue.append((0, y))
        queue.append((width - 1, y))

    while queue:
        px, py = queue.pop()
        if (px, py) in visited or not (0 <= px < width and 0 <= py < height):
            continue
        visited.add((px, py))
        if not is_background(px, py):
            continue

        r, g, b, _ = sprite.unmap_rgb(pixels[px, py])
        pixels[px, py] = (r, g, b, 0)
        queue.extend(((px + 1, py), (px - 1, py), (px, py + 1), (px, py - 1)))

    del pixels
    return sprite


def surface_has_visible_pixels(surface, min_pixels=12):
    count = 0
    for py in range(surface.get_height()):
        for px in range(surface.get_width()):
            if surface.get_at((px, py)).a > 10:
                count += 1
                if count >= min_pixels:
                    return True
    return False


def load_zombie_frames_from_sheet(sheet_path):
    frames = []
    sheet = pygame.image.load(str(sheet_path)).convert_alpha()
    cell_w, cell_h = 48, 48
    cols = sheet.get_width() // cell_w
    rows = sheet.get_height() // cell_h

    for row in range(rows):
        for col in range(cols):
            frame = pygame.Surface((cell_w, cell_h), pygame.SRCALPHA)
            frame.blit(sheet, (0, 0), pygame.Rect(col * cell_w, row * cell_h, cell_w, cell_h))
            if surface_has_visible_pixels(frame):
                frames.append(pygame.transform.scale(frame, (ZOMBIE_SPRITE_SIZE, ZOMBIE_SPRITE_SIZE)))
    return frames


def load_zombie_frames_from_folder(folder):
    frames = []
    if not folder.exists():
        return frames

    for image_path in sorted(folder.glob("*.png"), key=lambda item: item.name):
        try:
            raw = pygame.image.load(str(image_path)).convert_alpha()
            cleaned = remove_light_background(raw)
            frames.append(pygame.transform.smoothscale(cleaned, (ZOMBIE_SPRITE_SIZE, ZOMBIE_SPRITE_SIZE)))
        except Exception as exc:
            print(f"丧尸图片加载失败：{image_path.name}，原因：{exc}")
    return frames


def load_zombie_frames():
    character_dir = Path(__file__).resolve().parent / "character"
    sheet_path = character_dir / "zombie_sprite_sheet.png"

    if sheet_path.exists():
        try:
            frames = load_zombie_frames_from_sheet(sheet_path)
            if frames:
                return frames
        except Exception as exc:
            print(f"丧尸精灵表加载失败：{sheet_path.name}，原因：{exc}")

    return load_zombie_frames_from_folder(character_dir / "丧尸")


ZOMBIE_FRAMES = load_zombie_frames()

def remove_dark_edge_background(surface):
    sprite = surface.convert_alpha()
    width, height = sprite.get_size()
    pixels = pygame.PixelArray(sprite)
    queue = []
    visited = set()

    def is_background(px, py):
        r, g, b, a = sprite.unmap_rgb(pixels[px, py])
        if a == 0:
            return True
        return r < 54 and g < 60 and b < 76

    for x in range(width):
        queue.append((x, 0))
        queue.append((x, height - 1))
    for y in range(height):
        queue.append((0, y))
        queue.append((width - 1, y))

    while queue:
        px, py = queue.pop()
        if (px, py) in visited or not (0 <= px < width and 0 <= py < height):
            continue
        visited.add((px, py))
        if not is_background(px, py):
            continue
        r, g, b, _ = sprite.unmap_rgb(pixels[px, py])
        pixels[px, py] = (r, g, b, 0)
        queue.extend(((px + 1, py), (px - 1, py), (px, py + 1), (px, py - 1)))

    for py in range(height):
        for px in range(width):
            r, g, b, a = sprite.unmap_rgb(pixels[px, py])
            is_gray_label = abs(r - g) < 12 and abs(g - b) < 12 and 70 < r < 185
            if a > 0 and is_gray_label:
                pixels[px, py] = (r, g, b, 0)

    del pixels
    return sprite

def load_player_animations():
    sheet_path = Path(__file__).resolve().parent / "character" / "player_courier_sheet.png"
    animations = {"idle": [], "run": [], "hurt": [], "die": []}
    if not sheet_path.exists():
        return animations

    try:
        sheet = pygame.image.load(str(sheet_path)).convert_alpha()
        frame_slots = [(90, 158), (158, 224), (224, 292), (292, 360), (360, 428), (428, 496), (496, 565), (565, 636), (636, 708)]
        frame_slots.append(frame_slots[-1])
        frame_sets = {
            "idle": (54, 137),
            "run": (160, 250),
            "hurt": (270, 357),
            "die": (490, 574),
        }
        for name, (y1, y2) in frame_sets.items():
            for x1, x2 in frame_slots:
                frame = pygame.Surface((x2 - x1, y2 - y1), pygame.SRCALPHA)
                frame.blit(sheet, (0, 0), pygame.Rect(x1, y1, x2 - x1, y2 - y1))
                frame = remove_dark_edge_background(frame)
                frame = pygame.transform.scale(frame, (PLAYER_SPRITE_SIZE, PLAYER_SPRITE_SIZE))
                animations[name].append(frame)
    except Exception as exc:
        print(f"主角动画加载失败：{exc}")
        return {"idle": [], "run": [], "hurt": [], "die": []}
    return animations


PLAYER_ANIMATIONS = load_player_animations()

COLORS = {
    "R": (176, 176, 176),
    "B": (9, 9, 9),
    "L": (142, 212, 224),
    "G": (255, 234, 34),
    "D": (244, 32, 42),
    "C": (145, 61, 174),
    "P": (34, 179, 78),
    "F": (232, 250, 218),
    "K": (166, 101, 66),
    "S": (34, 179, 78),
    "H": (84, 111, 145),
}

WEATHER_TEXT = {
    "normal": "??",
    "rain": "???????",
    "typhoon": "???????",
    "fog": "???????",
}
pressed_keys = set()
score = 0
rescued = 0
failed = 0
carrying_order = False
target_dorm = None
target_dorm_map = None
ALL_PICKUPS = [(map_id, pos) for map_id, data in MAP_DATA.items() for pos in data["pickup_names"]]
ALL_DORMS = [(map_id, pos) for map_id, data in MAP_DATA.items() for pos in data["dorm_names"]]
active_pickup_map, active_pickup = random.choice(ALL_PICKUPS)
order_start = 0.0
weather = "normal"
weather_until = 0.0
message = "\u6a59\u8272\u5149\u5708\u662f\u672c\u6b21\u5916\u5356\u5237\u65b0\u70b9\uff0c\u9760\u8fd1\u540e\u6309 E \u6216\u7a7a\u683c\u53d6\u9910\u3002"
message_until = time.time() + 6
game_over = False
game_started_at = time.time()
last_hit_time = -10.0
transition = {"active": False, "started": 0.0, "target_map": None, "spawn": None, "switched": False}


def map_name(map_id):
    return MAP_NAMES.get(map_id, f"??{map_id + 1}")


def pickup_name(map_id, pos):
    return MAP_DATA[map_id]["pickup_names"][pos]


def dorm_name(map_id, pos):
    return MAP_DATA[map_id]["dorm_names"][pos]


def set_current_map(map_id):
    global current_map_id, GAME_MAP, DORM_NAMES, PICKUP_NAMES, PLAYGROUND_LABELS, LABELS, PICKUPS, DORMS, ZOMBIE_PATROLS
    current_map_id = map_id
    data = MAP_DATA[current_map_id]
    GAME_MAP = data["grid"]
    DORM_NAMES = data["dorm_names"]
    PICKUP_NAMES = data["pickup_names"]
    PLAYGROUND_LABELS = data["labels"]
    PICKUPS = list(PICKUP_NAMES.keys())
    DORMS = list(DORM_NAMES.keys())
    ZOMBIE_PATROLS = data["patrols"]
    LABELS = {}
    LABELS.update(DORM_NAMES)
    LABELS.update(PICKUP_NAMES)
    LABELS.update(CANTEENS)
    LABELS.update(PLAYGROUND_LABELS)


def tile_center(pos):
    x, y = pos
    return x * TILE + TILE / 2, HUD + y * TILE + TILE / 2


player = {"x": tile_center(START_TILE)[0], "y": tile_center(START_TILE)[1], "hp": 3, "state": "idle", "state_started": time.time(), "moving": False, "flip": False, "locked_until": 0.0, "invulnerable_until": 0.0}
zombies = []


def rebuild_zombies():
    zombies.clear()
    for patrol in ZOMBIE_PATROLS:
        x, y = tile_center(patrol[0])
        zombies.append({"x": x, "y": y, "patrol": patrol, "target": 1, "chasing": False, "flip": False, "frame_offset": random.random() * 10})


rebuild_zombies()


def switch_map(map_id, spawn_tile):
    set_current_map(map_id)
    rebuild_zombies()
    player["x"], player["y"] = tile_center(spawn_tile)
    player["moving"] = False
    player["state"] = "idle"
    player["state_started"] = time.time()
    pressed_keys.clear()


def nearest_connection_to(target_map_id):
    options = [(tile, data) for tile, data in CONNECTIONS.get(current_map_id, {}).items() if data[0] == target_map_id]
    if not options:
        return None
    px, py = player["x"], player["y"]
    return min(options, key=lambda item: dist((px, py), tile_center(item[0])))[0]


def target_tile_for_guide():
    if carrying_order:
        if target_dorm_map == current_map_id:
            return target_dorm, (255, 222, 68)
        return nearest_connection_to(target_dorm_map), (116, 214, 255)
    if active_pickup_map == current_map_id:
        return active_pickup, (255, 158, 64)
    return nearest_connection_to(active_pickup_map), (116, 214, 255)


def start_transition(target_map, spawn_tile):
    if transition["active"]:
        return
    transition.update({"active": True, "started": time.time(), "target_map": target_map, "spawn": spawn_tile, "switched": False})
    set_message(f"\u6b63\u5728\u524d\u5f80 {map_name(target_map)}...", 2)


def update_transition():
    if not transition["active"]:
        return
    elapsed = time.time() - transition["started"]
    if elapsed >= 0.22 and not transition["switched"]:
        switch_map(transition["target_map"], transition["spawn"])
        transition["switched"] = True
    if elapsed >= 0.58:
        transition["active"] = False
        set_message(f"??? {map_name(current_map_id)}", 2)


def check_map_connection():
    if transition["active"] or player["state"] in {"hurt", "die"}:
        return
    gx, gy = grid_from_pixel(player["x"], player["y"])
    target = CONNECTIONS.get(current_map_id, {}).get((gx, gy))
    if target:
        start_transition(target[0], target[1])


def grid_from_pixel(x, y):
    return int(x // TILE), int((y - HUD) // TILE)


def in_bounds(gx, gy):
    return 0 <= gx < COLS and 0 <= gy < ROWS


def tile_at(gx, gy):
    if not in_bounds(gx, gy):
        return "B"
    return GAME_MAP[gy][gx]


def pixel_walkable(x, y):
    gx, gy = grid_from_pixel(x, y)
    return in_bounds(gx, gy) and tile_at(gx, gy) in WALKABLE


def can_stand(x, y, radius):
    return all(
        pixel_walkable(px, py)
        for px, py in [
            (x - radius, y - radius),
            (x + radius, y - radius),
            (x - radius, y + radius),
            (x + radius, y + radius),
            (x, y),
        ]
    )


def move_with_collision(entity, dx, dy, radius):
    if can_stand(entity["x"] + dx, entity["y"], radius):
        entity["x"] += dx
    if can_stand(entity["x"], entity["y"] + dy, radius):
        entity["y"] += dy


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def distance_to_tile(pos):
    return dist((player["x"], player["y"]), tile_center(pos))


def set_message(text, seconds=3):
    global message, message_until
    message = text
    message_until = time.time() + seconds


def refresh_pickup(except_key=None):
    global active_pickup_map, active_pickup
    choices = [item for item in ALL_PICKUPS if item != except_key]
    active_pickup_map, active_pickup = random.choice(choices or ALL_PICKUPS)


def start_order():
    global carrying_order, target_dorm, target_dorm_map, order_start
    other_map_dorms = [item for item in ALL_DORMS if item[0] != active_pickup_map]
    same_map_dorms = [item for item in ALL_DORMS if item[0] == active_pickup_map]
    if other_map_dorms and random.random() < 0.45:
        target_dorm_map, target_dorm = random.choice(other_map_dorms)
    else:
        target_dorm_map, target_dorm = random.choice(same_map_dorms or ALL_DORMS)
    carrying_order = True
    order_start = time.time()
    set_message(f"\u65b0\u8ba2\u5355\uff1a\u4ece {map_name(active_pickup_map)}-{pickup_name(active_pickup_map, active_pickup)} \u9001\u5f80 {map_name(target_dorm_map)}-{dorm_name(target_dorm_map, target_dorm)}\u3002", 5)


def finish_order():
    global carrying_order, target_dorm, target_dorm_map, order_start, score, rescued
    score += 10
    rescued += 1
    name = dorm_name(target_dorm_map, target_dorm)
    old_pickup = (active_pickup_map, active_pickup)
    carrying_order = False
    target_dorm = None
    target_dorm_map = None
    order_start = 0
    refresh_pickup(old_pickup)
    set_message(f"{name} \u9001\u8fbe\u6210\u529f\uff0c+10 \u5206\uff01\u65b0\u7684\u53d6\u9910\u70b9\u5df2\u5237\u65b0\u3002", 5)


def fail_order(text):
    global carrying_order, target_dorm, target_dorm_map, order_start, score, failed
    old_pickup = (active_pickup_map, active_pickup)
    carrying_order = False
    target_dorm = None
    target_dorm_map = None
    order_start = 0
    failed += 1
    score = max(0, score - 5)
    refresh_pickup(old_pickup)
    set_message(text + " \u65b0\u7684\u53d6\u9910\u70b9\u5df2\u5237\u65b0\u3002", 4)


def interact():
    if game_over or transition["active"]:
        return
    if not carrying_order:
        if active_pickup_map != current_map_id:
            set_message(f"\u672c\u6b21\u5916\u5356\u5728 {map_name(active_pickup_map)}\uff0c\u5148\u8d70\u5230\u84dd\u8272\u8fde\u63a5\u53e3\u5207\u6362\u5730\u56fe\u3002", 3)
        elif distance_to_tile(active_pickup) < TILE * 1.25:
            start_order()
        else:
            set_message("\u53ea\u6709\u6a59\u8272\u5149\u5708\u4f4d\u7f6e\u80fd\u53d6\u5916\u5356\uff0c\u9760\u8fd1\u540e\u6309 E \u6216\u7a7a\u683c\u3002", 3)
    else:
        if target_dorm_map != current_map_id:
            set_message(f"\u9001\u8fbe\u70b9\u5728 {map_name(target_dorm_map)}\uff0c\u5148\u8d70\u5230\u84dd\u8272\u8fde\u63a5\u53e3\u5207\u6362\u5730\u56fe\u3002", 3)
        elif distance_to_tile(target_dorm) < TILE * 1.25:
            finish_order()
        else:
            set_message("\u9ec4\u8272\u5149\u5708\u624d\u662f\u672c\u5355\u9001\u8fbe\u70b9\uff0c\u8fd8\u6ca1\u5230\u3002", 3)


def key_down(code):
    keys = pygame.key.get_pressed()
    return code in pressed_keys or keys[code]


def update_player_state():
    global game_over
    now = time.time()
    if player["state"] == "hurt" and now >= player["locked_until"]:
        switch_map(0, START_TILE)
        player["state"] = "idle"
        player["state_started"] = now
        player["moving"] = False
        player["invulnerable_until"] = now + 1.2
        set_message("你被传送回出发点，短暂无敌，继续送！", 3)
    elif player["state"] == "die" and now >= player["locked_until"]:
        game_over = True


def update_player(dt):
    if player["state"] in {"hurt", "die"}:
        player["moving"] = False
        return

    dx = 0
    dy = 0
    if key_down(pygame.K_a) or key_down(pygame.K_LEFT):
        dx -= 1
    if key_down(pygame.K_d) or key_down(pygame.K_RIGHT):
        dx += 1
    if key_down(pygame.K_w) or key_down(pygame.K_UP):
        dy -= 1
    if key_down(pygame.K_s) or key_down(pygame.K_DOWN):
        dy += 1

    if dx == 0 and dy == 0:
        player["moving"] = False
        return

    player["moving"] = True
    if dx != 0:
        player["flip"] = dx > 0

    length = math.hypot(dx, dy)
    dx /= length
    dy /= length
    speed = RAIN_SPEED if weather == "rain" else PLAYER_SPEED
    gx, gy = grid_from_pixel(player["x"], player["y"])
    if tile_at(gx, gy) == "S":
        speed *= 0.58
    if weather == "typhoon" and random.random() < 0.015:
        dx += random.choice([-0.55, 0.55])
        dy += random.choice([-0.55, 0.55])
        length = math.hypot(dx, dy)
        dx /= length
        dy /= length
    move_with_collision(player, dx * speed * dt, dy * speed * dt, PLAYER_RADIUS)

def update_zombies(dt):
    for zombie in zombies:
        player_distance = dist((zombie["x"], zombie["y"]), (player["x"], player["y"]))
        zombie["chasing"] = player_distance < TILE * 4.6
        if zombie["chasing"]:
            tx, ty = player["x"], player["y"]
            speed = ZOMBIE_CHASE_SPEED
        else:
            target_tile = zombie["patrol"][zombie["target"]]
            tx, ty = tile_center(target_tile)
            speed = ZOMBIE_SPEED
            if dist((zombie["x"], zombie["y"]), (tx, ty)) < 9:
                zombie["target"] = (zombie["target"] + 1) % len(zombie["patrol"])
                tx, ty = tile_center(zombie["patrol"][zombie["target"]])

        vx = tx - zombie["x"]
        vy = ty - zombie["y"]
        length = math.hypot(vx, vy)
        if length == 0:
            continue
        vx /= length
        vy /= length
        if abs(vx) > 0.08:
            zombie["flip"] = vx < 0
        move_with_collision(zombie, vx * speed * dt, vy * speed * dt, ZOMBIE_RADIUS)


def update_weather():
    global weather, weather_until
    now = time.time()
    if weather != "normal" and now > weather_until:
        weather = "normal"
        set_message("天气恢复正常。", 3)
    elif weather == "normal" and random.random() < 0.0014:
        weather = random.choice(["rain", "typhoon", "fog"])
        weather_until = now + 14
        set_message(f"极端天气：{WEATHER_TEXT[weather]}", 4)


def player_caught(now, zombie):
    global last_hit_time, carrying_order, target_dorm, target_dorm_map, order_start
    last_hit_time = now
    player["hp"] -= 1
    pressed_keys.clear()

    if carrying_order:
        carrying_order = False
        target_dorm = None
        target_dorm_map = None
        order_start = 0
        refresh_pickup()

    zombie["x"], zombie["y"] = tile_center(zombie["patrol"][0])
    zombie["target"] = 1
    zombie["chasing"] = False

    if player["hp"] > 0:
        player["state"] = "hurt"
        player["state_started"] = now
        player["locked_until"] = now + PLAYER_HURT_DURATION
        player["moving"] = False
        set_message("被丧尸抓到了！播放受伤动画后回到出发点。", 3)
    else:
        player["state"] = "die"
        player["state_started"] = now
        player["locked_until"] = now + PLAYER_DIE_DURATION
        player["moving"] = False
        set_message("最后一条命没了……", 3)


def check_state():
    now = time.time()
    if carrying_order and now - order_start > ORDER_LIMIT:
        fail_order("订单超时，同学饿晕了，扣 5 分。")

    if player["state"] in {"hurt", "die"} or now < player["invulnerable_until"]:
        return

    for zombie in zombies:
        if dist((zombie["x"], zombie["y"]), (player["x"], player["y"])) < 28:
            player_caught(now, zombie)
            return

def text(s, x, y, color=(255, 255, 255), f=None):
    img = (f or FONT).render(s, True, color)
    screen.blit(img, (x, y))
    return img


def center_text(s, cx, cy, color=(255, 255, 255), f=None):
    img = (f or FONT).render(s, True, color)
    screen.blit(img, img.get_rect(center=(cx, cy)))
    return img


def draw_area_labels():
    labels = MAP_DATA[current_map_id].get("area_labels", {})
    for (gx, gy), label in labels.items():
        cx = gx * TILE + TILE // 2
        cy = HUD + gy * TILE + TILE // 2
        img = FONT_BOLD.render(label, True, (238, 52, 57))
        pad_x, pad_y = 10, 5
        rect = img.get_rect(center=(cx, cy))
        rect.x = max(6, min(WIDTH - rect.w - 6, rect.x))
        rect.y = max(HUD + 6, min(HEIGHT - rect.h - 6, rect.y))
        bg = rect.inflate(pad_x * 2, pad_y * 2)
        shade = pygame.Surface((bg.w, bg.h), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 112))
        screen.blit(shade, bg)
        pygame.draw.rect(screen, (255, 255, 255, 42), bg, 1)
        screen.blit(img, rect)



def pulse(speed=4):
    return (math.sin(time.time() * speed) + 1) / 2


def tile_seed(x, y):
    return (x * 37 + y * 53 + 17) % 100


def draw_road_tile(r, x, y):
    pygame.draw.rect(screen, (172, 171, 166), r)
    pygame.draw.rect(screen, (135, 136, 132), r, 1)
    if tile_seed(x, y) % 3 == 0:
        pygame.draw.rect(screen, (189, 188, 181), (r.x + 5, r.y + 6, 9, 3))
    if tile_seed(x, y) % 4 == 0:
        pygame.draw.rect(screen, (148, 149, 144), (r.x + 18, r.y + 22, 8, 2))


def draw_track_playground_tile(r, x, y):
    rel_x = x - 18
    rel_y = y - 1
    pygame.draw.rect(screen, (201, 49, 42), r)
    pygame.draw.rect(screen, (165, 32, 34), r, 1)

    if 2 <= rel_x <= 10 and 1 <= rel_y <= 5:
        stripe = (54, 148, 67) if (rel_y + rel_x // 2) % 2 == 0 else (83, 178, 78)
        pygame.draw.rect(screen, stripe, r.inflate(-2, -2))
        if rel_x in {2, 10} or rel_y in {1, 5}:
            pygame.draw.line(screen, (235, 245, 226), (r.x + 3, r.y + 3), (r.right - 3, r.y + 3), 1)
    elif rel_x == 0 and 1 <= rel_y <= 5:
        pygame.draw.rect(screen, (222, 239, 247), r)
        pygame.draw.rect(screen, (83, 164, 231), (r.x + 3, r.y + 4, r.w - 6, 5))
        pygame.draw.rect(screen, (48, 122, 199), (r.x + 3, r.y + 13, r.w - 6, 5))
        pygame.draw.line(screen, (93, 103, 112), (r.x + 3, r.bottom - 5), (r.right - 3, r.bottom - 5), 2)
    else:
        for offset in (6, 14, 22):
            pygame.draw.line(screen, (246, 220, 197), (r.x + 2, r.y + offset), (r.right - 2, r.y + offset), 1)
        if rel_y in {0, 6} or rel_x in {1, 11, 12}:
            pygame.draw.line(screen, (255, 245, 235), (r.x + 5, r.centery), (r.right - 5, r.centery), 1)

    if (rel_x, rel_y) in {(3, 2), (3, 3), (3, 4)}:
        pygame.draw.line(screen, (223, 225, 218), (r.centerx, r.y + 2), (r.centerx, r.bottom - 2), 2)
        if rel_y == 2:
            pygame.draw.polygon(screen, (222, 43, 39), [(r.centerx + 2, r.y + 4), (r.centerx + 15, r.y + 8), (r.centerx + 2, r.y + 13)])
    if rel_x == 9 and rel_y == 4:
        pygame.draw.rect(screen, (232, 238, 226), (r.x + 5, r.y + 9, 21, 13), 2)
        pygame.draw.line(screen, (232, 238, 226), (r.x + 5, r.y + 9), (r.x + 11, r.y + 15), 1)
        pygame.draw.line(screen, (232, 238, 226), (r.x + 26, r.y + 9), (r.x + 20, r.y + 15), 1)


def draw_soccer_field_tile(r, x, y):
    rel_x = x - 14
    rel_y = y - 1
    stripe = (211, 244, 196) if rel_x % 2 == 0 else (226, 250, 211)
    pygame.draw.rect(screen, stripe, r)
    pygame.draw.line(screen, (190, 232, 176), (r.x + 4, r.y + 7), (r.right - 4, r.y + 7), 1)
    pygame.draw.line(screen, (190, 232, 176), (r.x + 4, r.y + 22), (r.right - 4, r.y + 22), 1)
    if rel_y in {0, 4}:
        pygame.draw.line(screen, (244, 255, 234), (r.x + 2, r.centery), (r.right - 2, r.centery), 2)
    if rel_x in {0, 2}:
        pygame.draw.line(screen, (244, 255, 234), (r.centerx, r.y + 2), (r.centerx, r.bottom - 2), 2)
    if rel_x == 1 and rel_y == 2:
        pygame.draw.circle(screen, (244, 255, 234), r.center, 10, 2)
        pygame.draw.line(screen, (244, 255, 234), (r.x + 2, r.centery), (r.right - 2, r.centery), 1)
    if rel_x == 0 and rel_y in {1, 2, 3}:
        pygame.draw.rect(screen, (244, 255, 234), (r.x + 2, r.y + 8, 12, 16), 2)
    if rel_x == 2 and rel_y in {1, 2, 3}:
        pygame.draw.rect(screen, (244, 255, 234), (r.right - 14, r.y + 8, 12, 16), 2)


def draw_basketball_court_tile(r, x, y):
    left_court = x <= 23
    base_x = 18 if left_court else 25
    rel_x = x - base_x
    rel_y = y - 9
    pygame.draw.rect(screen, (181, 116, 66), r)
    pygame.draw.rect(screen, (165, 96, 54), r, 1)
    for yy in (8, 20):
        pygame.draw.line(screen, (218, 159, 96), (r.x + 4, r.y + yy), (r.right - 4, r.y + yy), 1)
    for xx in (9, 22):
        pygame.draw.line(screen, (139, 80, 45), (r.x + xx, r.y + 3), (r.x + xx, r.bottom - 3), 1)
    line = (245, 218, 176)
    if rel_y in {0, 3}:
        pygame.draw.line(screen, line, (r.x + 3, r.centery), (r.right - 3, r.centery), 2)
    if rel_x in {0, 5}:
        pygame.draw.line(screen, line, (r.centerx, r.y + 3), (r.centerx, r.bottom - 3), 2)
    if rel_x == 2 and rel_y == 1:
        pygame.draw.circle(screen, line, (r.right - 1, r.bottom - 1), 20, 2)
    if rel_x == 3 and rel_y == 2:
        pygame.draw.circle(screen, line, (r.x + 1, r.y + 1), 20, 2)
    if rel_x in {0, 5} and rel_y in {1, 2}:
        hoop_x = r.x + 7 if rel_x == 0 else r.right - 7
        pygame.draw.rect(screen, (81, 55, 42), (hoop_x - 3, r.centery - 8, 6, 16))
        pygame.draw.circle(screen, (232, 66, 42), (hoop_x, r.centery), 5, 2)
        pygame.draw.line(screen, (235, 235, 228), (hoop_x - 7, r.centery - 6), (hoop_x + 7, r.centery - 6), 2)


def draw_field_tile(r, x, y, tile):
    if current_map_id == 0 and tile == "P" and 18 <= x <= 30 and 1 <= y <= 7:
        draw_track_playground_tile(r, x, y)
        return
    if current_map_id == 0 and tile == "F" and 14 <= x <= 16 and 1 <= y <= 5:
        draw_soccer_field_tile(r, x, y)
        return
    if current_map_id == 0 and tile == "K" and ((17 <= x <= 23 and 9 <= y <= 12) or (25 <= x <= 30 and 9 <= y <= 12)):
        draw_basketball_court_tile(r, x, y)
        return
    base = COLORS.get(tile, (80, 180, 90))
    pygame.draw.rect(screen, base, r)
    if tile == "S":
        for i in range(2):
            ox = (tile_seed(x + i, y) * 7) % 22 + 4
            oy = (tile_seed(x, y + i) * 5) % 20 + 6
            pygame.draw.line(screen, (22, 137, 63), (r.x + ox, r.y + oy), (r.x + ox + 3, r.y + oy - 5), 2)
            pygame.draw.line(screen, (69, 205, 102), (r.x + ox + 2, r.y + oy), (r.x + ox + 5, r.y + oy - 4), 1)
    elif tile == "P":
        pygame.draw.rect(screen, (50, 156, 73), r)
        pygame.draw.line(screen, (212, 236, 202), (r.x + 5, r.centery), (r.right - 5, r.centery), 1)

def is_aerospace_building_tile(x, y):
    return current_map_id == 1 and 16 <= x <= 22 and 8 <= y <= 14 and tile_at(x, y) == "B"


def draw_jingfeng_canteen_overlay():
    if current_map_id != 0:
        return
    base = pygame.Rect(14 * TILE, HUD + 9 * TILE, 3 * TILE, 2 * TILE)
    shadow = pygame.Surface((base.w + 26, base.h + 38), pygame.SRCALPHA)
    pygame.draw.polygon(shadow, (0, 0, 0, 70), [(12, 22), (base.w + 22, 10), (base.w + 18, base.h + 34), (4, base.h + 36)])
    screen.blit(shadow, (base.x - 12, base.y - 12))

    body = pygame.Rect(base.x - 8, base.y + 8, base.w + 26, base.h + 38)
    pygame.draw.rect(screen, (181, 89, 57), body)
    pygame.draw.rect(screen, (113, 49, 38), body, 2)
    for yy in range(body.y + 8, body.bottom - 4, 9):
        pygame.draw.line(screen, (218, 125, 84), (body.x + 5, yy), (body.right - 6, yy), 1)

    glass = pygame.Rect(body.x + 44, body.y + 12, body.w - 58, body.h - 20)
    pygame.draw.rect(screen, (192, 213, 205), glass)
    for gx in range(glass.x + 8, glass.right - 5, 15):
        pygame.draw.line(screen, (86, 112, 123), (gx, glass.y + 2), (gx, glass.bottom - 2), 1)
    for gy in range(glass.y + 10, glass.bottom - 2, 13):
        pygame.draw.line(screen, (239, 246, 234), (glass.x + 2, gy), (glass.right - 2, gy), 2)
    pygame.draw.rect(screen, (68, 92, 103), glass, 2)

    roof = [(body.x - 6, body.y - 8), (body.right + 8, body.y - 8), (body.right, body.y + 8), (body.x - 14, body.y + 8)]
    pygame.draw.polygon(screen, (81, 78, 70), [(x, y + 6) for x, y in roof])
    pygame.draw.polygon(screen, (226, 217, 184), roof)
    pygame.draw.line(screen, (120, 108, 86), roof[0], roof[1], 2)

    door = pygame.Rect(body.x + 17, body.bottom - 28, 21, 28)
    pygame.draw.rect(screen, (32, 41, 49), door)
    pygame.draw.line(screen, (109, 150, 174), (door.centerx, door.y + 3), (door.centerx, door.bottom - 3), 1)
    pygame.draw.rect(screen, (228, 218, 179), (body.x + 8, body.y + 15, 24, 7))


def draw_student_activity_center_overlay():
    if current_map_id != 0:
        return
    base = pygame.Rect(14 * TILE, HUD + 14 * TILE, 10 * TILE, 3 * TILE)
    shadow = pygame.Surface((base.w + 32, base.h + 28), pygame.SRCALPHA)
    pygame.draw.polygon(shadow, (0, 0, 0, 72), [(18, 18), (base.w + 30, 8), (base.w + 22, base.h + 22), (4, base.h + 26)])
    screen.blit(shadow, (base.x - 14, base.y - 12))

    left = pygame.Rect(base.x - 4, base.y + 18, 132, 72)
    tower = pygame.Rect(base.x + 128, base.y - 8, 54, 104)
    right = pygame.Rect(base.x + 180, base.y + 6, 142, 88)
    bridge = pygame.Rect(base.x + 38, base.y + 28, 128, 30)

    for rect in (left, right):
        pygame.draw.rect(screen, (190, 199, 196), rect)
        pygame.draw.rect(screen, (116, 128, 130), rect, 2)
        pygame.draw.rect(screen, (70, 112, 143), (rect.x + 8, rect.y + 15, rect.w - 16, 22))
        for gx in range(rect.x + 17, rect.right - 12, 22):
            pygame.draw.line(screen, (38, 70, 96), (gx, rect.y + 15), (gx, rect.y + 37), 1)
        pygame.draw.line(screen, (218, 235, 238), (rect.x + 10, rect.y + 19), (rect.right - 12, rect.y + 19), 2)
        pygame.draw.rect(screen, (132, 145, 145), (rect.x, rect.bottom - 12, rect.w, 12))

    pygame.draw.rect(screen, (172, 178, 174), bridge)
    pygame.draw.rect(screen, (70, 112, 143), (bridge.x + 8, bridge.y + 6, bridge.w - 16, 15))
    pygame.draw.rect(screen, (82, 93, 96), bridge, 2)

    pygame.draw.rect(screen, (212, 216, 205), tower)
    pygame.draw.rect(screen, (136, 145, 143), tower, 2)
    pygame.draw.polygon(screen, (232, 235, 225), [(tower.x - 6, tower.y + 20), (tower.centerx, tower.y - 16), (tower.right + 8, tower.y + 20)])
    pygame.draw.line(screen, (150, 148, 136), (tower.x - 6, tower.y + 20), (tower.centerx, tower.y - 16), 2)
    pygame.draw.line(screen, (150, 148, 136), (tower.centerx, tower.y - 16), (tower.right + 8, tower.y + 20), 2)
    pygame.draw.rect(screen, (73, 112, 143), (tower.x + 13, tower.y + 38, 28, 48))
    for gy in range(tower.y + 48, tower.y + 84, 12):
        pygame.draw.line(screen, (203, 231, 237), (tower.x + 15, gy), (tower.x + 39, gy), 1)
    pygame.draw.rect(screen, (57, 78, 92), (tower.x + 13, tower.y + 38, 28, 48), 2)

    for tx in (base.x + 20, base.x + 304):
        pygame.draw.rect(screen, (96, 72, 48), (tx, base.bottom - 20, 5, 20))
        for ox, oy in [(-10, -7), (-4, -13), (6, -12), (12, -5)]:
            pygame.draw.circle(screen, (57, 143, 64), (tx + ox, base.bottom - 22 + oy), 9)
            pygame.draw.circle(screen, (116, 194, 76), (tx + ox + 2, base.bottom - 25 + oy), 5)


def draw_aerospace_building_overlay():
    if current_map_id != 1:
        return

    base = pygame.Rect(16 * TILE, HUD + 8 * TILE, 7 * TILE, 7 * TILE)
    shadow = pygame.Surface((base.w + 44, base.h + 42), pygame.SRCALPHA)
    pygame.draw.polygon(shadow, (0, 0, 0, 82), [(28, 26), (base.w + 38, 10), (base.w + 30, base.h + 28), (10, base.h + 40)])
    screen.blit(shadow, (base.x - 20, base.y - 22))

    left = pygame.Rect(base.x - 22, base.y + 38, 86, 140)
    mid = pygame.Rect(base.x + 58, base.y + 12, 108, 168)
    right = pygame.Rect(base.x + 160, base.y + 38, 86, 140)

    def brick_panel(rect):
        pygame.draw.rect(screen, (169, 73, 48), rect)
        pygame.draw.rect(screen, (112, 45, 36), rect, 2)
        for yy in range(rect.y + 9, rect.bottom - 3, 10):
            pygame.draw.line(screen, (215, 117, 79), (rect.x + 5, yy), (rect.right - 5, yy), 1)
        for xx in range(rect.x + 14, rect.right - 8, 28):
            pygame.draw.rect(screen, (239, 225, 186), (xx - 3, rect.y + 2, 6, rect.h - 5))

    def window_grid(rect, cols, rows):
        cell_w = rect.w // cols
        cell_h = rect.h // rows
        for row in range(rows):
            for col in range(cols):
                wx = rect.x + col * cell_w + 3
                wy = rect.y + row * cell_h + 4
                ww = max(7, cell_w - 6)
                wh = max(7, cell_h - 8)
                pygame.draw.rect(screen, (35, 78, 132), (wx, wy, ww, wh))
                pygame.draw.line(screen, (116, 177, 235), (wx + 2, wy + 2), (wx + ww - 3, wy + 2), 1)
                pygame.draw.rect(screen, (17, 45, 82), (wx, wy, ww, wh), 1)

    # Side wings with cream cornices and blue window grids.
    for wing in (left, right):
        brick_panel(wing)
        pygame.draw.rect(screen, (238, 224, 188), (wing.x - 4, wing.y - 12, wing.w + 8, 13))
        pygame.draw.rect(screen, (189, 172, 138), (wing.x - 4, wing.y, wing.w + 8, 5))
        pygame.draw.rect(screen, (238, 224, 188), (wing.x - 2, wing.bottom - 18, wing.w + 4, 12))
        window_grid(pygame.Rect(wing.x + 10, wing.y + 18, wing.w - 20, wing.h - 44), 3, 4)
        gable = [(wing.centerx - 28, wing.y - 12), (wing.centerx, wing.y - 35), (wing.centerx + 28, wing.y - 12)]
        pygame.draw.polygon(screen, (185, 166, 128), [(x, y + 4) for x, y in gable])
        pygame.draw.polygon(screen, (246, 235, 204), gable)
        pygame.draw.line(screen, (136, 116, 88), gable[0], gable[1], 2)
        pygame.draw.line(screen, (136, 116, 88), gable[1], gable[2], 2)

    # Central glass hall and taller pediment.
    pygame.draw.rect(screen, (226, 213, 180), (mid.x - 10, mid.y + 18, mid.w + 20, mid.h - 8))
    pygame.draw.rect(screen, (56, 101, 156), (mid.x + 7, mid.y + 36, mid.w - 14, mid.h - 48))
    for xx in range(mid.x + 16, mid.right - 12, 15):
        pygame.draw.line(screen, (22, 50, 90), (xx, mid.y + 38), (xx, mid.bottom - 14), 2)
    for yy in range(mid.y + 48, mid.bottom - 18, 16):
        pygame.draw.line(screen, (129, 184, 235), (mid.x + 9, yy), (mid.right - 9, yy), 2)
    pygame.draw.rect(screen, (22, 49, 89), (mid.x + 7, mid.y + 36, mid.w - 14, mid.h - 48), 2)

    roof = [(mid.x - 24, mid.y + 32), (mid.centerx, mid.y - 30), (mid.right + 24, mid.y + 32)]
    pygame.draw.polygon(screen, (169, 150, 113), [(x, y + 8) for x, y in roof])
    pygame.draw.polygon(screen, (248, 237, 205), roof)
    for step in range(5):
        y = mid.y - 20 + step * 10
        pygame.draw.line(screen, (198, 181, 145), (mid.x + 18 - step * 4, y), (mid.right - 18 + step * 4, y), 2)
    pygame.draw.line(screen, (132, 111, 83), roof[0], roof[1], 3)
    pygame.draw.line(screen, (132, 111, 83), roof[1], roof[2], 3)
    pygame.draw.rect(screen, (246, 235, 204), (mid.x - 18, mid.y + 22, mid.w + 36, 18))
    pygame.draw.rect(screen, (184, 164, 126), (mid.x - 18, mid.y + 38, mid.w + 36, 5))

    # Entrance arch, inspired by the reference facade.
    arch = pygame.Rect(mid.centerx - 31, mid.bottom - 62, 62, 62)
    pygame.draw.arc(screen, (244, 232, 199), arch, math.pi, 2 * math.pi, 8)
    pygame.draw.rect(screen, (244, 232, 199), (arch.x - 1, arch.centery, arch.w + 2, 42))
    inner = pygame.Rect(mid.centerx - 22, mid.bottom - 48, 44, 48)
    pygame.draw.arc(screen, (44, 78, 124), inner, math.pi, 2 * math.pi, 4)
    pygame.draw.rect(screen, (30, 54, 92), (inner.x, inner.centery, inner.w, 28))
    pygame.draw.line(screen, (120, 179, 233), (inner.centerx, inner.y + 8), (inner.centerx, inner.bottom - 5), 2)



def draw_furong_canteen_overlay():
    if current_map_id != 3:
        return

    base = pygame.Rect(1 * TILE, HUD + 3 * TILE, 4 * TILE, 3 * TILE)
    shadow = pygame.Surface((base.w + 34, base.h + 28), pygame.SRCALPHA)
    pygame.draw.polygon(shadow, (0, 0, 0, 58), [(15, 18), (base.w + 30, 9), (base.w + 24, base.h + 22), (5, base.h + 25)])
    screen.blit(shadow, (base.x - 12, base.y - 10))

    wall = (239, 243, 235)
    side = (205, 215, 211)
    glass = (72, 132, 168)
    glass_dark = (39, 86, 119)
    glass_hi = (162, 211, 226)
    roof = (202, 83, 47)
    roof_dark = (124, 54, 42)
    trim = (255, 250, 231)

    lower = pygame.Rect(base.x + 5, base.y + 45, base.w + 12, 48)
    upper = pygame.Rect(base.x + 24, base.y + 18, base.w - 4, 44)

    def roof_slab(rect, large=False):
        over = 18 if large else 12
        pts = [(rect.x - over, rect.y + 12), (rect.x + 14, rect.y + 2), (rect.right - 10, rect.y + 2), (rect.right + over, rect.y + 12), (rect.right + over - 4, rect.y + 19), (rect.x - over + 4, rect.y + 19)]
        pygame.draw.polygon(screen, roof_dark, [(x, y + 4) for x, y in pts])
        pygame.draw.polygon(screen, trim, pts)
        pygame.draw.polygon(screen, roof, [(rect.x + 4, rect.y + 9), (rect.right - 4, rect.y + 9), (rect.right - 12, rect.y + 16), (rect.x + 13, rect.y + 16)])
        pygame.draw.line(screen, (255, 252, 238), pts[0], pts[3], 2)

    pygame.draw.rect(screen, side, lower.move(0, 4))
    pygame.draw.rect(screen, wall, lower)
    pygame.draw.rect(screen, (226, 232, 226), (lower.x, lower.bottom - 10, lower.w, 10))
    for px in range(lower.x + 13, lower.right - 8, 23):
        pygame.draw.rect(screen, trim, (px - 3, lower.y + 8, 6, lower.h - 10))
        pygame.draw.line(screen, (174, 186, 184), (px + 3, lower.y + 8), (px + 3, lower.bottom - 3), 1)
    for wx in range(lower.x + 8, lower.right - 18, 24):
        pygame.draw.rect(screen, glass, (wx, lower.y + 15, 17, 14))
        pygame.draw.line(screen, glass_hi, (wx + 2, lower.y + 18), (wx + 15, lower.y + 18), 1)
        pygame.draw.rect(screen, glass_dark, (wx, lower.y + 15, 17, 14), 1)

    pygame.draw.rect(screen, side, upper.move(0, 3))
    pygame.draw.rect(screen, wall, upper)
    pygame.draw.rect(screen, (246, 247, 236), (upper.x + 4, upper.y + 4, upper.w - 8, 7))
    pygame.draw.rect(screen, glass, (upper.x + 9, upper.y + 16, upper.w - 18, 14))
    for gx in range(upper.x + 17, upper.right - 12, 17):
        pygame.draw.line(screen, glass_dark, (gx, upper.y + 16), (gx, upper.y + 30), 1)
    pygame.draw.line(screen, glass_hi, (upper.x + 11, upper.y + 19), (upper.right - 11, upper.y + 19), 1)
    pygame.draw.rect(screen, glass_dark, (upper.x + 9, upper.y + 16, upper.w - 18, 14), 1)

    roof_slab(upper, True)
    roof_slab(lower, False)

    # Lakeside terrace and greenery visible in the reference.
    terrace = pygame.Rect(base.x - 2, base.bottom - 2, base.w + 34, 12)
    pygame.draw.rect(screen, (205, 203, 190), terrace)
    pygame.draw.line(screen, (246, 244, 230), (terrace.x + 3, terrace.y + 3), (terrace.right - 3, terrace.y + 3), 1)
    pygame.draw.line(screen, (136, 145, 140), (terrace.x, terrace.bottom - 1), (terrace.right, terrace.bottom - 1), 1)
    for tx in (base.x + 7, base.x + 42, base.right + 12):
        pygame.draw.rect(screen, (91, 73, 46), (tx, base.bottom - 23, 4, 22))
        pygame.draw.circle(screen, (55, 128, 70), (tx - 8, base.bottom - 25), 8)
        pygame.draw.circle(screen, (76, 157, 77), (tx + 8, base.bottom - 27), 8)
        pygame.draw.circle(screen, (48, 112, 66), (tx, base.bottom - 36), 7)

def draw_pharmacy_school_overlay():
    if current_map_id != 2:
        return

    base = pygame.Rect(22 * TILE + 6, HUD + 1 * TILE + 2, 7 * TILE - 12, 5 * TILE - 6)
    shadow = pygame.Surface((base.w + 38, base.h + 28), pygame.SRCALPHA)
    pygame.draw.polygon(shadow, (0, 0, 0, 55), [(16, 22), (base.w + 32, 10), (base.w + 26, base.h + 22), (6, base.h + 25)])
    screen.blit(shadow, (base.x - 14, base.y - 12))

    wall = (236, 240, 232)
    wall_side = (205, 213, 211)
    trim = (255, 252, 235)
    line = (160, 169, 168)
    roof = (220, 73, 42)
    roof_dark = (132, 48, 38)
    glass = (55, 96, 124)
    glass_hi = (164, 212, 228)
    accent = (220, 93, 58)

    cx = base.centerx
    wing_w, wing_h = 78, 88
    center_w, center_h = 54, 108
    left = pygame.Rect(cx - center_w // 2 - wing_w + 8, base.y + 20, wing_w, wing_h)
    right = pygame.Rect(cx + center_w // 2 - 8, base.y + 20, wing_w, wing_h)
    center = pygame.Rect(cx - center_w // 2, base.y + 4, center_w, center_h)

    def roof_strip(rect, lift=8, curve=False):
        pts = [(rect.x - 8, rect.y + lift), (rect.x + 8, rect.y), (rect.right - 8, rect.y), (rect.right + 8, rect.y + lift), (rect.right + 4, rect.y + lift + 8), (rect.x - 4, rect.y + lift + 8)]
        pygame.draw.polygon(screen, roof_dark, [(x, y + 4) for x, y in pts])
        pygame.draw.polygon(screen, trim, pts)
        pygame.draw.polygon(screen, roof, [(rect.x + 5, rect.y + lift - 1), (rect.right - 5, rect.y + lift - 1), (rect.right - 14, rect.y + lift + 6), (rect.x + 14, rect.y + lift + 6)])
        if curve:
            pygame.draw.line(screen, trim, pts[0], (pts[0][0] - 7, pts[0][1] - 9), 3)
            pygame.draw.line(screen, trim, pts[3], (pts[3][0] + 7, pts[3][1] - 9), 3)

    def wall_panel(rect, cols, rows):
        pygame.draw.rect(screen, wall_side, rect.move(0, 4))
        pygame.draw.rect(screen, wall, rect)
        pygame.draw.rect(screen, line, rect, 1)
        for row in range(rows):
            for col in range(cols):
                wx = rect.x + 9 + col * ((rect.w - 18) // cols)
                wy = rect.y + 20 + row * ((rect.h - 33) // rows)
                ww = max(9, (rect.w - 28) // cols)
                pygame.draw.rect(screen, glass, (wx, wy, ww, 11))
                pygame.draw.line(screen, glass_hi, (wx + 2, wy + 2), (wx + ww - 2, wy + 2), 1)
                pygame.draw.rect(screen, (25, 55, 76), (wx, wy, ww, 11), 1)
        for yy in range(rect.y + 39, rect.bottom - 10, 23):
            pygame.draw.line(screen, (214, 219, 213), (rect.x + 5, yy), (rect.right - 5, yy), 1)
        pygame.draw.rect(screen, accent, (rect.x + 6, rect.bottom - 27, rect.w - 12, 6))

    wall_panel(left, 3, 3)
    wall_panel(right, 3, 3)
    wall_panel(center, 2, 4)
    roof_strip(left, 8, True)
    roof_strip(right, 8, True)
    roof_strip(center, 9, True)

    gable = [(center.centerx - 18, center.y + 4), (center.centerx, center.y - 15), (center.centerx + 18, center.y + 4)]
    pygame.draw.polygon(screen, (185, 192, 188), [(x, y + 4) for x, y in gable])
    pygame.draw.polygon(screen, (242, 244, 236), gable)
    pygame.draw.circle(screen, (128, 139, 138), (center.centerx, center.y + 13), 4)
    arch = pygame.Rect(center.centerx - 16, center.bottom - 39, 32, 38)
    pygame.draw.arc(screen, (54, 70, 80), (arch.x, arch.y - 10, arch.w, 24), math.pi, 2 * math.pi, 2)
    pygame.draw.rect(screen, glass, (arch.x + 3, arch.y + 5, arch.w - 6, arch.h - 5))
    pygame.draw.line(screen, glass_hi, (arch.centerx, arch.y + 1), (arch.centerx, arch.bottom - 4), 1)

    stone = pygame.Rect(base.x + 14, base.bottom - 20, 62, 20)
    pygame.draw.ellipse(screen, (196, 190, 177), stone)
    pygame.draw.line(screen, (230, 70, 58), (stone.x + 13, stone.y + 10), (stone.right - 12, stone.y + 7), 3)
    pygame.draw.rect(screen, (81, 142, 75), (base.x + 88, base.bottom - 16, base.w - 110, 14))


def draw_fengting_canteen_overlay():
    if current_map_id != 2:
        return

    base = pygame.Rect(28 * TILE + 4, HUD + 13 * TILE + 2, 4 * TILE - 8, 4 * TILE - 5)
    shadow = pygame.Surface((base.w + 30, base.h + 30), pygame.SRCALPHA)
    pygame.draw.polygon(shadow, (0, 0, 0, 58), [(12, 22), (base.w + 24, 10), (base.w + 20, base.h + 24), (4, base.h + 27)])
    screen.blit(shadow, (base.x - 12, base.y - 10))

    wall = (235, 224, 205)
    trim = (252, 241, 220)
    orange = (222, 88, 43)
    orange_dark = (145, 55, 39)
    roof = (218, 62, 33)
    roof_dark = (124, 42, 32)
    glass = (42, 93, 118)
    glass_hi = (148, 208, 225)

    body = pygame.Rect(base.x + 2, base.y + 30, base.w - 4, base.h - 35)
    pygame.draw.rect(screen, (188, 179, 165), body.move(0, 5))
    pygame.draw.rect(screen, wall, body)
    pygame.draw.rect(screen, orange, (body.x + 6, body.y + 18, body.w - 12, body.h - 28))

    roof_pts = [(base.x - 8, base.y + 39), (base.x + 10, base.y + 13), (base.right - 10, base.y + 13), (base.right + 8, base.y + 39), (base.right + 2, base.y + 48), (base.x - 2, base.y + 48)]
    pygame.draw.polygon(screen, roof_dark, [(x, y + 5) for x, y in roof_pts])
    pygame.draw.polygon(screen, trim, roof_pts)
    for yy in range(base.y + 16, base.y + 39, 4):
        pygame.draw.line(screen, roof, (base.x + 12, yy), (base.right - 12, yy), 2)
    pygame.draw.polygon(screen, roof, [(base.x + 8, base.y + 34), (base.right - 8, base.y + 34), (base.right - 18, base.y + 44), (base.x + 18, base.y + 44)])

    for wx in (body.x + 13, body.right - 35):
        pygame.draw.rect(screen, glass, (wx, body.y + 20, 22, 13))
        pygame.draw.line(screen, glass_hi, (wx + 3, body.y + 23), (wx + 19, body.y + 23), 1)
        pygame.draw.rect(screen, (24, 57, 78), (wx, body.y + 20, 22, 13), 1)

    for cx in (body.centerx - 26, body.centerx, body.centerx + 26):
        arch = pygame.Rect(cx - 13, body.bottom - 32, 26, 31)
        pygame.draw.arc(screen, trim, (arch.x, arch.y - 10, arch.w, 22), math.pi, 2 * math.pi, 5)
        pygame.draw.rect(screen, trim, (arch.x, arch.y + 2, arch.w, arch.h - 2))
        inner = pygame.Rect(cx - 9, body.bottom - 25, 18, 24)
        pygame.draw.rect(screen, (35, 45, 50), inner)
        pygame.draw.arc(screen, (35, 45, 50), (inner.x, inner.y - 8, inner.w, 16), math.pi, 2 * math.pi, 2)
        pygame.draw.circle(screen, (230, 42, 32), (cx, inner.y + 5), 4)

    pygame.draw.rect(screen, (211, 200, 181), (body.x - 4, body.bottom - 5, body.w + 8, 8))
    pygame.draw.line(screen, (255, 248, 228), (body.x + 5, body.y + 8), (body.right - 5, body.y + 8), 1)


def draw_express_center_overlay():
    if current_map_id != 2:
        return

    base = pygame.Rect(14 * TILE + 2, HUD + 2 * TILE + 2, 4 * TILE - 4, 5 * TILE - 6)
    shadow = pygame.Surface((base.w + 34, base.h + 24), pygame.SRCALPHA)
    pygame.draw.polygon(shadow, (0, 0, 0, 55), [(12, 20), (base.w + 30, 9), (base.w + 24, base.h + 19), (4, base.h + 22)])
    screen.blit(shadow, (base.x - 12, base.y - 10))

    wall = (239, 235, 224)
    side = (211, 205, 193)
    trim = (252, 250, 241)
    glass = (52, 92, 101)
    glass_hi = (174, 223, 226)
    ink = (38, 45, 48)
    blue = (54, 78, 156)

    left = pygame.Rect(base.x + 3, base.y + 22, 54, 82)
    right = pygame.Rect(base.x + 50, base.y + 45, 82, 58)
    roof = [(base.x - 8, base.y + 24), (base.x + 8, base.y + 11), (base.right - 8, base.y + 11), (base.right + 7, base.y + 24), (base.right + 1, base.y + 31), (base.x - 2, base.y + 31)]

    pygame.draw.rect(screen, side, left.move(0, 4))
    pygame.draw.rect(screen, wall, left)
    pygame.draw.rect(screen, side, right.move(0, 4))
    pygame.draw.rect(screen, wall, right)
    pygame.draw.polygon(screen, (180, 178, 166), [(x, y + 4) for x, y in roof])
    pygame.draw.polygon(screen, trim, roof)
    pygame.draw.line(screen, (158, 160, 154), roof[0], roof[3], 2)

    glass_box = pygame.Rect(left.x + 8, left.y + 18, left.w - 16, left.h - 26)
    pygame.draw.rect(screen, glass, glass_box)
    for gx in range(glass_box.x + 10, glass_box.right - 4, 12):
        pygame.draw.line(screen, ink, (gx, glass_box.y), (gx, glass_box.bottom), 1)
    for gy in range(glass_box.y + 13, glass_box.bottom - 4, 13):
        pygame.draw.line(screen, glass_hi, (glass_box.x + 2, gy), (glass_box.right - 2, gy), 1)
    pygame.draw.rect(screen, ink, glass_box, 2)
    pygame.draw.rect(screen, blue, (glass_box.x + 9, glass_box.y + 4, 20, 9))

    sign = pygame.Rect(right.x + 10, right.y + 13, right.w - 18, 18)
    pygame.draw.rect(screen, (246, 238, 238), sign)
    pygame.draw.rect(screen, (198, 172, 172), sign, 1)
    center_text("快递服务中心", sign.centerx, sign.centery, (31, 34, 38), FONT_MINI)
    door = pygame.Rect(right.right - 23, right.bottom - 28, 16, 28)
    pygame.draw.rect(screen, (31, 40, 38), door)
    pygame.draw.line(screen, glass_hi, (door.x + 3, door.y + 4), (door.x + 3, door.bottom - 5), 1)

    for i in range(5):
        step = pygame.Rect(glass_box.centerx - 30 - i * 4, glass_box.bottom - 1 + i * 4, 60 + i * 8, 4)
        pygame.draw.rect(screen, (210, 210, 202), step)
        pygame.draw.line(screen, (246, 246, 238), (step.x + 3, step.y + 1), (step.right - 3, step.y + 1), 1)
    for px in range(base.x + 8, base.x + 54, 12):
        pygame.draw.rect(screen, (238, 238, 230), (px, base.bottom - 30, 7, 9))
        pygame.draw.circle(screen, (73, 139, 74), (px + 3, base.bottom - 33), 5)
    for bx in (right.x + 16, right.x + 36, right.x + 56):
        pygame.draw.circle(screen, (70, 128, 63), (bx, right.bottom - 7), 7)
        pygame.draw.circle(screen, (97, 153, 73), (bx + 5, right.bottom - 10), 6)


def draw_duxing_dorm_overlay():
    if current_map_id != 2:
        return

    def dorm(rect, cols, name, palette, people_seed):
        wall, wall_light, roof, roof_dark, glass = palette
        shadow = pygame.Surface((rect.w + 18, rect.h + 18), pygame.SRCALPHA)
        pygame.draw.polygon(shadow, (0, 0, 0, 54), [(10, 15), (rect.w + 14, 8), (rect.w + 10, rect.h + 14), (4, rect.h + 16)])
        screen.blit(shadow, (rect.x - 8, rect.y - 8))
        pygame.draw.rect(screen, (137, 143, 143), rect.move(0, 4))
        pygame.draw.rect(screen, wall, rect)
        pygame.draw.rect(screen, wall_light, (rect.x + 5, rect.y + 10, rect.w - 10, rect.h - 18))
        roof_pts = [(rect.x - 8, rect.y + 17), (rect.x + 12, rect.y + 3), (rect.right - 12, rect.y + 3), (rect.right + 8, rect.y + 17), (rect.right + 2, rect.y + 24), (rect.x - 2, rect.y + 24)]
        pygame.draw.polygon(screen, roof_dark, [(x, y + 4) for x, y in roof_pts])
        pygame.draw.polygon(screen, (245, 239, 222), roof_pts)
        pygame.draw.polygon(screen, roof, [(rect.x + 10, rect.y + 13), (rect.right - 10, rect.y + 13), (rect.right - 18, rect.y + 20), (rect.x + 18, rect.y + 20)])

        window_positions = []
        for row in range(3):
            for col in range(cols):
                wx = rect.x + 13 + col * ((rect.w - 26) // cols)
                wy = rect.y + 32 + row * 23
                ww = max(10, (rect.w - 38) // cols)
                pygame.draw.rect(screen, glass, (wx, wy, ww, 12))
                pygame.draw.line(screen, (167, 215, 232), (wx + 2, wy + 3), (wx + ww - 2, wy + 3), 1)
                pygame.draw.rect(screen, (24, 55, 78), (wx, wy, ww, 12), 1)
                window_positions.append((wx, wy, ww))
        pygame.draw.rect(screen, (187, 194, 190), (rect.x, rect.bottom - 10, rect.w, 10))
        pygame.draw.rect(screen, (46, 58, 65), (rect.centerx - 10, rect.bottom - 27, 20, 27))
        pygame.draw.line(screen, (121, 167, 187), (rect.centerx, rect.bottom - 25), (rect.centerx, rect.bottom - 4), 1)
        pulse_a = math.sin(time.time() * 7 + people_seed) * 3
        for idx in (1, min(len(window_positions) - 2, 5), min(len(window_positions) - 1, 9)):
            wx, wy, ww = window_positions[idx]
            px, py = wx + ww // 2, wy + 14
            pygame.draw.rect(screen, (255, 245, 210), (wx + 1, wy + 1, ww - 2, 10))
            pygame.draw.circle(screen, (246, 195, 138), (px, py), 4)
            pygame.draw.rect(screen, (231, 54, 62), (px - 4, py + 4, 8, 10))
            pygame.draw.line(screen, (246, 195, 138), (px - 4, py + 7), (px - 13, py + int(pulse_a) - 2), 3)
            pygame.draw.line(screen, (246, 195, 138), (px + 4, py + 7), (px + 13, py - int(pulse_a) - 2), 3)
            pygame.draw.line(screen, (255, 244, 176), (px + 13, py - int(pulse_a) - 2), (px + 18, py - int(pulse_a) - 8), 2)
        sos = pygame.Rect(rect.right - 34, rect.y + 30, 26, 13)
        pygame.draw.rect(screen, (249, 241, 220), sos)
        pygame.draw.rect(screen, (151, 42, 48), sos, 1)
        center_text("SOS", sos.centerx, sos.centery, (207, 43, 51), FONT_MINI)

    dorm(
        pygame.Rect(13 * TILE + 3, HUD + 10 * TILE + 2, 7 * TILE - 6, 3 * TILE + 6),
        5,
        "笃行园区",
        ((185, 193, 185), (215, 221, 211), (184, 72, 50), (112, 48, 40), (53, 96, 124)),
        0,
    )
    dorm(
        pygame.Rect(21 * TILE + 3, HUD + 10 * TILE + 2, 7 * TILE - 6, 3 * TILE + 6),
        5,
        "笃行园区",
        ((178, 186, 190), (211, 216, 216), (204, 83, 45), (124, 52, 38), (50, 91, 128)),
        3,
    )


def draw_third_map_dorms_overlay():
    if current_map_id != 2:
        return

    def compact_dorm(rect, cols, rows, palette, roof_style, name, phase):
        if rect.w < 48:
            wall, light, roof, roof_dark, glass = palette
            body = rect.inflate(8, 0)
            shadow = pygame.Surface((body.w + 16, body.h + 16), pygame.SRCALPHA)
            pygame.draw.polygon(shadow, (0, 0, 0, 50), [(8, 13), (body.w + 12, 7), (body.w + 9, body.h + 12), (3, body.h + 14)])
            screen.blit(shadow, (body.x - 7, body.y - 7))
            pygame.draw.rect(screen, (123, 132, 132), body.move(0, 3), border_radius=2)
            pygame.draw.rect(screen, wall, body, border_radius=2)
            pygame.draw.rect(screen, light, (body.x + 4, body.y + 15, body.w - 8, body.h - 21), border_radius=1)
            if roof_style == "gable":
                roof_pts = [(body.x - 5, body.y + 16), (body.centerx, body.y + 2), (body.right + 5, body.y + 16), (body.right + 1, body.y + 22), (body.x - 1, body.y + 22)]
                pygame.draw.polygon(screen, roof_dark, [(x, y + 3) for x, y in roof_pts])
                pygame.draw.polygon(screen, (248, 241, 225), roof_pts)
                pygame.draw.polygon(screen, roof, [(body.x + 5, body.y + 15), (body.centerx, body.y + 7), (body.right - 5, body.y + 15), (body.right - 10, body.y + 20), (body.x + 10, body.y + 20)])
            else:
                pygame.draw.rect(screen, roof_dark, (body.x - 4, body.y + 8, body.w + 8, 7))
                pygame.draw.rect(screen, roof, (body.x - 2, body.y + 4, body.w + 4, 7))
                pygame.draw.line(screen, (255, 226, 193), (body.x + 4, body.y + 7), (body.right - 4, body.y + 7), 1)

            windows = [
                pygame.Rect(body.x + 7, body.y + 27, 10, 9),
                pygame.Rect(body.right - 17, body.y + 27, 10, 9),
                pygame.Rect(body.x + 7, body.y + 45, 10, 9),
                pygame.Rect(body.right - 17, body.y + 45, 10, 9),
            ]
            for w in windows:
                pygame.draw.rect(screen, glass, w)
                pygame.draw.line(screen, (170, 216, 232), (w.x + 2, w.y + 2), (w.right - 2, w.y + 2), 1)
                pygame.draw.rect(screen, (26, 57, 82), w, 1)
            pygame.draw.rect(screen, (44, 56, 63), (body.centerx - 5, body.bottom - 17, 10, 17))
            pygame.draw.line(screen, (126, 169, 185), (body.centerx, body.bottom - 15), (body.centerx, body.bottom - 3), 1)
            for ledge_y in (body.y + 39, body.y + 57):
                pygame.draw.line(screen, (190, 199, 194), (body.x + 4, ledge_y), (body.right - 4, ledge_y), 1)
            pygame.draw.rect(screen, (214, 220, 210), (body.x + 4, body.bottom - 21, body.w - 8, 3))
            pygame.draw.rect(screen, (178, 186, 181), (body.x, body.bottom - 5, body.w, 5))
            pygame.draw.line(screen, (244, 246, 235), (body.x + 5, body.y + 17), (body.right - 5, body.y + 17), 1)
            return

        wall, light, roof, roof_dark, glass = palette
        shadow = pygame.Surface((rect.w + 18, rect.h + 18), pygame.SRCALPHA)
        pygame.draw.polygon(shadow, (0, 0, 0, 52), [(10, 14), (rect.w + 14, 8), (rect.w + 10, rect.h + 14), (4, rect.h + 16)])
        screen.blit(shadow, (rect.x - 8, rect.y - 8))
        pygame.draw.rect(screen, (122, 131, 134), rect.move(0, 4))
        pygame.draw.rect(screen, wall, rect)
        pygame.draw.rect(screen, light, (rect.x + 4, rect.y + 11, rect.w - 8, rect.h - 19))
        if roof_style == "gable":
            pts = [(rect.x - 6, rect.y + 17), (rect.centerx, rect.y - 1), (rect.right + 6, rect.y + 17), (rect.right, rect.y + 24), (rect.x, rect.y + 24)]
            pygame.draw.polygon(screen, roof_dark, [(x, y + 4) for x, y in pts])
            pygame.draw.polygon(screen, (246, 239, 222), pts)
            pygame.draw.polygon(screen, roof, [(rect.x + 10, rect.y + 14), (rect.centerx, rect.y + 5), (rect.right - 10, rect.y + 14), (rect.right - 17, rect.y + 20), (rect.x + 17, rect.y + 20)])
        else:
            pygame.draw.rect(screen, roof_dark, (rect.x - 4, rect.y + 5, rect.w + 8, 9))
            pygame.draw.rect(screen, roof, (rect.x - 2, rect.y + 1, rect.w + 4, 9))
            pygame.draw.line(screen, (252, 230, 192), (rect.x + 5, rect.y + 4), (rect.right - 5, rect.y + 4), 1)

        windows = []
        for row in range(rows):
            for col in range(cols):
                wx = rect.x + 10 + col * ((rect.w - 20) // cols)
                wy = rect.y + 29 + row * max(18, (rect.h - 44) // rows)
                ww = max(9, (rect.w - 32) // cols)
                pygame.draw.rect(screen, glass, (wx, wy, ww, 10))
                pygame.draw.line(screen, (166, 213, 230), (wx + 2, wy + 2), (wx + ww - 2, wy + 2), 1)
                pygame.draw.rect(screen, (28, 58, 83), (wx, wy, ww, 10), 1)
                windows.append((wx, wy, ww))
        pygame.draw.rect(screen, (176, 184, 181), (rect.x, rect.bottom - 8, rect.w, 8))
        pygame.draw.rect(screen, (44, 56, 64), (rect.centerx - 8, rect.bottom - 24, 16, 24))
        if name:
            center_text(name, rect.centerx, rect.y + 39, (246, 72, 76), FONT_MINI)

    small_specs = [
        ((3, 2), "映雪园区", "flat", 1),
        ((5, 2), "映雪园区", "gable", 2),
        ((7, 2), "映雪园区", "flat", 3),
        ((9, 2), "映雪园区", "gable", 4),
        ((3, 5), "映雪园区", "gable", 5),
        ((5, 5), "映雪园区", "flat", 6),
        ((7, 5), "映雪园区", "gable", 7),
        ((9, 5), "映雪园区", "flat", 8),
        ((2, 10), "国光园区", "flat", 9),
        ((4, 10), "国光园区", "gable", 10),
        ((6, 10), "国光园区", "flat", 11),
        ((8, 10), "国光园区", "gable", 12),
        ((10, 10), "国光园区", "flat", 13),
        ((2, 13), "国光园区", "gable", 14),
        ((4, 13), "国光园区", "flat", 15),
        ((6, 13), "国光园区", "gable", 16),
        ((8, 13), "国光园区", "flat", 17),
        ((10, 13), "国光园区", "gable", 18),
    ]
    for (gx, gy), name, roof_style, phase in small_specs:
        palette = ((196, 202, 196), (226, 230, 219), (196, 73, 48), (120, 48, 38), (55, 101, 132))
        if name == "国光园区":
            palette = ((188, 197, 192), (219, 225, 216), (216, 88, 49), (133, 54, 39), (49, 93, 126))
        compact_dorm(
            pygame.Rect(gx * TILE + 2, HUD + gy * TILE + 2, TILE - 4, 2 * TILE - 4),
            1,
            1,
            palette,
            roof_style,
            "",
            phase,
        )
    compact_dorm(
        pygame.Rect(29 * TILE + 3, HUD + 10 * TILE + 2, 3 * TILE - 6, 3 * TILE + 8),
        2,
        2,
        ((181, 186, 178), (217, 220, 210), (196, 75, 48), (118, 49, 39), (55, 91, 121)),
        "flat",
        "丰庭园区",
        7,
    )


def draw_dewang_library_overlay():
    if current_map_id != 3:
        return

    base = pygame.Rect(11 * TILE + 14, HUD + 9 * TILE + 8, 9 * TILE, 4 * TILE)
    shadow = pygame.Surface((base.w + 70, base.h + 48), pygame.SRCALPHA)
    pygame.draw.polygon(shadow, (0, 0, 0, 62), [(24, 28), (base.w + 50, 12), (base.w + 42, base.h + 32), (8, base.h + 36)])
    screen.blit(shadow, (base.x - 26, base.y - 16))

    wall = (246, 247, 239)
    wall_side = (219, 228, 224)
    wall_shadow = (174, 187, 190)
    cornice = (255, 253, 238)
    line = (188, 199, 199)
    ink = (74, 92, 104)
    glass = (48, 103, 172)
    glass_dark = (25, 58, 108)
    glass_hi = (169, 214, 244)
    roof = (218, 84, 44)
    roof_dark = (132, 52, 38)
    green = (75, 148, 72)

    # All major parts are anchored to the same center line so both wings stay symmetric.
    cx = base.centerx
    wing_w, wing_h = 70, 66
    tower_w, tower_h = 124, 108
    gap = -8
    tower = pygame.Rect(cx - tower_w // 2, base.y + 0, tower_w, tower_h)
    left = pygame.Rect(tower.x - gap - wing_w, base.y + 45, wing_w, wing_h)
    right = pygame.Rect(tower.right + gap, base.y + 45, wing_w, wing_h)
    middle_band = pygame.Rect(cx - 68, base.y + 56, 136, 34)
    porch = pygame.Rect(cx - 31, base.y + 92, 62, 32)

    def roof_cap(rect, lift=18, wide=16):
        eave = [(rect.x - wide, rect.y + lift), (rect.x + 8, rect.y + 5), (rect.right - 8, rect.y + 5), (rect.right + wide, rect.y + lift), (rect.right + wide - 5, rect.y + lift + 7), (rect.x - wide + 5, rect.y + lift + 7)]
        pygame.draw.polygon(screen, roof_dark, [(x, y + 5) for x, y in eave])
        pygame.draw.polygon(screen, cornice, eave)
        tile = [(rect.x + 7, rect.y + lift - 4), (rect.right - 7, rect.y + lift - 4), (rect.right - 15, rect.y + lift + 4), (rect.x + 15, rect.y + lift + 4)]
        pygame.draw.polygon(screen, roof, tile)
        pygame.draw.line(screen, (255, 255, 244), eave[0], eave[3], 2)
        pygame.draw.line(screen, (165, 67, 49), tile[0], tile[1], 1)
        # Upturned tips on both ends, matching the reference roof silhouette.
        pygame.draw.line(screen, cornice, (eave[0][0], eave[0][1]), (eave[0][0] - 7, eave[0][1] - 8), 3)
        pygame.draw.line(screen, cornice, (eave[3][0], eave[3][1]), (eave[3][0] + 7, eave[3][1] - 8), 3)

    def wall_block(rect, cols, rows, arched_top=False):
        pygame.draw.rect(screen, wall_shadow, rect.move(0, 4))
        pygame.draw.rect(screen, wall, rect)
        pygame.draw.rect(screen, wall_side, (rect.x, rect.y + 2, 5, rect.h - 2))
        pygame.draw.rect(screen, cornice, (rect.x + 5, rect.y + 4, rect.w - 10, 9))
        pygame.draw.line(screen, line, (rect.x + 5, rect.y + 14), (rect.right - 5, rect.y + 14), 1)
        pygame.draw.line(screen, (255, 255, 248), (rect.x + 9, rect.y + 6), (rect.right - 9, rect.y + 6), 1)
        for gx in range(rect.x + 9, rect.right - 7, max(12, rect.w // max(2, cols))):
            pygame.draw.line(screen, (207, 216, 214), (gx, rect.y + 15), (gx, rect.bottom - 7), 1)
        for gy in range(rect.y + 36, rect.bottom - 10, 22):
            pygame.draw.line(screen, (207, 216, 214), (rect.x + 6, gy), (rect.right - 6, gy), 1)
        for row in range(rows):
            wy = rect.y + 22 + row * max(1, (rect.h - 35) // rows)
            for col in range(cols):
                wx = rect.x + 9 + col * max(1, (rect.w - 18) // cols)
                ww = max(7, (rect.w - 25) // cols)
                wh = 9
                if arched_top and row == 0:
                    pygame.draw.rect(screen, glass, (wx, wy + 3, ww, wh - 2))
                    pygame.draw.arc(screen, glass_dark, (wx, wy - 3, ww, 10), math.pi, 2 * math.pi, 1)
                else:
                    pygame.draw.rect(screen, glass, (wx, wy, ww, wh))
                pygame.draw.line(screen, glass_hi, (wx + 2, wy + 2), (wx + ww - 2, wy + 2), 1)
                pygame.draw.rect(screen, glass_dark, (wx, wy, ww, wh), 1)

    wall_block(left, 2, 3)
    wall_block(right, 2, 3)
    wall_block(tower, 5, 5, True)
    roof_cap(left, 13, 12)
    roof_cap(right, 13, 12)
    roof_cap(tower, 18, 24)

    # Central projecting glass arch and balcony, the most recognizable part of the real building.
    pygame.draw.rect(screen, (238, 241, 234), middle_band)
    pygame.draw.rect(screen, line, middle_band, 1)
    for wx in range(middle_band.x + 8, middle_band.right - 8, 14):
        pygame.draw.rect(screen, glass, (wx, middle_band.y + 10, 9, 14))
        pygame.draw.line(screen, glass_hi, (wx + 2, middle_band.y + 12), (wx + 7, middle_band.y + 12), 1)
        pygame.draw.rect(screen, glass_dark, (wx, middle_band.y + 10, 9, 14), 1)

    arch_frame = pygame.Rect(tower.centerx - 27, tower.y + 86, 54, 68)
    pygame.draw.rect(screen, (249, 249, 240), arch_frame.inflate(8, 8))
    pygame.draw.arc(screen, ink, (arch_frame.x + 2, arch_frame.y - 16, arch_frame.w - 4, 38), math.pi, 2 * math.pi, 3)
    arch = pygame.Rect(arch_frame.x + 8, arch_frame.y + 8, arch_frame.w - 16, arch_frame.h - 12)
    pygame.draw.rect(screen, glass_dark, arch)
    for gx in range(arch.x + 6, arch.right - 2, 8):
        pygame.draw.line(screen, glass_hi, (gx, arch.y + 3), (gx, arch.bottom - 4), 1)
    for gy in range(arch.y + 8, arch.bottom - 3, 9):
        pygame.draw.line(screen, (93, 149, 209), (arch.x + 3, gy), (arch.right - 3, gy), 1)
    pygame.draw.line(screen, (236, 242, 238), (arch.centerx, arch.y - 7), (arch.centerx, arch.bottom), 2)
    pygame.draw.rect(screen, ink, arch, 1)

    # Entrance porch with columns and a small statue-like dark doorway.
    pygame.draw.rect(screen, wall_shadow, porch.move(0, 4))
    pygame.draw.rect(screen, (252, 251, 241), porch)
    pygame.draw.rect(screen, line, porch, 1)
    pygame.draw.rect(screen, (238, 232, 201), (porch.x + 7, porch.y + 3, porch.w - 14, 5))
    for px in (porch.x + 12, porch.centerx, porch.right - 12):
        pygame.draw.rect(screen, cornice, (px - 3, porch.y + 7, 6, porch.h - 8))
        pygame.draw.line(screen, (189, 199, 198), (px + 3, porch.y + 7), (px + 3, porch.bottom - 2), 1)
    door = pygame.Rect(porch.centerx - 9, porch.bottom - 20, 18, 20)
    pygame.draw.rect(screen, (42, 61, 85), door)
    pygame.draw.circle(screen, (101, 112, 105), (door.centerx, door.y + 6), 5)

    # Broad ceremonial stairs and front landscape.
    for i in range(6):
        step_w = 110 + i * 22
        step = pygame.Rect(cx - step_w // 2, base.bottom - 12 + i * 4, step_w, 4)
        pygame.draw.rect(screen, (222, 224, 216), step)
        pygame.draw.line(screen, (158, 165, 160), (step.x, step.bottom - 1), (step.right, step.bottom - 1), 1)
    garden = pygame.Rect(cx - 32, base.bottom + 8, 64, 14)
    pygame.draw.rect(screen, (101, 150, 73), garden)
    pygame.draw.polygon(screen, (223, 206, 73), [(garden.x + 6, garden.y + 2), (garden.centerx, garden.y + 1), (garden.centerx - 4, garden.bottom - 2), (garden.x + 4, garden.bottom - 1)])
    pygame.draw.polygon(screen, (126, 74, 50), [(garden.centerx, garden.y + 1), (garden.right - 5, garden.y + 2), (garden.right - 4, garden.bottom - 1), (garden.centerx - 4, garden.bottom - 2)])
    pygame.draw.rect(screen, (238, 236, 218), (garden.centerx - 5, garden.y - 14, 10, 18))
    for tx in (cx - 130, cx + 130):
        pygame.draw.rect(screen, (103, 132, 74), (tx - 12, base.bottom - 29, 24, 11))
        pygame.draw.circle(screen, green, (tx - 8, base.bottom - 38), 8)
        pygame.draw.circle(screen, (101, 174, 81), (tx + 7, base.bottom - 38), 8)
        pygame.draw.circle(screen, (64, 132, 66), (tx, base.bottom - 48), 7)

def draw_fourth_map_side_buildings_overlay():
    if current_map_id != 3:
        return

    wall = (232, 235, 225)
    side = (204, 214, 210)
    roof = (199, 79, 45)
    roof_dark = (126, 52, 40)
    glass = (56, 103, 154)
    glass_hi = (137, 188, 225)

    def building(rect, cols):
        shadow = pygame.Surface((rect.w + 18, rect.h + 18), pygame.SRCALPHA)
        pygame.draw.polygon(shadow, (0, 0, 0, 54), [(10, 16), (rect.w + 14, 8), (rect.w + 10, rect.h + 14), (4, rect.h + 16)])
        screen.blit(shadow, (rect.x - 8, rect.y - 8))
        pygame.draw.rect(screen, side, rect.move(0, 4))
        pygame.draw.rect(screen, wall, rect)
        pygame.draw.rect(screen, (218, 226, 222), (rect.x, rect.y + rect.h - 12, rect.w, 12))
        pygame.draw.rect(screen, (246, 247, 238), (rect.x + 4, rect.y + 4, rect.w - 8, 8))
        roof_pts = [(rect.x - 8, rect.y + 13), (rect.x + 8, rect.y + 2), (rect.right - 8, rect.y + 2), (rect.right + 8, rect.y + 13), (rect.right + 2, rect.y + 20), (rect.x - 2, rect.y + 20)]
        pygame.draw.polygon(screen, roof_dark, [(x, y + 4) for x, y in roof_pts])
        pygame.draw.polygon(screen, (252, 248, 232), roof_pts)
        pygame.draw.polygon(screen, roof, [(rect.x + 8, rect.y + 10), (rect.right - 8, rect.y + 10), (rect.right - 15, rect.y + 16), (rect.x + 15, rect.y + 16)])
        for col in range(cols):
            for row in range(3):
                wx = rect.x + 9 + col * ((rect.w - 18) // cols)
                wy = rect.y + 26 + row * 19
                ww = max(9, (rect.w - 24) // cols)
                pygame.draw.rect(screen, glass, (wx, wy, ww, 10))
                pygame.draw.line(screen, glass_hi, (wx + 2, wy + 2), (wx + ww - 2, wy + 2), 1)
                pygame.draw.rect(screen, (29, 61, 96), (wx, wy, ww, 10), 1)
        pygame.draw.line(screen, (192, 202, 198), (rect.x + 5, rect.y + 48), (rect.right - 5, rect.y + 48), 1)

    building(pygame.Rect(22 * TILE, HUD + 10 * TILE, 4 * TILE, 5 * TILE), 3)
    building(pygame.Rect(27 * TILE, HUD + 10 * TILE, 4 * TILE, 5 * TILE), 3)

def draw_aerospace_building_tile(r, x, y):
    above = is_aerospace_building_tile(x, y - 1)
    below = is_aerospace_building_tile(x, y + 1)
    left = is_aerospace_building_tile(x - 1, y)
    right = is_aerospace_building_tile(x + 1, y)
    rel_x = x - 16
    rel_y = y - 8
    center = 3 <= rel_x <= 4

    brick = (175, 77, 50)
    brick_dark = (124, 48, 38)
    cream = (238, 226, 188)
    cream_shadow = (190, 174, 139)
    glass = (55, 112, 181)
    glass_dark = (28, 61, 105)
    glass_light = (111, 174, 235)

    pygame.draw.rect(screen, brick, r)
    for yy in range(r.y + 6, r.bottom - 3, 7):
        pygame.draw.line(screen, (209, 112, 76), (r.x + 3, yy), (r.right - 4, yy), 1)

    if center:
        pygame.draw.rect(screen, glass_dark, r.inflate(-4, -2))
        for gx in range(r.x + 5, r.right - 4, 9):
            pygame.draw.line(screen, (18, 45, 82), (gx, r.y + 4), (gx, r.bottom - 5), 1)
        for gy in range(r.y + 7, r.bottom - 4, 8):
            pygame.draw.line(screen, glass_light, (r.x + 5, gy), (r.right - 6, gy), 1)
        if rel_y == 0:
            pygame.draw.polygon(screen, cream_shadow, [(r.x - 6, r.y + 14), (r.centerx, r.y - 1), (r.right + 6, r.y + 14)])
            pygame.draw.polygon(screen, cream, [(r.x - 4, r.y + 11), (r.centerx, r.y - 5), (r.right + 4, r.y + 11)])
            pygame.draw.line(screen, (255, 246, 211), (r.x + 2, r.y + 11), (r.right - 2, r.y + 11), 2)
        if rel_y in {4, 5}:
            pygame.draw.arc(screen, cream, (r.x - 2, r.y - 7, r.w + 4, r.h + 18), math.pi, 2 * math.pi, 4)
    else:
        if not above:
            pygame.draw.rect(screen, cream_shadow, (r.x, r.y + 3, r.w, 5))
            pygame.draw.rect(screen, cream, (r.x, r.y, r.w, 5))
            if rel_x in {0, 6}:
                pygame.draw.polygon(screen, cream_shadow, [(r.x + 2, r.y + 8), (r.centerx, r.y - 3), (r.right - 2, r.y + 8)])
                pygame.draw.polygon(screen, cream, [(r.x + 4, r.y + 6), (r.centerx, r.y - 6), (r.right - 4, r.y + 6)])
        if rel_x % 2 == 0:
            pygame.draw.rect(screen, cream, (r.x + 1, r.y + 2, 4, r.h - 5))
            pygame.draw.rect(screen, cream_shadow, (r.right - 5, r.y + 2, 4, r.h - 5))
        for wy in (8, 20):
            pygame.draw.rect(screen, glass, (r.x + 8, r.y + wy, 17, 7))
            pygame.draw.line(screen, glass_light, (r.x + 10, r.y + wy + 2), (r.x + 22, r.y + wy + 2), 1)
            pygame.draw.rect(screen, glass_dark, (r.x + 8, r.y + wy, 17, 7), 1)

    if not left:
        pygame.draw.line(screen, brick_dark, (r.x, r.y + 5), (r.x, r.bottom), 2)
    if not right:
        pygame.draw.line(screen, brick_dark, (r.right - 1, r.y + 5), (r.right - 1, r.bottom), 2)
    if not below:
        pygame.draw.rect(screen, (75, 63, 67), (r.x, r.bottom - 4, r.w, 4))
        if center:
            pygame.draw.rect(screen, (35, 48, 71), (r.x + 8, r.y + 8, 16, 21))
            pygame.draw.arc(screen, cream, (r.x + 4, r.y + 3, 24, 26), math.pi, 2 * math.pi, 3)
    pygame.draw.rect(screen, (70, 43, 42), r, 1)


def draw_rescue_student(x, y, phase):
    shirt = [(244, 68, 72), (255, 198, 74), (92, 176, 238)][phase % 3]
    pygame.draw.circle(screen, (255, 214, 172), (x, y), 3)
    pygame.draw.rect(screen, shirt, (x - 3, y + 3, 6, 5))
    pygame.draw.line(screen, (255, 214, 172), (x - 3, y + 3), (x - 8, y - 2), 2)
    pygame.draw.line(screen, (255, 214, 172), (x + 3, y + 3), (x + 8, y - 3), 2)
    pygame.draw.line(screen, (255, 245, 146), (x + 7, y - 5), (x + 12, y - 9), 2)


def draw_dorm_window(r, wx, wy, lit, rescue=False, phase=0):
    glass = (245, 206, 112) if lit else (76, 104, 122)
    pygame.draw.rect(screen, glass, (wx, wy, 8, 8))
    pygame.draw.line(screen, (255, 239, 168) if lit else (121, 153, 166), (wx + 2, wy + 2), (wx + 6, wy + 2), 1)
    pygame.draw.rect(screen, (62, 47, 45), (wx, wy, 8, 8), 1)
    if rescue:
        draw_rescue_student(wx + 4, wy + 4, phase)


def draw_fourth_map_building_tile(r, x, y):
    above = tile_at(x, y - 1) == "B"
    below = tile_at(x, y + 1) == "B"
    left = tile_at(x - 1, y) == "B"
    right = tile_at(x + 1, y) == "B"
    wall = (232, 235, 225)
    wall_light = (248, 248, 239)
    wall_side = (204, 214, 210)
    roof = (199, 79, 45)
    roof_dark = (125, 52, 40)
    glass = (56, 103, 154)
    glass_hi = (137, 188, 225)

    pygame.draw.rect(screen, wall_side, r)
    pygame.draw.rect(screen, wall, (r.x + 2, r.y + 3, r.w - 4, r.h - 5))
    pygame.draw.line(screen, wall_light, (r.x + 4, r.y + 5), (r.right - 5, r.y + 5), 1)
    if not above:
        over_l = 4 if not left else 0
        over_r = 4 if not right else 0
        roof_poly = [(r.x - over_l, r.y + 11), (r.x + 8, r.y + 2), (r.right - 8, r.y + 2), (r.right + over_r, r.y + 11), (r.right, r.y + 18), (r.x, r.y + 18)]
        pygame.draw.polygon(screen, roof_dark, [(px, py + 3) for px, py in roof_poly])
        pygame.draw.polygon(screen, (252, 248, 232), roof_poly)
        pygame.draw.polygon(screen, roof, [(r.x + 6, r.y + 10), (r.right - 6, r.y + 10), (r.right - 11, r.y + 15), (r.x + 11, r.y + 15)])
    elif tile_seed(x, y) % 3 == 0:
        pygame.draw.rect(screen, (215, 222, 216), (r.x + 4, r.y + 4, r.w - 8, 5))
    y_slots = (8, 20) if above and below else ((8,) if not below else (17,))
    for wy in y_slots:
        for wx in (7, 19):
            pygame.draw.rect(screen, glass, (r.x + wx, r.y + wy, 8, 8))
            pygame.draw.line(screen, glass_hi, (r.x + wx + 2, r.y + wy + 2), (r.x + wx + 6, r.y + wy + 2), 1)
            pygame.draw.rect(screen, (29, 61, 96), (r.x + wx, r.y + wy, 8, 8), 1)
    if not below:
        pygame.draw.rect(screen, (190, 199, 194), (r.x, r.bottom - 4, r.w, 4))
        if tile_seed(x, y) % 4 == 0:
            pygame.draw.rect(screen, (65, 82, 103), (r.x + 11, r.y + 9, 10, 19))
            pygame.draw.line(screen, glass_hi, (r.x + 13, r.y + 12), (r.x + 19, r.y + 12), 1)
    if not left:
        pygame.draw.line(screen, (181, 193, 190), (r.x, r.y + 8), (r.x, r.bottom), 1)
    if not right:
        pygame.draw.line(screen, (158, 170, 169), (r.right - 1, r.y + 8), (r.right - 1, r.bottom), 1)

def draw_campus_building_tile(r, x, y):
    above = tile_at(x, y - 1) == "B"
    below = tile_at(x, y + 1) == "B"
    left = tile_at(x - 1, y) == "B"
    right = tile_at(x + 1, y) == "B"

    if current_map_id == 3:
        draw_fourth_map_building_tile(r, x, y)
        return
    if current_map_id != 0:
        pygame.draw.rect(screen, (82, 88, 92), r)
        pygame.draw.rect(screen, (118, 124, 125), (r.x + 3, r.y + 5, r.w - 6, r.h - 8))
        pygame.draw.rect(screen, (45, 48, 50), r, 1)
        return
    district = (x // 6 + y // 4) % 4
    palettes = [
        ((128, 89, 68), (161, 119, 86), (128, 45, 43), (82, 32, 36), (230, 188, 121)),
        ((116, 83, 72), (148, 111, 91), (104, 59, 54), (69, 42, 42), (231, 207, 135)),
        ((137, 101, 74), (174, 132, 90), (142, 54, 46), (88, 38, 35), (245, 214, 126)),
        ((106, 91, 79), (146, 124, 101), (92, 63, 57), (62, 43, 41), (220, 190, 130)),
    ]
    wall, wall_light, roof, roof_dark, trim = palettes[district]

    pygame.draw.rect(screen, wall, r)
    pygame.draw.rect(screen, wall_light, (r.x + 3, r.y + 5, r.w - 6, r.h - 8))

    if not above:
        if district == 1:
            pygame.draw.rect(screen, roof_dark, (r.x - (0 if left else 3), r.y + 5, r.w + (0 if left else 3) + (0 if right else 3), 10))
            pygame.draw.rect(screen, roof, (r.x - (0 if left else 3), r.y + 2, r.w + (0 if left else 3) + (0 if right else 3), 10))
            pygame.draw.line(screen, (185, 97, 78), (r.x + 4, r.y + 8), (r.right - 4, r.y + 8), 2)
        elif district == 3:
            roof_poly = [(r.x, r.y + 15), (r.x + 8, r.y + 3), (r.right - 8, r.y + 3), (r.right, r.y + 15), (r.right, r.y + 20), (r.x, r.y + 20)]
            pygame.draw.polygon(screen, roof_dark, [(px, py + 3) for px, py in roof_poly])
            pygame.draw.polygon(screen, roof, roof_poly)
        else:
            roof_poly = [(r.x - (0 if left else 5), r.y + 11), (r.centerx, r.y + 1), (r.right + (0 if right else 5), r.y + 11), (r.right, r.y + 19), (r.x, r.y + 19)]
            pygame.draw.polygon(screen, roof_dark, [(px, py + 3) for px, py in roof_poly])
            pygame.draw.polygon(screen, roof, roof_poly)
            pygame.draw.line(screen, (177, 79, 66), (r.x + 4, r.y + 13), (r.right - 4, r.y + 13), 2)
    elif tile_seed(x, y) % 5 == 0:
        pygame.draw.rect(screen, (107, 74, 61), (r.x + 4, r.y + 4, r.w - 8, 6))

    if not left:
        pygame.draw.line(screen, (76, 55, 50), (r.x, r.y + 7), (r.x, r.bottom), 2)
    if not right:
        pygame.draw.line(screen, (72, 49, 45), (r.right - 1, r.y + 7), (r.right - 1, r.bottom), 2)
    if district in {1, 3} and left and right:
        pygame.draw.rect(screen, (90, 67, 57), (r.x + 2, r.y + 17, r.w - 4, 3))
        pygame.draw.rect(screen, (90, 67, 57), (r.x + 2, r.y + 28, r.w - 4, 3))

    if above and below:
        lit = tile_seed(x, y) % 4 != 0
        rescue = current_map_id == 0 and tile_seed(x, y) in {7, 21, 45, 62, 84, 98}
        draw_dorm_window(r, r.x + 6, r.y + 8, lit, rescue, tile_seed(x, y))
        if district != 3:
            draw_dorm_window(r, r.x + 19, r.y + 8, not lit, False, tile_seed(x, y) + 1)
        else:
            pygame.draw.rect(screen, (86, 67, 62), (r.x + 18, r.y + 6, 10, 15), 1)
            draw_dorm_window(r, r.x + 19, r.y + 9, not lit, False, tile_seed(x, y) + 1)
    elif not below:
        pygame.draw.rect(screen, (65, 48, 44), (r.x, r.bottom - 5, r.w, 5))
        if tile_seed(x, y) % 4 == 0:
            pygame.draw.rect(screen, (82, 50, 38), (r.x + 10, r.y + 8, 12, 20))
            pygame.draw.rect(screen, trim, (r.x + 12, r.y + 10, 8, 4))
        else:
            draw_dorm_window(r, r.x + 6, r.y + 9, True, tile_seed(x, y) % 13 == 0, tile_seed(x, y))
            draw_dorm_window(r, r.x + 19, r.y + 9, tile_seed(x, y) % 2 == 0, False, tile_seed(x, y) + 2)

    pygame.draw.rect(screen, (43, 33, 32), r, 1)

def draw_lake_tile(r, x, y):
    pygame.draw.rect(screen, COLORS["L"], r)
    wave = (218, 246, 249)
    offset = (tile_seed(x, y) % 8) - 4
    pygame.draw.arc(screen, wave, (r.x + 3 + offset, r.y + 8, r.w - 10, 11), 0, math.pi, 2)
    pygame.draw.arc(screen, (89, 174, 196), (r.x + 4 - offset, r.y + 21, r.w - 8, 9), 0, math.pi, 2)


def draw_map():
    screen.fill((18, 23, 28))
    for y, row in enumerate(GAME_MAP):
        for x, tile in enumerate(row):
            r = pygame.Rect(x * TILE, HUD + y * TILE, TILE, TILE)
            if tile == "R":
                draw_road_tile(r, x, y)
            elif tile == "B":
                if current_map_id == 3 and 14 <= x <= 18 and 9 <= y <= 14:
                    draw_road_tile(r, x, y)
                elif current_map_id == 2 and (
                    (15 <= x <= 17 and 2 <= y <= 6)
                    or (x in {3, 5, 7, 9} and y in {2, 3, 5, 6})
                    or (x in {2, 4, 6, 8, 10} and y in {10, 11, 13, 14})
                    or (23 <= x <= 27 and 1 <= y <= 5)
                    or (13 <= x <= 19 and 10 <= y <= 12)
                    or (21 <= x <= 27 and 10 <= y <= 12)
                    or (29 <= x <= 31 and 10 <= y <= 12)
                    or (29 <= x <= 31 and 14 <= y <= 16)
                ):
                    draw_field_tile(r, x, y, "S") if y <= 7 else draw_road_tile(r, x, y)
                elif is_aerospace_building_tile(x, y):
                    draw_aerospace_building_tile(r, x, y)
                else:
                    draw_campus_building_tile(r, x, y)
            elif tile in {"P", "F", "K", "S"}:
                draw_field_tile(r, x, y, tile)
            elif tile == "L":
                draw_lake_tile(r, x, y)
            elif tile == "G":
                pygame.draw.rect(screen, COLORS["R"], r)
                pygame.draw.circle(screen, (255, 244, 120), r.center, 12)
                pygame.draw.circle(screen, (117, 91, 16), r.center, 12, 2)
            elif tile == "C":
                pygame.draw.rect(screen, COLORS["R"], r)
                pygame.draw.rect(screen, (145, 61, 174), r.inflate(-4, -4), border_radius=3)
                pygame.draw.rect(screen, (223, 170, 244), r.inflate(-10, -10), border_radius=2)
            elif tile == "D":
                pygame.draw.rect(screen, COLORS["R"], r)
                pygame.draw.rect(screen, (244, 68, 72), r.inflate(-10, -8), border_radius=5)
                pygame.draw.rect(screen, (104, 18, 22), r.inflate(-10, -8), 2, border_radius=5)
            else:
                color = COLORS.get(tile, (200, 200, 200))
                pygame.draw.rect(screen, color, r)
                pygame.draw.rect(screen, (47, 49, 50), r, 1)
    draw_jingfeng_canteen_overlay()
    draw_student_activity_center_overlay()
    draw_aerospace_building_overlay()
    draw_furong_canteen_overlay()
    draw_pharmacy_school_overlay()
    draw_fengting_canteen_overlay()
    draw_express_center_overlay()
    draw_duxing_dorm_overlay()
    draw_third_map_dorms_overlay()
    draw_dewang_library_overlay()
    draw_fourth_map_side_buildings_overlay()



def draw_marker(pos, color, title, subtitle=None, show_label=True):
    cx, cy = tile_center(pos)
    p = pulse()
    radius = int(21 + p * 12)
    pygame.draw.circle(screen, color, (int(cx), int(cy)), radius, 4)
    pygame.draw.circle(screen, (255, 255, 255), (int(cx), int(cy)), 11)
    pygame.draw.circle(screen, color, (int(cx), int(cy)), 7)
    for extra in (8, 16):
        alpha = max(35, int(120 * (1 - p)))
        ring = pygame.Surface((radius * 2 + extra * 2, radius * 2 + extra * 2), pygame.SRCALPHA)
        pygame.draw.circle(ring, (*color, alpha), (ring.get_width() // 2, ring.get_height() // 2), radius + extra, 2)
        screen.blit(ring, ring.get_rect(center=(cx, cy)))

    if not show_label:
        return

    box_w = max(118, min(170, len(subtitle or title) * 15 + 44))
    box = pygame.Rect(cx - box_w / 2, cy - 66, box_w, 46)
    pygame.draw.rect(screen, (30, 36, 43), box, border_radius=8)
    pygame.draw.rect(screen, color, box, 2, border_radius=8)
    center_text(title, box.centerx, box.y + 14, (255, 255, 255), FONT_SMALL)
    center_text(subtitle or "", box.centerx, box.y + 32, (255, 241, 166), FONT_MINI)

def draw_guide():
    target_tile, color = target_tile_for_guide()
    if not target_tile:
        return
    target = tile_center(target_tile)
    start = (player["x"], player["y"])
    total = dist(start, target)
    if total < 20:
        return
    pieces = max(8, int(total // 24))
    for i in range(pieces):
        if i % 2 == 0:
            a = i / pieces
            b = min(1, (i + 0.55) / pieces)
            p1 = (start[0] + (target[0] - start[0]) * a, start[1] + (target[1] - start[1]) * a)
            p2 = (start[0] + (target[0] - start[0]) * b, start[1] + (target[1] - start[1]) * b)
            pygame.draw.line(screen, color, p1, p2, 4)



def current_player_animation_name():
    if player["state"] in {"hurt", "die"}:
        return player["state"]
    return "run" if player["moving"] else "idle"


def draw_player():
    x, y = int(player["x"]), int(player["y"])
    pygame.draw.ellipse(screen, (20, 23, 24), (x - 18, y + 14, 36, 12))
    animation_name = current_player_animation_name()
    frames = PLAYER_ANIMATIONS.get(animation_name, [])

    if frames:
        elapsed = max(0, time.time() - player["state_started"])
        if animation_name in {"hurt", "die"}:
            frame_index = min(len(frames) - 1, int(elapsed * PLAYER_ANIMATION_FPS))
        else:
            frame_index = int(time.time() * PLAYER_ANIMATION_FPS) % len(frames)
        image = frames[frame_index]
        if player.get("flip", False):
            image = pygame.transform.flip(image, True, False)
        screen.blit(image, image.get_rect(center=(x, y - 10)))
    else:
        hurt = time.time() - last_hit_time < 0.18
        pygame.draw.circle(screen, (38, 29, 28), (x + 3, y + 5), 18)
        pygame.draw.circle(screen, (245, 80, 87) if not hurt else (255, 232, 232), (x, y), 16)
        pygame.draw.circle(screen, (255, 223, 187), (x, y - 8), 7)
        pygame.draw.rect(screen, (44, 48, 53), (x - 10, y - 2, 20, 5), border_radius=2)

def draw_entities():
    for z in zombies:
        x, y = int(z["x"]), int(z["y"])
        pygame.draw.ellipse(screen, (20, 26, 21), (x - 18, y + 13, 36, 12))
        if ZOMBIE_FRAMES:
            frame_index = int((time.time() + z["frame_offset"]) * ZOMBIE_ANIMATION_FPS) % len(ZOMBIE_FRAMES)
            image = ZOMBIE_FRAMES[frame_index]
            if z.get("flip", False):
                image = pygame.transform.flip(image, True, False)
            screen.blit(image, image.get_rect(center=(x, y - 4)))
        else:
            pygame.draw.circle(screen, (24, 40, 29), (x + 3, y + 5), 17)
            pygame.draw.circle(screen, (80, 166, 94), (x, y), 15)
            pygame.draw.circle(screen, (22, 56, 35), (x - 5, y - 5), 3)
            pygame.draw.circle(screen, (22, 56, 35), (x + 5, y - 5), 3)
            pygame.draw.line(screen, (24, 67, 40), (x - 6, y + 5), (x + 6, y + 5), 2)
        if z["chasing"]:
            center_text("!", x, y - 31, (255, 79, 79), FONT_BOLD)

    draw_player()


def draw_weather():
    if weather == "rain":
        for _ in range(42):
            x = random.randrange(0, WIDTH)
            y = random.randrange(HUD, HEIGHT)
            pygame.draw.line(screen, (136, 186, 225), (x, y), (x - 7, y + 13), 1)
    elif weather == "typhoon":
        for y in range(HUD + 30, HEIGHT, 72):
            shift = int(math.sin(time.time() * 4 + y) * 24)
            pygame.draw.arc(screen, (230, 234, 218), (shift - 25, y, 190, 28), 0.1, 2.8, 2)
    elif weather == "fog":
        fog = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        fog.fill((17, 21, 25, 176))
        pygame.draw.circle(fog, (0, 0, 0, 0), (int(player["x"]), int(player["y"])), TILE * 3)
        screen.blit(fog, (0, 0))


def format_seconds(seconds):
    seconds = max(0, int(seconds))
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


def draw_soft_panel(rect, fill, border, glow=None):
    if glow:
        for i, alpha in enumerate((55, 30, 16)):
            surface = pygame.Surface((rect.w + i * 10, rect.h + i * 10), pygame.SRCALPHA)
            pygame.draw.rect(surface, (*glow, alpha), surface.get_rect(), border_radius=10)
            screen.blit(surface, surface.get_rect(center=rect.center))
    pygame.draw.rect(screen, (7, 10, 15), rect.move(0, 5), border_radius=8)
    pygame.draw.rect(screen, fill, rect, border_radius=8)
    pygame.draw.rect(screen, border, rect, 2, border_radius=8)
    pygame.draw.line(screen, (255, 255, 255, 42), (rect.x + 10, rect.y + 6), (rect.right - 12, rect.y + 6), 1)


def draw_glow_line(x1, y, x2, color):
    pygame.draw.line(screen, (*color,), (x1, y), (x2, y), 2)
    pygame.draw.line(screen, (255, 255, 255), (x1, y - 1), (x1 + 28, y - 1), 1)


def draw_arcade_hearts(x, y):
    for i in range(3):
        ox = x + i * 34
        active = i < player["hp"]
        color = (255, 77, 101) if active else (64, 72, 84)
        shade = (132, 28, 45) if active else (30, 36, 44)
        pts = [(ox+8,y),(ox+14,y),(ox+18,y+5),(ox+22,y),(ox+28,y),(ox+34,y+7),(ox+34,y+16),(ox+21,y+30),(ox+17,y+34),(ox+13,y+30),(ox,y+16),(ox,y+7)]
        pygame.draw.polygon(screen, shade, [(px+2, py+3) for px, py in pts])
        pygame.draw.polygon(screen, color, pts)
        pygame.draw.polygon(screen, (255, 164, 174) if active else (91, 101, 114), [(ox+8,y+4),(ox+14,y+4),(ox+16,y+8),(ox+6,y+12),(ox+5,y+8)])


def draw_minimal_key(label, x, y, w):
    rect = pygame.Rect(x, y, w, 24)
    pygame.draw.rect(screen, (12, 17, 23), rect, border_radius=5)
    pygame.draw.rect(screen, (100, 118, 135), rect, 1, border_radius=5)
    center_text(label, rect.centerx, rect.centery - 1, (230, 237, 241), FONT_MINI)


def draw_task_meter(rect, ratio, color):
    ratio = max(0, min(1, ratio))
    pygame.draw.rect(screen, (9, 12, 17), rect, border_radius=7)
    pygame.draw.rect(screen, (59, 67, 77), rect, 1, border_radius=7)
    inner = rect.inflate(-5, -5)
    fill = pygame.Rect(inner.x, inner.y, int(inner.w * ratio), inner.h)
    if fill.w > 0:
        pygame.draw.rect(screen, color, fill, border_radius=5)
        shine = pygame.Surface((fill.w, fill.h), pygame.SRCALPHA)
        pygame.draw.rect(shine, (255, 255, 255, 42), (0, 0, fill.w, max(2, fill.h // 3)), border_radius=5)
        screen.blit(shine, fill)


def draw_portrait_chip(rect):
    draw_soft_panel(rect, (27, 34, 42), (244, 176, 78), (244, 176, 78))
    inner = rect.inflate(-10, -10)
    pygame.draw.rect(screen, (13, 17, 22), inner, border_radius=7)
    frames = PLAYER_ANIMATIONS.get("idle", [])
    if frames:
        image = pygame.transform.scale(frames[int(time.time() * 4) % len(frames)], (66, 66))
        screen.blit(image, image.get_rect(center=(inner.centerx, inner.centery + 4)))


def draw_hud():
    pygame.draw.rect(screen, (8, 11, 16), (0, 0, WIDTH, HUD))
    top = pygame.Surface((WIDTH, HUD), pygame.SRCALPHA)
    pygame.draw.rect(top, (18, 26, 35, 245), (0, 0, WIDTH, HUD - 10), border_radius=0)
    pygame.draw.polygon(top, (30, 43, 55, 230), [(0, 0), (WIDTH, 0), (WIDTH, 34), (0, 78)])
    pygame.draw.polygon(top, (31, 21, 31, 155), [(390, 0), (WIDTH, 0), (WIDTH, HUD - 10), (520, HUD - 10)])
    screen.blit(top, (0, 0))
    draw_glow_line(0, HUD - 10, WIDTH, (255, 173, 76))
    pygame.draw.rect(screen, (5, 7, 10), (0, HUD - 8, WIDTH, 8))

    portrait = pygame.Rect(20, 20, 92, 82)
    draw_portrait_chip(portrait)

    elapsed = time.time() - game_started_at
    text("重生之我在末日厦大送外卖", 130, 22, (255, 222, 122), FONT_TITLE)
    text("XMU EMERGENCY DELIVERY", 132, 54, (116, 144, 163), FONT_MINI)
    text(f"时间  {format_seconds(elapsed)}", 132, 78, (169, 224, 255), FONT_SMALL)
    text(f"分数  {score}", 258, 78, (255, 236, 160), FONT_SMALL)
    text(f"救援  {rescued}/{rescued + failed}", 360, 78, (150, 224, 174), FONT_SMALL)

    task_rect = pygame.Rect(514, 20, 430, 82)
    draw_soft_panel(task_rect, (32, 29, 38), (214, 139, 80), (214, 139, 80))
    if carrying_order:
        remain = max(0, ORDER_LIMIT - (time.time() - order_start))
        ratio = remain / ORDER_LIMIT
        title = "正在配送"
        target = f"{map_name(target_dorm_map)} / {dorm_name(target_dorm_map, target_dorm)}"
        meter_color = (255, 213, 83) if ratio > 0.35 else (239, 83, 91)
        status = f"{int(remain)} 秒"
    else:
        ratio = 1
        title = "等待取餐"
        target = f"{map_name(active_pickup_map)} / {pickup_name(active_pickup_map, active_pickup)}"
        meter_color = (255, 151, 69)
        status = "READY"
    text(title, task_rect.x + 22, task_rect.y + 14, (255, 192, 101), FONT_BOLD)
    text(target, task_rect.x + 132, task_rect.y + 15, (250, 242, 224), FONT)
    draw_task_meter(pygame.Rect(task_rect.x + 22, task_rect.y + 50, 290, 20), ratio, meter_color)
    text(status, task_rect.x + 326, task_rect.y + 48, (255, 233, 156), FONT_BOLD)

    right = pygame.Rect(WIDTH - 350, 20, 330, 82)
    draw_soft_panel(right, (23, 32, 41), (101, 184, 159), (101, 184, 159))
    text("生命", right.x + 20, right.y + 12, (255, 229, 143), FONT_SMALL)
    draw_arcade_hearts(right.x + 78, right.y + 8)
    text(f"天气  {WEATHER_TEXT[weather]}", right.x + 20, right.y + 50, (194, 225, 238), FONT_SMALL)
    draw_minimal_key("WASD", right.x + 204, right.y + 48, 50)
    draw_minimal_key("E/空格", right.x + 260, right.y + 48, 60)

    if message and time.time() < message_until:
        msg = FONT_SMALL.render(message, True, (255, 235, 139))
        msg_rect = msg.get_rect(center=(WIDTH // 2, HUD - 19))
        bubble = msg_rect.inflate(26, 10)
        pygame.draw.rect(screen, (12, 15, 20), bubble, border_radius=6)
        pygame.draw.rect(screen, (221, 164, 74), bubble, 1, border_radius=6)
        screen.blit(msg, msg_rect)

def draw_prompts():
    for connection_tile, (target_map, _) in CONNECTIONS.get(current_map_id, {}).items():
        draw_marker(connection_tile, (87, 190, 255), "\u8fde\u63a5\u53e3", map_name(target_map), show_label=False)

    if carrying_order:
        if target_dorm_map == current_map_id:
            draw_marker(target_dorm, (255, 218, 61), "\u9001\u8fbe\u70b9", dorm_name(target_dorm_map, target_dorm))
            if distance_to_tile(target_dorm) < TILE * 1.25:
                center_text("\u6309 E / \u7a7a\u683c \u9001\u8fbe\u5916\u5356", WIDTH // 2, HUD + 28, (255, 244, 168), FONT_BOLD)
        else:
            connection_tile = nearest_connection_to(target_dorm_map)
            if connection_tile:
                draw_marker(connection_tile, (87, 190, 255), "\u53bb\u4e0b\u4e00\u5f20\u5730\u56fe", map_name(target_dorm_map))
    else:
        if active_pickup_map == current_map_id:
            draw_marker(active_pickup, (255, 156, 58), "\u53d6\u5916\u5356", pickup_name(active_pickup_map, active_pickup), show_label=False)
            if distance_to_tile(active_pickup) < TILE * 1.25:
                center_text("\u6309 E / \u7a7a\u683c \u63a5\u5916\u5356", WIDTH // 2, HUD + 28, (255, 224, 168), FONT_BOLD)
        else:
            connection_tile = nearest_connection_to(active_pickup_map)
            if connection_tile:
                draw_marker(connection_tile, (87, 190, 255), "\u53bb\u53d6\u9910\u5730\u56fe", map_name(active_pickup_map))



def draw_game_over():
    layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    layer.fill((0, 0, 0, 182))
    screen.blit(layer, (0, 0))
    panel = pygame.Rect(WIDTH // 2 - 240, HEIGHT // 2 - 120, 480, 230)
    pygame.draw.rect(screen, (34, 41, 49), panel, border_radius=12)
    pygame.draw.rect(screen, (255, 218, 83), panel, 2, border_radius=12)
    center_text("game over!", WIDTH // 2, panel.y + 52, (255, 255, 255), FONT_BIG)
    center_text(f"最终分数：{score}    救下同学：{rescued}", WIDTH // 2, panel.y + 115, (255, 230, 132), FONT)
    center_text("按空格 / R 重新开始，按 ESC 退出", WIDTH // 2, panel.y + 166, (230, 235, 238), FONT_SMALL)


def reset_game():
    global score, rescued, failed, carrying_order, target_dorm, target_dorm_map, order_start, weather, weather_until
    global message, message_until, game_over, last_hit_time, pressed_keys, game_started_at
    score = 0
    rescued = 0
    failed = 0
    carrying_order = False
    target_dorm = None
    target_dorm_map = None
    order_start = 0
    weather = "normal"
    weather_until = 0
    game_over = False
    game_started_at = time.time()
    last_hit_time = -10
    pressed_keys = set()
    transition["active"] = False
    switch_map(0, START_TILE)
    player["hp"] = 3
    player["locked_until"] = 0
    player["invulnerable_until"] = time.time() + 1.2
    refresh_pickup()
    set_message("????????????????? E ??????", 5)


def draw_transition_overlay():
    if not transition["active"]:
        return
    elapsed = time.time() - transition["started"]
    if elapsed < 0.22:
        alpha = int(255 * (elapsed / 0.22))
    elif elapsed < 0.36:
        alpha = 255
    else:
        alpha = int(255 * max(0, 1 - (elapsed - 0.36) / 0.22))
    layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    layer.fill((0, 0, 0, max(0, min(255, alpha))))
    screen.blit(layer, (0, 0))


running = True
while running:
    dt = min(clock.tick(FPS) / 1000, 0.04)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            pressed_keys.add(event.key)
            if event.key == pygame.K_ESCAPE:
                running = False
            elif game_over and event.key in (pygame.K_r, pygame.K_SPACE):
                reset_game()
            elif event.key in (pygame.K_e, pygame.K_SPACE):
                interact()
        elif event.type == pygame.KEYUP:
            pressed_keys.discard(event.key)
        elif event.type == pygame.WINDOWFOCUSLOST:
            pressed_keys.clear()

    if not game_over:
        update_player_state()
        if transition["active"]:
            update_transition()
        elif player["state"] not in {"hurt", "die"}:
            update_player(dt)
            check_map_connection()
            update_zombies(dt)
            update_weather()
            check_state()

    draw_map()
    draw_area_labels()
    draw_guide()
    draw_prompts()
    draw_weather()
    draw_entities()
    draw_hud()
    if game_over:
        draw_game_over()
    draw_transition_overlay()
    pygame.display.flip()

pygame.quit()

