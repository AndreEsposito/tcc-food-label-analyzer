from .base import BaseScreen
from kivy.animation import Animation
from kivy.clock import Clock


SPLASH_DURATION = 2.5  # segundos antes de ir para home


class SplashScreen(BaseScreen):

    def on_enter(self):
        """Inicia animação e agenda transição para home."""
        self._animar_icone()
        Clock.schedule_once(self._ir_para_home, SPLASH_DURATION)

    def on_leave(self):
        """Para animações ao sair."""
        icon = self.ids.get("splash_icon")
        if icon:
            Animation.cancel_all(icon)

    def _animar_icone(self):
        """Rotaciona o ícone continuamente."""
        icon = self.ids.get("splash_icon")
        if not icon:
            return

        # Define o ponto de rotação no centro do widget
        icon.canvas.before.clear()

        anim = Animation(angle=360, duration=1.2)
        anim += Animation(angle=720, duration=1.2)

        # Usa propriedade de rotação via canvas
        self._rodar(icon)

    def _rodar(self, icon):
        """Loop de rotação usando Clock."""
        from kivy.graphics.context_instructions import Rotate, PushMatrix, PopMatrix
        from kivy.graphics import PushMatrix, PopMatrix, Rotate

        # Limpa instruções anteriores para não acumular
        with icon.canvas.before:
            PushMatrix()
            self._rotate_instr = Rotate(angle=0, origin=icon.center)

        with icon.canvas.after:
            PopMatrix()

        self._angle = 0
        Clock.schedule_interval(self._update_rotation, 1 / 60)

    def _update_rotation(self, dt):
        """Atualiza o ângulo de rotação a cada frame."""
        self._angle = (self._angle + 3) % 360  # 3° por frame = ~180°/s
        if hasattr(self, "_rotate_instr"):
            self._rotate_instr.angle = self._angle
            # Mantém a origem centralizada mesmo após resize
            icon = self.ids.get("splash_icon")
            if icon:
                self._rotate_instr.origin = icon.center

    def _ir_para_home(self, dt):
        """Transição para a tela inicial."""
        Clock.unschedule(self._update_rotation)
        self.manager.current = "home"
