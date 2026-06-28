from kivy.uix.screenmanager import Screen
from kivy.core.image import Image as CoreImage
from kivy.graphics import Color, Rectangle


class BaseScreen(Screen):
    """Tela base que aplica um fundo padrão repetido com opacidade.

    Desenha primeiro um fundo claro estático e, por cima, aplica o pattern
    repetido (`assets/images/placeholder.png`) com opacidade reduzida.
    """

    pattern_path = "assets/images/placeholder.png"
    pattern_alpha = 0.15

    def on_kv_post(self, base_widget):
        try:
            tex = CoreImage(self.pattern_path).texture
            tex.wrap = 'repeat'
        except Exception:
            tex = None

        with self.canvas.before:
            # fundo claro base (sem transparência)
            Color(240/255.0, 238/255.0, 234/255.0, 1)
            self._base_rect = Rectangle(pos=self.pos, size=self.size)

            # pattern por cima, com alpha definida
            if tex:
                Color(1, 1, 1, self.pattern_alpha)
                self._bg_rect = Rectangle(texture=tex, pos=self.pos, size=self.size)
                self._bg_texture = tex
            else:
                self._bg_rect = None

        self.bind(pos=self._update_bg, size=self._update_bg)

    def _update_bg(self, *args):
        if hasattr(self, '_base_rect'):
            self._base_rect.pos = self.pos
            self._base_rect.size = self.size
        if hasattr(self, '_bg_rect') and self._bg_rect:
            self._bg_rect.pos = self.pos
            self._bg_rect.size = self.size
            if hasattr(self, '_bg_texture') and self._bg_texture:
                w, h = self.size
                tw, th = self._bg_texture.width, self._bg_texture.height
                if tw > 0 and th > 0:
                    self._bg_rect.tex_coords = (0, 0, w / tw, 0, w / tw, h / th, 0, h / th)
