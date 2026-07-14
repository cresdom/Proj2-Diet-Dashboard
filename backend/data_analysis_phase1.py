import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns
import os

# Load the dataset
df = pd.read_csv("All_Diets.csv")

# Clean column names
df.columns = df.columns.str.strip()

# Columns used for nutrition analysis
nutrition_cols = ["Protein(g)", "Carbs(g)", "Fat(g)"]

# Convert nutrition columns to numbers
for col in nutrition_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Fill missing nutrition values with the column average
for col in nutrition_cols:
    df[col] = df[col].fillna(df[col].mean())

# Check missing values after cleaning
print("\nMissing values after cleaning:")
print(df[nutrition_cols].isnull().sum())

# Calculate average macronutrients for each diet type
avg_macros = df.groupby("Diet_type")[nutrition_cols].mean()

print("\nAverage macronutrients by diet type:")
print(avg_macros)

# Find top 5 protein-rich recipes for each diet type
top_protein = (
    df.sort_values("Protein(g)", ascending=False)
      .groupby("Diet_type")
      .head(5)
)

print("\nTop 5 protein-rich recipes for each diet type:")
print(top_protein[["Diet_type", "Recipe_name", "Cuisine_type", "Protein(g)"]])

# Find the recipe with the highest protein overall
highest_protein = df.loc[df["Protein(g)"].idxmax()]

print("\nRecipe with the highest protein overall:")
print(highest_protein[["Diet_type", "Recipe_name", "Protein(g)"]])

# Find the most common cuisine for each diet type
common_cuisine = (
    df.groupby("Diet_type")["Cuisine_type"]
      .agg(lambda x: x.value_counts().idxmax())
)

print("\nMost common cuisine for each diet type:")
print(common_cuisine)

# Create new ratio columns
df["Protein_to_Carbs_ratio"] = df["Protein(g)"] / df["Carbs(g)"]
df["Carbs_to_Fat_ratio"] = df["Carbs(g)"] / df["Fat(g)"]

print("\nRatio columns added:")
print(df[["Recipe_name", "Protein_to_Carbs_ratio", "Carbs_to_Fat_ratio"]].head())

# Save output files for submission
df.to_csv("cleaned_all_diets.csv", index=False)
avg_macros.to_csv("average_macros_by_diet.csv")
top_protein.to_csv("top_5_protein_recipes.csv", index=False)
common_cuisine.to_csv("most_common_cuisine.csv")

print("\nTask 1 analysis completed successfully.")
print("Output CSV files have been saved.")


# Create a folder to save chart images
os.makedirs("visualizations", exist_ok=True)

# Bar chart: average protein by diet type
plt.figure(figsize=(10, 6))
sns.barplot(x=avg_macros.index, y=avg_macros["Protein(g)"])
plt.title("Average Protein by Diet Type")
plt.xlabel("Diet Type")
plt.ylabel("Average Protein (g)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("visualizations/average_protein_by_diet.png")
plt.show()

# Bar chart: average carbs by diet type
plt.figure(figsize=(10, 6))
sns.barplot(x=avg_macros.index, y=avg_macros["Carbs(g)"])
plt.title("Average Carbs by Diet Type")
plt.xlabel("Diet Type")
plt.ylabel("Average Carbs (g)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("visualizations/average_carbs_by_diet.png")
plt.show()

# Bar chart: average fat by diet type
plt.figure(figsize=(10, 6))
sns.barplot(x=avg_macros.index, y=avg_macros["Fat(g)"])
plt.title("Average Fat by Diet Type")
plt.xlabel("Diet Type")
plt.ylabel("Average Fat (g)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("visualizations/average_fat_by_diet.png")
plt.show()

# Heatmap: average nutrition values by diet type
plt.figure(figsize=(10, 6))
sns.heatmap(avg_macros, annot=True, fmt=".2f", cmap="YlGnBu")
plt.title("Average Macronutrients by Diet Type")
plt.tight_layout()
plt.savefig("visualizations/macronutrient_heatmap.png")
plt.show()

# Scatter plot: top protein recipes by cuisine
plt.figure(figsize=(12, 6))
sns.scatterplot(
    data=top_protein,
    x="Cuisine_type",
    y="Protein(g)",
    hue="Diet_type"
)
plt.title("Top Protein Recipes by Cuisine")
plt.xlabel("Cuisine Type")
plt.ylabel("Protein (g)")
plt.xticks(rotation=60)
plt.tight_layout()
plt.savefig("visualizations/top_protein_scatterplot.png")
plt.show()
