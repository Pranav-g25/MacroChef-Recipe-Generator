Project Overview
MacroChef is a recipe generator system that creates LLM-ready prompts for generating chef SOPs (Standard Operating Procedures) and ingredient/macro data for operations teams.
Core Architecture
Component	Purpose
main.py	MacroChefGenerator class - orchestrates prompt generation
macrochef_prompt.jinja	Jinja2 template for structured LLM prompts
ingredients.csv	76 master ingredients across 5 categories
single_serve_guidelines.csv	Portion/macro reference table
custom_recipe_bank.json	Pre-fabricated recipes with SOPs
side_dish_db.json	Side dishes with serving-scaled SOPs
carb_db.json	Carb options (rice, roti variants)
Three Generation Modes
PRE-FAB - LLM generates cooking instructions from scratch
CUSTOM PRE-FAB - Retrieves pre-written SOPs from database, LLM validates vectors
FULL CUSTOM - Completely custom generation from raw input
Key Features
76-dimensional binary ingredient vectors for inventory tracking
Fuzzy matching (0.8 threshold) for ingredient name resolution
Serving size scaling with floor-based lookup keys
Optional translation support (e.g., Hinglish)
Categorized ingredient lists (Proteins, Essentials N.P./P., Speciality NP/P)
Data Flow

User Input → MacroChefGenerator.create_prompt() → Database Lookups → 
Vector Generation → Jinja2 Rendering → LLM-Ready Prompt