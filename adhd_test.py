import threading
import pygame
import time
import random
import os
import csv
import eog_logger
from datetime import datetime
from pygame.locals import *

pygame.init()
font = pygame.font.Font(None, 36)

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
clock = pygame.time.Clock()

black = (0, 0, 0)
white = (255, 255, 255)

WIDTH = screen.get_width()
HEIGHT = screen.get_height()

# ---------------- CSV / Command Setup ----------------
CSV_FILE = "session.csv"
COMMAND_FILE = "eog_command.txt"

HEADER = [
    "source",
    "event",
    "computer_time",
    "experiment_time"
]

# ALWAYS OVERWRITE FILE
with open(CSV_FILE, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(HEADER)

experiment_start_time = time.perf_counter()

def computer_time():
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S.%f %Z")

def experiment_time():
    return time.perf_counter() - experiment_start_time

def write_row(row):
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(row)

def log_task_event(event_name):
    write_row([
        "TASK",
        event_name,
        computer_time(),
        experiment_time()
    ])

def request_recalibration():
    with open(COMMAND_FILE, "w") as f:
        f.write("r")

    log_task_event("arduino_recalibration_requested")

def cleanup_and_exit():
    pygame.quit()
    exit()

def instructions(line1, line2, line3):
    waiting = True

    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                log_task_event("aborted")
                cleanup_and_exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if line1 == "CALIBRATION":
                        request_recalibration()
                        time.sleep(2)

                    waiting = False

                elif event.key == pygame.K_ESCAPE:
                    log_task_event("aborted")
                    cleanup_and_exit()

        screen.fill(black)

        rendered1 = font.render(line1, True, white)
        rendered2 = font.render(line2, True, white)
        rendered3 = font.render(line3, True, white)

        screen.blit(rendered1, rendered1.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50)))
        screen.blit(rendered2, rendered2.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        screen.blit(rendered3, rendered3.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50)))

        pygame.display.update()
        clock.tick(60)

# ---------------- Calibration ----------------
instructions(
    "CALIBRATION",
    "Look at the white dot in the center,",
    "Try not to move your eyes."
)

task_time = pygame.time.get_ticks()
running = True
log_task_event("calibration_start")

threading.Thread(target=eog_logger.start_logger, daemon=True).start()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            log_task_event("aborted_calibration")
            cleanup_and_exit()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                log_task_event("aborted_calibration")
                cleanup_and_exit()

    screen.fill(black)
    pygame.draw.circle(screen, white, (WIDTH // 2, HEIGHT // 2), 10)
    pygame.display.update()
    clock.tick(60)

    time_passed = pygame.time.get_ticks() - task_time

    if time_passed >= 10000:
        running = False
        log_task_event("calibration_end")

# ---------------- Task 1 - Fixation ----------------
instructions(
    "TASK 1",
    "Look at the white dot in the center,",
    "Try not to move your eyes."
)

for trial_num in [1, 2]:
    task_time = pygame.time.get_ticks()
    running = True
    log_task_event(f"task1_trial{trial_num}_start")

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                log_task_event("aborted")
                cleanup_and_exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    log_task_event("aborted")
                    cleanup_and_exit()

        time_passed = pygame.time.get_ticks() - task_time

        screen.fill(black)
        pygame.draw.circle(screen, white, (WIDTH // 2, HEIGHT // 2), 10)
        pygame.display.update()
        clock.tick(60)

        if time_passed >= 30000:
            running = False
            log_task_event(f"task1_trial{trial_num}_end")

    if trial_num == 1:
        instructions(
            "Trial 1 done!",
            "Rest your eyes.",
            "Trial 2 will start shortly."
        )

# ---------------- Task 2 - Saccade ----------------
num_of_trials = 40
trial_num = 0
trial_start_time = pygame.time.get_ticks()
fixation_duration = random.uniform(1500, 2000)
side = random.choice(["left", "right"])
phase = "fixation"

instructions(
    "TASK 2",
    "Look at the center, a dot will appear left or right,",
    "Follow it as fast as you can."
)

running = True
log_task_event("task2_start")

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            log_task_event("aborted")
            cleanup_and_exit()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                log_task_event("aborted")
                cleanup_and_exit()

    time_elapsed = pygame.time.get_ticks() - trial_start_time
    screen.fill(black)

    if phase == "fixation":
        pygame.draw.circle(screen, white, (WIDTH // 2, HEIGHT // 2), 10)

        if time_elapsed >= fixation_duration:
            log_task_event(f"target_{side}")
            phase = "target"

    elif phase == "target":
        if side == "left":
            pygame.draw.circle(screen, white, (WIDTH // 2 - WIDTH // 3, HEIGHT // 2), 10)
        else:
            pygame.draw.circle(screen, white, (WIDTH // 2 + WIDTH // 3, HEIGHT // 2), 10)

        if time_elapsed >= fixation_duration + 1000:
            trial_num += 1

            if trial_num >= num_of_trials:
                log_task_event("task2_end")
                running = False
            else:
                trial_start_time = pygame.time.get_ticks()
                fixation_duration = random.uniform(1500, 2000)
                side = random.choice(["left", "right"])
                phase = "fixation"

    pygame.display.update()
    clock.tick(60)

# ---------------- Test Run ----------------
instructions(
    "TEST RUN",
    "Look at the square, when a dot appears left or right,",
    "look the OPPOSITE direction from the dot."
)

num_of_trials = 5
trial_num = 0
trial_start_time = pygame.time.get_ticks()
fixation_duration = random.uniform(1500, 2000)
side = random.choice(["left", "right"])
phase = "fixation"

running = True
log_task_event("practice_run_start")

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            log_task_event("aborted_practice")
            cleanup_and_exit()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                log_task_event("aborted_practice")
                cleanup_and_exit()

    time_elapsed = pygame.time.get_ticks() - trial_start_time
    screen.fill(black)

    if phase == "fixation":
        pygame.draw.rect(screen, white, (WIDTH // 2 - 5, HEIGHT // 2 - 5, 10, 10))

        if time_elapsed >= fixation_duration:
            phase = "target"

    elif phase == "target":
        if side == "left":
            pygame.draw.circle(screen, white, (WIDTH // 2 - WIDTH // 3, HEIGHT // 2), 10)
        else:
            pygame.draw.circle(screen, white, (WIDTH // 2 + WIDTH // 3, HEIGHT // 2), 10)

        if time_elapsed >= fixation_duration + 1000:
            trial_num += 1

            if trial_num >= num_of_trials:
                log_task_event("practice_run_end")
                running = False
            else:
                trial_start_time = pygame.time.get_ticks()
                fixation_duration = random.uniform(1500, 2000)
                side = random.choice(["left", "right"])
                phase = "fixation"

    pygame.display.update()
    clock.tick(60)

# ---------------- Task 3 - Antisaccade ----------------
num_of_trials = 40
trial_num = 0
trial_start_time = pygame.time.get_ticks()
fixation_duration = random.uniform(1500, 2000)
side = random.choice(["left", "right"])
phase = "fixation"

instructions(
    "TASK 3",
    "Look at the square, when a dot appears left or right,",
    "look the OPPOSITE direction from the dot."
)

running = True
log_task_event("task3_start")

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            log_task_event("aborted")
            cleanup_and_exit()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                log_task_event("aborted")
                cleanup_and_exit()

    time_elapsed = pygame.time.get_ticks() - trial_start_time
    screen.fill(black)

    if phase == "fixation":
        pygame.draw.rect(screen, white, (WIDTH // 2 - 5, HEIGHT // 2 - 5, 10, 10))

        if time_elapsed >= fixation_duration:
            log_task_event(f"anti_target_{side}")
            phase = "target"

    elif phase == "target":
        if side == "left":
            pygame.draw.circle(screen, white, (WIDTH // 2 - WIDTH // 3, HEIGHT // 2), 10)
        else:
            pygame.draw.circle(screen, white, (WIDTH // 2 + WIDTH // 3, HEIGHT // 2), 10)

        if time_elapsed >= fixation_duration + 1000:
            trial_num += 1

            if trial_num >= num_of_trials:
                log_task_event("task3_end")
                running = False
            else:
                trial_start_time = pygame.time.get_ticks()
                fixation_duration = random.uniform(1500, 2000)
                side = random.choice(["left", "right"])
                phase = "fixation"

    pygame.display.update()
    clock.tick(60)

pygame.quit()