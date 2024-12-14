class Paddle:
    def __init__(self, width, height, color, my_turtle):
        self.width = width * 0.8
        self.height = height * 0.8
        self.location = [0, 0]
        self.color = color
        self.my_turtle = my_turtle
        self.my_turtle.penup()
        self.my_turtle.setheading(0)
        self.my_turtle.hideturtle()

    def set_location(self, location):
        self.location = location
        # Move turtle to the center of the paddle (offset by half the height and width)
        self.my_turtle.goto(self.location[0] - self.width / 2, self.location[1] - self.height / 2)

    def draw(self):
        self.my_turtle.color(self.color)
        self.my_turtle.pensize(5)
        self.my_turtle.pencolor("black")
        self.my_turtle.setheading(0)  # Make sure

        # hexagon
        self.my_turtle.pendown()
        self.my_turtle.begin_fill()

        # Draw the hexagon (6 sides)
        for _ in range(6):
            self.my_turtle.forward(self.width)  # Length of each side
            self.my_turtle.left(60)

        self.my_turtle.end_fill()
        self.my_turtle.penup()

    def clear(self):
        self.my_turtle.clear()

    def __str__(self):
        return "paddle"
