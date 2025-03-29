from dataclasses import dataclass
from datetime import timedelta
from typing import Optional

@dataclass
class Aula:
    titulo: str
    caminho_video: str
    duracao: str
    numero: str = ""
    concluida: bool = False
    anotacoes: str = ""
    data_conclusao: Optional[str] = None
    modulo_id: Optional[str] = None
    id: Optional[int] = None
    
    @property
    def titulo_formatado(self) -> str:
        """Retorna o título formatado com o número, se existir"""
        if self.numero:
            return f"{self.numero}. {self.titulo}"
        return self.titulo
    
    @property
    def duracao_timedelta(self) -> timedelta:
        """Converte a duração em string para um objeto timedelta"""
        try:
            if ':' in self.duracao:
                h, m, s = map(int, self.duracao.split(':'))
                return timedelta(hours=h, minutes=m, seconds=s)
            return timedelta(seconds=int(float(self.duracao)))
        except:
            return timedelta(seconds=0) 