**Organization Management Service**
A multi-tenant backend service designed to manage organization accounts, adhering to the requirements of the Backend Intern Assignment.
The service is built using the FastAPI framework (Python) and uses MongoDB to implement a Schema-Based Multi-Tenancy architecture.

**Core Features**
RESTful API: Complete set of CRUD endpoints for Organization management (/org/create, /org/get, /org/update, /org/delete).
Authentication: Secure Admin Login (/admin/login) using JWT (JSON Web Tokens).
Multi-Tenancy: Each organization receives a dedicated, isolated collection in the Master Database (pattern: org_<organization_name>).
Security: Passwords are securely hashed using the bcrypt algorithm.

**Project Architecture**
The service uses a centralized Master Database to store global metadata while achieving data separation by creating an isolated collection for each tenant.

**Follow these steps to set up and run the application locally on a MacBook.**
Prerequisites
Python 3.11+: Installed on your system.
MongoDB: A running instance (local on mongodb://localhost:27017 or a MongoDB Atlas URI).
Git: Installed for cloning the repository.

1. Clone the Repository
Clone the project and navigate into the directory:
git clone https://github.com/revakudchadkar/organization-management-service.git
cd organization-management-service

2. Create and Activate Virtual Environment
Create an isolated environment for dependencies:
python3 -m venv venv
source venv/bin/activate

3. Install Dependencies
Install all necessary Python packages:
pip install -r requirements.txt
# OR, if requirements.txt is not yet generated:
pip install fastapi uvicorn motor 'pydantic[email]' passlib[bcrypt] python-jose[cryptography] pydantic-settings

4. Configure Application Settings (Important!)
Open the config.py file and verify or update the following values:
MONGO_URI: Ensure this points to your running MongoDB instance.
SECRET_KEY: Replace the placeholder with a long, randomly generated secret string for JWT signing.

5. Run the Server
Start the application using the Uvicorn ASGI server:
uvicorn main:app --reload
The server will be accessible at: http://127.0.0.1:8000

**Follow these steps to set up and run the application locally on Windows **
1. Prerequisites (Installation)
You will need the following software installed on your Windows machine:
Python 3.11+:
Download the installer from the official Python website.
Crucially, during installation, ensure you check the box that says "Add python.exe to PATH". This allows you to use python and pip from the Command Prompt or PowerShell.
MongoDB:
Download and install MongoDB Community Server. Use the default settings for installation.
Install MongoDB Compass (the graphical client) to easily check your database collections later.

2. Project Preparation
Open Command Prompt (CMD) or PowerShell.
Clone the Repository: Navigate to the folder where you want to keep your project (e.g., C:\dev\) and clone your project:
git clone https://github.com/revakudchadkar/organization-management-service.git
cd organization-management-service
Start MongoDB: Ensure the MongoDB service is running in the background. (Usually, this is done automatically after installation, but you may need to start it via the Windows Services Manager if it's not running).

3. Create and Activate Virtual Environment
A virtual environment is essential to keep project dependencies isolated.
Create the Virtual Environment:
python -m venv venv
Activate the Virtual Environment:

For Command Prompt (CMD):
venv\Scripts\activate

For PowerShell:
.\venv\Scripts\Activate.ps1
(You should see (venv) appear at the start of your command prompt, indicating activation.)

4. Install Dependencies
Install all necessary Python packages using the pip command. Since we are using Windows, we do not need the quotes for the packages with extras, but using them is safe:
pip install fastapi uvicorn motor 'pydantic[email]' 'passlib[bcrypt]' 'python-jose[cryptography]' pydantic-settings
(If you have a requirements.txt file, you can simply use pip install -r requirements.txt)

5. Configure and Run the Application
Configure Settings:
Open the config.py file in a text editor.
Verify the MONGO_URI (the default mongodb://localhost:27017 should work if MongoDB is running locally).
CRITICALLY, change the SECRET_KEY to a long, random string.

Run the Server: Start the FastAPI application using Uvicorn:
uvicorn main:app --reload

6. Verification
You will see a message in the console indicating the server has started: Uvicorn running on http://127.0.0.1:8000
Open your browser and navigate to http://127.0.0.1:8000/docs to access the Swagger UI and begin testing your API endpoints.


API Documentation and Testing
Access the interactive documentation (Swagger UI) to test all endpoints:
API Docs URL: http://127.0.0.1:8000/docs
Key Testing Flow
Create Organization (POST /org/create): Create a new organization, which verifies collection creation and admin setup.
Admin Login (POST /admin/login): Log in and copy the returned JWT token.
Authorize: Use the JWT token in the "Authorize" button on the Swagger UI page to unlock the secured endpoints.
Test Secured Endpoints: Verify that PUT /org/update and DELETE /org/delete only work with the correct, authorized admin user.


