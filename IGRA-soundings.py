import numpy as np
import pandas as pd
from glob import glob
import os
from datetime import datetime, timedelta

def main():

  igra_folder = '/pixel/project01/cruman/Data/IGRA'

  # Read the stations file
  df_station = pd.read_csv(f'{igra_folder}/igra2-station-list-filter-r.txt', delim_whitespace=True, names=['ID', 'LAT', 'LON', 'ALT', 'NAME', 'YearI', 'YearF', 'OtherID'])
  #BEM00006447 50.7969 4.3581 99.0 UCCLE 1949 2015 42558
  datai = 2003 
  dataf = 2015

  f = open('soundings-IGRA.txt', 'w')


  f.write('NAME,ID,ALT,LAT,LON,SEASON,DELTAT,DT_STD,DTDZ,DTDZ_STD\n')

  #f.close()

  #f = open('soundings-IGRA.txt', 'a')

  for row in df_station.iterrows():
    row = row[1]
    lat = row.LAT
    lon = row.LON
    name = row.NAME
      
      
    # reading the soundings
    df = pd.read_csv(f'{igra_folder}/{row.ID}/{row.ID}.txt', delim_whitespace=True)
    df['NOMINAL'] =  pd.to_datetime(df['NOMINAL'], format='%Y%m%d%H')
    df['TEMPERATURE'] = df['TEMPERATURE'].replace(-9999.0, np.nan)
    df['GPHEIGHT'] = df['GPHEIGHT'].replace(-9999, np.nan)

    t_pd = pd.Series(pd.date_range(start='{0}-01-01 00:00'.format(datai), end='{0}-12-31 12:00'.format(dataf), freq="12H"))
    
    season = [12, 1, 2]
    sname = "DJF"
    dt, dt_std, dtdz, dtdz_std, freq = calcSoundingsIGRA(df, row.ALT, season, sname, t_pd, name)    

    f.write(f'{row.NAME},{row.ID},{row.ALT},{row.LAT},{row.LON},{sname},{dt:3.2f},{dt_std:3.2f},{dtdz:3.2f},{dtdz_std:3.2f},{freq:3.2f}\n')
    
    season = [6, 7, 8]
    sname = "JJA"
    dt, dt_std, dtdz, dtdz_std, freq = calcSoundingsIGRA(df, row.ALT, season, sname, t_pd, name)    

    f.write(f'{row.NAME},{row.ID},{row.ALT},{row.LAT},{row.LON},{sname},{dt:3.2f},{dt_std:3.2f},{dtdz:3.2f},{dtdz_std:3.2f},{freq:3.2f}\n')
    #f.write('NAME,ID,ALT,LAT,LON,SEASON,DELTAT,DT_STD,DTDZ,DTDZ_STD\n')

  f.close()
    
def calcSoundingsIGRA(df, alt, season, sname, t_pd, name):

  print(f"calculating values for {name} and season {sname}")
  
  # Filterin for season
  t_pd = t_pd[(t_pd.dt.month == season[0]) | (t_pd.dt.month == season[1]) | (t_pd.dt.month == season[2])]
  
  dt_l = []
  dtdz_l = []
  i = 0
  k = 0
  total = 0
  for date in t_pd:
    date_f = date + timedelta(hours=12)
    mask = (df['NOMINAL'] > date) & (df['NOMINAL'] <= date_f) & (df['PRESSURE'] >= 850)
    
    aux = df.loc[mask]
    total += 1
    if not aux.empty:
      if aux['TEMPERATURE'].iloc[-1] <= -999 or aux['TEMPERATURE'].iloc[0] <= -999:
        continue
      deltaT = aux['TEMPERATURE'].iloc[-1] - aux['TEMPERATURE'].iloc[0]
      dtdz = deltaT/(aux['GPHEIGHT'].iloc[-1] - alt)

      if not np.isnan(deltaT):
        if deltaT > 0:
          dt_l.append(deltaT)
          dtdz_l.append(dtdz)
          k += 1
        i += 1
  
  # if there are no inversions or if less than 1500 dates to calculate
  if len(dt_l) == 0 or i < 1500:
    dtdz = np.nan
    deltaT = np.nan
    freq = np.nan
    dtdz_std = np.nan
    deltaT_std = np.nan
  else:
    dtdz = np.mean(dtdz_l)
    deltaT = np.mean(dt_l)
    freq = float(k)/i
    
    dtdz_std = np.std(dtdz_l)
    deltaT_std = np.std(dt_l)
  
  #dt, dt_std, dtdz, dtdz_std, freq
  return deltaT, deltaT_std, dtdz, dtdz_std, freq
    
if __name__ == "__main__":
  main()