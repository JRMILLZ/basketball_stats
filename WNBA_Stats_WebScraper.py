import requests
import pandas as pd
from bs4 import BeautifulSoup
import playernames
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    filename='wnba_stats.log',  # Log file name
    level=logging.INFO,         # Log level
    format='%(asctime)s - %(levelname)s - %(message)s'  # Log format
)

logging.info('Starting WNBA stats scraping')

URL = "https://www.basketball-reference.com/wnba/years/2024_per_game.html"

try:
    page = requests.get(URL)
    response = page.status_code

    if response == 200:
        logging.info('URL Status Code = 200')
    else:
        raise Exception(f"Unexpected Status Code: {response}")

except Exception as e:
    logging.error(f"Error fetching URL: {e}")
    # You can choose to exit or handle the error differently here
    exit()

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
csv_file_save_path = f'wnba_stats_{timestamp}.csv'

# For statistics
soup = BeautifulSoup(page.content, "html.parser")
table = soup.find('table')
rows = table.find_all('tr')

# For headers
thead = table.find('thead')
column_headers = [th.get_text() for th in thead.find_all('th')]

# For player names
player_names = [a.get_text() for a in table.select('tbody a[href^="/wnba/players"]')]

# Collecting table data
table_data = []

for row in rows:
    cols = row.find_all(['td', 'th'])
    cols = [ele.text.strip() for ele in cols]
    table_data.append(cols)

df = pd.DataFrame(table_data)

# Removing rows that are just headers or empty
df = df[~df[0].str.contains("Player", na=False)].reset_index(drop=True)

# Assigning correct column headers
df.columns = column_headers

# Replacing 'Player' column with player names
df['Player'] = player_names

tot_stats = df[df['Team'] == 'TOT']
df = df[~df['Player'].isin(tot_stats['Player'])]
df = pd.concat([df, tot_stats])

df = df.reset_index(drop=True)

for col in ['FG%', '3P%', '2P%', 'FT%']:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

df = df.astype({
    'Player': 'str',
    'Team': 'str',
    'Pos': 'str',
    'G': 'float',
    'MP': 'float',
    'G': 'float',
    'GS': 'float',
    'MP': 'float',
    'FG': 'float',
    'FGA': 'float',
    'FG%': 'float',
    '3P': 'float',
    '3PA': 'float',
    '3P%': 'float',
    '2P': 'float',
    '2PA': 'float',
    '2P%': 'float',
    'FT': 'float',
    'FTA': 'float',
    'FT%': 'float',
    'ORB': 'float',
    'TRB': 'float',
    'AST': 'float',
    'STL': 'float',
    'BLK': 'float',
    'TOV': 'float',
    'PF': 'float',
    'PTS': 'float'
})

# Save to CSV
df.to_csv(csv_file_save_path, index=False)
logging.info(f'CSV saved to {csv_file_save_path}')

# Validation checks
if len(column_headers) == len(df.columns):
    logging.info('Column length matches')
else:
    logging.warning('Column length does not match')

if len(df) == playernames.df_names_len:
    logging.info('Row length matches')
else:
    logging.warning('Row length does not match')

logging.info('WNBA Stats scraping completed successfully')
logging.info('All stats courtesy of Basketball-Reference.com (https://www.basketball-reference.com/)')








