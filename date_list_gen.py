import datetime
def date_list_gen(f_date,l_date):
    date_list = []
    while f_date != l_date:
        x = (f_date,f_date+datetime.timedelta(days=2))
        date_list.append(x)
        f_date = f_date + datetime.timedelta(days=1)  
    return date_list