
import json
import threading

from dotenv import load_dotenv

load_dotenv(".env.extensao", override=True)

from neonize.client import NewClient
from neonize.events import (
    ConnectedEv,
    DisconnectedEv,
    MessageEv
)
from neonize import extract_text

from agente_planejador import planejar

from motor_ferramentas import (
    executar_plano,
    analisar_resultados
)


# ==========================================
# CONFIGURACOES
# ==========================================

cliente = NewClient("sessao_whatsapp.db")

conectado_evento = threading.Event()
bloqueio = threading.RLock()

# Dados separados por conversa
conversas = {}


# ==========================================
# CONTROLE DE CONVERSAS
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
# COMANDOS
# ==========================================

def gerar_menu():

    return (
        "🤖 *ASSISTENTE INTELIGENTE*\n\n"
        "Envie sua pergunta normalmente.\n\n"

        "Posso:\n"
        "📚 Consultar documentos PDF\n"
        "🎬 Pesquisar filmes e séries\n"
        "🔎 Comparar informações\n"
        "🤖 Responder perguntas gerais\n\n"

        "*Comandos:*\n"
        "/menu - Exibir menu\n"
        "/ajuda - Exemplos de perguntas\n"
        "/sobre - Informações do projeto\n"
        "/plano - Mostrar a última decisão da IA\n"
        "/limpar - Limpar o histórico"
    )


def gerar_ajuda():

    return (
        "❓ *EXEMPLOS DE PERGUNTAS*\n\n"

        "1. Quais documentos estão indexados?\n\n"

        "2. O que os artigos falam sobre RAG?\n\n"

        "3. Quem dirigiu Interestelar?\n\n"

        "4. Compare Matrix e Interestelar.\n\n"

        "5. Pesquise cinco filmes com Batman "
        "no título.\n\n"

        "6. Relacione inteligência artificial "
        "nos documentos com o filme Ex Machina.\n\n"

        "Não é necessário selecionar "
        "a fonte manualmente."
    )


def gerar_sobre():

    return (
        "ℹ️ *SOBRE O ASSISTENTE*\n\n"

        "Chatbot desenvolvido em Python, "
        "integrado ao WhatsApp e Ollama.\n\n"

        "Utiliza dois agentes de IA:\n\n"

        "🧠 Agente 1: planeja as consultas "
        "e seleciona as ferramentas.\n\n"

        "🤖 Agente 2: interpreta os dados "
        "recuperados e gera a resposta.\n\n"

        "Fontes disponíveis:\n"
        "📚 Documentos PDF com RAG\n"
        "🎬 API OMDb\n"
        "💬 Modelo local Ollama"
    )


# ==========================================
# EXECUTAR OS DOIS AGENTES
# ==========================================

def processar_pergunta(pergunta, identificador):

    # Nesta versao didatica, o bloqueio
    # tambem serializa o processamento.
    with bloqueio:

        conversa = obter_conversa(identificador)

        historico = conversa["historico"]

        # ==================================
        # IA 1 - PLANEJADOR
        # ==================================

        print(
            "\n[IA 1] Analisando pergunta...",
            flush=True
        )

        plano = planejar(
            pergunta,
            historico
        )

        print(
            "[IA 1] Plano:",
            json.dumps(
                plano,
                ensure_ascii=False,
                indent=2
            ),
            flush=True
        )

        # ==================================
        # EXECUTAR FERRAMENTAS
        # ==================================

        print(
            "\n[FERRAMENTAS] Executando...",
            flush=True
        )

        resultados = executar_plano(
            plano,
            pergunta,
            conversa["resultados"]
        )

        # ==================================
        # IA 2 - ANALISTA
        # ==================================

        print(
            "\n[IA 2] Interpretando resultados...",
            flush=True
        )

        resposta = analisar_resultados(
            pergunta,
            resultados,
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

        conversa["plano"] = plano
        conversa["resultados"] = resultados

        return resposta


# ==========================================
# EVENTO DE CONEXAO
# ==========================================

@cliente.event(ConnectedEv)
def conectado(client, evento):

    conectado_evento.set()

    print("\n✅ WhatsApp conectado!", flush=True)
    print("Dois agentes de IA disponíveis.")
    print("Aguardando perguntas...\n")


# ==========================================
# EVENTO DE DESCONEXAO
# ==========================================

@cliente.event(DisconnectedEv)
def desconectado(client, evento):

    conectado_evento.clear()

    print(
        "\n⚠️ WhatsApp desconectado!",
        flush=True
    )


# ==========================================
# ENVIAR RESPOSTA
# ==========================================

def enviar_resposta(client, evento, texto):

    if not conectado_evento.is_set():

        print(
            "Aguardando reconexao...",
            flush=True
        )

        conectado_evento.wait(timeout=30)

    if not conectado_evento.is_set():

        print(
            "WhatsApp indisponivel. "
            "Resposta nao enviada.",
            flush=True
        )

        return

    try:

        client.reply_message(texto, evento)

        print(
            "\n✅ Resposta enviada!",
            flush=True
        )

    except Exception as erro:

        print(
            "Erro ao enviar resposta:",
            repr(erro),
            flush=True
        )

        if "client is nil" in str(erro).lower():
            conectado_evento.clear()


# ==========================================
# EVENTO DE MENSAGEM
# ==========================================

@cliente.event(MessageEv)
def mensagem(client, evento):

    try:

        origem = evento.Info.MessageSource

        texto = (
            extract_text(evento.Message) or ""
        ).strip()

        if origem.IsFromMe:
            return

        if origem.Chat.Server in (
            "g.us", "broadcast"
        ):
            return

        if not texto:
            return

        identificador = (
            f"{origem.Chat.User}"
            f"@{origem.Chat.Server}"
        )

        print("\n========== NOVA PERGUNTA ==========")
        print("Conversa:", identificador)
        print("Pergunta:", texto)

        comando = texto.lower()

        # ==================================
        # MENU E AJUDA
        # ==================================

        if comando == "/menu":

            resposta = gerar_menu()

        elif comando == "/ajuda":

            resposta = gerar_ajuda()

        elif comando == "/sobre":

            resposta = gerar_sobre()

        # ==================================
        # CONSULTAR ULTIMO PLANO
        # ==================================

        elif comando == "/plano":

            with bloqueio:

                conversa = obter_conversa(
                    identificador
                )

                plano = conversa["plano"]

                if plano:

                    resposta = (
                        "🧠 *ÚLTIMO PLANO DA IA*\n\n"
                        + json.dumps(
                            plano,
                            ensure_ascii=False,
                            indent=2
                        )
                    )

                else:

                    resposta = (
                        "Nenhum plano foi executado "
                        "nesta conversa."
                    )

        # ==================================
        # LIMPAR HISTORICO
        # ==================================

        elif comando == "/limpar":

            with bloqueio:
                conversas.pop(
                    identificador, None
                )

            resposta = (
                "🧹 Histórico e plano apagados!\n"
                "Pode iniciar uma nova conversa."
            )

        # ==================================
        # PROCESSAMENTO AUTOMATICO
        # ==================================

        else:

            try:

                resposta = processar_pergunta(
                    texto,
                    identificador
                )

            except Exception as erro:

                print(
                    "Erro no processamento:",
                    repr(erro),
                    flush=True
                )

                resposta = (
                    "⚠️ Não foi possível processar "
                    "sua pergunta.\n"
                    "Tente novamente mais tarde."
                )

        # ==================================
        # ENVIAR AO WHATSAPP
        # ==================================

        enviar_resposta(
            client,
            evento,
            resposta
        )

    except Exception as erro:

        print(
            "Erro geral:",
            repr(erro),
            flush=True
        )


# ==========================================
# INICIAR
# ==========================================

if __name__ == "__main__":

    print("====================================")
    print("    WHATSAPP - DOIS AGENTES DE IA")
    print("====================================")

    cliente.connect()
