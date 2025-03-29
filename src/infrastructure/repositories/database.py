import sqlite3
from pathlib import Path
from typing import Optional, List, Tuple, Any, Dict
import os

class Database:
    """Classe para gerenciar o banco de dados SQLite"""
    
    def __init__(self, db_path: str = "dados_cursos.db"):
        """Inicializa a conexão com o banco de dados"""
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(str(self.db_path))
        self.cursor = self.conn.cursor()
        self.inicializar_banco()
    
    def inicializar_banco(self):
        """Inicializa o banco de dados com as tabelas necessárias"""
        # Criar tabela de cursos
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cursos (
                id INTEGER PRIMARY KEY,
                nome TEXT,
                caminho TEXT UNIQUE,
                tempo_total TEXT,
                data_inicio TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Criar tabela de aulas
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS aulas (
                id INTEGER PRIMARY KEY,
                curso_id INTEGER,
                caminho_video TEXT UNIQUE,
                titulo TEXT,
                duracao TEXT,
                concluida INTEGER DEFAULT 0,
                anotacoes TEXT,
                data_conclusao TEXT,
                FOREIGN KEY (curso_id) REFERENCES cursos (id)
            )
        ''')
        
        # Verificar e adicionar colunas necessárias
        self.verificar_e_adicionar_colunas()
        
        self.conn.commit()
    
    def verificar_e_adicionar_colunas(self):
        """Verifica se as colunas necessárias existem e as adiciona se não existirem"""
        try:
            # Verificar coluna data_inicio na tabela cursos
            self.cursor.execute("PRAGMA table_info(cursos)")
            colunas_cursos = [info[1] for info in self.cursor.fetchall()]
            
            if 'data_inicio' not in colunas_cursos:
                print("Adicionando coluna data_inicio à tabela cursos")
                # Adicionar a coluna sem valor padrão
                self.cursor.execute('''
                    ALTER TABLE cursos
                    ADD COLUMN data_inicio TEXT
                ''')
                # Atualizar registros existentes com a data atual
                self.cursor.execute('''
                    UPDATE cursos
                    SET data_inicio = datetime('now')
                    WHERE data_inicio IS NULL
                ''')
            
            # Verificar coluna data_conclusao na tabela aulas
            self.cursor.execute("PRAGMA table_info(aulas)")
            colunas_aulas = [info[1] for info in self.cursor.fetchall()]
            
            if 'data_conclusao' not in colunas_aulas:
                print("Adicionando coluna data_conclusao à tabela aulas")
                self.cursor.execute('''
                    ALTER TABLE aulas
                    ADD COLUMN data_conclusao TEXT
                ''')
            
            self.conn.commit()
            print("Verificação e atualização do banco de dados concluídas com sucesso")
            
        except sqlite3.Error as e:
            print(f"Erro ao verificar ou adicionar colunas: {e}")
    
    def executar_query(self, query: str, params: Tuple = ()) -> Optional[List[Tuple[Any, ...]]]:
        """Executa uma query no banco de dados e retorna os resultados"""
        try:
            self.cursor.execute(query, params)
            
            # Verificar se é uma query SELECT
            if query.strip().upper().startswith("SELECT"):
                return self.cursor.fetchall()
            
            self.conn.commit()
            return None
        except sqlite3.Error as e:
            print(f"Erro ao executar query: {e}")
            print(f"Query: {query}")
            print(f"Parâmetros: {params}")
            return None
    
    def inserir_curso(self, nome: str, caminho: str) -> Optional[int]:
        """Insere um novo curso no banco de dados ou atualiza se já existir"""
        try:
            # Verificar se o curso já existe
            self.cursor.execute('''
                SELECT id FROM cursos WHERE caminho = ?
            ''', (caminho,))
            
            resultado = self.cursor.fetchone()
            
            if resultado:
                # Curso já existe, atualizar o nome
                curso_id = resultado[0]
                self.cursor.execute('''
                    UPDATE cursos SET nome = ? WHERE id = ?
                ''', (nome, curso_id))
                self.conn.commit()
                return curso_id
            else:
                # Curso não existe, inserir novo
                self.cursor.execute('''
                    INSERT INTO cursos (nome, caminho, tempo_total)
                    VALUES (?, ?, ?)
                ''', (nome, caminho, "0"))
                
                curso_id = self.cursor.lastrowid
                self.conn.commit()
                return curso_id
        
        except sqlite3.Error as e:
            print(f"Erro ao inserir/atualizar curso: {e}")
            return None
    
    def inserir_aula(self, curso_id: int, titulo: str, caminho_video: str, 
                    duracao: str, concluida: bool = False, anotacoes: str = "") -> Optional[int]:
        """Insere uma nova aula no banco de dados ou atualiza se já existir"""
        try:
            # Verificar se a aula já existe
            self.cursor.execute('''
                SELECT id, concluida, anotacoes FROM aulas
                WHERE curso_id = ? AND caminho_video = ?
            ''', (curso_id, caminho_video))
            
            resultado = self.cursor.fetchone()
            
            if resultado:
                # Aula já existe, atualizar informações mantendo status de conclusão e anotações
                aula_id, aula_concluida, aula_anotacoes = resultado
                
                self.cursor.execute('''
                    UPDATE aulas SET titulo = ?, duracao = ?
                    WHERE id = ?
                ''', (titulo, duracao, aula_id))
                
                self.conn.commit()
                return aula_id
            else:
                # Aula não existe, inserir nova
                self.cursor.execute('''
                    INSERT INTO aulas (curso_id, caminho_video, titulo, duracao, concluida, anotacoes)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (curso_id, caminho_video, titulo, duracao, 1 if concluida else 0, anotacoes))
                
                aula_id = self.cursor.lastrowid
                self.conn.commit()
                return aula_id
                
        except sqlite3.Error as e:
            print(f"Erro ao inserir/atualizar aula: {e}")
            return None
    
    def atualizar_conclusao_aula(self, aula_id: int, concluida: bool) -> bool:
        """Atualiza o status de conclusão de uma aula"""
        try:
            if concluida:
                self.cursor.execute('''
                    UPDATE aulas SET concluida = 1, data_conclusao = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (aula_id,))
            else:
                self.cursor.execute('''
                    UPDATE aulas SET concluida = 0, data_conclusao = NULL
                    WHERE id = ?
                ''', (aula_id,))
            
            self.conn.commit()
            return True
        
        except sqlite3.Error as e:
            print(f"Erro ao atualizar status de conclusão: {e}")
            return False
    
    def atualizar_anotacoes_aula(self, aula_id: int, anotacoes: str) -> bool:
        """Atualiza as anotações de uma aula"""
        try:
            self.cursor.execute('''
                UPDATE aulas SET anotacoes = ?
                WHERE id = ?
            ''', (anotacoes, aula_id))
            
            self.conn.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"Erro ao atualizar anotações: {e}")
            return False
    
    def atualizar_tempo_total_curso(self, curso_id: int, tempo_total: str) -> bool:
        """Atualiza o tempo total de um curso"""
        try:
            self.cursor.execute('''
                UPDATE cursos SET tempo_total = ?
                WHERE id = ?
            ''', (tempo_total, curso_id))
            
            self.conn.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"Erro ao atualizar tempo total: {e}")
            return False
    
    def obter_curso_por_caminho(self, caminho: str) -> Optional[Dict[str, Any]]:
        """Obtém um curso pelo caminho"""
        try:
            self.cursor.execute('''
                SELECT id, nome, caminho, tempo_total, data_inicio
                FROM cursos WHERE caminho = ?
            ''', (caminho,))
            
            resultado = self.cursor.fetchone()
            
            if not resultado:
                return None
                
            return {
                'id': resultado[0],
                'nome': resultado[1],
                'caminho': resultado[2],
                'tempo_total': resultado[3],
                'data_inicio': resultado[4]
            }
            
        except sqlite3.Error as e:
            print(f"Erro ao obter curso: {e}")
            return None
    
    def obter_aulas_por_curso(self, curso_id: int) -> List[Dict[str, Any]]:
        """Obtém todas as aulas de um curso"""
        try:
            self.cursor.execute('''
                SELECT id, titulo, caminho_video, duracao, concluida, anotacoes, data_conclusao
                FROM aulas WHERE curso_id = ?
            ''', (curso_id,))
            
            resultados = self.cursor.fetchall()
            
            aulas = []
            for resultado in resultados:
                aulas.append({
                    'id': resultado[0],
                    'titulo': resultado[1],
                    'caminho_video': resultado[2],
                    'duracao': resultado[3],
                    'concluida': bool(resultado[4]),
                    'anotacoes': resultado[5],
                    'data_conclusao': resultado[6]
                })
                
            return aulas
            
        except sqlite3.Error as e:
            print(f"Erro ao obter aulas: {e}")
            return []
    
    def obter_todos_cursos(self) -> List[Dict[str, Any]]:
        """Obtém todos os cursos cadastrados"""
        try:
            self.cursor.execute('''
                SELECT id, nome, caminho, tempo_total, data_inicio
                FROM cursos
                ORDER BY nome
            ''')
            
            resultados = self.cursor.fetchall()
            
            cursos = []
            for resultado in resultados:
                cursos.append({
                    'id': resultado[0],
                    'nome': resultado[1],
                    'caminho': resultado[2],
                    'tempo_total': resultado[3],
                    'data_inicio': resultado[4]
                })
                
            return cursos
            
        except sqlite3.Error as e:
            print(f"Erro ao obter cursos: {e}")
            return []
    
    def fechar_conexao(self):
        """Fecha a conexão com o banco de dados"""
        if self.conn:
            self.conn.close() 