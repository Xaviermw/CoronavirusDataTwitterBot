import requests
import datetime
import time
import tweepy
import pandas as pd
import math
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from csv import writer

def main():

    MINUTES_BETWEEN_PULLS = 1
    STOP_COLLECTING_AFTER = 10080
    WEBSITE = "https://www.worldometers.info/coronavirus/"
    DATA_FILE_NAME = "country_data.csv"

    for i in range(0, STOP_COLLECTING_AFTER):
        date = datetime.datetime.now()
        while (date.minute != 0):
            time.sleep(5)
        try: 
            soup_object = get_soup_object(WEBSITE)
            corona_stats = pull_data(soup_object)
            country_lookup = pd.read_csv('country_mapping.csv')
            total_graph = generate_world_map(corona_stats, country_lookup, date, "TotalCases", "Cumulative Total", "Greens")
            post_twitter(total_graph)
            while (datetime.datetime.now().minute != 35):
                time.sleep(5)
            active_graph = generate_world_map(corona_stats, country_lookup, date, "ActiveCases", "Active", "Blues")
            post_twitter(active_graph)

        except:           
            print("Error Pulling Data From Source")
            time.sleep(300)
        time.sleep(60*5)

def get_soup_object(website):
    page = requests.get(website)
    soup = BeautifulSoup(page.text, 'html.parser')
    return soup

def pull_data(soup_object):

    table = soup_object.find(id="main_table_countries")
    rows = len(table.find_all('tr'))
    corona_table = pd.DataFrame(columns=range(0,9), index = range(0, rows-1))

    header_list = []
    for header in table.find_all('th'):
        header_list.append(header.get_text())

    corona_table.set_axis(header_list, axis=1, inplace=True)

    row_marker = 0
    for row in table.find_all('tr')[1:rows]:
        column_marker = 0
        columns = row.find_all('td')
        for column in columns:
            corona_table.iat[row_marker,column_marker] = column.get_text()
            column_marker += 1
        row_marker += 1

    return corona_table

def generate_world_map(case_table, country_lookup, date, metric, plot_title, color):
    world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
    country_counts = []
    for index, row in country_lookup.iterrows():
        if row['data_country'] == "NO CASES":
            country_counts.append(0)
        else:
            country_cases = case_table[case_table["Country,Other"] == row['data_country']][metric].values
            country_counts.append(math.log(int(country_cases.item(0).replace(',', ''))+1))

    world = world.sort_values(by=['name'])     
    world['corona_count'] = country_counts

    world_heat_map = geoplot.choropleth(
        world, hue=world['corona_count'],
        cmap=color, figsize=(20, 10), legend=True, legend_kwargs = {'label': f'Log of {plot_title} Coronovirus Cases'}
    )

    graph_name = f"graphs/countries/{metric}/{date.year}-{date.month}-{date.day}-{date.hour}.png"
    plt.title(f"{plot_title} Coronovirus Cases as of {date.year}-{date.month}-{date.day} {date.hour}:00 (EST)", fontdict={'fontsize' : 30})
    world_heat_map.get_figure().savefig(graph_name)
    return graph_name

def get_authenticated_api():

    f=open("twitter_auth.txt","r")
    lines=f.readlines()
    cus_key=lines[0]
    cus_secret=lines[1]
    acc_token=lines[2]
    acc_secret=lines[3]

    auth_keys = { 
        "consumer_key"        : cus_key,
        "consumer_secret"     : cus_secret,
        "access_token"        : acc_token,   
        "access_token_secret" : acc_secret
    }   

    auth = tweepy.OAuthHandler( auth_keys['consumer_key'], auth_keys['consumer_secret'])
    auth.set_access_token( auth_keys['access_token'], auth_keys['access_token_secret'])
    api = tweepy.API(auth)
    return api

def get_total_cases():
    data_file = "current_data.csv"
    corona_data = pd.read_csv(data_file)
    return corona_data['cases'][len(corona_data)-1]

def current_time_string():
    return str(datetime.datetime.now())

def post_twitter(graph):

    api = get_authenticated_api()
    api.update_with_media(graph, status = f"{'{:.7f}'.format(get_total_cases()/7530000000)}% of the world has gotten Coronavirus as of {current_time_string()}")

if __name__ == "__main__":
    main()