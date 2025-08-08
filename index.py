import pygame
import random
import sys

# Configuration
CELL_SIZE = 30
COLS = 10
ROWS = 20
WIDTH = CELL_SIZE * COLS
HEIGHT = CELL_SIZE * ROWS
FPS = 60
FALL_EVENT = pygame.USEREVENT + 1
FALL_SPEED = 500  # milliseconds

# Colors - Pastel palette
BLACK = (0, 0, 0)
GRAY = (220, 220, 220)
WHITE = (255, 255, 255)
COLORS = [
    (173, 216, 230),  # Pastel blue (I)
    (176, 196, 222),  # Pastel slate blue (J)
    (255, 218, 185),  # Pastel peach (L)
    (255, 255, 224),  # Pastel yellow (O)
    (144, 238, 144),  # Pastel green (S)
    (216, 191, 216),  # Pastel purple (T)
    (255, 182, 193),  # Pastel pink (Z)
]

# Tetromino shapes
SHAPES = [
    [[(0, 1), (1, 1), (2, 1), (3, 1)], [(2, 0), (2, 1), (2, 2), (2, 3)]],
    [[(0, 0), (0, 1), (1, 1), (2, 1)], [(1, 0), (2, 0), (1, 1), (1, 2)], [
        (0, 1), (1, 1), (2, 1), (2, 2)], [(1, 0), (1, 1), (1, 2), (0, 2)]],
    [[(2, 0), (0, 1), (1, 1), (2, 1)], [(1, 0), (1, 1), (1, 2), (2, 2)], [
        (0, 1), (1, 1), (2, 1), (0, 2)], [(0, 0), (1, 0), (1, 1), (1, 2)]],
    [[(1, 0), (2, 0), (1, 1), (2, 1)]],
    [[(1, 1), (2, 1), (0, 2), (1, 2)], [(1, 0), (1, 1), (2, 1), (2, 2)]],
    [[(1, 0), (0, 1), (1, 1), (2, 1)], [(1, 0), (1, 1), (2, 1), (1, 2)], [
        (0, 1), (1, 1), (2, 1), (1, 2)], [(1, 0), (0, 1), (1, 1), (1, 2)]],
    [[(0, 1), (1, 1), (1, 2), (2, 2)], [(2, 0), (1, 1), (2, 1), (1, 2)]],
]


class Piece:
    def __init__(self, x, y, shape_idx):
        self.x = x
        self.y = y
        self.shape_idx = shape_idx
        self.rot = 0
        self.shape = SHAPES[shape_idx]
        self.color = COLORS[shape_idx]

    def cells(self):
        state = self.shape[self.rot % len(self.shape)]
        return [(self.x + dx, self.y + dy) for dx, dy in state]

    def rotate(self, dir=1):
        old = self.rot
        self.rot = (self.rot + dir) % len(self.shape)
        return old


class Tetris:
    def __init__(self):
        self.grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.score = 0
        self.level = 1
        self.lines = 0
        self.game_over = False
        self.spawn()
        self.next_piece = self.random_piece()

    def random_piece(self):
        idx = random.randrange(len(SHAPES))
        return Piece(COLS // 2 - 2, 0, idx)

    def spawn(self):
        if hasattr(self, 'next_piece') and self.next_piece:
            self.current = self.next_piece
            self.next_piece = self.random_piece()
        else:
            self.current = self.random_piece()
            self.next_piece = self.random_piece()
        if not self.valid_position(self.current, self.current.x, self.current.y):
            self.game_over = True

    def valid_position(self, piece, nx, ny):
        for x, y in [(nx + dx, ny + dy) for dx, dy in piece.shape[piece.rot % len(piece.shape)]]:
            if x < 0 or x >= COLS or y < 0 or y >= ROWS:
                return False
            if self.grid[y][x] is not None:
                return False
        return True

    def lock_piece(self):
        for x, y in self.current.cells():
            if 0 <= y < ROWS and 0 <= x < COLS:
                self.grid[y][x] = self.current.color
        self.clear_lines()
        self.spawn()

    def clear_lines(self):
        new_grid = [row for row in self.grid if any(
            cell is None for cell in row)]
        cleared = ROWS - len(new_grid)
        if cleared > 0:
            for _ in range(cleared):
                new_grid.insert(0, [None for _ in range(COLS)])
            self.grid = new_grid
            self.lines += cleared
            self.score += (100 * cleared) * self.level
            new_level = self.lines // 10 + 1
            if new_level > self.level:
                self.level = new_level
                pygame.time.set_timer(FALL_EVENT, max(
                    50, FALL_SPEED - (self.level - 1) * 50))

    def move(self, dx, dy):
        if self.game_over:
            return False
        if self.valid_position(self.current, self.current.x + dx, self.current.y + dy):
            self.current.x += dx
            self.current.y += dy
            return True
        return False

    def rotate(self, dir=1):
        if self.game_over:
            return
        old_rot = self.current.rotate(dir)
        if not self.valid_position(self.current, self.current.x, self.current.y):
            for kick in (-1, 1, -2, 2):
                if self.valid_position(self.current, self.current.x + kick, self.current.y):
                    self.current.x += kick
                    return
            self.current.rot = old_rot

    def hard_drop(self):
        if self.game_over:
            return
        while self.move(0, 1):
            self.score += 2
        self.lock_piece()

    def soft_drop(self):
        moved = self.move(0, 1)
        if moved:
            self.score += 1
        else:
            self.lock_piece()


def draw_grid(surface):
    for y in range(ROWS):
        for x in range(COLS):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE,
                               CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, GRAY, rect, 1)


def draw_matrix(surface, grid):
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell:
                rect = pygame.Rect(x * CELL_SIZE, y *
                                   CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(surface, cell, rect)
                pygame.draw.rect(surface, BLACK, rect, 1)


def draw_piece(surface, piece):
    for x, y in piece.cells():
        if y >= 0:
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE,
                               CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, piece.color, rect)
            pygame.draw.rect(surface, BLACK, rect, 1)


def draw_next(surface, piece):
    s = pygame.Surface((CELL_SIZE * 6, CELL_SIZE * 4))
    s.fill((245, 245, 245))
    for dx, dy in piece.shape[piece.rot % len(piece.shape)]:
        rect = pygame.Rect((dx+1) * CELL_SIZE, (dy+1) *
                           CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(s, piece.color, rect)
        pygame.draw.rect(s, BLACK, rect, 1)
    return s


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH + 200, HEIGHT))
    pygame.display.set_caption('Tetris - Pastel Edition')
    clock = pygame.time.Clock()
    pygame.time.set_timer(FALL_EVENT, FALL_SPEED)

    game = Tetris()
    paused = False

    font = pygame.font.SysFont('consolas', 20)
    big_font = pygame.font.SysFont('consolas', 36)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                if game.game_over:
                    if event.key == pygame.K_r:
                        game = Tetris()
                else:
                    if not paused:
                        if event.key == pygame.K_LEFT:
                            game.move(-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            game.move(1, 0)
                        elif event.key == pygame.K_DOWN:
                            game.soft_drop()
                        elif event.key == pygame.K_UP or event.key == pygame.K_x:
                            game.rotate(1)
                        elif event.key == pygame.K_z:
                            game.rotate(-1)
                        elif event.key == pygame.K_SPACE:
                            game.hard_drop()
            elif event.type == FALL_EVENT and not paused and not game.game_over:
                game.move(0, 1) or game.lock_piece()

        screen.fill((250, 250, 250))

        play_surf = pygame.Surface((WIDTH, HEIGHT))
        play_surf.fill((255, 255, 255))
        draw_matrix(play_surf, game.grid)
        if not game.game_over:
            draw_piece(play_surf, game.current)
        screen.blit(play_surf, (0, 0))
        draw_grid(screen)

        sx = WIDTH + 20
        screen.fill((250, 250, 250), (WIDTH, 0, 200, HEIGHT))
        score_surf = font.render(f'Score: {game.score}', True, (70, 70, 70))
        lines_surf = font.render(f'Lines: {game.lines}', True, (70, 70, 70))
        level_surf = font.render(f'Level: {game.level}', True, (70, 70, 70))
        screen.blit(score_surf, (sx, 20))
        screen.blit(lines_surf, (sx, 50))
        screen.blit(level_surf, (sx, 80))

        next_s = draw_next(screen, game.next_piece)
        screen.blit(next_s, (sx, 120))
        nx_label = font.render('Next:', True, (70, 70, 70))
        screen.blit(nx_label, (sx, 100))

        if paused:
            p = big_font.render('PAUSED', True, (70, 70, 70))
            screen.blit(p, (WIDTH//2 - p.get_width()//2,
                        HEIGHT//2 - p.get_height()//2))
        if game.game_over:
            go = big_font.render('GAME OVER', True, (200, 70, 70))
            instr = font.render('Press R to restart', True, (70, 70, 70))
            screen.blit(go, (WIDTH//2 - go.get_width()//2,
                        HEIGHT//2 - go.get_height()//2 - 20))
            screen.blit(instr, (WIDTH//2 - instr.get_width()//2,
                        HEIGHT//2 - instr.get_height()//2 + 20))

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    main()
