import subprocess  # For executing a shell command
import time
import os
import requests
from datetime import datetime
from pytz import timezone

from pymongo import MongoClient
client = MongoClient("localhost", 27017)
db = client["Router"]
users = db["Users"]

bot_token = os.environ.get("BOT_TOKEN")

#Telegram url
url = f"https://api.telegram.org/bot{bot_token}/sendMessage?"


def ping(host):
	command = ['ping', '-c', '5', host]
	res = subprocess.call(command, stdout="/dev/null")
	if res == 0:
		return True
	else:
		return False

def main():
	while True:
		clients = users.find({"user_id": {"$exists": True}}, {'_id': 0})
		for client in clients:
			if client["flag"] == 'pause':
				continue
			else:
				res = ping(client["ip"])
				#ping succeeded
				if res == True:
					#if user had electricity and now has
					if client["flag"] == "on":
						continue
					#if user had no electricity but now has
					else:
						if "datetime" in client:
							#calculating for how long user didn't have the el
							now = int(datetime.now().timestamp())
							print(f"now it's {now}")
							print(f"{client['name']}: {client['datetime']}")
							dif = abs(now - client["datetime"])
							hours = int(dif // 3600)
							minutes = int((dif % 3600) // 60)
							if hours > 0:
								message = f"Guess who's back🌝\nElectricity was gone for {hours} hours and {minutes} minutes"
							else:
								message = f"Guess who's back🌝\nElectricity was gone for {minutes} minutes"
							try:
								result = requests.get(url+f"chat_id={client['user_id']}&text={message}", timeout=5)
							except requests.exceptions.ConnectionError:
								continue
						users.update_one({"ip": client["ip"]}, {"$set": {"flag": "on"}, "$unset": {"datetime": ""}})
						print(f"dif: {dif}, hours: {hours}, minutes: {minutes}")
				#ping not succeeded
				else:
					#if user had not electricity and now has not
					if client["flag"] == "off":
						continue
					#if user had not electricity and now has
					else:
						today = int(datetime.now().timestamp())
						users.update_one({"ip": client["ip"]}, {"$set": {"flag": "off", "datetime": today}})
						print(f"{client['name']} is off at {today}")
						try:
							result = requests.get(url+f"chat_id={client['user_id']}&text=Darkness has come 🌚", timeout=5)
						except requests.exceptions.ConnectionError:
							continue
if __name__=='__main__':
	main()
