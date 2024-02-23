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
- Once the venv has been setup run via your Terminal:
  ```
  pip install -r requirements.txt
  ```
- **DO NOT RUN pip freeze > requirements.txt** as this may cause an issue when you deploy the function to Azure. As this command with add **pywin32** to the requirements.txt which could cause issues when depyoing. Ref: [Troubleshoot Python errors in Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/recover-python-functions?tabs=vscode%2Cbash&pivots=python-mode-decorators#the-package-supports-only-windows-and-macos-platforms)
- You will now need to install Azure CLI: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli
- Once CLI is installed run the following command in you VS Code Terminal:
  ```az login```
  You will now be prompted to login to you Azure Account with the browser.
- Run indvidual python files need to be run as follows:
    - **create_database.py:**This file will create the CosmosDB Account, Database and Container in you Azure Account. This will also insert the sample data for books from books.json file.
        - **Ensure to rename the Cosmos DB Account as Globally unique.** Also this will create a Free-tier account for CosmosDB, you only are allowed onee Free Trie CosmosDB accout per Azure account, please delete or comment enable_free_tier property from                         create_database_account fuction.
               

Additional Infomation
This project is based on the ideas/instructions from https://learntocloud.guide/phase2/
