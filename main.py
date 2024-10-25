from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
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

class Molecule(Widget):
    # gravity = NumericProperty(0)  # Gravity value affecting the molecule
    color_slow = [5, 0, 102, 255]
    color_fast = [255, 81, 220, 255]
    color = ListProperty([x / 255 for x in color_fast])  # Initial color is red (RGBA)
    speed_cap = 500
    force_cap = 30000

    def __init__(self, **kwargs):
        
        self.center = kwargs.pop("molecule_center")
        self.radius = kwargs.pop("molecule_radius")
        self.total_velocity = Vector(kwargs.pop("molecule_vx"), kwargs.pop("molecule_vy"))
        
        self.parentpos = kwargs.pop("parent_pos")
        self.parentsize = kwargs.pop("parent_size")
        
        super().__init__(**kwargs)
        
        self.size = (self.radius * 2, self.radius * 2)  # Define the size of the molecule
        self.total_force = Vector(0, 0)
        
        with self.canvas:
            self.color_instruction = Color(*self.color)  # Set initial color
            self.molecule_shape = Ellipse(pos=self.pos, size=self.size)  # Set initial position and size
            self.arrow_color = Color(0, 0, 1, 1)  # Blue for initial arrow color
            self.arrow_line = Line(points=[], width=4)  # Arrow to represent force
            
    def fix_speed(self):
        
        if self.total_velocity.length() > self.speed_cap:
            self.total_velocity *= self.speed_cap / self.total_velocity.length()
            
    def fix_force(self):
        
        if self.total_force.length() > self.force_cap:
            self.total_force *= self.force_cap / self.total_force.length()

    def move(self, delta):
        
        self.fix_force()
        
        self.pos = self.total_velocity * delta + 0.5 * self.total_force * (delta ** 2) + self.pos
        self.molecule_shape.pos = self.pos  # Update the molecule's position in the canvas
        self.bounce_off_walls()
        
        self.total_velocity += self.total_force * delta
        self.fix_speed()
        
        print(self.total_force.length())
        
        self.update_color_based_on_speed()
        self.update_force_arrow()

    def bounce_off_walls(self):
        # Bounce off the walls of the layout, accounting for the molecule's size
        if self.x <= self.parentpos[0] or self.right >= self.parentpos[0] + self.parentsize[0]:
            self.total_velocity = Vector(-self.total_velocity.x, self.total_velocity.y)
            
        if self.y <= self.parentpos[1] or self.top >= self.parentpos[1] + self.parentsize[1]:
            self.total_velocity = Vector(self.total_velocity.x, -self.total_velocity.y)
            
        self.keep_within_bounds()

    def rescale_position(self, new_pos, new_size):
        """
        Proportionally rescale the molecule's position according to the new layout dimensions.
        """
        # Calculate the proportional change in size
        proportion_x = (self.pos[0] - self.parentpos[0]) / self.parentsize[0]
        proportion_y = (self.pos[1] - self.parentpos[1]) / self.parentsize[1]
        # print(f"Previous size: {self.parentpos}, New size: {new_size}")

        # Adjust the position of the molecule relative to the new layout size
        self.pos = (new_size[0] * proportion_x + new_pos[0], new_size[1] * proportion_y + new_pos[1])
        
        self.total_velocity = Vector(   self.total_velocity.x * new_size[0] / self.parentsize[0],
                                        self.total_velocity.y * new_size[1] / self.parentsize[1])
        
        self.fix_speed()
        self.update_color_based_on_speed()
        
        # Update the molecule's position on the canvas
        self.molecule_shape.pos = self.pos
        
        self.parentpos = new_pos
        self.parentsize = new_size
        self.keep_within_bounds()

    def keep_within_bounds(self):
        """
        Ensure the molecule stays within the bounds of the layout after a resize.
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
        self.molecule_shape.pos = self.pos

    def collide_widget(self, other):
        """
        Check if the molecule collides with another widget (another molecule).
        """
        distance = Vector(self.center).distance(other.center)
        return distance <= (self.width / 2 + other.width / 2)

    def resolve_collision(self, other):
        """
        Resolve a collision between two molecules using basic 2D collision mechanics.
        """
        v1 = self.total_velocity
        v2 = other.total_velocity

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

        self.total_velocity = v1n_new_vec + v1t_new_vec
        other.total_velocity = v2n_new_vec + v2t_new_vec
        
        self.fix_speed()
        other.fix_speed()

    def update_color_based_on_speed(self):
        """
        Update the molecule's color based on its speed, interpolating between slow and fast colors.
        """
        
        t = min(self.total_velocity.length(), self.speed_cap) / self.speed_cap  # t is between 0 and 1 based on the speed
        self.color_instruction.rgb = [(self.color_slow[0] + (self.color_fast[0] - self.color_slow[0]) * t) / 255,
                                      (self.color_slow[1] + (self.color_fast[1] - self.color_slow[1]) * t) / 255,
                                      (self.color_slow[2] + (self.color_fast[2] - self.color_slow[2]) * t) / 255]
        
    def lennard_jones_force(self, other, epsilon, sigma, scale):
        """
        Calculate the Lennard-Jones force between this molecule and another molecule.
        :param other: The other molecule object.
        :param epsilon: Depth of the potential well.
        :param sigma: Distance at which the potential is zero.
        :return: A Vector representing the force applied on this molecule due to the other molecule.
        """
        r = (Vector(self.center).distance(other.center)) / scale # Calculate distance between two molecules
        
        if r == 0:
            return Vector(0, 0)  # Avoid division by zero if the molecules are at the same position

        # Lennard-Jones force formula
        force_magnitude = 1000 * epsilon * ((2 * (sigma / r) ** 12) - ((sigma / r) ** 6)) / r ** 2
        force_direction = (Vector(self.center) - Vector(other.center)).normalize()  # Direction of the force
        
        return force_direction * force_magnitude

    def reset_total_force(self):
        self.total_force = Vector(0, 0)

    def add_force(self, force_to_add):
        self.total_force += force_to_add

    def update_force_arrow(self):
        """
        Update the arrow direction, length, and color based on the total force.
        :param total_force: The total Lennard-Jones force applied to this molecule.
        """
        # Calculate the arrow's end position based on the force magnitude and direction
        if self.total_force.length():
            force_magnitude = math.log(self.total_force.length()) / math.log(10) + 5
        else:
            force_magnitude = 0
        
        t = max(min(force_magnitude / 5, 1), 0)  # Scale t between 0 and 1 for color interpolation
        
        arrow_length = 30 * t # Limit arrow length to 30
        arrow_endpoint = Vector(self.center) + self.total_force.normalize() * arrow_length

        # Update the arrow points
        self.arrow_line.points = [self.center_x, self.center_y, arrow_endpoint[0], arrow_endpoint[1]]

        # Color the arrow based on the magnitude of the force (blue to red scale)
        self.arrow_color.rgb = [t, 0, 1 - t]  # Transition from blue to red

class GameLayout(Widget):
    intermolecular_forces = BooleanProperty(True)  # Toggle for intermolecular forces
    epsilon = NumericProperty(1.0)  # Lennard-Jones potential depth
    sigma = NumericProperty(1.0)  # Lennard-Jones potential sigma
    spring_constant = 100.0
    spring_rest_length = 2.0

    def __init__(self, **kwargs):
        super(GameLayout, self).__init__(**kwargs)
        with self.canvas.before:
            Color(0, 0, 0, 1)  # Set background color of the game area (black)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

        self.molecules = []  # List of all molecules in the game
        self.bonds = {}  # Dictionary to store Line objects for each bond
        self.molecule_radius = 10  # Radius of the molecule
        self.old_pos = self.pos[:]
        self.old_size = self.size[:]
        self.pos_in_between = self.pos[:]
        self.size_in_between = self.size[:]
        self.scale = 10 ** (2)
        self.gravity = 0  # Initialize gravity
        self.delta = 1 / 60.0  # Time step
        self.selected_molecule = None  # Track the first selected molecule for bonding
        Clock.schedule_interval(self.update, 1 / 60.0)  # Update 60 times per second

        # Labels for stats
        # self.total_energy_label = Label(text="Total Energy: 0", size_hint=(None, None), pos_hint={})
        # self.temperature_label = Label(text="Temperature: 0", size_hint=(None, None), pos_hint={})
        # self.pressure_label = Label(text="Pressure: 0", size_hint=(None, None), pos_hint={})
        # # self.add_widget(self.total_energy_label)
        # self.add_widget(self.temperature_label)
        # self.add_widget(self.pressure_label)

    def create_bond(self, molecule1, molecule2):
        """Creates a bond between two molecules and a Line object to represent it."""
        if (molecule1, molecule2) not in self.bonds and (molecule2, molecule1) not in self.bonds:

            # Create a Line object for the bond
            with self.canvas:
                line = Line(points=[molecule1.center_x, molecule1.center_y, molecule2.center_x, molecule2.center_y], width=1)
                # Store the line associated with this bond in bond_lines
                self.bonds[(molecule1, molecule2)] = line

    def remove_bond(self, molecule1, molecule2):
        """Removes a bond between two molecules and its associated Line object."""
        if (molecule1, molecule2) in self.bonds:
            bond = (molecule1, molecule2)
        elif (molecule2, molecule1) in self.bonds:
            bond = (molecule2, molecule1)
        else:
            return False
        
        self.canvas.remove(self.bonds[bond])
        del self.bonds[bond]
        return True
            
    def clear_bonds(self):
        """Clears all bonds and removes bond lines from the canvas."""
        for bond, line in self.bonds.items():
            self.canvas.remove(line)
        self.bonds.clear()

    def update_bond_lines(self):
        """Update the positions of all bond lines."""
        # Ensure the color is white when updating bond lines
        with self.canvas:
            Color(1, 1, 1, 1)  # Set the color to white
            for bond in self.bonds:
                line = self.bonds[bond]
                line.points = [bond[0].center_x, bond[0].center_y, bond[1].center_x, bond[1].center_y]
                
    def apply_spring_force(self):
        """Apply spring force to all bonded pairs of molecules."""
        for molecule1, molecule2 in self.bonds:
            # Vector between molecule1 and molecule2
            r12 = Vector(molecule2.center_x - molecule1.center_x, molecule2.center_y - molecule1.center_y)
            distance = r12.length()

            # Calculate the spring force using Hooke's law
            force_magnitude = -self.spring_constant * (distance - self.spring_rest_length)

            if distance > 0:
                force_vector = (force_magnitude / distance) * r12  # Normalize the force vector
                # Apply the force to both molecules
                molecule1.add_force(-force_vector)
                molecule2.add_force(force_vector)

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
        # if self.is_safe_touch(touch):
        #     self.spawn_molecule_at_touch(touch)
        # return
        """Handle touch events for creating bonds between two selected molecules."""
        
        selected_molecule = None

        # Check if the touch is near any molecule
        for molecule in self.molecules:
            if Vector(touch.pos).distance(molecule.center) <= self.molecule_radius:
                selected_molecule = molecule
                break

        if selected_molecule:
            if self.selected_molecule:
                # First molecule selected
                if not self.remove_bond(selected_molecule, self.selected_molecule):
                    self.create_bond(selected_molecule, self.selected_molecule)
                self.selected_molecule = None
            else:
                self.selected_molecule = selected_molecule
        else:
            # If no molecule is selected, spawn a new molecule at the touch position
            if self.is_safe_touch(touch):
                self.spawn_molecule_at_touch(touch)
            self.selected_molecule = None

    def is_safe_touch(self, touch):
        """
        Check if the touch is within safe bounds to prevent the molecule from extending past the edges.
        """
        safe_margin_x = self.molecule_radius
        safe_margin_y = self.molecule_radius

        return (
            self.pos[0] + safe_margin_x <= touch.x <= self.right - safe_margin_x and
            self.pos[1] + safe_margin_y <= touch.y <= self.top - safe_margin_y
        )

    def spawn_molecule_at_touch(self, touch):
        """
        Spawn a molecule at the touch position with a random initial velocity.
        """
        # Generate random angle
        angle = uniform(-math.pi, math.pi)
        
        
        vx = 300 * math.cos(angle)
        vy = 300 * math.sin(angle)
        
        molecule = Molecule(molecule_center=(touch.pos[0] + 40, touch.pos[1] + 40), molecule_radius=self.molecule_radius, molecule_vx=vx, molecule_vy=vy,
                    parent_pos=self.pos[:], parent_size=self.size[:])

        molecule.update_color_based_on_speed()  # Ensure the color is updated based on initial speed
        self.add_widget(molecule)
        self.molecules.append(molecule)

    def update(self, dt):
        """
        Update molecule positions, handle collisions, and update bonds.
        """
        total_energy = 0
        temperature = 0
        pressure = 0
        for molecule in self.molecules:
            molecule.reset_total_force()
            molecule.add_force(Vector(0, -self.gravity))
            
        self.apply_spring_force()

        for i in range(len(self.molecules)):
            molecule1 = self.molecules[i]
            for j in range(i + 1, len(self.molecules)):
                molecule2 = self.molecules[j]
                if molecule1.collide_widget(molecule2):
                    molecule1.resolve_collision(molecule2)
                    molecule1.update_color_based_on_speed()
                    molecule2.update_color_based_on_speed()
                if self.intermolecular_forces:
                    force = molecule1.lennard_jones_force(molecule2, self.epsilon, self.sigma, self.scale)
                    # print(force, i, j)
                    molecule1.add_force(force)
                    molecule2.add_force(-force)
                    
            molecule1.update_force_arrow()
            molecule1.move(self.delta)

            # Calculate kinetic energy
            kinetic_energy = 0.5 * (molecule1.total_velocity.length2())
            total_energy += kinetic_energy
            temperature += kinetic_energy  # Temperature proportional to kinetic energy

            pressure += abs(molecule1.total_velocity.x) + abs(molecule1.total_velocity.y)  # Simplified pressure calculation

        # self.total_energy_label.text = f"Total Energy: {total_energy:.2f}"
        # self.temperature_label.text = f"Temperature: {(temperature / len(self.molecules)) if len(self.molecules) else 0:.2f}"
        # self.pressure_label.text = f"Pressure: {pressure:.2f}"
        # Update bond lines after molecule movement
        self.update_bond_lines()

    def on_resize(self):
        # When the game layout is resized, rescale molecules' positions
        for molecule in self.molecules:
            molecule.rescale_position(self.pos[:], self.size[:])

    def set_gravity(self, value):
        """Update gravity for all molecules based on slider value."""
        self.gravity = value
        # for molecule in self.molecules:
        #     molecule.gravity = self.gravity

    def set_epsilon(self, value):
        """Update the epsilon parameter for Lennard-Jones potential."""
        self.epsilon = value

    def set_sigma(self, value):
        """Update the sigma parameter for Lennard-Jones potential."""
        self.sigma = value
        
    def set_delta(self, value):
        """Update the sigma parameter for Lennard-Jones potential."""
        self.delta = value

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

        # Create a GridLayout with 2 rows and 2 columns (for the sliders and labels)
        ui_panel = GridLayout(
            cols=2, 
            rows=2, 
            padding=0, 
            spacing=[20, 0],  # Reduce vertical spacing to 10 between rows
            size_hint=(0.9, 0.1), 
            pos_hint={'center_x': 0.5, 'y': 0.2}
        )
        
        # Gravity label and slider (inside BoxLayout)
        gravity_box = BoxLayout(orientation='horizontal', spacing=0)
        gravity_label = Label(text="Gravity", size_hint=(0.3, None), height=10)
        gravity_slider = Slider(min=0, max=10, value=0, step=0.01, size_hint=(0.7, None), height=10)
        gravity_slider.bind(value=lambda instance, value: game_area.set_gravity(value))
        gravity_box.add_widget(gravity_label)
        gravity_box.add_widget(gravity_slider)

        # Epsilon label and slider (inside BoxLayout)
        epsilon_box = BoxLayout(orientation='horizontal', spacing=0)
        epsilon_label = Label(text="Epsilon (Potential Depth)", size_hint=(0.3, None), height=10)
        epsilon_slider = Slider(min=0, max=10, value=1, step=0.1, size_hint=(0.7, None), height=10)
        epsilon_slider.bind(value=lambda instance, value: game_area.set_epsilon(value))
        epsilon_box.add_widget(epsilon_label)
        epsilon_box.add_widget(epsilon_slider)

        # Sigma label and slider (inside BoxLayout)
        sigma_box = BoxLayout(orientation='horizontal', spacing=0)
        sigma_label = Label(text="Sigma (Potential Distance)", size_hint=(0.3, None), height=10)
        sigma_slider = Slider(min=0.1, max=3, value=1, step=0.01, size_hint=(0.7, None), height=10)
        sigma_slider.bind(value=lambda instance, value: game_area.set_sigma(value))
        sigma_box.add_widget(sigma_label)
        sigma_box.add_widget(sigma_slider)

        # Delta label and slider (inside BoxLayout)
        delta_box = BoxLayout(orientation='horizontal', spacing=0)
        delta_label = Label(text="Delta (Timestep update for Verlet's)", size_hint=(0.3, None), height=10)
        delta_slider = Slider(min=0, max=1, value=1 / 60.0, step=1 / 60.0, size_hint=(0.7, None), height=10)
        delta_slider.bind(value=lambda instance, value: game_area.set_delta(value))
        delta_box.add_widget(delta_label)
        delta_box.add_widget(delta_slider)

        # Add widgets to the grid layout
        ui_panel.add_widget(gravity_box)
        ui_panel.add_widget(epsilon_box)
        ui_panel.add_widget(sigma_box)
        ui_panel.add_widget(delta_box)

        # Create a BoxLayout for the forces switch and button (horizontal layout)
        bottom_row = BoxLayout(orientation='horizontal', size_hint=(0.9, None), height=50, pos_hint={'center_x': 0.5, 'y': 0.1})

        # Forces switch label and switch (on the left side)
        forces_container = BoxLayout(orientation='horizontal', size_hint=(0.6, None), height=50)
        forces_switch_label = Label(text="Intermolecular Forces", size_hint=(0.6, 1), height=30)
        forces_switch = Switch(active=True, size_hint=(0.4, 1), height=30)
        forces_switch.bind(active=game_area.toggle_intermolecular_forces)
        forces_container.add_widget(forces_switch_label)
        forces_container.add_widget(forces_switch)

        # Clear button (on the right side)
        button = Button(text='Clear', size_hint=(0.3, None), height=50)
        button.bind(on_press=lambda x: (game_area.clear_widgets(), game_area.molecules.clear(), game_area.clear_bonds()))

        # Add the forces_container and button to the bottom row layout
        bottom_row.add_widget(forces_container)
        bottom_row.add_widget(button)

        # Add the bottom row to the root layout
        root.add_widget(bottom_row)

        # Add other panels and UI elements
        root.add_widget(ui_panel)
        
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
