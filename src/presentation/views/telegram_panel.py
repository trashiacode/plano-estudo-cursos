import tkinter as tk
from tkinter import ttk, messagebox
import asyncio
import threading
from typing import Callable, Dict, Any, List, Optional

class TelegramPanel(ttk.Frame):
    """Painel para gerenciar a integração com o Telegram e baixar vídeos"""
    
    def __init__(self, master=None, **kwargs):
        """Inicializa o painel do Telegram"""
        # Extrair callbacks
        self.on_configure_api = kwargs.pop('on_configure_api', None)
        self.on_list_channels = kwargs.pop('on_list_channels', None)
        self.on_download_channel = kwargs.pop('on_download_channel', None)
        
        # Extrair credenciais, se fornecidas
        self.api_id = kwargs.pop('api_id', None)
        self.api_hash = kwargs.pop('api_hash', None)
        
        # Inicializar Frame
        super().__init__(master, **kwargs)
        
        # Variáveis
        self.channels = []
        self.selected_channel_id = None
        self.filter_text = tk.StringVar()
        self.filter_text.trace_add("write", self._filtrar_canais)
        
        # Configurar interface
        self._configurar_interface()
        
        # Preencher campos com credenciais salvas, se existirem
        if self.api_id:
            self.entry_api_id.insert(0, self.api_id)
        if self.api_hash:
            self.entry_api_hash.insert(0, self.api_hash)
            
        # Se as credenciais já estão configuradas, habilitar a aba de download
        if self.api_id and self.api_hash:
            self.notebook.tab(1, state="normal")
    
    def _configurar_interface(self):
        """Configura a interface do painel"""
        # Adicionar padding geral ao frame
        self.configure(padding="10")
        
        # Mensagem explicativa no topo
        msg_label = ttk.Label(
            self, 
            text="Esta funcionalidade permite baixar vídeos de canais do Telegram.\n"
                 "É necessário configurar suas credenciais de API do Telegram para começar.",
            wraplength=800,
            justify=tk.LEFT,
            font=("", 10)
        )
        msg_label.pack(fill=tk.X, pady=(0, 10))
        
        # Notebook para separar as funcionalidades
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Painel de Configuração
        self.frame_config = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.frame_config, text="Configuração")
        
        # Painel de Download
        self.frame_download = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.frame_download, text="Download")
        
        # Configurar painéis
        self._configurar_painel_config()
        self._configurar_painel_download()
        
        # Desabilitar aba de download inicialmente se não tiver credenciais ou callbacks
        if not self.on_list_channels or not self.on_download_channel:
            self.notebook.tab(1, state="disabled")
            
        # Solicitar uma altura mínima para a janela principal 
        # mas só se encontrarmos uma referência para a janela principal
        try:
            # Tentar encontrar a janela principal (Tk ou Toplevel)
            root = self.winfo_toplevel()
            if root:
                self.after(100, lambda: root.minsize(800, 650))
        except Exception as e:
            print(f"Aviso: Não foi possível definir tamanho mínimo: {e}")
    
    def _configurar_painel_config(self):
        """Configura o painel de configuração da API"""
        frame = ttk.LabelFrame(self.frame_config, text="Configuração da API do Telegram", padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Instruções
        lbl_info = ttk.Label(
            frame, 
            text="Para usar esta funcionalidade, você precisa configurar as credenciais da API do Telegram.\n\n"
                 "1. Acesse https://my.telegram.org/apps\n"
                 "2. Faça login com sua conta do Telegram\n"
                 "3. Crie um aplicativo para obter suas credenciais (API ID e API Hash)\n"
                 "4. Insira as credenciais abaixo e clique em 'Salvar Configuração'\n\n"
                 "Observação: Suas credenciais são armazenadas apenas localmente e usadas "
                 "somente para acessar sua conta do Telegram.",
            wraplength=600,
            justify=tk.LEFT
        )
        lbl_info.pack(fill=tk.X, pady=(0, 20))
        
        # Frame para entradas
        frame_inputs = ttk.Frame(frame)
        frame_inputs.pack(fill=tk.X, pady=10)
        
        # API ID
        ttk.Label(frame_inputs, text="API ID:", width=12).grid(row=0, column=0, sticky=tk.W, padx=5, pady=10)
        self.entry_api_id = ttk.Entry(frame_inputs, width=30)
        self.entry_api_id.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=10)
        
        # API Hash
        ttk.Label(frame_inputs, text="API Hash:", width=12).grid(row=1, column=0, sticky=tk.W, padx=5, pady=10)
        self.entry_api_hash = ttk.Entry(frame_inputs, width=50)
        self.entry_api_hash.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=10)
        
        # Configurar expansão
        frame_inputs.columnconfigure(1, weight=1)
        
        # Frame para botões
        frame_botoes = ttk.Frame(frame)
        frame_botoes.pack(fill=tk.X, pady=20)
        
        # Botão para salvar
        self.btn_salvar = ttk.Button(
            frame_botoes, 
            text="Salvar Configuração",
            command=self._salvar_configuracao,
            width=20
        )
        self.btn_salvar.pack(pady=5)
        
        # Status
        self.lbl_status_config = ttk.Label(frame, text="", foreground="blue")
        self.lbl_status_config.pack(fill=tk.X, pady=10)
    
    def _configurar_painel_download(self):
        """Configura o painel de download de vídeos"""
        # Container principal com scrollbar
        container = ttk.Frame(self.frame_download)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar principal
        scrollbar = ttk.Scrollbar(container, orient="vertical")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Canvas para conteúdo rolável
        canvas = tk.Canvas(container, yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=canvas.yview)
        
        # Frame para conteúdo
        content_frame = ttk.Frame(canvas)
        canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw")
        
        # Função para ajustar o tamanho do canvas
        def _configure_canvas(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind("<Configure>", _configure_canvas)
        content_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Frame para seleção de canais
        frame_canais = ttk.LabelFrame(content_frame, text="Canais do Telegram", padding="10")
        frame_canais.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Instruções
        lbl_info = ttk.Label(
            frame_canais, 
            text="Selecione um canal na lista e clique em 'Baixar Vídeos' para fazer o download de todos os vídeos desse canal.\n"
                 "Os vídeos serão salvos na pasta 'Downloads/TelegramVideos' em seu diretório de usuário.\n\n"
                 "Para atualizar a lista de canais, clique em 'Atualizar Lista de Canais'.",
            wraplength=600,
            justify=tk.LEFT
        )
        lbl_info.pack(fill=tk.X, pady=(0, 10))
        
        # Botão para atualizar lista de canais
        frame_acoes = ttk.Frame(frame_canais)
        frame_acoes.pack(fill=tk.X, pady=10)
        
        self.btn_listar = ttk.Button(
            frame_acoes, 
            text="Atualizar Lista de Canais",
            command=self._listar_canais,
            width=25
        )
        self.btn_listar.pack(side=tk.LEFT, padx=5)
        
        # Status
        self.lbl_status_download = ttk.Label(frame_acoes, text="")
        self.lbl_status_download.pack(side=tk.LEFT, padx=10)
        
        # Frame para filtro de busca
        frame_filtro = ttk.Frame(frame_canais)
        frame_filtro.pack(fill=tk.X, pady=10)
        
        ttk.Label(frame_filtro, text="Filtrar canais:").pack(side=tk.LEFT, padx=(0, 5))
        
        # Campo de busca
        self.entry_filtro = ttk.Entry(frame_filtro, textvariable=self.filter_text, width=30)
        self.entry_filtro.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Botão para limpar filtro
        ttk.Button(
            frame_filtro, 
            text="Limpar",
            command=self._limpar_filtro,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        # Lista de canais
        frame_lista = ttk.Frame(frame_canais)
        frame_lista.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Treeview para canais - altura reduzida para garantir que os controles abaixo sejam visíveis
        colunas = ("id", "titulo", "tipo", "membros")
        self.tree_canais = ttk.Treeview(
            frame_lista, 
            columns=colunas,
            show="headings",
            selectmode="browse",
            height=6  # Altura reduzida
        )
        
        # Configurar colunas
        self.tree_canais.heading("id", text="ID")
        self.tree_canais.heading("titulo", text="Nome do Canal")
        self.tree_canais.heading("tipo", text="Tipo")
        self.tree_canais.heading("membros", text="Membros")
        
        self.tree_canais.column("id", width=100, anchor=tk.CENTER)
        self.tree_canais.column("titulo", width=300)
        self.tree_canais.column("tipo", width=100, anchor=tk.CENTER)
        self.tree_canais.column("membros", width=100, anchor=tk.CENTER)
        
        # Scrollbar
        scrollbar_y = ttk.Scrollbar(frame_lista, orient="vertical", command=self.tree_canais.yview)
        self.tree_canais.configure(yscrollcommand=scrollbar_y.set)
        
        scrollbar_x = ttk.Scrollbar(frame_lista, orient="horizontal", command=self.tree_canais.xview)
        self.tree_canais.configure(xscrollcommand=scrollbar_x.set)
        
        # Posicionamento
        self.tree_canais.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Vincular seleção
        self.tree_canais.bind("<<TreeviewSelect>>", self._selecionar_canal)
        
        # Frame para download - destaque visual
        frame_download = ttk.LabelFrame(content_frame, text="Baixar Vídeos", padding="10")
        frame_download.pack(fill=tk.X, pady=10, padx=5)
        
        # Botão para download
        self.btn_download = ttk.Button(
            frame_download, 
            text="Baixar Vídeos do Canal Selecionado",
            command=self._iniciar_download,
            state="disabled",
            width=30
        )
        self.btn_download.pack(side=tk.TOP, pady=10)
        
        # Frame para progresso
        frame_progresso = ttk.Frame(frame_download)
        frame_progresso.pack(fill=tk.X, expand=True, pady=10)
        
        # Barra de progresso
        ttk.Label(frame_progresso, text="Progresso:").pack(side=tk.LEFT, padx=(0, 5))
        
        # Configurar estilo da barra de progresso com cor verde
        estilo = ttk.Style()
        estilo.configure("verde.Horizontal.TProgressbar", background='green', troughcolor='lightgray')
        
        self.progresso = ttk.Progressbar(
            frame_progresso, 
            orient="horizontal", 
            length=300,
            mode="determinate",
            style="verde.Horizontal.TProgressbar"  # Aplicar o estilo verde
        )
        self.progresso.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Label de progresso - mostra informações detalhadas sobre o progresso do download
        self.lbl_progresso = ttk.Label(frame_download, text="", wraplength=700)
        self.lbl_progresso.pack(side=tk.TOP, padx=5, pady=10, fill=tk.X)
        
        # Explicação do rótulo de progresso
        ttk.Label(
            frame_download, 
            text="O rótulo de progresso acima mostra detalhes sobre o download atual, como número de arquivos baixados, ignorados e erros encontrados durante o processo.",
            wraplength=700,
            justify=tk.LEFT,
            font=("", 8),
            foreground="#555555"
        ).pack(fill=tk.X, pady=(0, 5))
    
    def _filtrar_canais(self, *args):
        """Filtra a lista de canais com base no texto digitado"""
        if not self.channels:
            return
            
        # Obter texto do filtro (converter para minúsculo para comparação insensível a caso)
        filtro = self.filter_text.get().lower()
        
        # Limpar lista atual
        for item in self.tree_canais.get_children():
            self.tree_canais.delete(item)
            
        # Se não houver filtro, mostrar todos os canais
        if not filtro:
            for channel in self.channels:
                self.tree_canais.insert(
                    "", "end",
                    values=(
                        channel['id'],
                        channel['title'],
                        channel['type'],
                        channel['members_count']
                    )
                )
            return
            
        # Filtrar e mostrar apenas os canais que correspondem ao filtro
        canais_filtrados = [
            channel for channel in self.channels
            if filtro in channel['title'].lower()
        ]
        
        for channel in canais_filtrados:
            self.tree_canais.insert(
                "", "end",
                values=(
                    channel['id'],
                    channel['title'],
                    channel['type'],
                    channel['members_count']
                )
            )
            
        # Atualizar status com contagem de resultados
        self.lbl_status_download.config(
            text=f"{len(canais_filtrados)} canais encontrados para '{filtro}' (de {len(self.channels)} total)"
        )
    
    def _limpar_filtro(self):
        """Limpa o filtro de busca"""
        self.filter_text.set("")
        self.entry_filtro.focus()
    
    def _salvar_configuracao(self):
        """Salva as configurações de API"""
        api_id = self.entry_api_id.get().strip()
        api_hash = self.entry_api_hash.get().strip()
        
        if not api_id or not api_hash:
            messagebox.showerror(
                "Erro de Configuração",
                "Preencha o API ID e API Hash para continuar."
            )
            return
        
        self.lbl_status_config.config(text="Salvando configuração...")
        self.btn_salvar.config(state="disabled")
        self.update_idletasks()
        
        if self.on_configure_api:
            # Chamar callback em uma thread para não travar a interface
            threading.Thread(
                target=self._processar_configuracao,
                args=(api_id, api_hash),
                daemon=True
            ).start()
    
    def _processar_configuracao(self, api_id, api_hash):
        """Processa a configuração da API em uma thread separada"""
        resultado = self.on_configure_api(api_id, api_hash)
        
        # Atualizar interface na thread principal
        self.after(0, lambda: self._atualizar_status_config(resultado))
    
    def _atualizar_status_config(self, sucesso):
        """Atualiza o status da configuração na interface"""
        if sucesso:
            self.lbl_status_config.config(text="Configuração salva com sucesso!", foreground="green")
            self.notebook.tab(1, state="normal")
        else:
            self.lbl_status_config.config(text="Erro ao salvar configuração. Verifique as credenciais.", foreground="red")
        
        self.btn_salvar.config(state="normal")
    
    def _listar_canais(self):
        """Lista os canais disponíveis no Telegram"""
        self.lbl_status_download.config(text="Carregando canais...")
        self.btn_listar.config(state="disabled")
        self.update_idletasks()
        
        # Limpar lista atual
        for item in self.tree_canais.get_children():
            self.tree_canais.delete(item)
        
        # Limpar filtro
        self.filter_text.set("")
        
        self.channels = []
        self.selected_channel_id = None
        self.btn_download.config(state="disabled")
        
        if self.on_list_channels:
            # Iniciar em uma thread separada
            threading.Thread(
                target=self._processar_listagem_canais,
                daemon=True
            ).start()
    
    def _processar_listagem_canais(self):
        """Processa a listagem de canais em uma thread separada"""
        try:
            if hasattr(self.on_list_channels, '__self__') and hasattr(self.on_list_channels.__self__, 'run_async'):
                # Usar o método run_async se disponível no controlador
                controller = self.on_list_channels.__self__
                controller.run_async(
                    self.on_list_channels,
                    callback=lambda result, error=None: self.after(0, lambda: self._processar_resultado_listagem(result, error))
                )
            else:
                # Fallback para o método antigo
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                channels = loop.run_until_complete(self.on_list_channels())
                loop.close()
                self.after(0, lambda: self._atualizar_lista_canais(channels))
                
        except Exception as e:
            self.after(0, lambda: self._mostrar_erro_listagem(str(e)))
    
    def _processar_resultado_listagem(self, channels, error=None):
        """Processa o resultado da listagem de canais"""
        if error:
            self._mostrar_erro_listagem(error)
        else:
            self._atualizar_lista_canais(channels)
    
    def _atualizar_lista_canais(self, channels):
        """Atualiza a lista de canais na interface"""
        self.channels = channels
        
        if not channels:
            self.lbl_status_download.config(text="Nenhum canal encontrado.")
            self.btn_listar.config(state="normal")
            self.entry_filtro.config(state="disabled")
            return
        
        # Habilitar campo de filtro
        self.entry_filtro.config(state="normal")
        
        # Preencher treeview
        for channel in channels:
            self.tree_canais.insert(
                "", "end",
                values=(
                    channel['id'],
                    channel['title'],
                    channel['type'],
                    channel['members_count']
                )
            )
        
        self.lbl_status_download.config(text=f"{len(channels)} canais encontrados.")
        self.btn_listar.config(state="normal")
        
        # Focar no campo de filtro para facilitar a busca
        self.entry_filtro.focus()
    
    def _mostrar_erro_listagem(self, erro):
        """Mostra uma mensagem de erro na interface"""
        self.lbl_status_download.config(text=f"Erro: {erro}")
        self.btn_listar.config(state="normal")
    
    def _selecionar_canal(self, event):
        """Manipula a seleção de um canal na lista"""
        selection = self.tree_canais.selection()
        if not selection:
            return
        
        item = self.tree_canais.item(selection[0])
        channel_id = item['values'][0]
        
        self.selected_channel_id = channel_id
        self.btn_download.config(state="normal")
    
    def _iniciar_download(self):
        """Inicia o download de vídeos do canal selecionado"""
        if not self.selected_channel_id:
            messagebox.showinfo("Seleção necessária", "Selecione um canal para baixar os vídeos.")
            return
        
        # Debug para verificar a chamada
        print(f"Iniciando download para o canal {self.selected_channel_id}")
        
        # Desabilitar botão durante o download
        self.btn_download.config(state="disabled")
        self.progresso["value"] = 0
        self.lbl_progresso.config(text="Iniciando download...")
        
        # Verificar se o label de progresso existe
        if not hasattr(self, 'lbl_progresso'):
            print("ERRO: Label lbl_progresso não foi encontrado!")
            self.btn_download.config(state="normal")
            return
        
        if self.on_download_channel:
            # Iniciar em uma thread separada
            threading.Thread(
                target=self._processar_download,
                args=(self.selected_channel_id,),
                daemon=True
            ).start()
        else:
            print("ERRO: Callback on_download_channel não está definido")
            self.lbl_progresso.config(text="Erro: Configuração de download inválida.")
            self.btn_download.config(state="normal")
    
    def _processar_download(self, channel_id):
        """Processa o download em uma thread separada"""
        # Debug para verificar se a thread está sendo executada
        print(f"Processando download do canal {channel_id}")
        
        try:
            # Simplificar o código para usar apenas o método run_async
            if hasattr(self.on_download_channel, '__self__'):
                # Debug para verificar se está usando run_async
                print("Obtendo referência ao controlador")
                controller = self.on_download_channel.__self__
                
                # Usar diretamente o método run_async do controlador em vez de criar um novo loop
                # Isso garante que usamos o mesmo loop em toda a aplicação
                print("Usando método run_async do controlador")
                controller.run_async(
                    controller.download_channel,
                    channel_id,
                    # Criar uma lambda que captura os argumentos e chama _atualizar_progresso
                    lambda current, total, text: self.after(0, 
                        # Usar uma lambda aninhada para passar os argumentos
                        lambda c=current, t=total, txt=text: self._atualizar_progresso(c, t, txt)
                    ),
                    # Função de callback que será chamada quando o download terminar
                    callback=lambda resultado, erro=None: self.after(0, 
                        lambda r=resultado, e=erro: self._processar_resultado_download(r, e)
                    )
                )
            else:
                # Fallback para o método antigo em casos onde o controlador não está disponível
                print("Usando método direto (fallback)")
                
                def progress_callback(current, total, text):
                    # Capturar os argumentos em um escopo local
                    c, t, txt = current, total, text
                    self.after(0, lambda: self._atualizar_progresso(c, t, txt))
                
                # Iniciar nova thread para executar o download de forma assíncrona
                threading.Thread(
                    target=self._executar_download_direto,
                    args=(channel_id, progress_callback),
                    daemon=True
                ).start()
        except Exception as e:
            # Capturar a exceção em uma variável local
            error_msg = str(e)
            print(f"Erro no _processar_download: {error_msg}")
            # Usar a variável local no lambda para evitar problemas de escopo
            self.after(0, lambda msg=error_msg: self._mostrar_erro_download(msg))
    
    def _executar_download_direto(self, channel_id, progress_callback):
        """Executa o download diretamente, sem passar pelo controlador"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                resultado = loop.run_until_complete(
                    self.on_download_channel(channel_id, progress_callback)
                )
                # Guardar o resultado em uma variável local
                final_result = resultado
                self.after(0, lambda r=final_result: self._finalizar_download(r))
            except Exception as e:
                # Capturar a exceção em uma variável local
                error_msg = str(e)
                print(f"Erro durante download direto: {error_msg}")
                # Usar a variável local no lambda
                self.after(0, lambda msg=error_msg: self._mostrar_erro_download(msg))
            finally:
                loop.close()
        except Exception as e:
            # Capturar a exceção em uma variável local
            error_msg = str(e)
            print(f"Erro no _executar_download_direto: {error_msg}")
            # Usar a variável local no lambda
            self.after(0, lambda msg=error_msg: self._mostrar_erro_download(msg))
            
    def _processar_resultado_download(self, resultado, erro=None):
        """Processa o resultado do download assíncrono"""
        if erro:
            print(f"Erro de download reportado: {erro}")
            self._mostrar_erro_download(erro)
        else:
            print(f"Download finalizado com sucesso: {resultado}")
            self._finalizar_download(resultado)
    
    def _atualizar_progresso(self, current, total, text):
        """Atualiza o progresso do download na interface"""
        print(f"Atualizando progresso: {current}/{total} - {text}")
        self.progresso["value"] = current
        self.progresso["maximum"] = total
        self.lbl_progresso.config(text=text)
    
    def _finalizar_download(self, resultado):
        """Finaliza o download na interface"""
        print(f"Finalizando download: {resultado}")
        if resultado:
            self.lbl_progresso.config(text="Download concluído com sucesso!")
        else:
            self.lbl_progresso.config(text="Erro ao concluir o download.")
        
        self.btn_download.config(state="normal")
    
    def _mostrar_erro_download(self, erro):
        """Mostra uma mensagem de erro na interface"""
        print(f"Erro de download: {erro}")
        self.lbl_progresso.config(text=f"Erro: {erro}")
        self.btn_download.config(state="normal") 