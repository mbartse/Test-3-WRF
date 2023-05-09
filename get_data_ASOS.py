import datetime
from datetime import timedelta
import pandas as pd
import time
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen
def get_data_ASOS(startf,endf):    
    
    ####### ASOS ######## ---------------------------------------------------------------------------------------------------------------------------------------------------------
    MAX_ATTEMPTS = 6
    # HTTPS here can be problematic for installs that don't have Lets Encrypt CA
    SERVICE = "http://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?"

    # Specify your stations here. These are the 31 nearest stations to Houston
    stations = ['UTS','11R','CXO','6R3','DWH','IAH','BYY','LBX','GLS','ARM','AXH','LVJ','EFD','HOU','ELA','66R','SGR','MCJ',
               'TME','T78','BMT','BPT','RPE','ORG','CRH','GVX','BQX','PSX','CLL','CFD','3T5']
    
    stations = ['GLS','HOU','MCJ','IAH','DWH','CXO','UTS']
    # stations = ['HOU','ELA','GLS']

    # timestamps in UTC to request data for

    #                          year mon day hour min
    startts = startf
    endts = endf + datetime.timedelta(days=1)

    def download_data(uri):
        attempt = 0
        while attempt < MAX_ATTEMPTS:
            try:
                data = urlopen(uri, timeout=300).read().decode("utf-8")
                if data is not None and not data.startswith("ERROR"):
                    return data
            except Exception as exp:
                print("download_data(%s) failed with %s" % (uri, exp))
                time.sleep(5)
            attempt += 1

        print("Exhausted attempts to download, returning empty data")
        return ""

    """Our main method"""
    # timestamps in UTC to request data for
    #service = SERVICE + "data=all&tz=Etc/UTC&format=comma&latlon=yes&"
    service = SERVICE + "data=sknt&data=p01i&data=alti&data=feel&data=drct&data=relh&data=dwpf&data=tmpf&tz=Etc/UTC&format=onlycomma&latlon=yes&"

    service += startts.strftime("year1=%Y&month1=%m&day1=%d&hour1=%H&minute1=%M&")
    service += endts.strftime("year2=%Y&month2=%m&day2=%d&hour2=%H&minute2=%M&")
    #'michael.bartsevich/SynopticPy/notebooks/ASOS_Auto/CSVs'
    # Two examples of how to specify a list of stations
    #stations = get_stations_from_networks()

    #stations = ['HOU']
    # stations = get_stations_from_filelist("mystations.txt")
    for station in stations:
        uri = "%s&station=%s" % (service, station)
        print("Downloading: %s" % (station,))
        data = download_data(uri)
        outfn = "/home/michael.bartsevich/SynopticPy/notebooks/2022_Obs_WRF/ASOS_CSVs/%s.csv" % (station)
        out = open(outfn, "w")
        out.write(data)
        out.close()

    print('Download finished')


        # main()
    # Creates a dictionary of dataframes from all the .csv files we just downloaded
    station_wx_dict = {}
    zero_list = []
    for i in stations:
        i_wx = pd.read_csv("/home/michael.bartsevich/SynopticPy/notebooks/2022_Obs_WRF/ASOS_CSVs/%s.csv" % i, 
            parse_dates=['valid'],
            dtype= {'station' : 'category',
                   '  tmpf ': 'category',
                   '  dwpf ': 'category',
                   '  sknt ': 'category',
                   '  relh ': 'category',
                   '  drct ': 'category',
                   '  p01i ': 'category',
                   '  alti ': 'category',
                   '  feel ': 'category',
                   '  lon  ': 'category',
                   '  lat  ': 'category'}
            ).rename(columns=lambda x: x.strip())
        station_wx_dict[i] = i_wx
        if len(i_wx) == 0:
            zero_list.append(i)
    if zero_list != []:
        print('DISCLAIMER:\n\nThe following stations have no data\nmost likely because they didnt exist\nduring the given time range:\n\n',zero_list)

    df_list = []
    # Set the date as the index
    for i in stations:
        df = station_wx_dict[i]
        df['valid'] = pd.to_datetime(df['valid'])
        df = df.set_index('valid')
    # Creates a list of dataframes
        df_list.append(df)
    # Combines all the dataframes into one and sorts by date
    df_all = pd.concat(df_list)
    df_all = df_all.sort_values(by="valid")

    # Now we have a dataframe of all the stations and their data over that given time range

    df_all.rename(columns={'station': 'Station', 'lon': 'long','sknt':'Wind Speed','drct':'Resultant Wind Direction','tmpf':'Outdoor Temperature','relh':'Relative Humidity'},
                  inplace=True)
    df_all.drop(['p01i', 'alti','feel','dwpf'], axis=1, inplace=True)
    cols=['Station','lat','long','Outdoor Temperature','Resultant Wind Direction','Wind Speed','Relative Humidity']
    df_all = df_all[cols]
    df_all['source']='ASOS'
    df_asos=df_all
    df_asos.index.names = ['DATETIME']
    
    return df_asos, stations

# Outdoor Temperature	 = Fahrenheit
# Relative Humidity = percent
# Wind Speed	 = Knots
# Resultant Wind Direction  = degree