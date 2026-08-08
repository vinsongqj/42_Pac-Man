import sys
import pygame
from srcs import display

# Starts the engine
pygame.init()

# Sets window dimensions
WIDTH = 900
HEIGHT = 1000
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption("42 Pac-Man")

screen_rect = screen.get_rect()
timer = pygame.time.Clock()
fps = 60

title_text = display.Text(
    text="PAC-MAN",
    font_size=100,
    color="Yellow",
    pos=(screen_rect.centerx, 100),
    anchor="midtop"
)

subtitle_text = display.Text(
    text="PRESS SPACE TO START",
    font_size=28,
    color=(255, 255, 255),
    pos=(screen_rect.centerx, 800),
    anchor="center",
    fade_speed=0.003
)

score_text = display.Text(
    text="SCORE: 0",
    font_size=24,
    color="White",
    pos=(20, 20),
    anchor="topleft"
)

pacman = display.Image(
    image_path="assets/images/main_menu/pacman.png",
    pos=(screen_rect.centerx, 550),
    anchor="center"
    )

run = True

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    subtitle_text.fade()
    screen.fill('black')
    pacman.draw(screen)
    title_text.draw(screen)
    subtitle_text.draw(screen)
    score_text.draw(screen)
    pygame.display.flip()
    timer.tick(fps)
pygame.quit()
sys.exit()
