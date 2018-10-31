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
#import matplotlib.pyplot as plt
from scipy import interpolate

#
# Read the csvs with the yearly soundings data and interpolate to nice levels
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

    for level in range(new_val.shape[0]):
        #print(pressure_levels[level])
        new_val[level] = f(pressure_levels[level])

    return new_val


# Reading the files to generate the pandas dataframe and calculate the means values
# files: 71082.2000010500.txt
#pressure_levels = [150.0, 200.0, 250.0, 300.0, 400.0, 500.0, 600.0, 700.0, 800.0, 850.0, 900.0, 925.0, 950.0, 975.0, 1000.0]

#press_original = df2['PRES'].values.astype(float)
#temp_original = df2['TEMP'].values.astype(float)
pressure_levels = [1000., 975., 950., 925., 900., 875., 850., 825., 800., 750., 700., 650., 600., 550., 500.]
types = ['PRES', 'HGHT', 'TEMP', 'DWPT', 'RELH', 'MIXR', 'DRCT', 'SKNT', 'THTA', 'THTE', 'THTV']

#new_values = interpPressure(press_original, pressure_levels, temp_original, 'linear')

error = 0
error_arr = []

stations = open('stations_arctic_step3.txt', 'r')

for line in stations:
    aa = line.split(';')
    stn_number = aa[0].replace("''", '')

    if stn_number == "#":
        #skip line
        print("skipped ",aa[2], stn_number)
        continue
    print(aa)
    stn_name = aa[1].replace('(', '').replace(')', '').replace(' ', '_').replace("''", '').replace("\n", '').replace("/", '_')

    print(stn_name, stn_number)

    i = 0

    df = pd.DataFrame()
    print (df)

    arquivos = glob.glob('{1}/soundings_{0}_????.csv'.format(stn_number, stn_name))
    #print '{0}/soundings_{0}_*.csv'.format(stn)
    #sys.exit()
    arquivos.sort()

    year_i = 1979
    dt = datetime(year_i, 1, 1, 0, 0)
    date_f = datetime(year_i, 12, 31, 12, 0)

    f = open("{0}/errors_{1}.txt".format(stn_name, stn_number), 'w')
    err = 0

    for arq in arquivos:

        df2 = pd.read_csv(arq, index_col=0)

        print ("file: " + arq)
        print ("********************")
        #print dt, date_f
        #print "************"
        # Loop throught the soundings
        while dt <= date_f:

            #print "date: ", dt, "datef: ", date_f
            # select sounding
            df_aux = df2.query("Year == {0} and Month == {1} and Day == {2} and Hour == {3}".format(dt.year, dt.month, dt.day, dt.hour))

            # Check if there is data to interpolate
            # Get the levels bellow 925. If 1000 is empty, remove it.
            # Interpolate the levels bellow 925, adding 925 if it doesn't exist.
            if not df_aux.empty:

                # Interpolate
                #press_original = pd.to_numeric(df_aux['PRES'], errors='coerce').values

                # removing indices where pressure < 850
                ind = df_aux[df_aux.PRES < 850].index
                df_aux = df_aux.drop(ind)

                press_original = pd.to_numeric(df_aux["PRES"], errors='coerce').values

                # Check if the first level exists.
                if (len(press_original) >= 3):
                    if (press_original[0] >= 1000. and press_original[-1] <= 850.):

                        # If the values of PRES=1000 equals NaN, remove it
                        try:
                            ind = df_aux[df_aux.PRES == 1000].index[0]
                        except:
                            print("Do not have 1000hPa, skipping    ")
                            dt = dt + timedelta(hours=12)
                            continue

                        # We dont have the 1000 hPa level. removing it
                        if np.isnan(df_aux.loc[ind,"TEMP"]):
                            df_aux = df_aux.drop([ind])

                        # removing indices where pressure < 900
                        #ind = df_aux[df_aux.PRES < 900].index
                        #df_aux = df_aux.drop(ind)

                        pressure_levels = df_aux.PRES.values

                        # Check to see if we have the 925 hPa level
                        aux = df_aux[df_aux.PRES == 925].index

                        if aux.empty:
                            # add the 925 level
                            pressure_levels = np.insert(pressure_levels, 0, 925)
                            pressure_levels[::-1].sort()

                        # If the 925hPa level is the first one, jump to the next date
                        if pressure_levels[0] == 925:
                            print("First level is 925hpa, skipping    ")
                            print(pressure_levels)
                            dt = dt + timedelta(hours=12)
                            continue


                        array_tmp = np.zeros([len(types), len(pressure_levels)])
                        array_tmp[0,:] = pressure_levels

                        for j in range(len(types)-1):
                            var_original = pd.to_numeric(df_aux[types[j+1]], errors='coerce').values
                            press_original = pd.to_numeric(df_aux["PRES"], errors='coerce').values
                            #print(var_original)
                            #print(press_original)
                            #print(pressure_levels)
                            #print(types[j+1])
                            #sys.exit()
                            array_tmp[j+1,:] = interpPressure(press_original, pressure_levels, var_original, 'linear')

                            #print var_original, array_tmp[j+1,:]

                        df3 = pd.DataFrame(data=array_tmp.transpose(), columns=types)
                        df3['Date'] = dt
                        df3['Day'] = dt.day
                        df3['Month'] = dt.month
                        df3['Year'] = dt.year
                        df3['Hour'] = dt.hour
                        df3['Location'] = stn_number

                        # Get the temperature gradient

                        frames = [df, df3]
                        df = pd.concat(frames)
                    else:
                        err += 1
                        f.write("Not enough levels near the surface. Date: {0}, pressure levels: {1}\n".format(dt, press_original))
                else:
                    err += 1
                    f.write("Not enough data. Date: {0}, pressure levels: {1}\n".format(dt, press_original))
            else:
                err += 1
                f.write("Sounding for this day missing. Date: {0}\n".format(dt))
            # go to next sounding
            dt = dt + timedelta(hours=12)

        year_i += 1
        date_f = datetime(year_i, 12, 31, 12, 0)


    df.to_csv('{0}/soundings_{1}_interp_v3.csv'.format(stn_name, stn_number), encoding='utf-8')
    f.write("\nTotal errors: {0}".format(err))
    f.close()
    #sys.exit()
