# Assistente WhatsApp com Ollama, RAG e OMDb

Projeto didático da Aula 07 de Inteligência Artificial: um assistente em Python integrado ao WhatsApp, com geração de respostas por modelos locais no Ollama, consulta a documentos PDF com RAG e pesquisa de filmes e séries pela API OMDb.

O repositório apresenta três versões do assistente: conversação básica, consultas por comandos e uma versão com dois agentes que seleciona ferramentas a partir de perguntas em linguagem natural.

## Funcionalidades

- Conversação em português com um modelo executado pelo Ollama.
- Histórico separado por conversa: até dez interações nos bots básico e por comandos; até seis na versão com agentes.
- Extração de texto de PDFs e geração local de embeddings.
- Recuperação de trechos por similaridade de cosseno, sem banco vetorial externo.
- Respostas sobre documentos acompanhadas dos nomes dos arquivos e das páginas recuperadas.
- Consulta de detalhes e pesquisa de títulos na OMDb.
- Planejamento em JSON, execução de ferramentas e análise dos resultados na versão com agentes.
- Comandos de ajuda, menu e limpeza do histórico; inspeção do último plano com `/plano` na versão com agentes.
- Filtro para ignorar mensagens próprias, grupos, status e mensagens sem texto.

## Versões do bot

| Arquivo | Finalidade | Como conversar |
| --- | --- | --- |
| `bot.py` | Assistente básico com Ollama e memória por conversa | Envie uma pergunta diretamente |
| `bot_rag_omdb.py` | Assistente com IA, documentos e OMDb | Use os comandos `/ia`, `/rag`, `/filme` e `/buscarfilme` |
| `bot_agentes.py` | Planejador e analista com seleção automática de ferramentas | Envie perguntas em linguagem natural; use `/plano` para consultar a última decisão |

Execute apenas uma versão por vez: os bots compartilham o arquivo de sessão do WhatsApp.

## Tecnologias

| Tecnologia | Uso no projeto |
| --- | --- |
| Python | Eventos, comandos e integração dos componentes |
| Neonize | Conexão e troca de mensagens com o WhatsApp |
| Ollama | API local de conversação e embeddings |
| Requests | Requisições HTTP ao Ollama e à OMDb |
| python-dotenv | Carregamento de configurações por ambiente |
| pypdf | Extração do texto dos PDFs |
| JSON | Armazenamento dos trechos e vetores da base RAG |

Os modelos padrão configurados no código são `qwen2.5:3b` para conversação e `nomic-embed-text` para embeddings.

## Estrutura

```text
.
├── bot.py                    # Bot básico: WhatsApp + Ollama
├── bot_rag_omdb.py            # Bot com comandos de IA, RAG e OMDb
├── bot_agentes.py            # WhatsApp com planejador, ferramentas e analista
├── agente_planejador.py      # Seleção de ferramentas e plano JSON
├── motor_ferramentas.py      # Execução de consultas e resposta final
├── teste_agentes.py          # Fluxo dos dois agentes no terminal
├── ollama_client.py           # Cliente da API de conversação
├── omdb_client.py             # Consulta, busca e formatação de títulos
├── rag_local.py               # Extração, indexação e busca vetorial
├── indexar_pdfs.py            # Entrada para gerar o índice dos PDFs
├── teste_ollama.py            # Chat interativo no terminal
├── teste_rag.py               # Consulta de trechos no terminal
├── teste_whatsapp.py          # Teste de conexão e resposta automática
├── requirements.txt          # Dependências Python
├── .env.example              # Modelo de configuração do bot básico
├── documents/                # PDFs usados como base de conhecimento
└── dados_rag/
    └── indice.json           # Índice gerado com trechos e embeddings
```

Os arquivos `.env`, `.env.extensao` e `sessao_whatsapp.db` são locais. O arquivo de sessão é criado ou reutilizado pelo Neonize.

## Pré-requisitos

- Python e `pip`, em uma versão compatível com as dependências de `requirements.txt`.
- Ollama instalado e em execução na máquina ou em um servidor acessível.
- Espaço em disco e memória suficientes para os modelos escolhidos.
- WhatsApp com acesso à opção de aparelhos conectados.
- PDFs com texto extraível para usar o RAG.
- Chave da API OMDb para os comandos de filmes.

A geração de texto e os embeddings podem rodar localmente. A comunicação com o WhatsApp e as consultas à OMDb dependem de internet.

## Instalação

Abra um terminal na pasta do projeto. No PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Os comandos abaixo usam diretamente o Python do ambiente virtual, dispensando sua ativação no PowerShell.

Baixe os modelos no Ollama:

```powershell
ollama pull qwen2.5:3b
ollama pull nomic-embed-text
```

Se o serviço do Ollama ainda não estiver em execução, inicie-o em outro terminal:

```powershell
ollama serve
```

## Configuração

### Bot básico

Copie o arquivo de exemplo, caso ainda não tenha um `.env`:

```powershell
Copy-Item .env.example .env
```

Conteúdo esperado:

```dotenv
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b
```

### Bot com RAG e OMDb

Crie um arquivo chamado `.env.extensao` na raiz do projeto:

```dotenv
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b
EMBEDDING_MODEL=nomic-embed-text
OMDB_API_KEY=COLOQUE_SUA_CHAVE_AQUI
```

Substitua o valor de `OMDB_API_KEY` pela sua chave. Ela é necessária apenas para as consultas à OMDb. Use em `OLLAMA_URL` a URL base do serviço, sem acrescentar `/api/chat` ou `/api/embed`.

O bot estendido carrega `.env.extensao` com prioridade sobre variáveis já existentes no ambiente. Os scripts independentes de RAG carregam esse arquivo sem sobrescrever variáveis do ambiente.

## Execução

Execute os comandos na raiz do projeto, pois os caminhos de configuração, documentos e sessão são relativos à pasta atual.

### Conversação básica

```powershell
.\.venv\Scripts\python.exe bot.py
```

### Assistente com documentos e filmes

1. Coloque seus PDFs na pasta `documents/`.
2. Gere o índice:

   ```powershell
   .\.venv\Scripts\python.exe indexar_pdfs.py
   ```

3. Aguarde a mensagem de conclusão da indexação e a quantidade de trechos indexados.
4. Inicie o bot:

   ```powershell
   .\.venv\Scripts\python.exe bot_rag_omdb.py
   ```

Na primeira conexão, siga o pareamento apresentado pelo Neonize, usando a opção de aparelhos conectados do WhatsApp. Após a conexão, envie uma mensagem de outra conta para o número conectado: mensagens enviadas pela própria conta são ignoradas.

Para encerrar o processo, pressione `Ctrl+C` no terminal.

## Comandos no WhatsApp

| Comando | Ação | Disponibilidade |
| --- | --- | --- |
| `/menu` | Exibe os comandos | Ambas as versões |
| `/ajuda` | Mostra instruções e exemplos | Ambas as versões |
| `/sobre` | Apresenta o assistente | Ambas as versões |
| `/limpar` | Remove o histórico da conversa atual | Ambas as versões |
| `/ia Explique aprendizado de máquina` | Conversa com o modelo local | Bot estendido |
| `/rag O que é a taxonomia de Bloom?` | Consulta os PDFs indexados | Bot estendido |
| `/documentos` | Lista arquivos e quantidade de páginas indexadas | Bot estendido |
| `/filme Interstellar` | Consulta detalhes de um título e gera uma resposta com Ollama | Bot estendido |
| `/buscarfilme Batman` | Lista até cinco resultados da OMDb | Bot estendido |

No bot básico, envie texto livre para conversar. No bot estendido, perguntas devem acompanhar um comando; texto livre recebe uma orientação para consultar o menu.

## Como funciona o RAG

1. O `pypdf` extrai o texto de cada página dos arquivos `*.pdf` diretamente em `documents/`.
2. O texto é normalizado e dividido em trechos de até 900 caracteres, com sobreposição de 120 caracteres.
3. O Ollama gera embeddings em lotes de até 12 trechos.
4. Os textos, vetores, nomes dos arquivos e páginas são gravados em `dados_rag/indice.json`.
5. A pergunta é convertida em um vetor e comparada com todos os trechos usando similaridade de cosseno.
6. Os três trechos mais semelhantes são enviados ao modelo como contexto para a resposta.
7. O bot acrescenta as referências dos trechos recuperados à mensagem enviada ao WhatsApp.

Execute novamente `indexar_pdfs.py` após adicionar, remover ou alterar PDFs, ou trocar o modelo de embeddings. A indexação reconstrói e substitui o índice anterior.

## Verificações manuais

Estes scripts são demonstrações de integração, não uma suíte automatizada de testes:

```powershell
# Chat interativo com Ollama; digite sair para encerrar
.\.venv\Scripts\python.exe teste_ollama.py

# Recuperação de trechos; exige Ollama e índice disponível
.\.venv\Scripts\python.exe teste_rag.py

# Conexão ao WhatsApp e resposta de confirmação às mensagens recebidas
.\.venv\Scripts\python.exe teste_whatsapp.py
```

O teste de WhatsApp usa a mesma sessão dos bots e deve ser executado separadamente. O teste de RAG mostra os trechos recuperados, sem gerar uma resposta de conversação.

## Limitações e observações

- O histórico fica apenas na memória do processo e é perdido ao reiniciar. No bot estendido, apenas `/ia` usa esse histórico; as consultas RAG e OMDb são independentes.
- PDFs digitalizados sem camada de texto precisam de OCR externo antes da indexação; o projeto não implementa OCR.
- A busca RAG retorna os trechos mais semelhantes sem aplicar um limiar mínimo de relevância. As referências exibidas indicam os trechos recuperados e não garantem que toda afirmação da resposta esteja sustentada por eles.
- O índice JSON é carregado e percorrido a cada busca, uma abordagem simples para fins didáticos e bases pequenas.
- O bloqueio usado na conversação com histórico permanece ativo durante a consulta ao Ollama, podendo fazer outras conversas aguardarem.
- As dependências não têm versões fixadas em `requirements.txt`.
- Os bots imprimem identificadores de conversa e textos recebidos no terminal.

## Problemas frequentes

| Situação | O que verificar |
| --- | --- |
| Falha ao consultar o Ollama | Serviço em execução, `OLLAMA_URL`, modelo baixado e recursos disponíveis |
| Base RAG não encontrada | Execute `indexar_pdfs.py` na raiz e confira a conclusão da indexação |
| Modelo de embeddings diferente | Reindexe com o mesmo `EMBEDDING_MODEL` usado nas consultas |
| Nenhum texto extraído | Verifique se os PDFs têm texto selecionável |
| Falha nas consultas de filmes | Chave OMDb configurada, conexão com a internet e título pesquisado |
| Bot não responde | Confira a conexão, use outra conta e envie uma mensagem privada com texto; no bot estendido, use um comando válido |

## Publicação no GitHub

O `.gitignore` exclui credenciais locais, ambientes virtuais, caches e a sessão do WhatsApp. Os modelos `.env.example` e `.env.extensao.example` são incluídos para orientar a configuração.

Os PDFs em `documents/` e o índice JSON em `dados_rag/` ficam locais e são ignorados pelo Git. Adicione seus próprios documentos e gere o índice seguindo as instruções de execução. O índice contém texto extraído dos PDFs; caso decida distribuir esses arquivos, verifique as permissões de distribuição e a presença de informações privadas.

Não há arquivo de licença na pasta analisada. Defina uma licença antes de oferecer permissões explícitas de reutilização do código.
