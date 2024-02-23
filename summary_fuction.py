import logging, json
import azure.functions as func
from openai import OpenAI, OpenAIError, AuthenticationError

#Set up the a blueprint Azure function, which will be registed in the main fuction_app.py file. 
bp = func.Blueprint()

#Decorate the fuction with required decorators
@bp.function_name(name='Book_Summary')
@bp.route(route='summary/{book_name}')
@bp.cosmos_db_input(arg_name='books', database_name='booksdb', container_name='books', connection='CosmosDbConnectionSetting',
                    sql_query="SELECT books.title, books.author, books.genre, books.publication_year, books.coverURL FROM books\
                                WHERE lower(books.title) = lower({book_name})")
def generate_book_summary(req: func.HttpRequest, books: func.DocumentList) -> func.HttpResponse:
    '''
        This function will return a summary of the book based to the title given by the client.
        DB is being queried by book name using Fuction Cosmos input Binding
        OpenAI API that uses GPT-3.5 model will be used to generate summary.
        Summary will be reutned with the book in info as HTTP response. 
        Fuction endpoint: https://thebooksapi.azurewebsites.net/summary/{book_name}
    '''

    logging.info("Book_Summary has been triggered via HTTPTrigger!")

    # Get the book name given by the client.
    book_name = req.route_params.get('book_name')
    
    try:
        #Since we need just one book, will just get first element in list retuned by func.DocumentList, 
        #which is stored as a fuction parameter
        book = json.loads(books[0].to_json())

        try:
            #Create the OpenAI object
            #NOTE - This object will need an API key which should be stored as environment variable. 
            #Documentation for this API in python- https://platform.openai.com/docs/quickstart?context=python
            #Once the fuction is ready to be deployed, API key should added to Function Enviroment Variables,
            #either via the Azure CLI or the Portal: https://learn.microsoft.com/en-us/azure/azure-functions/functions-how-to-use-azure-function-app-settings?tabs=portal#get-started-in-the-azure-portal
            ai_client = OpenAI()
            #Intialize the query to the OpenAI API
            ai_summary = ai_client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                {"role": "system", "content": "You are a Librarian who has read a lot of books and \
                 who can provide summaries of books."},
                {"role": "user", "content": f"Give me a one-two line summary of book {book_name} and \
                 do not include the book name in summary"}
                ]
            )
        except AuthenticationError:
            logging.info("Error with Authentication")
        except OpenAIError as err:
                logging.info(err)
        
        #Get only the content retuned by the ai_summary object which should be str()
        book_summary = ai_summary.choices[0].message.content
        #Create a dictonary onject toe store the book summary as kvp
        summary_dict = dict(generatedSummary = book_summary)
        #Update the book dictonary with summmary
        book.update(summary_dict)
    #If no books were returned by the DB, catch the indexError (as func.DocumentList will be empty) exception and promt the client. 
    except IndexError:
        return func.HttpResponse(f"No book found by name {book_name}. Pass in a correct Book name")
    else:
        #If not indexError return the book dict that was updated with the summary       
        return func.HttpResponse(json.dumps(book, indent=True), mimetype='application/json')
