import os
import time

from kivy.clock import Clock
from kivy.properties import BooleanProperty, StringProperty
from kivy.utils import platform

from .base import BaseScreen
from utils.image_files import get_image_cache_dir, prepare_image_for_app


class CameraScreen(BaseScreen):
    camera_active = BooleanProperty(False)
    status_text = StringProperty("Abrindo camera...")

    def on_enter(self):
        """Ativa a camera interna do app ao entrar na tela."""
        self.status_text = "Abrindo camera..."
        self.camera_active = False

        if platform == "android":
            self._solicitar_permissao_camera()
            return

        self._ativar_camera()

    def on_leave(self):
        self.camera_active = False

    def _solicitar_permissao_camera(self):
        try:
            from android.permissions import Permission, check_permission, request_permissions

            if check_permission(Permission.CAMERA):
                self._ativar_camera()
                return

            request_permissions([Permission.CAMERA], self._on_permissao_camera)
        except Exception as e:
            print(f"[CameraScreen] Erro ao solicitar permissao da camera: {e}")
            self._voltar_para_home()

    def _on_permissao_camera(self, permissions, grants):
        if permissions and grants and all(grants):
            Clock.schedule_once(lambda dt: self._ativar_camera(), 0)
            return

        print("[CameraScreen] Permissao da camera negada.")
        Clock.schedule_once(lambda dt: self._voltar_para_home(), 0)

    def _ativar_camera(self):
        self.status_text = "Posicione o rotulo"
        self.camera_active = True

    def capturar_foto(self):
        camera_widget = self.ids.get("camera_preview")
        if not camera_widget:
            print("[CameraScreen] Widget de camera nao encontrado.")
            self._voltar_para_home()
            return

        try:
            output_path = os.path.join(
                get_image_cache_dir(),
                f"captured_label_{int(time.time() * 1000)}.png",
            )

            if not camera_widget.texture:
                self.status_text = "Aguarde a camera carregar..."
                return

            camera_widget.texture.save(output_path, flipped=False)

            preview_path = prepare_image_for_app(output_path)
            self._abrir_preview(preview_path)
        except Exception as e:
            print(f"[CameraScreen] Erro ao capturar foto: {e}")
            self.status_text = "Nao foi possivel capturar. Tente novamente."

    def cancelar(self):
        self._voltar_para_home()

    def _abrir_preview(self, caminho):
        self.camera_active = False
        preview = self.manager.get_screen("preview")
        preview.image_path = caminho
        self.manager.current = "preview"

    def _voltar_para_home(self):
        self.camera_active = False
        self.manager.current = "home"
