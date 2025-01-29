from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.slider import Slider
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.switch import Switch
from kivy.uix.spinner import Spinner
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Rectangle, Line
from game_layout import GameLayout  # Import GameLayout
from HoverItem import HoverItem # Import HoverItem
from TextBlurb import TextBlurb
from CustomSlider import CustomSlider
from SliderBox import SliderBox
from SpinnerBox import SpinnerBox
from simulation import GameScreen

class WindowManager(ScreenManager):
    pass

class GameApp(App):

    def build(self):
        self.window_manager = WindowManager()
        self.game_screen = GameScreen()
        self.window_manager.add_widget(self.game_screen)
        return self.window_manager


if __name__ == "__main__":
    GameApp().run()