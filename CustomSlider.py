from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.properties import NumericProperty, StringProperty
from kivy.graphics import Rectangle


class CustomSlider(Widget):
    value = NumericProperty(0)  # Slider value (0 to 1)
    min = NumericProperty(0)   # Minimum slider value
    max = NumericProperty(100)  # Maximum slider value
    step = NumericProperty(1)   # Step value for the slider

    track_image = StringProperty("")  # Path to track image
    thumb_image = StringProperty("")  # Path to thumb image

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.track = Image(
            source=self.track_image,
            size_hint=(None, None),
            allow_stretch=True,
            keep_ratio=False,
        )
        self.thumb = Image(
            source=self.thumb_image,
            size_hint=(None, None),
            size=(30, 30),
            allow_stretch=True,
        )

        self.add_widget(self.track)
        self.add_widget(self.thumb)

        self.bind(pos=self.update_positions, size=self.update_positions)
        self.bind(value=self.update_thumb_from_value)

    def on_touch_down(self, touch):
        """Handle touch events for interaction."""
        if self.collide_point(*touch.pos):
            self.update_thumb_position(touch.x)
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        """Handle dragging of the thumb."""
        if self.collide_point(*touch.pos):
            self.update_thumb_position(touch.x)
            return True
        return super().on_touch_move(touch)

    def update_thumb_position(self, touch_x):
        """Move the thumb and update the slider value with steps."""
        x_min = self.x
        x_max = self.x + self.width - self.thumb.width
        new_x = min(max(touch_x, x_min), x_max)
        
        raw_value = self.min + (self.max - self.min) * ((new_x - x_min) / (self.width - self.thumb.width))
        
        snapped_value = round((raw_value - self.min) / self.step) * self.step + self.min
        self.value = max(self.min, min(snapped_value, self.max))
        
        self.thumb.pos = (self.x + (self.value - self.min) / (self.max - self.min) * (self.width - self.thumb.width),
                          self.center_y - self.thumb.height / 2)

    def update_positions(self, *args):
        """Update positions of the track and thumb."""
        self.track.size = (self.width, 10)
        self.track.pos = (self.x, self.center_y - 5)
        self.thumb.pos = (self.x + (self.value - self.min) / (self.max - self.min) * (self.width - self.thumb.width),
                          self.center_y - self.thumb.height / 2)
        
    def update_thumb_from_value(self, *args):
        """Update the thumb's position based on the current slider value."""
        self.thumb.pos = (
            self.x + (self.value - self.min) / (self.max - self.min) * (self.width - self.thumb.width),
            self.center_y - self.thumb.height / 2,
        )
