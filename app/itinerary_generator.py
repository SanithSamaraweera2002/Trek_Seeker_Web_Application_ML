import heapq
import pandas as pd
import random
from datetime import datetime, timedelta

df = pd.read_excel('app\data\destinations_data.xlsx')


# mock_output = [
#     'Pedro Tea Estate','Hortan Plains National Park', 'Victoria Park - Nuwaraeliya',
#     'Hakgala Botanical Garden', 'Nuwara Eliya Golf Club', 'Ambewela Farm',
# ]

# Convert Excel data to dictionary for quick lookup
destination_data = df.set_index('Name').to_dict('index')
cities = df[['Name', 'City']].drop_duplicates().set_index('Name')['City'].to_dict()
time_spent = df.set_index('Name')['Time_Spent'].to_dict()

def filter_destinations_by_city(destinations, city, city_mapping):
    return [dest for dest in destinations if city_mapping.get(dest) == city]

# data = {
#     'Destination Name': [
#         'Hortan Plains National Park', 'Lake Gregory', 'Victoria Park - Nuwaraeliya', 'Hakgala Botanical Garden',
#         'Moon Plains', 'Single Tree Hill', 'Pedro Tea Estate', 'Lover\'s Leap Waterfall',
#         'Ravan Ella Waterfall', 'Pidurutalagala', 'Ambewela Farm', 'Seetha Amman Kovil',
#         'Galway\'s Land National Park', 'Nuwara Eliya Golf Club', 'Nanu Oya Water Falls, Nanu Oya'
#     ],
#     'Hortan Plains National Park': [0, 60, 62, 65, 65, 64, 62, 66, 84, 78, 36, 64, 63, 63, 65],
#     'Lake Gregory': [60, 0, 6, 15, 11, 12, 4, 12, 57, 24, 45, 12, 7, 8, 23],
#     'Victoria Park - Nuwaraeliya': [62, 6, 0, 17, 16, 10, 7, 10, 58, 22, 8, 15, 6, 2, 20],
#     'Hakgala Botanical Garden': [65, 15, 17, 0, 19, 24, 16, 24, 45, 36, 10, 3, 19, 21, 32],
#     'Moon Plains': [65, 11, 16, 19, 0, 22, 14, 19, 61, 34, 9, 17, 13, 19, 30],
#     'Single Tree Hill': [64, 12, 10, 24, 22, 0, 12, 19, 64, 30, 43, 19, 13, 12, 10],
#     'Pedro Tea Estate': [62, 4, 7, 16, 14, 12, 0, 13, 58, 25, 7, 14, 8, 9, 20],
#     'Lover\'s Leap Waterfall': [66, 12, 10, 24, 19, 19, 13, 0, 66, 22, 50, 24, 9, 11, 25],
#     'Ravan Ella Waterfall': [84, 57, 58, 45, 61, 64, 58, 66, 0, 66, 43, 34, 55, 51, 62],
#     'Pidurutalagala': [78, 24, 22, 36, 34, 30, 25, 22, 66, 0, 58, 37, 23, 24, 37],
#     'Ambewela Farm': [36, 45, 8, 10, 9, 43, 7, 50, 43, 58, 0, 46, 46, 45, 49],
#     'Seetha Amman Kovil': [64, 12, 15, 3, 17, 19, 14, 24, 34, 37, 46, 0, 16, 18, 29],
#     'Galway\'s Land National Park': [63, 7, 6, 19, 13, 13, 8, 9, 55, 23, 46, 16, 0, 7, 23],
#     'Nuwara Eliya Golf Club': [63, 8, 2, 21, 19, 12, 9, 11, 51, 24, 45, 18, 7, 0, 22],
#     'Nanu Oya Water Falls, Nanu Oya': [65, 23, 20, 32, 30, 10, 20, 25, 62, 37, 49, 29, 23, 22, 0]
# }

# # DataFrame
# distance_matrix = pd.DataFrame(data)
# distance_matrix.set_index('Destination Name', inplace=True)

def load_distance_matrix(city):
    # Map city to corresponding Excel file
    city_files = {
        'Colombo': 'app/data/Colombo_dt.xlsx',
        'Nuwara Eliya': 'app/data/Nuwara_Eliya_dt.xlsx',
        'Kandy': 'app/data/Kandy_dt.xlsx',
        'Galle': 'app/data/Galle_dt.xlsx'
    }

    file_path = city_files.get(city)
    if not file_path:
        raise ValueError(f"No data available for city: {city}")

    # Load the Excel file into a DataFrame
    df = pd.read_excel(file_path)

    # Assuming the first column is the index and the rest are distances
    distance_matrix = df.set_index('Destination Name')

    # distance_matrix.to_excel('verifymatrix.xlsx')
    return distance_matrix

# Visit time for destinations
# visit_times = {
#     'Hortan Plains National Park': 180,
#     'Lake Gregory': 60,
#     'Victoria Park - Nuwaraeliya': 90,
#     'Hakgala Botanical Garden': 120,
#     'Moon Plains': 90,
#     'Pedro Tea Estate': 60,
#     'Nuwara Eliya Golf Club': 90,
#     'Ambewela Farm': 120
# }

def dijkstra(distance_matrix, start, filtered_destinations):
    destinations = distance_matrix.columns
    distances = {destination: float('inf') for destination in destinations}
    # print("dist", distances)
    distances[start] = 0
    priority_queue = [(0, start)]

    while priority_queue:
        current_distance, current_destination = heapq.heappop(priority_queue)

        if current_distance > distances[current_destination]:
            continue

        for neighbor in destinations:
            if neighbor == current_destination or neighbor not in filtered_destinations:
                continue

            travel_time = distance_matrix.at[current_destination, neighbor]
            new_distance = current_distance + travel_time

            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                heapq.heappush(priority_queue, (new_distance, neighbor))

    return distances

def create_itinerary(filtered_destinations, distance_matrix, start, visit_times, day_duration=600):
    itinerary = []
    total_time = 0

    current_start = start

    print("filtered_destinations",filtered_destinations)
    print("visit_times",visit_times)

    for _ in range(len(filtered_destinations)):
        if total_time >= day_duration:
            break

        # Dijkstra's algorithm
        distances = dijkstra(distance_matrix, current_start, filtered_destinations)
        
        # Sort by asc travel time
        sorted_destinations = sorted(distances.items(), key=lambda x: x[1])
        
        # Get nearest destination
        top_destination = None
        travel_time = None
        
        for destination, time in sorted_destinations:
            if destination not in [dest for dest, _, _ in itinerary] and destination in visit_times:
                top_destination = destination
                travel_time = time
                print(f"Top destination: {top_destination}, Travel time: {travel_time}")
                break

        if top_destination is None:
            break

        visit_time = visit_times[top_destination]
        
        if total_time + travel_time + visit_time > day_duration:
            break

        # Add top destination to the itinerary
        itinerary.append((top_destination, travel_time, visit_time))
        total_time += travel_time + visit_time

        # Update current point
        current_start = top_destination

    return itinerary


def create_multi_day_itinerary(filtered_destinations, distance_matrix, start, visit_times, days, day_duration=600):
    total_itinerary = []
    day_start_time = datetime.strptime('08:00 AM', '%I:%M %p')

    remaining_destinations = visit_times.keys()
    last_destination = start
    leftover_destinations = [] 

    for day in range(1, days + 1):
        # Current day itinerary create
        itinerary = create_itinerary(filtered_destinations, distance_matrix, last_destination, visit_times, day_duration)

        print(f"Day {day} Itinerary: {itinerary}")

        if not itinerary:
            break

        day_itinerary = []
        current_time = day_start_time

        for order, (destination, travel_time, visit_time) in enumerate(itinerary[:4], start=1):
            travel_time = int(travel_time)
            visit_time = int(visit_time)

            if order == 1:
                travel_time = 0

            time_from = current_time + timedelta(minutes=travel_time)
            time_to = time_from + timedelta(minutes=visit_time)
            
            day_itinerary.append({
                "dayNumber": day,
                "destination": destination,
                "destinationOrder": order,
                "timeFrom": time_from.strftime('%I:%M %p'),
                "timeTo": time_to.strftime('%I:%M %p'),
                "visitTime": visit_time,
                "travel_time": travel_time
            })

            current_time = time_to 
        
        total_itinerary.append({
            "DayNumber": day,
            "destinations": day_itinerary
        })

        # Store destinations not used 
        leftover_destinations = itinerary[4:] 

        # Starting point for next day
        last_destination = leftover_destinations[0][0] if leftover_destinations else itinerary[-1][0]

         # Destinations of todays itinerary 
        visited_today = [destination for destination, _, _ in itinerary[:4]]

        # Remove destinations included in todays itinerary from visit time
        visit_times = {key: val for key, val in visit_times.items() if key not in visited_today}

        #  Remove destinations included in todays itinerary from filtered_destinations
        filtered_destinations = [dest for dest in filtered_destinations if dest not in visited_today]

        # CHECK LATER
        # if not visit_times:
        #     break

    return total_itinerary

# itinerary = create_multi_day_itinerary(distance_matrix, 'Ambewela Farm', visit_times, days=2)

# # Itinerary print
# for day, day_itinerary in itinerary.items():
#     print(f"\n{day}:")
#     for destination, travel_time, visit_time in day_itinerary:
#         print(f"Visit {destination}, Travel Time: {travel_time} mins, Visit Time: {visit_time} mins")

def generate_itinerary(recommendations, city, duration):
    # Convert to list
    recommendations_list = [rec['Name'] for rec in recommendations] if isinstance(recommendations, pd.DataFrame) else recommendations

    filtered_destinations = filter_destinations_by_city(recommendations_list, city, cities)

    # Visits time dict
    visit_times = {dest: time_spent.get(dest, 0) for dest in filtered_destinations}
    
    # matrix for selected city
    distance_matrix = load_distance_matrix(city)

    # Start
    # start_point = 'Ambewela Farm'
    start_point = random.choice(filtered_destinations)

    days = int(duration)
    
    # Generate itinerary based on recommendations
    itinerary = create_multi_day_itinerary(filtered_destinations, distance_matrix, start_point, visit_times, days=days)
    
    # Return the formatted itinerary
    # return {
    #     "trip_name": "My Custom Trip",
    #     "destinations": itinerary
    # }

    return itinerary
