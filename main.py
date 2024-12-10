from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.slider import Slider
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.switch import Switch
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.graphics import Color, Ellipse, Rectangle, Line
from game_layout import GameLayout  # Import GameLayout
from HoverItem import HoverItem # Import HoverItem
from TextBlurb import TextBlurb

class MyApp(App):
    def build(self):
        # Root layout for the entire screen
        root = FloatLayout()

        # Add a grey background to cover the entire UI
        self.add_background(root)

        # Create the game area
        self.game_area = GameLayout(size_hint=(0.8, 0.6), pos_hint={'center_x': 0.5, 'center_y': 0.6})

        # Add the game area to the root layout
        root.add_widget(self.game_area)
    
        # Add the preset selector spinner in the control section
        self.add_preset_spinner(root)

        # Add other UI elements
        self.add_ui_elements(root)

        return root

    def add_background(self, root):
        """Add a grey background and bind its size/position to root."""
        with root.canvas.before:
            Color(0.05, 0.05, 0.05, 1)
            self.ui_rect = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=self.update_ui_background, size=self.update_ui_background)

    def update_ui_background(self, instance, *args):
        """Update background dynamically when the window size changes."""
        self.ui_rect.pos = instance.pos
        self.ui_rect.size = instance.size

    def add_preset_spinner(self, root):
        """Add the preset spinner to the bottom control section."""
        spinner_row = BoxLayout(orientation='horizontal', size_hint=(0.3, None), height=40, pos_hint={'center_x': 0.15, 'y': 0.15})

        # Label for the preset spinner
        preset_label = Label(text="Presets:", size_hint=(0.4, 1), font_size=14)
        spinner_row.add_widget(preset_label)

        # Spinner for presets
        preset_spinner = Spinner(
            text="Solid",
            values=("Solid", "Liquid", "Gas"),
            size_hint=(0.6, 1),
            font_size=14
        )
        preset_spinner.bind(text=self.on_preset_selected)
        spinner_row.add_widget(preset_spinner)

        # Add the spinner row to the root layout
        root.add_widget(spinner_row)

    def on_preset_selected(self, spinner, text):
        """Handle preset selection and update the GameLayout."""
        if text == "Solid":
            self.game_area.generate_solid()
        elif text == "Liquid":
            self.game_area.generate_liquid()
        elif text == "Gas":
            self.game_area.generate_gas()

    def add_ui_elements(self, root):
        """Add sliders, switches, and other UI elements."""
        ui_panel = self.create_sliders()
        bottom_row = self.create_bottom_controls()
        root.add_widget(ui_panel)
        root.add_widget(bottom_row)
        self.add_stat_labels(root)

    def create_sliders(self):
        """Create the slider UI for gravity, epsilon, sigma, and delta."""
        ui_panel = GridLayout(cols=2, rows=2, size_hint=(0.9, 0.1), pos_hint={'center_x': 0.5, 'y': 0.2})
        gravity_box, epsilon_box, sigma_box, delta_box = self.create_slider_boxes()
        ui_panel.add_widget(gravity_box)
        ui_panel.add_widget(epsilon_box)
        ui_panel.add_widget(sigma_box)
        ui_panel.add_widget(delta_box)
        return ui_panel

    def create_bottom_controls(self):
        """Create the bottom controls with switches and buttons."""
        bottom_row = BoxLayout(orientation='horizontal', size_hint=(0.9, None), height=50, pos_hint={'center_x': 0.5, 'y': 0.1})

        forces_container, _ = self.create_forces_switch()
        forces_visible_container, _ = self.create_forces_visible_switch()
        clear_button = self.create_hover_button("Clear", self.clear_game_area)
        start_stop_button = self.create_hover_button("Start", self.toggle_simulation)

        bottom_row.add_widget(forces_container)
        bottom_row.add_widget(forces_visible_container)
        bottom_row.add_widget(start_stop_button)
        bottom_row.add_widget(clear_button)
        return bottom_row

    def create_slider_boxes(self):
        """Create individual sliders for game parameters."""
        gravity_box = self.create_slider("Gravity", 0, 10, 0, self.game_area.set_gravity)
        epsilon_box = self.create_slider("Epsilon", 0, 10, 1, self.game_area.set_epsilon)
        sigma_box = self.create_slider("Sigma", 0.1, 3, 1, self.game_area.set_sigma)
        delta_box = self.create_slider("Delta", 0, 1, 1 / 60.0, self.game_area.set_delta)
        return gravity_box, epsilon_box, sigma_box, delta_box

    def create_slider(self, label_text, min_value, max_value, default_value, callback):
        """Helper to create labeled sliders."""
        box = BoxLayout(orientation='horizontal')
        label = Label(text=label_text, size_hint=(0.3, None), height=10)
        slider = Slider(min=min_value, max=max_value, value=default_value, size_hint=(0.7, None), height=10)
        slider.bind(value=lambda instance, value: callback(value))
        box.add_widget(label)
        box.add_widget(slider)
        return box

    def create_hover_button(self, label, callback):
        """Helper to create buttons with hover effects."""
        return HoverItem(
            size_hint=(1, None),
            height=50,
            hoverSource=f"Graphics/{label}_Highlighted.png",
            defaultSource=f"Graphics/{label}.png",
            function=lambda x: callback()
        )

    def toggle_simulation(self):
        """Toggle the simulation state."""
        if self.game_area.simulation_running:
            self.game_area.stop_simulation()
        else:
            self.game_area.start_simulation()

    def clear_game_area(self):
        """Clear the game area of all molecules and bonds."""
        self.game_area.clear_widgets()
        self.game_area.molecules.clear()
        self.game_area.clear_bonds()

    def create_forces_switch(self):
        """Create a switch for intermolecular forces."""
        return self.create_switch("Forces", self.game_area.toggle_intermolecular_forces)

    def create_forces_visible_switch(self):
        """Create a switch to toggle visibility of forces."""
        return self.create_switch("Show Forces", self.game_area.toggle_forces_visible)

    def create_switch(self, label_text, callback):
        """Helper to create labeled switches."""
        container = BoxLayout(orientation='horizontal', size_hint=(0.6, None), height=50)
        label = Label(text=label_text, size_hint=(0.6, 1))
        switch = Switch(active=True, size_hint=(0.4, 1))
        switch.bind(active=callback)
        container.add_widget(label)
        container.add_widget(switch)
        return container, switch

    def add_stat_labels(self, root):
        """Add labels to display simulation stats."""
        self.game_area.total_energy_label = Label(text="Total Energy: 0", size_hint=(0.2, 0.1), pos_hint={'center_x': 0.18, 'center_y': 0.95})
        self.game_area.temperature_label = Label(text="Temperature: 0", size_hint=(0.2, 0.1), pos_hint={'center_x': 0.51, 'center_y': 0.95})
        self.game_area.pressure_label = Label(text="Pressure: 0", size_hint=(0.2, 0.1), pos_hint={'center_x': 0.84, 'center_y': 0.95})

        root.add_widget(self.game_area.total_energy_label)
        root.add_widget(self.game_area.temperature_label)
        root.add_widget(self.game_area.pressure_label)


if __name__ == "__main__":
    MyApp().run()
