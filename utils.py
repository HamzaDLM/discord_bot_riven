import requests
import json
import random
from bs4 import BeautifulSoup as BSHTML
import urllib


def random_champ(patch="12.6.1") -> dict:
    """Return a random champion and their image"""

    url = f"http://ddragon.leagueoflegends.com/cdn/{patch}/data/en_US/champion.json"
    response = requests.get(url)
    result = json.loads(response.text)
    champions = result["data"].keys()
    champion = random.choice(list(champions))
    champ_img = result["data"][champion]["image"]["full"]
    img_url = f"https://ddragon.leagueoflegends.com/cdn/{patch}/img/champion/{champ_img}"
    
    return {
        "champion": champion,
        "img_url": img_url
    }


def random_quote() -> dict :
    """Return a random voice quote from a champion"""
    
    champion = random_champ()
    champ = champion["champion"]
    page = urllib.request.urlopen(f'https://leagueoflegends.fandom.com/wiki/{champ}/LoL/Audio')
    soup = BSHTML(page)
    images = soup.find_all('audio')
    results = []
    for image in images:
        lt = str(image).split()
        url = lt[20][5:-1]
        results.append(url)

    quote = random.choice(results)

    return {
        "quote_url": quote,
        "champion":champion["champion"],
        "img_url":champion["img_url"]
    }


def opgg_username(username) -> dict:
    """Return opgg stats for a username with elo icon"""

    server = "euw"
    page = 'https://' + server + '.op.gg/summoner/userName=' + username.replace(" ","+")

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    html = requests.get(page, headers=headers)

    soup = BSHTML(html.content, 'html.parser')

    rank = soup.find("div", {"class": "tier-rank"}).contents[0:3]
    if rank is not None:
        rank = ''.join(rank)
    else:
        rank = "Unranked"

    LP = soup.find("span", {"class": "lp"})
    if LP is not None:
        LP = ''.join(LP)
    else:
        LP = "0 LP"

    wr = list(soup.find("span", {"class": "win-lose"}))
    if wr is not None:
        winratio = f"{wr[0]} {wr[4]} {wr[6]} {wr[10]}{wr[12]}"
    else:
        winratio = "0%"

    elo_img = soup.find("div", {"class": "medal"})
    elo_img = elo_img.find("img")

    return {
        "elo": rank + "\n" + LP + "\n" + winratio,
        "img": elo_img["src"]
    }