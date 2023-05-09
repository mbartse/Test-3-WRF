import pandas as pd
from herbie.archive import Herbie
from herbie import FastHerbie
import datetime
from glob import glob
import os
def HRRR_download(date_generated, hour, startf, endf, grib_dir = '/home/michael.bartsevich/SynopticPy/notebooks/2022_Obs_WRF/HRRR_grib'):
    DATES = pd.date_range(start=datetime.datetime(date_generated[0].year, date_generated[0].month, date_generated[0].day, hour, 0), periods=1, freq="6H")
    fxx = range(48)
    FH = FastHerbie(DATES, model="hrrr", fxx=fxx ,  max_threads = 16, verbose = "True")
    test_path = grib_dir + '/hrrr/{}/'.format(startf.isoformat()[0:4]+startf.isoformat()[5:7]+startf.isoformat()[8:10])

    print('Temp (HRRR) download began')
    FH.download("TMP:2 m", save_dir = grib_dir, max_threads = 16, verbose = "True")
    zero_files = [aa for aa in sorted(glob(test_path+'subset*')) if os.stat(aa).st_size == 0]
    if zero_files:
        FH.download("TMP:2 m", save_dir = grib_dir, max_threads = 16, verbose = "True")
    else:
        pass
    ds = FH.xarray("TMP:2 m")
    t2m_cdf_path = "/home/michael.bartsevich/SynopticPy/notebooks/2022_Obs_WRF/HRRR_NC/HRRR_{}_{}_T2m.nc".format(startf.isoformat()[5:7]+startf.isoformat()[8:10],endf.isoformat()[5:7]+endf.isoformat()[8:10])
    ds.to_netcdf(t2m_cdf_path)
    print('Temp (HRRR) download finished')

    print('UV (HRRR) download began')
    FH.download("(?:U|V)GRD:10 m", save_dir = grib_dir, max_threads = 16, verbose = "True")
    zero_files = [aa for aa in sorted(glob(test_path+'subset*')) if os.stat(aa).st_size == 0]
    if zero_files:
        FH.download("(?:U|V)GRD:10 m", save_dir = grib_dir, max_threads = 16, verbose = "True")
    else:
        pass
    ds = FH.xarray("(?:U|V)GRD:10 m",max_threads = 16)
    uv_cdf_path = "/home/michael.bartsevich/SynopticPy/notebooks/2022_Obs_WRF/HRRR_NC/HRRR_{}_{}_UV10.nc".format(startf.isoformat()[5:7]+startf.isoformat()[8:10],endf.isoformat()[5:7]+endf.isoformat()[8:10])
    ds.to_netcdf(uv_cdf_path)
    print('UV (HRRR) download finished')

    print('UV (HRRR) download began')
    FH.download("RH:2 m", save_dir = grib_dir, max_threads = 16, verbose = "True")
    zero_files = [aa for aa in sorted(glob(test_path+'subset*')) if os.stat(aa).st_size == 0]
    if zero_files:
        FH.download("RH:2 m", save_dir = grib_dir, max_threads = 16, verbose = "True")
    else:
        pass
    ds = FH.xarray("RH:2 m",max_threads = 16,)
    rh_cdf_path = "/home/michael.bartsevich/SynopticPy/notebooks/2022_Obs_WRF/HRRR_NC/HRRR_{}_{}_RH2m.nc".format(startf.isoformat()[5:7]+startf.isoformat()[8:10],endf.isoformat()[5:7]+endf.isoformat()[8:10])
    ds.to_netcdf(rh_cdf_path)
    print('RH (HRRR) download finished')
    return t2m_cdf_path, uv_cdf_path, rh_cdf_path