
import imageio
import datetime
import time
import tweepy


def main():

	images = []

	while True:
		while (datetime.datetime.now().hour % 8 != 0 or datetime.datetime.now().minute != 0):
			time.sleep(5)
		date = datetime.datetime.now()
		gif_name = f'graphs/country_gifs/{date.year}-{date.month}-{date.day}-{date.hour}.gif'
		with imageio.get_writer(gif_name, duration=5, mode='I') as writer:
			for year in range(2020, 2021):
				for month in range(3, 13):
					for day in range (1, 32):
						for hour in range (1, 25):
							try:
								image = imageio.imread(f"graphs/countries/{year}-{month}-{day}-{hour}.png")
								writer.append_data(image)
							except:
								pass
		post_twitter(gif_name)
		time.sleep(60*5)

def get_authenticated_api():
    auth_keys = { 
        "consumer_key"        : "63b6hMB71bKkPOfDJV0boJCs1",
        "consumer_secret"     : "7XQVOTQ4EQwrT4d8NG7ryuuwKN2ALKPZfSTrhKvCxR93ukTH5d",
        "access_token"        : "799378974-4Qwo6g9k8dx58kmJ8Vyx83UHZt5647xe4eXtSLX9",   
        "access_token_secret" : "rCsf5boXJNBZoRXMsUujluiA9ZxyIoJGzvbAM9S5emoCc"
    }   

    auth = tweepy.OAuthHandler( auth_keys['consumer_key'], auth_keys['consumer_secret'])
    auth.set_access_token( auth_keys['access_token'], auth_keys['access_token_secret'])
    api = tweepy.API(auth)
    return api

def post_twitter(graph):
    api = get_authenticated_api()
    api.update_with_media(graph, status = f"Worldwide #Coronavirus cases over time")

if __name__ == "__main__":
    main()