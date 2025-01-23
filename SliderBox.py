from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.graphics import Color, Rectangle, Line


class SliderBox(BoxLayout):
    """A widget that encapsulates a slider with a label, a background, and a border."""
    def __init__(self, label_text, min_value, max_value, default_value, step, callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint = (None, None)
        self.size = (300, 100)  # Default size

        # Add background and border
        with self.canvas.before:
            Color(0.2, 0.2, 0.2, 1)  # Background color
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            Color(0, 0, 1, 1)  # Blue border
            self.border = Line(rectangle=(self.x, self.y, self.width, self.height), width=2)

        # Bind position and size changes to update the background and border
        self.bind(pos=self.update_graphics, size=self.update_graphics)

        # Add label
        self.label = Label(
            text=label_text,
            size_hint=(1, 0.4),
            halign='center',
            valign='middle'
        )
        self.label.bind(size=self._update_label_text_size)
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
        self.border.rectangle = (self.x, self.y, self.width, self.height)

    def _update_label_text_size(self, instance, value):
        """Ensure the label text fits within the box."""
        self.label.text_size = (self.label.width, None)
