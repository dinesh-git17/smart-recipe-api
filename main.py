from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Table,
    ForeignKey,
    Text,
    Float,
)
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.ext.declarative import declarative_base
import uvicorn

# Custom logger and secret configuration
from mylogger import logger

templates = Jinja2Templates(directory="templates")

# Database configuration: using SQLite for simplicity.
# IMPORTANT: If you see "no such column: recipes.rating", delete recipes.db so that the new schema is created.
DATABASE_URL = "sqlite:///./recipes.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Association table for many-to-many relationship between recipes and ingredients.
recipe_ingredient = Table(
    "recipe_ingredient",
    Base.metadata,
    Column("recipe_id", Integer, ForeignKey("recipes.id"), primary_key=True),
    Column("ingredient_id", Integer, ForeignKey("ingredients.id"), primary_key=True),
)


class Recipe(Base):
    __tablename__ = "recipes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)
    rating = Column(Float, nullable=True)
    ingredients = relationship(
        "Ingredient", secondary=recipe_ingredient, back_populates="recipes"
    )


class Ingredient(Base):
    __tablename__ = "ingredients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    recipes = relationship(
        "Recipe", secondary=recipe_ingredient, back_populates="ingredients"
    )


# Create the database tables.
Base.metadata.create_all(bind=engine)


# Pydantic models with examples (using new Pydantic V2 keys)
class IngredientBase(BaseModel):
    name: str

    class Config:
        json_schema_extra = {"example": {"name": "Tomato"}}


class IngredientCreate(IngredientBase):
    pass


class IngredientOut(IngredientBase):
    id: int

    class Config:
        from_attributes = True


class RecipeBase(BaseModel):
    title: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    rating: Optional[float] = None

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Spaghetti Bolognese",
                "description": "A classic Italian pasta dish",
                "instructions": "Boil pasta. Prepare sauce. Combine and serve.",
                "rating": 4.5,
            }
        }


class RecipeCreate(RecipeBase):
    ingredient_names: List[str] = []


class RecipeOut(RecipeBase):
    id: int
    ingredients: List[IngredientOut] = []

    class Config:
        from_attributes = True


# Dependency to get DB session.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI(
    title="Smart Recipe API",
    description="A RESTful API for managing and discovering recipes. Use /help for a getting-started guide.",
    version="1.0.0",
)


@app.on_event("startup")
def startup_event():
    logger.info("Smart Recipe API has started!")
    logger.info("Visit http://127.0.0.1:8000/ for the welcome page with instructions.")
    logger.info("Visit http://127.0.0.1:8000/docs for interactive API docs.")
    logger.info("Visit http://127.0.0.1:8000/redoc for alternative documentation.")


# Welcome endpoint: returns a simple HTML welcome message.
@app.get(
    "/",
    response_class=HTMLResponse,
    summary="Welcome Page",
    description="Displays a welcome page with instructions.",
)
def read_root(request: Request):
    content = """
    <html>
      <head><title>Smart Recipe API - Welcome</title></head>
      <body style="font-family: 'Segoe UI', sans-serif; background-color: #f5f5f5; text-align: center; padding-top: 50px;">
        <h1>Welcome to the Smart Recipe API! 🍲</h1>
        <p>Manage and discover delicious recipes with ease.</p>
        <p>Visit /docs for interactive API docs, /redoc for alternative docs, and /help for a getting started guide.</p>
      </body>
    </html>
    """
    return HTMLResponse(content=content)


# Help endpoint: returns a JSON guide.
@app.get(
    "/help",
    summary="Getting Started Guide",
    description="Provides sample API calls and instructions to use the API.",
)
def get_help():
    help_text = {
        "Endpoints": {
            "GET /recipes/": "Retrieve a list of recipes.",
            "POST /recipes/": "Create a new recipe. (Requires JSON payload.)",
            "GET /recipes/{recipe_id}": "Retrieve details of a specific recipe.",
            "PUT /recipes/{recipe_id}": "Update an existing recipe.",
            "DELETE /recipes/{recipe_id}": "Delete a recipe.",
            "GET /help": "View this help message.",
        },
        "Sample POST Payload for /recipes/": {
            "title": "Spaghetti Bolognese",
            "description": "A classic Italian pasta dish",
            "instructions": "Boil pasta. Prepare sauce. Combine and serve.",
            "rating": 4.5,
            "ingredient_names": [
                "Spaghetti",
                "Tomato",
                "Ground Beef",
                "Onion",
                "Garlic",
            ],
        },
    }
    return help_text


@app.post(
    "/recipes/",
    response_model=RecipeOut,
    summary="Create Recipe",
    description="Creates a new recipe along with its ingredients. If an ingredient doesn't exist, it will be created.",
)
def create_recipe(recipe: RecipeCreate, db: Session = Depends(get_db)):
    try:
        db_recipe = Recipe(
            title=recipe.title,
            description=recipe.description,
            instructions=recipe.instructions,
            rating=recipe.rating,
        )
        for ingredient_name in recipe.ingredient_names:
            ingredient = (
                db.query(Ingredient).filter(Ingredient.name == ingredient_name).first()
            )
            if not ingredient:
                ingredient = Ingredient(name=ingredient_name)
            db_recipe.ingredients.append(ingredient)
        db.add(db_recipe)
        db.commit()
        db.refresh(db_recipe)
        return db_recipe
    except Exception as e:
        logger.error(f"Error creating recipe: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error creating recipe. Please check the server logs for details.",
        )


@app.get(
    "/recipes/",
    response_model=List[RecipeOut],
    summary="List Recipes",
    description="Retrieves a list of recipes with optional pagination.",
)
def read_recipes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    try:
        recipes = db.query(Recipe).offset(skip).limit(limit).all()
        return recipes
    except Exception as e:
        logger.error(f"Error reading recipes: {e}")
        raise HTTPException(
            status_code=500, detail="Error retrieving recipes. Please try again later."
        )


@app.get(
    "/recipes/{recipe_id}",
    response_model=RecipeOut,
    summary="Get Recipe",
    description="Retrieve details for a specific recipe by its ID.",
)
def read_recipe(recipe_id: int, db: Session = Depends(get_db)):
    try:
        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if recipe is None:
            raise HTTPException(status_code=404, detail="Recipe not found")
        return recipe
    except Exception as e:
        logger.error(f"Error retrieving recipe {recipe_id}: {e}")
        raise HTTPException(
            status_code=500, detail="Error retrieving recipe. Please try again later."
        )


@app.put(
    "/recipes/{recipe_id}",
    response_model=RecipeOut,
    summary="Update Recipe",
    description="Update an existing recipe by its ID.",
)
def update_recipe(recipe_id: int, recipe: RecipeCreate, db: Session = Depends(get_db)):
    try:
        db_recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if db_recipe is None:
            raise HTTPException(status_code=404, detail="Recipe not found")
        db_recipe.title = recipe.title
        db_recipe.description = recipe.description
        db_recipe.instructions = recipe.instructions
        db_recipe.rating = recipe.rating
        db_recipe.ingredients = []
        for ingredient_name in recipe.ingredient_names:
            ingredient = (
                db.query(Ingredient).filter(Ingredient.name == ingredient_name).first()
            )
            if not ingredient:
                ingredient = Ingredient(name=ingredient_name)
            db_recipe.ingredients.append(ingredient)
        db.commit()
        db.refresh(db_recipe)
        return db_recipe
    except Exception as e:
        logger.error(f"Error updating recipe {recipe_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Error updating recipe. Please try again later."
        )


@app.delete(
    "/recipes/{recipe_id}",
    summary="Delete Recipe",
    description="Delete a recipe by its ID.",
)
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
    try:
        db_recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if db_recipe is None:
            raise HTTPException(status_code=404, detail="Recipe not found")
        db.delete(db_recipe)
        db.commit()
        return {"detail": "Recipe deleted"}
    except Exception as e:
        logger.error(f"Error deleting recipe {recipe_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Error deleting recipe. Please try again later."
        )


if __name__ == "__main__":
    uvicorn.run("explore_db:app", host="127.0.0.1", port=8000, reload=True)
