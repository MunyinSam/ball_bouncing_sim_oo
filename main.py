import turtle
import random
import heapq
import ball
import my_event
import paddle
import time
import math
from ball import Ball
import tkinter as tk
from tkinter import Toplevel, Label, Button
import csv
import datetime

class BouncingSimulator:
    def __init__(self, num_balls, level=1):
        self.num_balls = num_balls
        self.ball_list = []
        self.lasers = []
        self.t = 0.0
        self.pq = []
        self.HZ = 4

        # Initialize turtle settings
        turtle.speed(0)
        turtle.tracer(0)
        turtle.hideturtle()
        turtle.colormode(255)

        # Canvas dimensions
        self.canvas_width = 420
        self.canvas_height = 340

        # Game settings
        self.gamemode = "classic"
        self.done = False
        self.laser_delay = 0.4
        self.last_laser_time = 0  # Time when the last laser was fired
        self.laser_size = 1
        self.player_max_health = 3
        self.player_current_health = 3
        self.ball_spawn_interval = 2  # Interval to spawn a ball
        self.last_ball_time = 0  # Time when the last ball was spawned
        self.coins = 0
        self.score = 0
        self.level = 1
        self.level_notes_text = "LMB to shoot"

        # Writers for game stats
        self.coin_writer = turtle.Turtle()
        self.score_writer = turtle.Turtle()
        self.health_writer = turtle.Turtle()
        self.level_writer = turtle.Turtle()
        self.level_notes = turtle.Turtle()

        # Shop settings
        self.shop_window = None

        # Debugging print
        print(self.canvas_width, self.canvas_height)

        # Spawn the first wave of balls
        self.spawn_ball(amount=10)

        # Player initialization
        tom = turtle.Turtle()
        self.my_paddle = paddle.Paddle(50, 50, (37, 150, 190), tom)
        self.my_paddle.set_location([0, 0])

        # Screen settings
        self.screen = turtle.Screen()
        self.screen.onclick(self.shoot_laser)

        # Open the shop
        self.open_shop()

    # Spawn Balls -------------------------------

    def spawn_ball(self, size=0.05, input_speed=0.5, color=(255, 0, 0), 
                amount=1, health=1, reward=None):
        ball_radius = size * self.canvas_width  # Ball radius based on size
        min_distance = ball_radius * 2  # Minimum distance between balls (twice the radius to avoid overlap)
        max_attempts = 100  # Maximum attempts to find a valid position for the ball

        min_distance_from_center = 100  # Minimum distance from the center
        min_distance_from_wall = ball_radius + 50  # Ensure ball spawns at least this far from walls

        # List of existing ball positions to check for overlaps
        existing_ball_positions = [(ball.x, ball.y) for ball in self.ball_list]

        for _ in range(amount):
            attempts = 0
            while attempts < max_attempts:
                # Randomly choose an edge: 0 = top, 1 = bottom, 2 = left, 3 = right
                edge = random.randint(0, 3)

                if edge == 0:  # Top edge
                    x = random.uniform(
                        -self.canvas_width + min_distance_from_wall,
                        self.canvas_width - min_distance_from_wall
                    )
                    y = self.canvas_height - min_distance_from_wall
                elif edge == 1:  # Bottom edge
                    x = random.uniform(
                        -self.canvas_width + min_distance_from_wall,
                        self.canvas_width - min_distance_from_wall
                    )
                    y = -self.canvas_height + min_distance_from_wall
                elif edge == 2:  # Left edge
                    x = -self.canvas_width + min_distance_from_wall
                    y = random.uniform(
                        -self.canvas_height + min_distance_from_wall,
                        self.canvas_height - min_distance_from_wall
                    )
                else:  # Right edge
                    x = self.canvas_width - min_distance_from_wall
                    y = random.uniform(
                        -self.canvas_height + min_distance_from_wall,
                        self.canvas_height - min_distance_from_wall
                    )

                # Check if the ball is too close to the center
                if abs(x) < min_distance_from_center and abs(y) < min_distance_from_center:
                    continue  # Skip this position and try again

                # Check for overlaps with existing balls
                overlap = False
                for (existing_x, existing_y) in existing_ball_positions:
                    distance = math.sqrt((existing_x - x) ** 2 + (existing_y - y) ** 2)
                    if distance < min_distance:
                        overlap = True
                        break

                if not overlap:
                    # Calculate velocity directed toward the center
                    direction = math.sqrt(x ** 2 + y ** 2)
                    vx = input_speed * (-x / direction)
                    vy = input_speed * (-y / direction)

                    # Create and append the new ball
                    new_ball = ball.Ball(
                        ball_radius, x, y, vx, vy, color, len(self.ball_list),
                        health=health, reward=reward
                    )
                    self.ball_list.append(new_ball)
                    existing_ball_positions.append((x, y))
                    # print("Ball appended at position:", x, y)
                    break

                attempts += 1

    # Lasers -------------------------------

    def shoot_laser(self, x, y):
        # Calculate the direction of the laser towards the mouse position
        current_time = time.time()
        if current_time - self.last_laser_time < self.laser_delay:
            return  # Don't fire a laser if the delay has not passed

        paddle_x, paddle_y = self.my_paddle.location
        dx = x - paddle_x
        dy = y - paddle_y

        # Normalize the direction vector
        magnitude = math.sqrt(dx**2 + dy**2)
        if magnitude != 0:
            dx /= magnitude
            dy /= magnitude

        laser_speed = 10

        # Velocity of the laser
        vx = dx * laser_speed
        vy = dy * laser_speed

        laser = {
            "x": paddle_x,
            "y": paddle_y + self.my_paddle.height // 2,
            "vx": vx,
            "vy": vy,
            "width": 5 * self.laser_size,
            "height": 5 * self.laser_size
        }

        self.lasers.append(laser)
        self.last_laser_time = current_time

    def update_lasers(self, speed_cap=1):
        for laser in self.lasers[:]:
            laser["x"] += laser["vx"]
            laser["y"] += laser["vy"]

            # Check if laser goes off-screen
            if (laser["y"] > self.canvas_height or 
                    laser["x"] < -self.canvas_width or 
                    laser["x"] > self.canvas_width):
                self.lasers.remove(laser)
                continue

            # Check for collisions with balls
            for ball_obj in self.ball_list[:]:
                if (abs(laser["x"] - ball_obj.x) < ball_obj.radius + laser["width"] / 2 and
                        abs(laser["y"] - ball_obj.y) < ball_obj.radius + laser["height"] / 2):

                    # Calculate reflection
                    dx = laser["x"] - ball_obj.x
                    dy = laser["y"] - ball_obj.y
                    magnitude = math.sqrt(dx**2 + dy**2)

                    if magnitude != 0:
                        # Normalize the collision vector
                        dx /= magnitude
                        dy /= magnitude

                    # Reflect the laser velocity
                    dot_product = laser["vx"] * dx + laser["vy"] * dy
                    laser["vx"] -= 2 * dot_product * dx
                    laser["vy"] -= 2 * dot_product * dy

                    # Cap the speed of the laser
                    current_speed = math.sqrt(laser["vx"]**2 + laser["vy"]**2)
                    if current_speed > speed_cap:
                        scaling_factor = speed_cap / current_speed
                        laser["vx"] *= scaling_factor
                        laser["vy"] *= scaling_factor

                    # Handle ball health and rewards
                    if ball_obj.health > 1:
                        ball_obj.health -= 1
                    else:
                        self.ball_list.remove(ball_obj)
                        self.score += ball_obj.default_health
                        self.coins += ball_obj.default_health * 5

                        if ball_obj.reward == "increase_shooting_speed":
                            print("Shooting Speed Increased.")
                            self.laser_delay *= 0.8
                        if ball_obj.reward == "shooting_upgrade":
                            print("Increase Shooting Size.")
                            self.laser_size += 1

                    # Limit laser's lifetime by bounce count
                    if "bounces" not in laser:
                        laser["bounces"] = 0
                    laser["bounces"] += 1
                    if laser["bounces"] > 2:
                        self.lasers.remove(laser)
                    break

    def draw_lasers(self):
        for laser in self.lasers:
            turtle.penup()
            turtle.goto(
                laser["x"] - laser["width"] / 2,
                laser["y"] - laser["height"] / 2
            )
            turtle.pendown()
            turtle.color("blue")
            turtle.begin_fill()
            for _ in range(2):
                turtle.forward(laser["width"])
                turtle.left(90)
                turtle.forward(laser["height"])
                turtle.left(90)
            turtle.end_fill()\
            
    # Menu -------------------

    def show_menu(self):
        # Draw the menu screen
        turtle.clear()
        turtle.penup()
        turtle.goto(0, 50)
        turtle.color("black")
        turtle.write(
            "Tower Defence Demo", align="center", font=("Arial", 24, "bold")
        )
        turtle.goto(0, -50)
        turtle.write(
            "Press 'P' to Play (Classic Mode)", align="center", font=("Arial", 18, "normal")
        )
        turtle.goto(0, -100)
        turtle.write(
            "Press 'Q' to Play (Fast Game Mode)", align="center", font=("Arial", 18, "normal")
        )
        turtle.goto(0, -150)
        turtle.write(
            "Munyin Sam 6710545962", align="center", font=("Arial", 12, "bold")
        )
        turtle.hideturtle()
        turtle.update()

        # Wait for the user to press the play buttons
        self.screen.listen()
        self.screen.onkey(self.start_classic_mode, "p")
        self.screen.onkey(self.start_new_gamemode, "q")
        self.screen.mainloop()

    def start_classic_mode(self):
        self.gamemode = "classic"
        self.run()

    def start_new_gamemode(self):
        self.gamemode = "fast"
        self.run()

    # Setting Up Displays (set_display())
    def setup_display(self):
        self.display_elements = {
            "coins": {
                "writer": self.coin_writer,
                "position": (-360, 240),
                "text": f"Coins: {self.coins}",
            },
            "score": {
                "writer": self.score_writer,
                "position": (-360, 270),
                "text": f"Score: {self.score}",
            },
            "health": {
                "writer": self.health_writer,
                "position": (0, 50),
                "text": f"HP: {self.player_current_health}",
            },
            "level": {
                "writer": self.level_writer,
                "position": (280, 270),
                "text": f"Level: {self.level}",
            },
            "notes": {
                "writer": self.level_notes,
                "position": (0, -300),
                "text": f"Tip: {self.level_notes_text}",
            },
        }

        for key, value in self.display_elements.items():
            value["writer"].hideturtle()
            value["writer"].penup()
            value["writer"].goto(value["position"])
            self.update_display(key)

    def update_display(self, element):
        writer = self.display_elements[element]["writer"]
        text = self.display_elements[element]["text"]
        writer.clear()
        writer.write(
            text,
            align="left" if element not in ("notes", "health") else "center",
            font=("Arial", 14, "bold"),
        )

    def update_level(self):
        self.display_elements["level"]["text"] = f"Level: {self.level}"
        self.update_display("level")

    def setup_notes_display(self, tips):
        self.level_notes_text = tips  # Update the level notes
        self.display_elements["notes"]["text"] = f"Tip: {tips}"
        self.update_display("notes")

    def clear_notes(self):
        self.level_notes.clear()

    # -------------------------------------------
    # Shop

    def open_shop(self):
        self.shop_window = Toplevel()
        self.shop_window.title("Shop")
        self.shop_window.geometry("400x300")

        Label(self.shop_window, text="Upgrade Shop", font=("Arial", 16)).pack(pady=20)

        items = [
            ("Upgrade Shooting Speed", 100),
            ("Upgrade Laser Size", 150),
            ("Health Potion", 50),
        ]
        
        for item, price in items:
            Button(
                self.shop_window,
                text=f"{item} for {price} coins",
                command=lambda i=item, p=price: self.buy_item(i, p),
            ).pack(pady=5)

    def buy_item(self, item, price):
        if item == "Upgrade Shooting Speed" and self.coins >= 100:
            self.coins -= 100
            self.laser_delay *= 0.8
            print(f"You bought a {item} for {price} coins!")
        
        elif item == "Upgrade Laser Size" and self.coins >= 150:
            self.coins -= 150
            self.laser_size += 0.5
            print(f"You bought a {item} for {price} coins!")

        elif item == "Health Potion" and self.coins >= 50:
            self.coins -= 50
            self.player_current_health = self.player_max_health
            print(f"You bought a {item} for {price} coins!")

    def clear_shop_window(self):
        # Check if shop_window is initialized and destroy it
        if self.shop_window:
            self.shop_window.destroy()  # Destroy the whole shop window
            print("Shop window cleared!")
            self.shop_window = None  # Reset the shop window reference to None

    # updates priority queue with all new events for a_ball

    def __predict(self, a_ball):
        if a_ball is None:
            return

        # particle-particle collisions
        for i in range(len(self.ball_list)):
            dt = a_ball.time_to_hit(self.ball_list[i])
            heapq.heappush(self.pq, my_event.Event(self.t + dt, a_ball, self.ball_list[i], None))
        
        # particle-wall collisions
        dtX = a_ball.time_to_hit_vertical_wall()
        dtY = a_ball.time_to_hit_horizontal_wall()
        heapq.heappush(self.pq, my_event.Event(self.t + dtX, a_ball, None, None))
        heapq.heappush(self.pq, my_event.Event(self.t + dtY, None, a_ball, None))

    def handle_level_up(self, level, spawn_info, notes_text):
        """Handles level up logic: spawning balls and updating level."""
        for ball_info in spawn_info:
            self.spawn_ball(**ball_info)
        self.level += 1
        self.update_level()
        self.setup_notes_display(notes_text)
    
    def handle_gameplay(self):
        if self.gamemode == "classic":
            self.handle_normal_gameplay()
        elif self.gamemode == "fast":
            self.handle_fast_gameplay()

    def handle_normal_gameplay(self):
        if self.t > 1000 and self.level == 1:
            spawn_info = [
                {"size": 0.05, "input_speed": 0.5, "color": (255, 0, 0), "amount": 14},
                {"size": 0.03, "input_speed": 1, "color": (0, 0, 139), "amount": 3},
            ]
            self.handle_level_up(1, spawn_info, "Blue balls are fast! Be aware.")
            print("Level 2")
        
        if self.t > 2000 and self.level == 2:
            spawn_info = [
                {"size": 0.03, "input_speed": 1, "color": (0, 0, 139), "amount": 7},
                {"size": 0.06, "input_speed": 0.65, "color": (0, 128, 0), "amount": 1, "reward": "increase_shooting_speed"},
            ]
            self.handle_level_up(2, spawn_info, "Shooting green balls make you shoot faster.")
            print("Level 3")

        if self.t > 3000 and self.level == 3:
            spawn_info = [
                {"size": 0.05, "input_speed": 0.5, "color": (255, 0, 0), "amount": 14},
                {"size": 0.03, "input_speed": 1, "color": (0, 0, 139), "amount": 3},
                {"size": 0.07, "input_speed": 0.5, "color": (0, 0, 0), "amount": 5, "health": 2},
                {"size": 0.06, "input_speed": 0.7, "color": (0, 255, 255), "amount": 1, "reward": "shooting_upgrade"},
            ]
            self.handle_level_up(3, spawn_info, "Try shooting different kinds of ball to get an upgrade. Goodluck have fun!")
            print("Level 3")

        if self.t > 4300 and self.level == 4:
            spawn_info = [
                {"size": 0.05, "input_speed": 0.5, "color": (255, 0, 0), "amount": 14},
                {"size": 0.03, "input_speed": 1, "color": (0, 0, 139), "amount": 3},
                {"size": 0.07, "input_speed": 0.5, "color": (0, 0, 0), "amount": 5, "health": 2},
                {"size": 0.12, "input_speed": 0.35, "color": (128, 0, 128), "amount": 1, "health": 25},
            ]
            self.handle_level_up(4, spawn_info, "")
            print("Level 4")
        
        if self.level > 5:
            a = random.randint(1, 50)
            b = random.randint(1, 50 - a)
            c = random.randint(1, 50 - a - b)
            d = 50 - (a + b + c)
            spawn_info = [
                {"size": 0.05, "input_speed": 0.5, "color": (255, 0, 0), "amount": a},
                {"size": 0.03, "input_speed": 1, "color": (0, 0, 139), "amount": b},
                {"size": 0.07, "input_speed": 0.5, "color": (0, 0, 0), "amount": c, "health": 2},
                {"size": 0.12, "input_speed": 0.35, "color": (128, 0, 128), "amount": d, "health": 25},
            ]
            self.handle_level_up(4, spawn_info, "")           

        if self.score >= 150:
            self.done = True
            self.show_win_message()
            return

        if self.t > 8000:
            self.done = True
            self.show_lose_message()
            return

    def handle_fast_gameplay(self):
        if self.t > 1000 and self.level == 1:
            spawn_info = [
                {"size": 0.05, "input_speed": 0.6, "color": (255, 0, 0), "amount": 10},
                {"size": 0.03, "input_speed": 1.2, "color": (0, 0, 139), "amount": 5},
                {"size": 0.06, "input_speed": 0.65, "color": (0, 128, 0), "amount": 3, "reward": "increase_shooting_speed"},
            ]
            self.handle_level_up(1, spawn_info, "Blue balls are fast! Be aware.")
            print("Level 2")

        if self.t > 2000 and self.level == 2:
            spawn_info = [
                {"size": 0.03, "input_speed": 1.2, "color": (0, 0, 139), "amount": 15},
                {"size": 0.06, "input_speed": 0.65, "color": (0, 128, 0), "amount": 2, "reward": "increase_shooting_speed"},
                {"size": 0.06, "input_speed": 0.7, "color": (0, 255, 255), "amount": 1, "reward": "shooting_upgrade"},
            ]
            self.handle_level_up(2, spawn_info, "Shooting green balls make you shoot faster.")
            print("Level 3")

        if self.t > 3000 and self.level == 3:
            spawn_info = [
                {"size": 0.05, "input_speed": 0.6, "color": (255, 0, 0), "amount": 14},
                {"size": 0.03, "input_speed": 1.2, "color": (0, 0, 139), "amount": 3},
                {"size": 0.07, "input_speed": 0.6, "color": (0, 0, 0), "amount": 5, "health": 3},
                {"size": 0.06, "input_speed": 0.65, "color": (0, 128, 0), "amount": 2, "reward": "increase_shooting_speed"},
            ]
            self.handle_level_up(3, spawn_info, "Try shooting different kinds of ball to get an upgrade. Goodluck have fun!")
            print("Level 3")

        if self.t > 4300 and self.level == 4:
            spawn_info = [
                {"size": 0.05, "input_speed": 0.5, "color": (255, 0, 0), "amount": 15},
                {"size": 0.03, "input_speed": 1.2, "color": (0, 0, 139), "amount": 3},
                {"size": 0.07, "input_speed": 0.5, "color": (0, 0, 0), "amount": 5, "health": 7},
                {"size": 0.12, "input_speed": 0.35, "color": (128, 0, 128), "amount": 1, "health": 25},
            ]
            self.handle_level_up(4, spawn_info, "")
            print("Level 4")

        if self.score >= 120:
            self.done = True
            self.show_win_message()
            return

        if self.t > 7000:
            self.done = True
            self.show_lose_message()
            return

    def __draw_border(self):
        turtle.penup()
        turtle.goto(-self.canvas_width, -self.canvas_height)
        turtle.pensize(10)
        turtle.pendown()
        turtle.color((0, 0, 0))   
        for i in range(2):
            turtle.forward(2*self.canvas_width)
            turtle.left(90)
            turtle.forward(2*self.canvas_height)
            turtle.left(90)

    def __redraw(self):
        """Redraws all game objects."""
        turtle.clear()
        self.my_paddle.clear()
        self.__draw_border()
        self.my_paddle.draw()
        self.update_lasers()  # Update laser positions and handle collisions
        self.draw_lasers()  # Draw lasers
        for i in range(len(self.ball_list)):
            self.ball_list[i].draw()
        turtle.update()
        heapq.heappush(self.pq, my_event.Event(self.t + 1.0 / self.HZ, None, None, None))

    def __paddle_predict(self):
        for i in range(len(self.ball_list)):
            a_ball = self.ball_list[i]
            dtP = a_ball.time_to_hit_paddle(self.my_paddle)
            heapq.heappush(self.pq, my_event.Event(self.t + dtP, a_ball, None, self.my_paddle))

    def run(self):
        turtle.clear()
        # Initialize pq with collision events and redraw event
        for i in range(len(self.ball_list)):
            self.__predict(self.ball_list[i])
        
        heapq.heappush(self.pq, my_event.Event(0, None, None, None))
        lose_radius = 48  # Radius around the center where "You Lose" is triggered

        while True:
            e = heapq.heappop(self.pq)
            if not e.is_valid():
                continue

            ball_a = e.a
            ball_b = e.b
            paddle_a = e.paddle
            self.setup_display()

            if self.level == 1:
                self.setup_notes_display("Don't let the ball hit you. Press LMB to shoot")

            # Handle ball movement and health check
            for i in range(len(self.ball_list) - 1, -1, -1):  # Iterating backwards to avoid index errors when removing balls
                self.ball_list[i].move(e.time - self.t)

                # Check if any ball is within the lose radius around the center
                if abs(self.ball_list[i].x) <= lose_radius and abs(self.ball_list[i].y) <= lose_radius:
                    self.player_current_health -= 1  # Decrease health
                    print(f"Player hit! Health: {self.player_current_health}")  # Debugging statement
                    del self.ball_list[i]

                    if self.player_current_health <= 0:  # Check if health is zero or below
                        self.show_lose_message()  # Display lose message
                        return  # End the game if the player loses

            self.t = e.time

            # Handle collision events
            if ball_a is not None and ball_b is not None and paddle_a is None:
                ball_a.bounce_off(ball_b)
            elif ball_a is not None and ball_b is None and paddle_a is None:
                ball_a.bounce_off_vertical_wall()
            elif ball_a is None and ball_b is not None and paddle_a is None:
                ball_b.bounce_off_horizontal_wall()
            elif ball_a is None and ball_b is None and paddle_a is None:
                self.__redraw()
            elif ball_a is not None and ball_b is None and paddle_a is not None:
                ball_a.bounce_off_paddle()

            # Predict next events (Still Bugged So I commentted it)
            # self.__predict(ball_a)
            # if ball_b is not None:
            #     self.__predict(ball_b)
            self.__paddle_predict()

            # Handle the rest of the gameplay
            self.handle_gameplay()

            # Check if the game is done
            if self.done:
                break

        turtle.done()

    def restart_game(self):
        self.update_score("Local", self.score)
        self.clear_shop_window()
        self.__init__(self.num_balls, self.level)
        self.show_menu()

    def quit_game(self):
        self.update_score("Local", self.score)
        self.clear_shop_window()
        turtle.bye()

    def clear_screen(self):

        self.score_writer.clear()
        self.level_writer.clear()
        self.coin_writer.clear()
        self.health_writer.clear()
        self.my_paddle.my_turtle.clear()
        self.my_paddle.my_turtle.hideturtle()
        self.level_notes.clear()

    def show_lose_message(self):
        
        turtle.clear()
        self.clear_screen()
        turtle.penup()
        turtle.goto(0, 50)
        turtle.color("red")
        turtle.write("GAME OVER", align="center", font=("Arial", 36, "bold"))
        turtle.goto(0, 0)
        turtle.color("black")
        turtle.write(f"Final Score: {self.score}", align="center", font=("Arial", 24, "bold"))
        turtle.goto(0, -50)
        turtle.write("Press 'R' to Restart or 'Q' to Quit", align="center", font=("Arial", 18, "normal"))
        turtle.hideturtle()
        turtle.update()

        self.screen.listen()
        self.screen.onkey(self.restart_game, "r")
        self.screen.onkey(self.quit_game, "q")

    def show_win_message(self):

        turtle.clear()
        self.clear_screen()
        turtle.penup()
        turtle.goto(0, 0)
        turtle.write("Congrats! You Win.", align="center", font=("Arial", 36, "bold"))
        turtle.goto(0, -50)
        turtle.write("Press 'R' to Restart or 'Q' to Quit", align="center", font=("Arial", 18, "normal"))
        turtle.goto(0, -100)
        turtle.write("Munyin Sam 6710545962", align="center", font=("Arial", 12, "bold"))
        turtle.hideturtle()
        turtle.update()
        self.screen.listen()
        self.screen.onkey(self.restart_game, "r")
        self.screen.onkey(self.quit_game, "q")

    def update_score(self, player_name, score):

        file_path = 'game_scores.csv'
        finish_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        row = [player_name, score, finish_time]
        # Open the CSV file in append mode
        with open(file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            # If the file is empty, write the header
            if file.tell() == 0:
                writer.writerow(['Player Name', 'Score', 'Finish Time'])
            # Write the score data
            writer.writerow(row)
        print(f"Score for {player_name} updated: {score}")

# Start the application
num_balls = 10
simulator = BouncingSimulator(num_balls)
simulator.show_menu()
