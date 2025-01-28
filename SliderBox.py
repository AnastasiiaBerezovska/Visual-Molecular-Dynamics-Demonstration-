from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.graphics import Color, Rectangle, Line
import os


class SliderBox(BoxLayout):
    """A widget that encapsulates a slider with a label, a background, and a border."""
    
    def __init__(self, label_text, min_value, max_value, default_value, step, callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.font_path = os.path.join(os.path.dirname(__file__), "Fonts/Impact.ttf")
        self.base_font_size = 10
        self.font_scale_factor = 1
        # self.size_hint = (None, None)
        # self.size = (300, 100)

        # Add background and border
        with self.canvas.before:
            Color(0.2, 0.2, 0.2, 1)  # Background color
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            # Color(67/255, 157/255, 1, 1)  # Blue border
            # self.border = Line(rectangle=(self.x, self.y, self.width, self.height), width=2)

        # Bind position and size changes to update the background and border
        self.bind(pos=self.update_graphics, size=self.update_graphics)
        self.bind(size=self._update_label_text_size)

        # Add label
        self.label = Label(
            text=label_text,
            size_hint=(1, 0.4),
            font_name=self.font_path,
            font_size=10,
            halign='center',
            valign='middle'
        )
        self.add_widget(self.label)

        # Add slider
        self.slider = Slider(
            min=min_value,
            max=max_value,
            value=default_value,
            step=step,
            size_hint=(1, 0.6)
        )
        self.slider.bind(value=lambda instance, value: callback(value))
        self.add_widget(self.slider)

    def update_graphics(self, *args):
        """Update the background and border dimensions."""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        # self.border.rectangle = (self.x, self.y, self.width, self.height)

    def _update_label_text_size(self, *args):
        """Ensure the label text fits within the box."""
        self.label.height = self.height * .3
        self.label.font_size = self.height * .2
