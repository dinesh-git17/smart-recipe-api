SMART RECIPE API
================

Overview:
---------
The Smart Recipe API is a RESTful service built with FastAPI that allows users to manage and discover delicious recipes. The API supports standard CRUD operations for recipes, provides interactive documentation via Swagger UI and ReDoc, and includes helpful endpoints such as a Getting Started Guide (/help).

Features:
---------
- Create, read, update, and delete recipes.
- Manage ingredients and associate them with recipes.
- Interactive API documentation at /docs and /redoc.
- A visually pleasing welcome page with instructions.
- Detailed endpoint documentation with examples.
- Custom logging using a colorful, emoji-enhanced logger.
- Built-in Getting Started Guide at /help.

Setup:
------
1. Create a virtual environment and activate it:
   - On macOS/Linux:
       python3 -m venv env
       source env/bin/activate
   - On Windows:
       python -m venv env
       env\Scripts\activate

2. Install dependencies:
       pip install -r requirements.txt

   The requirements.txt includes:
       fastapi
       uvicorn
       sqlalchemy
       pydantic
       colorlog
       plotly
       pandas
       numpy
       matplotlib
       seaborn
       thefuzz[speedup]

3. Configure the API:
   - Create a file named secret.py in the project directory with your database credentials:
     
         DB_USER = "your_username"
         DB_PASS = "your_password"
         DB_HOST = "localhost"
         DB_PORT = "5432"
         DB_NAME = "recipes_db"

   - Ensure secret.py is added to your .gitignore.

4. Run the API:
   - In development mode, run:
         uvicorn explore_db:app --reload
   - This starts the API on http://127.0.0.1:8000

Usage:
------
- Welcome Page:
  Visit http://127.0.0.1:8000/ to see a visually pleasing welcome page with instructions.

- Interactive API Docs:
  Visit http://127.0.0.1:8000/docs for Swagger UI documentation.
  Visit http://127.0.0.1:8000/redoc for alternative API documentation.

- Getting Started Guide:
  Visit http://127.0.0.1:8000/help for a guide that provides sample API calls and instructions.

- Endpoints:
  • GET /recipes/        : Retrieve a list of recipes.
  • POST /recipes/       : Create a new recipe (requires a JSON payload).
  • GET /recipes/{id}    : Retrieve details of a specific recipe.
  • PUT /recipes/{id}    : Update an existing recipe.
  • DELETE /recipes/{id} : Delete a recipe.

- Sample POST Payload:
  {
      "title": "Spaghetti Bolognese",
      "description": "A classic Italian pasta dish",
      "instructions": "Boil pasta. Prepare sauce. Combine and serve.",
      "rating": 4.5,
      "ingredient_names": ["Spaghetti", "Tomato", "Ground Beef", "Onion", "Garlic"]
  }

Additional Notes:
-----------------
- The API uses FastAPI's automatic interactive documentation for easy testing.
- Custom logging is integrated to provide helpful startup messages.
- The API is built using a SQLite database for simplicity but can be switched to another DB by updating the DATABASE_URL.
- This project is a portfolio piece that demonstrates advanced REST API development skills using FastAPI, SQLAlchemy, and Pydantic.


