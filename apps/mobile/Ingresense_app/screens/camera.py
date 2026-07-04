import os

from plyer import camera

from .base import BaseScreen
from utils.image_files import get_capture_path, prepare_image_for_app


class CameraScreen(BaseScreen):

    def on_enter(self):
        """Abre a camera nativa assim que entra na tela."""
        self.abrir_camera()

    def abrir_camera(self):
        """Chama a camera nativa do dispositivo via plyer."""
        try:
            capture_path = get_capture_path()
            os.makedirs(os.path.dirname(capture_path), exist_ok=True)
            camera.take_picture(
                filename=capture_path,
                on_complete=self.on_foto_capturada,
            )
        except Exception as e:
            print(f"[CameraScreen] Erro ao abrir camera: {e}")
            self.manager.current = "home"

    def on_foto_capturada(self, caminho):
        """Callback chamado apos o usuario tirar a foto."""
        if caminho and os.path.exists(caminho):
            try:
                preview_path = prepare_image_for_app(caminho)
                preview = self.manager.get_screen("preview")
                preview.image_path = preview_path
                self.manager.current = "preview"
            except Exception as e:
                print(f"[CameraScreen] Erro ao preparar foto capturada: {e}")
                self.manager.current = "home"
        else:
            self.manager.current = "home"
