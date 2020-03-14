import requests
import datetime
import time
from bs4 import BeautifulSoup
from csv import writer

 
def main():

    MINUTES_BETWEEN_PULLS = 1
    STOP_COLLECTING_AFTER = 10080
    WEBSITE = "https://www.worldometers.info/coronavirus/"
    DATA_FILE_NAME = "current_data.csv"

    for i in range(0, STOP_COLLECTING_AFTER):
        try:
            soup_object = get_soup_object(WEBSITE)
            total_data = pull_data_from_soup(soup_object)
            append_data(total_data, DATA_FILE_NAME)
            time.sleep(MINUTES_BETWEEN_PULLS*60)
        except:
            print("Error Pulling Data From Source")
            time.sleep(300)

def get_soup_object(website):
    page = requests.get(website)
    soup = BeautifulSoup(page.text, 'html.parser')
    return soup

def pull_data_from_soup(soup_object):
    total_row = soup_object.find(class_='total_row')
    row_values = total_row.find_all('td')
    total_deaths = int(row_values[1].contents[0].replace(',', ''))
    total_cases = int(row_values[3].contents[0].replace(',', ''))
    total_active_cases = int(row_values[6].contents[0].replace(',', ''))
    total_recovered = int(row_values[5].contents[0].replace(',', ''))
    return [total_deaths, total_cases, total_recovered, total_active_cases, datetime.datetime.now()]

def append_data(total_data, data_file):
    with open(data_file, 'a+', newline='') as write_obj:
        csv_writer = writer(write_obj)
        csv_writer.writerow(total_data)

if __name__ == "__main__":
    main()

