#!/usr/bin/env python
#-------------------------------------------------------------------------------
# Name:        ForReg Prototype
# Purpose:     Initial Prototype of ForReg forensic Registry Analyser.
#
# Author:      Jim Hung @ Notional-Labs.com
#
# Created:     25/07/2013
# Licence:     Apache v2.0
#-------------------------------------------------------------------------------

import os
import sys
import argparse
import datetime
import logging

from Registry import Registry
from yapsy.PluginManager import PluginManager

version = '0.1'
build = '20130803'

def main():
    startTime = datetime.datetime.now()
    startTimeStr = str(startTime)[:19].replace(":","-").replace(" ","_")

    print ""
    outputfldr, inputfldr, pluginfldr = validateArgs()
    setupLogging(outputfldr,startTimeStr)

    print "\n[CONFIGURATION]"
    logging.info("Input Folder: " + os.path.abspath(inputfldr))
    logging.info("Output Folder: " + os.path.abspath(outputfldr))
    logging.info("Plugin Folder: " + os.path.abspath(pluginfldr))

    print "\n<ENUMERATING REGISTRY HIVES...>"
    hivesdict = loadHives(inputfldr)

    print "\n[LOADED REGISTRY HIVES]"
    for hivename, hive in hivesdict.iteritems():
        if hive[0] == 1:
            logging.info(" [Y] " + hivename + " -> Path: " + hive[2])
        elif hive[0] == 0:
            logging.info(" [N] " + hivename + " -] NOT FOUND")
        else:
            logging.info(" [!] " + hivename + " -] FAILED TO LOAD")

    print "\n<ENUMERATING PLUGINS...>"
    pluginmanager, compat_plugins = loadPlugins(pluginfldr,hivesdict)

    print "\n<EXECUTING COMPATIBLE PLUGINS...>"
    for pluginname in compat_plugins:
        plugin = pluginmanager.getPluginByName(pluginname)
        if not (plugin.plugin_object.process(hivesdict,outputfldr,startTimeStr)):
            logging.info(" - completed sucessfully.")
        else:
            logging.info(" - failed to complete.")

    print "\nForReg took " + str(datetime.datetime.now()-startTime) + " to run."

    # End program.

def loadPlugins(pluginfldr,hivesdict):
    """
    Enumerate plugins in the specified directory and return the populated
    plugin manager and a list of the compatible plugins. Compatibility is
    determined by checking if the required hives were loaded sucessfully.
    """
    pluginmanager = PluginManager()
    pluginmanager.setPluginPlaces([pluginfldr])
    pluginmanager.collectPlugins()

    print ""
    logging.info("[PLUGINS IDENTIFIED: %s]" % len(pluginmanager.getAllPlugins()))

    compat_plugins = list()
    incompat_plugins = list()
    for plugin in pluginmanager.getAllPlugins():
        compat = 1
        for req in plugin.plugin_object.getRequirements():
            if (hivesdict[req][0] <> 1):
                compat = 0
                break
        if compat:
            compat_plugins.append(plugin.name)
        else:
            incompat_plugins.append(plugin.name)

    logging.info(" [%s] Compatible Plugins:" % len(compat_plugins))
    for plugin in compat_plugins:
        logging.info("  - %s" % plugin)
    logging.info(" [%s] Incompatible Plugins:" % len(incompat_plugins))
    for plugin in incompat_plugins:
        logging.info("  - %s" % plugin)

    return pluginmanager, compat_plugins

def loadHives(inputfldr):
    """
    Create Registry objects for all available hives in the input directory.
    Returns a tuple containing the status code of the hive, the Registry object,
    and the relative path to the loaded file. Status codes: 0 = not found,
    1 = ok, 2 = failed to parse. Catches un-handled exception in Registry module
    which occurs when attempting to read a file < 4 bytes long.
    """
    hivesdict = dict()
    hivenames = ['SYSTEM','SOFTWARE','SECURITY','SAM','NTUSER.DAT']

    for hive in hivenames:
        for file in os.listdir(inputfldr):
            if (file.upper() == hive):
                try:
                    hivesdict[hive] = (1,Registry.Registry(os.path.join(inputfldr,file)),os.path.join(inputfldr,file),)
                except Registry.RegistryParse.ParseException:
                    logging.error("Cannot parse registry file: " + os.path.join(inputfldr,file) + ". File may be corrupt.")
                    hivesdict[hive] = (3,None,os.path.join(inputfldr,file),)
                except:
                    logging.error("Cannot parse registry file: " + os.path.join(inputfldr,file) + ". File may be corrupt - check the filesize is non-zero.")
                    hivesdict[hive] = (3,None,os.path.join(inputfldr,file),)
        if not hive in hivesdict:
            hivesdict[hive] = (0,None,"NULL")

    return hivesdict


def setupLogging(outputfldr,startTimeStr):
    """
    Configure basic logging and populate the log with bibliographic info.
    """
    logfilepath = "ForReg_%s.log" % startTimeStr
    logging.basicConfig(filename=os.path.join(outputfldr,logfilepath),level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%H:%M:%S')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter('%(message)s'))
    logging.getLogger('').addHandler(console)
    print """    ______           ____
   / ____/___  _____/ __ \___  ____ _
  / /_  / __ \/ ___/ /_/ / _ \/ __ `/
 / __/ / /_/ / /  / _, _/  __/ /_/ /
/_/    \____/_/  /_/ |_|\___/\__, /
 Forensic Registry Analyser /____/ Notional Labs 2013"""
    print "------------------------------------------------------"
    logging.info("Version ["+version+"] Build ["+build+"] Author [James E. Hung]")
    print "------------------------------------------------------"
    return

def validateArgs():
    """
    Validate arguments, including checking that the supplied folders exist.
    """
    parser = argparse.ArgumentParser(description="\nForReg Prototype - 2013 Jim Hung, Notional-Labs.com")
    parser.add_argument('-o','--output', help='Output folder path for results and logs', required=True)
    parser.add_argument('-i','--input', help='Input folder path to the exported registry hives (e.g. SYSTEM, SOFTWARE, etc...)', required=True)
    parser.add_argument('-p','--plugindir', help='Optional - path to plugin folder (defaults to /plugins/).', default=os.path.join(sys.path[0], "plugins"))
    args = vars(parser.parse_args())

    if not os.path.exists(args['output']):
        print "WARNING: Output folder does not exist - creating folder..."
        os.makedirs(args['output'])
    if not os.path.exists(args['input']):
        print "ERROR: Input folder does not exist - exiting..."
        sys.exit(1)
    if not os.path.exists(args['plugindir']):
        print "ERROR: Plugin folder does not exist - exiting..."
        sys.exit(1)

    return args['output'],args['input'],args['plugindir']

if __name__ == '__main__':
    main()