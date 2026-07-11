# assets.py 负责加载游戏素材：字体、主角动画、丧尸动画，以及图片背景清理。
# 这里不写游戏规则，只把图片处理成 pygame 能直接绘制的 Surface。

from pathlib import Path

import pygame

from config import PLAYER_SPRITE_SIZE, ZOMBIE_SPRITE_SIZE

# 按优先级寻找中文字体，保证地图名称、提示文字不会显示成方框。
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

# 游戏中不同用途的字体对象，绘制 HUD、地图标签、结算界面时会用到。
FONT_TITLE = font(26, True)
FONT = font(21)
FONT_BOLD = font(21, True)
FONT_SMALL = font(16)
FONT_MINI = font(12)
FONT_BIG = font(44, True)


# 清理丧尸图片的浅色/白色背景。
# 算法从图片边缘开始 flood fill，只把连到边缘的浅色区域变透明，尽量保留角色本体。
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


# 判断一张切出来的小图里是否真的有角色像素，避免把空白帧加入动画。
def surface_has_visible_pixels(surface, min_pixels=12):
    count = 0
    for py in range(surface.get_height()):
        for px in range(surface.get_width()):
            if surface.get_at((px, py)).a > 10:
                count += 1
                if count >= min_pixels:
                    return True
    return False


# 从丧尸精灵表中按固定 48x48 小格切出每一帧。
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


# 从 character/丧尸 文件夹中逐张读取 png，适合用户自己替换丧尸素材。
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


# 优先读取整张丧尸精灵表；如果没有精灵表，就退回读取文件夹里的多张图片。
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

# 清理主角图片的深色边缘和灰色标注，让外卖员在游戏中不出现底色或框线。
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

# 从主角精灵表中切出待机、跑步、受伤、倒地四组动画。
# 跳跃动画暂时不用，所以这里没有加入 jump 状态。
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


# 程序启动时就把主角动画加载好，后面绘制时只需要按状态取帧。
PLAYER_ANIMATIONS = load_player_animations()
