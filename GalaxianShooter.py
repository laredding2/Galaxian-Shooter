import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 100, 255)
RED = (255, 50, 50)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)

# Game setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galaxian")
clock = pygame.time.Clock()

class ExplosionParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 6)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = random.randint(20, 40)
        self.max_life = self.life
        self.size = random.randint(2, 5)
        self.color = random.choice([RED, ORANGE, YELLOW, WHITE])
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2  # Gravity
        self.life -= 1
        
    def draw(self, screen):
        if self.life > 0:
            alpha_ratio = self.life / self.max_life
            size = int(self.size * alpha_ratio)
            if size > 0:
                pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)

class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 60
        self.width = 40
        self.height = 30
        self.speed = 5
        self.bullets = []
        self.invulnerable = False
        self.invuln_timer = 0
        
    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width:
            self.x += self.speed
            
    def shoot(self):
        self.bullets.append(Bullet(self.x + self.width // 2, self.y))
        
    def draw(self, screen):
        # Draw player ship with flashing effect if invulnerable
        if self.invulnerable and self.invuln_timer % 10 < 5:
            return  # Don't draw (creates flashing effect)
            
        # Draw player ship
        points = [
            (self.x + self.width // 2, self.y),
            (self.x, self.y + self.height),
            (self.x + self.width, self.y + self.height)
        ]
        pygame.draw.polygon(screen, GREEN, points)
        
    def update_invulnerability(self):
        if self.invulnerable:
            self.invuln_timer += 1
            if self.invuln_timer > 120:  # 2 seconds at 60 FPS
                self.invulnerable = False
                self.invuln_timer = 0
        
    def update_bullets(self, enemies):
        for bullet in self.bullets[:]:
            bullet.move()
            if bullet.y < 0:
                self.bullets.remove(bullet)
            else:
                # Check collision with enemies
                for enemy in enemies[:]:
                    if enemy.check_collision(bullet):
                        if bullet in self.bullets:
                            self.bullets.remove(bullet)
                        enemies.remove(enemy)
                        return 100  # Score
        return 0

class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 8
        self.width = 3
        self.height = 10
        
    def move(self):
        self.y -= self.speed
        
    def draw(self, screen):
        pygame.draw.rect(screen, YELLOW, (self.x, self.y, self.width, self.height))

class Enemy:
    def __init__(self, x, y, row, speed_multiplier=1.0):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.width = 30
        self.height = 25
        self.speed = 1 * speed_multiplier
        self.diving = False
        self.dive_speed = 3 * speed_multiplier
        self.row = row
        self.color = CYAN if row < 2 else RED if row < 4 else BLUE
        self.bullets = []
        self.speed_multiplier = speed_multiplier
        
    def move_formation(self, direction, down=False):
        if not self.diving:
            self.x += direction * self.speed
            if down:
                self.y += 10
                
    def start_dive(self, player_x):
        self.diving = True
        self.target_x = player_x
        
    def update_dive(self):
        if self.diving:
            # Move toward player and down
            if self.x < self.target_x:
                self.x += self.dive_speed
            elif self.x > self.target_x:
                self.x -= self.dive_speed
                
            self.y += self.dive_speed
            
            # Return to formation if off screen
            if self.y > HEIGHT:
                self.diving = False
                self.x = self.start_x
                self.y = self.start_y
                
    def shoot(self):
        self.bullets.append(EnemyBullet(self.x + self.width // 2, self.y + self.height, self.speed_multiplier))
        
    def check_collision(self, bullet):
        return (bullet.x >= self.x and bullet.x <= self.x + self.width and
                bullet.y >= self.y and bullet.y <= self.y + self.height)
    
    def check_player_collision(self, player):
        return (self.x < player.x + player.width and
                self.x + self.width > player.x and
                self.y < player.y + player.height and
                self.y + self.height > player.y)
                
    def draw(self, screen):
        # Draw enemy ship
        points = [
            (self.x + self.width // 2, self.y + self.height),
            (self.x, self.y),
            (self.x + self.width, self.y)
        ]
        pygame.draw.polygon(screen, self.color, points)
        # Wings
        pygame.draw.rect(screen, self.color, (self.x - 5, self.y + 10, 5, 8))
        pygame.draw.rect(screen, self.color, (self.x + self.width, self.y + 10, 5, 8))

class EnemyBullet:
    def __init__(self, x, y, speed_multiplier=1.0):
        self.x = x
        self.y = y
        self.speed = 5 * speed_multiplier
        self.width = 3
        self.height = 10
        
    def move(self):
        self.y += self.speed
        
    def draw(self, screen):
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
        
    def check_collision(self, player):
        return (self.x >= player.x and self.x <= player.x + player.width and
                self.y >= player.y and self.y <= player.y + player.height)

def create_enemy_formation(speed_multiplier=1.0):
    enemies = []
    rows = 5
    cols = 10
    start_x = 100
    start_y = 80
    spacing_x = 60
    spacing_y = 50
    
    for row in range(rows):
        for col in range(cols):
            x = start_x + col * spacing_x
            y = start_y + row * spacing_y
            enemies.append(Enemy(x, y, row, speed_multiplier))
            
    return enemies

def play_death_cutscene(screen, player, enemies, score, lives, frame_count):
    """Play explosion animation when player loses a life"""
    # Create explosion particles
    particles = []
    for _ in range(30):
        particles.append(ExplosionParticle(
            player.x + player.width // 2,
            player.y + player.height // 2
        ))
    
    font = pygame.font.Font(None, 36)
    large_font = pygame.font.Font(None, 72)
    
    # Animation duration
    cutscene_frames = 90  # 1.5 seconds
    
    for frame in range(cutscene_frames):
        clock.tick(FPS)
        
        # Continue enemy movement during cutscene
        for enemy in enemies:
            enemy.update_dive()
        
        # Drawing
        screen.fill(BLACK)
        
        # Draw stars background
        for i in range(50):
            x = (i * 137) % WIDTH
            y = (i * 219 + frame_count + frame) % HEIGHT
            pygame.draw.circle(screen, WHITE, (x, y), 1)
        
        # Update and draw explosion particles
        for particle in particles:
            particle.update()
            particle.draw(screen)
        
        # Draw enemies (but not their bullets)
        for enemy in enemies:
            enemy.draw(screen)
        
        # Draw UI
        score_text = font.render(f"Score: {score}", True, WHITE)
        lives_text = font.render(f"Lives: {lives}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (WIDTH - 150, 10))
        
        # Flash "SHIP DESTROYED" message
        if frame < 60 and frame % 20 < 15:
            destroyed_text = large_font.render("SHIP DESTROYED!", True, RED)
            text_rect = destroyed_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(destroyed_text, text_rect)
        
        pygame.display.flip()
        
        # Allow quitting during cutscene
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
    
    return True

def main():
    player = Player()
    enemies = create_enemy_formation()
    score = 0
    lives = 3
    game_over = False
    game_speed = 1.0  # Speed multiplier
    
    direction = 1
    move_down = False
    frame_count = 0
    shoot_cooldown = 0
    
    font = pygame.font.Font(None, 36)
    
    running = True
    while running:
        clock.tick(FPS)
        frame_count += 1
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and shoot_cooldown == 0 and not game_over:
                    player.shoot()
                    shoot_cooldown = 15
                if event.key == pygame.K_r and game_over:
                    # Restart game
                    player = Player()
                    enemies = create_enemy_formation()
                    score = 0
                    lives = 3
                    game_over = False
                    game_speed = 1.0
                    direction = 1
                    frame_count = 0
                    
        if not game_over:
            keys = pygame.key.get_pressed()
            player.move(keys)
            player.update_invulnerability()
            
            if shoot_cooldown > 0:
                shoot_cooldown -= 1
            
            # Move enemies in formation
            if frame_count % 30 == 0:
                edge_hit = False
                for enemy in enemies:
                    if not enemy.diving:
                        if enemy.x <= 10 or enemy.x >= WIDTH - 40:
                            edge_hit = True
                            break
                            
                if edge_hit:
                    direction *= -1
                    move_down = True
                else:
                    move_down = False
                    
                for enemy in enemies:
                    enemy.move_formation(direction, move_down)
                    
            # Random enemy diving
            if frame_count % 120 == 0 and len(enemies) > 0:
                diver = random.choice(enemies)
                if not diver.diving:
                    diver.start_dive(player.x)
                    
            # Update diving enemies
            for enemy in enemies:
                enemy.update_dive()
                
                # Check if enemy collides with player
                if enemy.check_player_collision(player) and not player.invulnerable:
                    lives -= 1
                    
                    if lives > 0:
                        # Play death cutscene
                        continuing = play_death_cutscene(screen, player, enemies, score, lives, frame_count)
                        if not continuing:
                            running = False
                            break
                        
                        # Reset player position and make invulnerable
                        player.x = WIDTH // 2
                        player.y = HEIGHT - 60
                        player.invulnerable = True
                        player.invuln_timer = 0
                        
                        # Clear all enemy bullets
                        for e in enemies:
                            e.bullets.clear()
                    else:
                        game_over = True
                        break
                
                # Enemy shooting
                if random.random() < 0.002:
                    enemy.shoot()
                    
            # Update player bullets
            score += player.update_bullets(enemies)
            
            # Update enemy bullets
            for enemy in enemies:
                for bullet in enemy.bullets[:]:
                    bullet.move()
                    if bullet.y > HEIGHT:
                        enemy.bullets.remove(bullet)
                    elif bullet.check_collision(player) and not player.invulnerable:
                        enemy.bullets.remove(bullet)
                        lives -= 1
                        
                        if lives > 0:
                            # Play death cutscene
                            continuing = play_death_cutscene(screen, player, enemies, score, lives, frame_count)
                            if not continuing:
                                running = False
                                break
                            
                            # Reset player position and make invulnerable
                            player.x = WIDTH // 2
                            player.y = HEIGHT - 60
                            player.invulnerable = True
                            player.invuln_timer = 0
                            
                            # Clear all enemy bullets
                            for e in enemies:
                                e.bullets.clear()
                        else:
                            game_over = True
                            
            # Check if all enemies destroyed
            if len(enemies) == 0:
                game_speed *= 1.2  # Increase speed by 20%
                enemies = create_enemy_formation(game_speed)
                
        # Drawing
        screen.fill(BLACK)
        
        # Draw stars background
        for i in range(50):
            x = (i * 137) % WIDTH
            y = (i * 219 + frame_count) % HEIGHT
            pygame.draw.circle(screen, WHITE, (x, y), 1)
        
        player.draw(screen)
        
        for bullet in player.bullets:
            bullet.draw(screen)
            
        for enemy in enemies:
            enemy.draw(screen)
            for bullet in enemy.bullets:
                bullet.draw(screen)
                
        # Draw UI
        score_text = font.render(f"Score: {score}", True, WHITE)
        lives_text = font.render(f"Lives: {lives}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (WIDTH - 150, 10))
        
        if game_over:
            game_over_text = font.render("GAME OVER", True, RED)
            restart_text = font.render("Press R to Restart", True, WHITE)
            screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2 - 20))
            screen.blit(restart_text, (WIDTH // 2 - 130, HEIGHT // 2 + 20))
        
        pygame.display.flip()
        
    pygame.quit()

if __name__ == "__main__":
    main()