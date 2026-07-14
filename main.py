import math
import random
import time
from pathlib import Path

import pygame

# 初始化 pygame，并设置窗口标题。
pygame.init()
pygame.display.set_caption("重生之我在末日厦大送外卖")


# 导入配置参数和地图数据。星号导入是为了让课堂项目代码更直观，少写很多模块前缀。
from config import *
from maps import *

# 当前所在地图的运行时数据。
# 切换地图时，GAME_MAP、点位名称、巡逻路线都会跟着刷新。
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
from assets import *

# LABELS 合并当前地图所有要显示的文字，包括宿舍、取餐点、食堂和操场等。
LABELS = {}
LABELS.update(DORM_NAMES)
LABELS.update(PICKUP_NAMES)
LABELS.update(CANTEENS)
LABELS.update(PLAYGROUND_LABELS)
PICKUPS = list(PICKUP_NAMES.keys())
DORMS = list(DORM_NAMES.keys())
ZOMBIE_PATROLS = MAP_DATA[current_map_id]["patrols"]

COLORS = {
    "R": (176, 176, 176),#浅灰
    "B": (9, 9, 9),#纯黑
    "L": (142, 212, 224),#浅蓝
    "G": (255, 234, 34),#黄色
    "D": (244, 32, 42),#红色
    "C": (145, 61, 174),#紫色
    "P": (34, 179, 78),#绿色
    "F": (232, 250, 218),#浅绿
    "K": (166, 101, 66),#土黄色
    "S": (34, 179, 78),#深绿
    "H": (84, 111, 145),#灰蓝
}

# 极端天气对应的显示文字。天气不仅显示在 HUD，也会影响移动和视野。
WEATHER_TEXT = {
    "normal": "??",
    "rain": "???????",
    "typhoon": "???????",
    "fog": "???????",
}

# 游戏全局状态：分数、订单、天气、提示文字、是否 Game Over 等都放在这里。
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

# transition 保存地图切换黑屏动画的状态，避免传送点来回触发。
transition = {"active": False, "started": 0.0, "target_map": None, "spawn": None, "switched": False}


# 下面三个函数只负责把地图编号和格子坐标转换成可读名称，用于提示和 HUD。
def map_name(map_id):
    return MAP_NAMES.get(map_id, f"??{map_id + 1}")


def pickup_name(map_id, pos):
    return MAP_DATA[map_id]["pickup_names"][pos]


def dorm_name(map_id, pos):
    return MAP_DATA[map_id]["dorm_names"][pos]


# 切换当前地图数据，但不负责移动玩家。
# switch_map 会调用它，并额外处理玩家出生点和丧尸刷新。
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


# 把“地图格子坐标”转换成“屏幕像素中心点”，角色和丧尸移动都使用像素坐标。
def tile_center(pos):
    x, y = pos
    return x * TILE + TILE / 2, HUD + y * TILE + TILE / 2


# 玩家状态字典保存位置、血量、动画状态、朝向、无敌时间等。
# 用字典是为了初学阶段更容易直接看到每个字段的意义。
player = {"x": tile_center(START_TILE)[0],
           "y": tile_center(START_TILE)[1], 
           "hp": 3, "state": "idle",
            "state_started": time.time(),
            "moving": False, 
            "flip": False, 
            "locked_until": 0.0, 
            "invulnerable_until": 0.0}
zombies = []


# 根据当前地图的巡逻路线重新生成丧尸，切换地图和重开游戏时都会调用。
def rebuild_zombies():
    zombies.clear()
    for patrol in ZOMBIE_PATROLS:
        x, y = tile_center(patrol[0])
        zombies.append({"x": x, 
                        "y": y, 
                        "patrol": patrol, 
                        "target": 1, 
                        "chasing": False, 
                        "flip": False, 
                        "frame_offset": random.random() * 10
                        })


rebuild_zombies()


# 真正执行地图切换：刷新地图、重建丧尸、把玩家放到目标出生点。
def switch_map(map_id, spawn_tile):
    set_current_map(map_id)
    rebuild_zombies()
    player["x"], player["y"] = tile_center(spawn_tile)
    player["moving"] = False
    player["state"] = "idle"
    player["state_started"] = time.time()
    pressed_keys.clear()


# 当任务目标不在当前地图时，找到最近的连接口，用来画导航线。
def nearest_connection_to(target_map_id):
    # 筛选：当前地图所有能跳转到目标地图的传送门
    options = [(tile, data) for tile, data in CONNECTIONS.get(current_map_id, {}).items() if data[0] == target_map_id]
    if not options:
        return None
    px, py = player["x"], player["y"]
    # 按玩家到传送门中心点距离排序，取最近一个传送格子
    return min(options, key=lambda item: dist((px, py), tile_center(item[0])))[0]


# 计算当前应该引导玩家去哪里：
# 有订单时引导到送达点，没有订单时引导到取餐点；跨地图时先引导到传送口。
def target_tile_for_guide():
    if carrying_order:
        if target_dorm_map == current_map_id:
            return target_dorm, (255, 222, 68)
        return nearest_connection_to(target_dorm_map), (116, 214, 255)
    if active_pickup_map == current_map_id:
        return active_pickup, (255, 158, 64)
    return nearest_connection_to(active_pickup_map), (116, 214, 255)


# 开始黑屏转场动画，转场中不允许重复触发新的传送。
def start_transition(target_map, spawn_tile):
    if transition["active"]:
        return
    transition.update({"active": True, 
                       "started": time.time(), 
                       "target_map": target_map, 
                       "spawn": spawn_tile, 
                       "switched": False})
    set_message(f"\u6b63\u5728\u524d\u5f80 {map_name(target_map)}...", 2)


# 更新黑屏转场：先变黑，中间切换地图，再逐渐亮回来。
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


# 玩家走到传送点格子时，检查是否需要切换地图。
def check_map_connection():
    if transition["active"] or player["state"] in {"hurt", "die"}:
        return
    gx, gy = grid_from_pixel(player["x"], player["y"])
    target = CONNECTIONS.get(current_map_id, {}).get((gx, gy))
    if target:
        start_transition(target[0], target[1])


# ===== 碰撞与距离工具 =====
# 这些函数把像素位置、格子位置、可通行判断统一起来，角色和丧尸共用。
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


# 在顶部 HUD 下方显示一段临时提示文字。
def set_message(text, seconds=3):
    global message, message_until
    message = text
    message_until = time.time() + seconds


# 随机刷新取餐点，并尽量避开刚刚用过的点。
def refresh_pickup(except_key=None):
    global active_pickup_map, active_pickup
    choices = [item for item in ALL_PICKUPS if item != except_key]
    active_pickup_map, active_pickup = random.choice(choices or ALL_PICKUPS)


# ===== 订单系统 =====
# 订单可能在同一张地图内完成，也可能要求跨地图配送。
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


# 成功送达：加分、统计救援人数，然后刷新下一次取餐点。
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


# 订单失败：扣分、统计失败次数，并刷新取餐点。
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


# 玩家按 E 或空格时触发交互：根据当前状态决定是取餐还是送达。
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


# 兼容“按住移动”和“按键集合”两种判断，让 WASD 移动更稳定。
def key_down(code):
    keys = pygame.key.get_pressed()
    return code in pressed_keys or keys[code]


# 处理受伤和死亡动画结束后的后续结果。
# 受伤：回到出发点并短暂无敌；死亡：进入 Game Over。
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


# 根据 WASD/方向键更新玩家移动，同时处理雨天减速、草地减速和台风偏移。
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


# 丧尸 AI：距离玩家较近时追击，否则沿设定巡逻路线移动。
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


# 随机触发极端天气；天气结束后恢复正常。
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


# 玩家被丧尸抓到时的处理：扣血、丢失订单、重置丧尸位置，并播放受伤/死亡动画。
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


# 每帧检查订单是否超时、玩家是否被丧尸碰到。
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


# 加载绘制模块。
# rendering.py 中的绘制函数会直接使用 main.py 里的 screen、player、zombies 等变量。
# 这样可以把“画面绘制”和“游戏逻辑”拆开，同时避免给每个绘制函数传很多参数。
exec((Path(__file__).resolve().parent / "rendering.py").read_text(encoding="utf-8-sig"), globals())


# 重开游戏：清空分数和订单，恢复血量，回到第一张地图出生点。
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


show_start_screen = True

# ===== 主循环 =====
# 每一帧依次处理输入、更新游戏状态、绘制画面，直到玩家关闭窗口。
running = True
while running:
    dt = min(clock.tick(FPS) / 1000, 0.04)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if show_start_screen:
                if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_e):
                    show_start_screen = False
                    reset_game()
                elif event.key == pygame.K_ESCAPE:
                    running = False
                continue
            pressed_keys.add(event.key)
            if event.key == pygame.K_ESCAPE:
                running = False
            elif game_over and event.key in (pygame.K_r, pygame.K_SPACE):
                reset_game()
            elif event.key in (pygame.K_e, pygame.K_SPACE):
                interact()
        elif event.type == pygame.KEYUP:
            if not show_start_screen:
                pressed_keys.discard(event.key)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if show_start_screen and event.button == 1:
                show_start_screen = False
                reset_game()
        elif event.type == pygame.WINDOWFOCUSLOST:
            if not show_start_screen:
                pressed_keys.clear()

    if show_start_screen:
        draw_start_screen()
    elif not game_over:
        update_player_state()
        if transition["active"]:
            update_transition()
        elif player["state"] not in {"hurt", "die"}:
            update_player(dt)
            check_map_connection()
            update_zombies(dt)
            update_weather()
            check_state()

    if not show_start_screen:
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

