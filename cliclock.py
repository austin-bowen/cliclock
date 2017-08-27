#!/usr/bin/env python3

# Copyright (c) 2017 Austin Bowen
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

'''cliclock.py - A clock for the command line.'''

# TODO: Easter eggs:
# - Error 404: Time not found
# - 420 Blaze it!
# - 3:145926535...

__filename__ = 'cliclock.py'
__version__  = '0.1'
__author__   = 'Austin Bowen <austin.bowen.314@gmail.com>'

import time

from blessings import Terminal
from datetime  import datetime
from math      import floor

FULL_BLOCK_CHAR = '\u2588'

'''Each number is defined by a set of segments as shown:

    0000
  11    22
  11    22
    3333
  44    55
  44    55
    6666
'''
NUMBER_SEGMENTS = {
    0: {0, 1, 2, 4, 5, 6},
    1: {2, 5},
    2: {0, 2, 3, 4, 6},
    3: {0, 2, 3, 5, 6},
    4: {1, 2, 3, 5},
    5: {0, 1, 3, 5, 6},
    6: {0, 1, 3, 4, 5, 6},
    7: {0, 2, 5},
    8: {0, 1, 2, 3, 4, 5, 6},
    9: {0, 1, 2, 3, 5},
}

def cliclock(fg=FULL_BLOCK_CHAR, bg=' '):
    term = Terminal()
    
    with term.fullscreen(), term.hidden_cursor(), term.location(0, 0):
        try:
            while True:
                dt = datetime.now()
                print_datetime(term, dt, fg, bg)
                wait_time_or_resize(term, 1-(dt.microsecond/1000000))
        except KeyboardInterrupt:
            pass

def print_datetime(term, dt, fg=FULL_BLOCK_CHAR, bg=' '):
    print(term.clear)
    
    hour   = '%.2d' %(dt.hour % 12)
    minute = '%.2d' %dt.minute
    second = '%.2d' %dt.second
    
    # Number width calculation:
    # fw = 6nw + 3ns + 5gs
    # ns = nsr*nw
    # gs = gsr*nw
    # ==> fw = 6nw + 3*nsr*nw + 4*gsr*nw
    #        = nw * (6 + 3nsr + 4gsr)
    # ==> nw = fw / (6 + 3nsr + 4gsr)
    
    # Determine the number width (ratios are WRT number width)
    number_sep_ratio = .3
    group_sep_ratio  = .5
    number_width     = term.width / (6 + 3*number_sep_ratio + 4*group_sep_ratio)
    number_width     = floor(number_width)
    
    number_height = number_width-1
    number_sep    = floor(number_width*number_sep_ratio)
    group_sep     = floor(number_width*group_sep_ratio)
    full_width    = 6*number_width + 3*number_sep + 4*group_sep
    x = round((term.width-1-full_width)/2) + group_sep
    y = floor((term.height-1-number_height)/2)
    
    # Print hour group
    if (hour[0] != '0') or True:
        print_number(term, hour[0], (x, y), (number_width, number_height), fg, bg)
    x += number_width+number_sep
    print_number(term, hour[1], (x, y), (number_width, number_height), fg, bg)
    
    # Print minute group
    x += number_width+group_sep
    print_number(term, minute[0], (x, y), (number_width, number_height), fg, bg)
    x += number_width+number_sep
    print_number(term, minute[1], (x, y), (number_width, number_height), fg, bg)
    
    # Print second group
    x += number_width+group_sep
    print_number(term, second[0], (x, y), (number_width, number_height), fg, bg)
    x += number_width+number_sep
    print_number(term, second[1], (x, y), (number_width, number_height), fg, bg)
    
    # Print date
    d = dt.date()
    d = d.strftime('%A, %B %d, %Y')
    x = round((term.width-1-len(d))/2)
    y = y + number_height + 1
    with term.location(x, y):
        print(term.bold + d)

def print_number(term, number, origin, size, fg=FULL_BLOCK_CHAR, bg=' '):
    number = int(number)
    x, y   = origin
    w, h   = size
    if (fg == None): fg = str(number)
    
    top_line    = 0
    center_line = floor((h-1)/2)
    bottom_line = h-1
    segments    = NUMBER_SEGMENTS[number]
    
    for line in range(h):
        with term.location(x, y+line):
            s = ''
            
            # Segment 0?
            if (line == 0):
                s += (fg if (0 in segments or 1 in segments) else bg)*2
                s += (fg if 0 in segments else bg)*(w-4)
                s += (fg if (0 in segments or 2 in segments) else bg)*2
            
            # Segments 1 and 2?
            elif (line < center_line):
                s += (fg if 1 in segments else bg)*2
                s += bg*(w-4)
                s += (fg if 2 in segments else bg)*2
            
            # Segment 3?
            elif (line == center_line):
                s += (fg if any(s in segments for s in {1, 3, 4}) else bg)*2
                s += (fg if 3 in segments else bg)*(w-4)
                s += (fg if any(s in segments for s in {2, 3, 5}) else bg)*2
            
            # Segments 4 and 5?
            elif (line < bottom_line):
                s += (fg if 4 in segments else bg)*2
                s += bg*(w-4)
                s += (fg if 5 in segments else bg)*2
            
            # Segment 6?
            else:
                s += (fg if (4 in segments or 6 in segments) else bg)*2
                s += (fg if 6 in segments else bg)*(w-4)
                s += (fg if (5 in segments or 6 in segments) else bg)*2
            
            print(s, end='', flush=True)

def wait_time_or_resize(term, t, check_interval=0.2):
    t0 = time.time()
    w, h = term.width, term.height
    elapsed_time   = time.time()-t0
    remaining_time = t-elapsed_time
    while (elapsed_time < t and w == term.width and h == term.height):
        if (remaining_time > check_interval):
            time.sleep(check_interval)
            elapsed_time   = time.time()-t0
            remaining_time = t-elapsed_time
        else:
            time.sleep(remaining_time)
            return

def main():
    return cliclock()

if (__name__ == '__main__'):
    import sys
    sys.exit(main())
