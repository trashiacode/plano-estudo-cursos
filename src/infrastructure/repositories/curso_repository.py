from typing import List, Optional, Dict, Any, Tuple
import os
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3

from .database import Database
from src.domain.entities import Curso, Modulo, Aula

class CursoRepository:
    """Repositório para operações relacionadas a cursos"""
    
    def __init__(self, db_path: str = None):
        """Inicializa o repositório com conexão ao banco de dados"""
        if db_path is None:
            db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "dados_cursos.db")
        
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        
        # Inicializar banco de dados
        self._inicializar_tabelas()
    
    def _inicializar_tabelas(self):
        """Inicializa as tabelas do banco de dados"""
        # Tabela de cursos
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cursos (
                id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL,
                caminho TEXT UNIQUE NOT NULL,
                tempo_total TEXT,
                data_inicio TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de aulas
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS aulas (
                id INTEGER PRIMARY KEY,
                curso_id INTEGER NOT NULL,
                caminho_video TEXT NOT NULL,
                titulo TEXT NOT NULL,
                duracao TEXT,
                concluida INTEGER DEFAULT 0,
                anotacoes TEXT,
                data_conclusao TEXT,
                FOREIGN KEY (curso_id) REFERENCES cursos (id)
            )
        ''')
        
        # Verificar e adicionar colunas necessárias
        self._verificar_e_adicionar_colunas()
        
        self.conn.commit()
    
    def _verificar_e_adicionar_colunas(self):
        """Verifica e adiciona colunas que podem estar faltando"""
        # Verificar coluna data_inicio na tabela cursos
        self.cursor.execute("PRAGMA table_info(cursos)")
        colunas_cursos = [info[1] for info in self.cursor.fetchall()]
        
        if 'data_inicio' not in colunas_cursos:
            print("Adicionando coluna data_inicio à tabela cursos")
            self.cursor.execute('ALTER TABLE cursos ADD COLUMN data_inicio TEXT')
            self.cursor.execute(
                'UPDATE cursos SET data_inicio = datetime("now") WHERE data_inicio IS NULL'
            )
        
        # Verificar coluna data_conclusao na tabela aulas
        self.cursor.execute("PRAGMA table_info(aulas)")
        colunas_aulas = [info[1] for info in self.cursor.fetchall()]
        
        if 'data_conclusao' not in colunas_aulas:
            print("Adicionando coluna data_conclusao à tabela aulas")
            self.cursor.execute('ALTER TABLE aulas ADD COLUMN data_conclusao TEXT')
        
        if 'anotacoes' not in colunas_aulas:
            print("Adicionando coluna anotacoes à tabela aulas")
            self.cursor.execute('ALTER TABLE aulas ADD COLUMN anotacoes TEXT')
        
        self.conn.commit()
    
    def listar_cursos(self) -> List[Tuple[int, str, str]]:
        """Lista todos os cursos salvos"""
        try:
            self.cursor.execute(
                'SELECT id, nome, caminho FROM cursos ORDER BY nome'
            )
            return [(row[0], row[1], row[2]) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Erro ao listar cursos: {e}")
            return []
    
    def obter_curso_por_id(self, id_curso: int) -> Optional[Curso]:
        """Obtém um curso pelo ID"""
        try:
            # Buscar dados do curso
            self.cursor.execute(
                'SELECT id, nome, caminho, tempo_total, data_inicio FROM cursos WHERE id = ?',
                (id_curso,)
            )
            
            curso_row = self.cursor.fetchone()
            if not curso_row:
                return None
            
            curso_dict = dict(curso_row)
            
            # Criar objeto Curso
            curso = Curso(
                nome=curso_dict['nome'],
                caminho=curso_dict['caminho'],
                modulos=[],
                id=curso_dict['id'],
                data_inicio=curso_dict['data_inicio']
            )
            
            # Carregar aulas do curso
            self._carregar_aulas_do_curso(curso)
            
            return curso
            
        except sqlite3.Error as e:
            print(f"Erro ao obter curso por ID: {e}")
            return None
    
    def obter_curso_por_caminho(self, caminho: str) -> Optional[Curso]:
        """Obtém um curso pelo caminho"""
        try:
            # Normalizar caminho para comparação
            caminho_normalizado = os.path.normpath(caminho)
            
            # Buscar dados do curso
            self.cursor.execute(
                'SELECT id, nome, caminho, tempo_total, data_inicio FROM cursos WHERE caminho = ?',
                (caminho_normalizado,)
            )
            
            curso_row = self.cursor.fetchone()
            if not curso_row:
                # Se não encontrar, tentar criar novo curso
                return self._criar_novo_curso(caminho_normalizado)
            
            curso_dict = dict(curso_row)
            
            # Criar objeto Curso
            curso = Curso(
                nome=curso_dict['nome'],
                caminho=curso_dict['caminho'],
                modulos=[],
                id=curso_dict['id'],
                data_inicio=curso_dict['data_inicio']
            )
            
            # Carregar aulas do curso
            self._carregar_aulas_do_curso(curso)
            
            return curso
            
        except sqlite3.Error as e:
            print(f"Erro ao obter curso por caminho: {e}")
            return None
    
    def _criar_novo_curso(self, caminho: str) -> Optional[Curso]:
        """Cria um novo curso a partir do caminho fornecido"""
        try:
            # Verificar se é um diretório válido
            if not os.path.isdir(caminho):
                return None
            
            # Obter nome do curso a partir do diretório
            nome_curso = os.path.basename(caminho)
            
            # Inserir curso no banco
            self.cursor.execute(
                'INSERT INTO cursos (nome, caminho, data_inicio) VALUES (?, ?, datetime("now"))',
                (nome_curso, caminho)
            )
            
            id_curso = self.cursor.lastrowid
            self.conn.commit()
            
            # Criar objeto Curso
            curso = Curso(
                nome=nome_curso,
                caminho=caminho,
                modulos=[],
                id=id_curso,
                data_inicio=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
            # Analisar arquivos de vídeo e criar estrutura
            self._analisar_estrutura_curso(curso)
            
            return curso
            
        except sqlite3.Error as e:
            print(f"Erro ao criar novo curso: {e}")
            return None
    
    def _analisar_estrutura_curso(self, curso: Curso):
        """Analisa a estrutura de arquivos do curso e cria os módulos e aulas"""
        try:
            import re
            
            # Lista de extensões de vídeo comuns
            extensoes_video = ['.mp4', '.avi', '.mkv', '.mov', '.wmv']
            
            # Módulo raiz para vídeos na pasta principal
            modulo_raiz = None
            
            # Percorrer diretórios
            for raiz, dirs, arquivos in os.walk(curso.caminho):
                # Ignorar diretórios ocultos
                if os.path.basename(raiz).startswith('.'):
                    continue
                
                # Determinar se estamos na raiz ou em um subdiretório
                caminho_relativo = os.path.relpath(raiz, curso.caminho)
                
                # Processar vídeos na pasta
                videos = []
                for arquivo in arquivos:
                    if any(arquivo.lower().endswith(ext) for ext in extensoes_video):
                        caminho_completo = os.path.join(raiz, arquivo)
                        
                        # Tentar extrair número e título
                        padrao = r'^(\d+)[\s.-]+(.+)\.(?:mp4|avi|mkv|mov|wmv)$'
                        match = re.match(padrao, arquivo, re.IGNORECASE)
                        
                        if match:
                            numero = match.group(1)
                            titulo = match.group(2)
                        else:
                            numero = ""
                            titulo = os.path.splitext(arquivo)[0]
                        
                        # Obter duração (simplificado)
                        duracao = "00:00:00"  # Seria necessário um método para extrair duração real
                        
                        # Salvar aula no banco
                        titulo_formatado = f"{numero}. {titulo}" if numero else titulo
                        
                        self.cursor.execute(
                            '''
                            INSERT OR IGNORE INTO aulas 
                            (curso_id, caminho_video, titulo, duracao, concluida) 
                            VALUES (?, ?, ?, ?, 0)
                            ''',
                            (curso.id, caminho_completo, titulo_formatado, duracao)
                        )
                        
                        # Adicionar à lista de vídeos
                        videos.append({
                            "numero": numero,
                            "titulo": titulo,
                            "caminho_video": caminho_completo,
                            "duracao": duracao
                        })
                
                # Se temos vídeos neste diretório
                if videos:
                    if caminho_relativo == '.':
                        # Estamos na raiz
                        if not modulo_raiz:
                            modulo_raiz = Modulo(nome="(Raiz)", aulas=[], id=None)
                            curso.modulos.append(modulo_raiz)
                        
                        # Adicionar aulas ao módulo raiz
                        for video in videos:
                            aula = Aula(
                                titulo=video["titulo"],
                                caminho_video=video["caminho_video"],
                                duracao=video["duracao"],
                                numero=video["numero"],
                                concluida=False
                            )
                            modulo_raiz.aulas.append(aula)
                    
                    elif '/' not in caminho_relativo and '\\' not in caminho_relativo:
                        # É um módulo direto
                        modulo = Modulo(nome=os.path.basename(raiz), aulas=[], id=None)
                        
                        # Adicionar aulas ao módulo
                        for video in videos:
                            aula = Aula(
                                titulo=video["titulo"],
                                caminho_video=video["caminho_video"],
                                duracao=video["duracao"],
                                numero=video["numero"],
                                concluida=False
                            )
                            modulo.aulas.append(aula)
                        
                        # Adicionar módulo ao curso
                        curso.modulos.append(modulo)
            
            # Commit das alterações
            self.conn.commit()
            
        except Exception as e:
            print(f"Erro ao analisar estrutura do curso: {e}")
    
    def _carregar_aulas_do_curso(self, curso: Curso):
        """Carrega as aulas de um curso agrupadas por módulos"""
        try:
            # Carregar todas as aulas do curso
            self.cursor.execute(
                '''
                SELECT id, caminho_video, titulo, duracao, concluida, anotacoes, data_conclusao
                FROM aulas
                WHERE curso_id = ?
                ORDER BY caminho_video
                ''',
                (curso.id,)
            )
            
            aulas_rows = self.cursor.fetchall()
            
            # Estrutura para agrupar aulas por diretório
            aulas_por_diretorio = {}
            
            for aula_row in aulas_rows:
                aula_dict = dict(aula_row)
                
                # Extrair diretório da aula
                caminho_video = aula_dict['caminho_video']
                diretorio = os.path.dirname(caminho_video)
                
                # Verificar se é pasta raiz
                if diretorio == curso.caminho:
                    diretorio = "(Raiz)"
                else:
                    # Pegar apenas o nome do diretório
                    diretorio = os.path.basename(diretorio)
                
                # Adicionar ao dicionário
                if diretorio not in aulas_por_diretorio:
                    aulas_por_diretorio[diretorio] = []
                
                # Extrair número e título da aula
                titulo_completo = aula_dict['titulo']
                partes = titulo_completo.split(". ", 1)
                
                if len(partes) > 1 and partes[0].isdigit():
                    numero = partes[0]
                    titulo = partes[1]
                else:
                    numero = ""
                    titulo = titulo_completo
                
                # Criar objeto Aula
                aula = Aula(
                    id=aula_dict['id'],
                    titulo=titulo,
                    caminho_video=caminho_video,
                    duracao=aula_dict['duracao'],
                    numero=numero,
                    concluida=bool(aula_dict['concluida']),
                    anotacoes=aula_dict['anotacoes'],
                    data_conclusao=aula_dict['data_conclusao']
                )
                
                aulas_por_diretorio[diretorio].append(aula)
            
            # Criar módulos a partir dos diretórios
            for nome_diretorio, aulas in aulas_por_diretorio.items():
                # Ordenar aulas por número
                aulas.sort(key=lambda a: int(a.numero) if a.numero and a.numero.isdigit() else float('inf'))
                
                # Criar módulo
                modulo = Modulo(nome=nome_diretorio, aulas=aulas, id=None)
                curso.modulos.append(modulo)
            
            # Ordenar módulos (colocando "(Raiz)" primeiro)
            curso.modulos.sort(key=lambda m: (m.nome != "(Raiz)", m.nome))
            
        except sqlite3.Error as e:
            print(f"Erro ao carregar aulas do curso: {e}")
    
    def atualizar_status_aula(self, aula: Aula, concluida: bool) -> bool:
        """Atualiza o status de conclusão de uma aula"""
        try:
            if concluida:
                # Marcar como concluída com data atual
                self.cursor.execute(
                    '''
                    UPDATE aulas 
                    SET concluida = 1, data_conclusao = datetime('now')
                    WHERE id = ?
                    ''',
                    (aula.id,)
                )
            else:
                # Desmarcar como concluída
                self.cursor.execute(
                    '''
                    UPDATE aulas 
                    SET concluida = 0, data_conclusao = NULL
                    WHERE id = ?
                    ''',
                    (aula.id,)
                )
            
            self.conn.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"Erro ao atualizar status da aula: {e}")
            return False
    
    def atualizar_anotacoes_aula(self, aula: Aula, anotacoes: str) -> bool:
        """Atualiza as anotações de uma aula"""
        try:
            self.cursor.execute(
                'UPDATE aulas SET anotacoes = ? WHERE id = ?',
                (anotacoes, aula.id)
            )
            
            self.conn.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"Erro ao atualizar anotações da aula: {e}")
            return False
    
    def fechar(self):
        """Fecha a conexão com o banco de dados"""
        if self.conn:
            self.conn.close() 