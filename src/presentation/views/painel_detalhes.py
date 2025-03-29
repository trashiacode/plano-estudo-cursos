import tkinter as tk
from tkinter import ttk
from typing import Callable

from src.domain.entities import Aula

class PainelDetalhes(ttk.Frame):
    """Componente para exibir detalhes de uma aula selecionada"""
    
    def __init__(self, master=None, **kwargs):
        """Inicializa o painel de detalhes"""
        # Extrair callbacks antes de inicializar o Frame
        self.on_salvar_anotacoes = kwargs.pop('on_salvar_anotacoes', None)
        self.on_marcar_aula = kwargs.pop('on_marcar_aula', None)
        self.on_abrir_video = kwargs.pop('on_abrir_video', None)
        
        # Inicializar o Frame com os parâmetros restantes
        super().__init__(master, **kwargs)
        
        # Variáveis para armazenar o estado atual
        self.aula_atual = None
        
        # Construir interface
        self._construir_interface()
    
    def _construir_interface(self):
        """Constrói a interface do painel de detalhes"""
        # Frame principal de informações
        self.frame_info = ttk.LabelFrame(self, text="Detalhes da Aula")
        self.frame_info.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
        
        # Título da aula
        self.frame_titulo = ttk.Frame(self.frame_info)
        self.frame_titulo.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(self.frame_titulo, text="Título:").pack(side=tk.LEFT)
        
        self.lbl_titulo = ttk.Label(self.frame_titulo, text="", font=("Arial", 10, "bold"))
        self.lbl_titulo.pack(side=tk.LEFT, padx=(5, 0))
        
        # Status da aula
        self.frame_status = ttk.Frame(self.frame_info)
        self.frame_status.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(self.frame_status, text="Status:").pack(side=tk.LEFT)
        
        self.lbl_status = ttk.Label(self.frame_status, text="")
        self.lbl_status.pack(side=tk.LEFT, padx=(5, 0))
        
        # Duração do vídeo
        self.frame_duracao = ttk.Frame(self.frame_info)
        self.frame_duracao.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(self.frame_duracao, text="Duração:").pack(side=tk.LEFT)
        
        self.lbl_duracao = ttk.Label(self.frame_duracao, text="")
        self.lbl_duracao.pack(side=tk.LEFT, padx=(5, 0))
        
        # Caminho do vídeo
        self.frame_caminho = ttk.Frame(self.frame_info)
        self.frame_caminho.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(self.frame_caminho, text="Arquivo:").pack(side=tk.LEFT)
        
        self.lbl_caminho = ttk.Label(self.frame_caminho, text="")
        self.lbl_caminho.pack(side=tk.LEFT, padx=(5, 0))
        
        # Separador
        ttk.Separator(self.frame_info, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=10)
        
        # Anotações
        self.frame_anotacoes = ttk.Frame(self.frame_info)
        self.frame_anotacoes.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        ttk.Label(self.frame_anotacoes, text="Anotações:").pack(anchor=tk.W)
        
        # Frame para o texto e scrollbar
        self.frame_texto = ttk.Frame(self.frame_anotacoes)
        self.frame_texto.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self.frame_texto)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Campo de texto para anotações
        self.txt_anotacoes = tk.Text(
            self.frame_texto,
            wrap=tk.WORD,
            height=10,
            yscrollcommand=self.scrollbar.set
        )
        self.txt_anotacoes.pack(fill=tk.BOTH, expand=True)
        
        # Vincular scrollbar ao texto
        self.scrollbar.config(command=self.txt_anotacoes.yview)
        
        # Frame para botões
        self.frame_botoes = ttk.Frame(self)
        self.frame_botoes.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Botão de salvar anotações
        self.btn_salvar = ttk.Button(
            self.frame_botoes,
            text="Salvar Anotações",
            command=self._salvar_anotacoes
        )
        self.btn_salvar.pack(side=tk.LEFT, padx=(0, 5))
        
        # Botão de marcar como concluída
        self.btn_marcar = ttk.Button(
            self.frame_botoes,
            text="Marcar como Concluída",
            command=self._marcar_aula
        )
        self.btn_marcar.pack(side=tk.LEFT, padx=5)
        
        # Botão para abrir vídeo
        self.btn_abrir_video = ttk.Button(
            self.frame_botoes,
            text="Abrir Vídeo",
            command=self._abrir_video
        )
        self.btn_abrir_video.pack(side=tk.LEFT, padx=5)
        
        # Desabilitar componentes inicialmente
        self.desabilitar()
    
    def exibir_aula(self, aula: Aula):
        """Exibe os detalhes de uma aula"""
        if not aula:
            self.desabilitar()
            return
        
        # Armazenar aula atual
        self.aula_atual = aula
        
        # Atualizar informações
        self.lbl_titulo.config(text=aula.titulo_formatado)
        self.lbl_status.config(
            text="Concluída" if aula.concluida else "Pendente",
            foreground="green" if aula.concluida else "gray"
        )
        self.lbl_duracao.config(text=aula.duracao)
        self.lbl_caminho.config(text=aula.caminho_video)
        
        # Atualizar anotações
        self.txt_anotacoes.delete("1.0", tk.END)
        if hasattr(aula, 'anotacoes') and aula.anotacoes:
            self.txt_anotacoes.insert("1.0", aula.anotacoes)
        
        # Atualizar texto do botão de marcar
        if aula.concluida:
            self.btn_marcar.config(text="Marcar como Pendente")
        else:
            self.btn_marcar.config(text="Marcar como Concluída")
        
        # Habilitar componentes
        self.habilitar()
    
    def habilitar(self):
        """Habilita os componentes do painel"""
        self.txt_anotacoes.config(state=tk.NORMAL)
        self.btn_salvar.config(state=tk.NORMAL)
        self.btn_marcar.config(state=tk.NORMAL)
        self.btn_abrir_video.config(state=tk.NORMAL)
    
    def desabilitar(self):
        """Desabilita os componentes do painel"""
        # Limpar informações
        self.lbl_titulo.config(text="")
        self.lbl_status.config(text="")
        self.lbl_duracao.config(text="")
        self.lbl_caminho.config(text="")
        
        # Limpar e desabilitar campo de anotações
        self.txt_anotacoes.delete("1.0", tk.END)
        self.txt_anotacoes.config(state=tk.DISABLED)
        
        # Desabilitar botões
        self.btn_salvar.config(state=tk.DISABLED)
        self.btn_marcar.config(state=tk.DISABLED)
        self.btn_abrir_video.config(state=tk.DISABLED)
        
        # Limpar aula atual
        self.aula_atual = None
    
    def _salvar_anotacoes(self):
        """Salva as anotações da aula atual"""
        if not self.aula_atual:
            return
        
        # Obter texto das anotações
        anotacoes = self.txt_anotacoes.get("1.0", tk.END).strip()
        
        # Chamar callback para salvar anotações
        if self.on_salvar_anotacoes:
            self.on_salvar_anotacoes(anotacoes, self.aula_atual)
    
    def _marcar_aula(self):
        """Marca ou desmarca a aula atual como concluída"""
        if not self.aula_atual:
            return
        
        # Inverter estado atual
        concluida = not self.aula_atual.concluida
        
        # Chamar callback para marcar aula
        if self.on_marcar_aula:
            self.on_marcar_aula(self.aula_atual, concluida)
            
            # Atualizar componentes
            self.exibir_aula(self.aula_atual)
    
    def _abrir_video(self):
        """Abre o vídeo da aula atual"""
        if not self.aula_atual:
            return
        
        # Chamar callback para abrir vídeo
        if self.on_abrir_video:
            self.on_abrir_video(self.aula_atual) 