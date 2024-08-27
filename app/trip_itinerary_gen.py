import heapq
import pandas as pd

mock_output = [
    'Pedro Tea Estate','Hortan Plains National Park', 'Victoria Park - Nuwaraeliya',
    'Hakgala Botanical Garden', 'Nuwara Eliya Golf Club', 'Ambewela Farm',
]

data = {
    'Destination Name': [
        'Hortan Plains National Park', 'Lake Gregory', 'Victoria Park - Nuwaraeliya', 'Hakgala Botanical Garden',
        'Moon Plains', 'Single Tree Hill', 'Pedro Tea Estate', 'Lover\'s Leap Waterfall',
        'Ravan Ella Waterfall', 'Pidurutalagala', 'Ambewela Farm', 'Seetha Amman Kovil',
        'Galway\'s Land National Park', 'Nuwara Eliya Golf Club', 'Nanu Oya Water Falls, Nanu Oya'
    ],
    'Hortan Plains National Park': [0, 60, 62, 65, 65, 64, 62, 66, 84, 78, 36, 64, 63, 63, 65],
    'Lake Gregory': [60, 0, 6, 15, 11, 12, 4, 12, 57, 24, 45, 12, 7, 8, 23],
    'Victoria Park - Nuwaraeliya': [62, 6, 0, 17, 16, 10, 7, 10, 58, 22, 8, 15, 6, 2, 20],
    'Hakgala Botanical Garden': [65, 15, 17, 0, 19, 24, 16, 24, 45, 36, 10, 3, 19, 21, 32],
    'Moon Plains': [65, 11, 16, 19, 0, 22, 14, 19, 61, 34, 9, 17, 13, 19, 30],
    'Single Tree Hill': [64, 12, 10, 24, 22, 0, 12, 19, 64, 30, 43, 19, 13, 12, 10],
    'Pedro Tea Estate': [62, 4, 7, 16, 14, 12, 0, 13, 58, 25, 7, 14, 8, 9, 20],
    'Lover\'s Leap Waterfall': [66, 12, 10, 24, 19, 19, 13, 0, 66, 22, 50, 24, 9, 11, 25],
    'Ravan Ella Waterfall': [84, 57, 58, 45, 61, 64, 58, 66, 0, 66, 43, 34, 55, 51, 62],
    'Pidurutalagala': [78, 24, 22, 36, 34, 30, 25, 22, 66, 0, 58, 37, 23, 24, 37],
    'Ambewela Farm': [36, 45, 8, 10, 9, 43, 7, 50, 43, 58, 0, 46, 46, 45, 49],
    'Seetha Amman Kovil': [64, 12, 15, 3, 17, 19, 14, 24, 34, 37, 46, 0, 16, 18, 29],
    'Galway\'s Land National Park': [63, 7, 6, 19, 13, 13, 8, 9, 55, 23, 46, 16, 0, 7, 23],
    'Nuwara Eliya Golf Club': [63, 8, 2, 21, 19, 12, 9, 11, 51, 24, 45, 18, 7, 0, 22],
    'Nanu Oya Water Falls, Nanu Oya': [65, 23, 20, 32, 30, 10, 20, 25, 62, 37, 49, 29, 23, 22, 0]
}

# DataFrame
distance_matrix = pd.DataFrame(data)
distance_matrix.set_index('Destination Name', inplace=True)

# Visit time for destinations
visit_times = {
    'Hortan Plains National Park': 180,
    'Lake Gregory': 60,
    'Victoria Park - Nuwaraeliya': 90,
    'Hakgala Botanical Garden': 120,
    'Moon Plains': 90,
    'Pedro Tea Estate': 60,
    'Nuwara Eliya Golf Club': 90,
    'Ambewela Farm': 120
}

def dijkstra(distance_matrix, start):
    destinations = distance_matrix.columns
    distances = {destination: float('inf') for destination in destinations}
    distances[start] = 0
    priority_queue = [(0, start)]

    while priority_queue:
        current_distance, current_destination = heapq.heappop(priority_queue)

        if current_distance > distances[current_destination]:
            continue

        for neighbor in destinations:
            if neighbor == current_destination or neighbor not in mock_output:
                continue

            travel_time = distance_matrix.at[current_destination, neighbor]
            new_distance = current_distance + travel_time

            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                heapq.heappush(priority_queue, (new_distance, neighbor))

    return distances

# Itinerary Creat
def create_itinerary(destinations, time_spent, trip_duration=600):
    itinerary = []
    total_time = 0
    for destination, travel_time in sorted(destinations.items(), key=lambda x: x[1]):
        if destination not in time_spent:
            continue
        visit_time = time_spent[destination]
        if total_time + travel_time + visit_time > trip_duration:
            break
        itinerary.append((destination, travel_time, visit_time))
        total_time += travel_time + visit_time

    return itinerary

# Itinerary Multi Day
def create_multi_day_itinerary(distance_matrix, start, visit_times, days=2, day_duration=600):
    total_itinerary = {}
    remaining_destinations = visit_times.keys()

    last_destination = start

    for day in range(1, days + 1):
        distances = dijkstra(distance_matrix, last_destination)
        itinerary = create_itinerary(distances, visit_times, day_duration)

        if not itinerary:
            break

        total_itinerary[f'Day {day}'] = itinerary

        last_destination = itinerary[-1][0]  # Next day start destination

        for destination, _, _ in itinerary:
            if destination in visit_times:
                del visit_times[destination]

        remaining_destinations = visit_times.keys()
        if not remaining_destinations:
            break

    return total_itinerary

itinerary = create_multi_day_itinerary(distance_matrix, 'Ambewela Farm', visit_times, days=2)

# Itinerary print
for day, day_itinerary in itinerary.items():
    print(f"\n{day}:")
    for destination, travel_time, visit_time in day_itinerary:
        print(f"Visit {destination}, Travel Time: {travel_time} mins, Visit Time: {visit_time} mins")
