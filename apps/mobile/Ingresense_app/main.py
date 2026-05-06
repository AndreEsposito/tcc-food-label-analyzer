import os
import sys

# Garante que o Python encontra os módulos a partir da pasta do projeto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager

from screens.splash import SplashScreen
from screens.home import HomeScreen
from screens.camera import CameraScreen
from screens.preview import PreviewScreen
from screens.result import ResultScreen

# Carrega todos os .kv
for kv in ["splash", "home", "camera", "preview", "result"]:
    Builder.load_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), "layouts", f"{kv}.kv"))

class WindowManager(ScreenManager):
    pass

class IngreSenseApp(App):
    def build(self):
        sm = WindowManager()
        sm.add_widget(SplashScreen(name="splash"))
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(CameraScreen(name="camera"))
        sm.add_widget(PreviewScreen(name="preview"))
        sm.add_widget(ResultScreen(name="result"))
        sm.current = "splash"
        return sm

if __name__ == "__main__":
    IngreSenseApp().run()