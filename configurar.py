#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de Configuração do Projeto
---------------------------------

Este script verifica as dependências necessárias, prepara o ambiente
e configura o aplicativo para primeiro uso.
"""

import os
import sys
import subprocess
import platform
import tkinter as tk
from tkinter import messagebox, ttk

def main():
    """Função principal de configuração"""
    # Criar janela de configuração
    root = tk.Tk()
    root.title("Configuração - Plano de Estudo para Cursos")
    root.geometry("500x400")
    root.minsize(500, 400)
    
    # Frame principal
    frame_principal = ttk.Frame(root, padding=20)
    frame_principal.pack(fill=tk.BOTH, expand=True)
    
    # Título
    ttk.Label(
        frame_principal, 
        text="Configuração do Plano de Estudo para Cursos",
        font=("Arial", 14, "bold")
    ).pack(pady=(0, 20))
    
    # Frame para mensagem de boas-vindas
    frame_boas_vindas = ttk.LabelFrame(frame_principal, text="Bem-vindo!")
    frame_boas_vindas.pack(fill=tk.X, pady=10)
    
    ttk.Label(
        frame_boas_vindas,
        text="Este assistente verificará e configurará seu ambiente para o aplicativo.",
        wraplength=400
    ).pack(padx=10, pady=10)
    
    # Frame para status
    frame_status = ttk.LabelFrame(frame_principal, text="Status da Configuração")
    frame_status.pack(fill=tk.BOTH, expand=True, pady=10)
    
    # Criar área de texto para logs
    txt_logs = tk.Text(frame_status, height=10, width=50)
    txt_logs.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Frame para botões
    frame_botoes = ttk.Frame(frame_principal)
    frame_botoes.pack(fill=tk.X, pady=10)
    
    # Botão para verificar dependências
    btn_verificar = ttk.Button(
        frame_botoes,
        text="Verificar Dependências",
        command=lambda: verificar_dependencias(txt_logs)
    )
    btn_verificar.pack(side=tk.LEFT, padx=5)
    
    # Botão para migrar dados
    btn_migrar = ttk.Button(
        frame_botoes,
        text="Migrar Dados",
        command=lambda: migrar_dados(txt_logs)
    )
    btn_migrar.pack(side=tk.LEFT, padx=5)
    
    # Botão para iniciar aplicativo
    btn_iniciar = ttk.Button(
        frame_botoes,
        text="Iniciar Aplicativo",
        command=lambda: iniciar_aplicativo(root)
    )
    btn_iniciar.pack(side=tk.LEFT, padx=5)
    
    # Botão para fechar
    btn_fechar = ttk.Button(
        frame_botoes,
        text="Fechar",
        command=root.destroy
    )
    btn_fechar.pack(side=tk.RIGHT, padx=5)
    
    # Centralizar janela
    centralizar_janela(root)
    
    # Iniciar verificação automática
    root.after(500, lambda: verificar_dependencias(txt_logs))
    
    # Iniciar loop principal
    root.mainloop()

def verificar_dependencias(txt_logs):
    """Verifica as dependências necessárias"""
    txt_logs.delete(1.0, tk.END)
    
    log("Iniciando verificação de dependências...", txt_logs)
    
    # Verificar Python
    python_versao = sys.version.split()[0]
    log(f"Python: versão {python_versao}", txt_logs)
    
    # Verificar Tkinter
    try:
        tk_versao = tk.TkVersion
        log(f"Tkinter: versão {tk_versao}", txt_logs)
    except:
        log("Tkinter: Não encontrado!", txt_logs, erro=True)
    
    # Verificar SQLite
    try:
        import sqlite3
        sqlite_versao = sqlite3.sqlite_version
        log(f"SQLite: versão {sqlite_versao}", txt_logs)
    except:
        log("SQLite: Não encontrado!", txt_logs, erro=True)
    
    # Verificar sistema operacional
    sistema = platform.system()
    log(f"Sistema Operacional: {sistema} {platform.release()}", txt_logs)
    
    # Verificar banco de dados
    if os.path.exists("dados_cursos.db"):
        log("Banco de dados encontrado", txt_logs)
    else:
        log("Banco de dados não encontrado. Será criado na primeira execução.", txt_logs)
    
    log("\nVerificação concluída!", txt_logs)

def migrar_dados(txt_logs):
    """Inicia o processo de migração de dados"""
    log("\nIniciando migração de dados...", txt_logs)
    
    # Verificar se o script de migração existe
    if not os.path.exists("migrar_dados.py"):
        log("Script de migração não encontrado!", txt_logs, erro=True)
        messagebox.showerror("Erro", "Script de migração não encontrado!")
        return
    
    try:
        # Executar script de migração
        resultado = subprocess.run(
            [sys.executable, "migrar_dados.py"],
            capture_output=True,
            text=True
        )
        
        # Verificar resultado
        if resultado.returncode == 0:
            log("Migração executada com sucesso!", txt_logs)
            log(resultado.stdout, txt_logs)
        else:
            log("Erro na migração!", txt_logs, erro=True)
            log(resultado.stderr, txt_logs, erro=True)
    
    except Exception as e:
        log(f"Erro ao executar migração: {e}", txt_logs, erro=True)
        messagebox.showerror("Erro", f"Erro ao executar migração: {e}")

def iniciar_aplicativo(root):
    """Inicia o aplicativo principal"""
    try:
        # Fechar janela de configuração
        root.destroy()
        
        # Executar aplicativo
        subprocess.Popen([sys.executable, "plano-estudo-cursos.py"])
        
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao iniciar aplicativo: {e}")

def log(mensagem, txt_logs, erro=False):
    """Adiciona uma mensagem ao log"""
    txt_logs.configure(state=tk.NORMAL)
    
    if erro:
        txt_logs.insert(tk.END, f"ERRO: {mensagem}\n", "erro")
        txt_logs.tag_configure("erro", foreground="red")
    else:
        txt_logs.insert(tk.END, f"{mensagem}\n")
    
    txt_logs.see(tk.END)
    txt_logs.configure(state=tk.DISABLED)
    txt_logs.update()

def centralizar_janela(janela):
    """Centraliza uma janela na tela"""
    janela.update_idletasks()
    
    largura = janela.winfo_width()
    altura = janela.winfo_height()
    
    pos_x = (janela.winfo_screenwidth() // 2) - (largura // 2)
    pos_y = (janela.winfo_screenheight() // 2) - (altura // 2)
    
    janela.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

if __name__ == "__main__":
    main() 