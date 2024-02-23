import azure.functions as func
import logging, json, os
from summary_fuction import bp

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)
app.register_functions(bp)

@app.function_name(name="Home_fuction")
@app.route(route="home", auth_level=func.AuthLevel.ANONYMOUS)
def home(req: func.HttpRequest) -> func.HttpResponse:
    """
        Display a homepage with the required links to webpage
        Fuction endpoint: https://thebooksapi.azurewebsites.net/home
    """
    logging.info('Home Fuction HTTP Trigger has been intiated!')

    home_page = """
                <html>
                <head></head>
                <body>
                <h2>Welcome to TheBooksAPI:</h2>
                <ul>
                <li>To get all books: <a href="https://thebooksapi.azurewebsites.net/allbooks">https://thebooksapi.azurewebsites.net/allbooks</a></li>
                <li>To get books by genre: <a href="https://thebooksapi.azurewebsites.net/booksbygenre/{genre_name}">https://thebooksapi.azurewebsites.net/getbooksbygenre/{genre_name}</a></li>
                <ul>
                    <li>Genre Name should be replace with the required Genre name.</li>
                </ul>
                <li>To get AI Generated summary of the given book: <a href=https://thebooksapi.azurewebsites.net/summary/{book_name}>https://thebooksapi.azurewebsites.net/summary/{book_name}</a></li>
                <ul>
                    <li>Replace the book_name with the a book, if the book is not in Database no value will be returned.</li>
                </ul>
                </body>
                </html>
    """

    return func.HttpResponse(headers={'content-type':'text/html'}, body=home_page)    

#The following fucion will query the Database and reutn all the books as HTTP Response. 
#The fuction is decorated with Comsmos DB input binding to read the data. 
@app.function_name(name="All_Books")
@app.route(route='allbooks')
@app.cosmos_db_input(arg_name='books',database_name='booksdb', container_name='books',
                     connection='CosmosDbConnectionSetting', 
                     sql_query='SELECT books.title, books.author, books.genre,\
                     books.publication_year, books.coverURL FROM books')
def get_all_books(req: func.HttpRequest, books: func.DocumentList) -> func.HttpResponse:
    '''
        This fuction returns the HTTPResoponse for all books in DB
        The SQL query run by Comsmos DB input binding will retun a list for azure.Document objects as results.
        Assinged this list to 'books'paramemeter in fuciton defination. 
        Using .to_json() on these objects which will give str representtion for this object: 
        Ref: https://learn.microsoft.com/en-us/python/api/azure-functions/azure.functions.document?view=azure-python
        Fuction endpoint: https://thebooksapi.azurewebsites.net/allbooks
    '''
    logging.info("All_Books has been triggered via HTTPTrigger!")

    #intialize an empyt list to sotre the azure.Document objects
    books_list = []
    #looping through the books list to store the odjects in above list.
    for book in books:
        #.to_json() methdo will give a str() representtion, this needs to be converted to dict() obj to feed to json.dumps
        dict_obj = json.loads(book.to_json())
        books_list.append(dict_obj) #  Append the dict objects to the list. 

    # Return as HttpResponse
    return func.HttpResponse(json.dumps(books_list, indent=True), mimetype='application/json')


#This fuction will return the Books by the given year.
#The fuction is deocrated with same Input binding with the related SQL query.
@app.function_name(name="Genre_Books")
@app.route(route='booksbygenre/{genre_name}')
@app.cosmos_db_input(arg_name='booksbygenre', database_name='booksdb', container_name='books',
                     connection='CosmosDbConnectionSetting',
                     sql_query="SELECT books.title, books.author, books.genre, books.publication_year, books.coverURL FROM books\
                                WHERE lower(books.genre) = lower({genre_name})")
def get_books_by_genre(req: func.HttpRequest, booksbygenre: func.DocumentList) -> func.HttpResponse:

    '''
     This fuciton returns books by the given Genre Name. 
     SQL Qeury is set in the Cosmos DB input binding - Input binding,
     the genre name is fetched by sql_query from the route parameter,
     The result is them return as a list of Azure.Document objects from Cosmos DB. 
     Fuction endpoint: https://thebooksapi.azurewebsites.net/getbooksbygenre/{genre_name}
    '''
    logging.info("Genre_Books has been triggered via HTTPTrigger!")

    #Setting up an emply book list. 
    books_list = []
    #Grabbin the paramer passed by the user to print it out if needed. 
    genre_name = req.route_params.get('genre_name')

    #Running a try/except to watch out for any indexerrors when running the look of the DocumentList.
    #Rest of the fuction follows same logic as the get_all_books fuction. 
    try:
        for book in booksbygenre:
            dict_obj = json.loads(book.to_json())
            books_list.append(dict_obj)
    except IndexError:
        return func.HttpResponse(f"No books in the Genre: {genre_name}. Pass in a correct book genre.")
    else:
        #if our books list comes out to be empty or there is no book for given category,
        #The user will be prompted to with following message otherwise lise will rendered. 
        if len(books_list) == 0:
            return func.HttpResponse(f"No books in the Genre: {genre_name}. Pass in a correct book genre.")
        else:
            return func.HttpResponse(json.dumps(books_list, indent=True), mimetype='application/json')


    



