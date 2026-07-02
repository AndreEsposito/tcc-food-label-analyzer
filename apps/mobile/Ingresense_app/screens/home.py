import os
from urllib.parse import urlparse, unquote

from .base import BaseScreen
from kivy.app import App
from kivy.utils import platform


class HomeScreen(BaseScreen):

    def abrir_galeria(self):
        """Abre o seletor de arquivos nativo via plyer."""
        try:
            from plyer import filechooser
            filechooser.open_file(
                title="Selecionar imagem do rótulo",
                filters=[["Imagens", "*.png", "*.jpg", "*.jpeg"]],
                on_selection=self.on_imagem_selecionada
            )
        except Exception as e:
            print(f"[HomeScreen] Erro ao abrir galeria: {e}")

    def on_imagem_selecionada(self, selecao):
        """Callback chamado após o usuário selecionar uma imagem."""
        if not selecao:
            return  # Usuário cancelou

        try:
            caminho = self._resolver_caminho_imagem(selecao[0])
        except Exception as e:
            print(f"[HomeScreen] Erro ao preparar imagem selecionada: {e}")
            return
        if not caminho or not os.path.exists(caminho):
            print(f"[HomeScreen] Imagem selecionada inacessível: {selecao[0]}")
            return

        # Passa o caminho para a tela de preview
        preview = self.manager.get_screen("preview")
        preview.image_path = caminho
        self.manager.current = "preview"

    def _resolver_caminho_imagem(self, caminho):
        """Converte URIs Android em arquivos locais legíveis pelo Kivy."""
        print(f"[HomeScreen] Imagem recebida: {caminho}")

        if not caminho:
            return ""

        if caminho.startswith("file://"):
            caminho_local = unquote(urlparse(caminho).path)
            print(
                "[HomeScreen] URI file convertida: "
                f"{caminho_local} | existe={os.path.exists(caminho_local)}"
            )
            return caminho_local

        if caminho.startswith("content://"):
            if platform != "android":
                print("[HomeScreen] URI content recebida fora do Android")
                return ""

            caminho_local = self._copiar_content_uri_para_cache(caminho)
            print(
                "[HomeScreen] URI content copiada para cache: "
                f"{caminho_local} | existe={os.path.exists(caminho_local)}"
            )
            return caminho_local

        print(f"[HomeScreen] Caminho local existe={os.path.exists(caminho)}")
        return caminho

    def _copiar_content_uri_para_cache(self, uri):
        """Copia uma URI content:// para o diretório privado do app no Android."""
        from jnius import autoclass, jarray

        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        Uri = autoclass("android.net.Uri")

        context = PythonActivity.mActivity
        resolver = context.getContentResolver()
        input_stream = resolver.openInputStream(Uri.parse(uri))

        if input_stream is None:
            raise ValueError(f"Não foi possível abrir a URI selecionada: {uri}")

        cache_dir = os.path.join(App.get_running_app().user_data_dir, "selected_images")
        os.makedirs(cache_dir, exist_ok=True)
        mime_type = resolver.getType(Uri.parse(uri))
        extensao = ".png" if mime_type == "image/png" else ".jpg"
        destino = os.path.join(cache_dir, f"selected_label_image{extensao}")
        print(f"[HomeScreen] MIME da imagem selecionada: {mime_type}")

        try:
            with open(destino, "wb") as arquivo:
                buffer = jarray("b")([0] * 8192)
                while True:
                    bytes_lidos = input_stream.read(buffer)
                    if bytes_lidos == -1:
                        break
                    arquivo.write(bytes((byte & 0xFF for byte in buffer[:bytes_lidos])))
        finally:
            input_stream.close()

        return destino
