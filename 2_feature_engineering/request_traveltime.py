import asyncio
from datetime import datetime, timedelta
from traveltimepy import Coordinates, TravelTimeSdk, PublicTransport, FullRange, \
    Location, Property
from traveltimepy.errors import ApiError
import pandas as pd

# Paths to CSV files
MTC = "combined_data_MP_NE_MTC_Coord_5.csv"
UCO = "combined_data_MP_NE_Coord_uniqueClusterOutside.csv"
# Initialize counter to store the number of requests made
COUNTER = 0


# Read CSV files and prepare data for API requests
def read_csv(csv):
    df = pd.read_csv(csv)
    result = []
    result_names = []

    # Loop through rows in the DataFrame
    for index, row in df.iterrows():
        coords = Coordinates(lat=row["lat"], lng=row["lon"])
        location = Location(id=row["name"], coords=coords)
        result.append(location)
        result_names.append(row["name"])
    print(len(result))
    return result, result_names


# Fetch routes asynchronously
async def fetch_routes(loc_start, all_loc_end, sdk):
    try:
        all_results = []

        # Iterate in steps of 2 to create pairs of end locations
        for i in range(0, 6, 2):
            if i == 4:
                loc_end = [all_loc_end[i].id]
            else:
                loc_end = [all_loc_end[i].id, all_loc_end[i + 1].id]

            # Perform asynchronous API requests
            results = await sdk.routes_async(
                locations=[loc_start] + all_loc_end,
                search_ids={
                    loc_start.id: loc_end
                },
                properties=[Property("travel_time"), Property("distance")],
                transportation=PublicTransport(walking_time=28800, pt_change_delay=0),
                departure_time=datetime(year=2023, month=8, day=9, hour=7, minute=0),
                range=FullRange(enabled=True, max_results=1, width=3600)
            )
            all_results.append(results)

            global COUNTER
            COUNTER += 1
            print(COUNTER)

        return all_results

    except ApiError as e:
        # Handle API error by waiting for the next minute
        print("Too many requests, waiting for the next minute...")
        current_time = datetime.now()
        next_minute = current_time.replace(second=0, microsecond=0) + timedelta(minutes=1)
        await asyncio.sleep((next_minute - current_time).total_seconds())


# Fetch routes using semaphore to limit concurrent API requests
async def fetch_routes_with_semaphore(semaphore, loc_start, all_loc_end, sdk):
    async with semaphore:
        return await fetch_routes(loc_start, all_loc_end, sdk)


# Main asynchronous function
async def main():
    all_results = []
    top1_results = []

    # Initialize TravelTime SDK
    sdk = TravelTimeSdk(APP_ID, APP_KEY)

    # Read location data from CSV files
    all_loc_start, _ = read_csv(UCO)
    all_loc_end, loc_end_ids = read_csv(MTC)

    # Sort the starting locations
    all_loc_start = sorted(all_loc_start, key=lambda location: location.id, reverse=True)

    # Semaphore to limit concurrent API requests
    semaphore = asyncio.Semaphore(5)  # Limit to 5 simultaneous API requests

    tasks = []
    for loc_start in all_loc_start:
        tasks.append(fetch_routes_with_semaphore(semaphore, loc_start, all_loc_end, sdk))

    # Gather results from asynchronous tasks
    results = await asyncio.gather(*tasks)

    for loc_start, results_list in zip(all_loc_start, results):
        if results_list is not None:
            top1_tt = 43200
            top1 = {}
            for result in results_list:
                result = result[0]
                for location in result.locations:
                    if location.properties is not None:
                        for prop in location.properties:
                            all_results.append(
                                {'search_id': result.search_id,
                                 'id': location.id, 'travel_time': prop.travel_time,
                                 'distance': prop.distance})
                            if prop.travel_time < top1_tt:
                                top1_tt = prop.travel_time
                                top1 = {'search_id': result.search_id, 'id': location.id,
                                        'travel_time': prop.travel_time,
                                        'distance': prop.distance}

            top1_results.append(top1)

    # Store results in DataFrames and export to CSV files
    df = pd.DataFrame(all_results)
    df.to_csv("traveltime_results_all.csv", index=False)

    df_top1 = pd.DataFrame(top1_results)
    df_top1.to_csv("traveltime_results_top1.csv", index=False)


# Execute the main function using asyncio
def run_main():
    asyncio.run(main())


if __name__ == "__main__":
    run_main()
