from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
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

# Import our custom logger and secret configuration
from mylogger import logger


templates = Jinja2Templates(directory="templates")

# Database configuration: using SQLite for simplicity.
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


# Welcome endpoint: returns a visually pleasing HTML welcome page.
@app.get(
    "/",
    response_class=HTMLResponse,
    summary="Welcome Page",
    description="Displays a welcome page with instructions.",
)
def read_root(request: Request):
    return templates.TemplateResponse("welcome.html", {"request": request})


# Help endpoint: renders the Getting Started Guide from a template.
@app.get(
    "/help",
    response_class=HTMLResponse,
    summary="Getting Started Guide",
    description="Provides a guide on how to use the API.",
)
def help_page(request: Request):
    return templates.TemplateResponse("help.html", {"request": request})


@app.post(
    "/recipes/",
    response_model=RecipeOut,
    summary="Create Recipe",
    description="Creates a new recipe along with its ingredients. If an ingredient doesn't exist, it will be created.",
)
def create_recipe(recipe: RecipeCreate, db: Session = Depends(get_db)):
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


@app.get(
    "/recipes/",
    response_model=List[RecipeOut],
    summary="List Recipes",
    description="Retrieves a list of recipes with optional pagination.",
)
def read_recipes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    recipes = db.query(Recipe).offset(skip).limit(limit).all()
    return recipes


@app.get(
    "/recipes/{recipe_id}",
    response_model=RecipeOut,
    summary="Get Recipe",
    description="Retrieve details for a specific recipe by its ID.",
)
def read_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@app.put(
    "/recipes/{recipe_id}",
    response_model=RecipeOut,
    summary="Update Recipe",
    description="Update an existing recipe by its ID.",
)
def update_recipe(recipe_id: int, recipe: RecipeCreate, db: Session = Depends(get_db)):
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


@app.delete(
    "/recipes/{recipe_id}",
    summary="Delete Recipe",
    description="Delete a recipe by its ID.",
)
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
    db_recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if db_recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    db.delete(db_recipe)
    db.commit()
    return {"detail": "Recipe deleted"}


if __name__ == "__main__":
    uvicorn.run("explore_db:app", host="127.0.0.1", port=8000, reload=True)
