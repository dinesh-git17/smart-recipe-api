import requests
import json
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()

# Base URL for the API (adjust if needed)
BASE_URL = "http://127.0.0.1:8000"


def get_welcome():
    """Retrieve and display the welcome message as plain text."""
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            console.print(
                Panel(
                    "[bold green]Welcome endpoint is up![/bold green]\nAccess /docs for interactive API docs.",
                    title="Welcome",
                    border_style="green",
                )
            )
        else:
            console.print(
                Panel(
                    f"[bold red]Error: Welcome endpoint returned status code {response.status_code}[/bold red]",
                    title="Error",
                    border_style="red",
                )
            )
    except Exception as e:
        console.print(
            Panel(
                f"[bold red]Exception calling welcome endpoint: {e}[/bold red]",
                title="Error",
                border_style="red",
            )
        )


def get_help():
    """Retrieve and display the help page text."""
    try:
        response = requests.get(f"{BASE_URL}/help")
        try:
            data = response.json()
            help_text = json.dumps(data, indent=2)
        except Exception:
            help_text = response.text
        console.print(
            Panel(
                "[bold blue]Help Information:[/bold blue]\n" + help_text,
                title="Help",
                border_style="blue",
            )
        )
    except Exception as e:
        console.print(
            Panel(
                f"[bold red]Exception calling help endpoint: {e}[/bold red]",
                title="Error",
                border_style="red",
            )
        )


def list_recipes():
    """Retrieve a list of recipes and display them in a Rich table."""
    try:
        response = requests.get(f"{BASE_URL}/recipes/")
        try:
            recipes = response.json()
        except Exception as e:
            console.print(
                Panel(
                    f"[bold red]Error parsing JSON: {e}[/bold red]",
                    title="Error",
                    border_style="red",
                )
            )
            return

        if not isinstance(recipes, list) or not recipes:
            console.print(
                Panel("[bold yellow]No recipes found.[/bold yellow]", title="Recipes")
            )
            return

        table = Table(title="Recipes", box=box.DOUBLE_EDGE)
        table.add_column("ID", justify="right", style="cyan", no_wrap=True)
        table.add_column("Title", style="magenta")
        table.add_column("Rating", justify="right", style="green")

        for recipe in recipes:
            if isinstance(recipe, dict):
                rid = str(recipe.get("id", ""))
                title = recipe.get("title", "")
                rating = str(recipe.get("rating", "N/A"))
            else:
                rid = str(recipe)
                title = str(recipe)
                rating = "N/A"
            table.add_row(rid, title, rating)

        console.print(table)
    except Exception as e:
        console.print(
            Panel(
                f"[bold red]Error listing recipes: {e}[/bold red]",
                title="Error",
                border_style="red",
            )
        )


def create_recipe_interactive():
    """Interactively create a new recipe by asking the user for input."""
    console.print("[bold yellow]Enter the recipe details:[/bold yellow]")
    title = input("Title: ").strip()
    description = input("Description: ").strip()
    instructions = input("Instructions: ").strip()
    rating_input = input("Rating (e.g., 4.5): ").strip()
    try:
        rating = float(rating_input) if rating_input else None
    except ValueError:
        console.print(
            Panel(
                "[bold red]Invalid rating entered. Setting rating to None.[/bold red]",
                border_style="red",
            )
        )
        rating = None
    ingredients_str = input("Ingredient names (separate by commas): ").strip()
    ingredient_names = [
        ing.strip() for ing in ingredients_str.split(",") if ing.strip()
    ]

    payload = {
        "title": title,
        "description": description if description else None,
        "instructions": instructions if instructions else None,
        "rating": rating,
        "ingredient_names": ingredient_names,
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(
            f"{BASE_URL}/recipes/", headers=headers, data=json.dumps(payload)
        )
        if response.status_code == 200:
            recipe = response.json()
            console.print(
                Panel(
                    "[bold green]Created Recipe:[/bold green]\n"
                    + json.dumps(recipe, indent=2),
                    title="New Recipe",
                    border_style="green",
                )
            )
            return recipe.get("id")
        else:
            console.print(
                Panel(
                    "[bold red]Error creating recipe:[/bold red]\n" + response.text,
                    title="Error",
                    border_style="red",
                )
            )
            return None
    except Exception as e:
        console.print(
            Panel(
                f"[bold red]Exception creating recipe: {e}[/bold red]",
                title="Error",
                border_style="red",
            )
        )
        return None


def get_recipe(recipe_id):
    """Retrieve and display details for a specific recipe."""
    try:
        response = requests.get(f"{BASE_URL}/recipes/{recipe_id}")
        if response.status_code == 200:
            recipe = response.json()
            console.print(
                Panel(
                    "[bold green]Details for Recipe ID "
                    + str(recipe_id)
                    + ":[/bold green]\n"
                    + json.dumps(recipe, indent=2),
                    title="Recipe Details",
                    border_style="green",
                )
            )
        else:
            console.print(
                Panel(
                    "[bold red]Error retrieving recipe "
                    + str(recipe_id)
                    + ":[/bold red]\n"
                    + response.text,
                    title="Error",
                    border_style="red",
                )
            )
    except Exception as e:
        console.print(
            Panel(
                f"[bold red]Exception retrieving recipe: {e}[/bold red]",
                title="Error",
                border_style="red",
            )
        )


def update_recipe(recipe_id):
    """Update an existing recipe by prompting the user for new details."""
    console.print("[bold yellow]Enter updated details for the recipe:[/bold yellow]")
    title = input("Title: ").strip()
    description = input("Description: ").strip()
    instructions = input("Instructions: ").strip()
    rating_input = input("Rating (e.g., 4.5): ").strip()
    try:
        rating = float(rating_input) if rating_input else None
    except ValueError:
        console.print(
            Panel(
                "[bold red]Invalid rating entered. Setting rating to None.[/bold red]",
                border_style="red",
            )
        )
        rating = None
    ingredients_str = input("Ingredient names (separate by commas): ").strip()
    ingredient_names = [
        ing.strip() for ing in ingredients_str.split(",") if ing.strip()
    ]

    payload = {
        "title": title,
        "description": description if description else None,
        "instructions": instructions if instructions else None,
        "rating": rating,
        "ingredient_names": ingredient_names,
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.put(
            f"{BASE_URL}/recipes/{recipe_id}", headers=headers, data=json.dumps(payload)
        )
        if response.status_code == 200:
            updated_recipe = response.json()
            console.print(
                Panel(
                    "[bold green]Updated Recipe ID "
                    + str(recipe_id)
                    + ":[/bold green]\n"
                    + json.dumps(updated_recipe, indent=2),
                    title="Updated Recipe",
                    border_style="green",
                )
            )
        else:
            console.print(
                Panel(
                    "[bold red]Error updating recipe "
                    + str(recipe_id)
                    + ":[/bold red]\n"
                    + response.text,
                    title="Error",
                    border_style="red",
                )
            )
    except Exception as e:
        console.print(
            Panel(
                f"[bold red]Exception updating recipe: {e}[/bold red]",
                title="Error",
                border_style="red",
            )
        )


def delete_recipe(recipe_id):
    """Delete a recipe and display the response."""
    try:
        response = requests.delete(f"{BASE_URL}/recipes/{recipe_id}")
        if response.status_code == 200:
            result = response.json()
            console.print(
                Panel(
                    "[bold green]Deleted Recipe ID "
                    + str(recipe_id)
                    + ":[/bold green]\n"
                    + json.dumps(result, indent=2),
                    title="Deleted",
                    border_style="green",
                )
            )
        else:
            console.print(
                Panel(
                    "[bold red]Error deleting recipe "
                    + str(recipe_id)
                    + ":[/bold red]\n"
                    + response.text,
                    title="Error",
                    border_style="red",
                )
            )
    except Exception as e:
        console.print(
            Panel(
                f"[bold red]Exception deleting recipe: {e}[/bold red]",
                title="Error",
                border_style="red",
            )
        )


def show_menu():
    """Display an interactive menu and return the user's choice."""
    menu = """
[bold cyan]Smart Recipe API Client Menu[/bold cyan]
[bold yellow]1.[/bold yellow] Add a new recipe
[bold yellow]2.[/bold yellow] View a recipe by ID
[bold yellow]3.[/bold yellow] Update a recipe by ID
[bold yellow]4.[/bold yellow] Delete a recipe by ID
[bold yellow]5.[/bold yellow] List all recipes
[bold yellow]6.[/bold yellow] Exit
    """
    console.print(Panel(menu, title="Main Menu", border_style="magenta"))
    choice = input("Enter your choice (1-6): ").strip()
    return choice


def main():
    console.print(
        Panel(
            "[bold blue]Welcome to the Smart Recipe API Client[/bold blue]",
            title="Smart Recipe API Client",
            border_style="blue",
        )
    )
    while True:
        choice = show_menu()
        if choice == "1":
            console.print("[bold yellow]Creating a new recipe...[/bold yellow]")
            recipe_id = create_recipe_interactive()
            if recipe_id:
                console.print(
                    "[bold green]Recipe created with ID: "
                    + str(recipe_id)
                    + "[/bold green]"
                )
        elif choice == "2":
            recipe_id = input("Enter Recipe ID to view: ").strip()
            if recipe_id.isdigit():
                get_recipe(int(recipe_id))
            else:
                console.print(
                    Panel(
                        "[bold red]Invalid ID entered.[/bold red]",
                        title="Error",
                        border_style="red",
                    )
                )
        elif choice == "3":
            recipe_id = input("Enter Recipe ID to update: ").strip()
            if recipe_id.isdigit():
                update_recipe(int(recipe_id))
            else:
                console.print(
                    Panel(
                        "[bold red]Invalid ID entered.[/bold red]",
                        title="Error",
                        border_style="red",
                    )
                )
        elif choice == "4":
            recipe_id = input("Enter Recipe ID to delete: ").strip()
            if recipe_id.isdigit():
                delete_recipe(int(recipe_id))
            else:
                console.print(
                    Panel(
                        "[bold red]Invalid ID entered.[/bold red]",
                        title="Error",
                        border_style="red",
                    )
                )
        elif choice == "5":
            list_recipes()
        elif choice == "6":
            console.print(
                Panel(
                    "[bold blue]Goodbye![/bold blue]", title="Exit", border_style="blue"
                )
            )
            break
        else:
            console.print(
                Panel(
                    "[bold red]Invalid choice. Please try again.[/bold red]",
                    title="Error",
                    border_style="red",
                )
            )
        console.print("\n" + "-" * 50 + "\n")


def create_recipe_interactive():
    """Interactively create a new recipe by prompting the user for details."""
    console.print("[bold yellow]Enter the details for your new recipe:[/bold yellow]")
    title = input("Title: ").strip()
    description = input("Description: ").strip()
    instructions = input("Instructions: ").strip()
    rating_input = input("Rating (e.g., 4.5): ").strip()
    try:
        rating = float(rating_input) if rating_input else None
    except ValueError:
        console.print(
            Panel(
                "[bold red]Invalid rating entered. Setting rating to None.[/bold red]",
                border_style="red",
            )
        )
        rating = None
    ingredients_str = input("Ingredient names (separate by commas): ").strip()
    ingredient_names = [
        ing.strip() for ing in ingredients_str.split(",") if ing.strip()
    ]

    payload = {
        "title": title,
        "description": description if description else None,
        "instructions": instructions if instructions else None,
        "rating": rating,
        "ingredient_names": ingredient_names,
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(
            f"{BASE_URL}/recipes/", headers=headers, data=json.dumps(payload)
        )
        if response.status_code == 200:
            recipe = response.json()
            console.print(
                Panel(
                    "[bold green]Created Recipe:[/bold green]\n"
                    + json.dumps(recipe, indent=2),
                    title="New Recipe",
                    border_style="green",
                )
            )
            return recipe.get("id")
        else:
            console.print(
                Panel(
                    "[bold red]Error creating recipe:[/bold red]\n" + response.text,
                    title="Error",
                    border_style="red",
                )
            )
            return None
    except Exception as e:
        console.print(
            Panel(
                f"[bold red]Exception creating recipe: {e}[/bold red]",
                title="Error",
                border_style="red",
            )
        )
        return None


if __name__ == "__main__":
    main()
