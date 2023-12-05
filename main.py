#!/usr/bin/python3.9

import asyncio
import logging
import os
from datetime import datetime

from telethon import TelegramClient,functions
from telethon.sessions import StringSession

_state={}
_env={}

def init_env():

	env_api_id_raw=os.getenv("API_ID")
	env_api_hash=os.getenv("API_HASH")
	env_session=os.getenv("SESSION")
	env_chat_id_raw=os.getenv("CHAT_ID")
	env_targets_raw=os.getenv("TARGETS")
	env_freqmin_raw=os.getenv("FREQMIN")

	if (not env_api_id_raw):
		print("Missing: API_ID")
		return {}
	if not (env_api_hash):
		print("Missing: API_HASH")
		return {}
	if not env_session:
		print("Missing: SESSION")
		return {}
	if not env_targets_raw:
		print("Missing: TARGETS")
		return {}
	if not env_freqmin_raw:
		print("MISSING: FREQMIN")
		return {}

	env_api_id=int(env_api_id_raw)

	env_targets=env_targets_raw.split()
	if len(env_targets)==0:
		print("NO TARGET(S)???")
		return {}

	try:
		env_chat_id=int(env_chat_id_raw)
	except:
		env_chat_id="me"

	env_freqmin=int(env_freqmin_raw)

	return {
		"api_id":env_api_id,
		"api_hash":env_api_hash,
		"session":env_session,
		"chat_id":env_chat_id,
		"targets":env_targets,
		"freqmin":env_freqmin,
	}

async def check_status_spec(uname):

	logging.error(f"{uname} is being checked")

	result=2

	try:
		sent_msg=await _state["client"].send_message(uname,"/start")
		await asyncio.sleep(10)
		history = await _state["client"](
			functions.messages.GetHistoryRequest(
				peer=uname,
				offset_id=0,
				offset_date=None,
				add_offset=0,
				limit=1,
				max_id=0,
				min_id=0,
				hash=0,
			)
		)

		uid_sent=sent_msg.from_id.user_id
		uid_recieved=-1
		if history.messages[0].from_id is not None:
			uid_recieved=history.messages[0].from_id.user_id

		result=0
		print(uname,uid_sent,uid_recieved)
		if not uid_sent==uid_recieved:
			result=result+1

		await _state["client"].send_read_acknowledge(uname)

	except:
		logging.exception(f"{uname} FUCKED UP")

	logging.error(f"{uname} status = {result}")

	return result

async def check_status():

	msg_new=""

	for uname in _env["targets"]:
		await asyncio.sleep(1)
		status=await check_status_spec(uname)

		msg_new=f"{msg_new}\n"+{
			0:"DEAD",
			1:"ALIVE",
			2:"???",
		}[status]+f" {uname}"

	total=_state["total"]
	total=total+1
	_state["total"]=total

	msg_block=_state["msg_block"]
	msg=f"{msg_block}\n{msg_new}\n\nLast checked: {datetime.now().utcnow()} (UTC +0)\nTotal checks: {total}"

	try:
		await _state["ogmev"].edit(msg.strip())
	except:
		logging.exception(f"FAILED TO UPDATE\n\n{msg}")

async def mainloop_init():

	msg_block=f"**Monitoring bots**\n\nStarted: {str(datetime.now().utcnow())} (UTC +0)\nInterval: "+str(_env["freqmin"])+" minute(s)"

	ogmev=await _state["client"].send_message(
		_env["chat_id"],
		msg_block
	)

	_state.update({
		"ogmev":ogmev,
		"msg_block":msg_block,
		"total":0,
	})

async def mainloop():

	await mainloop_init()

	await asyncio.sleep(1)

	freqreal=_env["freqmin"]*60

	while True:

		await check_status()

		await asyncio.sleep(freqreal)

if __name__=="__main__":

	_env.update(init_env())
	if not _env:
		print("FIX YOUR ENV VARS")
		exit()

	logging.basicConfig(
		filename="bot.log",
		format='[%(levelname) 5s/%(asctime)s] %(name)s %(funcName)s: %(msg)s',
		level=logging.ERROR
	)

	_state.update(
		{
			"client":TelegramClient(
				session=StringSession(_env["session"]),
				api_id=_env["api_id"],
				api_hash=_env["api_hash"]
			).start()
		}
	)

	_state["client"].loop.run_until_complete(mainloop())
