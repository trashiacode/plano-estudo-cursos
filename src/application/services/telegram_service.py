import os
import configparser
import json
import asyncio
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
from pyrogram import Client
from pyrogram.errors import RPCError

try:
    from pyrogram.types import Chat, Message
    from pyrogram.enums import ChatType
    PYROGRAM_AVAILABLE = True
except ImportError:
    PYROGRAM_AVAILABLE = False

class TelegramService:
    """Serviço para gerenciar conexão e downloads do Telegram"""
    
    # Arquivo de configuração salvo na pasta do usuário para maior segurança
    CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".plano_estudo_telegram.json")
    
    def __init__(self):
        """Inicializa o serviço de Telegram"""
        self.app = None
        self.client_ready = False
        self.config_path = 'config.ini'
        self.session_name = 'plano_estudos_session'
        self.download_dir = 'downloads'
        self.api_id = None
        self.api_hash = None
        
        # Criar diretório de downloads se não existir
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
            
        # Verificar se a biblioteca está disponível
        if not PYROGRAM_AVAILABLE:
            print("A biblioteca Pyrogram não está instalada. Use 'pip install pyrogram' para instalar.")
            return
            
        # Inicializar cliente quando possível
        self._inicializar_cliente()
        
        # Carregar credenciais
        self._load_credentials()
        
    def _inicializar_cliente(self) -> bool:
        """Inicializa o cliente do Telegram se as credenciais estiverem disponíveis"""
        if not PYROGRAM_AVAILABLE:
            return False
            
        try:
            # Verificar se o arquivo config.ini existe
            if not os.path.exists(self.config_path):
                return False
                
            # Ler API_ID e API_HASH do config.ini
            config = configparser.ConfigParser()
            config.read(self.config_path)
            
            if not config.has_section('pyrogram') or not config.has_option('pyrogram', 'api_id') or not config.has_option('pyrogram', 'api_hash'):
                return False
                
            self.api_id = config.get("pyrogram", "api_id")
            self.api_hash = config.get("pyrogram", "api_hash")
            
            # Criar cliente Pyrogram
            self.app = Client(self.session_name, api_id=self.api_id, api_hash=self.api_hash)
            self.client_ready = True
            return True
        except Exception as e:
            print(f"Erro ao inicializar cliente Telegram: {e}")
            return False
            
    def has_valid_credentials(self) -> bool:
        """Verifica se o serviço possui credenciais válidas configuradas"""
        return self.client_ready
        
    def save_credentials(self, api_id: str, api_hash: str) -> bool:
        """Salva as credenciais de API no arquivo de configuração"""
        try:
            # Validar credenciais
            if not api_id or not api_hash:
                return False
                
            # Atualizar valores em memória
            self.api_id = api_id
            self.api_hash = api_hash
            
            # Salvar no arquivo de configuração
            config = {
                'api_id': api_id,
                'api_hash': api_hash
            }
            
            # Garantir que o diretório de configuração exista
            os.makedirs(os.path.dirname(self.CONFIG_FILE), exist_ok=True)
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(config, f)
                
            # Reinicializar cliente
            self._inicializar_cliente()
            return True
        except Exception as e:
            print(f"Erro ao salvar credenciais: {e}")
            return False
            
    async def list_channels(self) -> List[Dict[str, Any]]:
        """Lista todos os canais e grupos disponíveis"""
        if not self.client_ready:
            return []
            
        channels = []
        try:
            # Verificar se o cliente já está conectado
            is_connected = getattr(self.app, "is_connected", False)
            
            if is_connected:
                # Se já está conectado, usar diretamente
                async for dialog in self.app.get_dialogs():
                    chat = dialog.chat
                    if chat.type in (ChatType.CHANNEL, ChatType.SUPERGROUP):
                        channels.append({
                            'id': chat.id,
                            'title': chat.title,
                            'type': str(chat.type),
                            'members_count': getattr(chat, 'members_count', 0)
                        })
            else:
                # Se não está conectado, usar o contexto async with
                async with self.app:
                    async for dialog in self.app.get_dialogs():
                        chat = dialog.chat
                        if chat.type in (ChatType.CHANNEL, ChatType.SUPERGROUP):
                            channels.append({
                                'id': chat.id,
                                'title': chat.title,
                                'type': str(chat.type),
                                'members_count': getattr(chat, 'members_count', 0)
                            })
        except Exception as e:
            print(f"Erro ao listar canais: {e}")
            
        return channels
        
    async def download_channel_videos(self, channel_id, progress_callback=None):
        """
        Faz download de todos os vídeos de um canal específico
        
        Args:
            channel_id: ID do canal
            progress_callback: Função de callback para reportar progresso
        
        Returns:
            dict: Resultados do download
        """
        print(f"TelegramService.download_channel_videos iniciando para canal {channel_id}")
        if not self.has_valid_credentials():
            print("Credenciais inválidas")
            raise ValueError("Credenciais de API não configuradas. Configure suas credenciais em 'Telegram > Configurar API'")
            
        # Verificar se o cliente já está conectado
        is_connected = getattr(self.app, "is_connected", False)
        print(f"Cliente já está conectado? {is_connected}")
        
        download_path = os.path.join(os.path.expanduser("~"), "Downloads", "TelegramVideos")
        os.makedirs(download_path, exist_ok=True)
        print(f"Usando pasta de download: {download_path}")
        
        status = {
            "total": 0,
            "baixados": 0,
            "ignorados": 0,
            "erros": 0,
            "arquivos": []
        }
        
        try:
            print("Obtendo cliente Telegram")
            client = self._get_client()
            
            # Função para processar as mensagens
            async def process_messages():
                print("Iniciando processamento de mensagens")
                # Contar mensagens com mídia
                count = 0
                print("Contando mensagens com vídeo")
                async for message in client.get_chat_history(channel_id):
                    if message.video:
                        count += 1
                
                status["total"] = count
                print(f"Total de vídeos encontrados: {count}")
                if progress_callback:
                    print("Chamando callback de progresso inicial")
                    progress_callback(status)
                
                # Processar e baixar
                print("Iniciando download dos vídeos")
                async for message in client.get_chat_history(channel_id):
                    if message.video:
                        video = message.video
                        file_name = f"{message.date.strftime('%Y%m%d')}_{video.file_name or f'video_{video.file_id[-10:]}.mp4'}"
                        file_path = os.path.join(download_path, file_name)
                        print(f"Processando vídeo: {file_name}")
                        
                        if os.path.exists(file_path):
                            print(f"Vídeo já existe, ignorando: {file_path}")
                            status["ignorados"] += 1
                        else:
                            try:
                                print(f"Baixando vídeo para: {file_path}")
                                await client.download_media(
                                    message, 
                                    file_name=file_path
                                )
                                print(f"Download concluído: {file_path}")
                                status["baixados"] += 1
                                status["arquivos"].append(file_path)
                            except Exception as e:
                                print(f"Erro ao baixar vídeo: {e}")
                                status["erros"] += 1
                        
                        if progress_callback:
                            print("Atualizando progresso")
                            progress_callback(status)
                
                print(f"Processamento concluído. Status final: {status}")
            
            # Executar de acordo com o estado de conexão
            if is_connected:
                print("Executando com cliente já conectado")
                await process_messages()
                return status
            else:
                print("Conectando cliente com context manager")
                async with client:
                    await process_messages()
                    return status
                
        except RPCError as e:
            print(f"Erro do Telegram: {e}")
            raise
        except Exception as e:
            print(f"Erro ao baixar vídeos: {e}")
            raise
    
    async def _download_messages_range(
        self, channel_id: int, channel_dir: str, 
        start_id: int, end_id: int, 
        processed_media_groups: Set[str], control_data: Dict[str, Any],
        progress_callback=None
    ):
        """Faz download de mensagens em um intervalo específico"""
        total_range = start_id - end_id
        current = 0
        
        message_id = start_id
        async with self.app:
            while message_id > end_id:
                # Atualizar progresso
                if progress_callback and total_range > 0:
                    current += 1
                    progress_percent = min(int((current / total_range) * 100), 100)
                    progress_callback(progress_percent, 100, f"Mensagem {message_id}/{start_id}")
                
                try:
                    message = await self.app.get_messages(channel_id, message_ids=message_id)
                    
                    if not message.empty and message.media:
                        if message.media_group_id:
                            # Mensagem faz parte de um grupo de mídia
                            if message.media_group_id not in processed_media_groups:
                                # Criar pasta para o grupo de mídia
                                group_dir = os.path.join(channel_dir, f"media_group_{message.media_group_id}")
                                if not os.path.exists(group_dir):
                                    os.makedirs(group_dir)
                                
                                # Baixar grupo de mídia
                                media_group = await self.app.get_media_group(channel_id, message.id)
                                download_success = True
                                
                                for msg in media_group:
                                    success = await self._download_media(msg, group_dir)
                                    if not success:
                                        download_success = False
                                        break
                                
                                if download_success:
                                    processed_media_groups.add(message.media_group_id)
                                    control_data["processed_media_groups"] = list(processed_media_groups)
                                    control_data["last_message_id"] = message_id
                                    self._save_control_file(channel_id, control_data)
                        else:
                            # Mensagem de mídia única
                            success = await self._download_media(message, channel_dir)
                            if success:
                                control_data["last_message_id"] = message_id
                                self._save_control_file(channel_id, control_data)
                
                except errors.FloodWait as e:
                    if progress_callback:
                        progress_callback(0, 100, f"Aguardando {e.value} segundos (limite de requisições)...")
                    await asyncio.sleep(e.value)
                    continue
                except Exception as e:
                    print(f"Erro ao processar mensagem {message_id}: {e}")
                
                message_id -= 1
    
    async def _download_media(self, message: Message, folder: str) -> bool:
        """Faz download de uma mídia específica"""
        try:
            extension = self._get_media_extension(message)
            if not extension:
                return False  # Não é uma mídia suportada
            
            # Obter nome do arquivo
            if message.caption:
                filename = message.caption
            elif message.text:
                filename = message.text
            else:
                filename = f"msg_{message.id}"
            
            # Sanitizar nome do arquivo
            filename = self._sanitize_filename(filename)
            file_path = os.path.join(folder, f"{filename}{extension}")
            
            # Verificar se o arquivo já existe
            base_path = file_path
            counter = 1
            while os.path.exists(file_path):
                name, ext = os.path.splitext(base_path)
                file_path = f"{name}_{counter}{ext}"
                counter += 1
            
            # Fazer download
            await message.download(file_name=file_path)
            print(f"Baixou mídia: {os.path.basename(file_path)}")
            
            # Aguardar para evitar limites de requisição
            await asyncio.sleep(1)
            return True
        
        except errors.FloodWait as e:
            print(f"Aguardando {e.value} segundos (limite de requisições)...")
            await asyncio.sleep(e.value)
            return False
        except Exception as e:
            print(f"Erro ao baixar mídia: {e}")
            return False
    
    async def _get_last_message_id(self, chat_id: int) -> int:
        """Obtém o ID da última mensagem do chat"""
        try:
            last_message = None
            async for message in self.app.get_chat_history(chat_id, limit=1):
                last_message = message
            
            if last_message:
                return last_message.id
            return 0
        except errors.FloodWait as e:
            print(f"Aguardando {e.value} segundos (limite de requisições)...")
            await asyncio.sleep(e.value)
            return await self._get_last_message_id(chat_id)
        except Exception as e:
            print(f"Erro ao obter última mensagem: {e}")
            return 0
    
    def _load_control_file(self, channel_id: int) -> Optional[Dict[str, Any]]:
        """Carrega o arquivo de controle para um canal"""
        control_filename = os.path.join(self.download_dir, f"control_{channel_id}.json")
        if os.path.exists(control_filename):
            try:
                with open(control_filename, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erro ao carregar arquivo de controle: {e}")
        return None
    
    def _save_control_file(self, channel_id: int, data: Dict[str, Any]) -> bool:
        """Salva o arquivo de controle para um canal"""
        try:
            control_filename = os.path.join(self.download_dir, f"control_{channel_id}.json")
            with open(control_filename, 'w') as f:
                json.dump(data, f)
            return True
        except Exception as e:
            print(f"Erro ao salvar arquivo de controle: {e}")
            return False
    
    def _get_media_extension(self, message: Message) -> str:
        """Obtém a extensão do arquivo com base no tipo de mídia"""
        if message.photo:
            return '.jpg'
        elif message.video:
            return '.mp4'
        elif message.audio:
            return '.mp3'
        elif message.document:
            # Tentar obter a extensão do nome do arquivo original
            if message.document.file_name:
                return os.path.splitext(message.document.file_name)[1]
            else:
                return ''
        elif message.voice:
            return '.ogg'
        elif message.animation:
            return '.mp4'
        else:
            return ''
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitiza o nome do arquivo removendo caracteres inválidos"""
        # Remove caracteres inválidos para nome de arquivo
        invalid_chars = '<>:"/\\|?*\n\r\t'
        
        # Substitui quebras de linha e tabs por espaços
        filename = ' '.join(filename.split())
        
        # Remove outros caracteres inválidos
        for char in invalid_chars:
            filename = filename.replace(char, '')
            
        # Remove espaços múltiplos
        filename = ' '.join(filename.split())
        
        # Remove espaços no início e fim
        filename = filename.strip()
        
        # Se o filename estiver vazio após a limpeza, usa um nome genérico
        if not filename:
            filename = "arquivo"
            
        # Limita o tamanho do nome do arquivo
        return filename[:150]

    def get_credentials(self) -> tuple:
        """Retorna as credenciais atuais (api_id, api_hash)"""
        return self.api_id, self.api_hash

    def _load_credentials(self):
        """Carrega as credenciais salvas, se existirem"""
        try:
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    self.api_id = config.get('api_id')
                    self.api_hash = config.get('api_hash')
        except Exception as e:
            print(f"Erro ao carregar credenciais: {e}")

    def _get_client(self):
        """Obtém uma instância do cliente, criando-a se necessário"""
        if not self.app:
            # IMPORTANTE: Obtenha suas próprias credenciais em https://my.telegram.org/apps
            # O aplicativo não vem com credenciais pré-configuradas
            self.app = Client(
                "plano_estudo_downloader",
                api_id=self.api_id,
                api_hash=self.api_hash,
                workdir=os.path.expanduser("~")
            )
        return self.app

    async def download_channel_videos(self, channel_id, progress_callback=None):
        """
        Faz download de todos os vídeos de um canal específico
        
        Args:
            channel_id: ID do canal
            progress_callback: Função de callback para reportar progresso
        
        Returns:
            dict: Resultados do download
        """
        if not self.has_valid_credentials():
            raise ValueError("Credenciais de API não configuradas")
            
        # Verificar se o cliente já está conectado
        is_connected = getattr(self.app, "is_connected", False)
        
        download_path = os.path.join(os.path.expanduser("~"), "Downloads", "TelegramVideos")
        os.makedirs(download_path, exist_ok=True)
        
        status = {
            "total": 0,
            "baixados": 0,
            "ignorados": 0,
            "erros": 0,
            "arquivos": []
        }
        
        try:
            client = self._get_client()
            
            # Função para processar as mensagens
            async def process_messages():
                # Contar mensagens com mídia
                count = 0
                async for message in client.get_chat_history(channel_id):
                    if message.video:
                        count += 1
                
                status["total"] = count
                if progress_callback:
                    progress_callback(status)
                
                # Processar e baixar
                async for message in client.get_chat_history(channel_id):
                    if message.video:
                        video = message.video
                        file_name = f"{message.date.strftime('%Y%m%d')}_{video.file_name or f'video_{video.file_id[-10:]}.mp4'}"
                        file_path = os.path.join(download_path, file_name)
                        
                        if os.path.exists(file_path):
                            status["ignorados"] += 1
                        else:
                            try:
                                await client.download_media(
                                    message, 
                                    file_name=file_path
                                )
                                status["baixados"] += 1
                                status["arquivos"].append(file_path)
                            except Exception as e:
                                print(f"Erro ao baixar vídeo: {e}")
                                status["erros"] += 1
                        
                        if progress_callback:
                            progress_callback(status)
            
            # Executar de acordo com o estado de conexão
            if is_connected:
                await process_messages()
                return status
            else:
                async with client:
                    await process_messages()
                    return status
                
        except RPCError as e:
            print(f"Erro do Telegram: {e}")
            raise
        except Exception as e:
            print(f"Erro ao baixar vídeos: {e}")
            raise 