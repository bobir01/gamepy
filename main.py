import pygame
import random
import sys

pygame.init()

# Screen dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Buggy Jumper Game")

# Game variables
GRAVITY = 0.5
PLAYER_JUMP_SPEED = -10
SCROLL_SPEED = 2
PLAYER_SPEED = 5  # Speed for horizontal movement

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Load images
try:
    player_image = pygame.image.load('player.png').convert_alpha()
except pygame.error as e:
    print(f"Error loading player.png: {e}")
    pygame.quit()
    sys.exit()

try:
    coin_image = pygame.image.load('coin.png').convert_alpha()
except pygame.error as e:
    print(f"Error loading coin.png: {e}")
    pygame.quit()
    sys.exit()

try:
    background_image = pygame.image.load('sky.png').convert()
except pygame.error as e:
    print(f"Error loading background.png: {e}")
    pygame.quit()
    sys.exit()

# Optionally, scale images to desired size
player_image = pygame.transform.scale(player_image, (60, 50))
coin_image = pygame.transform.scale(coin_image, (25, 25))
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Classes
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
        self.velocity_y = 0
        self.velocity_x = 0  # Horizontal velocity

    def update(self):
        self.velocity_y += GRAVITY

        keys = pygame.key.get_pressed()

        # Jumping logic
        if keys[pygame.K_SPACE]:
            self.velocity_y = PLAYER_JUMP_SPEED

        # Horizontal movement logic
        self.velocity_x = 0  # Reset horizontal velocity each frame
        if keys[pygame.K_LEFT]:
            self.velocity_x = -PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.velocity_x = PLAYER_SPEED

        # Update position
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y

        # Screen boundary checks
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

        # Check if player has fallen off the bottom
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Wall(pygame.sprite.Sprite):
    def __init__(self, y_pos):
        super().__init__()
        self.image = pygame.Surface((100, 20))
        self.image.fill((128, 64, 0))
        self.rect = self.image.get_rect(center=(random.randint(50, SCREEN_WIDTH - 50), y_pos))

    def update(self):
        self.rect.y += SCROLL_SPEED  # Walls move downwards
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Coin(pygame.sprite.Sprite):
    def __init__(self, y_pos):
        super().__init__()
        self.image = coin_image
        self.rect = self.image.get_rect(center=(random.randint(15, SCREEN_WIDTH - 15), y_pos))

    def update(self):
        self.rect.y += SCROLL_SPEED + 1  # Coins move downwards faster
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

def game_over_screen(final_score):
    font_large = pygame.font.SysFont(None, 72)
    font_small = pygame.font.SysFont(None, 36)
    game_over_text = font_large.render("Game Over", True, BLACK)
    score_text = font_small.render(f"Score: {final_score}", True, BLACK)
    play_again_text = font_small.render("Press Enter to Play Again", True, BLACK)
    quit_text = font_small.render("Press Esc to Quit", True, BLACK)

    while True:
        screen.fill(WHITE)
        screen.blit(game_over_text, game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60)))
        screen.blit(score_text, score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))
        screen.blit(play_again_text, play_again_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)))
        screen.blit(quit_text, quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80)))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Handle key presses
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Enter key to play again
                    return  # Exit the game over screen and restart the game
                if event.key == pygame.K_ESCAPE:  # Escape key to quit
                    pygame.quit()
                    sys.exit()

def main():
    # Sprite groups
    player_group = pygame.sprite.Group()
    wall_group = pygame.sprite.Group()
    coin_group = pygame.sprite.Group()

    player = Player()
    player_group.add(player)

    # Create an initial wall under the player
    initial_wall = Wall(player.rect.bottom + 10)
    initial_wall.rect.centerx = player.rect.centerx  # Align wall with the player
    wall_group.add(initial_wall)

    # Background scrolling variables
    bg_scroll = 0

    # Main game loop
    clock = pygame.time.Clock()
    running = True
    score = 0
    font = pygame.font.SysFont(None, 36)

    # Wall generation timer
    WALL_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(WALL_EVENT, 1500)  # New wall every 1.5 seconds

    # Coin generation timer
    COIN_EVENT = pygame.USEREVENT + 2
    pygame.time.set_timer(COIN_EVENT, 2000)  # New coin every 2 seconds

    while running:
        clock.tick(60)  # 60 FPS

        # Scroll background
        bg_scroll += SCROLL_SPEED  # Move background downwards
        if bg_scroll >= SCREEN_HEIGHT:
            bg_scroll = 0

        # Draw the background
        screen.blit(background_image, (0, bg_scroll - SCREEN_HEIGHT))
        screen.blit(background_image, (0, bg_scroll))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == WALL_EVENT:
                wall = Wall(-20)  # Spawn walls at the top
                wall_group.add(wall)

            if event.type == COIN_EVENT:
                coin = Coin(-15)  # Spawn coins at the top
                coin_group.add(coin)

        # Update sprites
        player_group.update()
        wall_group.update()
        coin_group.update()

        # Collision detection with walls
        wall_collisions = pygame.sprite.spritecollide(player, wall_group, False)
        if wall_collisions:
            # Align player with the wall
            player.rect.bottom = wall_collisions[0].rect.top
            player.velocity_y = 0

        # Collision detection with coins
        coins_collected = pygame.sprite.spritecollide(player, coin_group, True)
        score += len(coins_collected)

        # Draw sprites
        wall_group.draw(screen)
        coin_group.draw(screen)
        player_group.draw(screen)

        # Display score
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))

        # Check if player has fallen off the screen
        if not player_group:
            running = False  # End game

        pygame.display.flip()

    # After the game loop ends, show the game over screen
    game_over_screen(score)

# Run the game loop
while True:
    main()
