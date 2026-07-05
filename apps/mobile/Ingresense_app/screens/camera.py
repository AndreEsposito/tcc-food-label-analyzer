import os

from kivy.clock import Clock
from kivy.utils import platform

from .base import BaseScreen
from utils.image_files import get_capture_path, prepare_image_for_app


class CameraScreen(BaseScreen):
    REQUEST_CAMERA_CAPTURE = 0x5343

    def on_enter(self):
        """Abre a camera nativa assim que entra na tela."""
        self.abrir_camera()

    def abrir_camera(self):
        """Chama a camera nativa do dispositivo."""
        if getattr(self, "_capture_in_progress", False):
            return

        self._capture_in_progress = True

        if platform == "android":
            self._abrir_camera_android_com_permissao()
            return

        self._abrir_camera_plyer()

    def _abrir_camera_plyer(self):
        try:
            from plyer import camera

            capture_path = get_capture_path()
            os.makedirs(os.path.dirname(capture_path), exist_ok=True)
            camera.take_picture(
                filename=capture_path,
                on_complete=self.on_foto_capturada,
            )
        except Exception as e:
            print(f"[CameraScreen] Erro ao abrir camera: {e}")
            self._voltar_para_home()

    def _abrir_camera_android_com_permissao(self):
        try:
            from android.permissions import Permission, check_permission, request_permissions

            if check_permission(Permission.CAMERA):
                self._abrir_camera_android()
                return

            request_permissions([Permission.CAMERA], self._on_permissao_camera)
        except Exception as e:
            print(f"[CameraScreen] Erro ao solicitar permissao da camera: {e}")
            self._voltar_para_home()

    def _on_permissao_camera(self, permissions, grants):
        if permissions and grants and all(grants):
            Clock.schedule_once(lambda dt: self._abrir_camera_android(), 0)
            return

        print("[CameraScreen] Permissao da camera negada.")
        Clock.schedule_once(lambda dt: self._voltar_para_home(), 0)

    def _abrir_camera_android(self):
        try:
            import android.activity
            from jnius import autoclass, cast

            Intent = autoclass("android.content.Intent")
            ClipData = autoclass("android.content.ClipData")
            MediaStore = autoclass("android.provider.MediaStore")
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            CaptureProvider = autoclass("br.com.ingresense.IngreSenseFileProvider")

            activity = PythonActivity.mActivity
            resolver = activity.getContentResolver()
            capture_file = CaptureProvider.getCaptureFile(activity)
            capture_uri = CaptureProvider.getUriForCapture(activity)

            self._pending_capture_path = str(capture_file.getAbsolutePath())
            self._pending_capture_uri = capture_uri

            intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
            parcelable_uri = cast("android.os.Parcelable", capture_uri)
            intent.putExtra(MediaStore.EXTRA_OUTPUT, parcelable_uri)
            intent.setClipData(ClipData.newUri(resolver, "rotulo", capture_uri))

            uri_permission_flags = (
                Intent.FLAG_GRANT_WRITE_URI_PERMISSION
                | Intent.FLAG_GRANT_READ_URI_PERMISSION
            )
            intent.addFlags(uri_permission_flags)
            self._grant_uri_to_camera_apps(intent, capture_uri, uri_permission_flags)

            android.activity.unbind(on_activity_result=self._on_android_activity_result)
            android.activity.bind(on_activity_result=self._on_android_activity_result)
            activity.startActivityForResult(intent, self.REQUEST_CAMERA_CAPTURE)
        except Exception as e:
            print(f"[CameraScreen] Erro ao abrir camera Android: {e}")
            self._limpar_captura_android_pendente(remove_file=True)
            self._voltar_para_home()

    def _on_android_activity_result(self, request_code, result_code, intent):
        if request_code != self.REQUEST_CAMERA_CAPTURE:
            return

        try:
            import android.activity
            from jnius import autoclass

            android.activity.unbind(on_activity_result=self._on_android_activity_result)
            Activity = autoclass("android.app.Activity")

            if result_code != Activity.RESULT_OK:
                print(f"[CameraScreen] Captura cancelada pela camera: {result_code}")
                self._limpar_captura_android_pendente(remove_file=True)
                Clock.schedule_once(lambda dt: self._voltar_para_home(), 0)
                return

            self._finalizar_captura_android()
        except Exception as e:
            print(f"[CameraScreen] Erro ao processar retorno da camera Android: {e}")
            self._limpar_captura_android_pendente(remove_file=True)
            Clock.schedule_once(lambda dt: self._voltar_para_home(), 0)

    def _finalizar_captura_android(self):
        try:
            capture_path = getattr(self, "_pending_capture_path", "")
            if not capture_path or not os.path.exists(capture_path):
                raise FileNotFoundError(f"Foto capturada nao encontrada: {capture_path}")

            if os.path.getsize(capture_path) <= 0:
                raise ValueError(f"Foto capturada vazia: {capture_path}")

            preview_path = prepare_image_for_app(capture_path)
            self._limpar_captura_android_pendente(remove_file=False)
            Clock.schedule_once(lambda dt: self._abrir_preview(preview_path), 0)
        except Exception as e:
            print(f"[CameraScreen] Erro ao preparar foto capturada no Android: {e}")
            self._limpar_captura_android_pendente(remove_file=True)
            Clock.schedule_once(lambda dt: self._voltar_para_home(), 0)

    def _grant_uri_to_camera_apps(self, intent, uri, flags):
        try:
            from jnius import autoclass

            PackageManager = autoclass("android.content.pm.PackageManager")
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            activity = PythonActivity.mActivity
            camera_apps = activity.getPackageManager().queryIntentActivities(
                intent,
                PackageManager.MATCH_DEFAULT_ONLY,
            )

            for index in range(camera_apps.size()):
                package_name = camera_apps.get(index).activityInfo.packageName
                activity.grantUriPermission(package_name, uri, flags)
        except Exception as e:
            print(f"[CameraScreen] Erro ao conceder permissao da URI: {e}")

    def _limpar_captura_android_pendente(self, remove_file):
        uri = getattr(self, "_pending_capture_uri", None)
        if uri is not None:
            try:
                from jnius import autoclass

                Intent = autoclass("android.content.Intent")
                PythonActivity = autoclass("org.kivy.android.PythonActivity")
                PythonActivity.mActivity.revokeUriPermission(
                    uri,
                    Intent.FLAG_GRANT_WRITE_URI_PERMISSION
                    | Intent.FLAG_GRANT_READ_URI_PERMISSION,
                )
            except Exception as e:
                print(f"[CameraScreen] Erro ao liberar permissao da URI: {e}")

        capture_path = getattr(self, "_pending_capture_path", "")
        if remove_file and capture_path and os.path.exists(capture_path):
            try:
                os.remove(capture_path)
            except OSError as e:
                print(f"[CameraScreen] Erro ao remover captura temporaria: {e}")

        self._pending_capture_uri = None
        self._pending_capture_path = ""
        self._capture_in_progress = False

    def _abrir_preview(self, caminho):
        self._capture_in_progress = False
        preview = self.manager.get_screen("preview")
        preview.image_path = caminho
        self.manager.current = "preview"

    def _voltar_para_home(self):
        self._capture_in_progress = False
        self.manager.current = "home"

    def on_foto_capturada(self, caminho):
        """Callback chamado apos o usuario tirar a foto no fallback desktop."""
        if caminho and os.path.exists(caminho):
            try:
                preview_path = prepare_image_for_app(caminho)
                self._abrir_preview(preview_path)
            except Exception as e:
                print(f"[CameraScreen] Erro ao preparar foto capturada: {e}")
                self._voltar_para_home()
        else:
            self._voltar_para_home()
