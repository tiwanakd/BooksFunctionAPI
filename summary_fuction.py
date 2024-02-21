import logging, json
import azure.functions as func
from openai import OpenAI, OpenAIError, AuthenticationError

bp = func.Blueprint()

@bp.function_name(name='Book_Summary')
@bp.route(route='summary/{book_name}')
@bp.cosmos_db_input(arg_name='books', database_name='booksdb', container_name='books', connection='CosmosDbConnectionSetting',
                    sql_query="SELECT books.title, books.author, books.genre, books.publication_year, books.coverURL FROM books\
                                WHERE lower(books.title) = lower({book_name})")
def generate_book_summary(req: func.HttpRequest, books: func.DocumentList) -> func.HttpResponse:
    '''
    
    '''

    logging.info("Book_Summary has been triggered via HTTPTrigger!")

    book_name = req.route_params.get('book_name')
    
    try:
        book = json.loads(books[0].to_json())

        try:
            ai_client = OpenAI()
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
        
        book_summary = ai_summary.choices[0].message.content
        summary_dict = dict(generatedSummary = book_summary)
        book.update(summary_dict)

    except IndexError:
        return func.HttpResponse(f"No book found by name {book_name}")
    else:       
        return func.HttpResponse(json.dumps(book, indent=True), mimetype='application/json')
    #return func.HttpResponse(books_summary.choices[0].message.content)
