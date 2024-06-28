import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import matplotlib.pyplot as plt


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
# df.sort_values(by='Date', inplace=True)

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

#Initializes new dataframe for each exercise
wide_pullup = df[df["Workouts"].str.contains("Wide")]
seated_db_ohp = df[df["Workouts"].str.contains("Seated db ohp")]
singlearm_machinerow = df[df["Workouts"].str.contains("Single arm machine row")]
db_bench_press = df[df["Workouts"].str.contains("Db bench press")]
cable_oh_ex = df[df["Workouts"].str.contains("1Cable oh ex")]
db_side_raises = df[df["Workouts"].str.contains("1Db side raises")]
alternating_seated_curl = df[df["Workouts"].str.contains("1Alternating seated curls")]

#Single arm machine row total tonnage divided, because much larger compared to other exercises. Makes the diagram look better.
singlearm_machinerow["Total Tonnage"] = singlearm_machinerow["Total Tonnage"].apply(lambda x: x / 5)

#Plot style
plt.style.use('fivethirtyeight')

#Plot for each exercise
plt.plot(wide_pullup["Date"], wide_pullup["Total Tonnage"], label="Wide Pull Up")
plt.plot(seated_db_ohp["Date"], seated_db_ohp["Total Tonnage"], label="Seated Overhead Press")
plt.plot(singlearm_machinerow["Date"], singlearm_machinerow["Total Tonnage"], label="Single Arm Machinerow")
plt.plot(db_bench_press["Date"], db_bench_press["Total Tonnage"], label="Dumbell Bench Press")
plt.plot(cable_oh_ex["Date"], cable_oh_ex["Total Tonnage"], label="Cable Overhead Extention")
plt.plot(db_side_raises["Date"], db_side_raises["Total Tonnage"], label="Side Raises")
plt.plot(alternating_seated_curl["Date"], alternating_seated_curl["Total Tonnage"], label="Seated Alternating Curl")


plt.legend()
plt.tight_layout()

plt.show()