A rotina de editores é permeada por insights e construções rápidas de pautas. Contudo, nem sempre, com a quantidade de notícias e informações que chegam às redações e são publicadas por concorrentes é possível aos editores ficarem a construção detalhada de guias de reportagem. 

Pautas, geralmente, possuem o seguinte formato:


1 - TÍTULO DE SUGESTÃO
2 - INTRODUÇÃO
3 - ABORDAGEM
4 - FONTES COMUNS
5 - PALAVRAS-CHAVES QUE POSSIBILITAM A PESQUISA DO ASSUNTO NA WEB
6 - PERGUNTAS POSSÍVEIS E BÁSICAS
7 - FONTES OFICIAIS QUE PODEM AJUDAR.


Por isso, para que uma boa pauta seja criada, perfaz necessário muito tempo do editor para fazer pesquisas e ter insights seguros. Com o tempo, a prática garante ao profissional mais agilidade por causa da experiência. Contudo, caso seja possível contar com a ajuda de um bom colaborador, tudo seria mais ágil.


Desse modo, foi criado o Bot das pautas com o intuito de ajudar o editor nesta rotina.



INFELIZMENTE

Infelizmente, o recurso de envio de e-mail não está funcionando na WEB. Somente via Jupyter. Mas vou deixar o código aqui para registro.

#------------------------------------------------------------------------/e-mail

    #
    elif parse_email_subject(ultima_mensagem):
        #
        print('Sim, tem um e-mail e um assunto, então serve para continuarmos')

        pauta_pronta = planilha.cell(2, 4).value
        corpo_email = f"""
Olá, tudo bem? Espero que sim.
Segue abaixo uma pauta para trabalho
********************************

{pauta_pronta}


********************************

Atenciosamente.

"""

        #CONSTRUIR E-MAIL E ENVIAR
        destinatario = ultima_mensagem
        assunto_do_email = f"Nova sugestão de pauta enviada por {nome_usuario}"
        print(destinatario)
        print(assunto_do_email)

        # Configuração do destinatário, assunto e corpo do e-mail
        msg = EmailMessage()
        msg["Subject"] = f"{assunto_do_email}"
        msg["From"] = f"{email}"
        msg["To"] = f"{destinatario}"
        msg.add_header("Content-Type", "text/html")
        #msg.set_payload(corpo_email)
        msg.set_content(corpo_email)

        #AQUI VAMOS CONFIGURAR A CONEXÃO SEGURA COM O SERVIDOR SMTP DE E-MAIL
        s = smtplib.SMTP("smtp.gmail.com:587")
        s.starttls()
        
        print("Chegamos até aqui no e-mail")
        
        # Envio do e-mail
        s.login(msg["From"], f"{senha_email}")
        s.sendmail(msg["From"], [msg["To"]], msg.as_string().encode("utf-8"))
        print("E-mail enviado")

        #MENSAGEM 05
        resposta = f"""
E-mail da pauta enviado com sucesso,{nome_usuario}.

Para trabalharmos com outra pauta, por favor, clique em:

/start

************
OBSERVAÇÃO: Sempre que quiser trabalhar uma nova pauta, por favor, digite e envie "/start" (sem aspas) ou clique em /start.
"""


    else:
        resposta = f"""
Você não digitou uma resposta válida. Digite novamente.
"""


#------------------------------------------------------------------------/fim
