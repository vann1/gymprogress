import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import matplotlib.pyplot as plt
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

#List of all unique cells from workouts column
unique_exercises = df['Workouts'].unique()

exercise_dfs = []

#Filters all different cells from workouts column that matches the regular expression \w+\(\w+\) which are the unique days.
unique_days = df[df['Workouts'].str.contains(r'\w+\(\w+\)')]['Workouts'].unique()

#Diagram style
plt.style.use('fivethirtyeight')

#Creates subplots for different days
fig, axs = plt.subplots(3, 2, figsize=(10, len(unique_days) * 5))

#Changes 2-dimension array to 1-dimension
axs_flat = axs.flatten()

current_day = None

# Create a dictionary where the keys are the values from the unique_days list (unique "Workouts" values)
# and the values are empty DataFrame objects with the same columns as the original df
day_dfs = {day: pd.DataFrame(columns=df.columns) for day in unique_days}

# Goes through each df row. Everytime rows value can be found from unique days list it updates the current_day variable with that value.
# Then it updates day_dfs dictionary with matching key value. It creates new dataframe from "row" series object and then adds that to day_dfs[current_day] dataframe.
for index, row in df.iterrows():
    if row["Workouts"] in unique_days:
        current_day = row["Workouts"]
    if current_day:
        day_dfs[current_day] = pd.concat([day_dfs[current_day], pd.DataFrame([row])], ignore_index=True)

# Goes through each element in unique_days list. Sets day_df variable as dataframe which is the current workout day.
# Second loop goes through each unique element in day_df. It filters same exercises to new dataframe. Skips all day names(titles). 
# Then it plots the exercise with x-axis being Date and y-axis being Total Tonnage
for index, day in enumerate(unique_days):
    day_df = day_dfs[day]
    for exercise in day_df['Workouts'].unique():
        if exercise not in unique_days:  # Skip the day names
            exercise_df = day_df[day_df['Workouts'] == exercise]
            axs_flat[index].plot(exercise_df['Date'], exercise_df['Total Tonnage'], label=exercise)
    axs_flat[index].set_title(day)
    axs_flat[index].legend(loc='center left',fontsize='xx-small', bbox_to_anchor=(-0.3,0.5))
    # Sets x-axis to max 5 stamps
    axs_flat[index].xaxis.set_major_locator(plt.MaxNLocator(5))
#Deletes empty plots if there's
for ax in axs_flat[len(unique_days):]:
    ax.set_visible(False)


plt.subplots_adjust(left=0.1, right=1, bottom=0.1, top=0.9, wspace=0.5, hspace=0.3)

# pos = axs_flat[0].get_position()
# pos.x0 = 0.1
# axs_flat[0].set_position(pos)

plt.show()
 