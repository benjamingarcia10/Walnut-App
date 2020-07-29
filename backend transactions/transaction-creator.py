import os
import uuid
import math
import random
from datetime import datetime
import threading
from cloudant.client import Cloudant
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv(override=True)

# Initiate connection with Cloudant server
client = Cloudant.iam(os.getenv('SERVICE_USERNAME'), os.getenv('CLOUDANT_APIKEY'), connect=True)

# Set desired database name for transactions, rounded up amounts, and donation transactions, respectively
database_names = {
    'user-transactions-db-name': 'user-transactions',
    'round-up-db-name': 'round-up',
    'donations-db-name': 'donations'
}
# Set minimum and maximum transaction amounts to generate
minimum_transaction_amount = 2.5
maximum_transaction_amount = 175
round_up_threshold = 5

# Create databases in server if not already created using user defined names
for database in database_names:
    if database_names[database] not in client.all_dbs():
        client.create_database(database_names[database], partitioned=False)

# Set CloudantDatabase objects
transactions_database = client[database_names['user-transactions-db-name']]
round_up_database = client[database_names['round-up-db-name']]
donations_database = client[database_names['donations-db-name']]

# Create store list from file named "store-names.txt"
with open('./store-names.txt') as f:
    store_names = f.readlines()
store_names = [line.strip() for line in store_names]


def clear_databases():
    for database in database_names:
        client.delete_database(database_names[database])
        client.create_database(database_names[database], partitioned=False)


def create_random_transactions():
    random_amount = round(random.uniform(minimum_transaction_amount, maximum_transaction_amount), 2)
    rounded_amount = round(math.ceil(random_amount) - random_amount, 2)
    current_datetime = datetime.now().strftime("%B %d, %Y %H:%M:%S")
    transaction_uuid = f'{current_datetime} {str(uuid.uuid4())}'
    data = {}
    transaction_data = {
        '_id': transaction_uuid,
        'date': current_datetime,
        'name': random.choice(store_names),
        'amount': f'{random_amount:.2f}',
        'rounded': f'{rounded_amount:.2f}'
    }
    data['transaction_data'] = transaction_data

    rounded_data = {
        '_id': transaction_uuid,
        'rounded': f'{rounded_amount:.2f}'
    }
    data['rounded_data'] = rounded_data

    return data


def add_random_transaction():
    threading.Timer(5, add_random_transaction).start()
    new_documents = create_random_transactions()
    new_transaction_document = transactions_database.create_document(new_documents['transaction_data'])
    print(f'{new_transaction_document} added to {transactions_database}.')
    new_rounded_document = round_up_database.create_document(new_documents['rounded_data'])
    print(f'{new_rounded_document} added to {round_up_database}.')
    check_threshold()


def check_threshold():
    round_up_amount = 0
    for document in round_up_database:
        round_up_amount += float(document['rounded'].replace('$', ''))
    if round_up_amount >= round_up_threshold:
        current_datetime = datetime.now().strftime("%B %d, %Y %H:%M:%S")
        transaction_uuid = f'{current_datetime} {str(uuid.uuid4())}'
        data = {
            '_id': transaction_uuid,
            'date': current_datetime,
            'name': 'Walnut Donation',
            'amount': f'{round(round_up_amount, 2):.2f}',
        }
        new_donation = donations_database.create_document(data)
        print(f'{new_donation} added to {donations_database}')
        client.delete_database(database_names['round-up-db-name'])
        client.create_database(database_names['round-up-db-name'], partitioned=False)


clear_databases()
add_random_transaction()
