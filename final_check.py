import jinja2
import pandas as pd

class FinalCheckGenerator:
    def __init__(self, template_file="final_check_prompt.jinja"):
        self.loader = jinja2.FileSystemLoader(searchpath="./")
        self.env = jinja2.Environment(loader=self.loader)
        self.template = self.env.get_template(template_file)

        try:
            self.df_ingredients = pd.read_csv("ingredients_new.csv")
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
    try:
        with open("llm_output.txt", "r") as f:
            llm_output = f.read()
    except FileNotFoundError:
        print("ERROR: llm_output.txt not found.")
        print("Please create llm_output.txt and paste the ingredients portion of the LLM output there.")
        exit(1)

    generator = FinalCheckGenerator()
    print(generator.create_prompt(llm_output))
