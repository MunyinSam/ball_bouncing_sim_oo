import ball
import my_event
import turtle
import random
import heapq
import paddle
import time

class BouncingSimulator:
    def __init__(self, num_balls):
        self.num_balls = num_balls
        self.ball_list = []
        self.t = 0.0
        self.pq = []
        self.HZ = 4
        turtle.speed(0)
        turtle.tracer(0)
        turtle.hideturtle()
        turtle.colormode(255)
        self.canvas_width = turtle.screensize()[0] # 400
        self.canvas_height = turtle.screensize()[1] # 300
        print(self.canvas_width, self.canvas_height)

        # Balls Size
        ball_radius = 0.05 * self.canvas_width

        # Balls Spawning Mechanics
        for i in range(self.num_balls):
            # Randomly choose one of the four edges (top, bottom, left, right)
            edge = random.choice(['top', 'bottom', 'left', 'right'])
            
            # Random position and velocity
            if edge == 'top':  # Spawn on the top edge
                x = random.uniform(-self.canvas_width, self.canvas_width)
                y = self.canvas_height  # Y position at the top of the screen
            elif edge == 'bottom':  # Spawn on the bottom edge
                x = random.uniform(-self.canvas_width, self.canvas_width)
                y = -self.canvas_height  # Y position at the bottom of the screen
            elif edge == 'left':  # Spawn on the left edge
                x = -self.canvas_width  # X position at the left of the screen
                y = random.uniform(-self.canvas_height, self.canvas_height)
            elif edge == 'right':  # Spawn on the right edge
                x = self.canvas_width  # X position at the right of the screen
                y = random.uniform(-self.canvas_height, self.canvas_height)
            
            # Random velocity in both directions
            vx = 5 * random.uniform(-1.0, 1.0)
            vy = 5 * random.uniform(-1.0, 1.0)
            
            # Random color
            ball_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            ball_color = (255, 0, 0)
            
            # Create the ball and append it to the list
            self.ball_list.append(ball.Ball(ball_radius, x, y, vx, vy, ball_color, i))

        
        tom = turtle.Turtle()
        # Width , Height , Color, Turtle
        self.my_paddle = paddle.Paddle(50, 50, (0, 0, 0), tom)
        self.my_paddle.set_location([0, 0])

        # Initialize Tom's life and create a text object to display the life
        self.tom_life = 3
        self.life_display = turtle.Turtle()
        self.life_display.hideturtle()
        self.life_display.penup()
        self.life_display.goto(0, self.canvas_height - 20)
        self.life_display.write(f"Life: {self.tom_life}", align="center", font=("Arial", 16, "normal"))


        self.screen = turtle.Screen()

    # updates priority queue with all new events for a_ball
    def __predict(self, a_ball):
        if a_ball is None:
            return

        # particle-particle collisions (2 Balls)
        for i in range(len(self.ball_list)):
            # Time to Hit
            dt = a_ball.time_to_hit(self.ball_list[i])
            # insert this event into pq
            heapq.heappush(self.pq, my_event.Event(self.t + dt, a_ball, self.ball_list[i], None))
        
        # particle-wall collisions (Walls)
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
        turtle.clear()
        self.my_paddle.clear()
        self.__draw_border()
        self.my_paddle.draw()
        for i in range(len(self.ball_list)):
            self.ball_list[i].draw()
        turtle.update()
        heapq.heappush(self.pq, my_event.Event(self.t + 1.0/self.HZ, None, None, None))

    def __paddle_predict(self):
        for i in range(len(self.ball_list)):
            a_ball = self.ball_list[i]
            dtP = a_ball.time_to_hit_paddle(self.my_paddle)
            heapq.heappush(self.pq, my_event.Event(self.t + dtP, a_ball, None, self.my_paddle))

    # move_left and move_right handlers update paddle positions
    def move_left(self):
        if (self.my_paddle.location[0] - self.my_paddle.width/2 - 40) >= -self.canvas_width:
            self.my_paddle.set_location([self.my_paddle.location[0] - 40, self.my_paddle.location[1]])

    # move_left and move_right handlers update paddle positions
    def move_right(self):
        if (self.my_paddle.location[0] + self.my_paddle.width/2 + 40) <= self.canvas_width:
            self.my_paddle.set_location([self.my_paddle.location[0] + 40, self.my_paddle.location[1]])

    # move_up handler updates paddle position upwards
    def move_down(self):
        if (self.my_paddle.location[1] - self.my_paddle.height/2 - 40) >= -self.canvas_height:
            self.my_paddle.set_location([self.my_paddle.location[0], self.my_paddle.location[1] - 40])

    # move_down handler updates paddle position downwards
    def move_up(self):
        if (self.my_paddle.location[1] + self.my_paddle.height/2 + 40) <= self.canvas_height:
            self.my_paddle.set_location([self.my_paddle.location[0], self.my_paddle.location[1] + 40])
 
    def flash_red(self):
        """Flashes Tom red to indicate damage."""
        self.my_paddle.color = (255, 0, 0)  # Change color to red
        self.my_paddle.draw()
        turtle.update()
        time.sleep(0.1)  # Flash for a short moment
        self.my_paddle.color = (0, 0, 0)  # Change color back to black
        self.my_paddle.draw()
        turtle.update()

    def reduce_life(self):
        """Reduces Tom's life and updates the display."""
        self.tom_life -= 1
        self.life_display.clear()
        self.life_display.write(f"Life: {self.tom_life}", align="center", font=("Arial", 16, "normal"))

    def run(self):
        # initialize pq with collision events and redraw event
        for i in range(len(self.ball_list)):
            self.__predict(self.ball_list[i])
        heapq.heappush(self.pq, my_event.Event(0, None, None, None))

        # listen to keyboard events and activate move_left and move_right handlers accordingly
        self.screen.listen()
        self.screen.onkey(self.move_left, "Left")
        self.screen.onkey(self.move_right, "Right")
        self.screen.onkey(self.move_up, "Up")
        self.screen.onkey(self.move_down, "Down")

        while (True):
            e = heapq.heappop(self.pq)
            if not e.is_valid():
                continue

            ball_a = e.a
            ball_b = e.b
            paddle_a = e.paddle

            # update positions, and then simulation clock
            for i in range(len(self.ball_list)):
                self.ball_list[i].move(e.time - self.t)
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

            self.__predict(ball_a)
            self.__predict(ball_b)

            if self.tom_life == 0:
                print("Tom has lost all lives! Game Over.")
                break

            # regularly update the prediction for the paddle as its position may always be changing due to keyboard events
            self.__paddle_predict()


        # hold the window; close it by clicking the window close 'x' mark
        turtle.done()

# num_balls = int(input("Number of balls to simulate: "))
num_balls = 10
my_simulator = BouncingSimulator(num_balls)
my_simulator.run()


