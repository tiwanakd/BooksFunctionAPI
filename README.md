# Books API Fuctions App
### Description
- This is API that provides books data for a few books in json format.
-	The API has the following Endpoints:
    - Home Page - https://thebooksapi.azurewebsites.net/home
    - All books - https://thebooksapi.azurewebsites.net/allbooks
    - Books in given genre - https://thebooksapi.azurewebsites.net/booksbygenre/{genre_name}
    - AI Generated book summary - https://thebooksapi.azurewebsites.net/summary/{book_name}
- This API is written in Python using the Azure Python SDK.
- It uses the following Azure Resouces:
    - Azure Fuctions: These does do the heaving Lifting of getting the data from DB and return the Json.
    - Azure Cosmos DB: Stores the books data in NoSQL DB.
    - Azure Blob Storage: Stores the Cover images for the books.
### Setup
- An Azure Account with Subscription enabled is needed.
- I have used VS Code for this project.
- Instructions realted to Azure Fuctions: [Azure Functions Python developer guide](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python?tabs=asgi%2Capplication-level&pivots=python-mode-decorators)
- [Setup Azure Fuctions in VS Code](https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-vs-code-python?pivots=python-mode-decorators)
- CreateDatabse and Create_ImageStorage pyton files have some python libraries that need to be installed, that are not part of requirements.txt file. You will have to run them through the cmd or create anoter requirements file.
- The data used for books is generated from ChatGPT and is sotred in books.josn file, you can change the data according to your needs and push it to DB as needed vai CreateDatabse file.
- You will need to add the URL and Keys for you Azure resouces in an environment file or add to your env variables.
Additional Infomation
This project is based on the ideas/instructions from https://learntocloud.guide/phase2/
