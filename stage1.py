#!/usr/bin/python
#
# stage1.py
#
# SXSW Music Events Crawler
# J. Adams <jna@retina.net> 
# Last update 1/31/2018
#
# Crawl the SXSW site, downloading every artist and event page into a
# cache directory for later parsing by stage2.py
#

import io
import requests
import os.path
import re
import sys
import string

BASE_URL='http://schedule.sxsw.com'
CACHE_DIR="cache"

# debug all fetches
DEBUG=False

def fetch(url,fn,daynumber,nocache = True):
  # fetch a URL, but if we have the file on disk, return the file instead.
  # This prevents us from beating on the remote site while developing.
  if not os.path.isdir("%s/%s" % (CACHE_DIR, daynumber)):
    print "makedir %s/%s" % (CACHE_DIR, daynumber)
    os.makedirs("%s/%s" % (CACHE_DIR, daynumber))

  cachefn = "%s/%s/%s" % (CACHE_DIR, daynumber, fn)
  print "fetch: %s" % cachefn

  if os.path.isfile(cachefn) and nocache == False:
    print "return cached content for url (%s)" % fn
    text = open(cachefn,'r').read()
    return text

  # lie. Alot. 
  headers = {'Accept'          : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
             'Accept-Charset'  : 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
             'Accept-Language' : 'en-US,en;q=0.8',
             'Cache-Control'   : 'max-age=0',
             'Host'            : 'schedule.sxsw.com',
             'Referer'         : 'http://schedule.sxsw.com/',
             'User-Agent'      : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.0.1364.68 Safari/537.22' } 

  print "fetch: %s --> %s " % (url, cachefn)

  r = requests.get(url, headers=headers)
  f = io.open(cachefn, 'w', encoding='utf8')
  f.write(r.text)
  f.close()
  print "  ... %d " % r.status_code
  return r.text 

def get_events(data):
  events=[]
  matches = re.findall('href=\"(/2018/events/\w+)\"', data, re.DOTALL)
  if matches:
    return matches

# https://schedule.sxsw.com/2018/artists/18953
def get_artists(data):
  events=[]
  matches = re.findall('href=\"(/2018/artists/\d+)\"', data, re.DOTALL)
  if matches:
    return matches
  
# http parameters
# https://schedule.sxsw.com/2018/artists
artistpage = fetch("%s/2018/artists" % ( BASE_URL ) ,"artists.html", 0 , nocache = False)
artists = get_artists(artistpage)
for artist in artists:
  detailurl = "%s%s" % (BASE_URL , artist)
  
  # fetch!
  print "%s fetch!" % detailurl
  artistnum = detailurl.split("/")[len(detailurl.split("/"))-1]
  detailpage = fetch(detailurl, "%s" % artist.replace("/","_"), "artists", nocache = False)

  # example -- <audio src="http://audio.sxsw.com/2018/mp3_by_artist_id/9bcd62f9d36703d530e39503818e2bf9fd84c2d177999c1b2c17be198e976961.mp3"></audio>
