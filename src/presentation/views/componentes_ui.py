import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont

class BarraProgresso(ttk.Frame):
    """Componente de barra de progresso personalizada com percentual"""
    
    def __init__(self, master=None, **kwargs):
        """Inicializa a barra de progresso personalizada"""
        super().__init__(master, **kwargs)
        
        # Configurações
        self.altura = kwargs.get('altura', 20)
        self.largura = kwargs.get('largura', 200)
        self.valor = kwargs.get('valor', 0)
        self.cor_fundo = kwargs.get('cor_fundo', '#e0e0e0')
        self.cor_barra = kwargs.get('cor_barra', '#2a9d8f')
        self.cor_texto = kwargs.get('cor_texto', '#000000')
        
        # Criar canvas
        self.canvas = tk.Canvas(
            self,
            width=self.largura,
            height=self.altura,
            bg=self.cor_fundo,
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Criar barra de progresso
        self.barra = self.canvas.create_rectangle(
            0, 0, 0, self.altura,
            fill=self.cor_barra, width=0
        )
        
        # Criar texto de percentual
        self.texto = self.canvas.create_text(
            self.largura / 2, self.altura / 2,
            text=f"{self.valor}%",
            fill=self.cor_texto,
            font=('Arial', 10, 'bold')
        )
        
        # Atualizar a barra com o valor inicial
        self.atualizar(self.valor)
        
    def atualizar(self, valor):
        """Atualiza o valor da barra de progresso"""
        if valor < 0:
            valor = 0
        elif valor > 100:
            valor = 100
            
        self.valor = valor
        
        # Calcular largura da barra
        largura_barra = (self.valor / 100) * self.largura
        
        # Atualizar barra
        self.canvas.coords(self.barra, 0, 0, largura_barra, self.altura)
        
        # Atualizar texto
        self.canvas.itemconfig(self.texto, text=f"{int(self.valor)}%")


class Tooltip:
    """Componente de tooltip para exibir dicas ao passar o mouse"""
    
    def __init__(self, widget, text):
        """Inicializa o tooltip"""
        self.widget = widget
        self.text = text
        self.tooltip = None
        
        # Vincular eventos
        self.widget.bind("<Enter>", self.exibir)
        self.widget.bind("<Leave>", self.ocultar)
        
    def exibir(self, event=None):
        """Exibe o tooltip"""
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        # Criar janela de tooltip
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        # Criar label
        label = tk.Label(
            self.tooltip, text=self.text, justify=tk.LEFT,
            background="#ffffe0", relief=tk.SOLID, borderwidth=1,
            padx=5, pady=5
        )
        label.pack(ipadx=1)
        
    def ocultar(self, event=None):
        """Oculta o tooltip"""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


class ScrollFrameVertical(ttk.Frame):
    """Frame com scrollbar vertical"""
    
    def __init__(self, master, **kwargs):
        """Inicializa o frame com scrollbar"""
        super().__init__(master, **kwargs)
        
        # Criar canvas
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Criar scrollbar
        self.scrollbar = ttk.Scrollbar(
            self, orient=tk.VERTICAL, command=self.canvas.yview
        )
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configurar canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox('all')
        ))
        
        # Criar frame interno
        self.frame_interno = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame_interno, anchor='nw')
        
        # Configurar rolagem com mouse
        self.frame_interno.bind('<Enter>', self._bind_mouse)
        self.frame_interno.bind('<Leave>', self._unbind_mouse)
        
    def _bind_mouse(self, event=None):
        """Vincula eventos de mouse para rolagem"""
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
    def _unbind_mouse(self, event=None):
        """Remove vinculação de eventos de mouse"""
        self.canvas.unbind_all("<MouseWheel>")
        
    def _on_mousewheel(self, event):
        """Trata evento de rolagem do mouse"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


class BotaoIcone(ttk.Button):
    """Botão personalizado com ícone e texto"""
    
    def __init__(self, master=None, texto="", icone=None, comando=None, **kwargs):
        """Inicializa o botão com ícone"""
        super().__init__(master, text=texto, command=comando, **kwargs)


class Separador(ttk.Frame):
    """Componente de separador com título opcional"""
    
    def __init__(self, master=None, texto="", **kwargs):
        """Inicializa o separador personalizado"""
        super().__init__(master, **kwargs)
        
        # Configurações
        self.texto = texto
        
        # Criar frame para o separador
        self.frame_separador = ttk.Frame(self)
        self.frame_separador.pack(fill=tk.X, pady=5)
        
        # Se houver texto, criar um separador com texto
        if texto:
            # Separador esquerdo
            self.sep_esquerdo = ttk.Separator(self.frame_separador, orient=tk.HORIZONTAL)
            self.sep_esquerdo.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=5)
            
            # Texto
            self.label_texto = ttk.Label(self.frame_separador, text=f" {texto} ")
            self.label_texto.pack(side=tk.LEFT, padx=5)
            
            # Separador direito
            self.sep_direito = ttk.Separator(self.frame_separador, orient=tk.HORIZONTAL)
            self.sep_direito.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=5)
        else:
            # Separador simples
            self.separador = ttk.Separator(self.frame_separador, orient=tk.HORIZONTAL)
            self.separador.pack(fill=tk.X, expand=True, pady=5)