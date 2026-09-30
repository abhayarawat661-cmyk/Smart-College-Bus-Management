import pandas as pd

# Bus data load
buses = pd.read_csv("college_bus_master.csv")

def return_bus(bus_id):

    if bus_id not in buses["bus_id"].values:
        print("❌ Bus not found!")
        return

    current_status = buses.loc[
        buses["bus_id"] == bus_id, "status"
    ].iloc[0]

    if current_status == "Running":

        buses.loc[
            buses["bus_id"] == bus_id, "status"
        ] = "Available"

        buses.to_csv("college_bus_master.csv", index=False)

        print("✅", bus_id, "has returned.")
        print("Status: Available")

    else:
        print("ℹ️", bus_id, "is already available.")


# Example
return_bus("BUS-01")