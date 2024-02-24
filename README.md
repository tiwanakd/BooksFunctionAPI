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
    - Azure Fuctions: These are HTTP Trigger fuctions that do the heaving Lifting of getting the data from DB and return the Json.
    - Azure Cosmos DB: Stores the books data in NoSQL DB.
    - Azure Blob Storage: Stores the Cover images for the books.
  
### Setup
- An Azure Account with Subscription enabled is needed.
- I have used VS Code for this project.
- Instructions realted to Azure Fuctions: [Azure Functions Python developer guide](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python?tabs=asgi%2Capplication-level&pivots=python-mode-decorators)
- [Setup Azure Fuctions in VS Code](https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-vs-code-python?pivots=python-mode-decorators)

### Installation
- Fork the repository to your Account and Clone it to your Desktop.
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
- Setup Enviroment variables:
     - There are two main enviroment variables needed to create the required infrastructre for this project.
         - ```SUBSCRIPTION_ID```: You can get this ID from under your Subsriptions in your Azure Portal or Az CLI.
         - ```AZURE_USER_PRINCIPAL_NAME```: User Prinicpal name can be reterived from Microsoft Entra ID under your account.
         - Once you have these values, please add them your envinoment variables as per you system.
         - E.g. For windows CMD run the following command:
           ```
           setx SUBSCRIPTION_ID "Your Subsciprtion Key"
           ```
         - Ensure that your current active Subsription is set to your required Subcription ID, you can do this vai Az CLI:
         ```
         az account set --subscription <SubscriptionId>
         ```
            
- Run indvidual python files as follows:
    - **create_database.py:** This file will create the Resource Group, CosmosDB Account, Database and Container in you Azure Account. This will also insert the sample data for books from books.json file.
        - **Ensure to rename the Resource Group & Cosmos DB Account as Globally unique.** Also this will create a Free-tier account for CosmosDB, you are allowed only one Free Tier CosmosDB accout per Azure account, please delete or comment enable_free_tier property 
            from create_database_account fuction if Free Tier account is not needed. Once the required changes are made run the file via Terminal:
          ```
          python create_database.py
          ```
    - **create_imageStorage.py:** This file will create a Storage Account, Blob Container and upload the sample book coverimages to the container. Like CosmosDB, you will need to **pass a Globally unique name for the Stroage Account**. Now run:
        ```
        python create_imageStorage.py
        ```
- Now we are all set to work on our Azure Fuctions. You will need to have the following Azure Extension added to your VS Code:
    - Azure Account.
    - Azure Tools.
    - Azure Functions.
- Create an Azure Fuction in Azure Account either using the Azure Portal or via VS code as mentioned here: [Create the function app in Azure](https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-vs-code-python?pivots=python-mode-decorators#publish-the-project-to-azure)
- Once the Azure Fuction is created in Azure. We will need to connect Our CosmosDB Account to the Azure Fuction. Instructions here: [Connect Azure Functions to Azure Cosmos DB using Visual Studio Code](https://learn.microsoft.com/en-us/azure/azure-functions/functions-add-output-binding-cosmos-db-vs-code?tabs=isolated-process%2Cv1&pivots=programming-language-python)
- You should now be able to run Two of the Three main fuctions locally:
    - ```All_Books```: This fuctions will give all books that are currently the the Database.
    - ```Genre_Books```: This fuctions will give all books in a given genre.
    - To test this run the Azure Fuction locally type the follwing in your Terminal:
    ```
    func host start
    ```
- Now for the Third fuction ```Book_Summary```:
    - This function is created as BluePrint fuction in a different module ```summary_fuction.py```. Ref: [Blueprints](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python?tabs=asgi%2Capplication-level&pivots=python-mode-decorators#blueprints)
    - This function will give a 1-2 line AI Generated book summary for given book name using [OpenAI's text generation models](https://platform.openai.com/docs/guides/text-generation)
    - You will need to get the OperAI API key from here: https://platform.openai.com/api-keys
    - Once you have the API key, refer to the python documentation for this API: [Developer quickstart](https://platform.openai.com/docs/quickstart?context=python)
    - OPenAI Library should alredy be installed in your environment as part of requirements.txt file.
    - Follow the instructions here to [Setup your API key](https://platform.openai.com/docs/quickstart/step-2-set-up-your-api-key)
    - Once the API key has been setup you are all setup to run the this fuction by ```func host start```

- After Testing the fuctions locally you should be all set to deploy to Azure:
    - You can use VS Code to deploy the fuction: [Deploy the project to Azure](https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-vs-code-python?pivots=python-mode-decorators#deploy-the-project-to-azure) OR,
    - Run the following command:
    ```
    func azure functionapp publish <FunctionAppName>
    ```
                 
#### Additional Infomation
This project is based on the ideas/instructions from https://learntocloud.guide/phase2/
