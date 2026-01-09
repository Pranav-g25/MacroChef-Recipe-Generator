"""
Interactive Recipe Configuration Generator
Run this script to create recipe_config.json with dropdown menus
"""

import json

def load_json(filename):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except:
        return {}

def display_menu(title, options, allow_skip=True):
    """Display a numbered menu and return the selected option."""
    print(f"\n{'='*50}")
    print(f" {title}")
    print('='*50)

    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")

    if allow_skip:
        print(f"  0. Skip / None")

    print()

    while True:
        choice = input("Enter number (or press Enter to skip): " if allow_skip else "Enter number: ").strip()

        if choice == "" and allow_skip:
            return None

        # Try as number first
        try:
            choice_num = int(choice)
            if allow_skip and choice_num == 0:
                return None
            if 1 <= choice_num <= len(options):
                return options[choice_num - 1]
            print(f"Invalid choice. Enter 1-{len(options)}" + (" or 0 to skip." if allow_skip else "."))
        except ValueError:
            print(f"Invalid input. Enter a number 1-{len(options)}" + (" or 0 to skip." if allow_skip else "."))

def get_text_input(prompt, allow_empty=True):
    """Get text input from user."""
    print(f"\n{prompt}")
    if allow_empty:
        print("(Press Enter to skip)")
    value = input("> ").strip()
    return value if value else None

def main():
    print("\n" + "="*60)
    print("   MACROCHEF RECIPE CONFIGURATION GENERATOR")
    print("="*60)

    # Load databases
    custom_recipes = load_json("custom_recipe_bank.json")
    side_dishes = load_json("side_dish_db.json")
    carbs = load_json("carb_db.json")

    # Extract options from databases
    side_dish_options = list(side_dishes.keys())
    carb_options = list(carbs.keys())

    # Parse custom recipes to extract base dishes, proteins, carbs, sauces, dressings
    salad_bases = set()
    chinese_bases = set()
    sandwich_bases = set()
    proteins_salad = set()
    proteins_chinese = set()
    proteins_sandwich = set()
    dressings = set()
    sauces = set()
    carb_choices_chinese = set()

    for key in custom_recipes.keys():
        if "Salad" in key:
            # Parse: "C01-B Salad Meal (Paneer, Vinaigrette)"
            base = key.split(" (")[0]
            salad_bases.add(base)
            if "(" in key:
                params = key.split("(")[1].rstrip(")").split(", ")
                if len(params) >= 1:
                    proteins_salad.add(params[0])
                if len(params) >= 2:
                    dressings.add(params[1])
        elif "Chinese" in key:
            base = key.split(" (")[0]
            chinese_bases.add(base)
            if "(" in key:
                params = key.split("(")[1].rstrip(")").split(", ")
                if len(params) >= 1:
                    proteins_chinese.add(params[0])
                if len(params) >= 2:
                    carb_choices_chinese.add(params[1])
        elif "Sandwich" in key:
            base = key.split(" (")[0]
            sandwich_bases.add(base)
            if "(" in key:
                params = key.split("(")[1].rstrip(")").split(", ")
                if len(params) >= 1:
                    proteins_sandwich.add(params[0])
                if len(params) >= 2:
                    sauces.add(params[1])

    config = {}

    # Step 1: Select Customer Plan
    plan_descriptions = [
        "SUB - Subscription plan (3 category ingredient list)",
        "DEMO - Demo plan (5 category ingredient list)"
    ]
    plan = display_menu("SELECT CUSTOMER PLAN", plan_descriptions, allow_skip=False)
    config["customer_plan"] = plan.split(" - ")[0]

    # Step 2: Select Mode
    modes = ["prefab", "custom_prefab", "full_custom"]
    mode_descriptions = [
        "prefab - LLM generates recipe from scratch",
        "custom_prefab - Use pre-written SOP from recipe bank",
        "full_custom - Fully custom request"
    ]
    mode = display_menu("SELECT MODE", mode_descriptions, allow_skip=False)
    config["mode"] = mode.split(" - ")[0]

    if config["mode"] == "prefab":
        # Prefab mode - free text dish title
        print("\n" + "-"*50)
        print(" PREFAB MODE: Generate recipe from scratch")
        print("-"*50)

        config["dish_title"] = get_text_input("Enter dish title (e.g., 'Shrimp Curry', 'Paneer Bhurji'):", allow_empty=False)

        # Serving size
        serving = get_text_input("Enter serving size (1-4):", allow_empty=False)
        config["serving_size"] = serving

        # Side dish
        config["side_title"] = display_menu("SELECT SIDE DISH", side_dish_options)

        # Carb side
        config["carb_side_title"] = display_menu("SELECT CARB SIDE", carb_options)

    elif config["mode"] == "custom_prefab":
        # Custom prefab mode - select from recipe bank
        print("\n" + "-"*50)
        print(" CUSTOM PREFAB MODE: Use pre-written recipe")
        print("-"*50)

        # Select dish type
        dish_types = ["Salad Meal", "Chinese Bowl", "Sandwich"]
        dish_type = display_menu("SELECT DISH TYPE", dish_types, allow_skip=False)

        if dish_type == "Salad Meal":
            config["dish_title"] = list(salad_bases)[0] if salad_bases else "C01-B Salad Meal"
            config["protein_choice"] = display_menu("SELECT PROTEIN", list(proteins_salad), allow_skip=False)
            config["dressing_choice"] = display_menu("SELECT DRESSING", list(dressings), allow_skip=False)

        elif dish_type == "Chinese Bowl":
            config["dish_title"] = list(chinese_bases)[0] if chinese_bases else "C02-B Chinese Bowl"
            config["protein_choice"] = display_menu("SELECT PROTEIN", list(proteins_chinese), allow_skip=False)
            config["carb_choice"] = display_menu("SELECT CARB", list(carb_choices_chinese), allow_skip=False)

        elif dish_type == "Sandwich":
            config["dish_title"] = list(sandwich_bases)[0] if sandwich_bases else "C03-B Sandwich"
            config["protein_choice"] = display_menu("SELECT PROTEIN", list(proteins_sandwich), allow_skip=False)
            config["sauce_choice"] = display_menu("SELECT SAUCE", list(sauces), allow_skip=False)

        # Serving size
        serving = get_text_input("Enter serving size (1-4):", allow_empty=False)
        config["serving_size"] = serving

        # Side dish (optional)
        config["side_title"] = display_menu("SELECT SIDE DISH (Optional)", side_dish_options)

    elif config["mode"] == "full_custom":
        # Full custom mode
        print("\n" + "-"*50)
        print(" FULL CUSTOM MODE: Enter your custom request")
        print("-"*50)

        config["full_custom_request"] = get_text_input("Enter your full custom recipe request:", allow_empty=False)

    # Common optional fields
    print("\n" + "-"*50)
    print(" OPTIONAL SETTINGS")
    print("-"*50)

    config["customization_string"] = get_text_input("Any customization? (e.g., 'Make it spicy', 'No onion'):")
    config["translation_lang"] = get_text_input("Translation language? (e.g., 'Hinglish with devnagri script'):")

    # Save config
    with open("recipe_config.json", "w") as f:
        json.dump(config, f, indent=2)

    print("\n" + "="*60)
    print(" Configuration saved to recipe_config.json")
    print("="*60)
    print("\nYour configuration:")
    print(json.dumps(config, indent=2))
    print("\nNow run: python main.py > prompt.txt")

if __name__ == "__main__":
    main()
