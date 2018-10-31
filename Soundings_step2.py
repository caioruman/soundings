
# coding: utf-8

#import urllib2
#from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
#import matplotlib #only needed to determine Matplotlib version number
import sys
import re
import time
import glob
import calendar
#import matplotlib.pyplot as plt
from scipy import interpolate


#
#  Read the monthly soundings files and create an csv with the data
#



def interpPressure(pressure, pressure_levels, data, interp='linear'):
    """
    Interpolate data to custom pressure levels

    pressure: Original pressure level

    pressure_levels: Custom pressure level

    data: Original variable to be interpolated to custom pressure level

    returns: new_val, the original variable interpolated.
    """
    new_val = np.zeros_like(pressure_levels)

    f = interpolate.interp1d(pressure, data, kind=interp)

    for level in xrange(new_val.shape[0]):
        new_val[level] = f(pressure_levels[level])

    return new_val


# Reading the files to generate the pandas dataframe and calculate the means values
# files: 71082.2000010500.txt


#press_original = df2['PRES'].values.astype(float)
#temp_original = df2['TEMP'].values.astype(float)
pressure_levels = [1000., 975., 950., 925., 900., 875., 850., 825., 800., 750., 700., 650., 600., 550., 500., 400.]
types = ['HGHT', 'TEMP', 'DWPT', 'RELH', 'MIXR', 'DRCT', 'SKNT', 'THTA', 'THTE', 'THTV']

#new_values = interpPressure(press_original, pressure_levels, temp_original, 'linear')

error = 0
error_arr = []
df = pd.DataFrame()

def tofloat(value):
  try:
    aux = float(value)
    return aux
  except ValueError:
    return np.nan

mon = 0

header = "PRES,HGHT,TEMP,DWPT,RELH,MIXR,DRCT,SKNT,THTA,THTE,THTV\n"

stations = open('stations_arctic_step2.txt', 'r')

for line in stations:
    aa = line.split(';')
    stn_number = aa[0].replace("''", '')

    if stn_number == "#":
        #skip line
        print("skipped ",aa[2], stn_number)
        continue
    stn_name = aa[1].replace('(', '').replace(')', '').replace(' ', '_').replace("''", '').replace("\n", '').replace("/", '_')

    print(stn_name, stn_number)

    arquivos = glob.glob('{0}/{1}.*_*'.format(stn_name, stn_number))

    arquivos.sort()
    df = pd.DataFrame(columns=["PRES", "HGHT", "TEMP", "DWPT", "RELH", "MIXR", "DRCT", "SKNT", "THTA", "THTE", "THTV", "Year", "Month", "Day", "Hour"])
    i = 0
    for arq in arquivos:

        # Each time I find the Station number, a new day started.
        f = open(arq,'r')

        for line in f:
            line = line.replace("\n","")

            #if line[0] == "-":
                #continue

            # after the date, skip the next 4 lines
            if (line[0:5] == stn_number):
                # New date
                year = int(line[-4:])
                mon_abbr = line[-8:-5]
                day = int(line[-11:-9])
                hour = int(line[-15:-13])
                mon = list(calendar.month_abbr).index(mon_abbr)

                # new list
                #file_content = []
                #file_content.append(header)
            else:
                aux1 = line[0:7]

                #for ll in xrange(0,77,7):
                #    f.write(line[0+ll:ll+7])
                #f.write("\n")
                if np.isnan(tofloat(aux1)):
                    continue
                else:
                    #print [tofloat(line[0+x:7+x]) for x in xrange(0,77,7)] + [year, mon, day, hour]
                    df.loc[i] = [tofloat(line[0+x:7+x]) for x in range(0,77,7)] + [year, mon, day, hour]
                    i += 1

            if (i%500 == 0):
                print(i, [tofloat(line[0+x:7+x]) for x in range(0,77,7)] + [year, mon, day, hour])
        f.close()

        if (mon == 12):
            print("Year: " + str(year) + " Saving file to csv and creating a new one")
            df.to_csv('{2}/soundings_{0}_{1}.csv'.format(stn_number, year, stn_name), encoding='utf-8')
            df = pd.DataFrame(columns=["PRES", "HGHT", "TEMP", "DWPT", "RELH", "MIXR", "DRCT", "SKNT", "THTA", "THTE", "THTV", "Year", "Month", "Day", "Hour"])
            print(df)
            i = 0
            #if year == 1978:
            #    sys.exit()
    #sys.exit()
