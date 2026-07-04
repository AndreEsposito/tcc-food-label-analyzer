from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.properties import ObjectProperty, StringProperty

from .base import BaseScreen


class PreviewScreen(BaseScreen):

    image_path = StringProperty("")
    _preview_texture = ObjectProperty(None, allownone=True)

    def on_kv_post(self, base_widget):
        super().on_kv_post(base_widget)
        self._schedule_preview_update(self.image_path)

    def on_image_path(self, instance, value):
        """Atualiza a imagem quando image_path muda."""
        self._schedule_preview_update(value)

    def _schedule_preview_update(self, value):
        Clock.schedule_once(lambda dt: self._update_preview_texture(value), 0)

    def _update_preview_texture(self, value):
        preview_img = self.ids.get("preview_image")
        if not preview_img:
            return

        if not value:
            self._preview_texture = None
            preview_img.texture = None
            preview_img.source = "assets/images/placeholder.png"
            preview_img.reload()
            return

        try:
            from PIL import Image, ImageOps

            with Image.open(value) as image:
                image = ImageOps.exif_transpose(image).convert("RGBA")
                image.thumbnail((1800, 1800))
                width, height = image.size
                texture = Texture.create(size=(width, height), colorfmt="rgba")
                texture.blit_buffer(
                    image.tobytes(),
                    colorfmt="rgba",
                    bufferfmt="ubyte",
                )
                texture.flip_vertical()

            self._preview_texture = texture
            preview_img.source = ""
            preview_img.texture = texture
            preview_img.canvas.ask_update()
            print(f"[PreviewScreen] Preview carregado como textura: {value}")
        except Exception as e:
            print(f"[PreviewScreen] Erro ao renderizar textura do preview: {e}")
            preview_img.source = value
            preview_img.reload()

    def enviar_para_analise(self):
        """Vai para a tela de loading e dispara a analise."""
        if not self.image_path:
            return

        result_screen = self.manager.get_screen("result")
        result_screen.image_path = self.image_path
        self.manager.current = "result"
        Clock.schedule_once(lambda dt: result_screen.on_enter(), 0.05)
