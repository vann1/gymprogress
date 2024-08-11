import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib.widgets import RadioButtons
import pandas.api.types as ptypes


# Google sheets API connection
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

# Authentication file for google sheets api
creds = ServiceAccountCredentials.from_json_keyfile_name("./credentials.json", scope)

# clinet object
client = gspread.authorize(creds)


# Open google shees file
sheet = client.open("Gymprogress").worksheet("Taulukko1")

# Saves columns from sheets to data variable
data = sheet.get_all_records(expected_headers=["Workouts","Weight", "Weight2", "Set1", "Set2", "Set3", "W2Set1","W2Set2","W2Set3","Total reps","Date","Bodyweight"])

df = pd.DataFrame(data)

date_format = "%d.%m."
# Updates each date from dataframe column to datetime objects
df["Date"] = df["Date"].apply(lambda x: pd.to_datetime(str(x) + ".2024", format=date_format + ".%Y", errors='coerce'))

current_date = None


# Fills nulls with recent date
for index, row in df.iterrows():
    if pd.notnull(row['Date']):
        current_date = row['Date']
    else:
        df.at[index, 'Date'] = current_date

#Function for filtering semicolon exercises
def contains_semicolon(cell):
    if pd.isna(cell):
        return False
    return ';' in str(cell)
#Filtered list
filtered_cells = df.applymap(contains_semicolon)
#splits singlearm work in two and sums it
for index, row in df.iterrows():
    for col in df.columns:
        if filtered_cells.at[index, col]:
            two_parts = df.at[index, col].split(";")
            totalreps = float(two_parts[0]) + float(two_parts[1])
            df.at[index, col] = totalreps

#Handles wrong inputs like alphabeticals to NaN
df['Set1'] = pd.to_numeric(df['Set1'], errors='coerce')
df['Set2'] = pd.to_numeric(df['Set2'], errors='coerce')
df['Set3'] = pd.to_numeric(df['Set3'], errors='coerce')
df['W2Set1'] = pd.to_numeric(df['W2Set1'], errors='coerce')
df['W2Set2'] = pd.to_numeric(df['W2Set2'], errors='coerce')
df['W2Set3'] = pd.to_numeric(df['W2Set3'], errors='coerce')
df['Weight'] = pd.to_numeric(df['Weight'], errors='coerce')
df['Weight2'] = pd.to_numeric(df['Weight2'], errors='coerce')

#Counts total tonnage for each set
df['Tonnage1'] = df['Weight'] * df['Set1']
df['Tonnage2'] = df['Weight'] * df['Set2']
df['Tonnage3'] = df['Weight'] * df['Set3']
df['Tonnage4'] = df['Weight2'] * df['W2Set1']
df['Tonnage5'] = df['Weight2'] * df['W2Set2']
df['Tonnage5'] = df['Weight2'] * df['W2Set3']

#Sums up all set's tonnages
df['Total Tonnage'] = df[['Tonnage1', 'Tonnage2', 'Tonnage3', 'Tonnage4', 'Tonnage5']].sum(axis=1)

#Filters all workouts column values except workout day names
filtered_df = df[~df['Workouts'].str.contains(r'\w+\(\w+\)', na=False)]

unique_exercises = filtered_df['Workouts'].unique()

unique_exercises = unique_exercises[unique_exercises != '']
 

#Filters all different cells from workouts column that matches the regular expression \w+\(\w+\) which are the unique days.
unique_days = df[df['Workouts'].str.contains(r'\w+\(\w+\)')]['Workouts'].unique()

#Diagram style
# plt.style.use('fivethirtyeight')

current_day = None

# Create a dictionary where the keys are the values from the unique_days list (unique "Workouts" values)
# and the values are empty DataFrame objects with the same columns as the original df
day_dfs = {day: pd.DataFrame(columns=df.columns) for day in unique_days}

# Goes through each df row. Everytime rows value can be found from unique days list it updates the current_day variable with that value.
# Then it updates day_dfs dictionary with matching key value. It creates new dataframe from "row" series object and then adds that to day_dfs[current_day] dataframe.
# Filter out day names
for index, row in df.iterrows():
    if row["Workouts"] in unique_days:
        current_day = row["Workouts"]
    if current_day:
        day_dfs[current_day] = pd.concat([day_dfs[current_day], pd.DataFrame([row])], ignore_index=True)
        day_dfs[current_day] = day_dfs[current_day][~day_dfs[current_day]["Workouts"].str.contains(r'\w+\(\w+\)', na=False)]
#Creates subplots for different days
fig, ax = plt.subplots(figsize=(10, 6))
plt.subplots_adjust(bottom=0.2, left=0.3)

# Muuttuja aktiiviselle kuvaajalle
current_day_index = [0]


def update_exercise(exercise):
    print("AWSDASD")

    

def update_day(index):
    keys = list(day_dfs.keys())
    ax.clear()
    day = day_dfs[keys[index]]
    day_unique_exercises = day["Workouts"].unique()

    #Removes old radiobuttons
    for widget in plt.gcf().axes:
        if isinstance(widget, RadioButtons):
            widget.remove()

    rax = plt.axes([0.05, 0.4, 0.24, 0.24])
    exerciseRadioBtn = RadioButtons(rax,labels=(day_unique_exercises), active=0)

    exerciseRadioBtn.on_clicked(lambda day_unique_exercises: update_exercise(day_unique_exercises))
    plt.draw()


def next(event):
    if current_day_index[0] < len(unique_days) - 1:
        current_day_index[0] += 1
    update_day(current_day_index[0])

def prev(event):
    if current_day_index[0] > 0:
        current_day_index[0] -= 1
    update_day(current_day_index[0])

axprev = plt.axes([0.1, 0.05, 0.2, 0.075])
axnext = plt.axes([0.7, 0.05, 0.2, 0.075])
bprev = Button(axprev, 'Previous', hovercolor="r")
bnext = Button(axnext, 'Next', hovercolor="g")
bprev.on_clicked(prev)
bnext.on_clicked(next)

# Näytä ensimmäinen kuvaaja
update_day(current_day_index[0])

plt.show()
