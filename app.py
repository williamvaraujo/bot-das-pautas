#IMPORTAR AS BIBLIOTECAS NECESSÁRIAS

from flask import Flask, request
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
token_telegram = "TELEGRAM_APY_TOKEN" 


#TOKEN GOOGLE SHEETS API #ARQUIVO OCULTO NA RAIZ

GOOGLE_SHEETS_CREDENTIALS = os.environ['GOOGLE_SHEETS_CREDENTIALS']
with open("credenciais.json", mode="w") as fobj:
  fobj.write(GOOGLE_SHEETS_CREDENTIALS)
id_da_planilha = '1JMO_CCRtR7y2ntpYNZixc2Ma3e7VbtMj31zb7ymJc8c'   #ID_PLANILHA
nome_da_pag = 'NOME_PLANILHA'    #NOME_PLANILHA

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

gs_credenciais = ServiceAccountCredentials.from_json_keyfile_name("credenciais.json")
cliente = gspread.authorize(gs_credenciais)
  
#ABRINDO A PLANILHA
planilha = cliente.open_by_key(id_da_planilha).sheet1
  
#TOKEN_CHAT_GPT #TOKEN_CHATGPT
token_chatgpt = 'TOKEN_CHATGPT'

#CADASTRO DO E-MAIL
# Configurar informações da conta
email = 'email' #email
senha_email = 'senha_email' #senha_email
#-----------------------------------------------------------------

#FAZENDO A CONFIGURAÇÃO DOS CLIENTES DOS TOKENS


#AQUI, ESTAMOS CRIANDO UMA PEQUENA FUNÇÃO PARA IDENTIFICAR SE É UM LINK O QUE O USUÁRIO ENVIOU
#Vamos usar ela na função cria_pautas, no segundo ELIF
def is_link(text):
    pattern = re.compile(r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*$')
    return pattern.match(text) is not None

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
    partes = texto.split(', ')
    destinatario = partes[0]
    assunto_do_email = partes[1]
    print(destinatario)
    print(assunto_do_email)
    return destinatario, assunto_do_email


#AQUI, VAMOS FAZER A CONFIGURAÇÃO DE ACESSO AO MODELO IDEAL DE CHATPGT, INCLUSIVE, COM HEARDERS PARA ENVIAR UM POST JSON
headers_chatgpt = {'Authorization': f'Bearer {token_chatgpt}', 'content-type': 'Application/json'}
link_chatgpt = 'https://api.openai.com/v1/chat/completions'
id_modelo_chatgpt = 'gpt-3.5-turbo'


#----------------------------------------------------------------

#Função para atualização do offset do link de endpoint da API

#**OFFSET**

#Identificador da primeira atualização a ser retornada. Deve ser maior em um do que o maior entre os identificadores de atualizações recebidas anteriormente.
#Por padrão, as atualizações que começam com a atualização não confirmada mais antiga são retornadas. Uma atualização é considerada confirmada assim que getUpdates
#é chamado com um offset maior que seu update_id . O deslocamento negativo pode ser especificado para recuperar atualizações a partir de -offset update a partir do
#final da fila de atualizações. Todas as atualizações anteriores serão esquecidas.

#OBSERVAÇÃO: Este offset não tem o mesmo significado do OFFSET presente nos dados da mensagem. Este offset representa o UPDATE_ID;

#**Sempre buscaremos a última interação do usuário, por isso, o update_id e a mensagem serão as últimas do dicionário JSON. Serão [-1] para poderem ser os últimos.**

offset = 0


#--------------------------------------------------------------- INSERIR AQUI A FLASK
app = Flask(__name__)


@app.route("/bot-das-pautas", methods=['POST'])

#FUNÇÃO PARA CRIAR A PAUTA

def bot_das_pautas():
    
    primeira_mensagem = request.json #get(f'https://api.telegram.org/bot{token_telegram}/getUpdates?offset={offset + 1}').json()['result']
    nome_usuario = primeira_mensagem[-1]['message']['from']['first_name']
    update_id = primeira_mensagem[-1]['update_id']
    ultima_mensagem = primeira_mensagem[-1]['message']['text']
    chat_id = primeira_mensagem[-1]['message']['chat']['id']
    print(update_id)
    print(ultima_mensagem)
    
#---------------------------------------------------------------------------- /START --> RESPOSTA1
    if  ultima_mensagem.startswith("/") and ultima_mensagem == '/start':
        nome_usuario = mensagem[-1]['message']['from']['first_name']
        update_id = mensagem[-1]['update_id']
        #data_hora = mensagem[-1]['date']
        #texto_da_mensagem = mensagem[-1]['message']['text']
        
        
        #MENSAGEM DE BOAS-VINDAS E ORIENTAÇÃO
        orientacao = f'''
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
        '''
        
        #ENVIA A MENSAGEM01 PARA O USUÁRIO
        resposta1 = {"chat_id": chat_id, "text": orientacao}
        requests.post(f"https://api.telegram.org./bot{token_telegram}/sendMessage", data=resposta1)
        
        time.sleep(10)
        
#---------------------------------------------------------------------------/CONTINUAR --> RESPOSTA2
        
    if ultima_mensagem.startswith("/") and ultima_mensagem == '/continuar':
        #ORIENTAÇÕES PARA CONSTRUÇÃO DO ASSUNTO
        assunto = f'''
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
'''
        #ENVIA A MENSAGEM 02
        resposta2 = {"chat_id": chat_id, "text": assunto}
        requests.post(f"https://api.telegram.org./bot{token_telegram}/sendMessage", data=resposta2)        
        
        #---------------------------------------- INSERÇÃO DA PAUTA --> RESPOSTA3 --> RESPOSTA4 --> RESPOSTA5

        if not ultima_mensagem.startswith("/"):

            print('É um assunto com link e chegou no CHATGPT***********')

            recebido = f'''

Ok. Recebi a pauta. Agora é só esperar.
Posso demorar cerca de 5 minutos.
Que tal tomar um café enquanto espera. Não precisa responder nada enquanto isso.'''

            #ENVIA O ENCERRAMENTO
            retorno_pauta = {"chat_id": chat_id, "text": recebido}
            requests.post(f"https://api.telegram.org./bot{token_telegram}/sendMessage", data=retorno_pauta)  



            #VERIFICANDO A MENSAGEM COMO UM LINK E FORMATANDO PARA SER USADA NO CHATGPT
            assunto = ultima_mensagem

            corpo_mensagem = {
            'model': id_modelo_chatgpt,
            'messages': [{'role': 'user', 'content': f'''

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
'''
                 }]}

            #CONFIGURANDO O ENVIO DO PROMPT PARA O CHATGPT
            corpo_mensagem = json.dumps(corpo_mensagem)
            requisicao_chatgpt = requests.post(link_chatgpt, headers=headers_chatgpt, data=corpo_mensagem)
            print (corpo_mensagem)

            #CONFIGURANDO O ENVIO DA RESPOSTA DO CHATGPT PARA SER REPASSADA AO TELEGRAM
            retorno_chatgpt = requisicao_chatgpt.json()
            resposta_chatgpt = retorno_chatgpt['choices'][0]['message']['content']
            print(resposta_chatgpt)

            #ENVIA A RESPOSTA AO TELEGRAM
            nome_usuario = mensagem[-1]['message']['from']['first_name']
            update_id = mensagem[-1]['update_id']
            resposta3 = {"chat_id": chat_id, "text": resposta_chatgpt+f'''

*******************************************************

{nome_usuario}, podemos continuar a partir dessa pauta?

Darei cerca de dois minutos para responder.

Clique para responder:
1 - /Sim, vamos para a próxima etapa.
2 - /Nao, refaça com uma abordagem diferente
'''
                }
            requests.post(f"https://api.telegram.org./bot{token_telegram}/sendMessage", data=resposta3)

                #IDENTAÇÃO
            if ultima_mensagem.startswith("/") and ultima_mensagem == '/Sim':

                print('A etapa do sim deu certo e podemos continuar com e-mail')

                #CADASTRANDO A PAUTA NA PLANILHA
                nome_usuario = primeira_mensagem[-1]['message']['from']['first_name']
                update_id_novo = primeira_mensagem[-1]['update_id']
                data_atual = datetime.now()
                data_formatada = data_atual.strftime('%d/%m/%Y')
                planilha.insert_row([data_formatada, update_id, nome_usuario, resposta_chatgpt], 2)


                #PEGAR O E-MAIL
                desfecho1 = f'''
Tudo bem, {nome_usuario}. Vamos finalizar a sessão e enviar a pauta para algum e-mail?
Para isso, escreva o e-mail e o assunto do e-mail logo abaixo. Ambos separados por vírgula.

EXEMPLO: nome_alguem@gmail.com, Pauta sobre XXXXXXXXXXX

FIQUE ATENTO: caso você não envie um e-mail válido e um assunto em menos de 3 minutos, retornarei à etapa anterior ou encerrarei a sessão.

'''
                #ENVIA A MENSAGEM 02
                resposta4 = {"chat_id": chat_id, "text": desfecho1}
                requests.post(f"https://api.telegram.org./bot{token_telegram}/sendMessage", data=resposta4)  

                if parse_email_subject(ultima_mensagem):
                    #

                    print('Sim, tem um e-mail e um assunto, então serve para continuarmos')

                    pauta_pronta = planilha.cell(2, 4).value
                    #print("Valor da célula B2:", pauta_pronta)


                    corpo_email = f'''
Olá, tudo bem? Espero que sim.
Segue abaixo uma pauta para trabalho
********************************

{pauta_pronta}


********************************

Atenciosamente.
Fico à disposição para esclarecer dúvidas.

'''

                    #CONSTRUIR E-MAIL E ENVIAR

                    partes = ultima_mensagem.split(', ')
                    destinatario = partes[0]
                    assunto_do_email = partes[1]
                    print(destinatario)
                    print(assunto_do_email)

                    # Configuração do destinatário, assunto e corpo do e-mail
                    msg = EmailMessage()
                    msg['Subject'] = f'{assunto_do_email}'
                    msg['From'] = f'{email}'
                    msg['To'] = f'{destinatario}'
                    msg.add_header('Content-Type','text/html')
                    #msg.set_payload(corpo_email)
                    msg.set_content(corpo_email)

                    #AQUI VAMOS CONFIGURAR A CONEXÃO SEGURA COM O SERVIDOR SMTP DE E-MAIL
                    s = smtplib.SMTP('smtp.gmail.com: 587')
                    s.starttls()

                    # Envio do e-mail
                    s.login(msg['From'], senha_email)
                    s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))
                    print('E-mail enviado')

                    nome_usuario = primeira_mensagem[-1]['message']['from']['first_name']

                    #MENSAGEM 05
                    enviado = f'''
E-mail da pauta enviado com sucesso,{nome_usuario}.

Para trabalharmos com outra pauta, por favor, clique em:

/start

************
OBSERVAÇÃO: Sempre que quiser trabalhar uma nova pauta, por favor, digite e envie "/start" (sem aspas) ou clique em /start.
'''
                    #ENVIA A MENSAGEM 05
                    resposta5 = {"chat_id": chat_id, "text": enviado}
                    requests.post(f"https://api.telegram.org./bot{token_telegram}/sendMessage", data=resposta5)


############################IDENTAÇÃO DAS NEGATIVAS--------------------------------------------- /NÃO
            elif ultima_mensagem.startswith("/") and ultima_mensagem == '/Nao':
                print('a pauta não serviu, vamos refazer')
                nome_usuario = primeira_mensagem[-1]['message']['from']['first_name']

                #MENSAGEM 04
                abordagem2 = f'''
Tudo bem, {nome_usuario}.
Desculpe pelo erro.
Vamos refazer a pauta.

Para isso, clique em /continuar.

'''
                #ENVIA A MENSAGEM 02
                resposta5 = {"chat_id": chat_id, "text": abordagem2}
                requests.post(f"https://api.telegram.org./bot{token_telegram}/sendMessage", data=resposta5)


                if ultima_mensagem == '/continuar':

                    print('A última mensagem é esta')
                    print(ultima_mensagem)

            #IDENTAÇÃO DE FIM
    else:

            nome_usuario = mensagem[-1]['message']['from']['first_name']

            #ENCERRAR ATENDIMENTO
            encerrar = f'''
Desculpe, {nome_usuario}.
Precisaremos encerrar o atendimento.
Para recomeçar,  clique em /start.

Muito obrigado.
'''
            #ENVIA O ENCERRAMENTO
            finalizar = {"chat_id": chat_id, "text": encerrar}
            requests.post(f"https://api.telegram.org./bot{token_telegram}/sendMessage", data=finalizar)  



    return "Bot funcionando"
    
    
#-------------------------------------------------- RODA O BOT
