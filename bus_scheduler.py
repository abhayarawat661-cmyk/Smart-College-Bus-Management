import pandas as pd
import math

# Bus data load karo
buses = pd.read_csv("college_bus_master.csv")

# Bus capacity
BUS_CAPACITY = 50


def allocate_buses(route, time, students):
    required_buses = math.ceil(students / BUS_CAPACITY)

    # Available buses
    available_buses = buses[buses["status"] == "Available"]

    print("\n-----------------------------")
    print("BUS ALLOCATION")
    print("-----------------------------")

    print("Route:", route)
    print("Time:", time)
    print("Students:", students)
    print("Buses Required:", required_buses)

    if len(available_buses) < required_buses:
        print("❌ Not enough buses available!")
        print("Available Buses:", len(available_buses))
        return

    # Required buses select karo
    selected_buses = available_buses.head(required_buses)

    print("\nAssigned Buses:")

    for bus_id in selected_buses["bus_id"]:
        print("🚍", bus_id)

        # Bus ko running mark karo
        buses.loc[buses["bus_id"] == bus_id, "status"] = "Running"

    # Updated bus data save karo
    buses.to_csv("college_bus_master.csv", index=False)

    print("\n✅ Buses successfully allocated!")


# Example trip
allocate_buses(
    route="R3",
    time="4:00 PM",
    students=87
)