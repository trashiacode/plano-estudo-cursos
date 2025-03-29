# Manual de Configuração - Plano de Estudo para Cursos

Este manual contém instruções detalhadas para configurar e usar o aplicativo "Plano de Estudo para Cursos", incluindo a configuração do ambiente Python, obtenção de credenciais do Telegram e instalação de ferramentas adicionais necessárias.

## Índice

1. [Requisitos de Sistema](#requisitos-de-sistema)
2. [Instalação do Python](#instalação-do-python)
3. [Instalação do Aplicativo](#instalação-do-aplicativo)
4. [Configuração do Telegram](#configuração-do-telegram)
5. [Instalação do FFmpeg](#instalação-do-ffmpeg)
6. [Uso do Aplicativo](#uso-do-aplicativo)
7. [Solução de Problemas](#solução-de-problemas)

## Requisitos de Sistema

- Sistema Operacional: Windows 10/11, macOS 10.14+, ou Linux (Ubuntu 18.04+, Debian 10+)
- Espaço em disco: Mínimo 500 MB para o aplicativo (exclui espaço para vídeos)
- Memória: 4 GB RAM ou mais recomendados
- Conexão com a Internet para download de vídeos do Telegram

## Instalação do Python

### Windows

1. Visite [python.org](https://www.python.org/downloads/) e baixe a versão mais recente do Python (3.8 ou superior)
2. Execute o instalador e marque a opção "Add Python to PATH"
3. Escolha "Install Now" para uma instalação padrão
4. Aguarde a instalação concluir
5. Abra o Prompt de Comando e digite `python --version` para verificar se o Python está instalado corretamente

### macOS

1. Visite [python.org](https://www.python.org/downloads/) e baixe a versão mais recente para macOS
2. Execute o instalador .pkg e siga as instruções
3. Abra o Terminal e digite `python3 --version` para verificar a instalação

### Linux

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv python3-tk
python3 --version  # Verifique a instalação
```

## Instalação do Aplicativo

1. Clone o repositório ou baixe o código-fonte:

```bash
git clone https://github.com/seu-usuario/plano-estudo-cursos.git
cd plano-estudo-cursos
```

2. Crie um ambiente virtual (opcional, mas recomendado):

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

## Configuração do Telegram

Para usar a funcionalidade de download de vídeos do Telegram, você precisa obter suas próprias credenciais de API:

1. Acesse [my.telegram.org](https://my.telegram.org/) e faça login com sua conta do Telegram
2. Clique em "API development tools"
3. Preencha o formulário com as seguintes informações:
   - App title: Plano Estudo Videos (ou qualquer nome que preferir)
   - Short name: PlanoEstudo (ou qualquer nome curto)
   - Platform: Desktop
   - Description: Aplicativo para download de vídeos educacionais
4. Clique em "Create application"
5. Anote seu **API ID** e **API Hash** (eles são pessoais e não devem ser compartilhados)
6. No aplicativo "Plano de Estudo para Cursos", vá para a aba "Download Telegram" e insira essas credenciais
7. Clique em "Salvar Configuração"

### Primeira Autenticação

Na primeira vez que você usar o download do Telegram, o aplicativo pedirá para você se autenticar:

1. Você receberá um prompt para inserir seu número de telefone (com código do país, ex: 551199999999)
2. Você receberá um código de verificação no Telegram, insira-o quando solicitado
3. Em alguns casos, pode ser necessário inserir uma senha adicional (se você tiver a autenticação de dois fatores ativada)

**NOTA IMPORTANTE**: Suas credenciais e sessão são salvas localmente no diretório do usuário. Nunca compartilhe esses arquivos ou suas credenciais.

## Instalação do FFmpeg

O FFmpeg é usado para processar vídeos e extrair informações como duração.

### Windows

1. Baixe o FFmpeg para Windows em [ffmpeg.org](https://ffmpeg.org/download.html) (escolha a versão "Windows builds")
2. Extraia os arquivos para uma pasta, como `C:\ffmpeg`
3. Adicione o caminho à pasta bin ao PATH do sistema:
   - Abra o Painel de Controle > Sistema > Configurações avançadas do sistema
   - Clique em "Variáveis de Ambiente"
   - Em "Variáveis do Sistema", encontre "Path" e clique em "Editar"
   - Clique em "Novo" e adicione `C:\ffmpeg\bin`
   - Clique em "OK" em todas as janelas
4. Reinicie o Prompt de Comando e digite `ffmpeg -version` para verificar a instalação

### macOS

Usando Homebrew:

```bash
brew install ffmpeg
ffmpeg -version  # Verifique a instalação
```

### Linux

```bash
sudo apt update
sudo apt install ffmpeg
ffmpeg -version  # Verifique a instalação
```

## Uso do Aplicativo

### Iniciar o Aplicativo

```bash
# No diretório do projeto
python plano-estudo-cursos.py
```

### Gerenciar Cursos

1. Clique em "Arquivo" > "Abrir Curso"
2. Selecione a pasta que contém seus vídeos de curso
3. O aplicativo organizará os vídeos em uma estrutura de módulos e aulas
4. Marque as aulas como concluídas à medida que as assiste
5. Use o painel de detalhes para adicionar anotações para cada aula

### Baixar Vídeos do Telegram

1. Configure suas credenciais de API (como explicado acima)
2. Vá para a aba "Download Telegram"
3. Clique em "Atualizar Lista de Canais"
4. Selecione um canal da lista
5. Clique em "Baixar Vídeos do Canal Selecionado"
6. Os vídeos serão baixados para a pasta `Downloads/TelegramVideos` no seu diretório de usuário

## Solução de Problemas

### Problema: O aplicativo não inicia

- Verifique se o Python está instalado corretamente
- Verifique se todas as dependências foram instaladas: `pip install -r requirements.txt`
- Verifique se o Tkinter está instalado (geralmente vem com o Python)

### Problema: Erro ao baixar vídeos do Telegram

- Verifique se suas credenciais de API estão corretas
- Verifique sua conexão com a Internet
- Verifique se o Pyrogram está instalado: `pip install pyrogram tgcrypto`
- Tente autenticar novamente (exclua o arquivo de sessão `.session` na pasta `~/.pyrogram_settings`)

### Problema: Vídeos sem informações de duração

- Verifique se o FFmpeg está instalado corretamente e disponível no PATH
- Use o comando `ffmpeg -version` para verificar se o FFmpeg está acessível

### Problema: Interface gráfica não aparece corretamente

- Verifique se o Tkinter está instalado corretamente
- Em sistemas Linux, instale o pacote: `sudo apt install python3-tk`

### Outros Problemas

Se você encontrar outros problemas, verifique:

1. Se todas as dependências estão instaladas
2. Se você está usando a versão mais recente do aplicativo
3. Se há erros específicos no console/terminal

Para problemas persistentes, abra uma issue no repositório GitHub com uma descrição detalhada do problema e quaisquer mensagens de erro que você esteja recebendo. 