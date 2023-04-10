#IMPORTAR AS BIBLIOTECAS NECESSÁRIAS

from flask import Flask, request
from gunicorn.config import Config
import requests
import gspread
import json
import re
import os
import time
import smtplib
from email.message import EmailMessage
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
#------------------------------------------------------------------

#ACESSANDO OS TOKENS

#TOKEN TELEGRAM #TELEGRAM_APY_TOKEN
token_telegram = os.environ["TELEGRAM_APY_KEY"]


#TOKEN GOOGLE SHEETS API #ARQUIVO OCULTO NA RAIZ
GOOGLE_SHEETS_CREDENTIALS = os.environ["GOOGLE_SHEETS_CREDENTIALS"]
with open("credenciais.json", mode="w") as fobj:
  fobj.write(GOOGLE_SHEETS_CREDENTIALS)
id_da_planilha = "1JMO_CCRtR7y2ntpYNZixc2Ma3e7VbtMj31zb7ymJc8c"   #ID_PLANILHA
nome_da_pag = "NOME_PLANILHA"    #NOME_PLANILHA
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
gs_credenciais = ServiceAccountCredentials.from_json_keyfile_name("credenciais.json")
cliente = gspread.authorize(gs_credenciais)
  
#ABRINDO A PLANILHA
planilha = cliente.open_by_key(id_da_planilha).sheet1
  
#TOKEN_CHAT_GPT #TOKEN_CHATGPT
token_chatgpt = os.environ["TOKEN_CHATGPT"]
headers_chatgpt = {"Authorization": f"Bearer {token_chatgpt}", "content-type": "Application/json"}
link_chatgpt = "https://api.openai.com/v1/chat/completions"
id_modelo_chatgpt = "gpt-3.5-turbo"

#CADASTRO DO E-MAIL
# Configurar informações da conta
email = os.environ["email"] #email
senha_email = os.environ["senha_email"] #senha_email
#-----------------------------------------------------------------
#################################################################

#FAZENDO A CONFIGURAÇÃO DOS CLIENTES DOS TOKENS

#AQUI VAMOS CRIAR UMA FUNÇÃO PARA IDENTIFICAR E-MAILS NO STRING
def parse_email_subject(text):
    if "@" in text:
        email, _, subject = text.partition(",")
        return email.strip(), subject.strip()
    else:
        # caso não seja um e-mail, retorne None para indicar que não há e-mail
        return None, None
    
#AQUI VAMOS CRIAR UMA FUNÇÃO PARA DIVIDIR O QUE FOI DIGITADO E PREENCHER OS DADOS PARA ENVIO DO E-MAIL
def dividir_texto(texto):
    partes = texto.split(", ")
    destinatario = partes[0]
    assunto_do_email = partes[1]
    print(destinatario)
    print(assunto_do_email)
    return destinatario, assunto_do_email
    
#AQUI, VAMOS FAZER A CONFIGURAÇÃO DE ACESSO AO MODELO IDEAL DE CHATPGT, INCLUSIVE, COM HEARDERS PARA ENVIAR UM POST JSON

#----------------------------------------------------------------

#Função para atualização do offset do link de endpoint da API
#**OFFSET**
#Identificador da primeira atualização a ser retornada. Deve ser maior em um do que o maior entre os identificadores de atualizações recebidas anteriormente.
#Por padrão, as atualizações que começam com a atualização não confirmada mais antiga são retornadas. Uma atualização é considerada confirmada assim que getUpdates
#é chamado com um offset maior que seu update_id . O deslocamento negativo pode ser especificado para recuperar atualizações a partir de -offset update a partir do
#final da fila de atualizações. Todas as atualizações anteriores serão esquecidas.
#OBSERVAÇÃO: Este offset não tem o mesmo significado do OFFSET presente nos dados da mensagem. Este offset representa o UPDATE_ID;
#**Sempre buscaremos a última interação do usuário, por isso, o update_id e a mensagem serão as últimas do dicionário JSON. Serão [-1] para poderem ser os últimos.**

#offset = 0
##############################################################################################################################
##############################################################################################################################





#FUNÇÃO DE FUNCIONAMENTO DO BOT

app = Flask(__name__)
@app.route("/bot-das-pautas", methods=["POST"])
def bot_das_pautas():
    #
    primeira_mensagem = request.json
    ultima_mensagem = primeira_mensagem["message"]["text"]
    chat_id = primeira_mensagem["message"]["chat"]["id"]
    nome_usuario = primeira_mensagem["message"]["from"]["first_name"]  
    print(primeira_mensagem)
    print(ultima_mensagem)
    print(chat_id)
    print(nome_usuario)
    resposta = "Você não digitou uma mensagem válida. Tente /start novamente"
#---------------------------------------------------------------------------- /START --> RESPOSTA1
    if ultima_mensagem == "/start":
        #MENSAGEM DE BOAS-VINDAS E ORIENTAÇÃO
        resposta = f"""
Olá, {nome_usuario}, tudo bem?
Antes de continuar, preciso que fique atento ao modo de uso da ferramenta:
1 - Responda apenas o que for solicitado pelo bot;
2 - AGUARDE O RETORNO PARA A DEMANDA, pois podemos demorar alguns segundos para responder;
3 - Compreenda que sou uma ferramenta colaborativa. Mesmo após obter os resultados, será necessário revisá-los para saber se consegui atender suas expectativas;
4 - Tenha em mãos algum link sobre a informação para que o BOT seja contextualizado com fatos dos dias atuais;
5 - Sempre que quiser resetar a conversa, digite e envie "/start" (sem aspas);
6 - Você pode pedir que a pauta seja refeita quantas vezes quiser, mas lembre-se de que quanto mais o assunto for detalhado e tiver links de balizamento melhor;
7 - Esta ferramenta foi desenvolvida pelo jornalista Will Araújo.
*************************
Para continuarmos, clique no link a seguir: /continuar.
Será um prazer ajudar.
  """

#---------------------------------------------------------------------------/CONTINUAR --> RESPOSTA2
        
    elif ultima_mensagem == "/continuar":
        #      
        #ORIENTAÇÕES PARA CONSTRUÇÃO DO ASSUNTO
        resposta = f"""
Vamos lá. 

Por favor, insira abaixo um assunto, um link para contextualização e uma editoria para balizar o viés de abordagem da pauta.


**************
LEMBRE-SE: links são importantes para que eu seja atualizado sobre o assunto e apresente informações mais assertivas.
Além disso, sempre aguarde o retorno, pois a construção da pauta pode demorar até 3 minutos.
**************

EXEMPLO: 
Gostaria de obter uma pauta sobre o assunto: "XXXXXXX XXX XXXXXXXXXXXXX"
Para balizar a abordagem e contexto, use o link: https://XXXX.XXXX.XXXX/XXXX como referência.
A abordagem precisa ser direcionada para a editoria: ECONOMIA.

OBSERVAÇÃO: quanto mais informação, mais assertiva a pauta. Por isso, seja claro sobre seus objetivos.
    """
    
#---------------------------------------- INSERÇÃO DA PAUTA --> RESPOSTA3 --> RESPOSTA4 --> RESPOSTA5

    elif not ultima_mensagem.startswith("/") and not "@" in ultima_mensagem:
        print("É um assunto com link e chegou no CHATGPT***********")
        print(ultima_mensagem)
                
        #VERIFICANDO A MENSAGEM COMO UM LINK E FORMATANDO PARA SER USADA NO CHATGPT
        assunto = ultima_mensagem
        print("chegou até o corpo da mensagem")
        
        corpo_mensagem = {
        "model": id_modelo_chatgpt,
        "messages": [{"role": "user", "content": f"""
Olá, gostaria de trabalhar com você para que construa uma pauta jornalística. Por isso, peço que entre em um modo que familiarizado com 
o jornalismo brasileiro.

Este é o assunto: {assunto}

A pauta precisa ter o seguinte formato:
1 - Produza uma sugestão de um título sobre o assunto com até 62 caracteres. Este tópico será chamado TÍTULO;
2 - Produza uma introdução e contextualização a partir do link enviado. Pode ser também um resumo. Este tópico será chamado INTRODUÇÃO;
3 - Produza uma abordagem semelhante à do link e somada a uma nova, explicando o que não foi explorado pelo texto, mas poderia ser apurado. Coloque a abordagem direciona à editoria que o usuário mencionou. Este tópico será chamado ABORDAGEM;
4 - Sugira ao menos 3 tipos de profissionais ou profissões que podem servir de fonte para a apuração. Junto, coloque o endereço de e-mail público de cada um, caso exista. Na ausência de nomes, indique profissões ou cargos que podem servir de fontes. Este tópico será chamado FONTES DE SUGESTÃO;
5 - Indique uma palavra-chave a ser pesquisa no Google e que pode fornecer mais links sobre o assunto. Este tópico será chamado USE ESTA PALAVRA-CHAVE E PESQUISE MAIS INFORMAÇÕES COM ELA;
6 - Sugira ao menos cinco perguntas com base no assunto e editoria que foi enviada. Este tópico será chamado PERGUNTAS DE SUGESTÃO;
7 - Indique quais secretarias do governo Federal, Estadual ou Municipal brasileiro que podem ajudar no assunto. Explique porque buscar essa fonte oficial é importante e qual a função dela. Este tópico será chamado FONTES OFICIAIS.
"""
           }]}
        
        #CONFIGURANDO O ENVIO DO PROMPT PARA O CHATGPT

        corpo_mensagem = json.dumps(corpo_mensagem)
        requisicao_chatgpt = requests.post(link_chatgpt, headers=headers_chatgpt, data=corpo_mensagem)
        teste = requisicao_chatgpt.json()
        print(f"Status code: {requisicao_chatgpt.status_code}")
        print(f"Resposta: {requisicao_chatgpt.text}")
        print(teste)
        print("Foi enviado o prompt ao ChatGPT")
        
        #CONFIGURANDO O ENVIO DA RESPOSTA DO CHATGPT PARA SER REPASSADA AO TELEGRAM
        
        resposta_chatgpt = None
            
        while not resposta_chatgpt:
            retorno_chatgpt = requisicao_chatgpt.json()
            resposta_chatgpt = retorno_chatgpt["choices"][0]["message"]["content"]
            time.sleep(5)

        
            print(resposta_chatgpt)
        print("Passou pelo While")        
        
        #CADASTRANDO A PAUTA NA PLANILHA
        nome_usuario = primeira_mensagem["message"]["from"]["first_name"]
        update_id = primeira_mensagem["update_id"]
        chat_id = primeira_mensagem["message"]["chat"]["id"]
        data_atual = datetime.now()
        data_formatada = data_atual.strftime("%d/%m/%Y")
        planilha.insert_row([data_formatada, update_id, nome_usuario, resposta_chatgpt], 2)
        
        #ENVIA A RESPOSTA AO TELEGRAM
        resposta = f"""{resposta_chatgpt}+
*******************************************************

{nome_usuario}, podemos continuar a partir dessa pauta?

Clique para responder:
1 - /Sim, vamos para a próxima etapa.
2 - /Nao, refaça com uma abordagem diferente
"""

#----------------------------------------------------------------------/Sim
    #IDENTAÇÃO
    elif ultima_mensagem == "/Sim":
        #
        print("A etapa do sim deu certo e podemos continuar com e-mail")

        #PEGAR O E-MAIL
        resposta = f"""
Tudo bem, {nome_usuario}. Vamos finalizar a sessão e enviar a pauta para algum e-mail?
Para isso, escreva o e-mail e o assunto do e-mail logo abaixo. Ambos separados por vírgula.

EXEMPLO: nome_alguem@gmail.com

FIQUE ATENTO: caso você não envie um e-mail válido e um assunto em menos de 3 minutos, retornarei à etapa anterior ou encerrarei a sessão.

"""
#------------------------------------------------------------------------/Nao

    elif ultima_mensagem == "/Nao":
        print('a pauta não serviu, vamos refazer')

        #MENSAGEM
        resposta = f"""
Tudo bem, {nome_usuario}.
Desculpe pelo erro.
Vamos refazer a pauta.

Para isso, clique em /continuar.

"""


    
    
    #ENVIA A MENSAGEM PARA O USUÁRIO
    novo_texto = {"chat_id": chat_id, "text": resposta}
    requests.post(f"https://api.telegram.org./bot{token_telegram}/sendMessage", data=novo_texto)
    return "Ok"
