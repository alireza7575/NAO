#!/usr/bin/env python2
# -*- coding: utf-8 -*-


import naoqi as nq
import pymongo as db
from pymongo import MongoClient

import smtplib,time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

client = MongoClient('localhost', 27017)
db = client.immigration
global passengers_data
passengers_data = db.passengers


numofip = "192.168.0.110"
portnum = 9559

nao_prx = nq.ALProxy("ALMemory", numofip, portnum)
last_access = "-1"
nao_prx.insertData('req_num',"-1")

def sendEmail( content,contact):
	EMAIL_ADDRESS = str("")
	EMAIL_PASSWORD = str("")

	msg =  MIMEMultipart()
	msg['Subject'] = 'Visa Status!'
	msg['From'] = EMAIL_ADDRESS
	msg['To'] = contact
	html ="""\
	<!DOCTYPE html>
	<html>
		<body>
			<h1 style="color:SlateGray;">Your Visa is {0}!</h1>
		</body>
	</html>
	""".format(content)

	# Record the MIME types of both parts - text/plain and text/html.
	part1 = MIMEText(content, 'plain')
	part2 = MIMEText(html, 'html')

# Attach parts into message container.
# According to RFC 2046, the last part of a multipart message, in this case
# the HTML message, is best and preferred.
	msg.attach(part1)
	msg.attach(part2)


	try:
		# Connect to the server
		server = smtplib.SMTP("smtp.gmail.com",587)
		server.ehlo()
		server.starttls()

		# Sign In
		server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
	# Send one mail
		server.sendmail(EMAIL_ADDRESS, contact, msg.as_string())

		# Sign Out
		server.quit()
	except Exception as e:
		# Convert error in a string for som checks
		e = str(e)

		# Show me if...
		if "The recipient address" in e and "is not a valid" in e:
			print("\n>>> {send_error_mail} [//> \n")
		elif "'ascii'" in e and "code can't encode characters" in e:
			print("\n>>> {send_error_char} [//> \n")
		elif "Please" in e and "log in via your web browser" in e:
			print("\n>>> {login_browser}\n>>>  - {login_browser_info}")


def readFromDataBase(require):
	print(require)
	return passengers_data.find_one({"key":str(require)})


def insertToMemory(found_data):

	del found_data['_id']
	nao_prx.insertData("firstname",str(found_data["name"]))
	nao_prx.insertData("familyname", str(found_data["fname"]))
	nao_prx.insertData("sex", str(found_data["sex"]))
	nao_prx.insertData("birthplace", str(found_data["birthplace"]))
	nao_prx.insertData("email",str( found_data["email"]))
	nao_prx.insertData("load",'1')
	print("finish loading")

def readFromMemory(name):
	try:
		#print("read:")
		return nao_prx.getData(name)

	except:
		#print("insert:defult")
		nao_prx.insertData(name,"0")


def main():
	pass

#sendEmail('accepted','ahmadyalireza75@gmail.com')
while (True):
	require = str(int(readFromMemory("req_num")))
	print(require)
	if last_access!=require:
		found_data = readFromDataBase(require)
		print(found_data)
		insertToMemory(found_data)
		last_access = require

	result = readFromMemory("result")
	print("result = {0}".format(result))
	if result == 1:
		found_data = readFromDataBase(require)
		sendEmail('accepted',found_data['email'])
		nao_prx.insertData("result",-1)

	elif result == 0:
		found_data = readFromDataBase(require)
		sendEmail('not accepted',found_data['email'])
		nao_prx.insertData("result",-1)

	time.sleep(0.5)
	print('loop')
