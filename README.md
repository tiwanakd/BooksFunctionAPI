# Books API Fuctions App

### Description
- This is API that provides books data for a few books in json format.
- The API has three Endpoints:
    - Home Page - https://thebooksapi.azurewebsites.net/home
    - All books - https://thebooksapi.azurewebsites.net/allbooks
    - Books in given genre - https://thebooksapi.azurewebsites.net/getbooksbygenre/{genre_name}
- This API is written in Python using the Azure Python SDK.
- It uses the following Azure Resouces:
    - **Azure Fuctions**: These doe do the heaving Lifting of getting the data from DB and return the Json.
    - **Azure Cosmos DB**: Stores the books data in NoSQL DB.
    - **Azure Blob Storage**: Stores the Cover images for the books.
 
  ### Setup
- I have used VS Code for this project.
- Instructions realted to Azure Fuctions: [Azure Functions Python developer guide](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python?tabs=asgi%2Capplication-level&pivots=python-mode-decorators)
- [Setup Azure Fuctions in VS Code](https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-vs-code-python?pivots=python-mode-decorators)

  
