# Books API Fuctions App
### Description
•	This is API that provides books data for a few books in json format.
•	The API has three Endpoints:
o	Home Page - https://thebooksapi.azurewebsites.net/home
o	All books - https://thebooksapi.azurewebsites.net/allbooks
o	Books in given genre - https://thebooksapi.azurewebsites.net/getbooksbygenre/{genre_name}
•	This API is written in Python using the Azure Python SDK.
•	It uses the following Azure Resouces:
o	Azure Fuctions: These doe do the heaving Lifting of getting the data from DB and return the Json.
o	Azure Cosmos DB: Stores the books data in NoSQL DB.
o	Azure Blob Storage: Stores the Cover images for the books.
### Setup
•	An Azure Account with Subscription enabled is needed.
•	I have used VS Code for this project.
•	Instructions realted to Azure Fuctions: Azure Functions Python developer guide
•	Setup Azure Fuctions in VS Code
•	CreateDatabse and Create_ImageStorage pyton files have some python libraries that need to be installed, that are not part of requirements.txt file. You will have to run them through the cmd or create anoter requirements file.
•	The data used for books is generated from ChatGPT and is sotred in books.josn file, you can change the data according to your needs and push it to DB as needed vai CreateDatabse file.
•	You will need to add the URL and Keys for you Azure resouces in an environment file or add to your env variables.
Additional Infomation
This project is based on the ideas/instructions from https://learntocloud.guide/phase2/
