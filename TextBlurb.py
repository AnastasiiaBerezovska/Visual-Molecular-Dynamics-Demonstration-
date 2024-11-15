from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import BooleanProperty, StringProperty


class TextBlurb(BoxLayout):
    """A reusable text blurb widget constrained to a box with toggleable visibility."""
    is_visible = BooleanProperty(False)  # Track visibility state
    text = StringProperty("This is a text blurb.")  # Text for the blurb

    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.size_hint = (None, None)  # Make the widget's size explicit
        self.size = (400, 200)  # Set the fixed size for the box

        # Label for the text blurb (constrained within the widget)
        self.text_label = Label(
            text=self.text,
            opacity=0,  # Initially hidden
            size_hint=(1, 1),
            text_size=(self.width - 20, None),  # Constrain text to fit inside the widget
            halign='center',  # Center horizontally
            valign='middle'  # Center vertically
        )
        self.text_label.bind(size=self._update_text_size)  # Adjust text size dynamically
        self.add_widget(self.text_label)

    def toggle_visibility(self):
        """Toggle the visibility of the text blurb."""
        self.is_visible = not self.is_visible
        self.text_label.opacity = 1 if self.is_visible else 0

    def _update_text_size(self, instance, value):
        """Adjust the text size dynamically based on the label size."""
        self.text_label.text_size = (self.width - 20, self.text_label.height)
