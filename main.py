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
from game_layout import GameLayout
from HoverItem import HoverItem
from TextBlurb import TextBlurb
from CustomSlider import CustomSlider
from SliderBox import SliderBox
from SpinnerBox import SpinnerBox
from simulation import GameScreen
from start_screen import StartScreen

class WindowManager(ScreenManager):
    
    def start_game(self):
        self.current = "GameScreen"

class GameApp(App):

    def build(self):
        self.window_manager = WindowManager()
        self.start_screen = StartScreen()
        self.game_screen = GameScreen()
        self.window_manager.add_widget(self.start_screen)
        self.window_manager.add_widget(self.game_screen)
        self.window_manager.current = "StartScreen"
        return self.window_manager


if __name__ == "__main__":
    GameApp().run()