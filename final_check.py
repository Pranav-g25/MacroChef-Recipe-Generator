import jinja2
import pandas as pd
import json

class FinalCheckGenerator:
    def __init__(self, customer_plan="SUB"):
        self.customer_plan = customer_plan
        self.loader = jinja2.FileSystemLoader(searchpath="./")
        self.env = jinja2.Environment(loader=self.loader)

        # Load plan-specific template and ingredients
        template_file = f"final_check_prompt_{customer_plan}.jinja"
        ingredients_file = f"ingredients_{customer_plan}.csv"

        self.template = self.env.get_template(template_file)

        try:
            self.df_ingredients = pd.read_csv(ingredients_file)
            self.master_ingredients = self.df_ingredients.to_string(index=False)

            # Get vector length
            raw_list = pd.melt(self.df_ingredients)['value'].dropna().unique().tolist()
            self.vector_length = len(raw_list)

        except Exception as e:
            print(f"CRITICAL ERROR LOADING CSV: {e}")
            self.master_ingredients = ""
            self.vector_length = 0

    def create_prompt(self, llm_ingredients_output):
        """
        Generate a prompt for LLM to validate and correct the ingredients output.
        """
        context = {
            "master_ingredient_list": self.master_ingredients,
            "vector_length": self.vector_length,
            "llm_output": llm_ingredients_output
        }

        return self.template.render(context)


if __name__ == "__main__":
    # Load customer_plan from recipe_config.json
    try:
        with open("recipe_config.json", "r") as f:
            config = json.load(f)
        customer_plan = config.get("customer_plan", "SUB")
    except FileNotFoundError:
        print("WARNING: recipe_config.json not found. Using default plan 'SUB'.")
        customer_plan = "SUB"

    try:
        with open("llm_output.txt", "r") as f:
            llm_output = f.read()
    except FileNotFoundError:
        print("ERROR: llm_output.txt not found.")
        print("Please create llm_output.txt and paste the ingredients portion of the LLM output there.")
        exit(1)

    generator = FinalCheckGenerator(customer_plan=customer_plan)
    print(generator.create_prompt(llm_output))
