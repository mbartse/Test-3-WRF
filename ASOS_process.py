import pandas as pd
import numpy as np
from wrf import (to_np, getvar, smooth2d, get_cartopy,vertcross, cartopy_xlim, 
    cartopy_ylim, latlon_coords, ALL_TIMES, uvmet, interplevel, CoordPair, interpline, 
    ll_to_xy, xy_to_ll, extract_global_attrs,extract_times)
def ASOS_process(files_Case_A_dataset, Land_mask, date_generated, df_asos):
    df = pd.concat([df_asos])
    df.sort_values(by=['DATETIME'],inplace=True)

    df = df.replace(['M',np.nan],'NaN')
    df.rename(columns = {'Outdoor Temperature':'Temperature', 'Resultant Wind Direction':'WDir','Wind Speed':'WSpeed','Nitrogen Dioxide':'NO2','Relative Humidity':'RH'}, inplace = True)
    df['Temperature'] = pd.to_numeric(df.Temperature, errors='coerce')
    df['WDir'] = pd.to_numeric(df.WDir, errors='coerce')
    df['WSpeed'] = pd.to_numeric(df.WSpeed, errors='coerce')
    # df['NO2'] = pd.to_numeric(df.NO2, errors='coerce')
    # df['Ozone'] = pd.to_numeric(df.Ozone, errors='coerce')
    df['RH'] = pd.to_numeric(df.RH, errors='coerce')

    # ASOS WSpeed Knots to m/s
    df.loc[df['source'] == 'ASOS' , 'WSpeed'] = df.loc[df['source'] == 'ASOS' , 'WSpeed'] * 0.514444

    temp = df.pivot_table('Temperature',['DATETIME'],'Station')
    RH = df.pivot_table('RH',['DATETIME'],'Station')
    direct = df.pivot_table('WDir',['DATETIME'],'Station')
    speed = df.pivot_table('WSpeed',['DATETIME'],'Station')

    lst=[temp,RH,direct,speed]
    list1_original = df.Station.unique()
    for i in lst:
        list2 = i.columns.values
        missing_sta = set(list1_original).difference(list2)
        if len(missing_sta) > 0:
            for ii in missing_sta:
                i[ii] = np.nan

    def custom_resampler(arraylike):
        return np.nanmean(arraylike) 

    emp=[]
    for i in lst:
        df_temp=i
        df_temp=df_temp.resample('1min').mean()
        df_temp=df_temp.resample('60min').apply(custom_resampler)
        # df_temp=df_temp.bfill().ffill()
        df_temp=df_temp.reset_index()
        # df_temp=df_temp.loc[df_temp['DATETIME'].dt.minute.eq(0)]
        # df_temp=df_temp.set_index('DATETIME')
        i=df_temp
        emp.append(i)            

    temp_hr=emp[0]
    RH_hr=emp[1]
    direct_hr=emp[2]
    speed_hr=emp[3]

    temp_hr = pd.melt(temp_hr, id_vars=['DATETIME'],  ignore_index=True).sort_values(by=['DATETIME','Station']).reset_index(drop=True).rename(columns = {'value':'Temperature'})
    RH_hr = pd.melt(RH_hr, id_vars=['DATETIME'],  ignore_index=True).sort_values(by=['DATETIME','Station']).reset_index(drop=True).rename(columns = {'value':'RH'})
    direct_hr = pd.melt(direct_hr, id_vars=['DATETIME'],  ignore_index=True).sort_values(by=['DATETIME','Station']).reset_index(drop=True).rename(columns = {'value':'WDir'})
    speed_hr = pd.melt(speed_hr, id_vars=['DATETIME'],  ignore_index=True).sort_values(by=['DATETIME','Station']).reset_index(drop=True).rename(columns = {'value':'WSpeed'})
    df_resamp = pd.merge(pd.merge(pd.merge(temp_hr, direct_hr, on=['DATETIME', 'Station']), speed_hr,on=['DATETIME', 'Station']),RH_hr,on=['DATETIME', 'Station'])

    station_name = []
    station_lat = []
    station_long = []
    station_source = []
    WRF_lat = []
    WRF_long = []
    WRF_IDX = []
    WRF_IDY = []

    for x in df.Station.unique():
        station_name.append(x)
        station_source.append(df.loc[df['Station'] == x]['source'].values[0])
        station_lat.append(df.loc[df['Station'] == x]['lat'].values[0])
        station_long.append(df.loc[df['Station'] == x]['long'].values[0])

        wrf_loc_idx = ll_to_xy(files_Case_A_dataset[0], df.loc[df['Station'] == x]['lat'].values[0],df.loc[df['Station'] == x]['long'].values[0])
        wrf_loc_a = 1
        wrf_loc_b = 0 
        WRF_long.append(Land_mask[0]['XLONG'][wrf_loc_idx[wrf_loc_a],wrf_loc_idx[wrf_loc_b]].data)
        WRF_lat.append(Land_mask[0]['XLAT'][wrf_loc_idx[wrf_loc_a],wrf_loc_idx[wrf_loc_b]].data)

        WRF_IDX.append(wrf_loc_idx[wrf_loc_a].data)
        WRF_IDY.append(wrf_loc_idx[wrf_loc_b].data)

    # initialize data of lists.
    data = {'station_name': station_name,
            'station_source': station_source,
            'station_lat': station_lat,
            'station_long': station_long,
            'WRF_LAT': WRF_lat,
            'WRF_LONG': WRF_long,
            'WRF_IDX': WRF_IDX,
            'WRF_IDY': WRF_IDY}
    # Create dataframe
    df_loc = pd.DataFrame(data, dtype=np.float32)
    df_loc[['WRF_IDX', 'WRF_IDY']] = df_loc[['WRF_IDX', 'WRF_IDY']].astype(int)

    df_resamp['LONG'] = 1.0 
    df_resamp['LAT'] = 1.0
    df_resamp['Source'] = 1.0
    df_resamp['WRF_LONG'] = 1.0 
    df_resamp['WRF_LAT'] = 1.0
    df_resamp['WRF_IDX'] = 1
    df_resamp['WRF_IDY'] = 1
    df_resamp['WRF_Temp'] = 1.0
    df_resamp['WRF_WSpeed'] = 1.0
    df_resamp['WRF_WDir'] = 1.0
    df_resamp['WRF_U'] = 1.0
    df_resamp['WRF_V'] = 1.0
    df_resamp['WRF_RH'] = 1.0

    df_resamp = df_resamp[df_resamp['DATETIME'].isin(date_generated)]
    return df_resamp, df_loc