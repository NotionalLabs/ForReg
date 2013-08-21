import os
import sys
import logging
from datetime import datetime

from Registry import Registry
from yapsy.IPlugin import IPlugin

_config = {
	'pluginmodname': 'OS_Info',
	'pluginname': 'Operating System Info Reporter',
	'version': '0.1a',
	'created_date': '20130805',
	'author':'James E. Hung',
	'email':'jim@notional-labs.com'
}

class OSInfo(IPlugin):
    def getRequirements(self):
        reqs = ["SOFTWARE","SYSTEM"]
        return reqs

    def process(self,hivesdict,outputfldr,startTimeStr):
    	statuscode = 0
    	outfile = self._setOutput(outputfldr,startTimeStr)
    	currcontrolsetkey = "ControlSet00%s" % self._getControlSet(hivesdict)
    	
    	# Parse OS product information.
    	outfile.write('[Installed OS Info]\n')
    	try:
    		key = hivesdict['SOFTWARE'][1].open('Microsoft\\Windows NT\\CurrentVersion')
    	except Registry.RegistryKeyNotFoundException:
    		logging.error("Key not found - check Windows version?")
    		return 1
    	for value in key.values():
    		if value.name() == "ProductName":
    			outfile.write("Product Name: %s\n" % value.value())
    		elif value.name() == "CSDVersion":
    			outfile.write("Service Pack: %s\n" % value.value())
    		elif value.name() == "ProductId":
    			outfile.write("Product ID: %s\n" % value.value())
    		elif value.name() == "CurrentVersion":
    			outfile.write("Current Version: %s\n" % value.value())
    		elif value.name() == "CurrentBuild":
    			outfile.write("Current Build: %s\n" % value.value())
    		elif value.name() == "EditionID":
    			outfile.write("Edition: %s\n" % value.value())
    		elif value.name() == "PathName":
    			outfile.write("Install Path: %s\n" % value.value())
    		elif value.name() == "RegisteredOrganization":
    			outfile.write("Registered Organization: %s\n" % value.value())
    		elif value.name() == "RegisteredOwner":
    			outfile.write("Registered Owner: %s\n" % value.value())
    		elif value.name() == "InstallDate":
    			installdate = datetime.utcfromtimestamp(int(value.value())).strftime('%Y-%m-%d %H:%M:%S')
    			outfile.write("Install Date: %s (UTC)\n" % installdate)
    	try:
    		key = hivesdict['SYSTEM'][1].open('%s\\Control\\Session Manager\\Environment' % currcontrolsetkey)
    		for value in key.values():
    			if value.name() == "PROCESSOR_ARCHITECTURE":
    				outfile.write("Processor Architecture: %s\n" % value.value())
    			elif value.name() == "PROCESSOR_IDENTIFIER":
    				outfile.write("Processor ID: %s\n" % value.value())
    	except Registry.RegistryKeyNotFoundException:
    		logging.error('Key not found: %s\\Control\\Session Manager\\Environment' % currcontrolsetkey)
    	
    	# Parse System Clock Settings/Timezone.
    	outfile.write('\n[System Clock Settings]\n')
    	try:
    		tzkey = hivesdict['SYSTEM'][1].open('%s\\Control\\TimeZoneInformation' % currcontrolsetkey)
    	except Registry.RegistryKeyNotFoundException:
    		logging.error("Key not found - check Windows version?")
    		return 1
    	for tzvalue in tzkey.values():
    		if tzvalue.name() == 'TimeZoneKeyName':
    			outfile.write("Time Zone Name: %s\n" % tzvalue.value())
    		elif tzvalue.name() == 'StandardName':
    			outfile.write("Standard Timezone Name: %s\n" % tzvalue.value())
    		elif tzvalue.name() == 'DaylightName':
    			outfile.write("Daylight Timezone Name: %s\n" % tzvalue.value())
    		elif tzvalue.name() == 'StandardName':
    			outfile.write("Standard Name: %s\n" % tzvalue.value())
    		elif tzvalue.name() == 'Bias':
    			outfile.write("Time Bias: %s minutes (%s)\n" % (tzvalue.value(),tzvalue.value()/60))
    			print long(hex(tzvalue.value()))

    	outfile.close()

    	return statuscode

    def _setOutput(self,outputfldr,startTimeStr):
    	"""
    	Basic Plugin Method - Creates the output report file for the plugin with the correct filename
    	formatting. Don't change this!
    	"""
    	outfilepath = os.path.join(outputfldr,"%s_%s.txt" % (_config['pluginmodname'],startTimeStr))
    	logging.info(" %s -> %s" % (_config['pluginname'],os.path.split(outfilepath)[1]))
    	try:
    		outfile = open(outfilepath,"w")
    		outfile.write('%s - v%s\n' % (_config['pluginname'],_config['version']))
    		outfile.write('--------------------------------------------------\n')
    	except:
    		logging.error("%s: Failed to create report file - check output folder. Plugin aborting..." % _config['pluginname'])
    		return 1
    	return outfile

    def _getControlSet(self,hivesdict):
    	"""
    	Basic Plugin Method - Convenience method for finding the current Control Set by querying the
    	Select key when examining the SYSTEM hive.
    	"""
    	controlset = ""
    	try:
    		key = hivesdict['SYSTEM'][1].open('Select')
    		for value in key.values():
    			if value.name() == "Current":
    				controlset = value.value()
    	except Registry.RegistryKeyNotFoundException:
    		logging.error("SYSTEM HIVE: Select Key not found.")
    		controlset = "0"
    	return controlset