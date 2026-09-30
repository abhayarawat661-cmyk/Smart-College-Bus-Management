import pandas as pd

# Load dataset
df = pd.read_csv("college_bus_demand_dataset.csv")

# First 10 rows
print("First 10 rows:")
print(df.head(10))

# Total records
print("\nTotal records:", len(df))

# All columns
print("\nColumns:")
print(df.columns.tolist())

# Routes
print("\nRoutes:")
print(df["route"].unique())

# Available timings
print("\nTimings:")
print(df["time"].unique())

# Total students needing bus
print("\nTotal students needing bus:",
      df["students_needing_bus"].sum())

# Total buses required
print("\nTotal required bus trips:",
      df["required_buses"].sum())

# Average bus demand
print("\nAverage students needing bus:",
      round(df["students_needing_bus"].mean(), 2))


import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv("college_bus_demand_dataset.csv")

# Average bus demand by time
time_demand = df.groupby("time")["students_needing_bus"].mean()

print("\nAverage bus demand by time:")
print(time_demand.round(2))

# Graph
time_demand.plot(kind="bar")

plt.title("Average Bus Demand by Time")
plt.xlabel("Time")
plt.ylabel("Average Students Needing Bus")
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()


import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error

# Load dataset
df = pd.read_csv("college_bus_demand_dataset.csv")

# Features
X = df[["route", "time", "day", "shift"]]

# Target
y = df["students_needing_bus"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Categorical columns
categorical_columns = ["route", "time", "day", "shift"]

# Encoding
preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_columns)
    ]
)

# ML Model
model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

# Complete pipeline
pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ]
)

# Train model
pipeline.fit(X_train, y_train)

# Prediction
predictions = pipeline.predict(X_test)

# Accuracy measurement
mae = mean_absolute_error(y_test, predictions)

print("Model trained successfully!")

print("Mean Absolute Error:", round(mae, 2))


# New trip for prediction
new_data = pd.DataFrame({
    "route": ["R3"],
    "time": ["4:00 PM"],
    "day": ["Monday"],
    "shift": ["Evening"]
})

# Predict students
predicted_students = pipeline.predict(new_data)[0]

# Bus capacity
bus_capacity = 50

# Calculate required buses
required_buses = int((predicted_students + bus_capacity - 1) // bus_capacity)

print("\n----- NEW TRIP PREDICTION -----")
print("Route:", new_data["route"].iloc[0])
print("Time:", new_data["time"].iloc[0])
print("Day:", new_data["day"].iloc[0])

print("Predicted Students:", round(predicted_students))
print("Required Buses:", required_buses)