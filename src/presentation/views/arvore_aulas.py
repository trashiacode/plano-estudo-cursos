import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, List, Callable, Optional

from src.domain.entities import Curso, Modulo, Aula

class ArvoreAulas(ttk.Frame):
    """Componente para exibir a estrutura de aulas em forma de árvore"""
    
    def __init__(self, master=None, **kwargs):
        """Inicializa o componente de árvore de aulas"""
        # Extrair callbacks antes de inicializar o Frame
        self.on_selecionar_aula = kwargs.pop('on_selecionar_aula', None)
        self.on_marcar_aula = kwargs.pop('on_marcar_aula', None)
        self.on_abrir_video = kwargs.pop('on_abrir_video', None)
        
        # Inicializar o Frame com os parâmetros restantes
        super().__init__(master, **kwargs)
        
        # Definir cores para os diferentes estados
        self.arvore_cores = {
            "aula_concluida": "#E0F2E0",  # Verde claro
            "modulo_completo": "#E0E0FF",  # Azul claro
            "destaque_pesquisa": "#FFFFAA"  # Amarelo claro
        }
        
        # Criar barra de pesquisa
        self.frame_pesquisa = ttk.Frame(self)
        self.frame_pesquisa.pack(fill=tk.X, padx=5, pady=5)
        
        self.entry_pesquisa = ttk.Entry(self.frame_pesquisa)
        self.entry_pesquisa.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.btn_pesquisar = ttk.Button(
            self.frame_pesquisa, 
            text="Pesquisar",
            command=self._pesquisar
        )
        self.btn_pesquisar.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Criar árvore
        self.frame_arvore = ttk.Frame(self)
        self.frame_arvore.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.arvore = ttk.Treeview(
            self.frame_arvore,
            columns=("progresso",),
            displaycolumns=("progresso",),
            selectmode="browse"
        )
        
        # Configurar colunas
        self.arvore.column("#0", width=350, minwidth=250)
        self.arvore.column("progresso", width=100, minwidth=80, anchor=tk.CENTER)
        
        # Configurar cabeçalhos
        self.arvore.heading("#0", text="Aulas")
        self.arvore.heading("progresso", text="Progresso")
        
        # Adicionar barra de rolagem
        self.scrollbar_y = ttk.Scrollbar(
            self.frame_arvore, 
            orient="vertical", 
            command=self.arvore.yview
        )
        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.scrollbar_x = ttk.Scrollbar(
            self.frame_arvore, 
            orient="horizontal", 
            command=self.arvore.xview
        )
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.arvore.configure(
            yscrollcommand=self.scrollbar_y.set,
            xscrollcommand=self.scrollbar_x.set
        )
        
        # Empacotar árvore
        self.arvore.pack(fill=tk.BOTH, expand=True)
        
        # Configurar tags para itens da árvore
        self.arvore.tag_configure("concluida", background=self.arvore_cores["aula_concluida"])
        self.arvore.tag_configure("modulo_completo", background=self.arvore_cores["modulo_completo"])
        self.arvore.tag_configure("pesquisa", background=self.arvore_cores["destaque_pesquisa"])
        
        # Vincular eventos
        self.arvore.bind("<<TreeviewSelect>>", self._on_selecionar_item)
        self.arvore.bind("<Double-1>", self._on_duplo_clique)
        self.arvore.bind("<space>", self._on_tecla_espaco)
        self.entry_pesquisa.bind("<Return>", self._pesquisar)
        
        # Adicionar menu de contexto
        self._criar_menu_contexto()
        self.arvore.bind("<Button-3>", self._exibir_menu_contexto)
        
        # Variáveis de controle
        self.curso_atual = None
        self.mapa_itens = {}  # Mapeamento de itens da árvore para objetos
        
    def _configurar_estilo(self):
        """Configura o estilo da árvore"""
        estilo = ttk.Style()
        
        # Configurar cores para os diferentes estados
        self.arvore_cores = {
            "aula_concluida": "#E0F2E0",  # Verde claro
            "modulo_completo": "#E0E0FF",  # Azul claro
            "destaque_pesquisa": "#FFFFAA"  # Amarelo claro
        }
        
        # Configurar tags para itens da árvore
        self.arvore.tag_configure("concluida", background=self.arvore_cores["aula_concluida"])
        self.arvore.tag_configure("modulo_completo", background=self.arvore_cores["modulo_completo"])
        self.arvore.tag_configure("pesquisa", background=self.arvore_cores["destaque_pesquisa"])
    
    def _criar_menu_contexto(self):
        """Cria o menu de contexto da árvore"""
        self.menu_contexto = tk.Menu(self, tearoff=0)
        
        self.menu_contexto.add_command(
            label="Marcar como concluída",
            command=lambda: self._marcar_desmarcar_aula(True)
        )
        
        self.menu_contexto.add_command(
            label="Marcar como não concluída",
            command=lambda: self._marcar_desmarcar_aula(False)
        )
        
        self.menu_contexto.add_separator()
        
        self.menu_contexto.add_command(
            label="Abrir vídeo",
            command=self._abrir_video
        )
        
        self.menu_contexto.add_separator()
        
        self.menu_contexto.add_command(
            label="Marcar todas as aulas deste módulo",
            command=lambda: self._marcar_desmarcar_todas_aulas(True)
        )
        
        self.menu_contexto.add_command(
            label="Desmarcar todas as aulas deste módulo",
            command=lambda: self._marcar_desmarcar_todas_aulas(False)
        )
    
    def _exibir_menu_contexto(self, event):
        """Exibe o menu de contexto"""
        item = self.arvore.identify_row(event.y)
        
        if item:
            # Selecionar o item clicado
            self.arvore.selection_set(item)
            
            # Exibir menu de contexto
            self.menu_contexto.post(event.x_root, event.y_root)
    
    def carregar_curso(self, curso: Curso):
        """Carrega um curso na árvore"""
        # Limpar árvore
        for item in self.arvore.get_children():
            self.arvore.delete(item)
        
        # Limpar mapa de itens
        self.mapa_itens = {}
        
        # Armazenar curso atual
        self.curso_atual = curso
        
        if not curso:
            return
        
        # Adicionar nó raiz do curso
        id_curso = self.arvore.insert(
            "", "end", 
            text=curso.nome,
            values=(f"{curso.progresso}%",),
            open=True
        )
        
        # Associar curso ao nó raiz
        self.mapa_itens[id_curso] = curso
        
        # Adicionar módulos e aulas
        for modulo in curso.modulos:
            self._adicionar_modulo(id_curso, modulo)
    
    def _adicionar_modulo(self, id_pai, modulo: Modulo):
        """Adiciona um módulo e seus filhos à árvore"""
        # Determinar progresso do módulo
        progresso = "0%"
        if hasattr(modulo, 'aulas_concluidas') and hasattr(modulo, 'total_aulas'):
            if modulo.total_aulas > 0:
                porcentagem = int((modulo.aulas_concluidas / modulo.total_aulas) * 100)
                progresso = f"{porcentagem}%"
        
        # Determinar se o módulo deve iniciar fechado
        esta_aberto = False
        
        # Adicionar nó do módulo
        id_modulo = self.arvore.insert(
            id_pai, "end",
            text=modulo.nome,
            values=(progresso,),
            open=esta_aberto,
            tags=("modulo",)
        )
        
        # Associar módulo ao nó
        self.mapa_itens[id_modulo] = modulo
        
        # Adicionar aulas do módulo
        if hasattr(modulo, 'aulas') and modulo.aulas:
            for aula in modulo.aulas:
                self._adicionar_aula(id_modulo, aula)
        
        # Adicionar submódulos recursivamente
        if hasattr(modulo, 'submodulos') and modulo.submodulos:
            for submodulo in modulo.submodulos:
                self._adicionar_modulo(id_modulo, submodulo)
                
        # Atualizar tags do módulo com base no estado das aulas
        self._atualizar_tags_modulo(id_modulo)
    
    def _adicionar_aula(self, id_pai, aula: Aula):
        """Adiciona uma aula à árvore"""
        # Determinar status da aula
        status = "Concluída" if aula.concluida else "Pendente"
        tags = ("aula", "concluida" if aula.concluida else "pendente")
        
        # Adicionar nó da aula
        id_aula = self.arvore.insert(
            id_pai, "end",
            text=aula.titulo_formatado,
            values=(status,),
            tags=tags
        )
        
        # Associar aula ao nó
        self.mapa_itens[id_aula] = aula
    
    def _atualizar_tags_modulo(self, id_modulo):
        """Atualiza as tags de um módulo com base no estado das aulas"""
        # Obter módulo
        modulo = self.mapa_itens.get(id_modulo)
        
        if not modulo or not hasattr(modulo, 'esta_completo'):
            return
        
        # Verificar se todas as aulas do módulo estão concluídas
        if modulo.esta_completo:
            # Módulo completamente concluído
            self.arvore.item(id_modulo, tags=("modulo", "modulo_completo"))
        else:
            # Módulo parcialmente concluído ou não concluído
            self.arvore.item(id_modulo, tags=("modulo", "pendente"))
    
    def atualizar_status_aulas(self):
        """Atualiza o status de todas as aulas na árvore"""
        # Atualizar recursivamente todos os itens da árvore
        for id_item in self.arvore.get_children():
            self._atualizar_status_item_recursivo(id_item)
    
    def _atualizar_status_item_recursivo(self, id_item):
        """Atualiza o status de um item e seus filhos recursivamente"""
        item = self.mapa_itens.get(id_item)
        
        if not item:
            return
        
        # Atualizar aula
        if isinstance(item, Aula):
            # Atualizar tags da aula
            tags = list(self.arvore.item(id_item, "tags"))
            
            if "aula" not in tags:
                tags.append("aula")
            
            if item.concluida:
                if "pendente" in tags:
                    tags.remove("pendente")
                if "concluida" not in tags:
                    tags.append("concluida")
                self.arvore.item(id_item, values=("Concluída",), tags=tags)
            else:
                if "concluida" in tags:
                    tags.remove("concluida")
                if "pendente" not in tags:
                    tags.append("pendente")
                self.arvore.item(id_item, values=("Pendente",), tags=tags)
        
        # Atualizar módulo
        elif isinstance(item, Modulo) or isinstance(item, Curso):
            # Atualizar filhos recursivamente
            for id_filho in self.arvore.get_children(id_item):
                self._atualizar_status_item_recursivo(id_filho)
            
            # Verificar se é um módulo
            if isinstance(item, Modulo):
                # Verificar se todas as aulas estão concluídas
                todas_concluidas = item.esta_completo
                
                # Atualizar tags do módulo
                tags = list(self.arvore.item(id_item, "tags"))
                
                if "modulo" not in tags:
                    tags.append("modulo")
                
                if todas_concluidas:
                    if "pendente" in tags:
                        tags.remove("pendente")
                    if "modulo_completo" not in tags:
                        tags.append("modulo_completo")
                        # Remover tag concluida se existir (para compatibilidade)
                        if "concluida" in tags:
                            tags.remove("concluida")
                else:
                    if "modulo_completo" in tags:
                        tags.remove("modulo_completo")
                    if "concluida" in tags:
                        tags.remove("concluida")
                    if "pendente" not in tags:
                        tags.append("pendente")
                
                # Calcular progresso do módulo
                progresso = "0%"
                if hasattr(item, 'total_aulas') and item.total_aulas > 0:
                    porcentagem = int((item.aulas_concluidas / item.total_aulas) * 100)
                    progresso = f"{porcentagem}%"
                
                # Atualizar item
                self.arvore.item(id_item, values=(progresso,), tags=tags)
            
            # Verificar se é o curso
            elif isinstance(item, Curso):
                # Atualizar progresso do curso
                self.arvore.item(id_item, values=(f"{item.progresso}%",))
    
    def _on_selecionar_item(self, event):
        """Trata a seleção de um item na árvore"""
        # Obter item selecionado
        selecionados = self.arvore.selection()
        
        if not selecionados:
            return
        
        # Obter o primeiro item selecionado
        id_item = selecionados[0]
        
        # Obter objeto associado ao item
        item = self.mapa_itens.get(id_item)
        
        if not item:
            return
        
        # Verificar se é uma aula
        if isinstance(item, Aula) and self.on_selecionar_aula:
            self.on_selecionar_aula(item)
    
    def _on_duplo_clique(self, event):
        """Trata o duplo clique em um item"""
        # Obter item clicado
        id_item = self.arvore.identify_row(event.y)
        
        if not id_item:
            return
        
        # Obter objeto associado ao item
        item = self.mapa_itens.get(id_item)
        
        if not item:
            return
        
        # Verificar se é uma aula ou módulo
        if isinstance(item, Aula):
            # Marcar/desmarcar aula como concluída
            self._marcar_desmarcar_aula(not item.concluida)
        elif isinstance(item, Modulo):
            # Expandir/colapsar módulo
            if self.arvore.item(id_item, "open"):
                self.arvore.item(id_item, open=False)
            else:
                self.arvore.item(id_item, open=True)
    
    def _on_tecla_espaco(self, event):
        """Trata a tecla de espaço para marcar/desmarcar aulas"""
        # Obter item selecionado
        selecionados = self.arvore.selection()
        
        if not selecionados:
            return
        
        # Obter o primeiro item selecionado
        id_item = selecionados[0]
        
        # Obter objeto associado ao item
        item = self.mapa_itens.get(id_item)
        
        if not item:
            return
        
        # Verificar se é uma aula
        if isinstance(item, Aula):
            # Marcar/desmarcar aula como concluída
            self._marcar_desmarcar_aula(not item.concluida)
    
    def _marcar_desmarcar_aula(self, concluida: bool):
        """Marca ou desmarca uma aula como concluída"""
        # Obter item selecionado
        selecionados = self.arvore.selection()
        
        if not selecionados:
            return
        
        # Obter o primeiro item selecionado
        id_item = selecionados[0]
        
        # Obter objeto associado ao item
        item = self.mapa_itens.get(id_item)
        
        if not item or not isinstance(item, Aula):
            return
        
        # Chamar callback para marcar aula
        if self.on_marcar_aula:
            self.on_marcar_aula(item, concluida)
            
            # Atualizar árvore
            self.atualizar_status_aulas()
    
    def _marcar_desmarcar_todas_aulas(self, concluida: bool):
        """Marca ou desmarca todas as aulas de um módulo como concluídas"""
        # Obter item selecionado
        selecionados = self.arvore.selection()
        
        if not selecionados:
            return
        
        # Obter o primeiro item selecionado
        id_item = selecionados[0]
        
        # Obter objeto associado ao item
        item = self.mapa_itens.get(id_item)
        
        if not item:
            return
        
        # Obter todas as aulas do módulo
        aulas = []
        
        # Função recursiva para coletar aulas
        def coletar_aulas(id_node):
            for id_filho in self.arvore.get_children(id_node):
                filho = self.mapa_itens.get(id_filho)
                
                if isinstance(filho, Aula):
                    aulas.append(filho)
                else:
                    coletar_aulas(id_filho)
        
        # Coletar aulas do item selecionado
        coletar_aulas(id_item)
        
        # Marcar cada aula
        for aula in aulas:
            if self.on_marcar_aula:
                self.on_marcar_aula(aula, concluida)
        
        # Atualizar árvore
        self.atualizar_status_aulas()
    
    def _abrir_video(self):
        """Abre o vídeo da aula selecionada"""
        # Obter item selecionado
        selecionados = self.arvore.selection()
        
        if not selecionados:
            return
        
        # Obter o primeiro item selecionado
        id_item = selecionados[0]
        
        # Obter objeto associado ao item
        item = self.mapa_itens.get(id_item)
        
        if not item or not isinstance(item, Aula):
            return
        
        # Chamar callback para abrir vídeo
        if hasattr(self, 'on_abrir_video') and self.on_abrir_video:
            self.on_abrir_video(item)
    
    def _pesquisar(self, event=None):
        """Realiza a pesquisa de aulas"""
        termo = self.entry_pesquisa.get().strip()
        
        if not termo or not self.curso_atual:
            return
        
        # Destacar itens que correspondem à pesquisa
        self._limpar_destaque_pesquisa()
        self._destacar_itens_pesquisa(termo)
    
    def _limpar_destaque_pesquisa(self):
        """Remove o destaque de pesquisa de todos os itens"""
        # Obter todos os itens recursivamente
        todos_itens = []
        
        def coletar_itens(item_id):
            todos_itens.append(item_id)
            for filho_id in self.arvore.get_children(item_id):
                coletar_itens(filho_id)
        
        # Coletar itens a partir da raiz
        for item_id in self.arvore.get_children():
            coletar_itens(item_id)
        
        # Remover tag de destaque de todos os itens
        for item_id in todos_itens:
            tags = list(self.arvore.item(item_id, "tags"))
            if "pesquisa" in tags:
                tags.remove("pesquisa")
                self.arvore.item(item_id, tags=tags)
    
    def _destacar_itens_pesquisa(self, termo):
        """Destaca itens que correspondem ao termo de pesquisa"""
        termo = termo.lower()
        
        # Configurar tag de pesquisa se ainda não estiver configurada
        try:
            self.arvore.tag_configure("pesquisa", background=self.arvore_cores["destaque_pesquisa"])
        except:
            pass
        
        # Função recursiva para verificar e destacar itens
        def verificar_item(item_id):
            encontrou = False
            item = self.mapa_itens.get(item_id)
            
            if item:
                # Verificar se o termo está no título do item
                if isinstance(item, Aula) and termo in item.titulo.lower():
                    # Adicionar tag de pesquisa
                    tags = list(self.arvore.item(item_id, "tags"))
                    if "pesquisa" not in tags:
                        tags.append("pesquisa")
                        self.arvore.item(item_id, tags=tags)
                    
                    # Expandir pais para mostrar o item
                    self._expandir_pais(item_id)
                    
                    # Verificar se é o primeiro item encontrado
                    if not self.primeiro_encontrado:
                        self.primeiro_encontrado = item_id
                    
                    encontrou = True
            
            # Verificar filhos recursivamente
            for filho_id in self.arvore.get_children(item_id):
                if verificar_item(filho_id):
                    encontrou = True
            
            return encontrou
        
        # Variável para rastrear o primeiro item encontrado
        self.primeiro_encontrado = None
        
        # Verificar todos os itens começando pela raiz
        for item_id in self.arvore.get_children():
            verificar_item(item_id)
        
        # Selecionar e mostrar o primeiro item encontrado
        if self.primeiro_encontrado:
            self.arvore.see(self.primeiro_encontrado)
            self.arvore.selection_set(self.primeiro_encontrado)
            self._on_selecionar_item(None)  # Simular seleção do item
    
    def _expandir_pais(self, item_id):
        """Expande todos os pais de um item para torná-lo visível"""
        pai_id = self.arvore.parent(item_id)
        
        while pai_id:
            self.arvore.item(pai_id, open=True)
            pai_id = self.arvore.parent(pai_id) 