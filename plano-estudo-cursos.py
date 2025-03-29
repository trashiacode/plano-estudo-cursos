#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Plano de Estudo para Cursos
---------------------------

Este é o arquivo de lançamento para a aplicação Plano de Estudo para Cursos.
Ele importa e executa a função principal da aplicação.
"""

import os
import sys
import sqlite3

# Adicionar o diretório atual ao path do Python
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

def verificar_banco_dados():
    """Verifica e atualiza o banco de dados se necessário"""
    try:
        # Verificar se o banco de dados existe
        db_path = os.path.join(current_dir, "dados_cursos.db")
        
        # Se não existir, será criado automaticamente ao conectar
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se a tabela cursos existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cursos'")
        if not cursor.fetchone():
            # Criar tabela de cursos
            cursor.execute('''
                CREATE TABLE cursos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    caminho TEXT NOT NULL,
                    tempo_total TEXT,
                    data_inicio TEXT
                )
            ''')
        
        # Verificar se a tabela aulas existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='aulas'")
        if not cursor.fetchone():
            # Criar tabela de aulas
            cursor.execute('''
                CREATE TABLE aulas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    curso_id INTEGER,
                    caminho_video TEXT NOT NULL,
                    titulo TEXT NOT NULL,
                    duracao TEXT,
                    concluida INTEGER DEFAULT 0,
                    anotacoes TEXT,
                    data_conclusao TEXT,
                    FOREIGN KEY (curso_id) REFERENCES cursos(id)
                )
            ''')
        
        # Verificar se existe coluna anotacoes na tabela aulas
        cursor.execute("PRAGMA table_info(aulas)")
        colunas = [info[1] for info in cursor.fetchall()]
        
        if 'anotacoes' not in colunas:
            cursor.execute("ALTER TABLE aulas ADD COLUMN anotacoes TEXT")
        
        if 'data_conclusao' not in colunas:
            cursor.execute("ALTER TABLE aulas ADD COLUMN data_conclusao TEXT")
        
        # Commit e fechar conexão
        conn.commit()
        conn.close()
        
        print("Verificação e atualização do banco de dados concluídas com sucesso")
        return True
        
    except Exception as e:
        print(f"Erro ao verificar/atualizar banco de dados: {e}")
        return False

try:
    # Verificar banco de dados
    if not verificar_banco_dados():
        raise Exception("Falha na inicialização do banco de dados")
    
    # Tentar importar o módulo principal
    from src.main import main
    
    if __name__ == "__main__":
        # Executar a função principal
        main()
        
except Exception as e:
    # Caso haja erro na importação, exibir mensagem de erro
    import tkinter as tk
    from tkinter import messagebox
    
    print(f"Erro ao iniciar aplicação: {e}")
    
    # Criar uma janela temporária para exibir a mensagem de erro
    root = tk.Tk()
    root.withdraw()  # Esconder a janela principal
    
    # Exibir mensagem de erro
    messagebox.showerror(
        "Erro ao Iniciar Aplicação",
        f"Não foi possível iniciar a aplicação: {e}\n\n"
        "Verifique se a estrutura de diretórios está correta e se todas as "
        "dependências estão instaladas."
    )
    
    # Fechar a janela
    root.destroy()
    
    # Sair com código de erro
    sys.exit(1) 