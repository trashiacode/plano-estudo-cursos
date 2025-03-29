import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from typing import Dict, Any, Optional

from src.application.services import AppService
from src.domain.entities import Aula
from src.presentation.views import ArvoreAulas, PainelDetalhes
from src.presentation.controllers.telegram_controller import TelegramController

class MainController:
    """Controlador principal da aplicação"""
    
    def __init__(self, root):
        """Inicializa o controlador principal"""
        self.root = root
        self.app_service = AppService()
        
        # Configurar interface
        self._configurar_interface()
        
        # Vincular eventos
        self._vincular_eventos()
    
    def _configurar_interface(self):
        """Configura a interface principal"""
        # Configurar a janela principal
        self.root.title("Plano de Estudo para Cursos")
        self.root.geometry("1200x700")
        self.root.minsize(800, 600)
        
        # Configurar estilo
        self._configurar_estilo()
        
        # Criar menu
        self._criar_menu()
        
        # Criar notebook para abas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Aba Plano de Estudo
        self.frame_plano = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_plano, text="Plano de Estudo")
        
        # Configurar aba de plano de estudo
        self._configurar_aba_plano()
        
        # Aba Telegram
        self.frame_telegram = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_telegram, text="Download Telegram")
        
        # Inicializar controlador do Telegram na aba correspondente
        self.telegram_controller = TelegramController(self.frame_telegram)
        
        # Barra de status
        self.barra_status = ttk.Frame(self.root, relief=tk.SUNKEN, borderwidth=1)
        self.barra_status.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)
        
        self.lbl_status = ttk.Label(self.barra_status, text="Pronto")
        self.lbl_status.pack(side=tk.LEFT, padx=5)
    
    def _configurar_aba_plano(self):
        """Configura a aba de Plano de Estudo"""
        # Criar painel principal
        self.painel_principal = ttk.PanedWindow(self.frame_plano, orient=tk.HORIZONTAL)
        self.painel_principal.pack(fill=tk.BOTH, expand=True)
        
        # Criar painel esquerdo (árvore de aulas)
        self.frame_esquerdo = ttk.Frame(self.painel_principal)
        self.painel_principal.add(self.frame_esquerdo, weight=1)
        
        # Criar painel direito (detalhes e progresso)
        self.frame_direito = ttk.Frame(self.painel_principal)
        self.painel_principal.add(self.frame_direito, weight=1)
        
        # Criar árvore de aulas
        self.arvore_aulas = ArvoreAulas(
            self.frame_esquerdo,
            on_selecionar_aula=self._on_selecionar_aula,
            on_marcar_aula=self._on_marcar_aula,
            on_abrir_video=self._on_abrir_video
        )
        self.arvore_aulas.pack(fill=tk.BOTH, expand=True)
        
        # Criar painel de progresso
        self.frame_progresso = ttk.LabelFrame(self.frame_direito, text="Progresso do Curso")
        self.frame_progresso.pack(fill=tk.X, padx=10, pady=10)
        
        # Informações de progresso
        self.frame_info_progresso = ttk.Frame(self.frame_progresso)
        self.frame_info_progresso.pack(fill=tk.X, padx=10, pady=10)
        
        # Barra de progresso
        self.barra_progresso = ttk.Progressbar(
            self.frame_info_progresso,
            mode="determinate",
            length=400,
            style="Green.Horizontal.TProgressbar"
        )
        self.barra_progresso.pack(fill=tk.X, expand=True)
        
        # Informações adicionais
        self.frame_info_adicionais = ttk.Frame(self.frame_progresso)
        self.frame_info_adicionais.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Tempo restante
        self.frame_tempo = ttk.Frame(self.frame_info_adicionais)
        self.frame_tempo.pack(fill=tk.X, pady=2)
        
        ttk.Label(self.frame_tempo, text="Tempo restante:").pack(side=tk.LEFT)
        self.lbl_tempo_restante = ttk.Label(self.frame_tempo, text="00:00:00")
        self.lbl_tempo_restante.pack(side=tk.LEFT, padx=(5, 0))
        
        # Estimativa de conclusão
        self.frame_estimativa = ttk.Frame(self.frame_info_adicionais)
        self.frame_estimativa.pack(fill=tk.X, pady=2)
        
        ttk.Label(self.frame_estimativa, text="Conclusão estimada:").pack(side=tk.LEFT)
        self.lbl_estimativa = ttk.Label(self.frame_estimativa, text="Indeterminado")
        self.lbl_estimativa.pack(side=tk.LEFT, padx=(5, 0))
        
        # Aulas concluídas
        self.frame_aulas = ttk.Frame(self.frame_info_adicionais)
        self.frame_aulas.pack(fill=tk.X, pady=2)
        
        ttk.Label(self.frame_aulas, text="Aulas concluídas:").pack(side=tk.LEFT)
        self.lbl_aulas = ttk.Label(self.frame_aulas, text="0/0")
        self.lbl_aulas.pack(side=tk.LEFT, padx=(5, 0))
        
        # Painel de detalhes
        self.painel_detalhes = PainelDetalhes(
            self.frame_direito,
            on_salvar_anotacoes=self._on_salvar_anotacoes,
            on_marcar_aula=self._on_marcar_aula,
            on_abrir_video=self._on_abrir_video
        )
        self.painel_detalhes.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
    
    def _configurar_estilo(self):
        """Configura o estilo da interface"""
        estilo = ttk.Style()
        
        # Usar tema claro
        estilo.theme_use("clam")
        
        # Configurar estilo da barra de progresso
        estilo.configure(
            "Green.Horizontal.TProgressbar",
            background="#4CAF50",  # Verde
            troughcolor="#F0F0F0",  # Cinza claro
            bordercolor="#AAAAAA",  # Cinza médio
            lightcolor="#4CAF50",  # Verde
            darkcolor="#388E3C"    # Verde escuro
        )
    
    def _criar_menu(self):
        """Cria o menu principal"""
        # Criar barra de menu
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        # Menu Arquivo
        self.menu_arquivo = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Arquivo", menu=self.menu_arquivo)
        
        self.menu_arquivo.add_command(label="Abrir Curso", command=self._abrir_curso)
        self.menu_arquivo.add_command(label="Cursos Salvos", command=self._abrir_cursos_salvos)
        self.menu_arquivo.add_separator()
        self.menu_arquivo.add_command(label="Exportar Relatório", command=self._exportar_relatorio)
        self.menu_arquivo.add_separator()
        self.menu_arquivo.add_command(label="Sair", command=self._sair)
        
        # Menu Curso
        self.menu_curso = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Curso", menu=self.menu_curso)
        
        self.menu_curso.add_command(
            label="Marcar Todas as Aulas",
            command=lambda: self._marcar_todas_aulas(True)
        )
        self.menu_curso.add_command(
            label="Desmarcar Todas as Aulas",
            command=lambda: self._marcar_todas_aulas(False)
        )
        
        # Menu Telegram
        self.menu_telegram = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Telegram", menu=self.menu_telegram)
        
        self.menu_telegram.add_command(
            label="Configurar API",
            command=lambda: self.notebook.select(self.frame_telegram)
        )
        self.menu_telegram.add_command(
            label="Baixar Vídeos",
            command=lambda: self.notebook.select(self.frame_telegram)
        )
        
        # Menu Ajuda
        self.menu_ajuda = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Ajuda", menu=self.menu_ajuda)
        
        self.menu_ajuda.add_command(label="Sobre", command=self._exibir_sobre)
    
    def _vincular_eventos(self):
        """Vincula eventos da interface"""
        # Vincular evento de fechar janela
        self.root.protocol("WM_DELETE_WINDOW", self._sair)
    
    def _abrir_curso(self):
        """Abre um curso a partir de um diretório"""
        # Solicitar diretório
        diretorio = filedialog.askdirectory(
            title="Selecione o diretório do curso",
            initialdir=os.path.expanduser("~")
        )
        
        if not diretorio:
            return
        
        # Atualizar barra de status
        self.lbl_status.config(text=f"Carregando curso de {diretorio}...")
        self.root.update_idletasks()
        
        # Carregar curso
        curso = self.app_service.carregar_curso(diretorio)
        
        if not curso:
            messagebox.showerror(
                "Erro ao Carregar Curso",
                "Não foi possível carregar o curso selecionado."
            )
            self.lbl_status.config(text="Pronto")
            return
        
        # Atualizar interface
        self.arvore_aulas.carregar_curso(curso)
        
        # Atualizar informações de progresso
        self._atualizar_informacoes_progresso()
        
        # Atualizar barra de status
        self.lbl_status.config(text=f"Curso carregado: {curso.nome}")
    
    def _atualizar_informacoes_progresso(self):
        """Atualiza as informações de progresso"""
        if not self.app_service.curso_atual:
            return
        
        # Atualizar barra de progresso
        progresso = self.app_service.obter_progresso_curso()
        self.barra_progresso["value"] = progresso
        
        # Atualizar tempo restante
        tempo_restante = self.app_service.obter_tempo_restante()
        self.lbl_tempo_restante.config(text=tempo_restante)
        
        # Atualizar estimativa de conclusão
        estimativa = self.app_service.obter_estimativa_conclusao()
        self.lbl_estimativa.config(text=estimativa)
        
        # Atualizar aulas concluídas
        if hasattr(self.app_service.curso_atual, 'aulas_concluidas') and hasattr(self.app_service.curso_atual, 'total_aulas'):
            self.lbl_aulas.config(
                text=f"{self.app_service.curso_atual.aulas_concluidas}/{self.app_service.curso_atual.total_aulas}"
            )
    
    def _exportar_relatorio(self):
        """Exporta um relatório do curso atual"""
        if not self.app_service.curso_atual:
            messagebox.showinfo(
                "Exportar Relatório",
                "Nenhum curso selecionado para exportar."
            )
            return
        
        # Solicitar arquivo de destino com opções de formato
        arquivo = filedialog.asksaveasfilename(
            title="Salvar Relatório",
            initialdir=os.path.expanduser("~"),
            defaultextension=".txt",
            filetypes=[
                ("Arquivo de Texto", "*.txt"), 
                ("Arquivo CSV", "*.csv"),
                ("Todos os Arquivos", "*.*")
            ]
        )
        
        if not arquivo:
            return
        
        # Atualizar barra de status
        self.lbl_status.config(text="Exportando relatório...")
        self.root.update_idletasks()
        
        # Verificar formato com base na extensão
        ext = os.path.splitext(arquivo)[1].lower()
        
        # Exportar no formato apropriado
        if ext == '.csv':
            resultado = self.app_service.exportar_dados_curso_csv(
                arquivo,
                lambda progresso: self.lbl_status.config(text=f"Exportando... {progresso}%")
            )
        else:
            resultado = self.app_service.exportar_dados_curso(
                arquivo,
                lambda progresso: self.lbl_status.config(text=f"Exportando... {progresso}%")
            )
        
        if resultado:
            messagebox.showinfo(
                "Exportar Relatório",
                f"Relatório exportado com sucesso para:\n{arquivo}"
            )
        else:
            messagebox.showerror(
                "Erro ao Exportar",
                "Não foi possível exportar o relatório."
            )
        
        # Atualizar barra de status
        self.lbl_status.config(text="Pronto")
    
    def _marcar_todas_aulas(self, concluida: bool):
        """Marca ou desmarca todas as aulas do curso"""
        if not self.app_service.curso_atual:
            messagebox.showinfo(
                "Marcar Aulas",
                "Nenhum curso selecionado."
            )
            return
        
        # Confirmar ação
        acao = "marcar" if concluida else "desmarcar"
        resposta = messagebox.askyesno(
            f"{acao.capitalize()} Todas as Aulas",
            f"Tem certeza que deseja {acao} todas as aulas deste curso?"
        )
        
        if not resposta:
            return
        
        # Atualizar barra de status
        self.lbl_status.config(text=f"{acao.capitalize()}ando todas as aulas...")
        self.root.update_idletasks()
        
        # Obter todas as aulas
        aulas = self.app_service.curso_atual.obter_todas_aulas()
        
        # Marcar cada aula
        for aula in aulas:
            self.app_service.marcar_aula_como_concluida(aula, concluida)
        
        # Atualizar interface
        self.arvore_aulas.atualizar_status_aulas()
        self._atualizar_informacoes_progresso()
        
        # Atualizar painel de detalhes se houver uma aula selecionada
        if self.app_service.aula_selecionada:
            self.painel_detalhes.exibir_aula(self.app_service.aula_selecionada)
        
        # Atualizar barra de status
        acao_completada = "marcadas" if concluida else "desmarcadas"
        self.lbl_status.config(text=f"Todas as aulas foram {acao_completada}")
    
    def _exibir_sobre(self):
        """Exibe informações sobre o aplicativo"""
        mensagem = (
            "Plano de Estudo para Cursos\n\n"
            "Versão 1.0\n\n"
            "Aplicativo para organizar e acompanhar o progresso de cursos em vídeo."
        )
        
        messagebox.showinfo("Sobre", mensagem)
    
    def _sair(self):
        """Fecha a aplicação"""
        # Confirmar saída
        resposta = messagebox.askyesno(
            "Sair",
            "Tem certeza que deseja sair?"
        )
        
        if not resposta:
            return
        
        # Fechar conexões
        self.app_service.fechar()
        
        # Fechar janela
        self.root.destroy()
    
    def _on_selecionar_aula(self, aula: Aula):
        """Trata a seleção de uma aula"""
        # Atualizar aula selecionada no serviço
        self.app_service.selecionar_aula(aula)
        
        # Exibir detalhes da aula
        self.painel_detalhes.exibir_aula(aula)
    
    def _on_marcar_aula(self, aula: Aula, concluida: bool):
        """Trata a marcação de uma aula como concluída ou não"""
        # Marcar aula
        self.app_service.marcar_aula_como_concluida(aula, concluida)
        
        # Atualizar interface
        self.arvore_aulas.atualizar_status_aulas()
        self._atualizar_informacoes_progresso()
    
    def _on_salvar_anotacoes(self, anotacoes: str, aula: Aula):
        """Trata o salvamento de anotações"""
        # Salvar anotações
        resultado = self.app_service.salvar_anotacoes(anotacoes, aula)
        
        if resultado:
            # Atualizar barra de status
            self.lbl_status.config(text="Anotações salvas com sucesso")
        else:
            messagebox.showerror(
                "Erro ao Salvar",
                "Não foi possível salvar as anotações."
            )
    
    def _on_abrir_video(self, aula: Aula):
        """Trata a abertura do vídeo de uma aula"""
        # Abrir vídeo
        resultado = self.app_service.abrir_video(aula)
        
        if not resultado:
            messagebox.showerror(
                "Erro ao Abrir Vídeo",
                f"Não foi possível abrir o vídeo:\n{aula.caminho_video}"
            )
    
    def _abrir_cursos_salvos(self):
        """Abre a janela de cursos salvos"""
        try:
            # Obter cursos salvos
            cursos = self.app_service.obter_cursos_salvos()
            
            if not cursos:
                messagebox.showinfo("Cursos Salvos", "Nenhum curso salvo encontrado.")
                return
            
            # Criar janela de diálogo
            janela_cursos = tk.Toplevel(self.root)
            janela_cursos.title("Cursos Salvos")
            janela_cursos.geometry("600x400")
            janela_cursos.transient(self.root)
            janela_cursos.grab_set()
            
            # Frame para lista de cursos
            frame_lista = ttk.Frame(janela_cursos, padding="10")
            frame_lista.pack(fill=tk.BOTH, expand=True)
            
            # Lista de cursos
            colunas = ("id", "nome", "caminho")
            tree_cursos = ttk.Treeview(frame_lista, columns=colunas, show="headings")
            
            # Configurar colunas
            tree_cursos.heading("id", text="ID")
            tree_cursos.heading("nome", text="Nome do Curso")
            tree_cursos.heading("caminho", text="Caminho")
            
            tree_cursos.column("id", width=50, anchor="center")
            tree_cursos.column("nome", width=200)
            tree_cursos.column("caminho", width=350)
            
            # Preencher lista
            for curso_id, nome, caminho in cursos:
                tree_cursos.insert("", "end", values=(curso_id, nome, caminho))
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=tree_cursos.yview)
            tree_cursos.configure(yscrollcommand=scrollbar.set)
            
            # Posicionamento
            tree_cursos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Frame para botões
            frame_botoes = ttk.Frame(janela_cursos, padding="10")
            frame_botoes.pack(fill=tk.X)
            
            # Função para carregar curso selecionado
            def carregar_curso_selecionado():
                selecao = tree_cursos.selection()
                if not selecao:
                    messagebox.showinfo("Seleção", "Por favor, selecione um curso.")
                    return
                
                item = tree_cursos.item(selecao[0])
                id_curso = item["values"][0]
                caminho = item["values"][2]
                
                # Fechar janela
                janela_cursos.destroy()
                
                # Carregar curso
                self._carregar_curso_por_id(id_curso, caminho)
            
            # Botões
            ttk.Button(frame_botoes, text="Carregar Curso", command=carregar_curso_selecionado).pack(side=tk.LEFT, padx=5)
            ttk.Button(frame_botoes, text="Cancelar", command=janela_cursos.destroy).pack(side=tk.RIGHT, padx=5)
            
            # Vincular duplo clique para carregar curso
            tree_cursos.bind("<Double-1>", lambda e: carregar_curso_selecionado())
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar cursos salvos: {e}")
    
    def _carregar_curso_por_id(self, id_curso, caminho):
        """Carrega um curso a partir do ID e caminho"""
        # Atualizar barra de status
        self.lbl_status.config(text=f"Carregando curso de {caminho}...")
        self.root.update_idletasks()
        
        # Carregar curso
        curso = self.app_service.carregar_curso_por_id(id_curso)
        
        if not curso:
            messagebox.showerror(
                "Erro ao Carregar Curso",
                "Não foi possível carregar o curso selecionado."
            )
            self.lbl_status.config(text="Pronto")
            return
        
        # Atualizar interface
        self.arvore_aulas.carregar_curso(curso)
        
        # Atualizar informações de progresso
        self._atualizar_informacoes_progresso()
        
        # Atualizar barra de status
        self.lbl_status.config(text=f"Curso carregado: {curso.nome}") 