import turtle
import random
import heapq
import ball
import my_event
import paddle
import time
import math
from ball import Ball

class BouncingSimulator:
    def __init__(self, num_balls, level=1):
        self.num_balls = num_balls
        self.ball_list = []
        self.lasers = []
        self.t = 0.0
        self.pq = []
        self.HZ = 4
        turtle.speed(0)
        turtle.tracer(0)
        turtle.hideturtle()
        turtle.colormode(255)
        self.canvas_width = 400
        self.canvas_height = 320

        self.laser_delay = 0.4
        self.last_laser_time = 0  # Time when the last laser was fired
        self.laser_size = 1

        self.ball_spawn_interval = 2  # Interval to spawn a ball
        self.last_ball_time = 0  # Time when the last ball was spawned
        print(self.canvas_width, self.canvas_height)

        self.score = 0  # Initial score
        self.score_writer = turtle.Turtle()
        self.level = level
        self.level_writer = turtle.Turtle()
        self.level_notes = turtle.Turtle()

        ball_radius = 0.05 * self.canvas_width
        for i in range(self.num_balls):
            # Randomly choose an edge: 0 = top, 1 = bottom, 2 = left, 3 = right
            edge = random.randint(0, 3)
            if edge == 0:  # Top edge
                x = random.uniform(-self.canvas_width, self.canvas_width)
                y = self.canvas_height
            elif edge == 1:  # Bottom edge
                x = random.uniform(-self.canvas_width, self.canvas_width)
                y = -self.canvas_height
            elif edge == 2:  # Left edge
                x = -self.canvas_width
                y = random.uniform(-self.canvas_height, self.canvas_height)
            else:  # Right edge
                x = self.canvas_width
                y = random.uniform(-self.canvas_height, self.canvas_height)

            # Speed and direction toward the center
            speed = 0.5
            direction = ((-x) ** 2 + (-y) ** 2) ** 0.5
            vx = speed * (-x / direction)
            vy = speed * (-y / direction)

            # Random color for each ball
            ball_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            ball_color = (255, 0, 0)
            self.ball_list.append(ball.Ball(ball_radius, x, y, vx, vy, ball_color, i))

        tom = turtle.Turtle()
        self.my_paddle = paddle.Paddle(50, 50, (37, 150, 190), tom)
        self.my_paddle.set_location([0, 0])

        self.screen = turtle.Screen()
        self.screen.onclick(self.shoot_laser)

    # Tom -----------------

    # Spawn Balls -------------------------------
    
    def spawn_ball(self, size=0.05, input_speed=0.5, color=(255, 0, 0), amount=1, health=1, reward=None):
        ball_radius = size * self.canvas_width  # Ball radius based on size

        # Minimum distance from the center (to avoid spawning in the lose radius)
        min_distance_from_center = 100  # Adjust this value to ensure balls aren't too close to the center
        
        for i in range(amount):
            # Randomly choose an edge: 0 = top, 1 = bottom, 2 = left, 3 = right
            edge = random.randint(0, 3)
            
            if edge == 0:  # Top edge
                x = random.uniform(-self.canvas_width, self.canvas_width)
                y = self.canvas_height
            elif edge == 1:  # Bottom edge
                x = random.uniform(-self.canvas_width, self.canvas_width)
                y = -self.canvas_height
            elif edge == 2:  # Left edge
                x = -self.canvas_width
                y = random.uniform(-self.canvas_height, self.canvas_height)
            else:  # Right edge
                x = self.canvas_width
                y = random.uniform(-self.canvas_height, self.canvas_height)

            # Check if the ball is too close to the center, if so, move it further out
            if abs(x) < min_distance_from_center and abs(y) < min_distance_from_center:
                if edge == 0 or edge == 1:
                    y += min_distance_from_center  # Move ball along the Y-axis
                else:
                    x += min_distance_from_center  # Move ball along the X-axis

            # Calculate speed and direction towards the center of the screen
            direction = math.sqrt(x**2 + y**2)  # Distance from the edge to the center
            vx = input_speed * (-x / direction)  # Horizontal velocity
            vy = input_speed * (-y / direction)  # Vertical velocity

            # Create a new Ball object and add it to the ball list
            new_ball = ball.Ball(ball_radius, x, y, vx, vy, color, len(self.ball_list), health=health, reward=reward)
            self.ball_list.append(new_ball)
            print("Ball appended at position:", x, y)

    # Lasers -------------------------------

    def shoot_laser(self, x, y):
        """Shoots a laser from the paddle's current position towards the mouse."""
        # Calculate the direction of the laser towards the mouse position

        current_time = time.time()  # Get the current time in seconds
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
        
        # Laser speed
        laser_speed = 10
        
        # Velocity of the laser
        vx = dx * laser_speed
        vy = dy * laser_speed
        
        # Create the laser object
        laser = {
            "x": paddle_x,
            "y": paddle_y + self.my_paddle.height // 2,
            "vx": vx,
            "vy": vy,
            "width": 5*self.laser_size,
            "height": 5*self.laser_size
        }
        
        self.lasers.append(laser)
        self.last_laser_time = current_time

    def update_lasers(self):
        """Moves lasers and checks for collisions with balls."""
        for laser in self.lasers[:]:
            laser["x"] += laser["vx"]
            laser["y"] += laser["vy"]

            # Check if laser goes off-screen
            if laser["y"] > self.canvas_height or laser["x"] < -self.canvas_width or laser["x"] > self.canvas_width:
                self.lasers.remove(laser)
                continue

            # Check for collisions with balls
            for ball_obj in self.ball_list[:]:
                if (abs(laser["x"] - ball_obj.x) < ball_obj.radius + laser["width"] / 2 and
                        abs(laser["y"] - ball_obj.y) < ball_obj.radius + laser["height"] / 2):
                    if ball_obj.health == 1:
                        self.ball_list.remove(ball_obj)
                        self.lasers.remove(laser)
                        # Increment the score
                        self.increase_score(points=ball_obj.default_health)
                        if ball_obj.reward == "increase_shooting_speed":
                            print("Shooting Speed Increased.")
                            self.laser_delay -= 1
                        if ball_obj.reward == "shooting_upgrade":
                            print("Increase Shooting Size.")
                            self.laser_size += 1
                    else:
                        ball_obj.health -= 1
                        self.lasers.remove(laser)
                    break

    def draw_lasers(self):
        for laser in self.lasers:
            turtle.penup()
            turtle.goto(laser["x"] - laser["width"] / 2, laser["y"] - laser["height"] / 2)
            turtle.pendown()
            turtle.color("blue")
            turtle.begin_fill()
            for _ in range(2):
                turtle.forward(laser["width"])
                turtle.left(90)
                turtle.forward(laser["height"])
                turtle.left(90)
            turtle.end_fill()

    # Updates

    # Menu

    def show_menu(self):
        # Draw the menu screen
        turtle.clear()
        turtle.penup()
        turtle.goto(0, 50)
        turtle.color("black")
        turtle.write("Tower Defence Demo", align="center", font=("Arial", 24, "bold"))
        turtle.goto(0, -50)
        turtle.write("Press 'P' to Play", align="center", font=("Arial", 18, "normal"))
        turtle.goto(0, -100)
        turtle.write("Munyin Sam 6710545962", align="center", font=("Arial", 12, "bold"))
        turtle.hideturtle()
        turtle.update()

        # Wait for the user to press the play button
        self.screen.listen()
        self.screen.onkey(self.run, "p")
        self.screen.mainloop()

    def setup_score_display(self):
        self.score_writer.hideturtle()
        self.score_writer.penup()
        self.score_writer.goto(-360, 270)
        self.update_score_display()

    def update_score_display(self):
        self.score_writer.clear() 
        self.score_writer.write(f"Score: {self.score}", align="left", font=("Arial", 16, "bold"))

    def increase_score(self, points=1):
        self.score += points
        self.update_score_display()

    def setup_level_display(self):
        self.level_writer.hideturtle()
        self.level_writer.penup()
        self.level_writer.goto(280, 270)
        self.update_level_display()

    def update_level_display(self):
        self.level_writer.clear() 
        self.level_writer.write(f"Level: {self.level}", align="left", font=("Arial", 16, "bold"))

    def update_level(self):
        self.update_score_display()

    def setup_notes_display(self, tips):
        self.level_notes.hideturtle()
        self.level_notes.penup()
        self.level_notes.goto(0, -300)
        self.level_notes.clear()
        self.level_notes.write(f"Tip: {tips}", align="center", font=("Arial", 12, "bold"))
    
    def clear_notes(self):
        self.level_notes.clear()

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

    # move handlers
    def move_left(self):
        if (self.my_paddle.location[0] - self.my_paddle.width/2 - 40) >= -self.canvas_width:
            self.my_paddle.set_location([self.my_paddle.location[0] - 40, self.my_paddle.location[1]])

    def move_right(self):
        if (self.my_paddle.location[0] + self.my_paddle.width/2 + 40) <= self.canvas_width:
            self.my_paddle.set_location([self.my_paddle.location[0] + 40, self.my_paddle.location[1]])

    def move_down(self):
        if (self.my_paddle.location[1] - self.my_paddle.height/2 - 40) >= -self.canvas_height:
            self.my_paddle.set_location([self.my_paddle.location[0], self.my_paddle.location[1] - 40])

    def move_up(self):
        if (self.my_paddle.location[1] + self.my_paddle.height/2 + 40) <= self.canvas_height:
            self.my_paddle.set_location([self.my_paddle.location[0], self.my_paddle.location[1] + 40])

    def run(self):
        turtle.clear()
        # Initialize pq with collision events and redraw event
        for i in range(len(self.ball_list)):
            self.__predict(self.ball_list[i])
        heapq.heappush(self.pq, my_event.Event(0, None, None, None))

        self.screen.listen()
        # self.screen.onkey(self.move_left, "Left")
        # self.screen.onkey(self.move_right, "Right")
        # self.screen.onkey(self.move_up, "Up")
        # self.screen.onkey(self.move_down, "Down")

        lose_radius = 48  # Radius around the center where "You Lose" is triggered

        while True:
            e = heapq.heappop(self.pq)
            if not e.is_valid():
                continue

            ball_a = e.a
            ball_b = e.b
            paddle_a = e.paddle
            self.setup_score_display()
            self.setup_level_display()
            if self.level == 1:
                self.setup_notes_display("Don't let the ball hit you. Press LMB to shoot")

            for i in range(len(self.ball_list)):
                self.ball_list[i].move(e.time - self.t)

                # Check if any ball is within the lose radius around the center
                if abs(self.ball_list[i].x) <= lose_radius and abs(self.ball_list[i].y) <= lose_radius:
                    self.show_lose_message()
                    return  # End the game

            self.t = e.time

            if (ball_a is not None) and (ball_b is not None) and (paddle_a is None):
                ball_a.bounce_off(ball_b)
            elif (ball_a is not None) and (ball_b is None) and (paddle_a is None):
                ball_a.bounce_off_vertical_wall()
            elif (ball_a is None) and (ball_b is not None) and (paddle_a is None):
                ball_b.bounce_off_horizontal_wall()
            elif (ball_a is None) and (ball_b is None) and (paddle_a is None):
                self.__redraw()
            elif (ball_a is not None) and (ball_b is None) and (paddle_a is not None):
                ball_a.bounce_off_paddle()

            # Bugged

            # self.__predict(ball_a)
            # self.__predict(ball_b)
            # self.__paddle_predict()

            if self.t > 1000 and self.level == 1:

                self.spawn_ball(size=0.05, input_speed=0.5, color=(255, 0, 0), amount=10)
                self.spawn_ball(size=0.03, input_speed=1, color=(0, 0, 139), amount=3)
                self.level+=1
                self.update_level()
                self.setup_notes_display("Blue balls are fast! Be aware.")
                print("Level 2")
                

            if self.t > 2000 and self.level == 2:
                self.spawn_ball(size=0.03, input_speed=1, color=(0, 0, 139), amount=8)
                self.spawn_ball(size=0.06, input_speed=0.65, color=(0, 128, 0), amount=1, reward="increase_shooting_speed")
                self.level+=1
                self.update_level()
                self.setup_notes_display("Shooting green balls make you shoot faster.")
                print("Level 3")

            if self.t > 3000 and self.level == 3:

                self.spawn_ball(size=0.05, input_speed=0.5, color=(255, 0, 0), amount=10)
                self.spawn_ball(size=0.03, input_speed=1, color=(0, 0, 139), amount=3)
                self.spawn_ball(size=0.07, input_speed=0.5, color=(0, 0, 0), amount=5, health=2)
                self.spawn_ball(size=0.06, input_speed=0.7, color=(0, 255, 255), amount=1, reward="shooting_upgrade")
                self.setup_notes_display("Try shooting different kinds of ball to get an upgrade. Goodluck have fun!")
                self.level+=1
                print("Level 3")

            if self.t > 4300 and self.level == 4:

                self.spawn_ball(size=0.05, input_speed=0.5, color=(255, 0, 0), amount=10)
                self.spawn_ball(size=0.03, input_speed=1, color=(0, 0, 139), amount=3)
                self.spawn_ball(size=0.07, input_speed=0.5, color=(0, 0, 0), amount=5, health=2)
                self.spawn_ball(size=0.12, input_speed=0.35, color=(128, 0, 128), amount=1, health=21)
                self.level+=1
                self.update_level()
                self.clear_notes()
                print("Level 4")
            
            if self.score == 100:
                self.show_win_message()

        turtle.done()

    def show_lose_message(self):
        turtle.clear()
        self.my_paddle.my_turtle.clear()
        self.my_paddle.my_turtle.hideturtle()
        turtle.penup()
        turtle.hideturtle()
        self.screen.bgcolor("white")
        turtle.color("red")
        turtle.goto(0, 0)
        turtle.write("You Lose!", align="center", font=("Arial", 36, "bold"))
        turtle.update()
        time.sleep(1) 
        turtle.bye()

    def show_win_message(self):
        turtle.clear()
        self.my_paddle.my_turtle.clear()
        self.my_paddle.my_turtle.hideturtle()
        turtle.penup()
        turtle.hideturtle()
        self.screen.bgcolor("white")
        turtle.goto(0, 0)
        turtle.write("Congrats! You Win.", align="center", font=("Arial", 36, "bold"))
        turtle.goto(0, -50)
        turtle.write("Munyin Sam 6710545962", align="center", font=("Arial", 12, "bold"))
        turtle.update()
        time.sleep(7)  
        turtle.bye()

# Start the application
num_balls = 10
simulator = BouncingSimulator(num_balls)
simulator.show_menu()
