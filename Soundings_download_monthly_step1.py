# coding: utf-8

from urllib.request import urlopen
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
#import matplotlib #only needed to determine Matplotlib version number
import os, sys
import re
import time
import glob
#import matplotlib.pyplot as plt
from scipy import interpolate
import calendar


year_i = 1979
year_f = 2015

datei = datetime(year_i, 1, 1, 0)
datef = datetime(year_f, 12, 31, 12)

dt = datetime(year_i, 1, 1, 0)

error = 0
error_arr = []

ferror = 'file_error.txt'

stations = open('stations_arctic.txt', 'r')
for line in stations:
    aa = line.split(';')
    stn_number = aa[0].replace("''", '')

    if stn_number == "#":
        #skip line
        print("skipped ",aa[2], stn_number)
        continue
    stn_name = aa[1].replace('(', '').replace(')', '').replace(' ', '_').replace("''", '').replace("\n", '').replace("/", '_')

    print(stn_name, stn_number)

    i = 0

    for y in range(year_i, year_f+1):

        for m in range(1, 13):
            m_range = calendar.monthrange(y, m)


            url = 'http://weather.uwyo.edu/cgi-bin/sounding?region=naconf&TYPE=TEXT%3ALIST&YEAR={0}&MONTH={1:02d}&FROM={2:02d}{3:02d}&TO={4:02d}{5:02d}&STNM={6}'.format(y, m, 1, 0, m_range[1], 12, stn_number)

            #print url
            try:
                content = urlopen(url).read()
            except:
                print("Sleeping for 15sec and trying again")
                time.sleep(15)

                content = urlopen(url).read()

                ferr = open(ferror, 'a')
                ferr.write(url + '\n')
                ferr.close()

            soup = BeautifulSoup(content, features="html5lib")
            data_text = soup.get_text()

            splitted = data_text.split("\n",data_text.count("\n"))

            if not os.path.isdir(stn_name):
                os.mkdir(stn_name)

            Sounding_filename = '{4}/{7}.{0}{1:02d}{2:02d}{3:02d}_{0}{1:02d}{5:02d}{6:02d}.txt'.format(y, m, 1, 0, stn_name, m_range[1], 12, stn_number)
            #print Sounding_filename
            f = open(Sounding_filename,'w')



                #21946 Chokurdah Observations at 12Z 14 Nov 2006
#00000000011111111112222222222333333333344444444445555555555666666666677777777777
#012345678901234567890123456789012345678901234567890123456789012345678901234567890
#-----------------------------------------------------------------------------
#   PRES   HGHT   TEMP   DWPT   RELH   MIXR   DRCT   SKNT   THTA   THTE   THTV
#    hPa     m      C      C      %    g/kg    deg   knot     K      K      K
#-----------------------------------------------------------------------------
# 1024.0     61  -10.1  -12.8     81   1.40     90      8  261.3  265.1  261.5
#   73.9  17721  -65.7                                     436.7         436.7
            for line in splitted[3:]:
                #for ll in xrange(0,77,7):
                #    f.write(line[0+ll:ll+7])
                #f.write("\n")
                #f.write(re.sub('\s+', ',', line)[1:]+'\n')
                f.write(line + '\n')
            f.close()

            print(Sounding_filename)


stations.close()





            #sys.exit()
