from typing import List, Optional, Dict, Any, Callable, Tuple
import os
import subprocess
import platform
from datetime import timedelta, datetime

from src.domain.entities import Curso, Aula, Modulo
from src.domain.services import CursoService
from src.infrastructure.repositories import CursoRepository

class AppService:
    """Serviço de aplicação que coordena as operações do sistema"""
    
    def __init__(self):
        """Inicializa o serviço de aplicação"""
        self.curso_service = CursoService()
        self.repository = CursoRepository()
        self.curso_atual = None
        self.aula_selecionada = None
    
    def carregar_curso(self, caminho: str) -> Optional[Curso]:
        """Carrega um curso a partir de um caminho"""
        curso = self.repository.obter_curso_por_caminho(caminho)
        if curso:
            self.curso_atual = curso
        return curso
    
    def carregar_curso_por_id(self, id_curso: int) -> Optional[Curso]:
        """Carrega um curso a partir do ID"""
        curso = self.repository.obter_curso_por_id(id_curso)
        if curso:
            self.curso_atual = curso
        return curso
    
    def obter_cursos_salvos(self) -> List[Tuple[int, str, str]]:
        """Retorna a lista de cursos salvos"""
        return self.repository.listar_cursos()
    
    def listar_cursos(self) -> List[Dict[str, Any]]:
        """Lista todos os cursos disponíveis"""
        return self.curso_service.listar_cursos()
    
    def selecionar_aula(self, aula: Aula) -> None:
        """Seleciona uma aula para exibição"""
        self.aula_selecionada = aula
    
    def marcar_aula_como_concluida(self, aula: Aula, concluida: bool) -> bool:
        """Marca uma aula como concluída ou não concluída"""
        resultado = self.repository.atualizar_status_aula(aula, concluida)
        
        # Atualizar objeto da aula
        if resultado:
            aula.concluida = concluida
            
            if concluida:
                aula.data_conclusao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            else:
                aula.data_conclusao = None
        
        return resultado
    
    def salvar_anotacoes(self, anotacoes: str, aula: Aula) -> bool:
        """Salva as anotações de uma aula"""
        resultado = self.repository.atualizar_anotacoes_aula(aula, anotacoes)
        
        # Atualizar objeto da aula
        if resultado:
            aula.anotacoes = anotacoes
        
        return resultado
    
    def abrir_video(self, aula: Aula) -> bool:
        """Abre o vídeo de uma aula no player padrão do sistema"""
        try:
            # Verificar se o arquivo existe
            if not os.path.exists(aula.caminho_video):
                return False
            
            # Abrir o vídeo com o player padrão do sistema
            if os.name == 'nt':  # Windows
                os.startfile(aula.caminho_video)
            elif os.name == 'posix':  # Linux/Mac
                subprocess.Popen(['xdg-open', aula.caminho_video])
            else:
                return False
            
            return True
        except Exception:
            return False
    
    def obter_progresso_curso(self) -> float:
        """Retorna o progresso do curso atual em porcentagem"""
        if not self.curso_atual:
            return 0.0
        
        return self.curso_atual.progresso
    
    def obter_tempo_restante(self) -> str:
        """Retorna o tempo restante formatado"""
        if not self.curso_atual:
            return "00:00:00"
        
        return str(self.curso_atual.duracao_restante)
    
    def obter_estimativa_conclusao(self) -> str:
        """Calcula uma estimativa de conclusão com base no progresso atual"""
        if not self.curso_atual:
            return "Indeterminado"
        
        # Verificar se o curso está completo
        if self.curso_atual.progresso >= 100:
            return "Curso concluído!"
        
        # Obter total de aulas e aulas concluídas
        total_aulas = self.curso_atual.total_aulas
        aulas_concluidas = self.curso_atual.aulas_concluidas
        
        if total_aulas == 0 or aulas_concluidas == 0:
            return "Indeterminado"
        
        # Calcular dias decorridos desde o início
        try:
            data_inicio = datetime.strptime(
                self.curso_atual.data_inicio, 
                "%Y-%m-%d %H:%M:%S"
            )
        except (ValueError, TypeError):
            data_inicio = datetime.now()
        
        dias_decorridos = (datetime.now() - data_inicio).days
        if dias_decorridos <= 0:
            dias_decorridos = 1
        
        # Calcular ritmo (aulas por dia)
        ritmo = aulas_concluidas / dias_decorridos
        
        if ritmo <= 0:
            return "Indeterminado"
        
        # Estimar dias restantes
        aulas_restantes = total_aulas - aulas_concluidas
        dias_restantes = aulas_restantes / ritmo
        
        # Formatar mensagem
        if dias_restantes < 1:
            horas_restantes = dias_restantes * 24
            if horas_restantes < 1:
                minutos_restantes = horas_restantes * 60
                return f"{int(minutos_restantes)} minutos"
            return f"{int(horas_restantes)} horas"
        elif dias_restantes < 7:
            return f"{int(dias_restantes)} dias"
        elif dias_restantes < 30:
            semanas_restantes = dias_restantes / 7
            return f"{int(semanas_restantes)} semanas"
        else:
            meses_restantes = dias_restantes / 30
            return f"{int(meses_restantes)} meses"
    
    def obter_proximas_aulas(self, quantidade: int = 5) -> List[Aula]:
        """Obtém as próximas aulas não concluídas do curso atual"""
        if not self.curso_atual:
            return []
            
        return self.curso_service.obter_proximas_aulas(self.curso_atual, quantidade)
    
    def pesquisar_aulas(self, termo_pesquisa: str) -> List[Aula]:
        """Pesquisa aulas no curso atual"""
        if not self.curso_atual or not termo_pesquisa:
            return []
            
        return self.curso_service.pesquisar_aulas(self.curso_atual, termo_pesquisa)
    
    def exportar_dados_curso(self, arquivo: str, callback: Callable[[int], Any] = None) -> bool:
        """Exporta os dados do curso atual para um arquivo de texto"""
        if not self.curso_atual:
            return False
        
        try:
            with open(arquivo, 'w', encoding='utf-8') as f:
                curso = self.curso_atual
                
                # Cabeçalho
                f.write(f"PLANO DE ESTUDO: {curso.nome}\n")
                f.write(f"Total de tempo: {curso.duracao_total}\n")
                f.write(f"Progresso: {curso.progresso:.1f}%\n\n")
                
                # Processar cada módulo
                total_modulos = len(curso.modulos)
                for i, modulo in enumerate(curso.modulos):
                    # Reportar progresso
                    if callback:
                        progresso = int((i / total_modulos) * 100)
                        callback(progresso)
                    
                    f.write(f"MÓDULO: {modulo.nome}\n")
                    f.write(f"Tempo total: {modulo.duracao_total}\n\n")
                    
                    # Listar aulas do módulo
                    for aula in modulo.aulas:
                        status = "✓" if aula.concluida else " "
                        f.write(f"  [{status}] {aula.titulo_formatado} ({aula.duracao})\n")
                        
                        # Incluir anotações se existirem
                        if aula.anotacoes:
                            linhas_anotacoes = aula.anotacoes.split("\n")
                            for linha in linhas_anotacoes:
                                f.write(f"      {linha}\n")
                            f.write("\n")
                    
                    f.write("-" * 50 + "\n\n")
                
                # Reportar progresso final
                if callback:
                    callback(100)
                
            return True
        except Exception:
            return False
    
    def exportar_dados_curso_csv(self, arquivo: str, callback: Callable[[int], Any] = None) -> bool:
        """Exporta os dados do curso atual para um arquivo CSV"""
        if not self.curso_atual:
            return False
        
        try:
            import csv
            
            with open(arquivo, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                
                # Cabeçalho
                writer.writerow([
                    "Módulo", "Aula", "Status", "Duração", 
                    "Data de Conclusão", "Anotações"
                ])
                
                # Processar cada módulo
                total_aulas = self.curso_atual.total_aulas
                aulas_processadas = 0
                
                for modulo in self.curso_atual.modulos:
                    for aula in modulo.aulas:
                        # Preparar dados
                        status = "Concluída" if aula.concluida else "Pendente"
                        data_conclusao = aula.data_conclusao or ""
                        anotacoes = aula.anotacoes or ""
                        
                        # Escapar aspas em anotações
                        anotacoes = anotacoes.replace('"', '""')
                        
                        # Escrever linha
                        writer.writerow([
                            modulo.nome,
                            aula.titulo_formatado,
                            status,
                            aula.duracao,
                            data_conclusao,
                            anotacoes
                        ])
                        
                        # Reportar progresso
                        aulas_processadas += 1
                        if callback and total_aulas > 0:
                            progresso = int((aulas_processadas / total_aulas) * 100)
                            callback(progresso)
                
                # Reportar progresso final
                if callback:
                    callback(100)
                
            return True
        except Exception as e:
            print(f"Erro ao exportar CSV: {e}")
            return False
    
    def fechar(self):
        """Fecha as conexões e recursos do serviço"""
        if hasattr(self.curso_service, 'repository') and self.curso_service.repository:
            self.curso_service.repository.fechar()
        if self.repository:
            self.repository.fechar() 