# Books API Fuctions App
### Description
- This is API that provides books data for a few books in json format.
-	My API has the following Endpoints:
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

### Installation
- Fork the repository to you local folder.
- Setup and activate Virtual Environment, instructions here: https://www.freecodecamp.org/news/how-to-setup-virtual-environments-in-python/
- Once the venv has been setup run via your command promt:
  ```
  pip install -r requirements.txt
  ```
- **DO NOT RUN pip freeze > requirements.txt** as this may cause an issue when you deploy the function to Azure. As this command with add **pywin32** to the requirements.txt which could cause issues when depyoing. Ref: (Troubleshoot Python errors in Azure Functions)[https://learn.microsoft.com/en-us/azure/azure-functions/recover-python-functions?tabs=vscode%2Cbash&pivots=python-mode-decorators#the-package-supports-only-windows-and-macos-platforms]

Additional Infomation
This project is based on the ideas/instructions from https://learntocloud.guide/phase2/
