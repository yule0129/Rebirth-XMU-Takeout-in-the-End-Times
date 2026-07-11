# config.py 专门存放“全局规则”和“基础参数”。
# 好处是以后想调速度、血量、地图格子大小时，不用去 main.py 里到处找。

# 地图每个格子的像素大小，以及顶部信息栏 HUD 的高度。
TILE = 32
HUD = 108
FPS = 60

# 每单外卖的限时，超过这个时间就算配送失败。
ORDER_LIMIT = 48

# 主角移动速度。下雨时会使用 RAIN_SPEED，让极端天气对玩法产生影响。
PLAYER_SPEED = 230
RAIN_SPEED = 150

# 丧尸普通巡逻和发现主角后的追击速度。
ZOMBIE_SPEED = 78
ZOMBIE_CHASE_SPEED = 110

# 碰撞半径：角色和丧尸不是用整张图片碰撞，而是用身体中心的小圆来判断，更顺滑。
PLAYER_RADIUS = 10
PLAYER_SPRITE_SIZE = 54
PLAYER_ANIMATION_FPS = 10
PLAYER_HURT_DURATION = 0.9
PLAYER_DIE_DURATION = 1.15
ZOMBIE_RADIUS = 10
ZOMBIE_SPRITE_SIZE = 44
ZOMBIE_ANIMATION_FPS = 7

# 每张地图统一采用 32 列、18 行，方便多地图切换时保持窗口大小一致。
MAP_COLS = 32
MAP_ROWS = 18

# 主角开局出生点，对应地图格子坐标，不是屏幕像素坐标。
START_TILE = (4, 0)

# R=粉色路线 B=黑色障碍 L=蓝色芙蓉湖/不可通行 G=黄色取餐点 D=红色送达点
# P=深绿色操场，可通行 F=浅绿色足球场，可通行 K=土黄色篮球场，可通行
# WALKABLE 表示“可以站上去”的地形，碰撞检测会用它判断能不能走。
WALKABLE = {"R", "G", "D", "P", "F", "K", "S", "C"}
