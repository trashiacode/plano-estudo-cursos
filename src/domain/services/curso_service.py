from typing import List, Optional, Dict, Any
import os
import re
from datetime import datetime, timedelta

from src.domain.entities import Curso, Modulo, Aula
from src.infrastructure.repositories import CursoRepository

class CursoService:
    """Serviço de domínio para operações relacionadas a cursos"""
    
    def __init__(self, repository: CursoRepository = None):
        """Inicializa o serviço com um repositório de cursos"""
        self.repository = repository if repository else CursoRepository()
    
    def carregar_curso(self, caminho: str) -> Optional[Curso]:
        """Carrega um curso a partir de um caminho"""
        # Verificar se o caminho existe
        if not os.path.exists(caminho):
            return None
            
        # Extrair o nome do curso a partir do último diretório
        nome_curso = os.path.basename(caminho)
        
        # Criar objeto Curso
        curso = Curso(nome=nome_curso, caminho=caminho)
        
        # Salvar no repositório para obter o ID
        curso_id = self.repository.salvar_curso(curso)
        
        if not curso_id:
            return None
            
        # Carregar curso completo do repositório
        return self.repository.carregar_curso_por_caminho(caminho)
    
    def listar_cursos(self) -> List[Dict[str, Any]]:
        """Lista todos os cursos disponíveis"""
        return self.repository.obter_todos_cursos()
    
    def marcar_aula_como_concluida(self, aula_id: int, concluida: bool = True) -> bool:
        """Marca uma aula como concluída ou não concluída"""
        return self.repository.atualizar_conclusao_aula(aula_id, concluida)
    
    def atualizar_anotacoes(self, aula_id: int, anotacoes: str) -> bool:
        """Atualiza as anotações de uma aula"""
        return self.repository.atualizar_anotacoes_aula(aula_id, anotacoes)
    
    def calcular_tempo_restante(self, curso: Curso) -> str:
        """Calcula o tempo restante para concluir o curso"""
        if not curso:
            return "00:00:00"
            
        tempo_restante = curso.duracao_restante
        
        if not tempo_restante:
            return "00:00:00"
            
        # Formatação amigável
        horas = int(tempo_restante.total_seconds() // 3600)
        minutos = int((tempo_restante.total_seconds() % 3600) // 60)
        segundos = int(tempo_restante.total_seconds() % 60)
        
        return f"{horas:02d}:{minutos:02d}:{segundos:02d}"
    
    def estimar_data_conclusao(self, curso: Curso, ritmo_diario: timedelta = None) -> str:
        """Estima a data de conclusão do curso com base no ritmo diário"""
        if not curso or curso.progresso >= 100:
            return "Curso concluído"
            
        # Usar ritmo padrão de 1 hora por dia se não especificado
        if not ritmo_diario:
            ritmo_diario = timedelta(hours=1)
            
        # Calcular dias restantes
        if curso.duracao_restante:
            dias_restantes = curso.calcular_estimativa_conclusao(ritmo_diario)
            
            if dias_restantes <= 0:
                return "Hoje"
                
            # Calcular data estimada
            data_estimada = datetime.now() + timedelta(days=dias_restantes)
            
            # Formatação amigável
            return data_estimada.strftime("%d/%m/%Y")
        
        return "Indeterminado"
    
    def obter_proximas_aulas(self, curso: Curso, quantidade: int = 5) -> List[Aula]:
        """Obtém as próximas aulas não concluídas do curso"""
        if not curso:
            return []
            
        # Obter todas as aulas não concluídas
        aulas_nao_concluidas = curso.obter_todas_aulas(apenas_nao_concluidas=True)
        
        # Ordenar por ordem alfabética (que geralmente segue a ordem numérica de lições)
        aulas_ordenadas = sorted(aulas_nao_concluidas, key=lambda a: a.titulo)
        
        # Retornar as primeiras N aulas
        return aulas_ordenadas[:quantidade]
    
    def pesquisar_aulas(self, curso: Curso, termo_pesquisa: str) -> List[Aula]:
        """Pesquisa aulas em um curso com base em um termo de pesquisa"""
        if not curso or not termo_pesquisa:
            return []
            
        termo_pesquisa = termo_pesquisa.lower()
        resultado = []
        
        # Função recursiva para encontrar aulas nos módulos
        def buscar_em_modulo(modulo):
            if hasattr(modulo, 'aulas') and modulo.aulas:
                for aula in modulo.aulas:
                    if termo_pesquisa in aula.titulo.lower():
                        resultado.append(aula)
            
            if hasattr(modulo, 'submodulos') and modulo.submodulos:
                for submodulo in modulo.submodulos:
                    buscar_em_modulo(submodulo)
        
        # Buscar em todos os módulos
        for modulo in curso.modulos:
            buscar_em_modulo(modulo)
            
        return resultado 