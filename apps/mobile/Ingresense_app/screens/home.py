import os
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock


class HomeScreen(Screen):

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

        caminho = selecao[0]
        if not os.path.exists(caminho):
            return

        # Passa o caminho para a tela de preview
        preview = self.manager.get_screen("preview")
        preview.image_path = caminho
        self.manager.current = "preview"
