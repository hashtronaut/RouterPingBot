#!/bin/env python3
import os, sys, signal, asyncio
from datetime import datetime
from utils import string_generator, get_config, check_ip
from pytz import timezone
import logging

logger = logging.getLogger('RouterPingBot')

admin_id = os.environ.get("ADMIN_ID")
bot_token = os.environ.get("BOT_TOKEN")
api_id = os.environ.get("API_ID")
api_hash = os.environ.get("API_HASH")


# Telegram imports
from telethon import TelegramClient, events

bot = TelegramClient('bot', int(api_id), api_hash).start(bot_token=bot_token)

#db imports
from pymongo import MongoClient
client = MongoClient("localhost", 27017)
db = client["Router"]
users = db["Users"]




@bot.on(events.NewMessage(pattern=r'/start\b'))
async def start_handle(event):
	if event.is_private and event.chat_id != admin_id:
		text = event.text.split(' ')
		if len(text) > 1:
			link = text[1]
			found = users.find_one({"link": link})
			if found:
				users.update_one({"link": link}, {"$unset": {"link": ""}, "$set": {"user_id": event.chat_id, "flag": ""}})
				await bot.send_message(event.chat_id, "Sniff-sniff.. Smells like teen spirit")



@bot.on(events.NewMessage(pattern=r'/add\b'))
async def start_handle(event):
	if event.is_private and event.chat_id == admin_id:
		print("entered")
		info = event.text.split(' ')
		name = info[1]
		ip = info[2]
		res = check_ip(ip)
		if res is False:
			await bot.send_message(event.chat_id, "IP is invalid")
		string = string_generator()
		users.insert_one({'link': string, "name": name, "ip": ip})
		link = f'https://t.me/electronyukh_bot?start={string}' 
		await bot.send_message(event.chat_id, link)


@bot.on(events.NewMessage(pattern='/list'))
async def handle_forwarded_message(event):
	if event.is_private and event.chat_id == admin_id:
		clients = users.find({"user_id": {"$exists": True}}, {'_id': 0})
		msg = "Ім'я      ID   IP    Status\n\n"
		counter = 0
		for i in clients:
			msg += f'{i["name"]}  <code>{int(i["user_id"])}</code>   {i["ip"]}    {i["flag"]}\n'
			counter += 1
		if counter > 0:
			await event.reply(msg, parse_mode='HTML')
		else:
			await event.reply("DB is empty", parse_mode='HTML')

@bot.on(events.NewMessage(pattern='/pause'))
async def handle_forwarded_message(event):
	if event.is_private and event.chat_id == admin_id:
		msg = event.text.split(' ')
		if len(msg) > 1:
			user_id = msg[1]
		try:
			user_id = int(user_id)
			res = users.update_one({"user_id": user_id}, {"$set":{"flag": "pause"}})
			if res.modified_count == 1:
				await event.reply("User was set on pause")
			else:
				await event.reply("User does not exist")
		except ValueError:
			await event.reply("ID must be an integer")



@bot.on(events.NewMessage(pattern='/unpause'))
async def handle_forwarded_message(event):
	if event.is_private and event.chat_id == admin_id:
		msg = event.text.split(' ')
		if len(msg) > 1:
			user_id = msg[1]
		try:
			user_id = int(user_id)
			res = users.update_one({"user_id": user_id}, {"$set":{"flag": ""}})
			if res.modified_count == 1:
				await event.reply("User was unpaused")
			else:
				await event.reply("User does not exist")
		except ValueError:
			await event.reply("ID must be an integer")


@bot.on(events.NewMessage(pattern='/del'))
async def handle_forwarded_message(event):
	if event.is_private and event.chat_id == admin_id:
		msg = event.text.split(' ')
		if len(msg) > 1:
			user_id = msg[1]
		try:
			user_id = int(user_id)
			res = users.delete_one({"user_id": user_id})
			if res.deleted_count == 1:
				await event.reply("You successfuly deleted user")
			else:
				await event.reply("User has been deleted or doesn't exist")
		except ValueError:
			await event.reply("ID must be an integer")



async def main():
	while True:
		try:
			await bot.run_until_disconnected()
		except Exception as e:
			print(str(e))
			await asyncio.sleep(5)  # Add a delay before attempting to reconnect
			await bot.connect()

if __name__ == '__main__':
	loop = asyncio.get_event_loop()
	loop.run_until_complete(main())