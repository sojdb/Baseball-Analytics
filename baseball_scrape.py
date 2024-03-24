### BASEBALL REFERENCE SCRAPE ###
import bs4
from urllib.request import Request,urlopen
import requests
from bs4 import BeautifulSoup as soup
import pandas as pd
from time import sleep
from io import StringIO
import re
from unidecode import unidecode
from os import listdir

teams_abbr = {
    "Arizona D'Backs" : 'ARI',
    "Los Angeles Dodgers" : 'LAD',
    "San Diego Padres": 'SDP',
    "San Francisco Giants": 'SFG',
    "Colorado Rockies": 'COL',
    "Houston Astros" : 'HOU',
    "Texas Rangers" : 'TEX',
    "Seattle Mariners": 'SEA',
    "Los Angeles Angels": 'LAA',
    "Oakland Athletics": 'OAK',
    "Milwaukee Brewers": 'MIL',
    "Chicago Cubs": 'CHC',
    "Cincinnati Reds": 'CIN',
    "Pittsburgh Pirates": 'PIT',
    "St. Louis Cardinals": 'STL',
    "Minnesota Twins": 'MIN',
    "Detroit Tigers": 'DET',
    "Cleveland Guardians": 'CLE',
    "Chicago White Sox": 'CHW',
    "Kansas City Royals": 'KCR',
    "Atlanta Braves": 'ATL',
    "Philadelphia Phillies": 'PHI',
    "Miami Marlins": 'MIA',
    "New York Mets": 'NYM',
    "Washington Nationals": 'WSN',
    "Baltimore Orioles": 'BAL',
    "Tampa Bay Rays": 'TBR',
    "Toronto Blue Jays": 'TOR',
    "New York Yankees": 'NYY',
    "Boston Red Sox": 'BOS'
}

def getSoup(url):
    req = Request(url=url,headers={'User-Agent': 'Mozilla/6.0'})
    uClient = urlopen(req)
    #grabs everything from page
    html = uClient.read()
    #close connection
    uClient.close()
    #does HTML parsing
    parse = soup(html, "html.parser")
    return parse

def get_player_url(first_name, last_name):
    text = getSoup("https://www.baseball-reference.com/players/{0}/".format(last_name[0].lower()))
    sleep(2)
    players = str(text.find('div', {'id':'div_players_'})).split('<p>')
    for player in players:
        if (first_name.lower() in player.lower()) & (last_name.lower() in player.lower()):
            url = re.search('"(.*)"', player).group(1)
            break
    return url

def get_player_last5(first_name, last_name):
    url = get_player_url(first_name, last_name)
    text = getSoup("https://www.baseball-reference.com{0}#all_last5".format(url))
    sleep(2)
    games = StringIO(str(text.find('table', {'id':'last5'})))
    df = pd.read_html(games)[0]
    df.insert(0, 'Name', last_name + ', ' + first_name)
    df.to_csv(r"C:\Users\joshm\OneDrive\Documents\NSC\Spring 2024\DATA Capstone\test.csv", index=False)

def get_lineups():
    ### NEED TO FIGURE OUT HOW TO GRAB CURRENT LINEUP FOR THE DAY ###
    ### https://www.baseball-reference.com/teams/ARI/2023-lineups.shtml should be best ###
    ### Biggest issue is knowing when lineups are posted to here (we need before game), test during spring training? ###
    lineup = 0
    return lineup

def get_40man(team, season):
    text = getSoup("https://www.baseball-reference.com/teams/{0}/{1}-roster.shtml#all_the40man".format(team, season))
    sleep(2)
    roster = StringIO(unidecode(str(text.find('table', {'id':'the40man'}))))
    df = pd.read_html(roster)[0]
    df = df.drop(df.index.to_list()[-1])
    df.insert(3, 'Team', team)
    df.insert(3, 'Season', season)
    if 'roster.csv' in listdir(r"C:\Users\joshm\OneDrive\Documents\NSC\Spring 2024\DATA Capstone"):
        df.to_csv(r"C:\Users\joshm\OneDrive\Documents\NSC\Spring 2024\DATA Capstone\roster.csv", index=False, header=False, mode='a')
    else:
        df.to_csv(r"C:\Users\joshm\OneDrive\Documents\NSC\Spring 2024\DATA Capstone\roster.csv", index=False)

def get_batting_gamelog(first_name, last_name, season):
    player_id = get_player_url(first_name, last_name)[11:20]
    text = getSoup("https://www.baseball-reference.com/players/gl.fcgi?id={0}&t=b&year={1}".format(player_id, season))
    sleep(2)
    games = StringIO(str(text.find('table', {'id':'batting_gamelogs'})))
    df = pd.read_html(games)[0]
    df = df.drop(df.index.to_list()[-1])
    df.insert(0, 'Name', last_name + ', ' + first_name)
    df = df[df['Tm'] != 'Tm']
    df.to_csv(r"C:\Users\joshm\OneDrive\Documents\NSC\Spring 2024\DATA Capstone\test.csv", index=False)

def get_pitching_gamelog(first_name, last_name, season):
    player_id = get_player_url(first_name, last_name)[11:20]
    text = getSoup("https://www.baseball-reference.com/players/gl.fcgi?id={0}&t=p&year={1}".format(player_id, season))
    sleep(2)
    games = StringIO(str(text.find('table', {'id':'pitching_gamelogs'})))
    df = pd.read_html(games)[0]
    df = df.drop(df.index.to_list()[-1])
    df.insert(0, 'Name', last_name + ', ' + first_name)
    df = df[df['Tm'] != 'Tm']
    df.to_csv(r"C:\Users\joshm\OneDrive\Documents\NSC\Spring 2024\DATA Capstone\test.csv", index=False)

def get_schedule():
    text = getSoup("https://www.baseball-reference.com/leagues/MLB-schedule.shtml")
    sleep(2)
    games = str(text.find('div', {'id':'div_3941183720'}))
    game_list = games.split("<div>")[1:]
    team_list = []
    dates = re.findall("\n<h3>(.*)</h3>\n", games)
    for k, i in enumerate(game_list):
        teams = re.findall(">(.*)</a>", i)
        date = dates[k]
        for j in range(0,len(teams),2):
            team_list.append([date, teams[j], teams[j+1]])
    df = pd.DataFrame(team_list, columns=['Date', 'Away', 'Home'])
    df.to_csv(r"C:\Users\joshm\OneDrive\Documents\NSC\Spring 2024\DATA Capstone\2024schedule.csv", index=False)

def main():
    #get_player_last5('Clayton', 'Kershaw')
    get_batting_gamelog('Mookie', 'Betts', 2024)
    # for team in teams_abbr:
    #     get_40man(teams_abbr[team], '2023')
    print('o')
main()