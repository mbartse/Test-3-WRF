import datetime
from glob import glob
from netCDF4 import Dataset,MFDataset
from wrf import (to_np, getvar, smooth2d, get_cartopy,vertcross, cartopy_xlim, 
    cartopy_ylim, latlon_coords, ALL_TIMES, uvmet, interplevel, CoordPair, interpline, 
    ll_to_xy, xy_to_ll, extract_global_attrs,extract_times)
import numpy as np
from wrf.g_rh import get_rh, get_rh_2m
from datetime import timedelta
def WRF_init(date, path="/home/hgamarro/data_hgamarro/Houston_WRF/automate/output_prev/{}/{}/{}/"):
    startf = date[0]
    endf = date[1]
    print(startf, 'initialized')
    base_path = path.format(startf.isoformat()[0:4],startf.isoformat()[5:7],startf.isoformat()[8:10])
    Case_A_path = base_path 
    files_Case_A = sorted(glob(Case_A_path+'/wrfout_d02**'))
    files_Case_A_dataset=[Dataset(item) for item in files_Case_A]

    Land_mask = getvar(files_Case_A_dataset, 'LU_INDEX', timeidx=ALL_TIMES, method="cat")
    temp = Land_mask [15] .data
    temp[temp == 17] =np.nan 
    temp[temp > 0] = 1

    lats, lons = latlon_coords(Land_mask)
    cart_proj = get_cartopy(Land_mask)

    t2_Case_A = getvar(files_Case_A_dataset, 'T2', timeidx=ALL_TIMES, method="cat")
    temp_t2_Case_A = (t2_Case_A - 273.15) * (9.0/5.0) + 32.0
    rh2_Case_A = getvar(files_Case_A_dataset, 'rh2', timeidx=ALL_TIMES, method="cat")
    uvmet10_Case_A = getvar(files_Case_A_dataset, "uvmet10", units="kts", timeidx=ALL_TIMES, method="cat")
    wspd_wdir10_Case_A = getvar(files_Case_A_dataset, "uvmet10_wspd_wdir", units="kts", timeidx=ALL_TIMES, method="cat")
    rh_Case_A = get_rh_2m(files_Case_A_dataset,timeidx=ALL_TIMES, method="cat")

    time_list_temp = [x / 1e9 for x in Land_mask['Time'][:].values.tolist()]
    timelist = [datetime.datetime.utcfromtimestamp(element) for element in time_list_temp]
    start =datetime.datetime.utcfromtimestamp(time_list_temp[0])
    end = datetime.datetime.utcfromtimestamp(time_list_temp[-1])
    duration = end - start                         # For build-in functions
    duration_in_s = duration.total_seconds()  
    hours_span = divmod(duration_in_s, 3600)[0] 
    date_generated = [start + timedelta(hours=x) for x in range(0, int(hours_span))]
    init_check = sorted(glob(Case_A_path+'/hrrr.t06z**'))
    return temp_t2_Case_A, rh2_Case_A, uvmet10_Case_A, wspd_wdir10_Case_A, date_generated, init_check, files_Case_A_dataset, Land_mask
