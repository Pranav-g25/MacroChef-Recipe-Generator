import jinja2
import pandas as pd
import json
import difflib
import math

class MacroChefGenerator:
    def __init__(self, template_file="macrochef_prompt.jinja"):
        self.loader = jinja2.FileSystemLoader(searchpath="./")
        self.env = jinja2.Environment(loader=self.loader)
        self.template = self.env.get_template(template_file)
        
        # 1. LOAD CSV & CREATE MASTER DOMAIN
        try:
            self.df_ingredients = pd.read_csv("ingredients.csv")
            self.master_ingredients = self.df_ingredients.to_string(index=False)
            
            # Flatten CSV
            raw_list = pd.melt(self.df_ingredients)['value'].dropna().unique().tolist()
            self.master_ingredient_domain = [str(x).strip() for x in raw_list]
            
            self.df_singleserve = pd.read_csv("single_serve_guidelines.csv")
            self.master_guidelines = self.df_singleserve.to_string(index=False)
            
        except Exception as e:
            print(f"CRITICAL ERROR LOADING CSV: {e}")
            self.master_ingredient_domain = []

        # 2. LOAD JSON DBs
        self.side_dish_db = self._load_json("side_dish_db.json")
        self.recipe_bank = self._load_json("custom_recipe_bank.json")
        self.carb_db = self._load_json("carb_db.json")
        self.abstract = "MacroChef: A nutrition aware private chef service for gym goers and fitness enthusiasts. Main USP: Just pay us X rupees a month per person and forget about \n" \
        "counting/tracking your macros as well buying groceries forever. Just update your daily/weekly or monthly cuisine/macro/calorific preference in our seamless and user-friendly app\n" \
        " and let our 'smart chefs' take care of it for you. Our chefs carry the highest quality ingredients sourced specifically for you on that day and preapre tasty, healthy and personalised meals\n" \
        " fresh in your own kitchen. This the startup that I am working to set up."

    def _load_json(self, filename):
        try:
            with open(filename, "r") as f: return json.load(f)
        except: return {}

    def _smart_match_ingredient(self, input_ing, master_list):
        input_clean = input_ing.lower().strip()
        for idx, master_item in enumerate(master_list):
            if master_item.lower().strip() == input_clean:
                return master_item, idx

        matches = difflib.get_close_matches(input_ing, master_list, n=1, cutoff=0.8)
        if matches:
            best_match = matches[0]
            return best_match, master_list.index(best_match)

        return None, -1

    def _generate_binary_vector(self, active_ingredients_list):
        master_len = len(self.master_ingredient_domain)
        if master_len == 0: return "[]"
            
        binary_vec = [0] * master_len
        matched_log = []
        unmatched_log = []

        for item in active_ingredients_list:
            matched_name, idx = self._smart_match_ingredient(item, self.master_ingredient_domain)
            if idx != -1:
                binary_vec[idx] = 1
                matched_log.append(f"{item} -> {matched_name}")
            else:
                unmatched_log.append(item)

        current_len = len(binary_vec)
        if current_len != master_len:
            print(f"CRITICAL ERROR: Vector Length Mismatch! Master: {master_len}, Generated: {current_len}")

        if unmatched_log:
            print(f" WARNING: Could not find these ingredients in Master CSV: {unmatched_log}")

        return str(binary_vec)

    def _get_side_lookup_key(self, serving_size_str):
        try:
            val = float(serving_size_str)
            floored_val = math.floor(val)
            if floored_val < 1: floored_val = 1
            return str(floored_val)
        except (ValueError, TypeError):
            return "1"

    def create_prompt(self, is_prefab=False, is_custom_prefab=False, is_customization=False, is_full_custom_request=False, **kwargs):
        
        vec_len = len(self.master_ingredient_domain)
        
        # Default Context
        context = {
            "abstract": self.abstract,
            "master_ingredient_list": self.master_ingredients,
            "master_single_serve_list": self.master_guidelines,
            "vector_length": vec_len,
            "is_prefab": is_prefab,
            "is_custom_prefab": is_custom_prefab,
            "is_full_custom_request": is_full_custom_request,
            "customization_string": kwargs.get("customization_string", "None"),
            "translation_lang": kwargs.get("translation_lang", None),
            # Default these to False/Empty to prevent leaking into wrong branches
            "is_side": False,
            "is_carbside": False 
        }

        # --- BRANCH 1: PRE-FAB (Generative) ---
        if is_prefab:
            context["dish_title"] = kwargs.get("dish_title")
            raw_serving_size = str(kwargs.get("serving_size", "1"))
            context["serving_size"] = raw_serving_size
            
            # A. SIDE DISH LOGIC
            side_title = kwargs.get("side_title")
            context["side_title"] = side_title
            
            if side_title and str(side_title).lower() != "none" and str(side_title).strip() != "":
                context["is_side"] = True
                side_db_key = self._get_side_lookup_key(raw_serving_size)
                dish_data = self.side_dish_db.get(side_title)
                
                if dish_data and side_db_key in dish_data:
                    context["side_dish_sop"] = dish_data[side_db_key]["sop"]
                    active_list = dish_data[side_db_key].get("active_ingredients", [])
                    context["side_ingredients_list"] = str(active_list)
                    context["side_ingredients_vector"] = self._generate_binary_vector(active_list)
                else:
                    context["side_dish_sop"] = "Standard Prep"
                    context["side_ingredients_list"] = "[]"
                    context["side_ingredients_vector"] = "[]"

            # B. CARB SIDE LOGIC (Explicitly for Pre-Fab)
            carb_title = kwargs.get("carb_side_title")
            if carb_title and str(carb_title).lower() != "none" and str(carb_title).strip() != "":
                context["is_carbside"] = True
                context["carb_side_title"] = carb_title
                
                carb_data = self.carb_db.get(carb_title)
                if carb_data:
                    context["carb_side_instructions"] = carb_data.get("sop", "Standard Prep")
                    carb_list = carb_data.get("active_ingredients", [])
                    context["carb_ingredients_list"] = str(carb_list)
                    context["carb_ingredients_vector"] = self._generate_binary_vector(carb_list)
                else:
                    context["carb_side_instructions"] = "Standard Boil"
                    context["carb_ingredients_list"] = "[]"
                    context["carb_ingredients_vector"] = "[]"

        # --- BRANCH 2: CUSTOM PRE-FAB (Strict Recipe Import) ---
        elif is_custom_prefab:
            base_title = kwargs.get("dish_title")
            protein_choice = kwargs.get("protein_choice", "")
            carb_choice = kwargs.get("carb_choice", "") # Used for Key Lookup ONLY
            sauce_choice = kwargs.get("sauce_choice", "")
            dressing_choice = kwargs.get("dressing_choice", "")
            
            raw_serving_size = str(kwargs.get("serving_size", "1"))
            context["serving_size"] = raw_serving_size
            context["dish_title"] = base_title
            context["protein_choice"] = protein_choice
            # We pass carb_choice just for display in the Dish Title if needed, 
            # BUT we do NOT trigger is_carbside logic.
            
            # A. KEY CONSTRUCTION
            lookup_key = base_title 
            if "Salad" in base_title:
                lookup_key = f"{base_title} ({protein_choice}, {dressing_choice})"
            elif "Chinese" in base_title:
                lookup_key = f"{base_title} ({protein_choice}, {carb_choice})"
            elif "Sandwich" in base_title:
                lookup_key = f"{base_title} ({protein_choice}, {sauce_choice})"
                
            # B. MAIN DISH LOOKUP (Carb ingredients are included here!)
            recipe_data = self.recipe_bank.get(lookup_key)
            if recipe_data and "1" in recipe_data:
                context["imported_recipe_sop"] = recipe_data["1"]["sop"]
                main_active_list = recipe_data["1"].get("active_ingredients", [])
                context["main_ingredients_list"] = str(main_active_list)
                context["main_ingredients_vector"] = self._generate_binary_vector(main_active_list)
            else:
                context["imported_recipe_sop"] = f"CRITICAL: Variant '{lookup_key}' not found."
                context["main_ingredients_list"] = "[]"
                context["main_ingredients_vector"] = "[]"
            
            # C. SIDE DISH LOOKUP (Optional independent side)
            side_title = kwargs.get("side_title")
            if side_title and str(side_title).lower() != "none" and str(side_title).strip() != "":
                context["is_side"] = True
                context["side_title"] = side_title
                side_db_key = self._get_side_lookup_key(raw_serving_size)
                side_data = self.side_dish_db.get(side_title)
                
                if side_data and side_db_key in side_data:
                    context["side_dish_sop"] = side_data[side_db_key]["sop"]
                    side_active_list = side_data[side_db_key].get("active_ingredients", [])
                    context["side_ingredients_list"] = str(side_active_list)
                    context["side_ingredients_vector"] = self._generate_binary_vector(side_active_list)
                else:
                    context["side_dish_sop"] = "Standard Preparation"
                    context["side_ingredients_list"] = "[]"
                    context["side_ingredients_vector"] = "[]"

        # --- BRANCH 3: FULL CUSTOM ---
        elif is_full_custom_request:
            context["full_custom_request"] = kwargs.get("full_custom_request", "")

        return self.template.render(context)

if __name__ == "__main__":
    generator = MacroChefGenerator()
    print(generator.create_prompt(
        
        #is_prefab=True,
        is_custom_prefab=True,
        #is_customization=True,
        #customization_string= "Make it spicy",
        dish_title="C02-B Chinese Bowl", 
        protein_choice="Orange Paneer",
        #dressing_choice="Vinaigrette",
        #sauce_choice="Spiced Red",
        #carb_choice="Noodles",
        carb_choice="Rice",
        #is_carbside = False,
        serving_size="4.5",
        #side_title= "Simple Caesar Salad",
        #carb_side_title="Roti",
        #translation_lang= "Hinglish with devnagri script",
    ))








