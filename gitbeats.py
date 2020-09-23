import os, sys, getopt, random
import requests
from html.parser import HTMLParser
from midiutil import MIDIFile

track    = 0
time     = 0    # In beats
duration = 1    # In beats
tempo    = 320   # In BPM, higher is more intense :p
volume   = 100  # 0-127, as per the MIDI standard

def main(argv):
   usernames = ''
   proxy = ''
   filename = 'gitbeats.mid'
   try:
      opts, args = getopt.getopt(argv,'hu:p:t:o',['username=', 'proxy=', 'tempo=', 'output-filename='])
   except getopt.GetoptError:
      print('gitbeats.py -u <username> -p <http-proxy> -t <tempo> -o <output-filename>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print('gitbeats.py -u <username> -p <http-proxy> -t <tempo>')
         sys.exit()
      elif opt in ('-u', '--username'):
         usernames = arg
      elif opt in ('-p', '--proxy'):
         proxy = arg
      elif opt in ('-t', '--tempo'):
         tempo = int(arg)
      elif opt in ('-o', '--output-filename'):
         tempo = int(arg)

   print('username: {}'.format(usernames))
   print('proxy: {}'.format(proxy))
   print('tempo: {}'.format(tempo))
   print('filename: {}'.format(filename))

   proxies = {}

   if proxy != '':
      proxies = {
         'http': proxy,
         'https': proxy
      }

   midi = MIDIFile(1)
   midi.addTempo(track, time, tempo)

   for channel, username in enumerate(usernames.split(',')):
      url = requests.urllib3.util.url.Url('https', None, 'github.com', None, username, None)   
      print('requesting data from {}'.format(url))
      request = requests.get(url, proxies=proxies)

      print('parsing data from {}'.format(url))
      parser = GitHubSvgActivityParser()
      parser.feed(request.text)

      print('processing data from {}'.format(url))
      for i, count in enumerate(parser.dataArray):
         pitch = (count + (channel * 12))
         if pitch > 255:
            pitch = 255

         midi.addNote(track, channel, pitch, time + i, duration, volume)
   
   path = os.path.dirname(__file__)
   outputfile = os.path.join(path, filename)

   print('exporting track to {}'.format(outputfile))

   with open(outputfile, 'wb') as data:
      midi.writeFile(data)
      
   print('exported track to {}'.format(outputfile))
   print('done')
  
   
class GitHubSvgActivityParser(HTMLParser):
   def __init__(self):
        HTMLParser.__init__(self)
        self.inSvg = False
        self.dataArray = []

   def handle_starttag(self, tag, attrs):
      if tag == 'svg':
         for name, value in attrs:
            if name == 'class' and value == 'js-calendar-graph-svg':
               self.inSvg = True
      elif tag == 'rect' and self.inSvg == True:
         for name, value in attrs:
            if name == 'data-count':
               self.dataArray.append(int(value))

   def handle_endtag(self, tag):
      if tag == 'svg':
         self.inSvg = False

if __name__ == '__main__':
   main(sys.argv[1:])
