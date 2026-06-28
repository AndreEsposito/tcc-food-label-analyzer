from kivy.config import Config
Config.set('graphics', 'fallback', 'true')
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from screens.result import ResultScreen

Builder.load_file('layouts/result.kv')

class TestApp(App):
    def build(self):
        root = FloatLayout()
        screen = ResultScreen(name='result')
        root.add_widget(screen)
        screen.state = 'loading'
        screen._atualizar_visibilidade_estado()
        print('ids_before', screen.ids.keys())
        screen.state = 'success'
        screen._atualizar_visibilidade_estado()
        print('success_exists', screen.ids.get('success_container') is not None)
        success = screen.ids.get('success_container')
        print('success_opacity', success.opacity if success else None)
        print('success_disabled', success.disabled if success else None)
        print('success_size', success.size if success else None)
        print('loading_exists', screen.ids.get('loading_container') is not None)
        print('error_exists', screen.ids.get('error_container') is not None)
        return root

TestApp().build()
