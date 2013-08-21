import os
import sys
import logging

from yapsy.IPlugin import IPlugin

_config = {
	'pluginmodname': 'Dummy',
	'pluginname': 'Dummy Plugin',
	'version': '0.1a',
	'created_date': '20130805',
	'author':'James E. Hung',
	'email':'jim@notional-labs.com'
}

class Dummy(IPlugin):
    def getRequirements(self):
        reqs = ["SYSTEM","SOFTWARE"]
        return reqs

    def process(self,hivesdict,outputfldr,startTimeStr):
    	statuscode = 0
    	outfile = self._setOutput(outputfldr,startTimeStr)
    	

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
	except:
		logging.error("%s: Failed to create report file - check output folder. Plugin aborting..." % _config['pluginname'])
		return 1
	return outfile