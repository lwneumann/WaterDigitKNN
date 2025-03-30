from digit_scores import digit_scores
from time import sleep
from collections import Counter
import pygame, heapq


SCREEN_SIZE = 280, 280
ANAL_MODE = SCREEN_SIZE[0], SCREEN_SIZE[1] + 80
SCREEN_TITLE = "Digits"
BACKGROUND_COLOR = 0, 0, 0
TEXT_COLOR = 255, 255, 255
ANAL_BG = 50, 50, 50
DRAW_COLOR = 255, 255, 255
BRUSH_RADIUS = 10
MAKE_VISIBLE = True
PAUSE_BETWEEN_TIME = 0.05
FRAME_PAUSE = 0.005
K_SETTING = 5
HEAD_COLOR = 255, 0, 0
PASS_COLOR = 19, 35, 69


class Window:
    def __init__(self):
        self.setup()
        self.run()
        return

    def setup(self):
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont('Comic Sans MS', 30)
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption(SCREEN_TITLE)
        self.running = True
        self.clear_grid()
        # Analysis
        self.analizing = False
        self.flattened = []
        self.cell_size = SCREEN_SIZE[0] // 28
        self.guess = ''
        return

    def clear_grid(self):
        self.grid = [[0 for _ in range(SCREEN_SIZE[0])] for _ in range(SCREEN_SIZE[1])]
        return

    def draw_screen(self):
        if not self.analizing:
            self.screen.fill(BACKGROUND_COLOR)
            # Render drawn pixels
            for y in range(SCREEN_SIZE[1]):
                for x in range(SCREEN_SIZE[0]):
                    if self.grid[y][x] > 0:
                        self.screen.set_at((x, y), DRAW_COLOR)
        else:
            self.screen.fill(ANAL_BG)
            self.draw_flat_grid()
            if self.guess != '':
                self.draw_text(self.guess)
        pygame.display.flip()
        return
    
    def draw_flat_grid(self, g=None, f=False):
        if g is None:
            g = self.flattened
        
        for i in range(28):
            for j in range(28):
                cell = g[i * 28 + j]
                color = 0, 0, 0
                if cell == 1:
                    color = DRAW_COLOR
                elif cell == 'X':
                    color = HEAD_COLOR
                elif cell == 2:
                    color = PASS_COLOR
                rect = pygame.Rect(j * self.cell_size, i * self.cell_size, self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, color, rect)
        if f:
            pygame.display.flip()
        return

    def run(self):
        while self.running:
            self.handle_events()
            if not self.analizing:
                # Check mouse input
                if pygame.mouse.get_pressed()[0]:
                    x, y = pygame.mouse.get_pos()
                    self.draw_circle(x, y, BRUSH_RADIUS)
            self.draw_screen()
        pygame.quit()
        return

    def resize_and_flatten(self, g=None, size=28):
        if g is None:
            g = self.grid

        n = len(g)
        scale = n / size
        new_grid = []
        
        for i in range(size):
            row = []
            for j in range(size):
                orig_i = int(i * scale)
                orig_j = int(j * scale)
                row.append(g[orig_i][orig_j])
            new_grid.extend(row)
        return new_grid

    def draw_text(self, t):
        text_surface = self.font.render(t, True, TEXT_COLOR)
        text_position = (10, ANAL_MODE[1] - 75)
        self.screen.blit(text_surface, text_position)
        return

    def prep_screen(self):
        self.flattened = self.resize_and_flatten()
        score = self.get_score()
        self.draw_flat_grid()
        self.guess = do_knn(score)
        self.screen = pygame.display.set_mode(ANAL_MODE)
        return

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
        
        keys = pygame.key.get_pressed()
        # Quit
        if keys[pygame.K_ESCAPE]:
            self.running = False
        elif keys[pygame.K_r]:
            self.clear_grid()
            self.analizing = False
            self.screen = pygame.display.set_mode(SCREEN_SIZE)
        elif keys[pygame.K_SPACE]:
            self.analizing = True
            self.prep_screen()
        return

    def draw_circle(self, cx, cy, radius):
        for y in range(max(0, cy - radius), min(SCREEN_SIZE[1], cy + radius)):
            for x in range(max(0, cx - radius), min(SCREEN_SIZE[0], cx + radius)):
                if (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2:  # Check if within circle
                    self.grid[y][x] = 1
        return

    def fill(self, pixels, constraint=None):
        pixels = pixels.copy()
        start = 14

        # Setup constraint
        height = len(pixels) // 28
        v_mid = height//2

        if constraint is not None:
            mapping = {
                # Down (bottom center)
                (1, 0): (height - 1, 14),
                # Up (top center)
                (-1, 0): (0, 14),
                # Right (right center)
                (0, 1): (v_mid, 27),
                # Left (left center)
                (0, -1): (v_mid, 0)
            }
            r, c = mapping[constraint]
            start = r * 28 + c

        # Start filling
        pixels[start] = 'X'

        while 'X' in pixels:
            active_locations = [i for i, x in enumerate(pixels) if x == "X"]
            
            if MAKE_VISIBLE:
                self.draw_flat_grid(pixels, True)
                sleep(FRAME_PAUSE)

            for p in active_locations:
                row, col = divmod(p, 28)

                for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    # Don't move in the blocked direction
                    if (dx, dy) == constraint:
                        continue
                    
                    new_row, new_col = row + dx, col + dy
                    
                    # Ensure within bounds
                    if 0 <= new_row < height and 0 <= new_col < 28:
                        new_pos = new_row * 28 + new_col
                        if pixels[new_pos] == 0:
                            pixels[new_pos] = 'X'

                # Mark as visited
                pixels[p] = 2
        
        if MAKE_VISIBLE:
            self.draw_flat_grid(pixels, True)
            sleep(PAUSE_BETWEEN_TIME)
        return pixels

    def get_score(self):
        height = len(self.flattened)//28
        score = []

        # Vertical
        for dir in [(1, 0), (-1, 0)]:
            filled = self.fill(self.flattened, dir)
            # Left Half
            score.append(score_pix([filled[r * 28 + c] for r in range(height) for c in range(14)]))
            # Right half
            score.append(score_pix([filled[r * 28 + c] for r in range(height) for c in range(14, 28)]))
        
        # Horizontal
        for dir in [(0, 1), (0, -1)]:
            filled = self.fill(self.flattened, dir)
            # Top half
            score.append(score_pix(filled[:len(self.flattened)//2]))
            # Bottom Half
            score.append(score_pix(filled[len(self.flattened)//2:]))
        
        # Submerged
        score.append(score_pix(self.fill(self.flattened)))

        return score


def score_pix(p):
    return p.count(0) / len(p)


def distance(p1, p2):
    return sum([(p1[i] - p2[i])**2 for i in range(len(p1))])**0.5


def do_knn(score, K=K_SETTING):
    guesses = []

    for d in digit_scores:
        dist = distance(d[:-1], score)
        label = d[-1]
        
        # Maintain a max-heap of size K for the K smallest distances
        if len(guesses) < K:
            # Store as (-dist, label) for max-heap
            heapq.heappush(guesses, (-dist, label))
        else:
            # Only keep the K closest
            heapq.heappushpop(guesses, (-dist, label))
    
    # Labels of K closest neighbors
    labels = [label for _, label in guesses]
    return str(Counter(labels).most_common(1)[0][0])


if __name__ == "__main__":
    Window()
