from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.slider import Slider
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.switch import Switch
from kivy.clock import Clock
from kivy.properties import NumericProperty, ListProperty, BooleanProperty
from kivy.vector import Vector
from kivy.graphics import Color, Ellipse, Rectangle, Line
from random import uniform, randint
import math

class Ball(Widget):
    vx = NumericProperty(0)
    vy = NumericProperty(0)
    # gravity = NumericProperty(0)  # Gravity value affecting the ball
    color_slow = [5, 0, 102, 255]
    color_fast = [255, 81, 220, 255]
    color = ListProperty([x / 255 for x in color_fast])  # Initial color is red (RGBA)
    cap = 8

    def __init__(self, **kwargs):
        self.center = kwargs.pop("ball_center")
        self.radius = kwargs.pop("ball_radius")
        super().__init__(**kwargs)
        self.size = (self.radius * 2, self.radius * 2)  # Define the size of the ball
        with self.canvas:
            self.color_instruction = Color(*self.color)  # Set initial color
            self.ball_shape = Ellipse(pos=self.pos, size=self.size)  # Set initial position and size
            self.arrow_color = Color(0, 0, 1, 1)  # Blue for initial arrow color
            self.arrow_line = Line(points=[], width=4)  # Arrow to represent force
            self.total_force = Vector(0, 0)
            
    def fix_speed(self):
        
        speed = ((self.vx ** 2) + (self.vy ** 2)) ** 0.5
        if speed > self.cap:
            self.vx *= self.cap / speed
            self.vy *= self.cap / speed

    def move(self):
        # Apply gravity to the vertical velocity
        # self.calculate_forces()
        # self.vy -= self.gravity
        self.vx += self.total_force[0]
        self.vy += self.total_force[1]
        self.fix_speed()
        self.update_color_based_on_speed()
        # print(self.vx, self.vy)
        # Update the ball's position based on velocity
        self.pos = Vector(self.vx, self.vy) + self.pos
        self.ball_shape.pos = self.pos  # Update the ball's position in the canvas
        self.update_force_arrow()

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
        self.fix_speed()
        self.update_color_based_on_speed()
        
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
        """
        Check if the ball collides with another widget (another ball).
        """
        distance = Vector(self.center).distance(other.center)
        return distance <= (self.width / 2 + other.width / 2)

    def resolve_collision(self, other):
        """
        Resolve a collision between two balls using basic 2D collision mechanics.
        """
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
        self.fix_speed()
        other.fix_speed()

    def update_color_based_on_speed(self):
        """
        Update the ball's color based on its speed, interpolating between slow and fast colors.
        """
        speed = math.sqrt(self.vx ** 2 + self.vy ** 2)  # Calculate the speed
        # print(speed)
        t = min(speed, 8) / 8  # t is between 0 and 1 based on the speed
        self.color_instruction.rgb = [(self.color_slow[0] + (self.color_fast[0] - self.color_slow[0]) * t) / 255,
                                      (self.color_slow[1] + (self.color_fast[1] - self.color_slow[1]) * t) / 255,
                                      (self.color_slow[2] + (self.color_fast[2] - self.color_slow[2]) * t) / 255]
        
    def lennard_jones_force(self, other, epsilon, sigma, scale):
        """
        Calculate the Lennard-Jones force between this ball and another ball.
        :param other: The other ball object.
        :param epsilon: Depth of the potential well.
        :param sigma: Distance at which the potential is zero.
        :return: A Vector representing the force applied on this ball due to the other ball.
        """
        r = (Vector(self.center).distance(other.center)) / scale # Calculate distance between two balls
        # print(r)
        if r == 0:
            return Vector(0, 0)  # Avoid division by zero if the balls are at the same position

        # Lennard-Jones force formula
        force_magnitude = 24 * epsilon * ((2 * (sigma / r) ** 12) - ((sigma / r) ** 6)) / r ** 2
        force_magnitude = max(-1, (min(1, force_magnitude)))
        force_direction = (Vector(self.center) - Vector(other.center)).normalize()  # Direction of the force
        return force_direction * force_magnitude

    def reset_total_force(self):
        self.total_force = Vector(0, 0)

    def add_force(self, force_to_add):
        self.total_force += force_to_add

    def update_force_arrow(self):
        """
        Update the arrow direction, length, and color based on the total force.
        :param total_force: The total Lennard-Jones force applied to this ball.
        """
        # Calculate the arrow's end position based on the force magnitude and direction
        arrow_length = 30  # Limit arrow length to 300
        arrow_endpoint = Vector(self.center) + self.total_force.normalize() * arrow_length
        # print("HELLO", arrow_length)
        # Update the arrow points
        self.arrow_line.points = [self.center_x, self.center_y, arrow_endpoint[0], arrow_endpoint[1]]
        # print("HI", self.arrow_line.points)

        # Color the arrow based on the magnitude of the force (blue to red scale)
        if self.total_force.length():
            force_magnitude = math.log(self.total_force.length()) / math.log(10) + 5
        else:
            force_magnitude = 0
        # print(force_magnitude)
        t = min(force_magnitude / 5, 1)  # Scale t between 0 and 1 for color interpolation
        self.arrow_color.rgb = [t, 0, 1 - t]  # Transition from blue to red

class GameLayout(Widget):
    intermolecular_forces = BooleanProperty(True)  # Toggle for intermolecular forces
    epsilon = NumericProperty(1.0)  # Lennard-Jones potential depth
    sigma = NumericProperty(1.0)  # Lennard-Jones potential sigma

    def __init__(self, **kwargs):
        super(GameLayout, self).__init__(**kwargs)
        with self.canvas.before:
            Color(0, 0, 0, 1)  # Set background color of the game area (black)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

        self.balls = []
        self.ball_radius = 10  # Radius of the ball, assuming size is 50x50
        self.old_pos = self.pos[:]
        self.old_size = self.size[:]
        self.pos_in_between = self.pos[:]
        self.size_in_between = self.size[:]
        self.scale = 10 ** (2)
        self.gravity = 0  # Initialize gravity
        Clock.schedule_interval(self.update, 1 / 60.0)  # Update 60 times per second

        # Labels for stats
        # self.total_energy_label = Label(text="Total Energy: 0", size_hint=(None, None), pos_hint={})
        # self.temperature_label = Label(text="Temperature: 0", size_hint=(None, None), pos_hint={})
        # self.pressure_label = Label(text="Pressure: 0", size_hint=(None, None), pos_hint={})
        # # self.add_widget(self.total_energy_label)
        # self.add_widget(self.temperature_label)
        # self.add_widget(self.pressure_label)

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
        """
        Spawn a ball at the touch position with a random initial velocity.
        """
        ball = Ball(ball_center=touch.pos, ball_radius=self.ball_radius)

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
        """
        Update ball positions, handle collisions, and calculate energy, temperature, and pressure.
        """
        total_energy = 0
        temperature = 0
        pressure = 0
        for ball in self.balls:
            ball.reset_total_force()
            ball.add_force(Vector(0, -self.gravity))
        for i in range(len(self.balls)):
            ball1 = self.balls[i]
            for j in range(i + 1, len(self.balls)):
                ball2 = self.balls[j]
                if ball1.collide_widget(ball2):
                    ball1.resolve_collision(ball2)
                    ball1.update_color_based_on_speed()
                    ball2.update_color_based_on_speed()
                if self.intermolecular_forces:
                    force = ball1.lennard_jones_force(ball2, self.epsilon, self.sigma, self.scale)
                    # print(force, i, j)
                    ball1.add_force(force)
                    ball2.add_force(-force)
                    
            ball1.update_force_arrow()
            ball1.move()
            ball1.bounce_off_walls()

            # Calculate kinetic energy
            kinetic_energy = 0.5 * (ball1.vx**2 + ball1.vy**2)
            total_energy += kinetic_energy
            temperature += kinetic_energy  # Temperature proportional to kinetic energy

            pressure += abs(ball1.vx) + abs(ball1.vy)  # Simplified pressure calculation

        self.total_energy_label.text = f"Total Energy: {total_energy:.2f}"
        self.temperature_label.text = f"Temperature: {(temperature / len(self.balls)) if len(self.balls) else 0:.2f}"
        self.pressure_label.text = f"Pressure: {pressure:.2f}"

    def on_resize(self):
        # When the game layout is resized, rescale balls' positions
        for ball in self.balls:
            ball.rescale_position(self.pos[:], self.size[:])

    def set_gravity(self, value):
        """Update gravity for all balls based on slider value."""
        self.gravity = value
        for ball in self.balls:
            ball.gravity = self.gravity

    def set_epsilon(self, value):
        """Update the epsilon parameter for Lennard-Jones potential."""
        self.epsilon = value

    def set_sigma(self, value):
        """Update the sigma parameter for Lennard-Jones potential."""
        self.sigma = value

    def toggle_intermolecular_forces(self, switch, value):
        """Toggle intermolecular forces on or off."""
        self.intermolecular_forces = value


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

        # Create a UI panel with sliders for gravity, epsilon, and sigma
        ui_panel = BoxLayout(orientation='vertical', size_hint=(0.8, 0.2), pos_hint={'center_x': 0.5, 'y': 0})
        root.add_widget(ui_panel)

        gravity_label = Label(text="Gravity", size_hint=(None, None), height=30)
        gravity_slider = Slider(min=0, max=10, value=0, step=0.01, size_hint=(1, None), height=30)
        gravity_slider.bind(value=lambda instance, value: game_area.set_gravity(value))

        epsilon_label = Label(text="Epsilon (Potential Depth)", size_hint=(None, None), height=30)
        epsilon_slider = Slider(min=0, max=10, value=1, step=0.1, size_hint=(1, None), height=30)
        epsilon_slider.bind(value=lambda instance, value: game_area.set_epsilon(value))

        sigma_label = Label(text="Sigma (Potential Distance)", size_hint=(None, None), height=30)
        sigma_slider = Slider(min=0.1, max=3, value=1, step=0.01, size_hint=(1, None), height=30)
        sigma_slider.bind(value=lambda instance, value: game_area.set_sigma(value))

        forces_switch_label = Label(text="Intermolecular Forces", size_hint=(None, None), height=30)
        forces_switch = Switch(active=True, size_hint=(None, None), height=50)
        forces_switch.bind(active=game_area.toggle_intermolecular_forces)

        ui_panel.add_widget(gravity_label)
        ui_panel.add_widget(gravity_slider)
        ui_panel.add_widget(epsilon_label)
        ui_panel.add_widget(epsilon_slider)
        ui_panel.add_widget(sigma_label)
        ui_panel.add_widget(sigma_slider)
        ui_panel.add_widget(forces_switch_label)
        ui_panel.add_widget(forces_switch)

        button = Button(text='Clear', size_hint=(0.07, 0.05), pos_hint={'center_x': 0.5, 'center_y': 0.25})
        button.bind(on_press=lambda x: (game_area.clear_widgets(), game_area.balls.clear()))
        root.add_widget(button)
        
        # Labels for stats, positioned using pos_hint
        self.total_energy_label = Label(text="Total Energy: 0", size_hint=(0.2, 0.1), pos_hint={'center_x': 0.18, 'center_y': .95})
        self.temperature_label = Label(text="Temperature: 0", size_hint=(0.2, 0.1), pos_hint={'center_x': 0.51, 'center_y': .95})
        self.pressure_label = Label(text="Pressure: 0", size_hint=(0.2, 0.1), pos_hint={'center_x': 0.84, 'center_y': .95})
        
        game_area.total_energy_label = self.total_energy_label
        game_area.temperature_label = self.temperature_label
        game_area.pressure_label = self.pressure_label
        
        # Add labels to the layout
        root.add_widget(self.total_energy_label)
        root.add_widget(self.temperature_label)
        root.add_widget(self.pressure_label)

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
