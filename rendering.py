# rendering.py 负责所有“画到屏幕上”的内容。
# main.py 管游戏规则和状态，rendering.py 管地图、建筑、角色、天气、HUD 和结束界面的绘制。
# 本文件通过 main.py 的 exec 加载，所以可以直接使用 screen、player、GAME_MAP 等全局变量。

# 基础文字绘制函数：一个按左上角画，一个按中心点画。
import math
import time
from pathlib import Path
import pygame

from assets import FONT, FONT_BOLD, FONT_TITLE, FONT_SMALL, FONT_MINI, FONT_BIG
from config import HUD, TILE
from maps import MAP_DATA

START_BG_IMAGE = None
START_INTRO_LINES = None
START_SCREEN_STARTED = time.time()


def text(s, x, y, color=(255, 255, 255), f=None):
    img = (f or FONT).render(s, True, color)
    screen.blit(img, (x, y))
    return img


def center_text(s, cx, cy, color=(255, 255, 255), f=None):
    img = (f or FONT).render(s, True, color)
    screen.blit(img, img.get_rect(center=(cx, cy)))
    return img


# 绘制地图上的地点名称，并限制文字不要超出屏幕边缘。
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



# pulse 用来生成 0 到 1 之间循环变化的数值，常用于光圈闪烁。
def pulse(speed=4):
    return (math.sin(time.time() * speed) + 1) / 2


# 给每个格子生成稳定的“伪随机数”，让地砖细节有变化但不会每帧乱跳。
def tile_seed(x, y):
    return (x * 37 + y * 53 + 17) % 100


HORROR_GREEN = (82, 255, 134)
HORROR_GREEN_DARK = (16, 81, 55)
HORROR_RED = (232, 43, 47)
HORROR_INK = (9, 16, 16)
HORROR_MAP_IDS = {0, 1, 2, 3}


# ===== 基础地形绘制 =====
# 下面几个函数负责道路、操场、足球场、篮球场、草地和湖面的像素风表现。
def draw_road_tile(r, x, y):
    if current_map_id in HORROR_MAP_IDS:
        base = (42, 53, 49) if (x + y) % 2 else (47, 58, 54)
        pygame.draw.rect(screen, base, r)
        pygame.draw.rect(screen, (18, 26, 25), r, 1)
        if tile_seed(x, y) % 2 == 0:
            pygame.draw.rect(screen, (66, 78, 71), (r.x + 4, r.y + 6, 12, 3))
        if tile_seed(x, y) % 3 == 0:
            pygame.draw.rect(screen, (24, 35, 31), (r.x + 18, r.y + 21, 10, 2))
        if tile_seed(x, y) % 7 == 0:
            pygame.draw.rect(screen, (36, 130, 76), (r.x + 8, r.y + 25, 15, 2))
        return
    pygame.draw.rect(screen, (172, 171, 166), r)
    pygame.draw.rect(screen, (135, 136, 132), r, 1)
    if tile_seed(x, y) % 3 == 0:
        pygame.draw.rect(screen, (189, 188, 181), (r.x + 5, r.y + 6, 9, 3))
    if tile_seed(x, y) % 4 == 0:
        pygame.draw.rect(screen, (148, 149, 144), (r.x + 18, r.y + 22, 8, 2))


def draw_track_playground_tile(r, x, y):
    rel_x = x - 18
    rel_y = y - 1
    if current_map_id == 0:
        pygame.draw.rect(screen, (63, 35, 35), r)
        pygame.draw.rect(screen, (24, 20, 20), r, 1)
        if 2 <= rel_x <= 10 and 1 <= rel_y <= 5:
            stripe = (23, 81, 55) if (rel_y + rel_x // 2) % 2 == 0 else (30, 103, 66)
            pygame.draw.rect(screen, stripe, r.inflate(-2, -2))
            if tile_seed(x, y) % 4 == 0:
                pygame.draw.rect(screen, (70, 255, 128), (r.x + 6, r.y + 8, 12, 2))
        else:
            for offset in (7, 15, 23):
                pygame.draw.line(screen, (123, 65, 58), (r.x + 2, r.y + offset), (r.right - 2, r.y + offset), 1)
        if rel_x == 9 and rel_y == 4:
            pygame.draw.rect(screen, (157, 205, 176), (r.x + 5, r.y + 9, 21, 13), 2)
        return
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
    if current_map_id == 0:
        stripe = (32, 83, 55) if rel_x % 2 == 0 else (25, 69, 50)
        pygame.draw.rect(screen, stripe, r)
        pygame.draw.rect(screen, (12, 31, 28), r, 1)
        if rel_y in {0, 4} or rel_x in {0, 2}:
            pygame.draw.line(screen, (134, 196, 154), (r.x + 3, r.centery), (r.right - 3, r.centery), 1)
        if rel_x == 1 and rel_y == 2:
            pygame.draw.circle(screen, (134, 196, 154), r.center, 9, 1)
        return
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
    if current_map_id == 0:
        pygame.draw.rect(screen, (87, 57, 47), r)
        pygame.draw.rect(screen, (33, 24, 23), r, 1)
        for yy in (8, 20):
            pygame.draw.line(screen, (122, 85, 67), (r.x + 4, r.y + yy), (r.right - 4, r.y + yy), 1)
        line = (151, 197, 157)
        if rel_y in {0, 3}:
            pygame.draw.line(screen, line, (r.x + 3, r.centery), (r.right - 3, r.centery), 1)
        if rel_x in {0, 5}:
            pygame.draw.line(screen, line, (r.centerx, r.y + 3), (r.centerx, r.bottom - 3), 1)
        if rel_x in {0, 5} and rel_y in {1, 2}:
            hoop_x = r.x + 7 if rel_x == 0 else r.right - 7
            pygame.draw.rect(screen, (22, 25, 23), (hoop_x - 3, r.centery - 8, 6, 16))
            pygame.draw.circle(screen, HORROR_RED, (hoop_x, r.centery), 5, 2)
        return
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
    if current_map_id in HORROR_MAP_IDS:
        palettes = {
            "S": ((24, 73, 49), (48, 122, 66)),
            "P": ((27, 83, 54), (62, 139, 76)),
            "F": ((31, 86, 57), (94, 151, 91)),
            "K": ((83, 57, 47), (134, 76, 58)),
        }
        base, detail = palettes.get(tile, ((24, 73, 49), (48, 122, 66)))
        pygame.draw.rect(screen, base, r)
        pygame.draw.rect(screen, (10, 26, 24), r, 1)
        if tile in {"S", "P", "F"}:
            for i in range(2):
                ox = (tile_seed(x + i, y) * 7) % 22 + 4
                oy = (tile_seed(x, y + i) * 5) % 20 + 6
                pygame.draw.line(screen, detail, (r.x + ox, r.y + oy), (r.x + ox + 3, r.y + oy - 5), 2)
            if tile_seed(x, y) % 6 == 0:
                pygame.draw.rect(screen, HORROR_GREEN, (r.x + 6, r.y + 24, 14, 2))
        else:
            pygame.draw.line(screen, detail, (r.x + 4, r.y + 9), (r.right - 4, r.y + 9), 1)
            pygame.draw.line(screen, (38, 28, 27), (r.x + 4, r.y + 21), (r.right - 4, r.y + 21), 1)
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

# 判断某个障碍格是否属于航空航天学院建筑，用于替换成专门的建筑外观。
def is_aerospace_building_tile(x, y):
    return current_map_id == 1 and 17 <= x <= 24 and 8 <= y <= 13 and tile_at(x, y) == "B"


# ===== 重点建筑叠加绘制 =====
# 这些 overlay 函数会在基础格子画完后再覆盖一层更精细的建筑外观。
# 好处是地图逻辑仍然按格子判断碰撞，视觉上可以做出更丰富的伪 3D 效果。
def draw_jingfeng_canteen_overlay():
    if current_map_id != 0:
        return
    base = pygame.Rect(14 * TILE, HUD + 9 * TILE, 3 * TILE, 2 * TILE)
    shadow = pygame.Surface((base.w + 26, base.h + 38), pygame.SRCALPHA)
    pygame.draw.polygon(shadow, (0, 0, 0, 70), [(12, 22), (base.w + 22, 10), (base.w + 18, base.h + 34), (4, base.h + 36)])
    screen.blit(shadow, (base.x - 12, base.y - 12))

    body = pygame.Rect(base.x - 8, base.y + 8, base.w + 26, base.h + 38)
    pygame.draw.rect(screen, (76, 70, 62), body)
    pygame.draw.rect(screen, HORROR_INK, body, 2)
    for yy in range(body.y + 8, body.bottom - 4, 9):
        pygame.draw.line(screen, (112, 103, 88), (body.x + 5, yy), (body.right - 6, yy), 1)

    glass = pygame.Rect(body.x + 44, body.y + 12, body.w - 58, body.h - 20)
    pygame.draw.rect(screen, (20, 84, 54), glass)
    for gx in range(glass.x + 8, glass.right - 5, 15):
        pygame.draw.line(screen, (8, 34, 29), (gx, glass.y + 2), (gx, glass.bottom - 2), 1)
    for gy in range(glass.y + 10, glass.bottom - 2, 13):
        pygame.draw.line(screen, HORROR_GREEN, (glass.x + 2, gy), (glass.right - 2, gy), 2)
    pygame.draw.rect(screen, HORROR_GREEN_DARK, glass, 2)

    roof = [(body.x - 6, body.y - 8), (body.right + 8, body.y - 8), (body.right, body.y + 8), (body.x - 14, body.y + 8)]
    pygame.draw.polygon(screen, (81, 78, 70), [(x, y + 6) for x, y in roof])
    pygame.draw.polygon(screen, (107, 110, 96), roof)
    pygame.draw.line(screen, (18, 23, 22), roof[0], roof[1], 2)

    door = pygame.Rect(body.x + 17, body.bottom - 28, 21, 28)
    pygame.draw.rect(screen, (8, 14, 15), door)
    pygame.draw.line(screen, HORROR_GREEN, (door.centerx, door.y + 3), (door.centerx, door.bottom - 3), 1)
    pygame.draw.rect(screen, (25, 30, 27), (body.x + 8, body.y + 15, 24, 7))
    pygame.draw.rect(screen, HORROR_RED, (body.x + 10, body.y + 16, 20, 4))


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
        pygame.draw.rect(screen, (75, 87, 82), rect)
        pygame.draw.rect(screen, (17, 25, 24), rect, 2)
        pygame.draw.rect(screen, (18, 91, 58), (rect.x + 8, rect.y + 15, rect.w - 16, 22))
        for gx in range(rect.x + 17, rect.right - 12, 22):
            pygame.draw.line(screen, (8, 34, 30), (gx, rect.y + 15), (gx, rect.y + 37), 1)
        pygame.draw.line(screen, HORROR_GREEN, (rect.x + 10, rect.y + 19), (rect.right - 12, rect.y + 19), 2)
        pygame.draw.rect(screen, (40, 51, 48), (rect.x, rect.bottom - 12, rect.w, 12))

    pygame.draw.rect(screen, (58, 69, 65), bridge)
    pygame.draw.rect(screen, (19, 90, 58), (bridge.x + 8, bridge.y + 6, bridge.w - 16, 15))
    pygame.draw.rect(screen, (15, 22, 22), bridge, 2)

    pygame.draw.rect(screen, (86, 94, 85), tower)
    pygame.draw.rect(screen, (17, 25, 24), tower, 2)
    pygame.draw.polygon(screen, (118, 123, 105), [(tower.x - 6, tower.y + 20), (tower.centerx, tower.y - 16), (tower.right + 8, tower.y + 20)])
    pygame.draw.line(screen, (22, 29, 27), (tower.x - 6, tower.y + 20), (tower.centerx, tower.y - 16), 2)
    pygame.draw.line(screen, (22, 29, 27), (tower.centerx, tower.y - 16), (tower.right + 8, tower.y + 20), 2)
    pygame.draw.rect(screen, (19, 91, 58), (tower.x + 13, tower.y + 38, 28, 48))
    for gy in range(tower.y + 48, tower.y + 84, 12):
        pygame.draw.line(screen, HORROR_GREEN, (tower.x + 15, gy), (tower.x + 39, gy), 1)
    pygame.draw.rect(screen, HORROR_GREEN_DARK, (tower.x + 13, tower.y + 38, 28, 48), 2)

    for tx in (base.x + 20, base.x + 304):
        pygame.draw.rect(screen, (96, 72, 48), (tx, base.bottom - 20, 5, 20))
        for ox, oy in [(-10, -7), (-4, -13), (6, -12), (12, -5)]:
            pygame.draw.circle(screen, (19, 62, 37), (tx + ox, base.bottom - 22 + oy), 9)
            pygame.draw.circle(screen, (38, 112, 61), (tx + ox + 2, base.bottom - 25 + oy), 5)


def draw_aerospace_building_overlay():
    if current_map_id != 1:
        return

    # 固定覆盖航院 8x6 建筑区：x=17..24, y=8..13。用独立画布避免细节超出道路。
    base = pygame.Rect(17 * TILE, HUD + 8 * TILE, 8 * TILE, 6 * TILE)
    art = pygame.Surface((base.w, base.h), pygame.SRCALPHA)

    brick = (176, 76, 50)
    brick_dark = (116, 47, 38)
    brick_line = (217, 115, 76)
    cream = (238, 228, 194)
    cream_shadow = (181, 166, 132)
    glass = (34, 92, 154)
    glass_dark = (17, 47, 87)
    glass_light = (119, 187, 238)
    roof = (239, 229, 199)
    roof_shadow = (169, 151, 116)

    # 不铺满矩形背景；画布保持透明，只绘制建筑物本身。

    # 三段式对称主体：左右翼楼 + 中央玻璃大厅。
    left = pygame.Rect(4, 58, 82, 120)
    mid = pygame.Rect(86, 34, 84, 144)
    right = pygame.Rect(170, 58, 82, 120)

    def draw_wing(rect, mirror=False):
        pygame.draw.rect(art, brick, rect)
        pygame.draw.rect(art, brick_dark, rect, 2)
        pygame.draw.rect(art, cream, (rect.x - 2, rect.y - 10, rect.w + 4, 12))
        pygame.draw.rect(art, cream_shadow, (rect.x - 2, rect.y + 2, rect.w + 4, 4))
        pygame.draw.rect(art, cream, (rect.x, rect.bottom - 16, rect.w, 11))

        # 图中左右翼楼有成排蓝色窗格和竖向浅色柱。
        for x in (rect.x + 7, rect.x + 33, rect.x + 59):
            pygame.draw.rect(art, cream, (x, rect.y + 8, 6, rect.h - 25))
            pygame.draw.rect(art, cream_shadow, (x + 5, rect.y + 9, 2, rect.h - 27))
        for row in range(4):
            wy = rect.y + 16 + row * 23
            for col in range(3):
                wx = rect.x + 12 + col * 23
                if col == 1:
                    wx += 2
                pygame.draw.rect(art, glass, (wx, wy, 17, 13))
                pygame.draw.line(art, glass_light, (wx + 2, wy + 3), (wx + 15, wy + 3), 1)
                pygame.draw.rect(art, glass_dark, (wx, wy, 17, 13), 1)

        # 左右翼楼顶部的小三角山墙，保持对称。
        gable = [(rect.centerx - 26, rect.y - 10), (rect.centerx, rect.y - 28), (rect.centerx + 26, rect.y - 10)]
        pygame.draw.polygon(art, roof_shadow, [(x, y + 4) for x, y in gable])
        pygame.draw.polygon(art, roof, gable)
        pygame.draw.line(art, (129, 111, 86), gable[0], gable[1], 2)
        pygame.draw.line(art, (129, 111, 86), gable[1], gable[2], 2)
        for yy in range(gable[1][1] + 9, gable[0][1] - 2, 6):
            pygame.draw.line(art, (192, 178, 145), (rect.centerx - 16, yy), (rect.centerx + 16, yy), 1)

    draw_wing(left)
    draw_wing(right, True)

    # 中央高大厅：大面积蓝色玻璃 + 顶部大三角山墙。
    pygame.draw.rect(art, cream_shadow, mid.move(0, 4))
    pygame.draw.rect(art, cream, mid)
    glass_rect = pygame.Rect(mid.x + 11, mid.y + 44, mid.w - 22, mid.h - 53)
    pygame.draw.rect(art, glass, glass_rect)
    for x in range(glass_rect.x + 10, glass_rect.right, 11):
        pygame.draw.line(art, glass_dark, (x, glass_rect.y), (x, glass_rect.bottom), 1)
    for y in range(glass_rect.y + 10, glass_rect.bottom, 12):
        pygame.draw.line(art, glass_light, (glass_rect.x + 2, y), (glass_rect.right - 2, y), 1)
    pygame.draw.rect(art, glass_dark, glass_rect, 2)

    main_roof = [(mid.x - 15, mid.y + 35), (mid.centerx, mid.y - 24), (mid.right + 15, mid.y + 35)]
    pygame.draw.polygon(art, roof_shadow, [(x, y + 7) for x, y in main_roof])
    pygame.draw.polygon(art, roof, main_roof)
    pygame.draw.line(art, (124, 105, 82), main_roof[0], main_roof[1], 3)
    pygame.draw.line(art, (124, 105, 82), main_roof[1], main_roof[2], 3)
    for step in range(7):
        yy = mid.y - 12 + step * 8
        x_pad = 22 - step * 2
        pygame.draw.line(art, (190, 176, 143), (mid.x + x_pad, yy), (mid.right - x_pad, yy), 1)
    pygame.draw.rect(art, cream, (mid.x - 12, mid.y + 31, mid.w + 24, 16))
    pygame.draw.rect(art, cream_shadow, (mid.x - 12, mid.y + 45, mid.w + 24, 4))

    # 圆形校徽位置和拱形正门，对应参考图中央门厅。
    pygame.draw.circle(art, (218, 213, 196), (mid.centerx, mid.y + 50), 12)
    pygame.draw.circle(art, (62, 99, 149), (mid.centerx, mid.y + 50), 8)
    arch = pygame.Rect(mid.centerx - 27, mid.bottom - 58, 54, 55)
    pygame.draw.arc(art, cream, arch, math.pi, 2 * math.pi, 8)
    pygame.draw.rect(art, cream, (arch.x - 2, arch.centery, arch.w + 4, 35))
    inner = pygame.Rect(mid.centerx - 19, mid.bottom - 44, 38, 41)
    pygame.draw.arc(art, glass_dark, inner, math.pi, 2 * math.pi, 4)
    pygame.draw.rect(art, glass, (inner.x, inner.centery, inner.w, 25))
    pygame.draw.line(art, glass_light, (inner.centerx, inner.y + 9), (inner.centerx, inner.bottom - 4), 1)

    # 前方低矮绿化只放在建筑画布底部，不伸出 8x6 范围。
    for x in range(12, base.w - 10, 34):
        pygame.draw.rect(art, (80, 83, 56), (x + 4, base.h - 23, 4, 18))
        pygame.draw.circle(art, (58, 128, 61), (x, base.h - 23), 8)
        pygame.draw.circle(art, (93, 168, 73), (x + 9, base.h - 25), 7)
    pygame.draw.rect(art, (94, 84, 76), (mid.centerx - 16, base.h - 13, 32, 10))

    screen.blit(art, base)


def draw_swimming_pool_overlay():
    if current_map_id != 1:
        return

    base = pygame.Rect(3 * TILE + 2, HUD + 2 * TILE + 2, 7 * TILE - 4, 3 * TILE - 4)
    shadow = pygame.Surface((base.w + 40, base.h + 36), pygame.SRCALPHA)
    pygame.draw.polygon(shadow, (0, 0, 0, 60), [(16, 24), (base.w + 34, 11), (base.w + 29, base.h + 29), (5, base.h + 33)])
    screen.blit(shadow, (base.x - 15, base.y - 14))

    brick = (145, 58, 48)
    brick_light = (177, 74, 58)
    roof = (232, 234, 226)
    roof_shadow = (177, 181, 178)
    trim = (228, 225, 211)
    glass = (48, 89, 113)
    glass_hi = (157, 210, 230)
    dark = (31, 43, 50)

    body = pygame.Rect(base.x + 1, base.y + 28, base.w - 2, base.h - 24)
    pygame.draw.rect(screen, (96, 50, 45), body.move(0, 4))
    pygame.draw.rect(screen, brick, body)
    pygame.draw.rect(screen, brick_light, (body.x + 4, body.y + 5, body.w - 8, body.h - 11))

    roof_rect = pygame.Rect(base.x - 10, base.y + 6, base.w + 20, 30)
    pygame.draw.ellipse(screen, roof_shadow, roof_rect.move(0, 5))
    pygame.draw.ellipse(screen, roof, roof_rect)
    pygame.draw.rect(screen, roof, (roof_rect.x, roof_rect.centery - 1, roof_rect.w, roof_rect.h // 2 + 2))
    for x in range(roof_rect.x + 15, roof_rect.right - 10, 18):
        pygame.draw.line(screen, (197, 201, 199), (x, roof_rect.y + 3), (x + 5, roof_rect.bottom - 2), 1)
    pygame.draw.line(screen, (255, 255, 248), (roof_rect.x + 10, roof_rect.y + 8), (roof_rect.right - 10, roof_rect.y + 8), 2)

    pygame.draw.rect(screen, trim, (body.x + 10, body.y + 8, body.w - 20, 11))
    for x in range(body.x + 20, body.right - 20, 25):
        pygame.draw.rect(screen, (191, 188, 177), (x, body.y + 10, 6, 6))

    hall = pygame.Rect(body.centerx - 45, body.y + 34, 90, body.h - 34)
    pygame.draw.rect(screen, (218, 219, 207), hall.move(0, 3))
    pygame.draw.rect(screen, trim, hall)
    glass_box = pygame.Rect(hall.x + 12, hall.y + 9, hall.w - 24, hall.h - 13)
    pygame.draw.rect(screen, glass, glass_box)
    for gx in range(glass_box.x + 12, glass_box.right - 4, 13):
        pygame.draw.line(screen, dark, (gx, glass_box.y), (gx, glass_box.bottom), 1)
    for gy in range(glass_box.y + 12, glass_box.bottom - 2, 13):
        pygame.draw.line(screen, glass_hi, (glass_box.x + 2, gy), (glass_box.right - 2, gy), 1)
    pygame.draw.rect(screen, dark, glass_box, 2)
    pygame.draw.rect(screen, dark, (hall.centerx - 8, hall.bottom - 22, 16, 22))
    pygame.draw.line(screen, glass_hi, (hall.centerx, hall.bottom - 20), (hall.centerx, hall.bottom - 3), 1)

    for wx in (body.x + 22, body.right - 54):
        pygame.draw.rect(screen, glass, (wx, body.y + 38, 32, 13))
        pygame.draw.line(screen, glass_hi, (wx + 3, body.y + 41), (wx + 29, body.y + 41), 1)
        pygame.draw.rect(screen, dark, (wx, body.y + 38, 32, 13), 1)

    sign = pygame.Rect(body.centerx - 48, body.y + 22, 96, 13)
    pygame.draw.rect(screen, brick, sign)
    center_text("佘明培游泳馆", sign.centerx, sign.centery, (244, 211, 150), FONT_MINI)

    plaza = pygame.Rect(hall.x - 14, body.bottom - 2, hall.w + 28, 16)
    pygame.draw.rect(screen, (201, 198, 185), plaza)
    for i in range(4):
        step = pygame.Rect(hall.centerx - 34 - i * 5, body.bottom - 6 + i * 4, 68 + i * 10, 4)
        pygame.draw.rect(screen, (224, 222, 211), step)
        pygame.draw.line(screen, (158, 161, 157), (step.x, step.bottom - 1), (step.right, step.bottom - 1), 1)
    for tx in (base.x + 22, base.x + 54, base.right - 42, base.right - 18):
        pygame.draw.rect(screen, (95, 72, 48), (tx - 2, body.bottom - 19, 4, 17))
        pygame.draw.circle(screen, (67, 133, 71), (tx - 7, body.bottom - 23), 8)
        pygame.draw.circle(screen, (92, 160, 78), (tx + 6, body.bottom - 23), 8)
        pygame.draw.circle(screen, (55, 119, 64), (tx, body.bottom - 33), 7)


def draw_siyuan_canteen_overlay():
    if current_map_id != 1:
        return

    # 完全覆盖思源餐厅上方 4x3 的建筑格子，不盖住最下面一排道路。
    base = pygame.Rect(6 * TILE, HUD + 14 * TILE, 4 * TILE, 3 * TILE)
    art = pygame.Surface((base.w, base.h), pygame.SRCALPHA)

    brick = (156, 63, 52)
    brick_light = (191, 82, 62)
    trim = (235, 236, 222)
    trim_shadow = (171, 180, 176)
    roof = (31, 121, 116)
    roof_dark = (18, 78, 82)
    roof_hi = (65, 159, 149)
    glass = (38, 91, 119)
    glass_hi = (134, 204, 219)
    dark = (31, 39, 45)

    # 不绘制整块矩形底色、外框和背景纹理，只保留餐厅建筑本体。

    pygame.draw.ellipse(art, (0, 0, 0, 58), (6, 3, 116, 34))
    body = pygame.Rect(6, 38, 116, 53)
    pygame.draw.rect(art, (91, 40, 36), body.move(0, 4), border_radius=3)
    pygame.draw.rect(art, brick, body, border_radius=3)
    pygame.draw.rect(art, brick_light, (body.x + 4, body.y + 7, body.w - 8, body.h - 15), border_radius=2)

    # 白色环形外廊，压在屋顶下方，形成原图的圆弧栏杆。
    balcony = pygame.Rect(1, 27, 126, 27)
    pygame.draw.ellipse(art, trim_shadow, balcony.move(0, 4))
    pygame.draw.ellipse(art, trim, balcony)
    pygame.draw.rect(art, trim, (balcony.x + 2, balcony.centery - 2, balcony.w - 4, 18))
    pygame.draw.line(art, (126, 136, 137), (balcony.x + 9, balcony.centery + 10), (balcony.right - 9, balcony.centery + 10), 2)
    for x in range(balcony.x + 14, balcony.right - 10, 12):
        pygame.draw.line(art, (247, 247, 236), (x, balcony.centery), (x, balcony.bottom - 5), 2)

    # 青绿色大弧形屋顶，整体被裁剪在 3x4 格子内。
    roof_rect = pygame.Rect(0, 5, 128, 44)
    pygame.draw.ellipse(art, roof_dark, roof_rect.move(0, 6))
    pygame.draw.ellipse(art, roof, roof_rect)
    pygame.draw.rect(art, roof, (roof_rect.x + 4, roof_rect.centery - 2, roof_rect.w - 8, roof_rect.h // 2 + 5))
    pygame.draw.arc(art, (238, 243, 226), roof_rect.inflate(-1, 1), math.pi * 0.04, math.pi * 0.96, 3)
    pygame.draw.arc(art, (20, 72, 75), roof_rect.inflate(-9, -9), math.pi * 0.05, math.pi * 0.95, 2)
    for x in range(10, 120, 8):
        pygame.draw.line(art, roof_dark, (x, roof_rect.y + 10), (x + 8, roof_rect.bottom - 4), 1)
    pygame.draw.line(art, roof_hi, (18, roof_rect.y + 11), (110, roof_rect.y + 11), 2)

    # 屋顶后方红色设备房。
    top_box = pygame.Rect(45, 1, 38, 13)
    pygame.draw.rect(art, (178, 73, 54), top_box)
    pygame.draw.rect(art, (226, 111, 78), (top_box.x + 3, top_box.y + 3, top_box.w - 6, 4))
    pygame.draw.rect(art, (103, 51, 45), top_box, 1)

    # 红砖柱和一层通廊。
    for x in (12, 38, 68, 98):
        pygame.draw.rect(art, (112, 55, 48), (x, body.y + 16, 10, body.h - 8))
        pygame.draw.rect(art, (198, 95, 69), (x + 2, body.y + 19, 6, body.h - 14))
        pygame.draw.rect(art, trim, (x - 2, body.y + 14, 14, 4))
    pygame.draw.rect(art, trim, (body.x + 5, body.y + 13, body.w - 10, 8))

    # 中央拱形玻璃门，是照片正面最明显的入口特征。
    door_frame = pygame.Rect(43, 58, 42, 34)
    pygame.draw.arc(art, trim, door_frame.inflate(8, 9), math.pi, 2 * math.pi, 6)
    pygame.draw.rect(art, trim, (door_frame.x - 4, door_frame.centery - 1, door_frame.w + 8, door_frame.h // 2 + 6))
    glass_box = pygame.Rect(door_frame.x + 6, door_frame.y + 9, door_frame.w - 12, door_frame.h - 10)
    pygame.draw.rect(art, glass, glass_box)
    for gx in range(glass_box.x + 10, glass_box.right, 11):
        pygame.draw.line(art, dark, (gx, glass_box.y), (gx, glass_box.bottom), 1)
    for gy in range(glass_box.y + 9, glass_box.bottom, 10):
        pygame.draw.line(art, glass_hi, (glass_box.x + 2, gy), (glass_box.right - 2, gy), 1)
    pygame.draw.rect(art, dark, glass_box, 2)

    # 小台阶也只画在建筑内部，不向右覆盖取餐道路。
    for i in range(3):
        step = pygame.Rect(38 + i * 5, 89 + i * 3, 52 - i * 6, 3)
        pygame.draw.rect(art, (224, 222, 211), step)
        pygame.draw.line(art, (143, 151, 150), (step.x, step.bottom - 1), (step.right, step.bottom - 1), 1)
    center_text("思源", base.x + base.w // 2, base.y + 58, (255, 231, 169), FONT_MINI)
    screen.blit(art, base)


def draw_aiqiu_gym_overlay():
    if current_map_id != 1:
        return

    # 爱秋体育馆覆盖第二张地图左中部 7x6 的障碍物区域。
    # 参考图特征：灰色大屋顶、中央折线屋脊、红砖墙、白色基座和正面入口广场。
    base = pygame.Rect(3 * TILE, HUD + 7 * TILE, 7 * TILE, 6 * TILE)
    art = pygame.Surface((base.w, base.h), pygame.SRCALPHA)

    sky_gray = (205, 214, 216)
    roof = (168, 177, 181)
    roof_dark = (102, 114, 122)
    roof_hi = (226, 233, 233)
    brick = (187, 76, 54)
    brick_dark = (128, 54, 45)
    wall = (238, 239, 229)
    glass = (73, 111, 127)
    glass_hi = (151, 195, 205)
    plaza = (196, 196, 184)
    shadow = (28, 33, 36, 70)

    # 保持画布透明，不画体育馆外围矩形边框。

    # 门前广场和中轴步道，限制在建筑图案内部，不影响地图可通行判断。
    pygame.draw.rect(art, plaza, (40, 136, 144, 52))
    for x in range(48, 180, 24):
        pygame.draw.line(art, (139, 145, 141), (x, 136), (x + 16, 188), 1)
    for y in range(146, 185, 13):
        pygame.draw.line(art, (222, 222, 212), (44, y), (178, y), 1)

    # 主体红砖墙和白色底座。
    body = pygame.Rect(25, 76, 174, 55)
    pygame.draw.rect(art, brick_dark, body.move(0, 5), border_radius=2)
    pygame.draw.rect(art, brick, body, border_radius=2)
    pygame.draw.rect(art, wall, (body.x, body.y + 39, body.w, 16))
    pygame.draw.line(art, (255, 255, 244), (body.x, body.y + 6), (body.right, body.y + 6), 3)
    for x in range(body.x + 18, body.right - 10, 22):
        pygame.draw.line(art, (139, 55, 43), (x, body.y + 15), (x, body.y + 35), 2)

    # 正面玻璃入口，做出原图中间大门的感觉。
    entrance = pygame.Rect(80, 96, 64, 33)
    pygame.draw.rect(art, wall, entrance.inflate(12, 8))
    pygame.draw.rect(art, glass, entrance)
    for x in range(entrance.x + 10, entrance.right, 12):
        pygame.draw.line(art, (38, 59, 66), (x, entrance.y), (x, entrance.bottom), 1)
    for y in range(entrance.y + 9, entrance.bottom, 10):
        pygame.draw.line(art, glass_hi, (entrance.x + 2, y), (entrance.right - 2, y), 1)
    pygame.draw.rect(art, (37, 45, 48), entrance, 2)

    # 建筑名称直接嵌在正立面横匾中，不再使用地图上浮动的文字框。
    name_plate = pygame.Rect(58, 84, 108, 18)
    pygame.draw.rect(art, (246, 242, 225), name_plate)
    pygame.draw.line(art, (171, 151, 119), name_plate.bottomleft, name_plate.bottomright, 1)
    label = FONT_MINI.render("爱秋体育馆", True, (97, 61, 43))
    art.blit(label, label.get_rect(center=(name_plate.centerx, name_plate.centery + 1)))

    # 白色低矮附属廊架，模拟照片前方两侧平台。
    for rect in (pygame.Rect(4, 127, 66, 44), pygame.Rect(154, 127, 66, 44)):
        pygame.draw.rect(art, wall, rect)
        pygame.draw.rect(art, (197, 203, 198), rect, 2)
        for x in range(rect.x + 10, rect.right - 6, 13):
            pygame.draw.line(art, (147, 153, 150), (x, rect.y + 6), (x, rect.bottom - 8), 1)
        for y in range(rect.y + 12, rect.bottom - 4, 11):
            pygame.draw.line(art, (229, 230, 221), (rect.x + 4, y), (rect.right - 4, y), 1)

    # 灰色大屋顶：先画外轮廓，再画中间折线屋脊和天窗。
    roof_pts = [(17, 71), (38, 31), (89, 12), (112, 33), (135, 12), (186, 31), (207, 71), (190, 82), (34, 82)]
    pygame.draw.polygon(art, shadow, [(x, y + 7) for x, y in roof_pts])
    pygame.draw.polygon(art, roof, roof_pts)
    pygame.draw.polygon(art, roof_hi, [(43, 52), (112, 18), (181, 52), (166, 61), (112, 34), (58, 61)])
    pygame.draw.polygon(art, sky_gray, [(58, 58), (112, 35), (166, 58), (151, 68), (112, 50), (73, 68)])
    pygame.draw.line(art, roof_dark, (112, 18), (112, 50), 3)
    pygame.draw.line(art, roof_dark, (43, 52), (112, 18), 2)
    pygame.draw.line(art, roof_dark, (181, 52), (112, 18), 2)
    pygame.draw.line(art, (244, 247, 244), (31, 72), (193, 72), 4)
    for x in range(54, 176, 17):
        pygame.draw.line(art, (133, 143, 149), (x, 35), (x + 16, 75), 1)
    for x in (64, 86, 138, 160):
        pygame.draw.ellipse(art, (238, 241, 240), (x, 29, 8, 4))
    for x in (74, 102, 130, 154):
        pygame.draw.ellipse(art, (238, 241, 240), (x, 50, 8, 4))

    # 两侧绿化和小标识，让建筑不只是一整块墙。
    for x in (36, 184):
        pygame.draw.rect(art, (91, 120, 63), (x - 4, 138, 8, 35), border_radius=3)
        pygame.draw.circle(art, (66, 118, 65), (x, 134), 8)
    pygame.draw.rect(art, (212, 69, 55), (169, 155, 30, 13), border_radius=2)
    pygame.draw.rect(art, (70, 73, 72), (27, 151, 35, 17), border_radius=2)

    screen.blit(art, base)



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
    """笃行园区宿舍楼：灰石基座 + 红砖 + 白色横带 + 横长窗 + 顶层拱窗 + 红瓦坡顶白脊。
       每个园区 = 对称双翼（4层）夹中间略低连接体（3层），只低一点点。"""
    if current_map_id != 2:
        return

    # ===== 调色板 =====
    STONE = (140, 144, 141)
    STONE_DARK = (110, 114, 111)
    STONE_LINE = (122, 126, 123)
    BRICK = (178, 84, 56)
    BRICK_DARK = (142, 58, 40)
    BRICK_HI = (202, 104, 74)
    TRIM = (244, 239, 228)
    TRIM_SHADOW = (194, 188, 174)
    GLASS = (52, 90, 128)
    GLASS_DARK = (24, 42, 60)
    GLASS_HI = (152, 210, 230)
    ROOF_TILE = (188, 64, 40)
    ROOF_DARK = (136, 40, 26)
    ROOF_RIDGE = (252, 248, 234)

    def draw_section(rect, cols, num_floors, people_seed, has_entrance=True, show_name=False):
        """绘制一个建筑段：阴影 → 石基座 → 红砖体 → 白横带+横长窗 → 拱窗顶 → 坡顶。"""

        # ---- 阴影 ----
        shadow = pygame.Surface((rect.w + 22, rect.h + 22), pygame.SRCALPHA)
        pygame.draw.polygon(shadow, (0, 0, 0, 54),
                           [(13, 17), (rect.w + 18, 11), (rect.w + 13, rect.h + 16), (5, rect.h + 18)])
        screen.blit(shadow, (rect.x - 9, rect.y - 9))

        base_h = 13

        # ---- 灰色石墙基座 ----
        stone_rect = pygame.Rect(rect.x - 2, rect.bottom - base_h, rect.w + 4, base_h + 2)
        pygame.draw.rect(screen, STONE_DARK, stone_rect.move(0, 3))
        pygame.draw.rect(screen, STONE, stone_rect)
        pygame.draw.rect(screen, STONE_DARK, stone_rect, 1)
        for sx in range(stone_rect.x + 6, stone_rect.right - 4, 16):
            pygame.draw.line(screen, STONE_LINE, (sx, stone_rect.y + 3), (sx, stone_rect.bottom - 3), 1)

        # ---- 红砖主体 ----
        body_h = rect.h - base_h
        body = pygame.Rect(rect.x, rect.y, rect.w, body_h)
        pygame.draw.rect(screen, BRICK_DARK, body.move(0, 4))
        pygame.draw.rect(screen, BRICK, body)
        for yy in range(body.y + 6, body.bottom - 4, 7):
            alpha = 48 if (yy // 7) % 2 == 0 else 32
            shade = pygame.Surface((body.w - 8, 1), pygame.SRCALPHA)
            shade.fill((*BRICK_HI, alpha))
            screen.blit(shade, (body.x + 4, yy))

        # ---- 白色横带 + 横长窗 + 顶层拱窗 ----
        floor_h = (body_h - 14) // num_floors
        band_positions = []
        for f in range(num_floors + 1):
            band_y = body.y + 6 + f * floor_h
            band_positions.append(band_y)
            pygame.draw.rect(screen, TRIM, (body.x, band_y, body.w, 5))
            pygame.draw.line(screen, TRIM_SHADOW, (body.x, band_y + 5), (body.right, band_y + 5), 1)
            pygame.draw.line(screen, (255, 254, 245), (body.x + 2, band_y + 1), (body.right - 2, band_y + 1), 1)

        window_positions = []
        # 窗宽占满两白带之间，做出横长比例（宽 > 高）
        col_w = max(13, (body.w - 16) // cols)
        for f in range(num_floors):
            band_y = band_positions[f]
            next_band = band_positions[f + 1]
            gap = next_band - band_y
            wy = band_y + 6
            wh = gap - 10
            is_top = (f == num_floors - 1)  # 顶层 → 拱窗

            for c in range(cols):
                wx = body.x + 6 + c * col_w
                ww = max(11, col_w - 4)

                if is_top:
                    # 顶层拱窗：下半矩形 + 上半椭圆弧
                    # 矩形主体
                    pygame.draw.rect(screen, GLASS, (wx, wy + 2, ww, wh - 2))
                    # 拱形顶部（半椭圆）
                    arch_top = pygame.Rect(wx, wy - 3, ww, 10)
                    pygame.draw.ellipse(screen, GLASS, arch_top)
                    # 高光
                    pygame.draw.line(screen, GLASS_HI, (wx + 2, wy + 3), (wx + ww - 2, wy + 3), 1)
                    # 窗框 — 矩形部分
                    pygame.draw.rect(screen, GLASS_DARK, (wx, wy + 2, ww, wh - 2), 1)
                    # 窗框 — 拱形部分
                    pygame.draw.arc(screen, GLASS_DARK, arch_top, math.pi, 2 * math.pi, 1)
                    # 拱顶竖框连接
                    pygame.draw.line(screen, GLASS_DARK, (wx, wy + 2), (wx, wy), 1)
                    pygame.draw.line(screen, GLASS_DARK, (wx + ww, wy + 2), (wx + ww, wy), 1)
                else:
                    # 普通横长窗
                    pygame.draw.rect(screen, GLASS, (wx, wy, ww, wh))
                    pygame.draw.line(screen, GLASS_HI, (wx + 2, wy + 2), (wx + ww - 2, wy + 2), 1)
                    if ww > 16:
                        pygame.draw.line(screen, GLASS_DARK, (wx + ww // 2, wy + 1),
                                        (wx + ww // 2, wy + wh - 1), 1)
                    pygame.draw.rect(screen, GLASS_DARK, (wx, wy, ww, wh), 1)

                window_positions.append((wx, wy, ww, wh))

        # ---- 一楼入口 ----
        if has_entrance:
            door_y = band_positions[0] + 6
            door_h = band_positions[1] - band_positions[0] - 5
            door_x = body.centerx - 12
            door_w = 24
            pygame.draw.rect(screen, (28, 34, 40), (door_x, door_y, door_w, door_h + 12))
            pygame.draw.rect(screen, (46, 54, 62), (door_x, door_y, door_w, door_h + 12), 1)
            pygame.draw.line(screen, (88, 116, 136), (door_x + door_w // 2, door_y + 2),
                           (door_x + door_w // 2, door_y + door_h + 10), 1)
            pygame.draw.rect(screen, TRIM, (door_x - 3, door_y - 3, door_w + 6, 4))
            pygame.draw.line(screen, TRIM_SHADOW, (door_x - 3, door_y + 1),
                           (door_x + door_w + 3, door_y + 1), 1)

        # ---- 建筑名牌 ----
        if show_name:
            sign_w = min(80, body.w - 16)
            sign = pygame.Rect(body.centerx - sign_w // 2, body.y + 3, sign_w, 10)
            pygame.draw.rect(screen, (24, 30, 36), sign)
            pygame.draw.rect(screen, TRIM, sign, 1)
            center_text("笃行园区", sign.centerx, sign.centery, (244, 232, 182), FONT_MINI)

        # ---- 红瓦坡顶 + 白脊 ----
        roof_y = body.y
        eave = [
            (body.x - 9, roof_y + 13),
            (body.centerx, roof_y - 10),
            (body.right + 9, roof_y + 13),
            (body.right + 2, roof_y + 20),
            (body.x - 2, roof_y + 20),
        ]
        pygame.draw.polygon(screen, ROOF_DARK, [(x, y + 5) for x, y in eave])
        pygame.draw.polygon(screen, (255, 251, 240), eave)
        tile_surf = [
            (body.x + 7, roof_y + 10),
            (body.centerx, roof_y - 4),
            (body.right - 7, roof_y + 10),
            (body.right - 13, roof_y + 15),
            (body.x + 13, roof_y + 15),
        ]
        pygame.draw.polygon(screen, ROOF_TILE, tile_surf)
        for i in range(1, 4):
            yy = roof_y + i * 4
            prog = i / 4
            x_pad = int(7 + prog * (body.w // 2 - 7))
            pygame.draw.line(screen, (160, 50, 32), (body.x + x_pad, yy), (body.right - x_pad, yy), 1)
        pygame.draw.line(screen, ROOF_RIDGE, (body.centerx, roof_y - 10), (body.centerx, roof_y - 4), 3)
        for dx in (-1, 1):
            pygame.draw.line(screen, ROOF_RIDGE, (body.centerx, roof_y - 10),
                           (body.centerx + dx * 6, roof_y - 14), 2)

        # ---- 救援学生 ----
        pulse_a = math.sin(time.time() * 6 + people_seed) * 3
        for idx in (cols + 1, min(len(window_positions) - 3, 2 * cols + cols // 2)):
            if idx < len(window_positions):
                wx, wy, ww, wh = window_positions[idx]
                px, py = wx + ww // 2, wy + wh + 5
                pygame.draw.rect(screen, (255, 244, 200), (wx + 1, wy + 1, ww - 2, wh - 1))
                pygame.draw.circle(screen, (248, 198, 140), (px, py), 4)
                pygame.draw.rect(screen, (226, 52, 58), (px - 4, py + 4, 8, 10))
                pygame.draw.line(screen, (248, 198, 140), (px - 4, py + 7),
                                (px - 13, py + int(pulse_a) - 2), 3)
                pygame.draw.line(screen, (248, 198, 140), (px + 4, py + 7),
                                (px + 13, py - int(pulse_a) - 2), 3)
                pygame.draw.line(screen, (255, 244, 160), (px + 13, py - int(pulse_a) - 2),
                                (px + 19, py - int(pulse_a) - 9), 2)

        return body

    # ============================================================
    #  对称三段式：左 2 列(4层) + 中 3 列(3层) + 右 2 列(4层)
    #  中间只低一层（~20px），形成微妙的高低错落
    # ============================================================

    def draw_one_complex(origin_col, people_seed):
        ox = origin_col * TILE
        oy = HUD + 10 * TILE
        tall_h = 3 * TILE + 6               # 高层全高：102
        mid_h = tall_h - TILE // 2 + 2      # 中层略低：88（只低 14px）
        mid_y = oy + TILE // 3              # 中层略微下沉
        wing_w = 2 * TILE - 4              # 翼宽：60
        mid_w = 3 * TILE - 6               # 中宽：90

        # 左翼（2 列，4 层）
        left_body = draw_section(
            pygame.Rect(ox + 3, oy + 2, wing_w, tall_h),
            cols=2, num_floors=4, people_seed=people_seed,
            has_entrance=True, show_name=True,
        )
        # 中间连接（3 列，3 层，只低一点点）
        draw_section(
            pygame.Rect(ox + wing_w + 1, mid_y, mid_w, mid_h),
            cols=3, num_floors=3, people_seed=people_seed + 1,
            has_entrance=False, show_name=False,
        )
        # 右翼（2 列，4 层，与左翼对称）
        right_body = draw_section(
            pygame.Rect(ox + wing_w + mid_w - 1, oy + 2, wing_w, tall_h),
            cols=2, num_floors=4, people_seed=people_seed + 2,
            has_entrance=True, show_name=False,
        )

        # 楼前绿化
        for body, sd in [(left_body, 0), (right_body, 2)]:
            for i, tx in enumerate([body.x + 10, body.x + body.w // 2, body.x + body.w - 14]):
                trunk_h = 14 + (tile_seed(int(tx), people_seed + sd + i) % 8)
                trunk_y = body.bottom + 17
                pygame.draw.rect(screen, (88, 70, 44), (tx - 2, trunk_y - trunk_h, 4, trunk_h))
                canopy_y = trunk_y - trunk_h
                for layer, (cw, ch, color) in enumerate([
                    (18, 14, (52, 122, 64)),
                    (14, 12, (70, 148, 72)),
                    (10, 10, (96, 168, 78)),
                ]):
                    cx_off = (i % 2) * 4 - 2
                    pygame.draw.ellipse(screen, color,
                                       (tx - cw // 2 + cx_off, canopy_y - ch + 4 - layer * 8, cw, ch))

    # 左园区（列 13-19）
    draw_one_complex(13, people_seed=0)
    # 右园区（列 21-27）
    draw_one_complex(21, people_seed=10)


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
    """第四张地图教学楼群：学武楼 / 坤銮楼 / 文宣楼 / 5号楼。
       现代风格：奶油色墙面 + 大幅深蓝玻璃窗 + 灰石基座 + 红棕女儿墙 + 平屋顶。"""
    if current_map_id != 3:
        return

    # ===== 调色板 =====
    WALL = (238, 236, 226)         # 奶油白
    WALL_SHADOW = (204, 202, 192)  # 暗面
    WALL_HI = (250, 249, 242)      # 高光
    GLASS = (48, 86, 122)          # 深蓝玻璃
    GLASS_DARK = (22, 42, 60)      # 窗框
    GLASS_HI = (138, 198, 222)     # 玻璃反光
    PARAPET = (182, 70, 46)        # 红棕女儿墙
    PARAPET_DARK = (136, 46, 32)
    PARAPET_HI = (210, 92, 60)
    TRIM_SHADOW = (196, 194, 184)  # 楼层横线阴影

    def building(rect, num_floors, name, people_seed):
        """绘制一栋现代教学楼。"""

        # ---- 阴影 ----
        shadow = pygame.Surface((rect.w + 20, rect.h + 20), pygame.SRCALPHA)
        pygame.draw.polygon(shadow, (0, 0, 0, 55),
                           [(12, 16), (rect.w + 16, 10), (rect.w + 12, rect.h + 15), (5, rect.h + 17)])
        screen.blit(shadow, (rect.x - 8, rect.y - 8))

        # ---- 奶油色主体墙面（占满整个 rect，无基座） ----
        body = pygame.Rect(rect.x, rect.y, rect.w, rect.h)
        pygame.draw.rect(screen, WALL_SHADOW, body.move(0, 4))
        pygame.draw.rect(screen, WALL, body)

        # ---- 红棕女儿墙（顶部横带） ----
        parapet_h = 10
        parapet = pygame.Rect(body.x, body.y, body.w, parapet_h)
        pygame.draw.rect(screen, PARAPET_DARK, parapet.move(0, 2))
        pygame.draw.rect(screen, PARAPET, parapet)
        pygame.draw.line(screen, PARAPET_HI, (parapet.x + 3, parapet.y + 2), (parapet.right - 3, parapet.y + 2), 1)
        pygame.draw.line(screen, PARAPET_DARK, (parapet.x, parapet.bottom), (parapet.right, parapet.bottom), 2)

        # ---- 底层底线（建筑与地面交界） ----
        pygame.draw.line(screen, WALL_SHADOW, (body.x - 2, body.bottom - 1), (body.right + 2, body.bottom - 1), 2)

        # ---- 楼层横线 + 对称窗户 ----
        usable_h = body.h - parapet_h - 4
        floor_h = usable_h // num_floors
        cols = 3
        margin_x = 10
        gap_x = 6
        total_win_w = body.w - 2 * margin_x - (cols - 1) * gap_x
        ww = total_win_w // cols
        actual_total = cols * ww + (cols - 1) * gap_x
        start_x = body.x + (body.w - actual_total) // 2

        ground_wy = 0

        for f in range(num_floors):
            floor_top = body.y + parapet_h + 2 + f * floor_h
            line_y = floor_top
            pygame.draw.line(screen, TRIM_SHADOW, (body.x + 4, line_y), (body.right - 4, line_y), 1)
            pygame.draw.line(screen, WALL_HI, (body.x + 4, line_y + 1), (body.right - 4, line_y + 1), 1)

            wy = floor_top + 4
            wh = floor_h - 8
            is_ground = (f == num_floors - 1)

            if is_ground:
                ground_wy = wy

            for c in range(cols):
                if is_ground and c == 1:
                    continue  # 大门位置跳过窗户

                wx = start_x + c * (ww + gap_x)
                pygame.draw.rect(screen, GLASS, (wx, wy, ww, wh))
                pygame.draw.line(screen, GLASS_HI, (wx + 2, wy + 2), (wx + ww - 3, wy + 2), 1)
                if ww > 16:
                    pygame.draw.line(screen, GLASS_DARK, (wx + ww // 2, wy + 1),
                                    (wx + ww // 2, wy + wh - 1), 1)
                pygame.draw.rect(screen, GLASS_DARK, (wx, wy, ww, wh), 1)

        # ---- 一楼入口（底层中间，直通底部） ----
        door_w = 26
        door_x = body.centerx - door_w // 2
        door_y = ground_wy
        door_h = body.bottom - door_y - 2  # 大门直通建筑底部
        pygame.draw.rect(screen, (28, 32, 38), (door_x, door_y, door_w, door_h))
        pygame.draw.rect(screen, (46, 52, 60), (door_x, door_y, door_w, door_h), 1)
        pygame.draw.line(screen, (80, 104, 124), (door_x + door_w // 2, door_y + 2),
                        (door_x + door_w // 2, door_y + door_h - 2), 1)
        # 门楣
        pygame.draw.rect(screen, WALL_HI, (door_x - 3, door_y - 3, door_w + 6, 4))
        pygame.draw.line(screen, TRIM_SHADOW, (door_x - 3, door_y + 1), (door_x + door_w + 3, door_y + 1), 1)

        # ---- 建筑名牌（嵌在红棕女儿墙上） ----
        sign_w = min(76, body.w - 20)
        sign = pygame.Rect(body.centerx - sign_w // 2, body.y + 2, sign_w, 8)
        pygame.draw.rect(screen, (24, 28, 34), sign)
        pygame.draw.rect(screen, PARAPET_HI, sign, 1)
        center_text(name, sign.centerx, sign.centery, (244, 232, 182), FONT_MINI)

        return body

    # ===== 四栋教学楼 =====
    # 5号楼（列 1-4）
    building(pygame.Rect(1 * TILE, HUD + 10 * TILE, 4 * TILE, 5 * TILE),
             num_floors=5, name="5号楼", people_seed=0)
    # 文宣楼（列 6-9）
    building(pygame.Rect(6 * TILE, HUD + 10 * TILE, 4 * TILE, 5 * TILE),
             num_floors=5, name="文宣楼", people_seed=4)
    # 坤銮楼（列 22-25）
    building(pygame.Rect(22 * TILE, HUD + 10 * TILE, 4 * TILE, 5 * TILE),
             num_floors=5, name="坤銮楼", people_seed=8)
    # 学武楼（列 27-30）
    building(pygame.Rect(27 * TILE, HUD + 10 * TILE, 4 * TILE, 5 * TILE),
             num_floors=5, name="学武楼", people_seed=12)

    # ---- 楼前绿化 ----
    for bx, sd in [(1 * TILE, 0), (6 * TILE, 4), (22 * TILE, 8), (27 * TILE, 12)]:
        body_x = bx
        body_w = 4 * TILE
        body_bottom = HUD + 15 * TILE  # 基座底部
        for i, tx in enumerate([body_x + 20, body_x + body_w - 24]):
            trunk_h = 14 + (tile_seed(int(tx), sd + i) % 8)
            trunk_y = body_bottom + 5
            pygame.draw.rect(screen, (88, 70, 44), (tx - 2, trunk_y - trunk_h, 4, trunk_h))
            canopy_y = trunk_y - trunk_h
            for layer, (cw, ch, color) in enumerate([
                (18, 14, (52, 122, 64)),
                (14, 12, (70, 148, 72)),
                (10, 10, (96, 168, 78)),
            ]):
                cx_off = (i % 2) * 4 - 2
                pygame.draw.ellipse(screen, color,
                                   (tx - cw // 2 + cx_off, canopy_y - ch + 4 - layer * 8, cw, ch))
    
# 单格建筑组件：给普通障碍物增加屋顶、窗户、阴影等像素细节。
def draw_aerospace_building_tile(r, x, y):
    draw_field_tile(r, x, y, "S")
    return

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


# 小人物/窗户辅助绘制，用来表现宿舍楼的末日氛围。
def draw_rescue_student(x, y, phase):
    shirt = [(244, 68, 72), (255, 198, 74), (92, 176, 238)][phase % 3]
    pygame.draw.circle(screen, (255, 214, 172), (x, y), 3)
    pygame.draw.rect(screen, shirt, (x - 3, y + 3, 6, 5))
    pygame.draw.line(screen, (255, 214, 172), (x - 3, y + 3), (x - 8, y - 2), 2)
    pygame.draw.line(screen, (255, 214, 172), (x + 3, y + 3), (x + 8, y - 3), 2)
    pygame.draw.line(screen, (255, 245, 146), (x + 7, y - 5), (x + 12, y - 9), 2)


def draw_dorm_window(r, wx, wy, lit, rescue=False, phase=0):
    if current_map_id in HORROR_MAP_IDS:
        glass = HORROR_GREEN if lit else (23, 59, 49)
        pygame.draw.rect(screen, glass, (wx, wy, 8, 8))
        pygame.draw.line(screen, (167, 255, 181) if lit else (55, 95, 79), (wx + 2, wy + 2), (wx + 6, wy + 2), 1)
        pygame.draw.rect(screen, (8, 22, 19), (wx, wy, 8, 8), 1)
        if rescue:
            draw_rescue_student(wx + 4, wy + 4, phase)
        return
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
    if current_map_id in HORROR_MAP_IDS:
        draw_horror_building_tile(r, x, y, above, below, left, right)
        return
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
    if current_map_id in HORROR_MAP_IDS:
        draw_horror_building_tile(r, x, y, above, below, left, right)
        return
    if current_map_id != 0:
        pygame.draw.rect(screen, (82, 88, 92), r)
        pygame.draw.rect(screen, (118, 124, 125), (r.x + 3, r.y + 5, r.w - 6, r.h - 8))
        pygame.draw.rect(screen, (45, 48, 50), r, 1)
        return


def draw_horror_building_tile(r, x, y, above, below, left, right):
        district = (x // 6 + y // 4) % 4
        palettes = [
            ((56, 61, 55), (84, 91, 80), (26, 34, 31), (8, 13, 14), (144, 151, 124)),
            ((63, 55, 52), (89, 80, 72), (50, 43, 39), (14, 17, 17), (126, 126, 105)),
            ((61, 66, 58), (96, 100, 84), (47, 36, 34), (12, 15, 16), (149, 142, 113)),
            ((45, 56, 53), (72, 84, 76), (31, 41, 37), (8, 15, 15), (118, 134, 111)),
        ]
        wall, wall_light, roof, roof_dark, trim = palettes[district]

        pygame.draw.rect(screen, (6, 10, 11), r.move(2, 2))
        pygame.draw.rect(screen, wall, r)
        pygame.draw.rect(screen, wall_light, (r.x + 3, r.y + 5, r.w - 6, r.h - 8))

        if not above:
            if district == 1:
                pygame.draw.rect(screen, roof_dark, (r.x - (0 if left else 3), r.y + 5, r.w + (0 if left else 3) + (0 if right else 3), 10))
                pygame.draw.rect(screen, roof, (r.x - (0 if left else 3), r.y + 2, r.w + (0 if left else 3) + (0 if right else 3), 10))
                pygame.draw.line(screen, (98, 116, 92), (r.x + 4, r.y + 8), (r.right - 4, r.y + 8), 2)
            else:
                roof_poly = [(r.x - (0 if left else 5), r.y + 11), (r.centerx, r.y + 1), (r.right + (0 if right else 5), r.y + 11), (r.right, r.y + 19), (r.x, r.y + 19)]
                pygame.draw.polygon(screen, roof_dark, [(px, py + 3) for px, py in roof_poly])
                pygame.draw.polygon(screen, roof, roof_poly)
                pygame.draw.line(screen, (92, 110, 91), (r.x + 4, r.y + 13), (r.right - 4, r.y + 13), 1)
        elif tile_seed(x, y) % 5 == 0:
            pygame.draw.rect(screen, (34, 45, 40), (r.x + 4, r.y + 4, r.w - 8, 6))

        if not left:
            pygame.draw.line(screen, (10, 18, 18), (r.x, r.y + 7), (r.x, r.bottom), 2)
        if not right:
            pygame.draw.line(screen, (7, 13, 14), (r.right - 1, r.y + 7), (r.right - 1, r.bottom), 2)
        if district in {1, 3} and left and right:
            pygame.draw.rect(screen, (42, 49, 43), (r.x + 2, r.y + 17, r.w - 4, 3))
            pygame.draw.rect(screen, (42, 49, 43), (r.x + 2, r.y + 28, r.w - 4, 3))

        if above and below:
            lit = tile_seed(x, y) % 4 != 0
            rescue = tile_seed(x, y) in {7, 21, 45, 62, 84, 98}
            draw_dorm_window(r, r.x + 6, r.y + 8, lit, rescue, tile_seed(x, y))
            draw_dorm_window(r, r.x + 19, r.y + 8, tile_seed(x, y) % 3 == 0, False, tile_seed(x, y) + 1)
        elif not below:
            pygame.draw.rect(screen, (21, 25, 23), (r.x, r.bottom - 5, r.w, 5))
            if tile_seed(x, y) % 4 == 0:
                pygame.draw.rect(screen, (9, 15, 16), (r.x + 10, r.y + 8, 12, 20))
                pygame.draw.rect(screen, trim, (r.x + 12, r.y + 10, 8, 4))
            else:
                draw_dorm_window(r, r.x + 6, r.y + 9, True, tile_seed(x, y) % 13 == 0, tile_seed(x, y))
                draw_dorm_window(r, r.x + 19, r.y + 9, tile_seed(x, y) % 2 == 0, False, tile_seed(x, y) + 2)

        if tile_seed(x, y) % 11 == 0:
            pygame.draw.line(screen, (89, 42, 37), (r.x + 7, r.y + 18), (r.x + 17, r.y + 28), 1)
        pygame.draw.rect(screen, (5, 9, 10), r, 1)
        return

def draw_unused_daytime_campus_building_tile(r, x, y):
    above = tile_at(x, y - 1) == "B"
    below = tile_at(x, y + 1) == "B"
    left = tile_at(x - 1, y) == "B"
    right = tile_at(x + 1, y) == "B"
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

# 湖面格子的水波纹绘制。
def draw_lake_tile(r, x, y):
    if current_map_id in HORROR_MAP_IDS:
        pygame.draw.rect(screen, (18, 70, 67), r)
        pygame.draw.rect(screen, (8, 25, 29), r, 1)
        wave = (74, 255, 143)
        offset = (tile_seed(x, y) % 8) - 4
        pygame.draw.arc(screen, wave, (r.x + 3 + offset, r.y + 8, r.w - 10, 11), 0, math.pi, 2)
        pygame.draw.arc(screen, (23, 119, 87), (r.x + 4 - offset, r.y + 21, r.w - 8, 9), 0, math.pi, 2)
        return
    pygame.draw.rect(screen, COLORS["L"], r)
    wave = (218, 246, 249)
    offset = (tile_seed(x, y) % 8) - 4
    pygame.draw.arc(screen, wave, (r.x + 3 + offset, r.y + 8, r.w - 10, 11), 0, math.pi, 2)
    pygame.draw.arc(screen, (89, 174, 196), (r.x + 4 - offset, r.y + 21, r.w - 8, 9), 0, math.pi, 2)


def draw_first_map_horror_atmosphere():
    elapsed = time.time()
    mist = pygame.Surface((WIDTH, HEIGHT - HUD), pygame.SRCALPHA)
    for i in range(9):
        band_y = int((i * 67 + elapsed * (11 + i % 3 * 5)) % (HEIGHT - HUD + 80)) - 48
        alpha = 24 + (i % 3) * 8
        color = (24, 178, 86, alpha)
        pygame.draw.ellipse(mist, color, (i * 119 - 90, band_y, 310, 44))
        pygame.draw.ellipse(mist, (6, 28, 24, alpha + 10), (i * 127 - 130, band_y + 22, 280, 30))
    screen.blit(mist, (0, HUD))

    vignette = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(vignette, (0, 0, 0, 50), (0, HUD, WIDTH, HEIGHT - HUD))
    pygame.draw.rect(vignette, (0, 0, 0, 82), (0, HUD, WIDTH, 18))
    pygame.draw.rect(vignette, (0, 0, 0, 94), (0, HEIGHT - 52, WIDTH, 52))
    pygame.draw.rect(vignette, (0, 0, 0, 76), (0, HUD, 40, HEIGHT - HUD))
    pygame.draw.rect(vignette, (0, 0, 0, 76), (WIDTH - 40, HUD, 40, HEIGHT - HUD))
    if int(elapsed * 2) % 5 == 0:
        pygame.draw.rect(vignette, (80, 255, 133, 22), (0, HUD + 6, WIDTH, 3))
    screen.blit(vignette, (0, 0))


def apply_horror_building_filter(rect, strength=124, green=50):
    overlay = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, strength))
    pygame.draw.rect(overlay, (15, 70, 45, green), overlay.get_rect())
    pygame.draw.rect(overlay, (0, 0, 0, 82), overlay.get_rect(), 2)
    screen.blit(overlay, rect)

    scan_y = rect.y + 9 + (tile_seed(rect.x // TILE, rect.y // TILE) % max(8, rect.h - 16))
    pygame.draw.line(screen, (79, 255, 132), (rect.x + 6, scan_y), (rect.right - 6, scan_y), 1)
    if rect.w > 70:
        for x in range(rect.x + 18, rect.right - 10, 36):
            pygame.draw.rect(screen, (38, 228, 101), (x, rect.y + 20, 11, 5))


def draw_horror_filters_for_special_buildings():
    if current_map_id == 1:
        rects = [
            pygame.Rect(3 * TILE, HUD + 2 * TILE, 7 * TILE, 4 * TILE),
            pygame.Rect(3 * TILE, HUD + 7 * TILE, 7 * TILE, 6 * TILE),
            pygame.Rect(6 * TILE, HUD + 14 * TILE, 4 * TILE, 3 * TILE),
            pygame.Rect(17 * TILE, HUD + 8 * TILE, 8 * TILE, 6 * TILE),
        ]
    elif current_map_id == 2:
        rects = [
            pygame.Rect(1 * TILE, HUD + 1 * TILE, 12 * TILE, 7 * TILE),
            pygame.Rect(1 * TILE, HUD + 9 * TILE, 12 * TILE, 8 * TILE),
            pygame.Rect(14 * TILE, HUD + 2 * TILE, 4 * TILE, 5 * TILE),
            pygame.Rect(13 * TILE, HUD + 10 * TILE, 15 * TILE, 7 * TILE),
            pygame.Rect(22 * TILE, HUD + 1 * TILE, 7 * TILE, 5 * TILE),
            pygame.Rect(28 * TILE, HUD + 10 * TILE, 4 * TILE, 7 * TILE),
        ]
    elif current_map_id == 3:
        rects = [
            pygame.Rect(1 * TILE, HUD + 3 * TILE, 5 * TILE, 3 * TILE),
            pygame.Rect(11 * TILE, HUD + 9 * TILE, 10 * TILE, 5 * TILE),
            pygame.Rect(0 * TILE, HUD + 8 * TILE, 11 * TILE, 8 * TILE),
            pygame.Rect(22 * TILE, HUD + 8 * TILE, 10 * TILE, 8 * TILE),
        ]
    else:
        return

    for rect in rects:
        clipped = rect.clip(screen.get_rect())
        if clipped.w > 0 and clipped.h > 0:
            apply_horror_building_filter(clipped)


# 根据当前地图和格子类型，把整张地图逐格绘制出来。
# 绘制顺序是：先画基础地形，再画重点建筑叠加层。
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
                elif current_map_id == 1 and 3 <= x <= 9 and 2 <= y <= 5:
                    draw_field_tile(r, x, y, "S")
                elif is_aerospace_building_tile(x, y):
                    draw_aerospace_building_tile(r, x, y)
                else:
                    draw_campus_building_tile(r, x, y)
            elif tile in {"P", "F", "K", "S"}:
                draw_field_tile(r, x, y, tile)
            elif tile == "L":
                draw_lake_tile(r, x, y)
            elif tile == "G":
                draw_road_tile(r, x, y)
                pygame.draw.circle(screen, (255, 244, 120), r.center, 12)
                pygame.draw.circle(screen, (117, 91, 16), r.center, 12, 2)
            elif tile == "C":
                draw_road_tile(r, x, y)
                pygame.draw.rect(screen, (145, 61, 174), r.inflate(-4, -4), border_radius=3)
                pygame.draw.rect(screen, (223, 170, 244), r.inflate(-10, -10), border_radius=2)
            elif tile == "D":
                draw_road_tile(r, x, y)
                pygame.draw.rect(screen, (244, 68, 72), r.inflate(-10, -8), border_radius=5)
                pygame.draw.rect(screen, (104, 18, 22), r.inflate(-10, -8), 2, border_radius=5)
            else:
                color = COLORS.get(tile, (200, 200, 200))
                pygame.draw.rect(screen, color, r)
                pygame.draw.rect(screen, (47, 49, 50), r, 1)
    draw_jingfeng_canteen_overlay()
    draw_student_activity_center_overlay()
    draw_aerospace_building_overlay()
    draw_swimming_pool_overlay()
    draw_aiqiu_gym_overlay()
    draw_siyuan_canteen_overlay()
    draw_furong_canteen_overlay()
    draw_pharmacy_school_overlay()
    draw_fengting_canteen_overlay()
    draw_express_center_overlay()
    draw_duxing_dorm_overlay()
    draw_third_map_dorms_overlay()
    draw_dewang_library_overlay()
    draw_fourth_map_side_buildings_overlay()
    draw_horror_filters_for_special_buildings()
    if current_map_id in HORROR_MAP_IDS:
        draw_first_map_horror_atmosphere()



# 绘制取餐点、送达点、传送点周围的闪烁光圈。
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

# 从玩家位置到当前目标画一条虚线导航，降低玩家迷路概率。
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



# 根据玩家当前状态选择待机、跑步、受伤或倒地动画。
def current_player_animation_name():
    if player["state"] in {"hurt", "die"}:
        return player["state"]
    return "run" if player["moving"] else "idle"


# 绘制主角。如果素材加载失败，会用简单图形作为备用外观。
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

# 绘制所有丧尸，然后再绘制主角，保证主角在画面层级上更清楚。
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


# 绘制雨天、台风、雾天的屏幕效果。
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


# 把秒数格式化成 00:00，供顶部 HUD 显示。
def format_seconds(seconds):
    seconds = max(0, int(seconds))
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


# ===== HUD 组件 =====
# 下面的函数是顶部像素风界面的组件：面板、发光线、血量、按键提示、任务进度条等。
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


# 绘制顶部信息栏：标题、时间、分数、订单、血量、天气和操作提示。
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

# 根据当前任务状态，绘制取餐点、送达点或跨地图连接口提示。
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



# 绘制游戏结束界面，并提示玩家按空格或 R 重玩。
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


# 绘制地图切换时的闪黑动画。
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


def draw_cover_image(image):
    scale = max(WIDTH / image.get_width(), HEIGHT / image.get_height())
    scaled_size = (int(image.get_width() * scale), int(image.get_height() * scale))
    scaled = pygame.transform.smoothscale(image, scaled_size)
    screen.blit(scaled, ((WIDTH - scaled_size[0]) // 2, (HEIGHT - scaled_size[1]) // 2))


def draw_start_button(rect):
    hover = rect.collidepoint(pygame.mouse.get_pos())
    glow = int(40 + pulse(3) * (76 if hover else 48))
    halo = pygame.Surface((rect.w + 22, rect.h + 22), pygame.SRCALPHA)
    pygame.draw.rect(halo, (83, 255, 151, glow), halo.get_rect(), border_radius=8)
    screen.blit(halo, (rect.x - 11, rect.y - 11))
    fill = (25, 45, 33) if hover else (13, 25, 22)
    pygame.draw.rect(screen, fill, rect, border_radius=6)
    pygame.draw.rect(screen, (114, 255, 154), rect, 2, border_radius=6)
    pygame.draw.line(screen, (255, 64, 76), (rect.x + 14, rect.y + 7), (rect.x + 42, rect.y + 7), 2)
    pygame.draw.line(screen, (255, 64, 76), (rect.right - 42, rect.bottom - 7), (rect.right - 14, rect.bottom - 7), 2)
    center_text("开始配送", rect.centerx, rect.centery - 2, (235, 255, 232), FONT_BOLD)


def draw_start_horror_layers(elapsed):
    tint = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    tint.fill((0, 0, 0, 42))
    pygame.draw.rect(tint, (3, 26, 15, 64), (0, 0, WIDTH, HEIGHT))
    pygame.draw.rect(tint, (0, 0, 0, 86), (0, 0, WIDTH, 132))
    pygame.draw.rect(tint, (0, 0, 0, 74), (0, 126, WIDTH, HEIGHT - 218))
    pygame.draw.rect(tint, (0, 0, 0, 116), (0, HEIGHT - 146, WIDTH, 146))
    screen.blit(tint, (0, 0))

    vignette = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for i in range(12):
        alpha = 11 + i * 8
        pygame.draw.rect(vignette, (0, 0, 0, alpha), (i * 11, i * 7, WIDTH - i * 22, HEIGHT - i * 14), 1)
    screen.blit(vignette, (0, 0))

    fog = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for i in range(7):
        y = int(128 + i * 62 + math.sin(elapsed * 0.55 + i) * 13)
        x = int(-90 + ((elapsed * 18 + i * 137) % (WIDTH + 180)))
        pygame.draw.rect(fog, (54, 255, 135, 18), (x - 160, y, 330, 18), border_radius=9)
        pygame.draw.rect(fog, (176, 255, 201, 10), (x - 80, y + 13, 240, 10), border_radius=5)
    screen.blit(fog, (0, 0))

    for scan_y in range(0, HEIGHT, 5):
        pygame.draw.line(screen, (0, 0, 0), (0, scan_y), (WIDTH, scan_y), 1)


def draw_start_title(elapsed):
    shake = 1 if int(elapsed * 11) % 17 == 0 else 0
    title = "重生之我在末日厦大送外卖"
    center_text(title, WIDTH // 2 + 2 + shake, 48 + 2, (72, 0, 9), FONT_TITLE)
    center_text(title, WIDTH // 2 - 1, 48, (255, 218, 118), FONT_TITLE)
    pygame.draw.line(screen, (117, 255, 156), (WIDTH // 2 - 185, 76), (WIDTH // 2 + 185, 76), 1)
    pygame.draw.line(screen, (136, 23, 34), (WIDTH // 2 - 120, 80), (WIDTH // 2 + 120, 80), 2)
    center_text("灾变第三日  /  XMU EMERGENCY DELIVERY", WIDTH // 2, 100, (143, 231, 172), FONT_MINI)


def draw_start_story_panel(rect):
    panel = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(panel, (4, 10, 10, 104), panel.get_rect(), border_radius=6)
    pygame.draw.rect(panel, (105, 255, 151, 90), panel.get_rect(), 1, border_radius=6)
    screen.blit(panel, rect)

    corner = 24
    color = (151, 255, 172)
    danger = (210, 35, 45)
    pygame.draw.line(screen, color, rect.topleft, (rect.x + corner, rect.y), 2)
    pygame.draw.line(screen, color, rect.topleft, (rect.x, rect.y + corner), 2)
    pygame.draw.line(screen, color, rect.topright, (rect.right - corner, rect.y), 2)
    pygame.draw.line(screen, color, rect.topright, (rect.right, rect.y + corner), 2)
    pygame.draw.line(screen, danger, (rect.x + 24, rect.y + 30), (rect.right - 24, rect.y + 30), 1)
    text("灾变档案 / 校园配送员幸存记录", rect.x + 28, rect.y + 10, (244, 81, 88), FONT_MINI)


def wrap_text_line(line, font, max_width):
    wrapped = []
    current = ""
    for char in line:
        candidate = current + char
        if current and font.size(candidate)[0] > max_width:
            wrapped.append(current)
            current = char
        else:
            current = candidate
    if current:
        wrapped.append(current)
    return wrapped or [""]


def load_start_intro():
    intro_path = Path(__file__).resolve().parent / "引言.txt"
    try:
        raw_lines = intro_path.read_text(encoding="utf-8-sig").splitlines()
    except OSError:
        raw_lines = ["末日封校，丧尸游荡。", "你是唯一还在接单的校园外卖员。"]

    lines = []
    previous_blank = False
    for raw in raw_lines:
        line = raw.strip()
        if not line:
            if not previous_blank:
                lines.append("")
            previous_blank = True
            continue
        lines.extend(wrap_text_line(line, FONT_SMALL, WIDTH - 220))
        previous_blank = False
    return lines


def typewriter_visible_lines(lines, elapsed, char_time=0.075, line_pause=0.55):
    visible_lines = []
    remaining = elapsed
    for line in lines:
        if not line:
            visible_lines.append("")
            remaining -= line_pause
            continue

        reveal_time = len(line) * char_time
        if remaining <= 0:
            visible_lines.append("")
        elif remaining < reveal_time:
            visible_count = max(1, int(remaining / char_time))
            visible_lines.append(line[:visible_count])
        else:
            visible_lines.append(line)
        remaining -= reveal_time + line_pause
    return visible_lines


def draw_start_screen():
    """绘制开始界面：背景图 + 引言文字 + 开始按钮。"""
    global START_BG_IMAGE, START_INTRO_LINES
    if START_BG_IMAGE is None:
        bg_path = Path(__file__).resolve().parent / "start_bg.png"
        START_BG_IMAGE = pygame.image.load(str(bg_path)).convert()
    if START_INTRO_LINES is None:
        START_INTRO_LINES = load_start_intro()

    elapsed = time.time() - START_SCREEN_STARTED
    draw_cover_image(START_BG_IMAGE)
    draw_start_horror_layers(elapsed)
    draw_start_title(elapsed)

    panel = pygame.Rect(WIDTH // 2 - 365, 124, 730, HEIGHT - 220)
    draw_start_story_panel(panel)
    line_height = FONT_SMALL.get_height() + 7
    max_text_height = panel.h - 58
    y = panel.y + 50
    visible_intro_lines = typewriter_visible_lines(START_INTRO_LINES, elapsed)
    last_line_rect = None
    for line in visible_intro_lines:
        if not line:
            y += line_height // 2
            continue
        if y > panel.y + 42 + max_text_height:
            break
        img = FONT_SMALL.render(line, True, (214, 232, 216))
        rect = img.get_rect(center=(WIDTH // 2, y))
        shadow = FONT_SMALL.render(line, True, (65, 9, 12))
        screen.blit(shadow, (rect.x + 2, rect.y + 1))
        screen.blit(img, rect)
        if line:
            last_line_rect = rect
        y += line_height

    if last_line_rect and int(time.time() * 2.2) % 2 == 0:
        cursor = pygame.Rect(last_line_rect.right + 5, last_line_rect.y + 3, 8, last_line_rect.h - 6)
        pygame.draw.rect(screen, (129, 255, 153), cursor)

    button = pygame.Rect(WIDTH // 2 - 92, HEIGHT - 66, 184, 42)
    draw_start_button(button)
    center_text("空格 / 回车 / E / 鼠标点击", WIDTH // 2, HEIGHT - 14, (168, 190, 183), FONT_MINI)
