
from neonize.client import NewClient
from neonize.events import ConnectedEv, MessageEv
from neonize import extract_text


# ==========================================
# CONFIGURACAO DO WHATSAPP
# ==========================================

cliente = NewClient("sessao_whatsapp.db")


# ==========================================
# EVENTO DE CONEXAO
# ==========================================

@cliente.event(ConnectedEv)
def conectado(client, evento):

    print("\nWhatsApp conectado!", flush=True)
    print("Aguardando mensagens...\n", flush=True)


# ==========================================
# EVENTO DE MENSAGEM
# ==========================================

@cliente.event(MessageEv)
def mensagem(client, evento):

    print("\n========== NOVA MENSAGEM ==========")

    try:
        origem = evento.Info.MessageSource
        texto = (extract_text(evento.Message) or "").strip()

        print("Chat:", origem.Chat)
        print("Remetente:", origem.Sender)
        print("Mensagem:", repr(texto))

        # Ignorar mensagens proprias
        if origem.IsFromMe:
            return

        # Ignorar grupos e status
        if origem.Chat.Server in ("g.us", "broadcast"):
            return

        # Ignorar mensagens sem texto
        if not texto:
            return

        # Resposta automatica
        client.reply_message(
            "Recebi sua mensagem: " + texto,
            evento
        )

        print("Resposta enviada!", flush=True)

    except Exception as erro:
        print("Erro:", repr(erro), flush=True)


# ==========================================
# INICIAR
# ==========================================

if __name__ == "__main__":
    print("Iniciando conexao com WhatsApp...")
    cliente.connect()
