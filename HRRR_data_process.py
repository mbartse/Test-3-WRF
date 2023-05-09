import xarray as xr
import pandas as pd
from wind import uv_to_spddir
def HRRR_data_process(t2m_cdf_path, uv_cdf_path, rh_cdf_path, date_generated):    
    # Cleaning the HRRR data up
    ds_t = xr.open_dataset(t2m_cdf_path)
    ds_uv = xr.open_dataset(uv_cdf_path)
    ds_rh = xr.open_dataset(rh_cdf_path)

    d1={'GLS':(-94.8604,29.2653),
     'HOU':(-95.2824,29.6375),
     'MCJ':(-95.395,29.714),
     'IAH':(-95.3607,29.9844),
     'DWH':(-95.5562,30.068),
     'CXO':(-95.4145,30.3524),
     'UTS':(-95.5872,30.7469)}

    l1=list(d1.values())
    l2=list(d1.keys())

    dsi_t = ds_t.herbie.nearest_points(l1, names=l2)
    dsi_uv = ds_uv.herbie.nearest_points(l1, names=l2)
    dsi_rh = ds_rh.herbie.nearest_points(l1, names=l2)
    # Kelvin to Fahrenheit
    dsi_t.t2m.data = 1.8*(dsi_t.t2m.data - 273.15) + 32

    da_t = xr.DataArray(dsi_t.t2m.data,[("station", list(dsi_t.point.data)),("date_time", list(dsi_t.valid_time.data))])
    da_u10 = xr.DataArray(dsi_uv.u10.data,[("station", list(dsi_t.point.data)),("date_time", list(dsi_t.valid_time.data))])
    da_v10 = xr.DataArray(dsi_uv.v10.data,[("station", list(dsi_t.point.data)),("date_time", list(dsi_t.valid_time.data))])
    da_rh = xr.DataArray(dsi_rh.r2.data,[("station", list(dsi_t.point.data)),("date_time", list(dsi_t.valid_time.data))])

    HRRR_temp_fil = da_t.sel(date_time=date_generated)
    HRRR_u10_fil = da_u10.sel(date_time=date_generated)
    HRRR_v10_fil = da_v10.sel(date_time=date_generated)
    HRRR_rh_fil = da_rh.sel(date_time=date_generated)

    df_HRRR_t=HRRR_temp_fil.to_dataframe(name='HRRR_temp')
    df_HRRR_u10=HRRR_u10_fil.to_dataframe(name='HRRR_u10')
    df_HRRR_v10=HRRR_v10_fil.to_dataframe(name='HRRR_v10')
    df_HRRR_rh=HRRR_rh_fil.to_dataframe(name='HRRR_rh')

    df_HRRR_t.reset_index(inplace=True)
    df_HRRR_u10.reset_index(inplace=True)
    df_HRRR_v10.reset_index(inplace=True)
    df_HRRR_rh.reset_index(inplace=True)

    d1=pd.merge(df_HRRR_rh, df_HRRR_t, on=['date_time','station'])
    d2=pd.merge(df_HRRR_u10, df_HRRR_v10, on=['date_time','station'])
    df_HRRR=pd.merge(d1, d2, on=['date_time','station'])

    x=uv_to_spddir(df_HRRR['HRRR_u10'],df_HRRR['HRRR_v10'])
    df_HRRR['HRRR_wspeed']=x[0]
    df_HRRR['HRRR_wdir']=x[1]
    df_HRRR.drop(['HRRR_u10','HRRR_v10'], axis=1, inplace=True)
    return df_HRRR