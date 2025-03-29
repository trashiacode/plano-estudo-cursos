# Plano de Estudo para Cursos

Um aplicativo desktop Python para gerenciar seu progresso em cursos online e baixar vídeos do Telegram.

## Características

- **Gerenciamento de cursos**: Organize seus cursos, módulos e aulas
- **Acompanhamento de progresso**: Acompanhe seu progresso em cada curso
- **Estimativa de conclusão**: Veja uma estimativa de quando você concluirá o curso
- **Anotações**: Adicione anotações para cada aula
- **Sincronização com vídeos**: Abra os vídeos de aulas diretamente do aplicativo
- **Integração com Telegram**: Baixe vídeos de canais do Telegram para assistir offline

## Requisitos

- Python 3.8+
- Tkinter (geralmente vem instalado com Python)
- Bibliotecas adicionais (veja `requirements.txt`)

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/plano-estudo-cursos.git
cd plano-estudo-cursos
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute o aplicativo:
```bash
python plano-estudo-cursos.py
```

## Uso

### Gerenciamento de Cursos

1. Abra o aplicativo
2. Clique em "Arquivo" > "Abrir Curso" para escolher a pasta do curso
3. O aplicativo escaneará a pasta em busca de vídeos e criará a estrutura do curso
4. Marque as aulas como concluídas à medida que as assiste
5. Adicione anotações para cada aula conforme necessário

### Baixar Vídeos do Telegram

1. Na aba "Download Telegram", configure suas credenciais da API do Telegram
   - Obtenha suas credenciais em https://my.telegram.org/apps
2. Clique em "Atualizar Lista de Canais" para ver os canais disponíveis
3. Selecione um canal e clique em "Baixar Vídeos do Canal Selecionado"
4. Os vídeos serão baixados para a pasta "Downloads/TelegramVideos" no seu diretório de usuário

## Estrutura do Projeto

O projeto segue uma arquitetura baseada em Domain-Driven Design (DDD):

- `src/domain/entities/`: Classes de entidades do domínio (Aula, Módulo, Curso)
- `src/application/services/`: Serviços da aplicação
- `src/presentation/views/`: Componentes da interface gráfica
- `src/presentation/controllers/`: Controladores que conectam a interface aos serviços
- `src/infrastructure/`: Código de infraestrutura (banco de dados, arquivos)

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo LICENSE para detalhes.

## Aviso

Este aplicativo foi desenvolvido para fins educacionais. Use-o de forma responsável e respeite os direitos autorais dos conteúdos. 