from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import numpy.ma as ma
#import matplotlib #only needed to determine Matplotlib version number
import sys
import re
import time
import glob
import matplotlib.pyplot as plt
from scipy import interpolate
from scipy import stats

yeari = 1986
yearf = 2015
stations = open('stations_arctic_step4.txt', 'r')
#cols=["INV_S", "INV_F", "Hour", "Date", "STN_Number"]
cols=["GRADT", "INV_S", "Date", "Year", "Month", "Day", "Hour", "STN_Number"]

df_list = []
i = 0
# Loop throught all the stations
for line in stations:
    df_list = []
    aa = line.split(';')
    stn_number = aa[0].replace("''", '')

    if stn_number == "#":
        #skip line
        print("skipped ",aa[2], stn_number)
        continue
    print(aa)
    stn_name = aa[1].replace('(', '').replace(')', '').replace(' ', '_').replace("''", '').replace("\n", '').replace("/", '_')

    print(stn_name, stn_number)

    #Open interpolated file
    #arq = "{0}/soundings_{1}_interp.csv".format(stn_name, stn_number)
    arq = "Stations/{0}/soundings_{1}_interp_v3.csv".format(stn_name, stn_number)
    df = pd.read_csv(arq, index_col=0)

    dt = datetime(yeari, 1, 1, 0, 0)
    date_f = datetime(yearf, 12, 31, 12, 0)

    # Calculate the monthly values

    if not df.empty:
        while dt <= date_f:
            for tt in [0, 12]:
                # Filter for the values of the first level and 925 hPa


                df_1000 = df.query("Year == {0} and Month == {1} and Day == {2} and Hour == {3}".format(dt.year, dt.month, dt.day, tt))
                df_925 = df.query("Year == {0} and Month == {1} and Day == {2} and PRES == {3} and Hour == {4}".format(dt.year, dt.month, dt.day, 925, tt))

                # If there are no data on the selected date
                if (len(df_1000.index) == 0):
                    #print(df_1000.index, dt, tt)
                    continue

                # Selecting the first level with data                
                if not np.isnan(df_1000.iloc[0].TEMP):
                    tmp = df_1000.iloc[0].TEMP
                    pres = df_1000.iloc[0].PRES
                else:
                    continue

                tmp_925 = df_925.TEMP.values[0]
                pres_925 = df_925.PRES.values[0]

                temp_diff = tmp-tmp_925
                pres_diff = pres-pres_925

                grad_temp_pres = temp_diff/pres_diff  # in K/hPa
                inv_strength = grad_temp_pres*(75) # in K. Inversion between 925 and 1000 hPa

                #filter high values
                if (inv_strength > 30):
                    continue

                df_list.append((grad_temp_pres, inv_strength, dt, dt.year, dt.month, dt.day, tt, stn_number))

            dt = dt + timedelta(hours=24)

    df_end = pd.DataFrame(df_list, columns=cols)
    df_end.to_csv("Stations/{0}/soundings_{1}_inversion.csv".format(stn_name, stn_number), encoding='utf-8')


# In[67]:

stations.close()
