import pygame
import sys
import random
import itertools
from pygame.locals import *

# 初始化pygame
pygame.init()

# 屏幕设置
WIDTH, HEIGHT = 800, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("24点游戏 - 点击卡片构建表达式")

# 颜色定义
BACKGROUND = (25, 25, 40)
PANEL_COLOR = (40, 40, 60)
CARD_COLOR = (70, 130, 180)
OPERATOR_COLOR = (220, 120, 70)
HIGHLIGHT_COLOR = (100, 200, 225)
TEXT_COLOR = (240, 240, 240)
BUTTON_COLOR = (80, 180, 100)
BUTTON_HOVER = (100, 200, 120)
ERROR_COLOR = (220, 80, 80)
SUCCESS_COLOR = (80, 200, 120)
EXPRESSION_COLOR = (60, 60, 90)

# 多语言支持
LANGUAGES = {
    "zh": {
        "title": "24点游戏 - 点击卡片构建表达式",
        "num_label": "数字卡片",
        "op_label": "运算符卡片",
        "check_button": "检查答案",
        "reset_button": "重置游戏",
        "undo_button": "撤销",
        "lang_button": "English",
        "success": "正确！结果为24！",
        "fail": "错误！请再试一次。",
        "instructions": [
            "游戏规则：",
            "1. 使用4个数字和运算符组成表达式，使其结果为24",
            "2. 每个数字必须使用一次",
            "3. 运算符包括 +, -, ×, ÷ 和括号",
            "4. 点击卡片添加到表达式区域"
        ]
    },
    "en": {
        "title": "24 Game - Click Cards to Build Expression",
        "num_label": "Number Cards",
        "op_label": "Operator Cards",
        "check_button": "Check Answer",
        "reset_button": "Reset Game",
        "undo_button": "Undo",
        "lang_button": "中文",
        "success": "Correct! The result is 24!",
        "fail": "Wrong! Please try again.",
        "instructions": [
            "Game Rules:",
            "1. Use the 4 numbers and operators to form an expression equal to 24",
            "2. Each number must be used exactly once",
            "3. Operators include +, -, ×, ÷, and parentheses",
            "4. Click cards to add to expression area"
        ]
    }
}

# 当前语言
current_lang = "zh"

# 字体
font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 28)


class Card:
    def __init__(self, x, y, width, height, text, color, is_operator=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.is_operator = is_operator
        self.original_pos = (x, y)
        self.in_expression = False
        self.expression_pos = (0, 0)
        self.used = False  # 标记数字卡片是否已使用

    def draw(self, surface):
        # 如果在表达式中，使用不同的颜色
        if self.in_expression:
            pygame.draw.rect(surface, EXPRESSION_COLOR, self.rect, border_radius=10)
            pygame.draw.rect(surface, HIGHLIGHT_COLOR, self.rect, 2, border_radius=10)
        else:
            # 如果是数字卡片且已使用，变暗
            if not self.is_operator and self.used:
                pygame.draw.rect(surface, (color[0] // 2, color[1] // 2, color[2] // 2), self.rect, border_radius=10)
            else:
                pygame.draw.rect(surface, self.color, self.rect, border_radius=10)

            pygame.draw.rect(surface, (150, 150, 170), self.rect, 2, border_radius=10)

        text_surf = font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_click(self, pos):
        if self.rect.collidepoint(pos):
            # 如果是数字卡片且已使用，不能再点击
            if not self.is_operator and self.used:
                return False
            return True
        return False

    def reset(self):
        self.in_expression = False
        self.used = False
        self.rect.x, self.rect.y = self.original_pos

    def move_to_expression(self, pos):
        self.in_expression = True
        if not self.is_operator:
            self.used = True
        self.expression_pos = pos
        self.rect.x, self.rect.y = pos


class Button:
    def __init__(self, x, y, width, height, text, color=BUTTON_COLOR):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover = False

    def draw(self, surface):
        color = BUTTON_HOVER if self.hover else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, HIGHLIGHT_COLOR, self.rect, 2, border_radius=8)

        text_surf = small_font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == MOUSEBUTTONDOWN and self.hover:
            return True
        return False


def generate_numbers():
    """生成4个1-13之间的数字，并确保有解"""
    while True:
        numbers = [random.randint(1, 13) for _ in range(4)]
        if has_solution(numbers):
            return numbers


def has_solution(numbers):
    """检查给定的4个数字是否有解（24点）"""
    # 尝试所有可能的排列和运算符组合
    for perm in itertools.permutations(numbers):
        a, b, c, d = perm
        for ops in itertools.product(["+", "-", "*", "/"], repeat=3):
            op1, op2, op3 = ops
            # 尝试不同的括号组合
            expressions = [
                f"(({a} {op1} {b}) {op2} {c}) {op3} {d}",
                f"({a} {op1} ({b} {op2} {c})) {op3} {d}",
                f"{a} {op1} (({b} {op2} {c}) {op3} {d})",
                f"{a} {op1} ({b} {op2} ({c} {op3} {d}))",
                f"({a} {op1} {b}) {op2} ({c} {op3} {d})"
            ]

            for expr in expressions:
                try:
                    result = eval(expr)
                    # 处理浮点数精度问题
                    if abs(result - 24) < 1e-6:
                        return True
                except ZeroDivisionError:
                    continue
    return False


def evaluate_expression(cards):
    """安全地计算表达式"""
    try:
        # 将卡片组合成表达式
        expr = ""
        for card in cards:
            expr += card.text

        # 替换运算符为Python可识别的形式
        expr = expr.replace("×", "*").replace("÷", "/")
        return eval(expr)
    except (ZeroDivisionError, SyntaxError, TypeError, NameError):
        return None


def create_game_objects():
    """创建游戏对象"""
    numbers = generate_numbers()
    number_cards = []
    operator_cards = []

    # 创建数字卡片
    for i, num in enumerate(numbers):
        x = 150 + i * 120
        y = 100
        number_cards.append(Card(x, y, 80, 80, str(num), CARD_COLOR))

    # 创建运算符卡片
    operators = ["+", "-", "×", "÷", "(", ")"]
    for i, op in enumerate(operators):
        x = 150 + i * 80
        y = 220
        operator_cards.append(Card(x, y, 60, 60, op, OPERATOR_COLOR, True))

    return number_cards, operator_cards


def toggle_language():
    """切换语言"""
    global current_lang
    current_lang = "en" if current_lang == "zh" else "zh"


def main():
    global current_lang
    clock = pygame.time.Clock()

    # 创建游戏对象
    number_cards, operator_cards = create_game_objects()
    expression_area = pygame.Rect(100, 350, 600, 80)
    expression_cards = []
    message = ""
    message_color = TEXT_COLOR

    # 创建按钮
    check_button = Button(WIDTH // 2 - 100, 550, 200, 50, LANGUAGES[current_lang]["check_button"])
    reset_button = Button(WIDTH // 2 - 100, 450, 200, 50, LANGUAGES[current_lang]["reset_button"], (180, 100, 80))
    lang_button = Button(WIDTH - 150, 20, 120, 40, LANGUAGES[current_lang]["lang_button"], (100, 100, 180))
    undo_button = Button(WIDTH // 2 - 100, 500, 200, 40, LANGUAGES[current_lang]["undo_button"], (150, 150, 200))

    # 复杂运算示例
    complex_ops = [
        "√(x) - 平方根",
        "x² - 平方",
        "x! - 阶乘",
        "|x| - 绝对值",
        "log₂(x) - 对数",
        "eˣ - 指数",
        "sin(x) - 正弦",
        "cos(x) - 余弦"
    ]

    # 表达式位置计数器
    expression_x = expression_area.x + 20
    expression_y = expression_area.y + 40

    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            # 处理按钮事件
            if check_button.handle_event(event):
                result = evaluate_expression(expression_cards)
                if result is not None and abs(result - 24) < 1e-6:
                    message = LANGUAGES[current_lang]["success"]
                    message_color = SUCCESS_COLOR
                else:
                    message = LANGUAGES[current_lang]["fail"]
                    message_color = ERROR_COLOR

            if reset_button.handle_event(event):
                number_cards, operator_cards = create_game_objects()
                expression_cards = []
                message = ""
                expression_x = expression_area.x + 20
                # 重置所有卡片
                for card in number_cards + operator_cards:
                    card.reset()

            if lang_button.handle_event(event):
                toggle_language()
                # 更新按钮文本
                check_button.text = LANGUAGES[current_lang]["check_button"]
                reset_button.text = LANGUAGES[current_lang]["reset_button"]
                lang_button.text = LANGUAGES[current_lang]["lang_button"]
                undo_button.text = LANGUAGES[current_lang]["undo_button"]

            if undo_button.handle_event(event) and expression_cards:
                # 撤销最后一步
                last_card = expression_cards.pop()
                last_card.reset()

                # 更新位置计数器
                if last_card.text in ["(", ")"]:
                    expression_x -= 40
                else:
                    expression_x -= 60

            # 处理卡片点击事件
            if event.type == MOUSEBUTTONDOWN:
                # 检查数字卡片
                for card in number_cards:
                    if card.handle_click(event.pos) and not card.used:
                        # 添加到表达式
                        expression_cards.append(card)
                        card.move_to_expression((expression_x, expression_y))

                        # 更新下一个卡片位置
                        expression_x += 60
                        break

                # 检查运算符卡片
                for card in operator_cards:
                    if card.handle_click(event.pos):
                        # 添加到表达式
                        expression_cards.append(card)
                        card.move_to_expression((expression_x, expression_y))

                        # 更新下一个卡片位置
                        expression_x += 60
                        break

        # 更新按钮悬停状态
        check_button.hover = check_button.rect.collidepoint(mouse_pos)
        reset_button.hover = reset_button.rect.collidepoint(mouse_pos)
        lang_button.hover = lang_button.rect.collidepoint(mouse_pos)
        undo_button.hover = undo_button.rect.collidepoint(mouse_pos)

        # 绘制界面
        screen.fill(BACKGROUND)

        # 绘制标题
        title = font.render(LANGUAGES[current_lang]["title"], True, HIGHLIGHT_COLOR)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))

        # 绘制数字卡片区域
        pygame.draw.rect(screen, PANEL_COLOR, (50, 70, 700, 100), border_radius=10)
        num_label = small_font.render(LANGUAGES[current_lang]["num_label"], True, TEXT_COLOR)
        screen.blit(num_label, (60, 75))

        # 绘制运算符卡片区域
        pygame.draw.rect(screen, PANEL_COLOR, (50, 190, 700, 100), border_radius=10)
        op_label = small_font.render(LANGUAGES[current_lang]["op_label"], True, TEXT_COLOR)
        screen.blit(op_label, (60, 195))

        # 绘制表达式区域
        pygame.draw.rect(screen, PANEL_COLOR, expression_area, border_radius=10)
        pygame.draw.rect(screen, HIGHLIGHT_COLOR, expression_area, 2, border_radius=10)

        # 绘制表达式标签
        expr_label = small_font.render("表达式区域:", True, TEXT_COLOR)
        screen.blit(expr_label, (expression_area.x + 10, expression_area.y - 30))

        # 绘制消息
        if message:
            msg_surf = font.render(message, True, message_color)
            screen.blit(msg_surf, (WIDTH // 2 - msg_surf.get_width() // 2, 320))

        # 绘制卡片
        for card in number_cards + operator_cards:
            card.draw(screen)

        # 绘制按钮
        check_button.draw(screen)
        reset_button.draw(screen)
        lang_button.draw(screen)
        undo_button.draw(screen)

        # 绘制游戏说明
        instructions = LANGUAGES[current_lang]["instructions"]
        for i, text in enumerate(instructions):
            inst_surf = small_font.render(text, True, (180, 180, 200))
            screen.blit(inst_surf, (WIDTH // 2 - 200, 600 + i * 25))

        # 绘制复杂运算示例
        complex_title = small_font.render("复杂运算示例（仅展示）:", True, HIGHLIGHT_COLOR)
        screen.blit(complex_title, (20, HEIGHT - 120))

        for i, op in enumerate(complex_ops):
            op_surf = small_font.render(op, True, (200, 200, 100))
            screen.blit(op_surf, (20 + (i % 4) * 190, HEIGHT - 90 + (i // 4) * 25))

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()