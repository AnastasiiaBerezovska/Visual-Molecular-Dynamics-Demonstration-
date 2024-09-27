from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.slider import Slider
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.properties import NumericProperty, ListProperty
from kivy.vector import Vector
from kivy.graphics import Color, Ellipse, Rectangle
from random import uniform, randint
import math


class Ball(Widget):
    vx = NumericProperty(0)
    vy = NumericProperty(0)
    gravity = NumericProperty(0)  # Gravity value affecting the ball
    color_slow = [5, 0, 102, 255]
    color_fast = [255, 81, 220, 255]
    color = ListProperty([x / 255 for x in color_fast])  # Initial color is red (RGBA)

    def __init__(self, **kwargs):
        self.center = kwargs.pop("ball_center")
        self.radius = kwargs.pop("ball_radius")
        super().__init__(**kwargs)
        self.size = (self.radius * 2, self.radius * 2)  # Define the size of the ball
        with self.canvas:
            self.color_instruction = Color(*self.color)  # Set initial color
            self.ball_shape = Ellipse(pos=self.pos, size=self.size)  # Set initial position and size

    def move(self):
        # Apply gravity to the vertical velocity
        self.vy -= self.gravity

        # Update the ball's position based on velocity
        self.pos = Vector(self.vx, self.vy) + self.pos
        self.ball_shape.pos = self.pos  # Update the ball's position in the canvas

    def bounce_off_walls(self):
        # Bounce off the walls of the layout, accounting for the ball's size
        if self.x <= self.parentpos[0] or self.right >= self.parentpos[0] + self.parentsize[0]:
            self.vx = -self.vx
        if self.y <= self.parentpos[1] or self.top >= self.parentpos[1] + self.parentsize[1]:
            self.vy = -self.vy
        self.keep_within_bounds()

    def rescale_position(self, new_pos, new_size):
        """
        Proportionally rescale the ball's position according to the new layout dimensions.
        """
        # Calculate the proportional change in size
        proportion_x = (self.pos[0] - self.parentpos[0]) / self.parentsize[0]
        proportion_y = (self.pos[1] - self.parentpos[1]) / self.parentsize[1]
        # print(f"Previous size: {self.parentpos}, New size: {new_size}")

        # Adjust the position of the ball relative to the new layout size
        self.pos = (new_size[0] * proportion_x + new_pos[0], new_size[1] * proportion_y + new_pos[1])
        self.vx *= (new_size[0] / self.parentsize[0])
        self.vy *= (new_size[1] / self.parentsize[1])
        
        # Update the ball's position on the canvas
        self.ball_shape.pos = self.pos
        
        self.parentpos = new_pos
        self.parentsize = new_size
        self.keep_within_bounds()

    def keep_within_bounds(self):
        """
        Ensure the ball stays within the bounds of the layout after a resize.
        Adjust the position if it's out of bounds.
        """
        # Clamp the x position
        if self.x < self.parentpos[0]:
            self.x = self.parentpos[0]
        if self.right > self.parentpos[0] + self.parentsize[0]:
            self.right = self.parentpos[0] + self.parentsize[0]

        # Clamp the y position
        if self.y < self.parentpos[1]:
            self.y = self.parentpos[1]
        if self.top > self.parentpos[1] + self.parentsize[1]:
            self.top = self.parentpos[1] + self.parentsize[1]

        # Update the shape's position
        self.ball_shape.pos = self.pos

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
        speed = math.sqrt(self.vx ** 2 + self.vy ** 2)  # Calculate the speed
        t = min(speed, 8) / 8  # t is between 0 and 1 based on the speed

        self.color_instruction.rgb = [(self.color_slow[0] + (self.color_fast[0] - self.color_slow[0]) * t) / 255,
                                      (self.color_slow[1] + (self.color_fast[1] - self.color_slow[1]) * t) / 255,
                                      (self.color_slow[2] + (self.color_fast[2] - self.color_slow[2]) * t) / 255]


class GameLayout(Widget):
    def __init__(self, **kwargs):
        super(GameLayout, self).__init__(**kwargs)
        with self.canvas.before:
            Color(0, 0, 0, 1)  # Set background color of the game area (black)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

        self.balls = []
        self.ball_radius = 25  # Radius of the ball, assuming size is 50x50
        self.old_pos = self.pos[:]
        self.old_size = self.size[:]
        self.pos_in_between = self.pos[:]
        self.size_in_between = self.size[:]
        self.gravity = 0  # Initialize gravity
        Clock.schedule_interval(self.update, 1 / 60.0)  # Update 60 times per second

    def update_rect(self, instance, value):
        # Store the current position and size before updating
        self.old_pos = self.pos_in_between[:]
        self.old_size = self.size_in_between[:]

        # Print current and new sizes and positions
        # print(f"Previous pos: {self.old_pos}, Previous size: {self.old_size}")
        # print(f"New pos: {self.pos}, New size: {self.size}")
        # print(f"Updating because of: {instance} with value: {value}")

        # Store old size and position for future reference
        self.pos_in_between = self.pos[:]
        self.size_in_between = self.size[:]

        # Update the rectangle position and size
        self.rect.pos = self.pos
        self.rect.size = self.size

        # Call the resize logic
        self.on_resize()

    def on_touch_down(self, touch):
        if self.is_safe_touch(touch):
            self.spawn_ball_at_touch(touch)

    def is_safe_touch(self, touch):
        """
        Check if the touch is within safe bounds to prevent the ball from extending past the edges.
        """
        safe_margin_x = self.ball_radius
        safe_margin_y = self.ball_radius

        return (
            self.pos[0] + safe_margin_x <= touch.x <= self.right - safe_margin_x and
            self.pos[1] + safe_margin_y <= touch.y <= self.top - safe_margin_y
        )

    def spawn_ball_at_touch(self, touch):
        ball = Ball(ball_center = touch.pos, ball_radius = self.ball_radius)

        # Generate random velocity with fixed magnitude
        angle = uniform(-math.pi, math.pi)
        a = 5 * math.cos(angle)
        b = 5 * math.sin(angle)
        ball.vx = a
        ball.vy = b

        ball.parentpos = self.pos[:]
        ball.parentsize = self.size[:]
        ball.gravity = self.gravity  # Apply the current gravity setting to the ball

        ball.update_color_based_on_speed()  # Ensure the color is updated based on initial speed
        self.add_widget(ball)
        self.balls.append(ball)

    def update(self, dt):
        # Update ball positions and handle collisions with walls and other balls
        for ball in self.balls:
            ball.move()
            ball.bounce_off_walls()

        for i, ball1 in enumerate(self.balls):
            for ball2 in self.balls[i + 1:]:
                if ball1.collide_widget(ball2):
                    ball1.resolve_collision(ball2)
                    ball1.update_color_based_on_speed()
                    ball2.update_color_based_on_speed()

    def on_resize(self):
        # When the game layout is resized, rescale balls' positions
        for ball in self.balls:
            ball.rescale_position(self.pos[:], self.size[:])

    def set_gravity(self, value):
        """Update gravity for all balls based on slider value."""
        self.gravity = value
        for ball in self.balls:
            ball.gravity = self.gravity


class MyApp(App):
    def build(self):
        # Root layout for the entire screen
        root = FloatLayout()

        # Add a grey background to cover the entire UI
        with root.canvas.before:
            Color(0.2, 0.2, 0.2, 1)  # Dark grey background
            self.ui_rect = Rectangle(pos=root.pos, size=root.size)

        # Bind the position and size of the grey background to the root layout
        root.bind(pos=self.update_ui_background, size=self.update_ui_background)

        # Create the game area (black), manually controlled size and position
        game_area = GameLayout(size_hint=(0.8, 0.6), pos_hint={'center_x': 0.5, 'center_y': 0.6})

        # Add the game area to the root layout
        root.add_widget(game_area)

        # Create a UI panel with a slider for gravity
        ui_panel = BoxLayout(orientation='vertical', size_hint=(0.8, 0.2), pos_hint={'center_x': 0.5, 'y': 0})
        root.add_widget(ui_panel)

        gravity_label = Label(text="Gravity", size_hint=(None, None), height=30)
        gravity_slider = Slider(min=0, max=10, value=0, step=0.01, size_hint=(1, None), height=50)
        gravity_slider.bind(value=lambda instance, value: game_area.set_gravity(value))

        ui_panel.add_widget(gravity_label)
        ui_panel.add_widget(gravity_slider)

        button = Button(text='Clear', size_hint=(0.15, 0.1), pos_hint={'center_x': 0.5, 'center_y': 0.2})
        button.bind(on_press=lambda x: (game_area.clear_widgets(), game_area.balls.clear()))
        root.add_widget(button)

        return root

    def update_ui_background(self, instance, *args):
        """ Update the grey background dynamically when the window size changes """
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(0.2, 0.2, 0.2, 1)  # Grey background for the entire screen
            self.ui_rect = Rectangle(pos=instance.pos, size=instance.size)
        
        # Force canvas update
        instance.canvas.ask_update()


if __name__ == "__main__":
    MyApp().run()
