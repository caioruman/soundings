import numpy as np
import pandas as pd
#from sklearn import linear_model
#from sklearn.metrics import mean_squared_error, r2_score
from glob import glob
import os
from datetime import datetime, timedelta

def main():
  """
   Read the soundings and calculate the mean and statistics of the temperature inversion parameters

   Only save data if there are at least 80% of valid values in the 2003-2015 period.
  """

  datai = 2003
  dataf = 2015
  periods = [('DJF', [12, 1, 2]), ('JJA', [6, 7, 8])]

  dd = "/pixel/project01/cruman/Data/Soundings"

  #tarray = np.arange(datetime(datai,1,1,0), datetime(dataf,12,31,12), timedelta(hours=12)).astype(datetime)
  t_pd = pd.Series(pd.date_range(start='{0}-01-01 00:00'.format(datai), end='{0}-12-31 12:00'.format(dataf), freq="12H"))


  #print(tarray)
  list_dir = sorted([f for f in os.listdir('.') if os.path.isdir(f) and not f.startswith('.')])

  f = open('inversion_results.csv', 'a')

  f.write('stationName, deltaT, deltaT_std, dtdz, dtdz_std, freq, season\n')

  for dname in list_dir:
    
    fname = glob('{0}/{1}/*fill1000.csv'.format(dd,dname))[0]
    print(dname)
    df = pd.read_csv(fname, index_col=0)
    df['Date'] = pd.to_datetime(df['Date'])

    for per in periods:
      t_season = pd.Series(dtype='datetime64[ns]')
      for m in per[1]:
        t_season = t_season.append(t_pd[(t_pd.dt.month == m)])

      i = 0
      s = 0
      n = 0
      deltaT_l = []
      dtdz_l = []

      for t in t_season:
        date_f = t + timedelta(hours=12)
        mask = (df['Date'] > t) & (df['Date'] <= date_f) & (df['PRES'] >= 850)

        aux = df.loc[mask]

        if aux.empty:
          i += 1
          continue
        
        if i > 432:
          # more than 20% of the data is empy. Skip location
          break

        #print(aux)

        deltaT = aux['TEMP'].iloc[-1] - aux['TEMP'].iloc[0]
        deltaZ = (aux['HGHT'].iloc[-1] - aux['HGHT'].iloc[0])/1000

        dtdz = deltaT/deltaZ

        if deltaT > 0:
          s += 1
          deltaT_l.append(deltaT)
          dtdz_l.append(dtdz)
        else:
          n += 1

      # Save data
      freq = float(s) / (n + s)

      #f.write('stationName, deltaT, deltaT_std, dtdz, dtdz_std, freq, season\n')
      f.write('{0};{1:3.2f};{2:3.2f};{3:3.2f};{4:3.2f};{5:3.2f};{6}\n'.format(dname, np.mean(deltaT_l), np.std(deltaT_l),
                                               np.mean(dtdz_l), np.std(dtdz_l), freq, per[0]))
    
  f.close()

    #print(df.head())


if __name__ == '__main__':
    main()
