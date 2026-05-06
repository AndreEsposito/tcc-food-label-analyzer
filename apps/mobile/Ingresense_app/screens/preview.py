from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty


class PreviewScreen(Screen):

    image_path = StringProperty("")

    def on_image_path(self, instance, value):
        """Atualiza a imagem quando image_path muda."""
        preview_img = self.ids.get("preview_image")
        if preview_img and value:
            preview_img.source = value
            preview_img.reload()

    def enviar_para_analise(self):
        """Vai para a tela de loading e dispara a análise."""
        if not self.image_path:
            return

        # Passa o caminho para a tela de resultado e inicia análise
        result_screen = self.manager.get_screen("result")
        result_screen.image_path = self.image_path

        self.manager.current = "result"
