import tweepy
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as md
import dateutil
import datetime
import time
from datetime import timedelta

def main():

        POSTS_TO_RUN_FOR = 48 * 365 * 10
        DATA_FILE = "current_data.csv"

        run_analysis(POSTS_TO_RUN_FOR, DATA_FILE)

def create_graphs(data_file):
    corona_data = pd.read_csv(data_file)
    corona_data['datetime_object'] = pd.to_datetime(corona_data['time'])
    corona_data = corona_data.sort_values(by=['datetime_object'])
    corona_data['mortality_rate'] = corona_data['deaths']/(corona_data['recovered'] + corona_data['deaths'])
    last_day = corona_data.loc[corona_data['datetime_object'] > (datetime.datetime.now() - timedelta(days=1))]
    last_week = corona_data.loc[corona_data['datetime_object'] > (datetime.datetime.now() - timedelta(days=7))]
    last_month = corona_data.loc[corona_data['datetime_object'] > (datetime.datetime.now() - timedelta(days=30))]

    total_display_dictionary = {
        "cases": ("purple", "Total Cases"),
        "active": ("blue", "Active"),
        "deaths": ("red", "Deaths"),
        "recovered": ("green", "Recovered")
     }

    last_day_dictionary = {
        "active": ("blue", "Active"),
        "deaths": ("red", "Deaths"),
        "recovered": ("green", "Recovered")
    }
    deaths_dictionary = {
        "deaths": ("red", "Deaths")
    }

    active_dictionary = {
        "active": ("blue", "Active")
    }

    all_graph_name = create_graph(corona_data, total_display_dictionary, "full_period", '%m-%d', "Date", "Coronavirus Cases To Date", "Cumulative Reported Coronavirus Cases", 15)
    all_deaths_name = create_graph(corona_data, deaths_dictionary, "full_deaths", '%m-%d', "Date", "Coronavirus Deaths To Date", "Total Reported Coronavirus Deaths", 15)
    all_active_name = create_graph(corona_data, active_dictionary, "full_active", '%m-%d', "Date", "Coronavirus Cases Active", "Active Worldwide Coronavirus Cases", 15)
    day_graph_name = create_graph(last_day, last_day_dictionary, "last_day", '%H:%M', "Time (EST)", "Coronavirus Cases To Date", "Last Day Cumulative Reported Coronavirus Cases", 24)

    week_graph_name = create_graph(last_week, total_display_dictionary, "last_week", '%m-%d %H:%M', "Date and Time (EST)", "Coronavirus Cases To Date", "Last Week Reported Cumulative Coronavirus Cases", 14)
    month_graph_name = create_graph(last_month, total_display_dictionary, "last_month", '%m-%d', "Date", "Coronavirus Cases To Date", "Last Month Reported Cumulative Coronavirus Cases", 30)

    mortality_display_dictionary = {
        "mortality_rate": ("red", "Cumulative Mortality Rate")
    }
        
    mortality_graph_name = create_graph(corona_data, mortality_display_dictionary, "mortality", '%m-%d', "Date", "Death Rate", "Cumulative Mortality Rate", 20)
    return all_graph_name, day_graph_name, week_graph_name, month_graph_name, mortality_graph_name, all_deaths_name, all_active_name

def create_graph(corona_subset, total_display_dictionary, folder, date_format, xlab, ylab, title, interval):
        plt.figure(figsize=(12,5))
        dates = [dateutil.parser.parse(s) for s in corona_subset['time']]
        plt.xticks(rotation=25)
        plt.title(title)
        ax = plt.gca()
        plt.locator_params(axis='x', nbins=interval)
        ax.set_xlabel(xlab)
        ax.set_ylabel(ylab)
        xfmt = md.DateFormatter(date_format)
        ax.xaxis.set_major_formatter(xfmt)
        for key in total_display_dictionary:
                values = total_display_dictionary[key]
                plt.plot(dates, corona_subset[key], "-", color=values[0], label=values[1])
        plt.legend(bbox_to_anchor=(1.01, 1), loc='upper left', borderaxespad=0.)
        plt.tight_layout()
        image_name = f"graphs/{folder}/{current_time_string().replace(' ', '').replace('.', '').replace(':', '').replace('-', '')}.png"
        plt.savefig(image_name)
        plt.close()
        return image_name

def get_authenticated_api():

        f=open("twitter_auth.txt","r")
        lines=f.readlines()
        cus_key=lines[0].rstrip()
        cus_secret=lines[1].rstrip()
        acc_token=lines[2].rstrip()
        acc_secret=lines[3].rstrip()

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

def update_and_wait(graph):
        api = get_authenticated_api()
        api.update_with_media(graph, status = f"{format(get_total_cases(), ',d')} #Coronavirus cases as of {current_time_string()}")

def current_time_string():
    time_now = datetime.datetime.now() 
    return f"{time_now.year}-{time_now.month}-{time_now.day} {time_now.hour}:{time_now.minute}:{time_now.second}"

def get_total_cases():
        data_file = "current_data.csv"
        corona_data = pd.read_csv(data_file)
        return corona_data['cases'][len(corona_data)-1]

def post_graphs(full, day, week, month, mortality, all_deaths, all_active):
        while datetime.datetime.now().minute != 10:
                time.sleep(5)
        update_and_wait(full)
        while datetime.datetime.now().minute != 20:
                time.sleep(5)
        update_and_wait(mortality)
        while datetime.datetime.now().minute != 30:
                time.sleep(5)
        update_and_wait(all_deaths)
        while datetime.datetime.now().minute != 40:
                time.sleep(5)
        update_and_wait(all_active)
        while datetime.datetime.now().minute != 50:
                time.sleep(5)
        update_and_wait(day)

        # update_and_wait(api, week)
        # update_and_wait(api, month)

def run_analysis(posts_to_run_for, data_file):
        for i in range(0, posts_to_run_for):
                full, day, week, month, mortality, all_deaths, all_active = create_graphs(data_file)
                post_graphs(full, day, week, month, mortality, all_deaths, all_active)

if __name__ == "__main__":
        main()
