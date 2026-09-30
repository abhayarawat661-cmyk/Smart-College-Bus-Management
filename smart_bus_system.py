import pandas as pd
import math

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline

# -----------------------------
# 1. Load dataset
# -----------------------------

df = pd.read_csv("college_bus_demand_dataset.csv")

# Features
X = df[["route", "time", "day", "shift"]]

# Target
y = df["students_needing_bus"]

# -----------------------------
# 2. Train ML model
# -----------------------------

categorical_columns = ["route", "time", "day", "shift"]

preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"),
         categorical_columns)
    ]
)

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("model", model)
])

pipeline.fit(X, y)

print("✅ ML Model trained successfully!")


# -----------------------------
# 3. Take user input
# -----------------------------

route = input("\nEnter route (R1-R10): ")
time = input("Enter time (7:00 AM / 11:00 AM / 1:00 PM / 4:00 PM / 6:00 PM): ")
day = input("Enter day: ")
shift = input("Enter shift: ")


# -----------------------------
# 4. Predict students
# -----------------------------

new_data = pd.DataFrame({
    "route": [route],
    "time": [time],
    "day": [day],
    "shift": [shift]
})

predicted_students = pipeline.predict(new_data)[0]

bus_capacity = 50

required_buses = math.ceil(
    predicted_students / bus_capacity
)

print("\n==============================")
print("BUS DEMAND PREDICTION")
print("==============================")

print("Route:", route)
print("Time:", time)
print("Day:", day)

print(
    "Predicted Students:",
    round(predicted_students)
)

print(
    "Required Buses:",
    required_buses
)


# -----------------------------
# 5. Load buses
# -----------------------------

buses = pd.read_csv("college_bus_master.csv")

available_buses = buses[
    buses["status"] == "Available"
]

print("\nAvailable Buses:",
      len(available_buses))


# -----------------------------
# 6. Allocate buses
# -----------------------------

if len(available_buses) >= required_buses:

    selected_buses = available_buses.head(
        required_buses
    )

    print("\n🚍 Assigned Buses:")

    for bus_id in selected_buses["bus_id"]:

        print("   ", bus_id)

        buses.loc[
            buses["bus_id"] == bus_id,
            "status"
        ] = "Running"

    buses.to_csv(
        "college_bus_master.csv",
        index=False
    )

    print("\n✅ Buses successfully assigned!")

else:

    print("\n❌ Not enough buses available!")

    print(
        "Required:",
        required_buses
    )

    print(
        "Available:",
        len(available_buses)
    )