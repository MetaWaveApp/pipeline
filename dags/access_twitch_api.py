import requests
import json
import logging
import os

base_path = os.path.dirname(os.path.abspath(__file__))
file_twit = os.path.join(base_path, 'twitchfile.json')
file_topg = os.path.join(base_path, "top_games_views.json")

def saveSession(session):
    try:
        with open("sessionfile.json", "w") as f:
            f.write(json.dumps(session))
            return True
    except:
        return False


def getSession():
    try:
        with open("sessionfile.json", "r") as f:
            return json.loads(f.read())
    except:
        return False


def openSession():

    clientVars = { 'id': '', 'secret':'' }
    
    try:
        logging.info("Tentando leitura de arquivo "+file_twit)
        with open(file_twit, "r") as f:
            logging.info("Iniciando leitura de arquivo "+file_twit)
            content = f.read()
            logging.info("Leu o arquivo "+file_twit+": "+content)
            clivars = json.loads(content)
            clientVars['id'] = clivars['cliente']
            clientVars['secret'] = clivars['secret']
    except Exception as e:
        logging.error("Erro ao tentar abrir ou ler o arquivo twitchfile.json")
        logging.error(f"Tipo: {type(e).__name__}")
        logging.error(f"Mensagem: {str(e)}")
        return False

    url = 'https://id.twitch.tv/oauth2/token'

    data = {
        'client_id': clientVars['id'],
        'client_secret': clientVars['secret'],
        'grant_type': 'client_credentials'
    }

    response = requests.post(url, data=data)

    if(response.status_code == 401):
        logging.error("Erro 401 - Erro ao tentar gerar acess_token")
        return False

    logging.info("A resposta do servidor veio com um codigo: "+str(response.status_code))

    response.raise_for_status()

    session = response.json()['access_token']
    sessObj = { "session": session, "clientVars":clientVars }

    saveSession(sessObj)

    return sessObj


def dentro_de_10_porcento(valor: int, comparacao: float) -> bool:
    limite_inferior = comparacao * 0.9
    limite_superior = comparacao * 1.1
    return limite_inferior <= valor <= limite_superior


def calcularProximaPagina(maiorStream, menorStream, media):
    calc = (
            maiorStream['viewer_count'] < 1000 
            and dentro_de_10_porcento(maiorStream['viewer_count'], media)
            and dentro_de_10_porcento(menorStream['viewer_count'], media)
        )
    if calc:
        log = "Usou a média em: "+ str(maiorStream['viewer_count'])+" e "+str(menorStream['viewer_count'])
        print(log)
        logging.info(log)
    else:
        logging.info("Não calculou pela media. Pegou todos os espectadores.")
    return calc


def addViewersInGame(game, session):

    logging.info("Calculando quantidade views no jogo " + game['name'] + " - " + game['id'])

    tem_proxima_pagina = False
    cursor = ""
    totalViews = 0

    while True:

        media = 0
        soma = 0

        url = "https://api.twitch.tv/helix/streams?game_id="+game['id']+"&first=100"

        if tem_proxima_pagina:
            url += "&before="+cursor

        response = requests.get(url, 
            headers={
                "Authorization":"Bearer "+session['session'],
                "Client-Id":session['clientVars']['id']
            }
        )

        data = response.json()

        streams = data['data']

        for stream in streams:
            soma += stream['viewer_count']

        totalViews += soma
        totalStreams = len(streams)
        media = soma / totalStreams if streams else 0

        tem_proxima_pagina = (
            totalStreams == 100 and
            "pagination" in data and
            "cursor" in data["pagination"] and
            calcularProximaPagina(streams[0], streams[99], media)
        )

        if tem_proxima_pagina:
            cursor = data['pagination']['cursor']
            continue
        break 
    
    game['totalViews'] = totalViews
    logging.info(game['name']+" - total: "+str(totalViews))



def getTop50():

    try:
        
        session = openSession()
        
        logging.info("Iniciando a extração dos top 50 jogos ...")
        
        if session == False:
            raise ValueError("Erro ao tentar gerar sessão da twitch")

        # recuperar os top 50 jogos

        response = requests.get("https://api.twitch.tv/helix/games/top?first=50",
            headers={
                "Client-Id":session['clientVars']['id'],
                "Authorization":"Bearer "+session['session']
            }
        )

        if response.status_code == 401:
            raise ValueError("401 - Requisição não autorizada pela twitch")
        
        if response.status_code == 404:
            raise ValueError("404 - Rota não encontrada na twitch")
        
        response.raise_for_status()
        games = response.json()['data']
        
        for game in games:
            addViewersInGame(game=game, session=session)

        with open(file_topg, "w") as f:
            json.dump(games, f, indent=2)

    except Exception as e:
        logging.error(f"Erro encontrado: {e}")
        raise 
