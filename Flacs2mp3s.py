#!/bin/python3

import subprocess
import os
import re

# I like colors
# For zamn: http://misc.flogisoft.com/bash/tip_colors_and_formatting
def pgood(text):
  print('\033[92m' + text + '\033[0m')

def pfail(text):
  print('\033[91m\033[1m' + text + '\033[0m')
  
def pwarn(text):
  print('\033[93m' + text + '\033[0m')

# Check we have the tools
for cmd in ['lame', 'metaflac']:
  rv = subprocess.call('type '+cmd, shell=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
  if rv is not 0:
    pfail("Could not find {0} executable.".format(cmd))
    exit(1)

def getFlacTags(f):
  tags = {}
  for tagname in ["ARTIST", "TITLE", "ALBUM", "TRACKNUMBER", "DATE", "GENRE", "DISCNUMBER"]:
    try:
      output = subprocess.check_output(["metaflac", "--show-tag="+tagname, f], stderr=subprocess.STDOUT)
      output = output.decode("utf-8")
      output = output.rstrip('\n')
      try:
        output = output.split("=")[1]
        tags[tagname] = output
      except: pass
    except subprocess.CalledProcessError as e:
      pfail("metaflac output:")
      print(e.output.decode("utf-8"))
      pfail("Error retrieving tag {0} from flac \"{1}\"".format(tagname, f))
      print(e)
      exit(1)
  return tags


flacExt = re.compile('.*\\.flac$')
flacfiles = []
for f in os.listdir('.'):
  if os.path.isfile(os.path.join('.',f)) and flacExt.match(f):
    flacfiles.append(f)

if not flacfiles:
  pfail("No flac files found, exiting.")
  os.exit(1)

flacfiles.sort()
numFiles=len(flacfiles)

pgood("Found {0} FLAC files.".format(numFiles))
pgood("Creating directorys 320, V2, V0...")

for d in ['320','V2','V0']:
  if not os.path.exists(d):
    try:
      os.mkdir(d)
    except OSError as e:
      pfail("Cannot make directory \"{0}\": {1}".format(d, e.strerror))
  else:
    pwarn("Directory {0} already exists".format(d))

c = 0
for f in flacfiles:
  c+=1
  outf = re.sub('.flac$', '.mp3', f)
  tags = getFlacTags(f)
  pgood("Detected the following usable FLAC tags:")
  pgood(str(tags))
  lame_common = ['lame', '--add-id3v2', '--pad-id3v2', '--ignore-tag-errors']
  for tag, value in tags.items():
    if tag is 'ARTIST':
      lame_common += ['--ta', value]
    if tag is 'TITLE':
      lame_common += ['--tt', value]
    if tag is 'TRACKNUMBER':
      lame_common += ['--tn', value]
    if tag is 'ALBUM':
      lame_common += ['--tl', value]
    if tag is 'DATE':
      lame_common += ['--ty', value]
    if tag is 'GENRE':
      lame_common += ['--tg', value]
  
  lame320 = lame_common+['-b', '320', '-h', f, '320/'+outf]
  lameV2  = lame_common+['-V', '2', '--vbr-new', f, 'V2/'+outf]
  lameV0  = lame_common+['-V', '0', '--vbr-new', f, 'V0/'+outf]
  
  pgood("* [{0}/{1}] Starting 320kbps encoder".format(c, numFiles))
  print("Command:  "+str(lame320))
  subprocess.call(lame320)
  
  pgood("* [{0}/{1}] Starting V2 encoder".format(c, numFiles))
  print("Command:  "+str(lameV2))
  subprocess.call(lameV2)
  
  pgood("* [{0}/{1}] Starting V0 encoder".format(c, numFiles))
  print("Command:  "+str(lameV0))
  subprocess.call(lameV0)





