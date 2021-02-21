import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from random import randint

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']


class Products:
    """Gets product data from a Sheets spreadsheet and creates Products from it.
    """
    def __init__(self, sheet='Shop'):
        self.spreadsheet_id = '16h1kQYuilq8BUXBvFrZ7Am0mBL1m_sxUe76Ko09Jd6Y'
        self.product_list = self.fetch_products(sheet)

    def fetch_products(self, sheetname):
        """Shows basic usage of the Sheets API.
        Prints values from a sample spreadsheet.
        """
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
        range_name = '%s!A2:J'%sheetname
        result = sheet.values().get(spreadsheetId=self.spreadsheet_id,
                                    range=range_name).execute()
        values = result.get('values', [])

        product_list = []
        if not values:
            return 'No data found.'
        else:
            for row in values:
                # Create a product for each row
                product_list.append(Product(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]))
        return product_list

    def generate_products(self):
        items = []
        for p in self.product_list:
            items.append(p.generate_product())
        return items

    def pick_few(self, amount):
        """Picks # number of items from product list, no repeats.
        """
        picked = []
        temp_items = self.generate_products()
        for i in range(amount):
            random_int = randint(0, len(temp_items)-1)
            pick = temp_items[random_int]
            picked.append(pick)
            temp_items.remove(pick)
        return picked

class Product:
    """Products are the data representation of 'items' on a shopfront.
    """
    def __init__(self, p_id, name, stock, cost_type, cost_min, cost_max, product_type, product_min, product_max, desc):
        self.product_id = p_id
        self.name = name
        self.base_stock = int(stock)
        self.cost_type = cost_type
        self.base_cost = (int(cost_min), int(cost_max))  # cost range
        self.product_type = product_type
        self.base_product = (int(product_min), int(product_max))
        self.description = desc
        self.cost = 0
        self.product = 0
        self.stock = 0

    def generate_product(self):
        self.cost = min(max(round(randint(self.base_cost[0], self.base_cost[1])/50)*50, self.base_cost[0]), self.base_cost[1])   # it's ok i hate this too
        self.product = min(max(round(randint(self.base_product[0], self.base_product[1])/10)*10, self.base_product[0]), self.base_product[1])
        return self

if __name__ == '__main__':
    p = Products('Black market')
    items = p.pick_few(3)
    for i in items:
        print(i.name)
