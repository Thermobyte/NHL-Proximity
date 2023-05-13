# Data pulled from
# Canada data: https://simplemaps.com/data/canada-cities
# US data: https://simplemaps.com/data/us-cities

import csv
from math import radians, cos, sin, asin, sqrt
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def determine_distance(lat1, lon1, lat2, lon2):
    # Haversine formula
    # https://en.wikipedia.org/wiki/Haversine_formula
    # https://stackoverflow.com/questions/27928/calculate-distance-between-two-latitude-longitude-points-haversine-formula/21623206#21623206
    # convert decimal degrees to radians 

    # convert strings to floats
    lat1 = float(lat1)
    lon1 = float(lon1)
    lat2 = float(lat2)
    lon2 = float(lon2)

    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    
    # Radius of earth in kilometers is 6371
    c = 2 * asin(sqrt(a)) 
    km = 6371* c
    return km

# a master list will be passed in in the format of {team: [city, city, city, city]}
# a city will be passed in and it will find the closest team to that city using the determine_distance function
# when it finds the closest team it will add itself ot the list of cities associated with that team in the master list
# if the city is already in the list, it will not add it again
def evaluate_city(teams_list, city, master_list):
    logging.debug(f'evaluating {city["city_ascii"]}...')

    closest_distance = 0
    closest_team = ""

    for team in teams_list:
        if team["nhl_team"] not in master_list:
            master_list[team["nhl_team"]] = []
        # check if the city being checked has the same id as a team's city
        if city["id"] == team["id"]:
            # if it does, then add the city to the list of cities associated with that team
            master_list[team["nhl_team"]].append(city)
            logging.debug(f'added {city["city_ascii"]} to {team["nhl_team"]}')
            return True
        else:
            # if it doesn't, then calculate the distance between the city and the team's city
            distance = determine_distance(city["lat"], city["lng"], team["lat"], team["lng"])
            # if the distance is less than the closest distance, then set the closest distance to the current distance and set the closest team to the current team
            if distance < closest_distance or closest_distance == 0:
                closest_distance = distance
                closest_team = team["nhl_team"]
    
    # if the closest distance is 0, then something went wrong
    if closest_distance == 0:
        logging.error(f'closest distance is 0 for {city["city_ascii"]}, no team was found')
        return False
    
    # after all the teams have been checked, add the city to the list of cities associated with the closest team
    master_list[closest_team].append(city)
    logging.debug(f'added {city["city_ascii"]} to {closest_team}')
    return True


def add_populations(master_list):
    # for each team in the master list, add up the population of each city associated with that team
    # make a new list of teams with the total population of each team
    total_fans_list = []
    for team in master_list:
        total_population = 0
        for city in master_list[team]:
            total_population += (float)(city["population"])
        total_fans_list.append({"nhl_team": team, "total_population": total_population})
        logging.debug(f'{team} was appended to the list with a total population of {total_population}')
    
    # sort the list by total population
    total_fans_list.sort(key=lambda x: x["total_population"], reverse=True)
    return total_fans_list



# Main method will read in the list of cities that have NHL stadiums, and then determine the which stadium is closest to each Canadian and American city or town
# Once that is determined for each town, it will add the population of that town to the total for that team which it is closest to
# It will output a list of teams and the total population of towns whose closest NHL arena is that team's arena
def main():
    # teams_list will contain a list of all the teams, the city's id, and their total associated population
    # the team item in the csv file is called "nhl_team"
    teams_list = []
    # Read in the list of teams
    with open('nhl-stadiums.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            teams_list.append({"nhl_team": row['nhl_team'], "id": row['id'], "lat": row['lat'], "lng": row['lng'], "population": 0})
    
    # Canadian cities are in a CSV called canadacities.csv and US cities are in a CSV called uscities.csv
    # The names of the fields in the CSVs are the same, and are as follows:
    # city_ascii, lat, lng, population, id
    # If the id of a city being checked matches an arena city's id, then the population of that city will be added to the total population of the arena city
    # Read in every city in the US and Canada, their lat/long, and their population as a dictionary
    # The dictionary will be called cities_list
    cities_list = []
    with open('canadacities.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            logging.debug(f'appending {row["city_ascii"]}...')
            cities_list.append({"city_ascii": row['city_ascii'], "lat": row['lat'], "lng": row['lng'], "population": row['population'], "id": row['id']})
    with open('uscities.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            logging.debug(f'appending {row["city_ascii"]}...')
            cities_list.append({"city_ascii": row['city_ascii'], "lat": row['lat'], "lng": row['lng'], "population": row['population'], "id": row['id']})

    # master_list will contain a list of all the teams and the cities associated with them
    # the team item in the csv file is called "nhl_team"
    master_list = {}

    for city in cities_list:
        evaluate_city(teams_list, city, master_list)
    
    total_fans_list = add_populations(master_list)

    # print it nicely in a table
    for team in total_fans_list:
        print(f'{team["nhl_team"]}: {team["total_population"]}')
    
    


if __name__ == "__main__":
    main()