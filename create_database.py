########################################################
# Please run the following PIP installs need to be run
# before running this file:
# azure-identity==1.15.0
# azure-mgmt-core==1.4.0
# azure-mgmt-cosmosdb==9.4.0
# azure-mgmt-resource==23.0.1
# azure-common==1.1.28
# azure-core==1.30.0
# azure-cosmos==4.5.1
#########################################################


#Import python specefic modules
import os, json, uuid, random, re, pprint 
from dotenv import load_dotenv

#Import python Azure modules 
from azure.identity import DefaultAzureCredential
from azure.mgmt.cosmosdb import CosmosDBManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.cosmos import CosmosClient, exceptions, PartitionKey
from azure.core.exceptions import ResourceExistsError, HttpResponseError

#Setting up environment variables. 
load_dotenv('.env')
SUBSCRIPTION_ID = os.getenv('SUBSCRIPTION_ID')
COSMOS_URL = os.environ['COSMOS_URL']
COSMOS_KEY = os.environ['COSMOS_KEY']

#Setting up the Azure Credential
credentail = DefaultAzureCredential()

#Setting up the Resource group, Cosmosdb mgmg and Cosmos client.
resource_group_client = ResourceManagementClient(credential=credentail, subscription_id=SUBSCRIPTION_ID)

#Creating the resource group. 
resource_group = resource_group_client.resource_groups.create_or_update(resource_group_name='BooksAPI',parameters={'location': 'westus2'})

#Setting up the CosmosDB Management client to create the DB Account
cosmos_mgmt_client = CosmosDBManagementClient(credential=credentail, subscription_id=SUBSCRIPTION_ID)


#Creating the Cosmos Database Account
def create_database_account():
    '''
    This fuction creates Database Account.
    '''

    # Setup the CosmosDBManagementClient
    cosmos_mgmt_client = CosmosDBManagementClient(credential=credentail, subscription_id=SUBSCRIPTION_ID)
    cosmosdb_account_name = "booksdbaccount"

    try:
        cosmos_mgmt_client.database_accounts.begin_create_or_update(
        resource_group_name=resource_group.name,
        account_name=cosmosdb_account_name,
        create_update_parameters={
            "location": "West US 2",  
            "kind": "GlobalDocumentDB",
            "properties": {
                "databaseAccountOfferType": "Standard",
                "consistencyPolicy": {
                    "defaultConsistencyLevel": "Session",
                        }
                    }
                }       
            )
    except HttpResponseError as error:
        print(error.message)


#Setting up the Database on the created DB account
def create_database():
    '''
        Function to create a New Databse in the CosmosDB Account
    '''

    # Setup the Cosmos Client
    cosmos_client = CosmosClient(COSMOS_URL, COSMOS_KEY)

    database_name = 'booksdb'

    # Using a try/catch to 
    try:
        database = cosmos_client.create_database(id=database_name)
    except exceptions.CosmosResourceExistsError:
        database = cosmos_client.get_database_client(database=database_name)
    except exceptions.CosmosHttpResponseError as err:
        print(err.message)

    return database

#Creating the container for the database. 
def create_container():

    database = create_database()
    container_name = 'books'
    
    try:
        container = database.create_container(id=container_name, partition_key=PartitionKey(path="/genre"))
    except exceptions.CosmosResourceExistsError:
        container = database.get_container_client(container=container_name)
    except exceptions.CosmosHttpResponseError as err:
        print(err.message)

    return container

#This fuction will insert the links for the cover images that are stored in the blob container. 
def insert_cover_links():

    with open('books.json', 'rb') as file:
        books_list = json.load(file)

        new_book_list = []

        for book in books_list:
            #Using regulare expressing to remote punctuations from the titlenames so this can be used in image url. 
            title = re.findall(r"[^!.', ]+",book.get('title'))
            blob_title = ''.join(title)
            dict_blob_link = {'coverURL':f'https://booksapistorage.blob.core.windows.net/books-cover-images/{blob_title}.jpg'}
            #udpate each book dictionary item with blob link.
            book.update(dict_blob_link)
            #append then new book dick obj to the new list
            new_book_list.append(book)

    #Write back the new list to the json file. 
    with open('books.json', 'w') as file:
        json.dump(new_book_list, file, indent=True)

#Inserting the data to the database books container.
#Using the books.json file that has some sample book data in it. 
def insert_data():
    
    #This logic is just to organize the json file to add the id the doc
    #Also, sufflingin the objects in json list as I had the genres of books togther
    # This has nothing specefic to Azure
    with open('books.json') as file:
        data = json.load(file)

    books_list = []

    for item in data:
        new_dict = {"id": str(uuid.uuid4())}
        new_dict.update(item)
        books_list.append(new_dict)

    random.shuffle(books_list)

    # Getting the cotainer object from create_container method to insert into the collection.
    container = create_container()
    
    #Inseting to the database
    try:
        for book in books_list:
            container.create_item(book)

    except exceptions.CosmosHttpResponseError as error:
        print(error.message)

         
#This fuction brings all the above fuctions together. 
#Only needs to be executed once to prevent duplication of data.  
def configure_comos_db():
    #Running the fuctions to setup the Databse
    create_database_account()
    create_database()
    create_container()
    insert_cover_links()
    insert_data()


if __name__ == '__main__':
    configure_comos_db()


    


