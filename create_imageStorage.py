#Download the required Azure packages to create container. 
import os, requests, json, re, subprocess
from azure.identity import DefaultAzureCredential
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.storage.models import StorageAccountCreateParameters, Sku, Kind
from azure.storage.blob import BlobServiceClient, PublicAccess, ContentSettings
from azure.core.exceptions import ResourceExistsError, HttpResponseError

# Getting the Subscription ID from the environt variables
SUBSCRIPTION_ID = os.environ['SUBSCRIPTION_ID']
#User Prinicpal name is needed to assign the Storage Account Role.
#User Prinicpal name can be reterived from Microst Entra ID under your account.
AZURE_USER_PRINCIPAL_NAME = os.environ['AZURE_USER_PRINCIPAL_NAME']

#Setup the Azure Credentails. 
credential = DefaultAzureCredential()

#Setup the Storage Management client to Create Storage Account Resources.
storage_management_client = StorageManagementClient(credential=credential, subscription_id=SUBSCRIPTION_ID)

def create_storage_account(storage_account_name, resource_group_name, location, principal_user_id):
    '''
        This function will create a Storage Account where the book covers can be stored in blob container.
        First the storage account will be created. 
        Next, required roles are to be assisnged to the Stroage account to which allows for permissions to
        upload files to the blob container.
    '''

    #Begin Stroage account create by try/except. 
    try:
        #Assigning a poller object to create the account
        storage_account = storage_management_client.storage_accounts.begin_create(
            resource_group_name=resource_group_name,
            account_name=storage_account_name,
            parameters=StorageAccountCreateParameters(
                location=location,
                kind=Kind.STORAGE_V2,
                sku=Sku(name='Standard_LRS'),
                allow_blob_public_access=True #This is needed to allow public access to view containers. 
            )
        )
        #Get the result from poller object. 
        result = storage_account.result()
        print(f'Storage account: {result.name} has been created/updated.')
    except ResourceExistsError:
        pass
    except HttpResponseError as err:
        print(err.message)

    #Assign the required roles to the Storage container, storing as list so this can be lopped over. 
    roles = ['Storage Blob Data Contributor', 'Storage Queue Data Contributor']

    #There is no python method to assign roles direclty. This to be either done via Azure Portal or AZ CLI.
    #Using the python subprocess with Az CLI to run the command in backgroud.
    #Ref: https://learn.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-python?tabs=managed-identity%2Croles-azure-cli%2Csign-in-azure-cli#authenticate-to-azure-and-authorize-access-to-blob-data
    #Looping over the roles list. 
    for role in roles:
        az_command = f'az role assignment create --role "{role}" --assignee {principal_user_id} --scope {result.id}'

        try:
            subprocess.run(az_command, shell=True, check=True, text=True, capture_output=True)
            print(f"Role '{role}' added successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error adding role '{role}': {e}")
            print("Error Output:")
            print(e.stderr)

def create_get_blob_container(resource_group_name, storage_account_name, container_name): 
    '''
        This fucntion will create a blob container to upload the book covers to. 
    '''

    #Get the propeties of the Storage Account.
    storage_account = storage_management_client.storage_accounts.get_properties(
        resource_group_name=resource_group_name,
        account_name=storage_account_name
    )

    #Get the account URL needed for BlobServiceClient
    account_url = f"https://{storage_account.name}.blob.core.windows.net/"

    # Create a blob client for manage blob container. 
    blob_service_client = BlobServiceClient(
        account_url=account_url,
        credential=credential 
    )

    #Crete the container using BlobServiceClient.
    #If the container already exists with that name, get the Container
    #Return the container object in any case. 
    try:
        blob_container = blob_service_client.create_container(name=container_name, public_access=PublicAccess.BLOB)
        print(f"Blob Container with name {container_name} has been created.")
    except ResourceExistsError:
        blob_container = blob_service_client.get_container_client(container=container_name)
        print(f"Blob Container with name {container_name} already exists in {storage_account.name}.")

    return blob_container

def get_book_olID():
    '''
        Using the openlibrary.org book api to pull out the cover images.
        This fuction will just create ol_id as dictionary for each book which will be used to
        fetch cover api endpoint.
    '''
    # Pulling the book title names from books.json file
    with open('books.json', 'rb') as file:
        json_file_data = json.load(file)

    #intiate an empty list that will be pused to a new json file.
    isbn_list = []

    #set up the base url for openlibrary.org API
    base_url = 'https://openlibrary.org/search.json'

    # loppping over the json date from books.json file
    for book in json_file_data:
        
        title = book.get('title')
        parameters = {'q':title} # set the parameter for base_url

        try:
            response = requests.get(base_url,params=parameters)
            data = response.json()
            #setting up a dictinary object with title and cover_edition_key which is ol_id for that book.  
            dict_obj = {'title':title, 'ol_id':data['docs'][0].get('cover_edition_key')}
            isbn_list.append(dict_obj)
   
        except requests.exceptions.RequestException as err:
            print(f"API Connection Failed with following error: {err}")
    
    #Open a new josn file a write the list to this file. 
    with open('books_ol.json', 'w') as file:
        json.dump(isbn_list,file,indent=2)


def download_book_images():

    '''
        This fuction will download the images from openlibrary Coves API using scraping.
        ol_ids that were created in books_ol.json file will be used to hit the endpoint for 
        each book cover image.
        DO NOT CRAWL over the openlibrary.org API as it may led to a block by them
    '''
    #Open the books_ol.json file to load json data.
    with open('books_ol.json', 'r') as file:
        book_olid_json = json.load(file)

    #Loop over the json list to get the ol_id and title. 
    for book in book_olid_json:
        olid = book.get('ol_id')

        #Using Regular Expressing to remove puntuations and whitespaces from title name so it can be used as image name. 
        title = re.findall(r"[^!.', ]+",book.get('title')) #This will reuturn a list of letters 
        image_name = ''.join(title) # Join the title to get the imagename

        #Getting images from API and writing each image with the above title name to folder. 
        try:
            response = requests.get(f'https://covers.openlibrary.org/b/olid/{olid}-M.jpg')
            with open(f"Book-Covers/{image_name}.jpg", 'wb') as file:
                file.write(response.content)

        except requests.exceptions.RequestException as err:
            print(f"API Connection Failed with following error: {err}")
            print(f"Error code: {response.status_code}")

def upload_images_to_container(container, folder_name):

    '''
        Thie fuction will upload all the images to the blob container. 
    '''
    #Looping for the files in the folder that has cover images.
    for file in os.listdir(folder_name):
            
            #file path needs to be joined as using only the file name will throw an error
            #so full file path needs to be used. 
            file_path = os.path.join(folder_name,file)

            #User the container object reutned from create_get_blob_container which is passed as a parameter in Fuction Definition. 
            blob_client = container.get_blob_client(file)

            #Open the images as read binary and uplaod to the blob contaner.
            #content settings need to be set to image/jpg so the images can be viewed in browser.
            #Default type is set to application/octet-stream which will trigger image download when the endpoing is hit.
            with open(file_path,'rb') as image:
                blob_client.upload_blob(data=image, overwrite=True, content_settings=ContentSettings(content_type='image/jpg'))


def setup_image_storage():
    '''
        This fuction will bring all the above fuctions together and setup the storage and coverimages. 
    '''
    storage_account_name = 'booksapistorage'
    resource_group_name = 'BooksAPI'
    location = 'West US 2'
    container_name = 'books-cover-images'

    create_storage_account(storage_account_name, resource_group_name, location, AZURE_USER_PRINCIPAL_NAME)
    container = create_get_blob_container(resource_group_name, storage_account_name, container_name)

    #The following two functions only need to be run if you need get need more books and add them to books.json file
    # get_book_olID()
    # download_book_images()

    upload_images_to_container(container, 'Book-Covers')
    

if __name__=='__main__':
    setup_image_storage()
                