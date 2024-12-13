class BouncingSimulator:
    def __init__(self, num_balls, level=1):
        self.num_balls = num_balls
        self.ball_list = []
        self.lasers = []
        self.level = level
        self.t = 0.0