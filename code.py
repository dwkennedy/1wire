#!/usr/bin/python
# this is the code that goes in the http directory

import os
import rrdtool
import tempfile
import web

# web.py app URL routing setup
URLS = ('/graph.png', 'Graph',
        '/view', 'Page')

RRD_FILE = '/var/1w_files/templog.rrd'
SCALES = ('hour', 'qtrday', 'semiday', 'day', 'week', 'month', 'quarter', 'half', 'year')
RESOLUTIONS = {'hour': '-1hours', 'qtrday': '-6hours', 'semiday': '-13hours', 'day': '-26hours', 'week':'-8d', 'month':'-35d', 'quarter':'-90d',
  'half':'-6months', 'year':'-1y'}

class Page:
    def GET(self):
        scale = web.input(scale='hour').scale.lower()
        if scale not in SCALES:
            scale = SCALES[0]
        result = '<html><head><title>Refrigerator Logger</title><meta http-equiv="refresh" content="60"></head><h4>'
        for tag in SCALES:
            if tag == scale:
                result += '| %s |' % (tag,)
            else:
                result += '| <a href="./view?scale=%s">%s</a> |' % (tag, tag)
        result += '</h4>'
        result += '<img src="./graph.png?scale=%s">' % (scale, )
        result += '</html>'
        web.header('Content-Type', 'text/html')
        return result
 
class Graph:
  def GET(self):
      scale = web.input(scale='day').scale.lower()
      if scale not in SCALES:
          scale = SCALES[0]
      fd,path = tempfile.mkstemp('.png')
      rrdtool.graph(path,
                    '-w 900',  '-h',  '400', '-a', 'PNG',
                    '--start',  ',%s' % (RESOLUTIONS[scale], ),
                    '--end', 'now',
                    '--vertical-label',  'temperature (C)',
                    '--right-axis', '1.8:32',
                    '--right-axis-label', 'temperature (F)',
                    'DEF:ambient=%s:ambient:AVERAGE' % (RRD_FILE, ),
                    'DEF:freezer=%s:freezer:AVERAGE' % (RRD_FILE, ),
                    'DEF:fridge=%s:fridge:AVERAGE' % (RRD_FILE, ),
                    'DEF:light=%s:light:AVERAGE' % (RRD_FILE, ),
                    'CDEF:light_offset=light,11,-',
                    'HRULE:4.45#000000::dashes',
                    'HRULE:1.67#000000::dashes',
                    'HRULE:-12.0#000000::dashes',
                    'HRULE:-18.0#000000::dashes',
                    'HRULE:0#000000',
                    'LINE2:ambient#00ff00:ambient ',
                    'GPRINT:ambient:LAST:Cur\:%8.2lf',
                    'GPRINT:ambient:AVERAGE:Avg\:%8.2lf',
                    'GPRINT:ambient:MAX:Max\:%8.2lf',
                    r'GPRINT:ambient:MIN:Min\:%8.2lf\j',
                    'LINE2:freezer#0000ff:freezer ',
                    'GPRINT:freezer:LAST:Cur\:%8.2lf',
                    'GPRINT:freezer:AVERAGE:Avg\:%8.2lf',
                    'GPRINT:freezer:MAX:Max\:%8.2lf',
                    r'GPRINT:freezer:MIN:Min\:%8.2lf\j',
                    'LINE2:fridge#ff0000:fridge  ',
                    'GPRINT:fridge:LAST:Cur\:%8.2lf',
                    'GPRINT:fridge:AVERAGE:Avg\:%8.2lf',
                    'GPRINT:fridge:MAX:Max\:%8.2lf',
                    r'GPRINT:fridge:MIN:Min\:%8.2lf\j',
                    'LINE2:light_offset#000000:light on/off ')
      data = open(path, 'r').read()
      fd.close()
      os.unlink(path)
      web.header('Content-Type', 'image/png')
      return data
      

if __name__ == "__main__":
    web.application(URLS, globals()).run()
