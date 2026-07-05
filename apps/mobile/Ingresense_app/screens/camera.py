import os
import time

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
            self._capture_in_progress = False
            self.manager.current = "home"

    def _abrir_camera_android_com_permissao(self):
        try:
            from android.permissions import Permission, check_permission, request_permissions

            if check_permission(Permission.CAMERA):
                self._abrir_camera_android()
                return

            request_permissions(
                [Permission.CAMERA],
                self._on_permissao_camera,
            )
        except Exception as e:
            print(f"[CameraScreen] Erro ao solicitar permissao da camera: {e}")
            self._capture_in_progress = False
            self.manager.current = "home"

    def _on_permissao_camera(self, permissions, grants):
        if permissions and grants and all(grants):
            Clock.schedule_once(lambda dt: self._abrir_camera_android(), 0)
            return

        print("[CameraScreen] Permissao da camera negada.")
        self._capture_in_progress = False
        Clock.schedule_once(lambda dt: setattr(self.manager, "current", "home"), 0)

    def _abrir_camera_android(self):
        try:
            import android.activity
            from jnius import autoclass, cast

            Intent = autoclass("android.content.Intent")
            ClipData = autoclass("android.content.ClipData")
            MediaStore = autoclass("android.provider.MediaStore")
            ContentValues = autoclass("android.content.ContentValues")
            Environment = autoclass("android.os.Environment")
            Build = autoclass("android.os.Build")
            PythonActivity = autoclass("org.kivy.android.PythonActivity")

            activity = PythonActivity.mActivity
            resolver = activity.getContentResolver()

            values = ContentValues()
            values.put(
                MediaStore.Images.Media.DISPLAY_NAME,
                f"ingresense_rotulo_{int(time.time() * 1000)}.jpg",
            )
            values.put(MediaStore.Images.Media.MIME_TYPE, "image/jpeg")

            if Build.VERSION.SDK_INT >= 29:
                values.put(
                    MediaStore.Images.Media.RELATIVE_PATH,
                    str(Environment.DIRECTORY_PICTURES) + "/IngreSense",
                )

            uri = resolver.insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, values)
            if uri is None:
                raise RuntimeError("Android nao retornou URI para salvar a captura.")

            self._pending_capture_uri = uri
            self._pending_capture_uri_text = str(uri.toString())

            intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
            parcelable_uri = cast("android.os.Parcelable", uri)
            intent.putExtra(MediaStore.EXTRA_OUTPUT, parcelable_uri)
            intent.setClipData(ClipData.newUri(resolver, "rotulo", uri))
            uri_permission_flags = (
                Intent.FLAG_GRANT_WRITE_URI_PERMISSION
                | Intent.FLAG_GRANT_READ_URI_PERMISSION
            )
            intent.addFlags(uri_permission_flags)
            self._grant_uri_to_camera_apps(intent, uri, uri_permission_flags)

            if intent.resolveActivity(activity.getPackageManager()) is None:
                raise RuntimeError("Nenhum app de camera disponivel para atender a captura.")

            android.activity.unbind(on_activity_result=self._on_android_activity_result)
            android.activity.bind(on_activity_result=self._on_android_activity_result)
            activity.startActivityForResult(intent, self.REQUEST_CAMERA_CAPTURE)
        except Exception as e:
            print(f"[CameraScreen] Erro ao abrir camera Android: {e}")
            self._capture_in_progress = False
            self._limpar_captura_android_pendente()
            self.manager.current = "home"

    def _on_android_activity_result(self, request_code, result_code, intent):
        if request_code != self.REQUEST_CAMERA_CAPTURE:
            return

        try:
            import android.activity
            from jnius import autoclass

            android.activity.unbind(on_activity_result=self._on_android_activity_result)
            Activity = autoclass("android.app.Activity")

            if result_code != Activity.RESULT_OK:
                self._limpar_captura_android_pendente()
                Clock.schedule_once(lambda dt: self._voltar_para_home(), 0)
                return

            self._finalizar_captura_android()
        except Exception as e:
            print(f"[CameraScreen] Erro ao processar retorno da camera Android: {e}")
            self._limpar_captura_android_pendente()
            Clock.schedule_once(lambda dt: self._voltar_para_home(), 0)

    def _finalizar_captura_android(self):
        try:
            preview_path = prepare_image_for_app(self._pending_capture_uri_text)
            self._liberar_uri_android_pendente()
            Clock.schedule_once(lambda dt: self._abrir_preview(preview_path), 0)
        except Exception as e:
            print(f"[CameraScreen] Erro ao preparar foto capturada no Android: {e}")
            self._limpar_captura_android_pendente()
            Clock.schedule_once(lambda dt: self._voltar_para_home(), 0)

    def _limpar_captura_android_pendente(self):
        uri = getattr(self, "_pending_capture_uri", None)
        if uri is not None:
            try:
                from jnius import autoclass

                Intent = autoclass("android.content.Intent")
                PythonActivity = autoclass("org.kivy.android.PythonActivity")
                activity = PythonActivity.mActivity
                activity.revokeUriPermission(
                    uri,
                    Intent.FLAG_GRANT_WRITE_URI_PERMISSION
                    | Intent.FLAG_GRANT_READ_URI_PERMISSION,
                )
                activity.getContentResolver().delete(uri, None, None)
            except Exception as e:
                print(f"[CameraScreen] Erro ao remover captura temporaria: {e}")

        self._pending_capture_uri = None
        self._pending_capture_uri_text = ""
        self._capture_in_progress = False

    def _liberar_uri_android_pendente(self):
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

        self._pending_capture_uri = None
        self._pending_capture_uri_text = ""
        self._capture_in_progress = False

    def _abrir_preview(self, caminho):
        self._capture_in_progress = False
        preview = self.manager.get_screen("preview")
        preview.image_path = caminho
        self.manager.current = "preview"

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

    def _voltar_para_home(self):
        self._capture_in_progress = False
        self.manager.current = "home"

    def on_foto_capturada(self, caminho):
        """Callback chamado apos o usuario tirar a foto."""
        if caminho and os.path.exists(caminho):
            try:
                preview_path = prepare_image_for_app(caminho)
                self._abrir_preview(preview_path)
            except Exception as e:
                print(f"[CameraScreen] Erro ao preparar foto capturada: {e}")
                self._voltar_para_home()
        else:
            self._voltar_para_home()
