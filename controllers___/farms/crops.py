import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def fetch_crops(sheetname):
    spreadsheet_id = '16h1kQYuilq8BUXBvFrZ7Am0mBL1m_sxUe76Ko09Jd6Y'

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    range_name = '%s!A2:V'%sheetname
    result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                range=range_name).execute()
    values = result.get('values', [])

    product_list = []
    if not values:
        return 'No data found.'
    else:
        for row in values:
            def get_int(s):  # handle empty string as 0
                return int(s) if s else 0
            # Create a product for each row
            crop_id = int(row[0])
            category = row[1]
            name = row[2]
            emoji = (row[3], row[4], row[5])
            reusable = row[6] == 'y'
            grow_time = (get_int(row[7])) * 60  # convert minutes to secs
            cost = [Price('credits', get_int(row[8])), Price('asacoco', get_int(row[9])), Price('yubi', get_int(row[10]))]
            product = [Price('credits', get_int(row[11])), Price('asacoco', get_int(row[12])), Price('yubi', get_int(row[13]))]
            description = row[-1]
            prerequisite = int(row[-2])
            xp = int(row[-3])
            product_list.append(Crop(
                crop_id,
                name,
                emoji,
                description,
                prerequisite,
                category,
                reusable,
                grow_time,
                cost,
                product,
                xp,
            ))
    print(product_list[0])
    return product_list[:16]


class Crop:
    """Static? class for a plant in a farms.
    """
    def __init__(self, c_id, name, emoji, description, prerequisite, category, reusable, grow_time, cost, product, xp):
        self.id = c_id
        self.name = name
        self.emoji = emoji
        self.description = description
        self.prerequisite = prerequisite
        self.category = category
        self.cost = cost
        self.product = product
        self.grow_time = grow_time
        self.reusable = reusable  # Whether the crop disappears or not after harvesting
        self.xp = xp

    def __str__(self):
        return str((self.id, self.name, self.description, self.prerequisite, self.category, self.cost, self.product, self.grow_time, self.reusable))


class Price:
    """Static data class for costs and prices.
    """
    def __init__(self, curr_type='credits', amount=0):
        self.type = curr_type
        self.amount = int(amount)

    def __str__(self):
        return str((self.type, self.amount))

    def __repr__(self):
        return str((self.type, self.amount))

if __name__ == '__main__':
    p = fetch_crops('Crops')
    print(p)
