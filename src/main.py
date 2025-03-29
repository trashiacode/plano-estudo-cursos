#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
import os
import sys

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.presentation.controllers import MainController

def main():
    """Função principal para iniciar a aplicação"""
    # Criar janela principal
    root = tk.Tk()
    
    # Configurar ícone (se disponível)
    try:
        icone_path = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
        if os.path.exists(icone_path):
            root.iconbitmap(icone_path)
    except Exception:
        pass
    
    # Inicializar controlador principal
    app = MainController(root)
    
    # Iniciar loop principal
    root.mainloop()

if __name__ == "__main__":
    main() 