
import threading

from neonize.client import NewClient
from neonize.events import ConnectedEv, MessageEv
from neonize import extract_text

from ollama_client import consultar_ollama


# ==========================================
# CONFIGURACOES
# ==========================================

cliente = NewClient("sessao_whatsapp.db")

# Historico separado por conversa
historicos = {}

# Controle de acesso ao historico
bloqueio = threading.RLock()


# ==========================================
# MENU DE COMANDOS
# ==========================================

def gerar_menu():

    return (
        "🤖 *ASSISTENTE IA LOCAL*\n\n"
        "📋 /menu - Exibir o menu\n"
        "❓ /ajuda - Instruções de utilização\n"
        "ℹ️ /sobre - Sobre o assistente\n"
        "🧹 /limpar - Limpar a memória\n\n"
        "💬 Envie sua pergunta para conversar "
        "com a inteligência artificial."
    )


# ==========================================
# AJUDA
# ==========================================

def gerar_ajuda():

    return (
        "❓ *COMO UTILIZAR O ASSISTENTE*\n\n"
        "1. Envie uma pergunta em texto.\n"
        "2. O assistente consultará o modelo "
        "de IA executado pelo Ollama.\n"
        "3. A resposta será enviada "
        "diretamente no WhatsApp.\n\n"
        "O chatbot utiliza as mensagens "
        "anteriores para contextualizar "
        "suas respostas.\n\n"
        "Utilize /limpar para iniciar "
        "uma nova conversa."
    )


# ==========================================
# SOBRE O ASSISTENTE
# ==========================================

def gerar_sobre():

    return (
        "ℹ️ *SOBRE O ASSISTENTE*\n\n"
        "🤖 *WhatsApp Ollama Python*\n\n"
        "Assistente virtual desenvolvido "
        "em Python e integrado ao WhatsApp "
        "para responder perguntas utilizando "
        "Inteligência Artificial Generativa.\n\n"
        "🛠️ *Tecnologias utilizadas:*\n"
        "🐍 Python\n"
        "💬 WhatsApp e Neonize\n"
        "🧠 Ollama\n"
        "🔗 API REST\n\n"
        "As respostas são geradas por um "
        "modelo de IA executado localmente.\n\n"
        "📋 Digite /menu para conhecer "
        "os comandos disponíveis."
    )


# ==========================================
# EVENTO DE CONEXAO
# ==========================================

@cliente.event(ConnectedEv)
def conectado(client, evento):

    print("\n✅ WhatsApp conectado!", flush=True)
    print("🤖 Bot com Ollama iniciado!", flush=True)
    print("Aguardando mensagens...\n", flush=True)


# ==========================================
# RECEBER MENSAGENS
# ==========================================

@cliente.event(MessageEv)
def mensagem(client, evento):

    try:

        origem = evento.Info.MessageSource

        texto = (
            extract_text(evento.Message) or ""
        ).strip()

        # Ignorar mensagens proprias
        if origem.IsFromMe:
            return

        # Ignorar grupos e status
        if origem.Chat.Server in ("g.us", "broadcast"):
            return

        # Ignorar mensagens sem texto
        if not texto:
            return

        # ==================================
        # IDENTIFICAR A CONVERSA
        # ==================================

        identificador = (
            f"{origem.Chat.User}"
            f"@{origem.Chat.Server}"
        )

        print("\n========== NOVA MENSAGEM ==========")
        print("Conversa:", identificador)
        print("Texto:", texto)

        comando = texto.lower()

        # ==================================
        # COMANDO /menu
        # ==================================

        if comando == "/menu":

            client.reply_message(
                gerar_menu(),
                evento
            )
            return

        # ==================================
        # COMANDO /ajuda
        # ==================================

        if comando == "/ajuda":

            client.reply_message(
                gerar_ajuda(),
                evento
            )
            return

        # ==================================
        # COMANDO /sobre
        # ==================================

        if comando == "/sobre":

            client.reply_message(
                gerar_sobre(),
                evento
            )
            return

        # ==================================
        # COMANDO /limpar
        # ==================================

        if comando == "/limpar":

            with bloqueio:
                historicos.pop(identificador, None)

            client.reply_message(
                "🧹 Histórico da conversa limpo!\n\n"
                "Pode iniciar uma nova conversa.",
                evento
            )
            return

        # ==================================
        # CONSULTAR O OLLAMA
        # ==================================

        print("Consultando Ollama...", flush=True)

        try:

            with bloqueio:

                historico = historicos.get(
                    identificador,
                    []
                )

                resposta = consultar_ollama(
                    texto,
                    historico
                )

                # Registrar pergunta e resposta
                novo_historico = historico + [
                    {
                        "role": "user",
                        "content": texto
                    },
                    {
                        "role": "assistant",
                        "content": resposta
                    }
                ]

                # Manter ultimas 10 interacoes
                historicos[identificador] = (
                    novo_historico[-20:]
                )

        except Exception as erro:

            print(
                "Erro ao consultar Ollama:",
                repr(erro),
                flush=True
            )

            resposta = (
                "⚠️ Não consegui consultar "
                "a inteligência artificial.\n\n"
                "Tente novamente mais tarde."
            )

        # ==================================
        # ENVIAR RESPOSTA
        # ==================================

        client.reply_message(
            resposta,
            evento
        )

        print("✅ Resposta enviada!", flush=True)

    except Exception as erro:

        print(
            "Erro no processamento:",
            repr(erro),
            flush=True
        )


# ==========================================
# INICIAR CHATBOT
# ==========================================

if __name__ == "__main__":

    print("====================================")
    print("     WHATSAPP + PYTHON + OLLAMA")
    print("====================================")

    print("Iniciando bot...", flush=True)

    cliente.connect()
