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

# Calculate the mean inversion strength and the mean inversion percentage
yeari = 1986
yearf = 2015
stations = open('latlonlist_v2.txt', 'r')
df_list = []
i = 0
# Loop throught all the stations
outdata = open('inv_list.dat', 'w')
outdata.write("Station_number;Latitude;Longitude;Inv_00;Inv_P_00;Inv_12;Inv_P_12;Inv_TT;Inv_P_TT;TotalYear;TotalYearTT\n")
for line in stations:
    df_list = []
    aa = line.split(';')
    stn_number = aa[0].replace("''", '')
    stn_lat = aa[3].replace("\n",'')
    stn_lon = aa[5].replace("\n",'')
    stn_name = aa[1]

    # Just in the testing phase
    #if stn_number == "#":
        #skip line
        #print("skipped ",aa[2], stn_number)
    #    stn_number = aa[1].replace("''", '')
    #    print(stn_number)
    #else:
    #    continue
    #print(aa)
    # change to 1 later
    #stn_name = aa[2].replace('(', '').replace(')', '').replace(' ', '_').replace("''", '').replace("\n", '').replace("/", '_')

    print(stn_name, stn_number, stn_lat, stn_lon)

    #Open interpolated file
    #arq = "{0}/soundings_{1}_interp.csv".format(stn_name, stn_number)
    arq = "Stations/{0}/soundings_{1}_inversion.csv".format(stn_name, stn_number)
    print(arq)
    df = pd.read_csv(arq, index_col=0)

    if not df.empty:
        aux = []
        years = np.zeros((2))
        for tt in [0,12,100]:
            if tt != 100:
                df2 = df.query("Hour == {0}".format(tt))
                years[0] = len(df2.index)/365
            else:
                df2 = df
                years[1] = len(df2.index)/365/2

            inv = df2.INV_S.values
            inv_num = len(inv[inv>0])
            total = len(inv)
            inv_perc = (inv_num/total)*100
            inv_mean = np.mean(inv[inv>0])
            aux.append((inv_mean, inv_perc))

        print(aux)
        if (years[0] >= 20):
            outdata.write("{0};{1};{2};{3:2.3f};{4:3.3f};{5:2.3f};{6:3.3f};{7:2.3f};{8:3.3f};{9:3.3f};{10:3.3f}\n".format(stn_number,stn_lat,stn_lon,aux[0][0],aux[0][1],aux[1][0],aux[1][1],aux[2][0],aux[2][1], years[0], years[1]))
        else:
            print("Not enough years",stn_number,years)
#        "Station_number;Latitude;Longitude;Inv_00;Inv_P_00;Inv_12;Inv_P_12;Inv_TT;Inv_P_TT;TotalYear;TotalYearTT\n"
#        sys.exit()

stations.close()
outdata.close()
