# MacroChef Recipe Generator

A prompt engineering system for generating nutrition-aware recipes with standardized SOPs (Standard Operating Procedures) and ingredient tracking for a private chef service.

## Overview

MacroChef is a nutrition-aware private chef service for gym-goers and fitness enthusiasts. This repository contains the prompt generation system that creates structured prompts for LLM chatbots to generate:

1. **Chef SOPs** - Step-by-step cooking instructions with Indian cuisine techniques
2. **Categorized Ingredient Lists** - Ingredients grouped by operational categories
3. **Binary Ingredient Vectors** - 76-dimension vectors for inventory tracking
4. **Macro Summaries** - Nutritional information per serving

## Project Structure

```
MacroChef-Recipe-Generator/
|
|-- Core Scripts
|   |-- recipe_config.py      # Interactive config generator with dropdown menus
|   |-- main.py               # Main prompt generator
|   |-- final_check.py        # Ingredient validation prompt generator
|
|-- Jinja2 Templates (Plan-Specific)
|   |-- macrochef_prompt_SUB.jinja      # Recipe prompt template (Subscription)
|   |-- macrochef_prompt_DEMO.jinja     # Recipe prompt template (Demo)
|   |-- final_check_prompt_SUB.jinja    # Validation prompt template (Subscription)
|   |-- final_check_prompt_DEMO.jinja   # Validation prompt template (Demo)
|
|-- Ingredient Data (Plan-Specific)
|   |-- ingredients_SUB.csv             # 76 ingredients, 3 categories (MWR/WR/RNT)
|   |-- ingredients_DEMO.csv            # 76 ingredients, 5 categories (legacy)
|
|-- Recipe Databases
|   |-- custom_recipe_bank.json   # Pre-written recipes (Salads, Chinese, Sandwiches)
|   |-- side_dish_db.json         # Side dishes with serving-scaled SOPs
|   |-- carb_db.json              # Carb options (Rice, Roti variants)
|
|-- Reference Data
|   |-- single_serve_guidelines_new.csv  # Portion sizes and macro info
|
|-- Generated Files (git-ignored)
|   |-- recipe_config.json        # Current recipe configuration
|   |-- prompt.txt                # Generated LLM prompt
|   |-- llm_output.txt            # LLM response for validation
|
|-- .gitignore
```

## Customer Plans

The system supports two customer plan types with different ingredient categorizations:

| Plan | Categories | Use Case |
|------|------------|----------|
| **SUB** (Subscription) | 3 categories: List 1 (MWR), List 2 (WR), List 3 (RNT) | Production subscribers |
| **DEMO** | 5 categories: Proteins, Essentials (N.P.), Essentials (P), Speciality (NP), Speciality (P) | Demo/trial customers |

## Generation Modes

### 1. Prefab Mode
LLM generates complete recipe from scratch based on dish title.
- Free-text dish input (e.g., "Shrimp Curry", "Paneer Bhurji")
- LLM creates SOP with Indian cooking techniques (bhuna, tadka)
- Generates ingredient list and vector

### 2. Custom Prefab Mode
Uses pre-written SOPs from the recipe database.
- Select from predefined recipes (Salad Meal, Chinese Bowl, Sandwich)
- Choose protein, carb/sauce/dressing variants
- LLM formats output and calculates vectors

### 3. Full Custom Mode
Completely custom recipe request via free-text input.

---

## Complete Recipe Generation Flow

```
+-----------------------------------------------------------------------------+
|                        RECIPE GENERATION WORKFLOW                           |
+-----------------------------------------------------------------------------+

STEP 1: CONFIGURATION
---------------------
    +---------------------+
    |  recipe_config.py   |
    +---------+-----------+
              |
              v
    +-----------------------------------------+
    |  Interactive Menu:                      |
    |  1. Select Customer Plan (SUB/DEMO)     |
    |  2. Select Mode (prefab/custom/full)    |
    |  3. Enter dish details                  |
    |  4. Select side dish (from DB)          |
    |  5. Select carb side (from DB)          |
    |  6. Optional: customization, language   |
    +---------+-------------------------------+
              |
              v
    +---------------------+
    | recipe_config.json  |  (Generated config file)
    +---------------------+


STEP 2: PROMPT GENERATION
-------------------------
    +---------------------+
    |      main.py        |
    +---------+-----------+
              |
              | Reads: recipe_config.json
              | Loads: macrochef_prompt_{PLAN}.jinja
              | Loads: ingredients_{PLAN}.csv
              | Loads: side_dish_db.json, carb_db.json
              |
              v
    +-----------------------------------------+
    |  Jinja2 Template Rendering:             |
    |  - Injects master ingredient list       |
    |  - Injects single serve guidelines      |
    |  - Injects side dish SOP (if selected)  |
    |  - Injects carb side SOP (if selected)  |
    |  - Pre-calculates vectors for DB items  |
    +---------+-------------------------------+
              |
              v
    +---------------------+
    |     prompt.txt      |  (LLM-ready prompt)
    +---------------------+


STEP 3: LLM PROCESSING
----------------------
    +---------------------+
    |     prompt.txt      |
    +---------+-----------+
              |
              | Copy & paste to LLM chatbot
              | (Gemini Pro, GPT-4, Claude, etc.)
              |
              v
    +-----------------------------------------+
    |  LLM Generates:                         |
    |  1. Complete cooking SOP                |
    |  2. Macro summary per serving           |
    |  3. Categorized ingredient list         |
    |  4. 76-dimension binary vector          |
    +---------+-------------------------------+
              |
              | Copy ingredients portion
              |
              v
    +---------------------+
    |   llm_output.txt    |  (Paste LLM response here)
    +---------------------+


STEP 4: VALIDATION PROMPT GENERATION
------------------------------------
    +---------------------+
    |   final_check.py    |
    +---------+-----------+
              |
              | Reads: recipe_config.json (for plan)
              | Reads: llm_output.txt
              | Loads: final_check_prompt_{PLAN}.jinja
              | Loads: ingredients_{PLAN}.csv
              |
              v
    +-----------------------------------------+
    |  Generates validation prompt with:      |
    |  - Master ingredient list               |
    |  - Original LLM output to validate      |
    |  - Instructions for error checking      |
    |  - Strict output template               |
    +---------+-------------------------------+
              |
              v
    +---------------------+
    |  Validation Prompt  |  (Output to console)
    +---------------------+


STEP 5: FINAL VALIDATION
------------------------
    +---------------------+
    |  Validation Prompt  |
    +---------+-----------+
              |
              | Paste to SAME LLM chat session
              |
              v
    +-----------------------------------------+
    |  LLM Validates & Outputs:               |
    |  1. <errors_found>: List of issues      |
    |  2. <final_ing_list>: Corrected list    |
    |  3. <final_ing_vec>: Corrected vector   |
    +---------+-------------------------------+
              |
              v
    +---------------------+
    |   FINAL RECIPE      |  (Ready for operations)
    +---------------------+
```

---

## Quick Start

### Prerequisites

```bash
pip install jinja2 pandas
```

### Usage

```bash
# Step 1: Generate configuration (interactive)
python recipe_config.py

# Step 2: Generate LLM prompt
python main.py > prompt.txt

# Step 3: Copy prompt.txt content to your LLM chatbot (Gemini, GPT-4, Claude)

# Step 4: Copy the ingredients portion of LLM response to llm_output.txt

# Step 5: Generate validation prompt
python final_check.py > validation_prompt.txt

# Step 6: Paste validation prompt to the SAME LLM chat for final verification
```

## Example Configuration

```json
{
  "customer_plan": "SUB",
  "mode": "prefab",
  "dish_title": "Paneer Chilla",
  "serving_size": "4",
  "side_title": "Vegetable Raita",
  "carb_side_title": "Ghee Roti",
  "customization_string": null,
  "translation_lang": "bengali"
}
```

---

## Ingredient Categories

### SUB Plan (3 Categories)
| Category | Description | Examples |
|----------|-------------|----------|
| List 1 (MWR) | Fresh/perishable items | lemon, garlic, curd, tomato, ginger |
| List 2 (WR) | Dry goods, pantry staples | spices, oils, flour, rice, dal |
| List 3 (RNT) | Proteins, dairy, produce | eggs, paneer, chicken, vegetables |

### DEMO Plan (5 Categories)
| Category | Description |
|----------|-------------|
| Proteins | Eggs, paneer, chicken, fish, etc. |
| Essentials (N.P.) | Non-perishable essentials (spices, oils) |
| Essentials (P) | Perishable essentials (garlic, curd) |
| Speciality (NP) | Non-perishable specialty items |
| Speciality (P) | Perishable specialty items |

---

## Binary Ingredient Vector

The system generates a 76-dimension binary vector for inventory tracking:
- Each position represents one ingredient from the master list
- `1` = ingredient used, `0` = ingredient not used
- Order follows CSV columns (top to bottom, left to right)

Example:
```
[1, 0, 1, 1, 0, 0, 1, 0, ...]  # 76 elements
 |  |  |  |           |
 |  |  |  |           +-- 76th ingredient (not used)
 |  |  |  +-- 4th ingredient (used)
 |  |  +-- 3rd ingredient (used)
 |  +-- 2nd ingredient (not used)
 +-- 1st ingredient (used)
```

---

## Recipe Databases

### custom_recipe_bank.json
Pre-fabricated recipes with variants:
- **C01-B Salad Meal**: Protein + Dressing combinations
- **C02-B Chinese Bowl**: Protein + Carb combinations
- **C03-B Sandwich**: Protein + Sauce combinations

### side_dish_db.json
Side dishes with serving-scaled SOPs (1-4 servings):
- Dal, Sambhar, Seasonal Veggie
- Boiled Eggs, Fruit Chat
- Indian Kachumber Salad, Caesar Salad
- Vegetable Raita, Whole Seasonal Fruit

### carb_db.json
Carbohydrate options:
- Rice (with macro info)
- Roti, Ghee Roti, Butter Roti

---

## LLM Recommendations

| Use Case | Recommended Models |
|----------|-------------------|
| Simple prefab recipes | Gemini Flash, GPT-4o-mini |
| Complex recipes with precise macros | Gemini Pro, GPT-4o, Claude Sonnet |
| If vector accuracy is critical | Gemini Pro (thinking), Claude Opus |

### Cost Estimates (Post-Trial)
- ~3K tokens per recipe generation cycle
- 100 recipes/month: $0.02 (Flash) to $0.80 (GPT-4o)

---

## Tips

1. **Use same chat session** for recipe generation + validation (context retention)
2. **Start fresh chat** for each new recipe to avoid context pollution
3. **Vector errors?** The Python scripts have built-in vector generation - consider using that instead of LLM
4. **Batch similar recipes** in same session to reuse ingredient list context

---

## File Descriptions

| File | Purpose |
|------|---------|
| `recipe_config.py` | Interactive CLI for generating recipe configuration |
| `main.py` | Generates LLM prompts using Jinja2 templates |
| `final_check.py` | Generates validation prompts for ingredient verification |
| `*.jinja` | Jinja2 templates for prompt generation |
| `ingredients_*.csv` | Master ingredient lists (76 items) |
| `*_db.json` | Recipe and side dish databases |
| `single_serve_guidelines_new.csv` | Portion sizes and macro information |

---

## License

Private project - MacroChef
