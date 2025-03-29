import tkinter as tk
from tkinter import ttk, messagebox
import asyncio
import threading
import nest_asyncio

from src.application.services import TelegramService
from src.presentation.views import TelegramPanel

class TelegramController:
    """Controlador para gerenciar a integração com o Telegram"""
    
    def __init__(self, master):
        """Inicializa o controlador do Telegram"""
        self.master = master
        self.telegram_service = TelegramService()
        
        # Configurar loop assíncrono global e habilitar aninhamento
        # Isso permite que múltiplas operações assíncronas sejam executadas no mesmo loop
        self.main_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.main_loop)
        nest_asyncio.apply(self.main_loop)
        
        # Obter credenciais salvas, se existirem
        api_id, api_hash = self.telegram_service.get_credentials()
        
        # Criar painel do Telegram
        self.painel = TelegramPanel(
            master,
            on_configure_api=self.configure_api,
            on_list_channels=self.list_channels,
            on_download_channel=self.download_channel,
            api_id=api_id,
            api_hash=api_hash
        )
        # Empacotar o painel para preencher todo o espaço disponível
        self.painel.pack(fill=tk.BOTH, expand=True)
    
    def configure_api(self, api_id, api_hash):
        """Configura as credenciais da API do Telegram"""
        try:
            resultado = self.telegram_service.save_credentials(api_id, api_hash)
            return resultado
        except Exception as e:
            print(f"Erro ao configurar API: {e}")
            return False
    
    async def list_channels(self):
        """Lista os canais disponíveis no Telegram"""
        if not self.telegram_service.has_valid_credentials():
            raise Exception("Credenciais de API não configuradas ou inválidas.")
        
        try:
            canais = await self.telegram_service.list_channels()
            return canais
        except Exception as e:
            print(f"Erro ao listar canais: {e}")
            raise
    
    async def download_channel(self, channel_id, progress_callback=None):
        """Faz download de vídeos de um canal"""
        print(f"Método download_channel chamado para o canal: {channel_id}")
        
        # Verificar se estamos usando o loop correto
        current_loop = asyncio.get_running_loop()
        if current_loop != self.main_loop:
            print(f"AVISO: Loop atual ({id(current_loop)}) não é o loop principal ({id(self.main_loop)})")
        
        if not self.telegram_service.has_valid_credentials():
            print("Credenciais inválidas ou não configuradas")
            raise Exception("Credenciais de API não configuradas ou inválidas.")
        
        try:
            # Adaptar o callback para o formato esperado pelo serviço
            # O serviço espera um callback que recebe um dicionário de status,
            # mas a interface espera (current, total, text)
            adapter = None
            if progress_callback:
                print("Criando adaptador para callback de progresso")
                def adapter(status):
                    print(f"Callback de progresso chamado. Status: {status}")
                    current = status.get("baixados", 0) + status.get("ignorados", 0)
                    total = max(status.get("total", 1), 1)  # Evitar divisão por zero
                    text = f"Baixados: {status.get('baixados', 0)}, Ignorados: {status.get('ignorados', 0)}, Erros: {status.get('erros', 0)}"
                    progress_callback(current, total, text)
            
            print(f"Iniciando download_channel_videos para o canal: {channel_id}")
            resultado = await self.telegram_service.download_channel_videos(
                channel_id,
                adapter
            )
            print(f"Download concluído. Resultado: {resultado}")
            return resultado
        except Exception as e:
            print(f"Erro ao baixar vídeos: {e}")
            raise
    
    def run_async(self, coro_func, *args, callback=None):
        """
        Executa uma função corrotina usando o loop assíncrono compartilhado
        
        Args:
            coro_func: A função corrotina a ser executada
            *args: Argumentos para a função
            callback: Função de callback a ser chamada com o resultado
        """
        try:
            # Preparar função assíncrona com argumentos
            async def async_task():
                try:
                    result = await coro_func(*args)
                    if callback:
                        # Agendar callback na thread principal
                        self.master.after(0, lambda: callback(result))
                    return result
                except Exception as error:
                    # Capturar o erro no escopo local
                    error_msg = str(error)
                    if callback:
                        # Usar uma cópia local do erro para o callback
                        self.master.after(0, lambda: callback(None, error_msg))
                    raise
            
            # Executar a tarefa em uma thread separada
            threading.Thread(
                target=self._run_task_in_loop,
                args=(async_task,),
                daemon=True
            ).start()
            
        except Exception as error:
            # Capturar o erro no escopo local
            error_msg = str(error)
            print(f"Erro ao executar tarefa assíncrona: {error_msg}")
            if callback:
                callback(None, error_msg)
    
    def _run_task_in_loop(self, async_task):
        """
        Executa uma tarefa no loop principal
        
        Isso evita problemas de múltiplos loops que causam o erro 
        "Task got Future attached to a different loop"
        """
        try:
            # Usar o loop global
            return self.main_loop.run_until_complete(async_task())
        except Exception as e:
            print(f"Erro ao executar tarefa no loop: {e}")
            # Não re-levantar a exceção para evitar crashes na thread 