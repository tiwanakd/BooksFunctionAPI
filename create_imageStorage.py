#Download the required Azure packages to create container. 
import os, requests, json, re
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, PublicAccess, ContentSettings
from azure.core.exceptions import ResourceExistsError

# Getting the Subscription ID from the environt variables
SUBSCRIPTION_ID = os.environ['SUBSCRIPTION_ID']

credential = DefaultAzureCredential()

# Create a blob client for manage blob container. 
blob_service_client = BlobServiceClient(
    account_url='https://booksapistorage.blob.core.windows.net/',
    credential=credential 
)


def create_blob_container(): 
    '''
        This fucntion will create a blobc container to upload the book covers to. 
    '''

    container_name = 'books-cover-images'

    try:
        blob_service_client.create_container(name=container_name, public_access=PublicAccess.BLOB)
    except ResourceExistsError:
        pass

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
        each book cover image
    
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



def upload_images_to_container():

    '''
        Thie fuction will upload all the images to the blob container. 
    '''
    #Get the container client. 
    container_client = blob_service_client.get_container_client('books-cover-images')

    #Looping for the files in the folder that has cover images.
    for file in os.listdir('Book-Covers'):
            
            #file path needs to be joined as using only the file name will throw an error
            #so full file path needs to be used. 
            file_path = os.path.join('Book-Covers',file)

            #setup the blob client. 
            blob_client = container_client.get_blob_client(file)

            #Open the images as read binary and uplaod to the blob contaner.
            #content settings need to be set to image/jpg so the images can be viewed in browser.
            #Default type is set to application/octet-stream which will trigger image download when the endpoing is hit.
            with open(file_path,'rb') as image:
                blob_client.upload_blob(data=image, content_settings=ContentSettings(content_type='image/jpg'))


def setup_image_storage():
    create_blob_container()
    get_book_olID()
    download_book_images()
    upload_images_to_container()
    

if __name__=='__main__':
    setup_image_storage()
                