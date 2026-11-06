
import json
import threading

from dotenv import load_dotenv

# ==========================================
# CONFIGURACOES DA EXTENSAO
# ==========================================

load_dotenv(".env.extensao", override=True)

from neonize.client import NewClient
from neonize.events import (
    ConnectedEv,
    DisconnectedEv,
    MessageEv
)
from neonize import extract_text

from agentes_autonomos import (
    pesquisar_com_ia,
    responder_com_ia
)


# ==========================================
# CONFIGURACOES GERAIS
# ==========================================

SESSAO_WHATSAPP = "sessao_whatsapp.db"

cliente = NewClient(SESSAO_WHATSAPP)

# Estado da conexao
conectado_evento = threading.Event()

# Controle de acesso as conversas
bloqueio = threading.RLock()

# Historico e resultados por conversa
conversas = {}


# ==========================================
# GERENCIAMENTO DE CONVERSAS
# ==========================================

def obter_conversa(identificador):

    if identificador not in conversas:

        conversas[identificador] = {
            "historico": [],
            "plano": None,
            "resultados": None
        }

    return conversas[identificador]


# ==========================================
# GERAR MENU
# ==========================================

def gerar_menu():

    return (
        "🤖 *ASSISTENTE INTELIGENTE*\n\n"

        "Envie sua pergunta normalmente.\n"
        "Os agentes selecionam automaticamente "
        "as fontes de informação.\n\n"

        "📚 *Documentos PDF*\n"
        "Consultas aos arquivos indexados "
        "utilizando RAG.\n\n"

        "🎬 *Filmes e séries*\n"
        "Pesquisas na API OMDb.\n\n"

        "🧠 *Conhecimento geral*\n"
        "Perguntas respondidas pelo Ollama.\n\n"

        "🔎 *Consultas combinadas*\n"
        "Relacionamento entre documentos "
        "e informações de filmes.\n\n"

        "⚙️ *COMANDOS*\n"
        "/menu - Exibir menu\n"
        "/ajuda - Exemplos de perguntas\n"
        "/sobre - Informações do assistente\n"
        "/plano - Mostrar a última pesquisa\n"
        "/limpar - Reiniciar a conversa"
    )


# ==========================================
# GERAR AJUDA
# ==========================================

def gerar_ajuda():

    return (
        "❓ *COMO UTILIZAR O ASSISTENTE*\n\n"

        "Não é necessário escolher "
        "uma ferramenta manualmente.\n\n"

        "📚 *Documentos:*\n"
        "Quais artigos estão indexados?\n"
        "O que os PDFs dizem sobre RAG?\n\n"

        "🎬 *Filmes:*\n"
        "Quem dirigiu Interestelar?\n"
        "Compare Matrix e Interestelar.\n"
        "Pesquise filmes com Batman no título.\n\n"

        "🧠 *Conhecimento geral:*\n"
        "Explique o que é Python.\n"
        "O que é Inteligência Artificial?\n\n"

        "🔎 *Consulta combinada:*\n"
        "Relacione a inteligência artificial "
        "dos meus PDFs com o filme Ex Machina.\n\n"

        "⚙️ *Outros comandos:*\n"
        "/plano - Ver as decisões da IA\n"
        "/limpar - Limpar o histórico."
    )


# ==========================================
# GERAR SOBRE
# ==========================================

def gerar_sobre():

    return (
        "ℹ️ *SOBRE O ASSISTENTE*\n\n"

        "🤖 *Chatbot com Agentes de IA*\n\n"

        "Assistente virtual desenvolvido "
        "em Python e integrado ao WhatsApp "
        "e ao Ollama.\n\n"

        "🧠 *IA 1 - Planejador*\n"
        "Interpreta perguntas, seleciona "
        "ferramentas e realiza pesquisas.\n\n"

        "🤖 *IA 2 - Analista*\n"
        "Interpreta os resultados e "
        "produz as respostas finais.\n\n"

        "📚 *Fontes disponíveis:*\n"
        "• Conhecimento geral do Ollama\n"
        "• Documentos PDF com RAG\n"
        "• API de filmes OMDb\n\n"

        "🛠️ *Tecnologias:*\n"
        "Python, Neonize, Ollama, "
        "RAG e API REST."
    )


# ==========================================
# PROCESSAR PERGUNTA COM DOIS AGENTES
# ==========================================

def processar_pergunta(pergunta, identificador):

    with bloqueio:

        conversa = obter_conversa(
            identificador
        )

        historico = conversa["historico"]

        # ==================================
        # IA 1 - PLANEJAR E PESQUISAR
        # ==================================

        print(
            "\n[IA 1] Iniciando planejamento...",
            flush=True
        )

        pesquisa = pesquisar_com_ia(
            pergunta,
            historico
        )

        print(
            "\n[IA 1] Pesquisa concluida.",
            flush=True
        )

        print(
            "Categoria:",
            pesquisa["categoria"],
            flush=True
        )

        print(
            "Consultas realizadas:",
            pesquisa["consultas"],
            flush=True
        )

        # ==================================
        # IA 2 - ANALISAR E RESPONDER
        # ==================================

        print(
            "\n[IA 2] Gerando resposta...",
            flush=True
        )

        resposta = responder_com_ia(
            pergunta,
            pesquisa,
            historico
        )

        # ==================================
        # ATUALIZAR HISTORICO
        # ==================================

        conversa["historico"] = (
            historico + [
                {
                    "role": "user",
                    "content": pergunta
                },
                {
                    "role": "assistant",
                    "content": resposta
                }
            ]
        )[-12:]

        # Registrar a ultima pesquisa
        conversa["plano"] = pesquisa

        conversa["resultados"] = (
            pesquisa["evidencias"]
        )

        print(
            "\n[IA 2] Resposta final:",
            resposta,
            flush=True
        )

        return resposta


# ==========================================
# EVENTO: CONEXAO WHATSAPP
# ==========================================

@cliente.event(ConnectedEv)
def conectado(client, evento):

    conectado_evento.set()

    print(
        "\n✅ WhatsApp conectado!",
        flush=True
    )

    print(
        "🤖 Dois agentes de IA disponíveis.",
        flush=True
    )

    print(
        "📨 Aguardando perguntas...\n",
        flush=True
    )


# ==========================================
# EVENTO: DESCONEXAO WHATSAPP
# ==========================================

@cliente.event(DisconnectedEv)
def desconectado(client, evento):

    conectado_evento.clear()

    print(
        "\n⚠️ WhatsApp desconectado!",
        flush=True
    )

    print(
        "Aguardando reconexão...",
        flush=True
    )


# ==========================================
# ENVIAR RESPOSTA PELO WHATSAPP
# ==========================================

def enviar_resposta(client, evento, texto):

    # Verificar conexao
    if not conectado_evento.is_set():

        print(
            "WhatsApp desconectado. "
            "Aguardando reconexão...",
            flush=True
        )

        conectado_evento.wait(
            timeout=30
        )

    if not conectado_evento.is_set():

        print(
            "Resposta não enviada: "
            "WhatsApp indisponível.",
            flush=True
        )

        return False

    try:

        print(
            "\n📤 Enviando resposta...",
            flush=True
        )

        client.reply_message(
            texto,
            evento
        )

        print(
            "✅ Resposta enviada!",
            flush=True
        )

        return True

    except Exception as erro:

        print(
            "❌ Erro ao enviar resposta:",
            repr(erro),
            flush=True
        )

        if "client is nil" in str(erro).lower():

            conectado_evento.clear()

            print(
                "Cliente WhatsApp indisponível. "
                "Aguardando reconexão.",
                flush=True
            )

        return False


# ==========================================
# EVENTO: NOVA MENSAGEM
# ==========================================

@cliente.event(MessageEv)
def mensagem(client, evento):

    try:

        # ----------------------------------
        # EXTRAIR MENSAGEM
        # ----------------------------------

        origem = evento.Info.MessageSource

        texto = (
            extract_text(evento.Message) or ""
        ).strip()

        # Ignorar mensagens proprias
        if origem.IsFromMe:
            return

        # Ignorar grupos e status
        if origem.Chat.Server in (
            "g.us",
            "broadcast"
        ):
            return

        # Ignorar mensagens vazias
        if not texto:
            return

        # ----------------------------------
        # IDENTIFICAR CONVERSA
        # ----------------------------------

        identificador = (
            f"{origem.Chat.User}"
            f"@{origem.Chat.Server}"
        )

        print(
            "\n========== NOVA PERGUNTA ==========",
            flush=True
        )

        print(
            "Conversa:",
            identificador,
            flush=True
        )

        print(
            "Pergunta:",
            texto,
            flush=True
        )

        comando = texto.lower()

        # ==================================
        # COMANDO /menu
        # ==================================

        if comando == "/menu":

            resposta = gerar_menu()

        # ==================================
        # COMANDO /ajuda
        # ==================================

        elif comando == "/ajuda":

            resposta = gerar_ajuda()

        # ==================================
        # COMANDO /sobre
        # ==================================

        elif comando == "/sobre":

            resposta = gerar_sobre()

        # ==================================
        # COMANDO /plano
        # ==================================

        elif comando == "/plano":

            with bloqueio:

                conversa = obter_conversa(
                    identificador
                )

                plano = conversa["plano"]

                if plano:

                    texto_plano = json.dumps(
                        plano,
                        ensure_ascii=False,
                        indent=2
                    )

                    # Evitar mensagens excessivas
                    texto_plano = texto_plano[:3500]

                    resposta = (
                        "🧠 *ÚLTIMA PESQUISA DA IA*\n\n"
                        + texto_plano
                    )

                else:

                    resposta = (
                        "Nenhuma pesquisa foi "
                        "realizada nesta conversa."
                    )

        # ==================================
        # COMANDO /limpar
        # ==================================

        elif comando == "/limpar":

            with bloqueio:

                conversas.pop(
                    identificador,
                    None
                )

            resposta = (
                "🧹 *Conversa reiniciada!*\n\n"
                "O histórico, o planejamento "
                "e os resultados anteriores "
                "foram removidos da memória.\n\n"
                "Pode enviar uma nova pergunta."
            )

        # ==================================
        # PERGUNTA PARA OS DOIS AGENTES
        # ==================================

        else:

            try:

                resposta = processar_pergunta(
                    texto,
                    identificador
                )

            except Exception as erro:

                print(
                    "❌ Erro no processamento:",
                    repr(erro),
                    flush=True
                )

                resposta = (
                    "⚠️ Não foi possível processar "
                    "sua pergunta.\n\n"
                    "Verifique se o Ollama está "
                    "funcionando e tente novamente."
                )

        # ==================================
        # ENVIAR RESPOSTA
        # ==================================

        enviar_resposta(
            client,
            evento,
            resposta
        )

    except Exception as erro:

        print(
            "\n❌ Erro geral:",
            repr(erro),
            flush=True
        )


# ==========================================
# INICIAR APLICACAO
# ==========================================

if __name__ == "__main__":

    print("====================================")
    print("    WHATSAPP - DOIS AGENTES DE IA")
    print("====================================")

    print(
        "Iniciando chatbot...",
        flush=True
    )

    cliente.connect()
