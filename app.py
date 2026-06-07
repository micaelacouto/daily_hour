from flask import Flask, render_template, request, redirect, flash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
from datetime import datetime
import threading

app = Flask(__name__)
app.secret_key = "chave_secreta_para_os_avisos" # Necessário para usar o sistema de alertas (flash)

# CONFIGURAÇÕES PROFISSIONAIS DA EMPRESA (BREVO)
SERVIDOR_SMTP = "smtp-relay.brevo.com"
EMAIL_EMISSOR = "SUA_CHAVE_DE_LOGIN_AQUI" 
SENHA_EMISSOR = "SUA_SENHA_DO_BREVO_AQUI"          
EMAIL_AUTENTICADO = "SEU_EMAIL_DE_CADASTRO_AQUI"

lista_de_tarefas = []

def enviar_lembrete_email(email_destino, nome_tarefa):
    # Função que conecta ao servidor e envia o e-mail real para o usuário
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_AUTENTICADO 
        msg['To'] = email_destino
        msg['Subject'] = "⏰ Lembrete Daily Hour!"

        # Conteúdo da mensagem que vai ser enviada
        corpo_mensagem = f"Olá! Viemos te lembrar que chegou a hora de: {nome_tarefa}. Não vá se esquecer, hein!"
        msg.attach(MIMEText(corpo_mensagem, 'plain'))

        # Conexão segura com o servidor SMTP da empresa
        servidor = smtplib.SMTP(SERVIDOR_SMTP, 587)
        servidor.starttls()
        servidor.login(EMAIL_EMISSOR, SENHA_EMISSOR)
        
        # Faz o disparo do e-mail usando a autenticação da conta do Brevo
        servidor.sendmail(EMAIL_AUTENTICADO, email_destino, msg.as_string())
        servidor.quit()
        print(f"Sucesso! E-mail enviado via sistema para {email_destino}!")
    except Exception as e:
        print(f"Erro ao disparar o e-mail: {e}")

def relogio_espiao():
    # Função que roda em segundo plano vigiando as horas minuto a minuto
    while True:
        # Pega o horário atual do computador
        hora_atual = datetime.now().strftime("%H:%M")
        
        for tarefa in lista_de_tarefas[:]:
            # Se o horário da tarefa bater com o relógio agora, dispara o e-mail
            if tarefa["hora"] == hora_atual:
                enviar_lembrete_email(tarefa["email"], tarefa["nome"])
                # Remove da lista para não enviar repetido no mesmo minuto
                lista_de_tarefas.remove(tarefa)
                
        # Aguarda 30 segundos antes de checar as horas novamente
        time.sleep(30)

@app.route("/")
def pagina_inicial():
    # Renderiza o visual e joga a lista dinâmica para a tela
    return render_template("index.html", lista_de_tarefas=lista_de_tarefas)

@app.route("/adicionar", methods=["POST"])
def adicionar_tarefa():
    # Coleta as informações digitadas pelo usuário no HTML
    email = request.form.get("email_usuario")
    nome = request.form.get("nome_tarefa")
    hora = request.form.get("hora_tarefa")
    
    # Guarda na lista para exibir na tela embaixo do quadro
    nova_tarefa = {
        "email": email,
        "nome": nome,
        "hora": hora
    }
    lista_de_tarefas.append(nova_tarefa)
    
    # Cria a mensagem de sucesso que vai aparecer no topo da tela
    flash("Tarefa cadastrada com sucesso! ⏰")
    
    # Recarrega a página atualizando as tarefas na tela
    return redirect("/")

@app.route("/deletar/<int:id_tarefa>")
def deletar_tarefa(id_tarefa):
    # Remove o item da lista baseado na posição dele
    if 0 <= id_tarefa < len(lista_de_tarefas):
        lista_de_tarefas.pop(id_tarefa)
    return redirect("/")

if __name__ == "__main__":
    # Inicia o relógio inteligente em segundo plano antes do site abrir
    threading.Thread(target=relogio_espiao, daemon=True).start()
    app.run(debug=True)