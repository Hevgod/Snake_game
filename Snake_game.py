import pygame
import random
import json
import os

# Khởi tạo pygame
pygame.init()

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (0, 200, 0)
BLUE = (80, 80, 255)
GRAY = (200, 200, 200)
YELLOW = (255, 255, 100)
PURPLE = (180, 0, 180)
ORANGE = (255, 150, 50)

# Cài đặt cửa sổ game
WIDTH, HEIGHT = 1000, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = (HEIGHT - 100) // GRID_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Rắn Săn Mồi - Phiên Bản Chuẩn')

# Font chữ
font = pygame.font.SysFont('Arial', 20, bold=True)
medium_font = pygame.font.SysFont('Arial', 25, bold=True)
large_font = pygame.font.SysFont('Arial', 40, bold=True)

clock = pygame.time.Clock()
FPS = 60  # Giữ FPS ở mức 60 là đủ "mượt"

# File lưu high score
HIGH_SCORE_FILE = "snake_high_scores.json"

# Nút bấm
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)

        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

# Con sờ nếch
class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)
        self.length = 1
        self.score = 0
        self.color = GREEN
        self.speed = 5  # Tốc độ di chuyển (ô/giây)
        self.max_speed = 12
        self.move_counter = 0

    def get_head_position(self):
        return self.positions[0]

    def move(self):
        head = self.get_head_position()
        x, y = self.direction
        new_head = ((head[0] + x) % GRID_WIDTH, (head[1] + y) % GRID_HEIGHT)

        if new_head in self.positions[1:]:
            return False

        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.positions.pop()

        self.speed = min(5 + self.length // 5, self.max_speed)
        return True

    def grow(self):
        self.length += 1
        self.score += 10

    def change_direction(self, direction):
        if (direction[0] * -1, direction[1] * -1) != self.direction:
            self.direction = direction

    def draw(self, surface):
        for i, p in enumerate(self.positions):
            # Đầu rắn màu xanh đậm hơn
            color = (0, 150, 0) if i == 0 else self.color
            rect = pygame.Rect((p[0] * GRID_SIZE, p[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, BLACK, rect, 1)

            # Vẽ mắt cho đầu rắn
            if i == 0:
                eye_size = GRID_SIZE // 5
                if self.direction == (1, 0):  # Phải
                    pygame.draw.rect(surface, WHITE,
                                     (rect.right - eye_size * 2, rect.top + eye_size, eye_size, eye_size))
                    pygame.draw.rect(surface, BLACK,
                                     (rect.right - eye_size * 2, rect.top + eye_size, eye_size, eye_size), 1)
                elif self.direction == (-1, 0):  # Trái
                    pygame.draw.rect(surface, WHITE, (rect.left + eye_size, rect.top + eye_size, eye_size, eye_size))
                    pygame.draw.rect(surface, BLACK, (rect.left + eye_size, rect.top + eye_size, eye_size, eye_size), 1)
                elif self.direction == (0, 1):  # Xuống
                    pygame.draw.rect(surface, WHITE,
                                     (rect.left + eye_size, rect.bottom - eye_size * 2, eye_size, eye_size))
                    pygame.draw.rect(surface, BLACK,
                                     (rect.left + eye_size, rect.bottom - eye_size * 2, eye_size, eye_size), 1)
                elif self.direction == (0, -1):  # Lên
                    pygame.draw.rect(surface, WHITE, (rect.left + eye_size, rect.top + eye_size, eye_size, eye_size))
                    pygame.draw.rect(surface, BLACK, (rect.left + eye_size, rect.top + eye_size, eye_size, eye_size), 1)

# Công cụ kiếm điểm
class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = RED
        self.randomize_position()

    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH - 1), (random.randint(0, GRID_HEIGHT - 1)))

    def draw(self, surface):
        rect = pygame.Rect((self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.color, rect)
        pygame.draw.rect(surface, BLACK, rect, 1)

        # Vẽ dấu + màu trắng ở giữa
        center_x = rect.centerx
        center_y = rect.centery
        line_length = GRID_SIZE // 3
        pygame.draw.line(surface, WHITE, (center_x - line_length // 2, center_y),
                         (center_x + line_length // 2, center_y), 2)
        pygame.draw.line(surface, WHITE, (center_x, center_y - line_length // 2),
                         (center_x, center_y + line_length // 2), 2)

# Sân chơi :))
def draw_grid(surface):
    for y in range(0, HEIGHT - 100, GRID_SIZE):
        for x in range(0, WIDTH, GRID_SIZE):
            rect = pygame.Rect((x, y), (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, WHITE, rect)
            pygame.draw.rect(surface, (220, 220, 220), rect, 1)

# Khi thua
def show_game_over(surface, score):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))

    game_over_text = large_font.render("GAME OVER", True, RED)
    score_text = medium_font.render(f"SCORE: {score}", True, WHITE)

    surface.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
    surface.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))

# Điểm
def load_high_scores():
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, 'r') as file:
            return json.load(file)
    return [0, 0, 0, 0, 0]


def save_high_scores(scores):
    with open(HIGH_SCORE_FILE, 'w') as file:
        json.dump(scores, file)


def update_high_scores(new_score):
    scores = load_high_scores()
    scores.append(new_score)
    scores = sorted(scores, reverse=True)[:5]
    save_high_scores(scores)
    return scores


def draw_high_scores(surface, scores):
    title = medium_font.render("HIGH SCORES", True, PURPLE)
    surface.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT - 95))

    for i, score in enumerate(scores):
        color = YELLOW if i == 0 else BLACK
        score_text = font.render(f"{i + 1}. {score}", True, color)
        surface.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT - 70 + i * 25))

# Cấu trúc game
def main():
    snake = Snake()
    food = Food()
    replay_button = Button(WIDTH // 2 - 75, HEIGHT // 2 + 20, 150, 40, "REPLAY", ORANGE, YELLOW)

    high_scores = load_high_scores()
    running = True
    game_over = False
    frame_count = 0

    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game_over:
                replay_button.check_hover(mouse_pos)
                if replay_button.is_clicked(mouse_pos, event):
                    snake.reset()
                    food.randomize_position()
                    game_over = False
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        snake.change_direction((0, -1))
                    elif event.key == pygame.K_DOWN:
                        snake.change_direction((0, 1))
                    elif event.key == pygame.K_LEFT:
                        snake.change_direction((-1, 0))
                    elif event.key == pygame.K_RIGHT:
                        snake.change_direction((1, 0))

        screen.fill(WHITE)
        draw_grid(screen)

        if not game_over:
            frame_count += 1
            # Di chuyển rắn dựa trên tốc độ
            if frame_count % (FPS // snake.speed) == 0:
                if not snake.move():
                    high_scores = update_high_scores(snake.score)
                    game_over = True

            if snake.get_head_position() == food.position:
                snake.grow()
                food.randomize_position()
                while food.position in snake.positions:
                    food.randomize_position()

            snake.draw(screen)
            food.draw(screen)
        else:
            snake.draw(screen)
            food.draw(screen)
            show_game_over(screen, snake.score)
            replay_button.draw(screen)

        # Panel thông tin
        info_panel = pygame.Rect(0, HEIGHT - 100, WIDTH, 100)
        pygame.draw.rect(screen, (220, 220, 220), info_panel)
        pygame.draw.rect(screen, BLACK, info_panel, 2)

        score_text = font.render(f"SCORE: {snake.score}", True, PURPLE)
        screen.blit(score_text, (20, HEIGHT - 80))

        speed_text = font.render(f"SPEED: {min(snake.speed, 12)}", True, PURPLE)
        screen.blit(speed_text, (20, HEIGHT - 50))

        draw_high_scores(screen, high_scores)

        pygame.display.update()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()