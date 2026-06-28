import threading

from .base import BaseScreen
from kivy.app import App
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.clock import Clock

from services.api_service import enviar_imagem

LOADING_TEXTS = [
    "Analisando ingredientes...",
    "Identificando indícios de ultraprocessamento",
]

NOVA_CONFIG = {
    1: {
        "cor": (0.20, 0.70, 0.35, 1),
        "progresso": 0.15,
        "label": "Baixo processamento",
        "descricao": (
            "Alimentos in natura ou minimamente processados. "
            "São a base de uma alimentação saudável: frutas, legumes, "
            "carnes, ovos, leite, grãos e cereais."
        ),
        "dica": "Pode consumir à vontade. Prefira estes alimentos no dia a dia.",
        "dica_icone": "🟢",
    },
    2: {
        "cor": (0.60, 0.80, 0.20, 1),
        "progresso": 0.38,
        "label": "Ingrediente culinário",
        "descricao": (
            "Óleos, gorduras, sal, açúcar e farinhas extraídos de alimentos naturais. "
            "Usados para temperar e cozinhar, mas não são consumidos sozinhos."
        ),
        "dica": "Use com moderação como parte do preparo de refeições.",
        "dica_icone": "🟡",
    },
    3: {
        "cor": (1.00, 0.55, 0.10, 1),
        "progresso": 0.65,
        "label": "Alimento processado",
        "descricao": (
            "Produtos fabricados com adição de sal, açúcar ou outros ingredientes "
            "como conservantes e emulsificantes. Exemplos: queijos, embutidos, "
            "conservas e pães."
        ),
        "dica": "Consuma com moderação e prefira versões com menos aditivos.",
        "dica_icone": "🟡",
    },
    4: {
        "cor": (0.85, 0.15, 0.15, 1),
        "progresso": 1.00,
        "label": "Ultraprocessado",
        "descricao": (
            "Produtos industriais com muitos aditivos como corantes, aromatizantes, "
            "edulcorantes e estabilizantes. São formulados para serem "
            "hiper-palatáveis e têm pouco valor nutricional."
        ),
        "dica": (
            "Evite ou consuma raramente. Estudos associam ao risco de "
            "obesidade, diabetes e doenças cardiovasculares."
        ),
        "dica_icone": "🔴",
    },
}

NUM_DOTS     = 4
DOT_INTERVAL = 0.18  # segundos entre cada ponto acender


class ResultScreen(BaseScreen):

    state           = StringProperty("loading")
    image_path      = StringProperty("")
    loading_text    = StringProperty(LOADING_TEXTS[0])
    dot_index       = NumericProperty(0)
    classificacao   = StringProperty("")
    resumo          = StringProperty("")
    justificativa   = StringProperty("")
    orientacao      = StringProperty("")
    evidencias_texto = StringProperty("")
    aviso           = StringProperty("")
    nova_grupo_texto = StringProperty("")
    nova_descricao  = StringProperty("")
    nova_dica       = StringProperty("")
    nova_dica_icone = StringProperty("")
    erro_titulo     = StringProperty("")
    erro_detalhe    = StringProperty("")
    nova_cor        = ListProperty([0.5, 0.5, 0.5, 1])
    nova_progresso  = NumericProperty(0)

    _dot_event  = None
    _text_event = None
    _text_index = 0
    _error_touch_target = None

    def on_kv_post(self, base_widget):
        super().on_kv_post(base_widget)
        self._bind_buttons()

    def on_enter(self):
        self._cancelar_animacoes()
        self._error_touch_target = None

        self.state           = "loading"
        self.classificacao   = ""
        self.resumo          = ""
        self.justificativa   = ""
        self.orientacao      = ""
        self.evidencias_texto = ""
        self.aviso           = ""
        self.nova_grupo_texto = ""
        self.nova_descricao  = ""
        self.nova_dica       = ""
        self.nova_dica_icone = ""
        self.erro_titulo     = ""
        self.erro_detalhe    = ""
        self.nova_cor        = [0.5, 0.5, 0.5, 1]
        self.nova_progresso  = 0
        self.dot_index       = 0
        self._text_index     = 0
        self.loading_text    = LOADING_TEXTS[0]

        self._dot_event  = Clock.schedule_interval(self._avancar_ponto, DOT_INTERVAL)
        self._text_event = Clock.schedule_interval(self._alternar_texto, 4.0)

        self._bind_buttons()
        Clock.schedule_once(lambda dt: self._atualizar_visibilidade_estado(), 0.05)

        thread = threading.Thread(target=self._analisar, daemon=True)
        thread.start()

    def on_leave(self):
        self._error_touch_target = None
        self._cancelar_animacoes()

    def on_state(self, instance, value):
        self._bind_buttons()
        Clock.schedule_once(lambda dt: self._atualizar_visibilidade_estado(), 0.05)

    def _bind_buttons(self):
        retry_button = self.ids.get("retry_button")
        home_button = self.ids.get("home_button")

        if retry_button is not None and not getattr(retry_button, "_result_bound", False):
            retry_button._result_bound = True

        if home_button is not None and not getattr(home_button, "_result_bound", False):
            home_button._result_bound = True

    def _atualizar_visibilidade_estado(self):
        loading = self.ids.get("loading_container")
        error = self.ids.get("error_container")
        success = self.ids.get("success_container")
        retry = self.ids.get("retry_button")
        home = self.ids.get("home_button")

        def aplicar(container, ativo):
            if container is None:
                return
            container.opacity = 1 if ativo else 0
            container.disabled = not ativo

        aplicar(loading, self.state == "loading")
        aplicar(error, self.state == "error")
        aplicar(success, self.state == "success")

        if retry is not None:
            retry.disabled = self.state != "error"
            retry.opacity = 1 if self.state == "error" else 0
            retry.size_hint_y = None
            retry.height = "52dp" if self.state == "error" else 0
        if home is not None:
            home.disabled = self.state != "error"
            home.opacity = 1 if self.state == "error" else 0
            home.size_hint_y = None
            home.height = "40dp" if self.state == "error" else 0

    # ── animações ─────────────────────────────────────────────────────────────

    def _avancar_ponto(self, dt):
        self.dot_index = (self.dot_index + 1) % NUM_DOTS

    def _alternar_texto(self, dt):
        self._text_index  = (self._text_index + 1) % len(LOADING_TEXTS)
        self.loading_text = LOADING_TEXTS[self._text_index]

    def _cancelar_animacoes(self):
        if self._dot_event:
            self._dot_event.cancel()
            self._dot_event = None
        if self._text_event:
            self._text_event.cancel()
            self._text_event = None

    # ── análise ───────────────────────────────────────────────────────────────

    def _analisar(self):
        resultado = enviar_imagem(self.image_path)
        Clock.schedule_once(lambda dt: self._exibir_resultado(resultado))

    def _exibir_resultado(self, resultado):
        self._cancelar_animacoes()

        if "erro" in resultado:
            self.erro_titulo  = resultado.get("erro", "Algo deu errado.")
            self.erro_detalhe = resultado.get("detalhe", "Tente novamente.")
            self.state = "error"
            Clock.schedule_once(lambda dt: self._atualizar_visibilidade_estado(), 0.05)
            return

        try:
            grupo = int(resultado.get("nova_grupo", 4))
        except (TypeError, ValueError):
            grupo = 4

        config = NOVA_CONFIG.get(grupo, NOVA_CONFIG[4])

        self.nova_cor        = list(config["cor"])
        self.nova_progresso  = config["progresso"]
        self.nova_grupo_texto = f"NOVA\n{grupo}"
        self.classificacao   = resultado.get("titulo") or resultado.get(
            "classificacao",
            config["label"],
        )
        self.resumo          = resultado.get("resumo", "")
        self.justificativa   = resultado.get("justificativa", "")
        self.orientacao      = resultado.get("orientacao", "")
        self.evidencias_texto = self._formatar_evidencias(
            resultado.get("evidencias", [])
        )
        self.aviso           = resultado.get("aviso", "")
        self.nova_descricao  = self.resumo or config["descricao"]
        self.nova_dica       = self.orientacao or config["dica"]
        self.nova_dica_icone = config["dica_icone"]

        self.state = "success"
        Clock.schedule_once(lambda dt: self._atualizar_visibilidade_estado(), 0.05)

    def _formatar_evidencias(self, evidencias):
        linhas = []
        for evidencia in evidencias or []:
            termo = evidencia.get("termo", "")
            descricao = evidencia.get("descricao", "")
            if termo and descricao:
                linhas.append(f"{termo}: {descricao}")
            elif termo:
                linhas.append(termo)

        return "\n".join(linhas)

    def tentar_novamente(self, *args):
        """Reinicia a análise com a mesma imagem sem sair da tela."""
        self._cancelar_animacoes()
        Clock.schedule_once(lambda dt: self.on_enter(), 0)

    def voltar(self, *args):
        if self.manager is not None:
            self.manager.current = "home"
            return

        app = App.get_running_app()
        if app and getattr(app, "root", None) is not None:
            app.root.current = "home"

    def on_touch_down(self, touch):
        if self.state == "error":
            retry = self.ids.get("retry_button")
            home = self.ids.get("home_button")

            for button in (retry, home):
                if (
                    button is not None
                    and not button.disabled
                    and button.opacity > 0
                    and button.collide_point(*touch.pos)
                ):
                    self._error_touch_target = button
                    return button.on_touch_down(touch)

        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self._error_touch_target is not None:
            button = self._error_touch_target
            self._error_touch_target = None

            if button is not None:
                return button.on_touch_up(touch)

        return super().on_touch_up(touch)

