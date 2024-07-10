import pandas as pd
from pyorbital.orbital import Orbital
from datetime import datetime, timedelta

#This function reads the tle data from TLE.txt
def read_tle():
    with open('C:/Users/Administrator/satellites/pyorbital/TLEs.txt', 'r') as f:
        lines = f.readlines()
        
    #An empty dictionary to store the satellite details
    satellites = {}
    #Looping through the TLEs.txt grouping them to each satellite
    for i in range(0, len(lines), 3):
        line1 = lines[i].strip()
        line2 = lines[i+1].strip()
        satellite_id = line1.split()[1]
        satellites[satellite_id] = (line1, line2)
        #sat = Orbital(satellite_id, line1=tle[0], line2=tle[1])
        #print(sat)
    return satellites

#Using pyorbital get_observer_look function to get the azimuth and elevation of a target at a specific time. 
#The target is defined by latitude longitude and altitude.
def azel(sat, time, lat, lng):
    az, el = sat.get_observer_look(time, lat, lng,0)
    return az, el

#This function outputs the visibility of each satellite from a specific target
def calculate_visibility(satellites, targets):
    start_time = datetime(2024, 5, 1, 0, 0) # year, month, date, hour, minute
    end_time = start_time + timedelta(hours=24) #Tie range of a whole day
    time_steps = pd.date_range(start_time, end_time, freq='h')  # Hourly steps
    results = []
    #Interpreting each satellite's TLE to find observers look
    for satellite_id, tle in satellites.items():
        sat = Orbital(satellite_id, line1=tle[0], line2=tle[1])
        for time in time_steps:
            for index, target in targets.iterrows():
                az, el = azel(sat, time, target['lat'], target['lng'])
                if el > 10:  # Taking minimum elevation to be 10 degrees
                    results.append({
                        'Satellite': satellite_id,
                        'Time': time,
                        'City': target['city'],
                        'Latitude': target['lat'],
                        'Longitude': target['lng'],
                        'Azimuth': az,
                        'Elevation': el
                    })
    
    return pd.DataFrame(results)


satellites = read_tle()

targets = pd.read_csv('C:/Users/Administrator/satellites/pyorbital/targets.csv')

visibility_df = calculate_visibility(satellites, targets)


#Saving the results obtained
visibility = pd.DataFrame(visibility_df)

visibility.set_index('Time', inplace=True)
visibility.to_csv('results/satellite_visibility.csv')
visibility.head()

pass_times = pd.read_csv('results/satellite_visibility.csv')



grouped = pass_times.groupby('City')

# Grouping the results by city
for city, group in grouped:
    #print(f"City: {city}")
    group = pd.DataFrame(group)
    #print(group.head())

# Save the grouped data to a CSV file
for city, group in grouped:
    group.drop('City')
    group.to_csv(f'results/satellite_visibility_{city}.csv', index= False)



