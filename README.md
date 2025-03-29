# Plano de Estudo para Cursos

Um aplicativo desktop Python para gerenciar seu progresso em cursos online e baixar vídeos do Telegram.

## Características

- **Gerenciamento de cursos**: Organize seus cursos, módulos e aulas
- **Acompanhamento de progresso**: Acompanhe seu progresso em cada curso
- **Estimativa de conclusão**: Veja uma estimativa de quando você concluirá o curso
- **Anotações**: Adicione anotações para cada aula
- **Sincronização com vídeos**: Abra os vídeos de aulas diretamente do aplicativo
- **Integração com Telegram**: Baixe vídeos de canais do Telegram para assistir offline

## Requisitos de Sistema

- **Sistema Operacional**: Windows 10/11, macOS 10.14+, ou Linux (Ubuntu 18.04+, Debian 10+)
- **Python 3.8+**
- **Espaço em disco**: Mínimo 500 MB para o aplicativo (exclui espaço para vídeos)
- **Memória**: 4 GB RAM ou mais recomendados
- **Tkinter** (geralmente vem instalado com Python)
- **FFmpeg** (para processamento de vídeos)
- **Conexão com a Internet** para download de vídeos do Telegram
- **Bibliotecas adicionais** (veja `requirements.txt`)

## Instalação

### Instalação do Python

#### Windows

1. Visite [python.org](https://www.python.org/downloads/) e baixe a versão mais recente do Python (3.8 ou superior)
2. Execute o instalador e marque a opção "Add Python to PATH"
3. Escolha "Install Now" para uma instalação padrão
4. Verifique a instalação com `python --version` no Prompt de Comando

#### macOS

1. Visite [python.org](https://www.python.org/downloads/) e baixe a versão mais recente para macOS
2. Execute o instalador .pkg e siga as instruções
3. Verifique a instalação com `python3 --version` no Terminal

#### Linux

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv python3-tk
python3 --version  # Verifique a instalação
```

### Instalação do Aplicativo

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/plano-estudo-cursos.git
cd plano-estudo-cursos
```

2. (Opcional) Crie um ambiente virtual:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute o aplicativo:
```bash
python plano-estudo-cursos.py
```

### Instalação do FFmpeg

O FFmpeg é usado para processar vídeos e extrair informações como duração.

#### Windows

1. Baixe o FFmpeg para Windows em [ffmpeg.org](https://ffmpeg.org/download.html) (escolha a versão "Windows builds")
2. Extraia os arquivos para uma pasta, como `C:\ffmpeg`
3. Adicione o caminho à pasta bin ao PATH do sistema:
   - Abra o Painel de Controle > Sistema > Configurações avançadas do sistema
   - Clique em "Variáveis de Ambiente"
   - Em "Variáveis do Sistema", encontre "Path" e clique em "Editar"
   - Clique em "Novo" e adicione `C:\ffmpeg\bin`
   - Clique em "OK" em todas as janelas
4. Verifique com `ffmpeg -version` em um novo Prompt de Comando

#### macOS

Usando Homebrew:
```bash
brew install ffmpeg
ffmpeg -version  # Verifique a instalação
```

#### Linux

```bash
sudo apt update
sudo apt install ffmpeg
ffmpeg -version  # Verifique a instalação
```

## Uso

### Gerenciamento de Cursos

1. Abra o aplicativo
2. Clique em "Arquivo" > "Abrir Curso" para escolher a pasta do curso
3. O aplicativo escaneará a pasta em busca de vídeos e criará a estrutura do curso
4. Marque as aulas como concluídas à medida que as assiste
5. Adicione anotações para cada aula conforme necessário

### Configuração do Telegram

Para usar a funcionalidade de download de vídeos do Telegram, é necessário obter suas próprias credenciais de API:

1. Acesse [my.telegram.org](https://my.telegram.org/) e faça login com sua conta do Telegram
2. Clique em "API development tools"
3. Preencha o formulário:
   - App title: Plano Estudo Videos (ou nome de sua preferência)
   - Short name: PlanoEstudo (ou nome curto de sua preferência)
   - Platform: Desktop
   - Description: Aplicativo para download de vídeos educacionais
4. Clique em "Create application"
5. Anote seu **API ID** e **API Hash** (eles são pessoais e não devem ser compartilhados)

### Baixar Vídeos do Telegram

1. Na aba "Download Telegram", configure suas credenciais da API do Telegram
   - Insira o API ID e API Hash obtidos anteriormente
   - Clique em "Salvar Configuração"
2. Clique em "Atualizar Lista de Canais" para ver os canais disponíveis
3. Selecione um canal e clique em "Baixar Vídeos do Canal Selecionado"
4. Os vídeos serão baixados para a pasta "Downloads/TelegramVideos" no seu diretório de usuário

Na primeira utilização, o aplicativo solicitará autenticação:
1. Insira seu número de telefone (com código do país, ex: 551199999999)
2. Insira o código de verificação recebido no Telegram
3. Se necessário, insira a senha (caso tenha autenticação de dois fatores)

## Estrutura do Projeto

O projeto segue uma arquitetura baseada em Domain-Driven Design (DDD):

- `src/domain/entities/`: Classes de entidades do domínio (Aula, Módulo, Curso)
- `src/application/services/`: Serviços da aplicação
- `src/presentation/views/`: Componentes da interface gráfica
- `src/presentation/controllers/`: Controladores que conectam a interface aos serviços
- `src/infrastructure/`: Código de infraestrutura (banco de dados, arquivos)

## Solução de Problemas

### Problema: O aplicativo não inicia
- Verifique a instalação do Python e das dependências
- Verifique se o Tkinter está instalado

### Problema: Erro ao baixar vídeos do Telegram
- Verifique se as credenciais de API estão corretas
- Verifique sua conexão com a Internet
- Verifique se o Pyrogram está instalado: `pip install pyrogram tgcrypto`
- Tente autenticar novamente (exclua o arquivo `.session` na pasta do usuário)

### Problema: Vídeos sem informações de duração
- Verifique a instalação do FFmpeg e se está disponível no PATH

### Problema: Interface gráfica não aparece corretamente
- Em sistemas Linux, instale: `sudo apt install python3-tk`

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo LICENSE para detalhes.

## Aviso

Este aplicativo foi desenvolvido para fins educacionais. Use-o de forma responsável e respeite os direitos autorais dos conteúdos. 