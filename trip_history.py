import pandas as pd
from datetime import datetime
import os

FILE = "trip_history.csv"

# Agar file nahi hai to create karo
if not os.path.exists(FILE):
    df = pd.DataFrame(columns=[
        "date",
        "route",
        "time",
        "predicted_students",
        "required_buses",
        "assigned_buses",
        "status"
    ])

    df.to_csv(FILE, index=False)


def add_trip(route, time, students, buses):

    df = pd.read_csv(FILE)

    new_trip = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "route": route,
        "time": time,
        "predicted_students": students,
        "required_buses": len(buses),
        "assigned_buses": ", ".join(buses),
        "status": "Running"
    }

    df = pd.concat(
        [df, pd.DataFrame([new_trip])],
        ignore_index=True
    )

    df.to_csv(FILE, index=False)

    print("✅ Trip saved successfully!")


# Example
add_trip(
    "R3",
    "4:00 PM",
    87,
    ["BUS-01", "BUS-02"]
)