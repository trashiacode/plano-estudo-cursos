from dataclasses import dataclass, field
from typing import List, Optional
from datetime import timedelta

from .aula import Aula

@dataclass
class Modulo:
    nome: str
    aulas: List[Aula] = field(default_factory=list)
    submodulos: List['Modulo'] = field(default_factory=list)
    id: Optional[int] = None
    
    @property
    def total_aulas(self) -> int:
        """Retorna o total de aulas, incluindo as dos submódulos"""
        count = len(self.aulas)
        for submodulo in self.submodulos:
            count += submodulo.total_aulas
        return count
    
    @property
    def aulas_concluidas(self) -> int:
        """Retorna o número de aulas concluídas, incluindo as dos submódulos"""
        count = sum(1 for aula in self.aulas if aula.concluida)
        for submodulo in self.submodulos:
            count += submodulo.aulas_concluidas
        return count
    
    @property
    def esta_completo(self) -> bool:
        """Verifica se todas as aulas do módulo estão concluídas"""
        if not self.aulas and not self.submodulos:
            return False
        
        # Verificar se todas as aulas estão concluídas
        if not all(aula.concluida for aula in self.aulas):
            return False
        
        # Verificar se todos os submódulos estão completos
        if not all(submodulo.esta_completo for submodulo in self.submodulos):
            return False
        
        return True
    
    @property
    def duracao_total(self) -> timedelta:
        """Calcula a duração total do módulo, incluindo submódulos"""
        total = timedelta()
        for aula in self.aulas:
            total += aula.duracao_timedelta
        
        for submodulo in self.submodulos:
            total += submodulo.duracao_total
        
        return total 