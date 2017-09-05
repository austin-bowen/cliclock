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

from blessed  import Terminal
from datetime import datetime
from math     import ceil, floor

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

def cliclock(twelve_hour_format=False, fg=FULL_BLOCK_CHAR, bg=' '):
    term = Terminal()
    
    with term.fullscreen(), term.hidden_cursor(), term.cbreak():
        try:
            while True:
                dt = datetime.now()
                print_datetime(term, dt, twelve_hour_format, fg, bg)
                timeout = 1-(dt.microsecond/1000000)
                reason  = wait_key_press_or_resize(term, timeout)
                if (reason == 'key_press'): break
        except KeyboardInterrupt:
            pass

def print_colon(term, origin, size, fg=FULL_BLOCK_CHAR, bg=' '):
    x, y = origin
    w, h = size
    if (fg == None): fg = FULL_BLOCK_CHAR
    
    top_dot_top = floor(h/5)
    top_dot_bot = floor(2*h/5)
    bot_dot_top = ceil(3*h/5)
    bot_dot_bot = ceil(4*h/5)
    
    for line in range(h):
        with term.location(x, y+line):
            if   (line >= top_dot_top and line < top_dot_bot): s = fg*w
            elif (line >= bot_dot_top and line < bot_dot_bot): s = fg*w
            else: s = bg*w
            print(s, end='', flush=True)

def print_datetime(term, dt,
        twelve_hour_format=False, fg=FULL_BLOCK_CHAR, bg=' '):
    print(term.clear)
    with term.location(0, term.height-1):
        print('Press any key to quit')
    
    hour   = '%.2d' %((dt.hour % 12) if twelve_hour_format else dt.hour)
    minute = '%.2d' %dt.minute
    second = '%.2d' %dt.second
    
    # Time Height Calculation:
    # tw = 6nw + 2cw + 7sw + 2bw.
    # h  = nw-1 ==> nw = h+1.
    # cw = h*2/5.
    # sw = swr*nw = swr*(h+1).
    # bw = bwr*nw = bwr*(h+1).
    # ==> tw = 6(h+1) + h*4/5 + 7*swr*(h+1) + 2*bwr*(h+1)
    #        = 6h + 6 + h*4/5 + 7*swr*h + 7*swr + 2*bwr*h + 2*bwr
    #        = (6 + 4/5 + 7*swr + 2*bwr)*h + 6 + 7swr + 2bwr
    # ==> h  = (tw - 2bwr - 7swr - 6) / (2bwr + 7swr + 6.8).
    
    # Determine the height of the time
    border_width_ratio = 0.5    # WRT number width; can be changed.
    sep_width_ratio    = 0.3    # WRT number width; can be changed.
    h  = (term.width - 2*border_width_ratio - 7*sep_width_ratio - 6)
    h /= (2*border_width_ratio + 7*sep_width_ratio + 6.8)
    h  = min(term.height-6, floor(h))
    
    # Determine widths
    number_width = h+1
    colon_width  = floor(h*2/5)
    sep_width    = floor(sep_width_ratio*number_width)
    border_width = floor(border_width_ratio*number_width)
    time_width   = 6*number_width + 2*colon_width + 7*sep_width + 2*border_width
    
    # Determine starting origin
    x = round((term.width-1-time_width)/2) + border_width
    y = floor((term.height-1-h)/2)
    
    # Print hour group
    print_number(term, hour[0], (x, y), (number_width, h), fg, bg)
    x += number_width+sep_width
    print_number(term, hour[1], (x, y), (number_width, h), fg, bg)
    x += number_width
    
    # Print colon
    x += sep_width
    print_colon(term, (x, y), (colon_width, h), fg, bg)
    x += colon_width
    
    # Print minute group
    x += sep_width
    print_number(term, minute[0], (x, y), (number_width, h), fg, bg)
    x += number_width+sep_width
    print_number(term, minute[1], (x, y), (number_width, h), fg, bg)
    x += number_width
    
    # Print colon
    x += sep_width
    print_colon(term, (x, y), (colon_width, h), fg, bg)
    x += colon_width
    
    # Print second group
    x += sep_width
    print_number(term, second[0], (x, y), (number_width, h), fg, bg)
    x += number_width+sep_width
    print_number(term, second[1], (x, y), (number_width, h), fg, bg)
    
    # Print date
    d = dt.date()
    d = d.strftime('%A, %B %d, %Y')
    x = round((term.width-1-len(d))/2)
    y = y + h + 1
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

def wait_key_press_or_resize(term, timeout, check_interval=0.2):
    '''Waits until a key is pressed, the terminal is resized, or timeout.
    Returns the reason for returning: "key_press", "resize", or "timeout".
    '''
    t0 = time.time()
    w, h = term.width, term.height
    with term.cbreak():
        while True:
            # Check for timeout
            remaining_time = timeout-(time.time()-t0)
            if (remaining_time < check_interval):
                time.sleep(remaining_time)
                return "timeout"
            
            # Check for terminal resize
            if (term.width != w or term.height != h):
                return "resize"
            
            # Check for key press
            if term.inkey(timeout=check_interval):
                return "key_press"

def main():
    return cliclock()

if (__name__ == '__main__'):
    import sys
    sys.exit(main())
