#Phone script
#version: 5.0
#author: Anton Bubnov
#email: uaantony@gmail.com
#This programm works with gammu: send and recieve USSD requests, read them and analyze

# -*- coding: utf-8 -*- 
import ConfigParser
import logging
import subprocess
import ast
from time import localtime, strftime
import os
import re
import time

#Creating and opening log file
logging.basicConfig(filename='phoneScript.log',level=logging.DEBUG)

#Function for logging
#Not tested yet
def writeInLog(message):
	logging.info(strftime("%d-%m %H:%M:%S", localtime())+" "+message)
	pass

#This function creates a config file with default parameters (for MTS operator)
#Directory of created file is ~/home/username/phoneScript.cfg
def createConfig():
	config = ConfigParser.RawConfigParser()
	config.add_section('Main config')
	config.set('Main config', 'operator', 'MTS') #add default operator parameter
	config.set('Main config', 'checkbalance_mts', """gammu getussd '*101#'""") #add default USSD request parameter (check balance)
	config.set('Main config', 'checksms_mts', """gammu getussd '*101*03#'""") #add default USSD request parameter (check current number of sms)
	config.set('Main config', 'buysms_mts', """gammu getussd '*101*200#'""") #add default USSD request parameter (request to buy 200 sms)
	config.set('Main config', 'balancerange', '20') #add default critical balance range (gryvnas) parameters (if balance is lower than this parameter - program send email)
	config.set('Main config', 'smsrange', '70') #add default minimal number of sms, when they are bought
	config.set('Main config', 'smsprice_mts', '20') #add default price of sms packet (200sms)
	config.set('Main config', 'checkperiod', '10') #parameter - how often check sms number (times per hour)

	# Writing our configuration file to 'phoneScript.cfg'
	with open('phoneScript.cfg', 'wb') as configfile:
	    config.write(configfile)
	    writeInLog('Config file was created and filled with default parameters')

#Try to open config file. If it is'nt exist - call to createConfig() function
try:
   with open('phoneScript.cfg'): pass
except IOError:
	writeInLog('Config file was not found')
	createConfig()
   	pass
config = ConfigParser.RawConfigParser()
config.read('phoneScript.cfg')
pausetime = 3600/int(config.get('Main config', 'checkperiod')) 




#This function check balance
def checkBalance():
	writeInLog('Starting checkBalance')
	#Check operator to know number of USSD request
	if config.get('Main config', 'operator') == 'MTS':
		checkBalance = 'checkbalance_mts'
		pass
	cmd = config.get('Main config', checkBalance) #command for USSD request considering operator
	PIPE = subprocess.PIPE
	p = subprocess.Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=subprocess.STDOUT, close_fds=True)
	request = False
	#Check if request answer is OK
	while True:
		if p.stdout.readline() != "":
			line = p.stdout.readline()
			if 'USSD received' == line[0:13]:
				request = True #Set true if requets was successful
				writeInLog('Request answer was successfully readed')
		else:
			if request == False:
				writeInLog('Request answer is unreadable')
			break
	if request == True:
		#loop to put request answer (further: RA) in array
		arr = []
		for i in line:
			arr.append(i)
		pass
		balance = '' #Variable to add value of balance
		#Loop for MTS operator
		if config.get('Main config', 'operator') == 'MTS':
			char = iter(arr)
			item = char.next()
			#A loop to find the beginning of RA
			while item != '"':
				item = char.next()
				pass
			#A loop to find the end of gryvnas
			while item != '.':
				item = char.next()
				balance += item
				pass
			#A loop to find the end of kopecks
			while item != ' ':
				item = char.next()
				balance += item
				pass
		logging.info(strftime("%d-%m %H:%M:%S", localtime())+' Current balance: '+balance+'Operator: '+config.get('Main config', 'operator'))
		balance = ast.literal_eval(balance) #String to number
		pass
	#Check if request was successful
	output, errors = p.communicate()
	if p.returncode or errors:
		logging.error(strftime("%d-%m %H:%M:%S", localtime())+' Request was unsuccessful. Error code: '+str(p.returncode))
	else:
		writeInLog('Request was OK')
		pass
	return balance
	pass

#function to check symbol is a number
def special_match(strg, search=re.compile(r'[0-9]').search):
	return bool(search(strg))

#function to check number of sms
def checkSms():
	writeInLog('Starting checkSms')
	#Check operator to know number of USSD request
	if config.get('Main config', 'operator') == 'MTS':
		checkSms = 'checksms_mts'
		pass
	cmd = config.get('Main config', checkSms) #command for USSD request considering operator
	PIPE = subprocess.PIPE
	p = subprocess.Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=subprocess.STDOUT, close_fds=True)
	request = False
	#Check if request answer is OK
	while True:
		if p.stdout.readline() != "":
			line = p.stdout.readline()
			if 'USSD received' == line[0:13]:
				request = True #Set true if requets was successful
				writeInLog('Request answer was successfully readed')
		else:
			if request == False:
				writeInLog('Request answer is unreadable')
			break
	if request == True:
		#loop to put request answer (further: RA) in array
		arr = []
		for i in line:
			arr.append(i)
		pass
		smsnumber = '' #Variable to add value of smsnumber
		#Loop for MTS operator
		if config.get('Main config', 'operator') == 'MTS':
			char = iter(arr)
			item = char.next()
			#A loop to find the beginning of RA
			while item != '"':
				item = char.next()
				pass
			#A loop to find the number of sms
			while special_match(item) == False:
				item = char.next()
				pass
			smsnumber += item #put first symbol of number
			#put all other symbols of number
			while special_match(item) == True:
				item = char.next()
				smsnumber += item
				pass
		logging.info(strftime("%d-%m %H:%M:%S", localtime())+' Current sms number: '+smsnumber+'Operator: '+config.get('Main config', 'operator'))
		smsnumber = ast.literal_eval(smsnumber)
		pass
	#Check if request was successful
	output, errors = p.communicate()
	if p.returncode or errors:
		logging.error(strftime("%d-%m %H:%M:%S", localtime())+' Request was unsuccessful. Error code: '+str(p.returncode))
	else:
		writeInLog('Request was OK')
		pass
	return smsnumber
	pass

#This function buying sms
#Attantion! This function was not tested yet!
def buysms():
	writeInLog('Starting checkSms')
	#Check operator to know number of USSD request
	#Checking config file (take 'operator' parametes)
	if config.get('Main config', 'operator') == 'MTS':
		checkSms = 'buysms_mts'
		pass
	cmd = config.get('Main config', buySms) #command for USSD request considering operator
	PIPE = subprocess.PIPE
	p = subprocess.Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=subprocess.STDOUT, close_fds=True)
	#Check if request answer is OK
	while True:
		message = ''
		if p.stdout.readline() != "":
			message += line #collect all RA lines in one variable
			line = p.stdout.readline()
			if 'USSD received' == line[0:13]:
				request = True #Set true if requets was successful
				writeInLog('Request answer was successfully readed')
		else:
			if request == False:
				writeInLog('Request answer is unreadable')
			break
	if request == True:
		#check confirmation of operator
		if 'spysano' in message:
			writeInLog('Sms packet was ordered')
		pass
	pass

#This function check at first the number of sms. If this num is critical (config parameter) it check current balance.
#If current balance is bigger than price of sms packet - call to buysms function and buys sms. If balance is lower it will report by email (not realized yet)
def controlsmsnumber():
	try:
		smsnumber = checkSms()
		if int(smsnumber) < int(config.get('Main config', 'smsrange')):
			logging.info(strftime("%d-%m %H:%M:%S", localtime())+' Sms number is lower than: '+config.get('Main config', 'smsrange'))
			try:
				balance = checkBalance()
				if int(balance) < int(ast.literal_eval(config.get('Main config', 'smsprice_mts'))):
	 				logging.info(strftime("%d-%m %H:%M:%S", localtime())+' The balace is lower than: '+config.get('Main config', 'smsprice_mts'))
	 				#Here should be email sending function call
					pass
				else:
					try:
						buysms()
						pass
					except Exception, e:
						writeInLog('Running function buySms was failed')
						pass
				pass
			except Exception, e:
				writeInLog('Running function checkBalance was failed')
				pass
			pass
	except Exception, e:
		writeInLog('Running function checkSms was failed')
		pass
	pass
controlsmsnumber()
