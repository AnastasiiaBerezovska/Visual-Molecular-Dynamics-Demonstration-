from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.properties import NumericProperty, ListProperty
from kivy.vector import Vector
from kivy.graphics import Color, Ellipse, Rectangle
from random import uniform, randint
from math import sqrt


class Ball(Widget):
    vx = NumericProperty(0)
    vy = NumericProperty(0)
    color_slow = [5, 0, 102, 255]
    color_fast = [255, 81, 220, 255]
    color = ListProperty([x / 255 for x in color_fast])  # Initial color is red (RGBA)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (50, 50)  # Define the size of the ball
        with self.canvas:
            self.color_instruction = Color(*self.color)  # Set initial color (red)
            self.ball_shape = Ellipse(pos=self.pos, size=self.size)  # Set initial position and size

    def move(self):
        # Update the ball's position
        self.pos = Vector(self.vx, self.vy) + self.pos
        self.ball_shape.pos = self.pos  # Update the ball's position in the canvas

    def bounce_off_walls(self, width, height):
        if (self.x <= 0 and self.vx < 0) or (self.right >= width and self.vx > 0):
            self.vx = -self.vx
        if (self.y <= 0 and self.vy < 0) or (self.top >= height and self.vy > 0):
            self.vy = -self.vy

    def collide_widget(self, other):
        distance = Vector(self.center).distance(other.center)
        return distance <= (self.width / 2 + other.width / 2)

    def resolve_collision(self, other):
        v1 = Vector(self.vx, self.vy)
        v2 = Vector(other.vx, other.vy)

        p1 = Vector(self.center)
        p2 = Vector(other.center)

        m1 = self.width / 2
        m2 = other.width / 2

        normal = (p1 - p2).normalize()
        tangent = Vector(-normal[1], normal[0])

        v1n = normal.dot(v1)
        v1t = tangent.dot(v1)

        v2n = normal.dot(v2)
        v2t = tangent.dot(v2)

        v1n_new = (v1n * (m1 - m2) + 2 * m2 * v2n) / (m1 + m2)
        v2n_new = (v2n * (m2 - m1) + 2 * m1 * v1n) / (m1 + m2)

        v1t_new = v1t
        v2t_new = v2t

        v1n_new_vec = v1n_new * normal
        v1t_new_vec = v1t_new * tangent

        v2n_new_vec = v2n_new * normal
        v2t_new_vec = v2t_new * tangent

        self.vx, self.vy = v1n_new_vec + v1t_new_vec
        other.vx, other.vy = v2n_new_vec + v2t_new_vec

    def update_color_based_on_speed(self):
        speed = sqrt(self.vx ** 2 + self.vy ** 2)  # Calculate the speed
        t = min(speed, 8) / 8  # t is between 0 and 1 based on the speed
                
        self.color_instruction.rgb = [(self.color_slow[0] + (self.color_fast[0] - self.color_slow[0]) * t) / 255, 
                                      (self.color_slow[1] + (self.color_fast[1] - self.color_slow[1]) * t) / 255, 
                                      (self.color_slow[2] + (self.color_fast[2] - self.color_slow[2]) * t) / 255]  # Lerp between red and green


class GameScreen(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.balls = []
        Clock.schedule_interval(self.update, 1 / 60.0)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.spawn_ball_at_touch(touch)

    def spawn_ball_at_touch(self, touch):
        ball = Ball()  # Ball size is now set in the constructor
        ball.center = touch.pos

        # Generate random velocity with fixed magnitude 1
        a = uniform(-5, 5)
        b = sqrt(25 - a ** 2) * (2 * randint(0, 1) - 1)
        ball.vx = a
        ball.vy = b
        
        ball.update_color_based_on_speed() # Ensure the color is updated based on initial speed
        self.add_widget(ball)
        self.balls.append(ball)

    def update(self, dt):
        for ball in self.balls:
            ball.move()
            ball.bounce_off_walls(self.width, self.height)
            # ball.update_color_based_on_speed()  # Update the ball's color based on speed

        for i, ball1 in enumerate(self.balls):
            for ball2 in self.balls[i + 1:]:
                if ball1.collide_widget(ball2):
                    ball1.resolve_collision(ball2)
                    ball1.update_color_based_on_speed()
                    ball2.update_color_based_on_speed()

class GameLayout(Widget):
    def __init__(self, **kwargs):
        super(GameLayout, self).__init__(**kwargs)
        with self.canvas.before:
            # Set background color of the game area (black)
            self.bg_color = Color(0, 0, 0, 1)  # Black color
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class MyApp(App):
    def build(self):
        # Root layout for the entire screen
        root = FloatLayout()

        # Add a grey background to cover the entire UI
        with root.canvas.before:
            self.bg_color = Color(0.2, 0.2, 0.2, 1)  # Dark grey background
            self.ui_rect = Rectangle(pos=root.pos, size=root.size)

        # Bind the position and size of the grey background to the root layout
        root.bind(pos=self.update_ui_background, size=self.update_ui_background)

        # Create the game area (black), manually controlled size and position
        game_area = GameLayout(size_hint=(0.8, 0.6), pos_hint={'center_x': 0.5, 'center_y': 0.6})

        # Add the game area to the root layout
        root.add_widget(game_area)

        # Create a button below the game area for testing positioning
        button = Button(text='Clear', size_hint=(0.15, 0.1), pos_hint={'center_x': 0.5, 'center_y': 0.2})
        root.add_widget(button)

        # Dynamically update the size and position of the game area when the root size changes
        root.bind(size=lambda *_: game_area.update_rect())

        return root

    def update_ui_background(self, instance, *args):
        """ Update the grey background dynamically when the window size changes """
        instance.canvas.before.clear()
        with instance.canvas.before:
            self.bg_color = Color(0.2, 0.2, 0.2, 1)  # Grey background for the entire screen
            self.ui_rect = Rectangle(pos=instance.pos, size=instance.size)

        # Force canvas update
        instance.canvas.ask_update()

if __name__ == "__main__":
    MyApp().run()