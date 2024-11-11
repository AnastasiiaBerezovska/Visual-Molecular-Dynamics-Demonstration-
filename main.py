from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.slider import Slider
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.switch import Switch
from kivy.graphics import Color, Ellipse, Rectangle, Line
from game_layout import GameLayout  # Import GameLayout
from HoverItem import HoverItem # Import HoverItem

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
        
        # Gravity, epsilon, sigma, and delta sliders
        gravity_box, epsilon_box, sigma_box, delta_box = self.create_slider_boxes(game_area)
        
        # Add sliders to the grid layout
        ui_panel.add_widget(gravity_box)
        ui_panel.add_widget(epsilon_box)
        ui_panel.add_widget(sigma_box)
        ui_panel.add_widget(delta_box)

        # Create a BoxLayout for the forces switch, control buttons, and clear button
        bottom_row = BoxLayout(orientation='horizontal', size_hint=(0.9, None), height=50, pos_hint={'center_x': 0.5, 'y': 0.1})

        # Forces switch label and switch
        forces_container, forces_switch = self.create_forces_switch(game_area)
        
        # Forces switch label and switch
        forces_visible_container, forces_visible_switch = self.create_forces_visible_switch(game_area)

        # Clear button
        clear_button = Button(text='Clear', size_hint=(0.3, None), height=50)
        clear_button.bind(on_press=lambda x: (game_area.clear_widgets(), game_area.molecules.clear(), game_area.clear_bonds()))
        clear_button = HoverItem(size_hint=(0.3, None), height=50, hoverSource="Graphics/Clear_Highlighted.png", defaultSource="Graphics/Clear.png", function=lambda x: (game_area.clear_widgets(), game_area.molecules.clear(), game_area.clear_bonds()))

        # Start/Stop button
        start_stop_button = Button(text='Start', size_hint=(0.3, None), height=50)
        start_stop_button.bind(on_press=lambda x: self.toggle_simulation(start_stop_button, game_area))

        # Speed control slider
        speed_box = BoxLayout(orientation='horizontal', spacing=10)
        speed_label = Label(text="Speed of Simulation (Y increase, H decrease)", size_hint=(0.3, None), height=50)
        speed_slider = Slider(min=0.1, max=1, value=1, step=0.1, size_hint=(0.7, None), height=50)
        speed_slider.bind(value=lambda instance, value: game_area.set_speed(value))
        
        size_box = BoxLayout(orientation='horizontal', spacing=10)
        size_label = Label(text="Size of Molecules (U increase, J decrease)", size_hint=(0.3, None), height=50)
        size_slider = Slider(min=0.2, max=1, value=0.6, step=0.05, size_hint=(0.7, None), height=50)
        size_slider.bind(value=lambda instance, value: game_area.set_size(value))
        
        speed_box.add_widget(speed_label)
        speed_box.add_widget(speed_slider)
        size_box.add_widget(size_label)
        size_box.add_widget(size_slider)
        
        game_area.speed_slider = speed_slider
        game_area.size_slider = size_slider

        # Add the widgets to the bottom row layout
        bottom_row.add_widget(forces_container)
        bottom_row.add_widget(forces_visible_container)
        bottom_row.add_widget(start_stop_button)
        bottom_row.add_widget(speed_box)
        bottom_row.add_widget(size_box)
        bottom_row.add_widget(clear_button)

        # Add the bottom row to the root layout
        root.add_widget(bottom_row)

        # Add other panels and UI elements
        root.add_widget(ui_panel)
        
        # Labels for stats, positioned using pos_hint
        self.add_stat_labels(game_area, root)

        return root

    def toggle_simulation(self, button, game_area):
        if button.text == 'Start':
            game_area.start_simulation()
            button.text = 'Stop'
        else:
            game_area.stop_simulation()
            button.text = 'Start'

    def create_slider_boxes(self, game_area):
        # Gravity label and slider
        gravity_box = BoxLayout(orientation='horizontal', spacing=0)
        gravity_label = Label(text="Gravity (W increase, S decrease)", size_hint=(0.3, None), height=10)
        gravity_slider = Slider(min=0, max=10, value=0, step=0.01, size_hint=(0.7, None), height=10)
        gravity_slider.bind(value=lambda instance, value: game_area.set_gravity(value))
        gravity_box.add_widget(gravity_label)
        gravity_box.add_widget(gravity_slider)

        # Epsilon label and slider (inside BoxLayout)
        epsilon_box = BoxLayout(orientation='horizontal', spacing=0)
        epsilon_label = Label(text="Epsilon (Potential Depth used for Lennard-Jones force between Molecules) (E increase, D decrease)", size_hint=(0.3, None), height=10)
        epsilon_slider = Slider(min=0, max=10, value=1, step=0.1, size_hint=(0.7, None), height=10)
        epsilon_slider.bind(value=lambda instance, value: game_area.set_epsilon(value))
        epsilon_box.add_widget(epsilon_label)
        epsilon_box.add_widget(epsilon_slider)

        # Sigma label and slider (inside BoxLayout)
        sigma_box = BoxLayout(orientation='horizontal', spacing=0)
        sigma_label = Label(text="Sigma (Potential Distance used for Lennard-Jones force between Molecules) (R increase, F decrease)", size_hint=(0.3, None), height=10)
        sigma_slider = Slider(min=0.1, max=3, value=1, step=0.01, size_hint=(0.7, None), height=10)
        sigma_slider.bind(value=lambda instance, value: game_area.set_sigma(value))
        sigma_box.add_widget(sigma_label)
        sigma_box.add_widget(sigma_slider)

        # Delta label and slider (inside BoxLayout)
        delta_box = BoxLayout(orientation='horizontal', spacing=0)
        delta_label = Label(text="Delta (Timestep update for Verlet's Algorithm) (T increase, G decrease)", size_hint=(0.3, None), height=10)
        delta_slider = Slider(min=0, max=1, value=1 / 60.0, step=1 / 60.0, size_hint=(0.7, None), height=10)
        delta_slider.bind(value=lambda instance, value: game_area.set_delta(value))
        delta_box.add_widget(delta_label)
        delta_box.add_widget(delta_slider)
        
        game_area.gravity_slider = gravity_slider
        game_area.epsilon_slider = epsilon_slider
        game_area.sigma_slider = sigma_slider
        game_area.delta_slider = delta_slider
        
        return gravity_box, epsilon_box, sigma_box, delta_box

    def create_forces_switch(self, game_area):
        forces_container = BoxLayout(orientation='horizontal', size_hint=(0.6, None), height=50)
        forces_switch_label = Label(text="Intermolecular Forces", size_hint=(0.6, 1), height=30)
        forces_switch = Switch(active=True, size_hint=(0.4, 1), height=30)
        forces_switch.bind(active=game_area.toggle_intermolecular_forces)
        forces_container.add_widget(forces_switch_label)
        forces_container.add_widget(forces_switch)
        
        return forces_container, forces_switch
    
    def create_forces_visible_switch(self, game_area):
        forces_visible_container = BoxLayout(orientation='horizontal', size_hint=(0.6, None), height=50)
        forces_visible_switch_label = Label(text="See Net Force", size_hint=(0.6, 1), height=30)
        forces_visible_switch = Switch(active=True, size_hint=(0.4, 1), height=30)
        forces_visible_switch.bind(active=game_area.toggle_forces_visible)
        forces_visible_container.add_widget(forces_visible_switch_label)
        forces_visible_container.add_widget(forces_visible_switch)
        
        return forces_visible_container, forces_visible_switch

    def add_stat_labels(self, game_area, root):
        self.total_energy_label = Label(text="Total Energy: 0", size_hint=(0.2, 0.1), pos_hint={'center_x': 0.18, 'center_y': .95})
        self.temperature_label = Label(text="Temperature: 0", size_hint=(0.2, 0.1), pos_hint={'center_x': 0.51, 'center_y': .95})
        self.pressure_label = Label(text="Pressure: 0", size_hint=(0.2, 0.1), pos_hint={'center_x': 0.84, 'center_y': .95})
        
        game_area.total_energy_label = self.total_energy_label
        game_area.temperature_label = self.temperature_label
        game_area.pressure_label = self.pressure_label
        
        root.add_widget(self.total_energy_label)
        root.add_widget(self.temperature_label)
        root.add_widget(self.pressure_label)

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
