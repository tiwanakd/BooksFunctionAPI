#Import python specefic modules
import os, json, uuid, random, re
from dotenv import load_dotenv

#Import python Azure modules 
from azure.identity import DefaultAzureCredential
from azure.mgmt.cosmosdb import CosmosDBManagementClient
from azure.mgmt.cosmosdb.models import DatabaseAccountCreateUpdateParameters, Location
from azure.mgmt.resource import ResourceManagementClient
from azure.cosmos import CosmosClient, exceptions, PartitionKey
from azure.core.exceptions import HttpResponseError

#Set up environment variables. 
SUBSCRIPTION_ID = os.environ['SUBSCRIPTION_ID']

#Setg up the Azure Credential
credentail = DefaultAzureCredential()

#Set up the Resource group, Cosmosdb mgmg and Cosmos client.
resource_group_client = ResourceManagementClient(credential=credentail, subscription_id=SUBSCRIPTION_ID)

#Create the resource group. Will do nothing if resoucrce group by the given name alread exists.
resource_group = resource_group_client.resource_groups.create_or_update(resource_group_name='BooksAPI',parameters={'location': 'westus2'})

#Setup the CosmosDBManagementClient for creating and fecthing cosmodb account/properties.
cosmos_mgmt_client = CosmosDBManagementClient(credential=credentail, subscription_id=SUBSCRIPTION_ID)

#Creating the Cosmos Database Account
def create_database_account(cosmosdb_account_name, location):
    '''
        This fuction creates Database Account.
        NOTE: This will be create a free-tier CosmosDB Account and only one free tier CosmosDB account is allowed per account. 
        Set enable_free_tier to False if there is already a free-tier cosmos account in your Azure Account.  
    '''
    try:
        poller = cosmos_mgmt_client.database_accounts.begin_create_or_update(
        resource_group_name=resource_group.name,
        account_name=cosmosdb_account_name,
        create_update_parameters=DatabaseAccountCreateUpdateParameters(
            location=location,
            locations=[Location(location_name=location)],
            enable_free_tier=True #Make this fale if Free tier account is not needed.
        )
    )
        #Make the account creation wait until complete and fetch the results. 
        poller.wait()
        result = poller.result()
        print(f"Database account create/updated successfully. Account name: {cosmosdb_account_name}, Provisiong State: {result.provisioning_state}")

    except HttpResponseError as error:
        print(error.message)


#Setting up the Database on the created DB account
def create_get_database(cosmosdb_account_name, database_name):
    '''
        Function to create a New Databse in the CosmosDB Account.
    '''
    #Get the CosmosDB account so URI and Key can be fetched from it.  
    cosmos_account = cosmos_mgmt_client.database_accounts.get(resource_group_name=resource_group.name, account_name=cosmosdb_account_name)

    #Get the CosmosDB Keys from cosmos_account
    cosmosdb_key = cosmos_mgmt_client.database_accounts.list_keys(
        resource_group_name=resource_group.name,
        account_name=cosmosdb_account_name
    )
    #Get the URI
    cosmosdb_uri = cosmos_account.document_endpoint

    #Setup Cosmos client to Create the database.
    cosmos_client = CosmosClient(url=cosmosdb_uri, credential=cosmosdb_key.primary_master_key)

    try:
        database = cosmos_client.create_database_if_not_exists(id=database_name)
    except exceptions.CosmosHttpResponseError as err:
        print(err.message)
    else:
        #Return the database so it can be user to create the container. 
        return database

    
def create_get_container(cosmosdb_account_name, database_name, container_name):
    '''
        Ths fuction creates a the container of the given name in provided db, 
        using the database obj reutned by create_database func. 
    '''
    #Calling the create_get_database to the database object. 
    database = create_get_database(cosmosdb_account_name=cosmosdb_account_name, database_name=database_name)
    #container_name = 'books'

    try:
        #Create the container, use genre name as the Partition key. 
        container = database.create_container_if_not_exists(id=container_name, partition_key=PartitionKey(path="/genre"))
    except exceptions.CosmosHttpResponseError as err:
        print(err.message)
    else:
        #Return the container so the data can be inserted. 
        return container


def insert_cover_links():
    '''
        This fuction will insert the links for the cover images that are stored in the blob container. 
        Use the books.json file that has the sample data realted to the books. 
        Inser the link to the each each obj in that file. 
    '''
    #Get the json object list from the json file. 
    with open('books.json', 'rb') as file:
        books_list = json.load(file)

    #Intialize an empty list to store the dictnaties with inserted links. 
    new_book_list = []

    #Loop over each dict obj in books_list
    for book in books_list:
        #Using regulare expressing to remote punctuations from the titlenames so this can be used in image url. 
        title = re.findall(r"[^!.', ]+",book.get('title'))
        #re.findall returns the list for all characters which has to be joined into str()
        blob_title = ''.join(title)
        #Create a new dict() for the coverURL with URL
        dict_blob_link = {'coverURL':f'https://booksapistorage.blob.core.windows.net/books-cover-images/{blob_title}.jpg'}
        #udpate each book dictionary item with blob link.
        book.update(dict_blob_link)
        #append then new book dick obj to the new list
        new_book_list.append(book)

    #Write back the new list to the json file. 
    with open('books.json', 'w') as file:
        json.dump(new_book_list, file, indent=True)

#Inserting the data to the database books container.
def insert_data(container):
    '''
        The fuction will insert the sample data from books.json file do DB container. 
    '''
    #This logic is just to organize the json file to add the id the doc
    #Also, suffling the objects in json list as I had the genres of books grouped togther.
    #This has nothing specefic to Azure
    with open('books.json') as file:
        data = json.load(file)

    books_list = []

    for item in data:
        new_dict = {"id": str(uuid.uuid4())}
        new_dict.update(item)
        books_list.append(new_dict)

    #Shuffle the objects in list.
    random.shuffle(books_list)

    #Inseting to the database Container
    try:
        for book in books_list:
            container.create_item(book)

    except exceptions.CosmosHttpResponseError as error:
        print(error.message)

#This fuction brings all the above fuctions together. 
def configure_comos_db():
    #Running the fuctions to setup the Databse
    cosmos_db_account = 'booksdbaccount'
    location = 'West US 2'
    database_name = 'booksdb'
    container_name = 'books'

    create_database_account(cosmosdb_account_name=cosmos_db_account, location=location)
    create_get_database(cosmosdb_account_name=cosmos_db_account, database_name=database_name)
    container = create_get_container(cosmosdb_account_name=cosmos_db_account, database_name=database_name, container_name=container_name)

    #The following fuctions will duplicate the data in json file and in db. 
    #Ensure to uncomment or change above parametes before re-running the fucntion. 
    insert_cover_links()
    insert_data(container=container)

if __name__ == '__main__':
    configure_comos_db()


    


