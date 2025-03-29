from dataclasses import dataclass, field
from typing import List, Optional
from datetime import timedelta, datetime

from .modulo import Modulo
from .aula import Aula

@dataclass
class Curso:
    nome: str
    caminho: str
    modulos: List[Modulo] = field(default_factory=list)
    id: Optional[int] = None
    data_inicio: Optional[str] = None
    
    @property
    def total_aulas(self) -> int:
        """Retorna o número total de aulas no curso"""
        return sum(modulo.total_aulas for modulo in self.modulos)
    
    @property
    def aulas_concluidas(self) -> int:
        """Retorna o número de aulas concluídas no curso"""
        return sum(modulo.aulas_concluidas for modulo in self.modulos)
    
    @property
    def progresso(self) -> float:
        """Retorna o progresso do curso em porcentagem"""
        if self.total_aulas == 0:
            return 0.0
        return (self.aulas_concluidas / self.total_aulas) * 100
    
    @property
    def duracao_total(self) -> timedelta:
        """Calcula a duração total do curso"""
        return sum((modulo.duracao_total for modulo in self.modulos), timedelta())
    
    @property
    def duracao_restante(self) -> timedelta:
        """Calcula a duração restante do curso"""
        total = timedelta()
        
        # Coletar todas as aulas não concluídas
        aulas_nao_concluidas = self.obter_todas_aulas(apenas_nao_concluidas=True)
        
        for aula in aulas_nao_concluidas:
            total += aula.duracao_timedelta
            
        return total
    
    def obter_todas_aulas(self, apenas_nao_concluidas=False) -> List[Aula]:
        """Retorna todas as aulas do curso, opcionalmente apenas as não concluídas"""
        todas_aulas = []
        
        def coletar_aulas(modulo):
            for aula in modulo.aulas:
                if not apenas_nao_concluidas or not aula.concluida:
                    todas_aulas.append(aula)
            
            for submodulo in modulo.submodulos:
                coletar_aulas(submodulo)
        
        for modulo in self.modulos:
            coletar_aulas(modulo)
            
        return todas_aulas
    
    def calcular_estimativa_conclusao(self) -> Optional[int]:
        """Calcula a estimativa de dias para concluir o curso"""
        if not self.data_inicio or self.aulas_concluidas == 0:
            return None
            
        try:
            # Converter a data de início para datetime
            data_inicio_dt = datetime.strptime(self.data_inicio, "%Y-%m-%d %H:%M:%S")
            
            # Obter a data da última aula concluída
            aulas = self.obter_todas_aulas()
            aulas_concluidas = [aula for aula in aulas if aula.concluida and aula.data_conclusao]
            
            if not aulas_concluidas:
                return None
                
            # Encontrar a data mais recente de conclusão
            ultima_aula = max(aulas_concluidas, key=lambda a: datetime.strptime(a.data_conclusao, "%Y-%m-%d %H:%M:%S"))
            ultima_conclusao_dt = datetime.strptime(ultima_aula.data_conclusao, "%Y-%m-%d %H:%M:%S")
            
            # Calcular dias desde o início
            dias_decorridos = (ultima_conclusao_dt - data_inicio_dt).days + 1  # Evitar divisão por zero
            if dias_decorridos <= 0:
                dias_decorridos = 1
                
            # Calcular ritmo (aulas por dia)
            ritmo = self.aulas_concluidas / dias_decorridos
            
            if ritmo <= 0:
                return None
                
            # Estimar dias restantes
            aulas_restantes = self.total_aulas - self.aulas_concluidas
            dias_restantes = aulas_restantes / ritmo
            
            return int(dias_restantes)
            
        except (ValueError, TypeError):
            return None 