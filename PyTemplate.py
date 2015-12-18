###############################################################
## Program: PyTemplate.py
## Description: Generate folder/files base on templates
## Author: jamedina@gmail.com
## Git : https://github.com/cecile/PyTemplate
##-------------------------------------------------------------
## Required Modules: pybars3
###############################################################

#--------------------------------------------------------------
# INFO
#--------------------------------------------------------------
# The script will copy the folder structure and files into
#  the output directory.
#
# Configuration is a JSON file, by default PyTemplate.json
#
# You could change JSON as input parameter:
#
#  $ python PyTemplate.py file.json
#
# All paths are relative to the JSON file location
#
# Folders and files could have __var__ in the names
#
# The files could use template variables as {{var}}
#  templates could use Handlebars.js like syntax
#  more details in: https://github.com/wbond/pybars3
#
# There is a couple of helpers:
#  {{lower var}} for lowercase variable content
#  {{upper var}} for uppercase variable content
#
# This could be use in the file names and paths:
#  __lower var__
#  __upper var__
#--------------------------------------------------------------

#pybar helpers
def _lower(this, name):
    return name.lower()

def _upper(this, name):
    return name.upper()

helpers = {
  "lower": _lower,
  "upper": _upper
}

#--------------------------------------------------------------
# ACTUAL CODE BELLOW, DO NOT EDIT
#--------------------------------------------------------------

#system imports
import logging
import os
import sys
from os import walk
import codecs
import re
import getopt
import json
from datetime import datetime

#pybars
from pybars import Compiler

#store time
startTime = datetime.now()

# Global compiler
compiler = Compiler()

def translate(text, variables):
  template = compiler.compile(text)
  return template(variables, helpers=helpers)

# Log object
log = None

# Get Directory/File from a path
def GetDirectory(path):
  log.info("reading template folder [%s]", path)
  directories = []
  files = []

  for (dirpath, dirnames, filenames) in walk(path):
      directories.append(dirpath)
      for filename in filenames:
        files.append(dirpath + os.sep + filename)

  return directories,files

#compiled Reg Exp
regex = re.compile(ur'(__+.*?__)')

# Translate path, could include variables
def TranslatePath(template_path, output_path, path, variables):

  traslate_path = ""

  strip_path = path.replace(template_path, "")

  if not (strip_path==""):
      traslate_path = output_path + strip_path

      for var in re.findall(regex, traslate_path):
        traslate_path = traslate_path.replace(var, "{{" + var[2:-2] + "}}")

      traslate_path = translate(unicode(traslate_path), variables)

  return traslate_path

# Create directories from the template
def CreateDirectories(template_path, output_path, variables, directories):
  log.info("Creating directories")
  for directory in directories:

    traslate_path = TranslatePath(template_path, output_path, directory, variables)

    if not (traslate_path==""):

      if not os.path.exists(traslate_path):
        log.info("creating path [%s]", traslate_path)
        os.makedirs(traslate_path)
      else:
        log.warning("path exist [%s]", traslate_path)

# Create the files and translate file folders
def CreateFiles(template_path, output_path, variables, files):
  log.info("Creating files")
  for filename in files:
    translate_file = TranslatePath(template_path, output_path, filename, variables)

    exist = os.path.isfile(translate_file)

    content = []

    with codecs.open(filename, encoding='utf-8') as input_file:
      for line in input_file.readlines():
        traslate_line = translate(line, variables)
        content.append(traslate_line)

    output_file = codecs.open(translate_file, encoding='utf-8', mode='w')
    output_file.writelines(content)
    if exist:
      log.warning("file overwrited [%s]", translate_file)
    else:
      log.info("file created [%s]", translate_file)

def LoadCfg(path):

  try:
    with codecs.open(path, encoding='utf-8') as input_file:
      lines = input_file.read()
  except Exception as ex:
    raise Exception(str.format("Exception loading cfg [{0}] = {1}", path, ex))

  try:
    cfg = json.loads(lines)
  except Exception as ex:
    raise Exception(str.format("JSON error in cfg [{0}] = {1}", path, ex))

  if not cfg.has_key("output_path"):
    raise Exception("No output_path in cfg")

  if not cfg.has_key("templates_path"):
    raise Exception("No templates_path in cfg")

  if not cfg.has_key("template_name"):
    raise Exception("No template_name in cfg")

  if not cfg.has_key("variables"):
    raise Exception("No variables in cfg")

  return cfg

if __name__ == '__main__':

  LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

  log = logging.getLogger(__name__)

  try:

    cfg_path = "PyTemplate.json"

    if len(sys.argv)>1:
      cfg_path = sys.argv[1]

    if not os.path.isfile(cfg_path):
      raise Exception(str.format("Cfg does not exist [{0}]", cfg_path))

    cfg = LoadCfg(cfg_path)

    base_path = os.path.dirname(os.path.realpath(cfg_path))
    output_path = os.path.abspath(os.path.join(base_path, cfg["output_path"]))
    templates_path = os.path.abspath(os.path.join(base_path, cfg["templates_path"]))

    log.info("base_path = [%s]",base_path)
    log.info("output_path = [%s]",output_path)
    log.info("templates_path = [%s]",templates_path)

    if not os.path.exists(templates_path):
      raise Exception("Templates path does not exist")

    template_path = templates_path+os.sep + cfg["template_name"]

    if not os.path.exists(template_path):
      raise Exception("Template path does not exist")

    directories, files = GetDirectory(template_path)
    CreateDirectories(template_path,output_path, cfg["variables"], directories)
    CreateFiles(template_path,output_path, cfg["variables"], files)

    log.info("All done in %s", str(datetime.now() - startTime))

  except Exception as ex:
    logging.error(ex, exc_info = True)
    raise ex