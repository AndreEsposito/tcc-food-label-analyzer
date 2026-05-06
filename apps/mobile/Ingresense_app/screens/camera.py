import os
from kivy.uix.screenmanager import Screen
from plyer import camera


CAPTURE_PATH = os.path.join("assets", "images", "captured.png")


class CameraScreen(Screen):

    def on_enter(self):
        """Abre a câmera nativa assim que entra na tela."""
        os.makedirs(os.path.dirname(CAPTURE_PATH), exist_ok=True)
        self.abrir_camera()

    def abrir_camera(self):
        """Chama a câmera nativa do dispositivo via plyer."""
        try:
            camera.take_picture(
                filename=CAPTURE_PATH,
                on_complete=self.on_foto_capturada
            )
        except Exception as e:
            print(f"[CameraScreen] Erro ao abrir câmera: {e}")
            self.manager.current = "home"

    def on_foto_capturada(self, caminho):
        """Callback chamado após o usuário tirar a foto."""
        if caminho and os.path.exists(caminho):
            preview = self.manager.get_screen("preview")
            preview.image_path = caminho
            self.manager.current = "preview"
        else:
            # Usuário cancelou ou erro — volta para home
            self.manager.current = "home"
