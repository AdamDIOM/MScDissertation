from lxml import etree
from pyproj import Transformer
from datetime import date, timedelta
from dateutil.easter import easter
import shutil
import os


XSLT_FOLDER = 'XSLT/'
OUTPUT_FOLDER = 'output/'
XML_FOLDER = 'XML/'

transformer = Transformer.from_crs("epsg:27700", "epsg:4326")

START_DATE = "20250101"
END_DATE = "20291231"

SCOTLAND = False

errors = []

def tx(xsl_file):
    data = []
    xslt = etree.parse(XSLT_FOLDER + xsl_file + '.xsl')
    transform = etree.XSLT(xslt)

    for file in os.listdir(XML_FOLDER):
        data.append(str(transform(etree.parse(f"{XML_FOLDER}{os.fsdecode(file)}"))))
    
    data_processed = [data[0]]
    for item in range(1, len(data)):
        i = str(data[item]).split('\n')
        del i[0]
        data_processed.append("\n".join(i))

    return '\n'.join(data_processed)

def output(output_file, out):
    with open(OUTPUT_FOLDER + output_file + '.txt', 'w') as f:
        f.write(str(out))

def pt_time_string_validation(time_string):
    nonbreaking_local_error = ""

    if len(time_string) < 4 or len(time_string) > 5:
        return False, "Time string invalid length"

    if time_string[0:2] != "PT":
        nonbreaking_local_error = "*Time string starts invalid"
        # non-breaking error so doesn't return
    period = time_string[-1]

    if period not in ['H', 'M', 'S']:
        return False, "Time period invalid"
    
    value = time_string[2:-1].zfill(2)

    if not value.isnumeric():
        return False, "Time value not numeric"
    elif int(value) > 59 or int(value) < 0:
        return False, "Time value out of bounds"

    return True, nonbreaking_local_error

def extract_time_string(pt_format):
    add_time = "00:00:00"
    local_error = ""
    valid, local_error = pt_time_string_validation(pt_format)

    if not valid:
        return add_time, local_error

    period = pt_format[-1]
    value = pt_format[2:-1].zfill(2)

    # handle second waits
    if(period == 'S'):
        add_time = add_time[0:6] + value
        #add_time[6:8] = value;
    # handle minute waits
    elif(period == 'M'):
        add_time = add_time[0:3] + value + add_time[5:]
        #add_time[3:5] = value
    # handle hour waits
    elif(period == 'H'):
        add_time = value + add_time[2:]
        #add_time[0:2] = value
    
    return add_time, local_error

def time_string_validation(time_string):
    nonbreaking_local_error = ""
    if len(time_string) != 8:
        return False, "Time string invalid length"

    if time_string[2] != ":" or time_string[5] != ":":
        nonbreaking_local_error = "Time string incorrect delimeter"
        
    if not (time_string[0:2].isnumeric() and time_string[3:5].isnumeric() and time_string[6:8].isnumeric()):
        return False, "Time value not numeric"
    
    if int(time_string[0:2]) > 72 or int(time_string[3:5]) > 59 or int(time_string[6:8]) > 59:
        return False, "Time value out of bounds"

    return True, nonbreaking_local_error

def add_time_string(initial_time, add_time):
    local_error = ""
    initial_valid, initial_error = time_string_validation(initial_time) 
    add_valid, add_error = time_string_validation(add_time)

    if initial_error != "":
        local_error = f"Initial Time: {initial_error}"
    if add_error != "":
        if local_error != "": local_error += "; "
        local_error += f"Journey Time: {add_error}"

    if not initial_valid:
        return "00:00:00", local_error
    if not add_valid:
        return initial_time, local_error
    
    
    overflow = 0
    s = int(initial_time[6:8]) + int(add_time[6:8])
    if(s > 59):
        overflow = 1
        s -= 60
    m = int(initial_time[3:5]) + int(add_time[3:5]) + overflow
    overflow = 0
    if(m > 59):
        overflow = 1
        m -= 60
    h = int(initial_time[0:2]) + int(add_time[0:2]) + overflow
    overflow = 0
    new_time = f'{str(h).zfill(2)}:{str(m).zfill(2)}:{str(s).zfill(2)}'
    return new_time, local_error

def validate_lat_lon(line):
    lat, lon = line.split(",")[-2], line.split(",")[-1]
    lat_error, lon_error = '', ''
    if lat == '':
        lat_error = "Latitude missing"
    if lon == '':
        lon_error = "Longitude missing"

    try:
        if not lat_error: l = float(lat)
    except:
        lat_error = "Latitude invalid format"
    try:
        if not lon_error: l = float(lon)
    except:
        lon_error = "Longitude invalid format"
    
    if not lat_error and (float(lat) > 54.5 or float(lat) < 54):
        lat_error = "*Latitude out of bounds"
        
    if not lon_error and (float(lon) > -4.3 or float(lon) < -4.85):
        lon_error = "*Longitude out of bounds"

    local_error = ''
    if lat_error and lon_error:
        local_error = f"{lat_error}, {lon_error}"
    elif lat_error:
        local_error = lat_error
    elif lon_error:
        local_error = lon_error

    if local_error != '':
        errors.append(f"Stop location error: {local_error}, {line}")
        return False
    return True

def process_stops(stops):
    stops_processed = []
    for line in stops.split("\n"):
        if line.startswith("stop_id, stop_name, stop_lat, stop_lon") or line == '':
            continue
        # this line stops duplicates based on the stop id
        match = next((item for item in stops_processed if item.startswith(line[0:12])), None)
        if match:
            if match[14] != '*':
                continue
            
        if "E*" in line and "N*" in line:
            #print(line)
            line_split = line.split("E*")
            easting = int(line_split[1])
            line_split = line.split("N*")
            northing = int(line_split[1])

            lat, lon = transformer.transform(easting, northing)

            line_split = line.split("E*")
            line_split[1] = str(lat)
            line = "".join(line_split)
            line_split = line.split("N*")
            line_split[1] = str(lon)
            line = "".join(line_split)

        if not validate_lat_lon(line) and not match:
            line = line[0:14] + '*' + line[14:]
        elif match:
            stops_processed.remove(match)
        stops_processed.append(line)
        
    return stops_processed

def process_stop_times(stop_times):
    # separate each line into items
    stop_times_split = str(stop_times).strip().split("\n")
    # split each line into its own list
    stop_times_lists = [x.split(",") for x in stop_times_split]

    list_length = len(stop_times_split)
    # loop through each item in list and append wait time to arrival time
    for list_item_index in range(1, list_length):
        # skip blanks between files
        if stop_times_split[list_item_index] == '':
            continue

    # if length > 5 ie has a departure time and a wait time (even if 0)
        if(len(stop_times_lists[list_item_index]) > 5):
            arr_time = stop_times_lists[list_item_index][3]
            # eliminate no wait first as it's most common

            if(stop_times_lists[list_item_index][4] == 'PT0S'):
                stop_times_lists[list_item_index][4] = arr_time
            
            else:
                # get the amount of time to add from format PTxy, where x is number and y is H/M/S
                add_time, at_error = extract_time_string(stop_times_lists[list_item_index][4])

                if at_error != "":
                    errors.append(f"Time format error: {at_error}, {stop_times_split[list_item_index]}")

                # add the new time onto the original time
                dep_time, ats_error = add_time_string(arr_time, add_time)

                if ats_error != "":
                    errors.append(f"Time addition erorr: {ats_error}, {stop_times_split[list_item_index]}, {add_time}")
                # write back to the list
                stop_times_lists[list_item_index][4] = dep_time


        # not last item of service and length > 5 ie has all values AND a time addition
        if(list_item_index < list_length - 1 and stop_times_lists[list_item_index][0] == stop_times_lists[list_item_index + 1][0] and len(stop_times_lists[list_item_index]) > 5):
            time_to_next_stop, ttns_error = extract_time_string(stop_times_lists[list_item_index][5])

            if ttns_error != "":
                errors.append(f"Time format error: {ttns_error}, {stop_times_split[list_item_index]}")

            stop_times_lists[list_item_index + 1][3], ats_error = add_time_string(stop_times_lists[list_item_index][4], time_to_next_stop)

            if ats_error != "":
                errors.append(f"Time addition erorr: {ats_error}, {stop_times_split[list_item_index]}, {time_to_next_stop}")

            stop_times_lists[list_item_index].pop()
        
        else:
            stop_times_lists[list_item_index][4] = stop_times_lists[list_item_index][3]
        # append wait time to arrival time

    stop_times_split = [','.join(item) for item in stop_times_lists]

    return stop_times_split

def decode_days(id, dow):
# create list that will eventually be output
    calendar_item = [id]
    # create list of days - all start as no service and service is added in
    days_list = ["0","0","0","0","0","0","0"]
    # for each child, add the respective days to days_list as service
    for days in dow:
        if days == "MondayToSunday":
            for i in range(0,7):
                days_list[i] = "1"
        elif days == "MondayToSaturday":
            for i in range(0,6):
                days_list[i] = "1"
        elif days == "Not Saturday":
            days_list[6] = "1"
            for i in range(0,5):
                days_list[i] = "1"
        elif days == "MondayToFriday":
            for i in range(0,5):
                days_list[i] = "1"
        elif days == "Weekend":
            days_list[5] = "1"
            days_list[6] = "1"
        elif days == "Monday":
            days_list[0] = "1"
        elif days == "Tuesday":
            days_list[1] = "1"
        elif days == "Wednesday":
            days_list[2] = "1"
        elif days == "Thursday":
            days_list[3] = "1"
        elif days == "Friday":
            days_list[4] = "1"
        elif days == "Saturday":
            days_list[5] = "1"
        elif days == "Sunday":
            days_list[6] = "1"
    
    # append the chosen days onto the id
    calendar_item.extend(days_list)
    # mock start and end date
    calendar_item.append(START_DATE)
    calendar_item.append(END_DATE)
    return calendar_item

def process_date_range(id, dates_list, exception_type):
    cdp = []
    for date_range in dates_list:
        s_date = date_range.split('-')[0]
        e_date = date_range.split('-')[1]
        if s_date == e_date:
            cdp.append(f"{id},{s_date},{exception_type}")
        else:
            start_date = date(int(s_date[0:4]), int(s_date[4:6]), int(s_date[6:8])) 
            end_date = date(int(e_date[0:4]), int(e_date[4:6]), int(e_date[6:8])) 
            change = end_date - start_date   # returns timedelta
            for i in range(change.days + 1):
                day = start_date + timedelta(days=i)
                cdp.append(f"{id},{day.strftime('%Y%m%d')},{exception_type}")
    return cdp

def get_dates(date):
    s_year = int(START_DATE[0:4])
    s_date = int(START_DATE[4:])
    e_year = int(END_DATE[0:4])
    e_date = int(END_DATE[4:])

    if s_date > date:
        s_year += 1
    if e_date < date:
        e_year -= 1
    
    dates = []
    for year in range(s_year, e_year + 1):
        dates.append(f"{year}{date}")

    return dates

# offset +1 for Easter Monday, -2 for Good Friday
def get_easter(offset=0):
    s_year = int(START_DATE[0:4])
    s_date = int(START_DATE[4:])
    e_year = int(END_DATE[0:4])
    e_date = int(END_DATE[4:])

    dates = []

    # if same year only calculate for that year
    if e_year == s_year:
        x_easter = (easter(s_year) + timedelta(days=offset)).strftime('%Y%m%d')
        if int(x_easter[4:]) >= s_date and int(x_easter[4:]) <= e_date:
            dates.append(x_easter)
    
    else:
        f_easter = (easter(s_year) + timedelta(days=offset)).strftime('%Y%m%d')
        if int(f_easter[4:]) >= s_date:
            dates.append(f_easter)

        if e_year - s_year > 1:
            for year in range(s_year + 1, e_year):
                dates.append((easter(year) + timedelta(days=offset)).strftime('%Y%m%d'))
        
        l_easter = (easter(e_year) + timedelta(days=offset)).strftime('%Y%m%d')
        if int(l_easter[4:]) <= e_date:
            dates.append(l_easter)

    return dates

def get_firstmonday(month):
    s_year = int(START_DATE[0:4])
    s_date = int(START_DATE[4:])
    e_year = int(END_DATE[0:4])
    e_date = int(END_DATE[4:])

    dates = []

    if e_year == s_year:
        x_d = date(e_year, month, 7)
        x_mayday = (x_d + timedelta(-x_d.weekday())).strftime('%Y%m%d')
        if int(x_mayday[4:]) >= s_date and int(x_mayday[4:]) <= e_date:
            dates.append(x_mayday)
    
    else:
        f_d = date(s_year, month, 7)
        f_mayday = (f_d + timedelta(-f_d.weekday())).strftime('%Y%m%d')
        if int(f_mayday[4:]) >= s_date:
            dates.append(f_mayday)

        if e_year - s_year > 1:
            for year in range(s_year + 1, e_year):
                d = date(year, month, 7)
                dates.append((d + timedelta(-d.weekday())).strftime('%Y%m%d'))
        
        l_d = date(e_year, month, 7)
        l_mayday = (l_d + timedelta(-l_d.weekday())).strftime('%Y%m%d')
        if int(l_mayday[4:]) <= e_date:
            dates.append(l_mayday)

    return dates

def get_lastmonday(month):
    s_year = int(START_DATE[0:4])
    s_date = int(START_DATE[4:])
    e_year = int(END_DATE[0:4])
    e_date = int(END_DATE[4:])

    dates = []

    if e_year == s_year:
        x_d = date(e_year, month, 31)
        x_mayday = (x_d + timedelta(-x_d.weekday())).strftime('%Y%m%d')
        if int(x_mayday[4:]) >= s_date and int(x_mayday[4:]) <= e_date:
            dates.append(x_mayday)
    
    else:
        f_d = date(s_year, month, 31)
        f_mayday = (f_d + timedelta(-f_d.weekday())).strftime('%Y%m%d')
        if int(f_mayday[4:]) >= s_date:
            dates.append(f_mayday)

        if e_year - s_year > 1:
            for year in range(s_year + 1, e_year):
                d = date(year, month, 31)
                dates.append((d + timedelta(-d.weekday())).strftime('%Y%m%d'))
        
        l_d = date(e_year, month, 31)
        l_mayday = (l_d + timedelta(-l_d.weekday())).strftime('%Y%m%d')
        if int(l_mayday[4:]) <= e_date:
            dates.append(l_mayday)

    return dates

# disp_day is christmas day as standard. wd1 is saturday, which displaces christmas bank hol to the 27th; wd2 is sunday, which displaces bank hol to the 26th.
def get_christmas_displacement(disp_day=25, wd=None, disp=None, month=12, disp_month=None):
    if wd == None: wd = [5,6]
    if disp == None: disp=[27,26]
    if disp_month == None: disp_month = month
    s_year = int(START_DATE[0:4])
    s_date = int(START_DATE[4:])
    e_year = int(END_DATE[0:4])
    e_date = int(END_DATE[4:])

    dates = []

    if e_year == s_year:
        x_christmas_day = date(e_year, month, disp_day) # 26
        x_displacement = ""
        for i in range(len(wd)):
            if x_christmas_day.weekday() == wd[i]:
                x_displacement = f"{e_year}{str(disp_month).zfill(2)}{str(disp[i]).zfill(2)}"
                break;
        
        if x_displacement != "" and int(x_displacement[4:]) >= s_date and int(x_displacement[4:]) <= e_date:
            dates.append(x_displacement)
    
    else:
        f_christmas_day = date(s_year, month, disp_day)
        f_displacement = ""

        for i in range(len(wd)):
            if f_christmas_day.weekday() == wd[i]:
                f_displacement = f"{s_year}{str(disp_month).zfill(2)}{str(disp[i]).zfill(2)}"
                break;
        
        if f_displacement != "" and int(f_displacement[4:]) >= s_date:
            dates.append(f_displacement)


        if e_year - s_year > 1:
            for year in range(s_year + 1, e_year):
                christmas_day = date(year, month, disp_day)
                displacement = ""
                for i in range(len(wd)):
                    if christmas_day.weekday() == wd[i]:
                        displacement = f"{year}{str(disp_month).zfill(2)}{str(disp[i]).zfill(2)}"
                        break;
                if displacement != "":
                    dates.append(displacement)

        l_christmas_day = date(e_year, month, disp_day)
        l_displacement = ""
        for i in range(len(wd)):
            if l_christmas_day.weekday() == wd[i]:
                l_displacement = f"{e_year}{str(disp_month).zfill(2)}{str(disp[i]).zfill(2)}"
                break;
        
        if l_displacement != "" and int(l_displacement[4:]) <= e_date:
            dates.append(l_displacement)

    return dates

def process_holiday(id, holiday, exception_type):
    
    holiday_dates = []

    for day in holiday:
        if str(day).isnumeric():
            holiday_dates.append(day)
            # print(f"{id},{day},{exception_type}")
        else:

            # print(day, end=' ')
            if str(day) == "NewYearsDay":
                holiday_dates.extend(get_dates(101))
            elif str(day) == "Jan2ndScotland":
                holiday_dates.extend(get_dates(102))
            elif str(day) == "GoodFriday":
                holiday_dates.extend(get_easter(-2))
            elif str(day) == "StAndrewsDay":
                holiday_dates.extend(get_dates(1130))

            elif str(day) == "Holidays":
                holiday_dates.extend(get_dates(101))
                if SCOTLAND: holiday_dates.extend(get_dates(102))
                holiday_dates.extend(get_easter(-2))
                if SCOTLAND: holiday_dates.extend(get_dates(1130))

            elif str(day) == "ChristmasDay":
                holiday_dates.extend(get_dates(1225))
            elif str(day) == "BoxingDay":
                holiday_dates.extend(get_dates(1226))

            elif str(day) == "Christmas":
                holiday_dates.extend(get_dates(1225))
                holiday_dates.extend(get_dates(1226))
            
            elif str(day) == "EasterMonday":
                holiday_dates.extend(get_easter(1))

            elif str(day) == "MayDay":
                holiday_dates.extend(get_firstmonday(5))
            elif str(day) == "SpringBank":
                holiday_dates.extend(get_lastmonday(5))
            elif str(day) == "LateSummerBankHolidayNotScotland":
                holiday_dates.extend(get_lastmonday(8))
            elif str(day) == "AugustBankHolidayScotland":
                holiday_dates.extend(get_firstmonday(8))

            elif str(day) == "HolidayMondays":
                holiday_dates.extend(get_easter(1))
                holiday_dates.extend(get_firstmonday(5))
                holiday_dates.extend(get_lastmonday(5))
                if not SCOTLAND: holiday_dates.extend(get_lastmonday(8))
                if SCOTLAND: holiday_dates.extend(get_firstmonday(8))

            elif str(day) == "ChristmasDayHoliday":
                # if christmas day is a saturday, award the momday; if christmas is a sunday, award the tuesday
                holiday_dates.extend(get_christmas_displacement())
            elif str(day) == "BoxingDayHoliday":
                holiday_dates.extend(get_christmas_displacement(26, [5, 6, 0], [28, 28, 27]))
            elif str(day) == "NewYearsDayHoliday":
                holiday_dates.extend(get_christmas_displacement(1, [5, 6], [3, 2], 1))
            elif str(day) == "Jan2ndScotlandHoliday":
                holiday_dates.extend(get_christmas_displacement(2, [5, 6, 0], [4, 4, 3], 1))
            elif str(day) == "StAndrewsDayHoliday":
                holiday_dates.extend(get_christmas_displacement(30, [6], [1], 11, 12))

            elif str(day) == "DisplacementHolidays":
                holiday_dates.extend(get_christmas_displacement())
                holiday_dates.extend(get_christmas_displacement(26, [5, 6, 0], [28, 28, 27]))
                holiday_dates.extend(get_christmas_displacement(1, [5, 6], [3, 2]), 1)
                if SCOTLAND: holiday_dates.extend(get_christmas_displacement(2, [5, 6, 0], [4, 4, 3], 1))
                if SCOTLAND: holiday_dates.extend(get_christmas_displacement(30, [6], [1], 11, 12))

            elif str(day) == "ChristmasEve":
                holiday_dates.extend(get_dates(1224))
            elif str(day) == "NewYearsEve":
                holiday_dates.extend(get_dates(1231))
        
    
    holiday_dates_processed = [f"{id},{day},{exception_type}" for day in holiday_dates]

    return holiday_dates_processed         

def process_calendar(calendar):

    # get heading from xsl
    calendar_processed = [str(calendar).strip().split('\n')[0]]

    calendar_dates_processed = ["service_id,date,exception_type"]

    # loop through every service (ie each line of calendar)
    for item in str(calendar).strip().split('\n')[1:]:
        # split it by commas
        item_list = item.strip(',').split(',')
        item_list.append("END")

        #print(item_list)
        id = item_list[0]
        del item_list[0]
        # if list has Days of Week
        if item_list[0][0:3] == "DOW":
            calendar_item = decode_days(id, item_list[0][4:].split(';'))
            # remove DOW so that the next operation is first
            del item_list[0]
            # add calendar_item to the calendar file – this is the only day op that fits calendar.txt
            calendar_processed.append(','.join(calendar_item))
        #print(item_list)
        if item_list[0][0:6] == "SDO-OP":
            dates_list = item_list[0][7:].split(';')
            calendar_dates_processed.extend(process_date_range(id, dates_list, "1"))

            del item_list[0]

        if item_list[0][0:6] == "SDO-NO":
            dates_list = item_list[0][7:].split(';')
            calendar_dates_processed.extend(process_date_range(id, dates_list, "2"))

            del item_list[0]

        #print(item_list[0])
        if item_list[0][0:6] == "BHO-OP":
            holidays_list = item_list[0][7:].split(';')
            # print("------OP------")
            calendar_dates_processed.extend(process_holiday(id, holidays_list, "1"))
            #print(item_list[0])
            #print(holidays_list)

            del item_list[0]

        if item_list[0][0:6] == "BHO-NO":
            holidays_list = item_list[0][7:].split(';')
            # print("------NO------")
            calendar_dates_processed.extend(process_holiday(id, holidays_list, "2"))
            #print(item_list[0])            

            del item_list[0]
    return calendar_processed, calendar_dates_processed    

def process_agencies(agency):
    agency_split = agency.split('\n')
    headers = [agency_split[0]]
    del agency_split[0]

    unique = [x for x in list(set(agency_split)) if x]
    headers.extend(unique)
    return "\n".join(headers)

def convert():


    agency = tx('agency')

    agency_processed = process_agencies(agency)

    output('agency', agency_processed)
    output('routes', tx('routes'))
    output('trips', tx('trips'))

    stops = str(tx('stops'))
    # process stops to remove easting/northings
    stops_processed = "\n".join(process_stops(stops))

    output('stops', stops_processed)

    stop_times = tx('stop_times')

    stop_times_processed = '\n'.join(process_stop_times(stop_times))

    output('stop_times', stop_times_processed)

    calendar = tx('calendar')

    calendar_processed, calendar_dates_processed = process_calendar(calendar)
    calendar_processed = "\n".join(calendar_processed)
    calendar_dates_processed = "\n".join(calendar_dates_processed)

    output('calendar', calendar_processed)
    output('calendar_dates', calendar_dates_processed)

    feed_info = '\n'.join([
        "feed_publisher_name,feed_publisher_url,feed_lang,feed_start_date,feed_end_date,feed_version,feed_contact_email",
        f"Bus Vannin,https://bus.im,en-GB,{START_DATE},{END_DATE},{date.today().strftime('%Y%m%d')},publictransport@gov.im"
    ])

    output('feed_info', feed_info)

    shutil.make_archive("output", 'zip', "output")

convert()

if errors:
    print("Errors detected in data:")
for error in errors:
    print("\t" + error)