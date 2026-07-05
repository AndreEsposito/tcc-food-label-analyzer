from .base import BaseScreen
from kivy.clock import Clock


SPLASH_DURATION = 2.5  # segundos antes de ir para home


class SplashScreen(BaseScreen):
    _transition_event = None

    def on_enter(self):
        """Exibe a identidade visual e agenda transicao para home."""
        self._transition_event = Clock.schedule_once(self._ir_para_home, SPLASH_DURATION)

    def on_leave(self):
        """Cancela a transicao pendente caso a tela seja interrompida."""
        if self._transition_event:
            self._transition_event.cancel()
            self._transition_event = None

    def _ir_para_home(self, dt):
        """Transicao para a tela inicial."""
        self._transition_event = None
        if self.manager:
            self.manager.current = "home"
