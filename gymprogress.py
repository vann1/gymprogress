import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import matplotlib.pyplot as plt
import pandas.api.types as ptypes

colors={
    "red": "#FF0000",
    "green": "#00FF00"
}


# Käyttöoikeudet ja google sheets API yhdistäminen
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

# Lataa autentikointitiedot JSON-tiedostosta
creds = ServiceAccountCredentials.from_json_keyfile_name("./credentials.json", scope)

# Luo asiakasobjekti, joka käyttää autentikointitietoja
client = gspread.authorize(creds)


# Avaa Google Sheets -dokumentti nimeltä 'Gymprogress'
sheet = client.open("Gymprogress").worksheet("Taulukko1")

data = sheet.get_all_records(expected_headers=["Workouts","Weight", "Weight2", "Set1", "Set2", "Set3", "W2Set1","W2Set2","W2Set3","Total reps","Date","Bodyweight"])

df = pd.DataFrame(data)

date_format = "%d.%m."

df["Date"] = df["Date"].apply(lambda x: pd.to_datetime(str(x) + ".2024", format=date_format + ".%Y", errors='coerce'))

current_date = None

for index, row in df.iterrows():
    if pd.notnull(row['Date']):
        current_date = row['Date']
    else:
        df.at[index, 'Date'] = current_date
# Täytä tyhjät arvot nollilla
df.fillna(0, inplace=True)


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

unique_exercises = df['Workouts'].unique()
exercise_dfs = []

for exercise in unique_exercises:
    if exercise != "Upper(Pull)":
        exercise_df = df[df["Workouts"].str.contains(exercise)]   
        if exercise == "Single arm machine row":
            exercise_df["Total Tonnage"] = exercise_df["Total Tonnage"] / 5
        exercise_dfs.append(exercise_df)



# Plot for each exercise

for exercise_df in exercise_dfs:
    if exercise_df["Workouts"].iloc[0] != "":
        plt.plot(exercise_df["Date"], exercise_df["Total Tonnage"], label=exercise_df["Workouts"].iloc[0])

plt.legend()
plt.tight_layout()
plt.show()
