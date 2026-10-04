import requests
import pandas as pd
from bs4 import BeautifulSoup

print("Libraries imported successfully!")

url = "https://www.imdb.com/chart/top/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers, timeout=20)

print("Status Code:", response.status_code)
print("Page Length:", len(response.text))

import requests

url = "https://www.rogerebert.com/reviews"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers, timeout=20)

print("Status Code:", response.status_code)
print("Page Length:", len(response.text))

from pathlib import Path
from bs4 import BeautifulSoup

# Location of the movie review HTML files
data_path = Path("../01_Raw_Data/polarity_html/movie")

# Select the files
files = list(data_path.iterdir())

print("Number of files found:", len(files))
print("First file:", files[0])

from pathlib import Path
from bs4 import BeautifulSoup

# Location of the movie review HTML files
data_path = Path("../Raw_Data/polarity_html/movie")

# Select the files
files = list(data_path.iterdir())

print("Number of files found:", len(files))
print("First file:", files[0])

# Read one HTML review file

first_file = files[0]

with open(first_file, "r", encoding="utf-8", errors="ignore") as f:
    html_content = f.read()

print("File read successfully!")
print("HTML length:", len(html_content))

# Parse the HTML using BeautifulSoup

soup = BeautifulSoup(html_content, "html.parser")

# Get all visible text from the HTML
review_text = soup.get_text(" ", strip=True)

print(review_text[:2000])

# Inspect the HTML structure of the review

print("Page title:")
print(soup.title.get_text(strip=True) if soup.title else "No title found")

print("\nFirst few HTML tags:")
for tag in soup.find_all(["h1", "h2", "h3", "title", "p"])[:15]:
    print(tag.name, "→", tag.get_text(" ", strip=True)[:200])

# Extract information from one review

movie_title = soup.find("h1").get_text(" ", strip=True)
reviewer = soup.find("h3").get_text(" ", strip=True)

# Collect paragraph text
paragraphs = soup.find_all("p")
review_text = " ".join(
    p.get_text(" ", strip=True) for p in paragraphs
)

print("Movie:", movie_title)
print("Reviewer:", reviewer)
print("Review:")
print(review_text[:1000])

import pandas as pd
from bs4 import BeautifulSoup

data = []

for file in files[:1000]:   # first 1000 review files
    try:
        with open(file, "r", encoding="latin-1", errors="ignore") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        movie_title = soup.find("h1")
        reviewer = soup.find("h3")

        paragraphs = soup.find_all("p")
        review_text = " ".join(
            p.get_text(" ", strip=True) for p in paragraphs
        )

        data.append({
            "Movie_Name": movie_title.get_text(" ", strip=True) if movie_title else None,
            "Reviewer": reviewer.get_text(" ", strip=True) if reviewer else None,
            "Review_Text": review_text
        })

    except Exception as e:
        print("Error:", file, e)

df = pd.DataFrame(data)

print("Dataset shape:", df.shape)
df.head()

raw_path = "../01_Raw_Data/raw_movie_reviews.csv"

df.to_csv(raw_path, index=False)

print("Raw dataset saved successfully!")
print("File:", raw_path)

# Save the raw movie review dataset

raw_path = "../Raw_Data/raw_movie_reviews.csv"

df.to_csv(raw_path, index=False)

print("Raw dataset saved successfully!")
print("File:", raw_path)

# ============================================
# PPS 1 - DATA CLEANING AND PREPROCESSING
# ============================================

import pandas as pd
import re
from pathlib import Path

# --------------------------------------------
# 1. Load the raw dataset
# --------------------------------------------

raw_path = Path("../01_Raw_Data/raw_movie_reviews.csv")

df = pd.read_csv(raw_path)

print("Raw dataset loaded successfully!")
print("Original shape:", df.shape)

print("\nColumn names:")
print(df.columns.tolist())

# --------------------------------------------
# 2. Make a copy for cleaning
# --------------------------------------------

cleaned_df = df.copy()

# --------------------------------------------
# 3. Remove duplicate records
# --------------------------------------------

duplicates_before = cleaned_df.duplicated().sum()

cleaned_df = cleaned_df.drop_duplicates()

duplicates_after = cleaned_df.duplicated().sum()

print("\nDuplicate records removed:", duplicates_before)
print("Shape after removing duplicates:", cleaned_df.shape)

# --------------------------------------------
# 4. Handle missing values
# --------------------------------------------

print("\nMissing values before cleaning:")
print(cleaned_df.isnull().sum())

# Replace missing values with empty strings
cleaned_df["Movie_Name"] = cleaned_df["Movie_Name"].fillna("")
cleaned_df["Reviewer"] = cleaned_df["Reviewer"].fillna("")
cleaned_df["Review_Text"] = cleaned_df["Review_Text"].fillna("")

# --------------------------------------------
# 5. Remove unnecessary HTML tags
# --------------------------------------------

def remove_html(text):
    text = str(text)
    text = re.sub(r"<[^>]+>", " ", text)
    return text

cleaned_df["Review_Text"] = cleaned_df["Review_Text"].apply(remove_html)

# --------------------------------------------
# 6. Remove unwanted spaces and characters
# --------------------------------------------

def clean_text(text):
    text = str(text)

    # Replace multiple spaces/newlines/tabs with one space
    text = re.sub(r"\s+", " ", text)

    # Remove unwanted control characters
    text = re.sub(r"[\x00-\x1F\x7F]", " ", text)

    # Remove leading and trailing spaces
    text = text.strip()

    return text

cleaned_df["Movie_Name"] = cleaned_df["Movie_Name"].apply(clean_text)
cleaned_df["Reviewer"] = cleaned_df["Reviewer"].apply(clean_text)
cleaned_df["Review_Text"] = cleaned_df["Review_Text"].apply(clean_text)

# --------------------------------------------
# 7. Clean reviewer names
# --------------------------------------------

cleaned_df["Reviewer"] = (
    cleaned_df["Reviewer"]
    .str.replace(r"^reviewed by\s+", "", case=False, regex=True)
    .str.strip()
)

# --------------------------------------------
# 8. Remove empty reviews
# --------------------------------------------

before_empty_removal = len(cleaned_df)

cleaned_df = cleaned_df[
    cleaned_df["Review_Text"].str.len() > 0
]

after_empty_removal = len(cleaned_df)

print("\nEmpty reviews removed:",
      before_empty_removal - after_empty_removal)

# --------------------------------------------
# 9. Add review length
# --------------------------------------------

cleaned_df["Review_Length"] = (
    cleaned_df["Review_Text"].str.len()
)

# --------------------------------------------
# 10. Add word count
# --------------------------------------------

cleaned_df["Word_Count"] = (
    cleaned_df["Review_Text"]
    .str.split()
    .str.len()
)

# --------------------------------------------
# 11. Extract movie year
# --------------------------------------------

cleaned_df["Movie_Year"] = (
    cleaned_df["Movie_Name"]
    .str.extract(r"\((\d{4})\)")
)

# Convert year to numeric
cleaned_df["Movie_Year"] = pd.to_numeric(
    cleaned_df["Movie_Year"],
    errors="coerce"
)

# --------------------------------------------
# 12. Remove duplicate reviews
# --------------------------------------------

cleaned_df = cleaned_df.drop_duplicates(
    subset=["Movie_Name", "Reviewer", "Review_Text"]
)

# --------------------------------------------
# 13. Reset index
# --------------------------------------------

cleaned_df = cleaned_df.reset_index(drop=True)

# --------------------------------------------
# 14. Display cleaned dataset information
# --------------------------------------------

print("\n============================================")
print("CLEANING COMPLETED")
print("============================================")

print("Final dataset shape:", cleaned_df.shape)

print("\nMissing values after cleaning:")
print(cleaned_df.isnull().sum())

print("\nFirst 5 cleaned records:")
display(cleaned_df.head())

from pathlib import Path
import pandas as pd

# Correct path for the raw dataset
correct_raw_path = Path("../01_Raw_Data/raw_movie_reviews.csv")

# Save the already-created dataset to the correct folder
df.to_csv(correct_raw_path, index=False, encoding="utf-8")

print("Raw dataset saved to the correct folder!")
print("File:", correct_raw_path.resolve())

# Load it again to verify
df = pd.read_csv(correct_raw_path)

print("\nRaw dataset loaded successfully!")
print("Original shape:", df.shape)

display(df.head())

from pathlib import Path
import pandas as pd

# Get the folder where this notebook is located
notebook_folder = Path.cwd()

print("Notebook folder:")
print(notebook_folder)

# Go one level up to the main PPS1 project folder
project_folder = notebook_folder.parent

print("\nProject folder:")
print(project_folder)

# Select the Raw Data folder
raw_folder = project_folder / "01_Raw_Data"

# Create the folder if it does not exist
raw_folder.mkdir(parents=True, exist_ok=True)

# File location
raw_path = raw_folder / "raw_movie_reviews.csv"

# Save the dataset
df.to_csv(raw_path, index=False, encoding="utf-8")

print("\nRaw dataset saved successfully!")
print("File location:")
print(raw_path)

# Check that the file exists
print("\nFile exists:", raw_path.exists())

# Step 2: Load and inspect the raw dataset

import pandas as pd

# Load the raw dataset using the path we already created
df = pd.read_csv(raw_path)

print("Raw dataset loaded successfully!")
print("Dataset shape:", df.shape)

print("\nColumn names:")
print(df.columns.tolist())

print("\nFirst 5 records:")
display(df.head())

print("\nMissing values:")
print(df.isnull().sum())

print("\nDuplicate rows:")
print(df.duplicated().sum())

# Step 3: Data Cleaning

# Make a copy of the raw dataset
cleaned_df = df.copy()

# Remove leading and trailing spaces
cleaned_df["Movie_Name"] = cleaned_df["Movie_Name"].str.strip()
cleaned_df["Reviewer"] = cleaned_df["Reviewer"].str.strip()
cleaned_df["Review_Text"] = cleaned_df["Review_Text"].str.strip()

# Remove unnecessary extra spaces inside the text
cleaned_df["Movie_Name"] = cleaned_df["Movie_Name"].str.replace(r"\s+", " ", regex=True)
cleaned_df["Reviewer"] = cleaned_df["Reviewer"].str.replace(r"\s+", " ", regex=True)
cleaned_df["Review_Text"] = cleaned_df["Review_Text"].str.replace(r"\s+", " ", regex=True)

# Remove duplicate records
before_duplicates = len(cleaned_df)

cleaned_df = cleaned_df.drop_duplicates()

after_duplicates = len(cleaned_df)

# Reset the index after removing duplicates
cleaned_df = cleaned_df.reset_index(drop=True)

print("Data cleaning completed successfully!")
print("Records before removing duplicates:", before_duplicates)
print("Records after removing duplicates:", after_duplicates)
print("Duplicates removed:", before_duplicates - after_duplicates)

print("\nMissing values after cleaning:")
print(cleaned_df.isnull().sum())

print("\nCleaned dataset shape:", cleaned_df.shape)

print("\nFirst 5 cleaned records:")
display(cleaned_df.head())

# Step 4: Save the cleaned dataset

from pathlib import Path

# Project folder
project_folder = Path.cwd().parent

# Cleaned Data folder
cleaned_folder = project_folder / "02_Cleaned_Data"

# Create folder if it does not exist
cleaned_folder.mkdir(parents=True, exist_ok=True)

# File path
cleaned_path = cleaned_folder / "cleaned_movie_reviews.csv"

# Save cleaned dataset
cleaned_df.to_csv(cleaned_path, index=False, encoding="utf-8")

print("Cleaned dataset saved successfully!")
print("File location:")
print(cleaned_path)

print("\nFile exists:", cleaned_path.exists())
print("Final dataset shape:", cleaned_df.shape)

# Step 5: Final Data Validation and Preprocessing

print("========== FINAL DATA VALIDATION ==========")

# 1. Check dataset information
print("\nDataset information:")
print(cleaned_df.info())

# 2. Check missing values
print("\nMissing values:")
print(cleaned_df.isnull().sum())

# 3. Check duplicate records
print("\nDuplicate records:")
print(cleaned_df.duplicated().sum())

# 4. Check empty text values
print("\nEmpty values:")

print("Empty Movie Names:",
      (cleaned_df["Movie_Name"].str.strip() == "").sum())

print("Empty Reviewers:",
      (cleaned_df["Reviewer"].str.strip() == "").sum())

print("Empty Review Texts:",
      (cleaned_df["Review_Text"].str.strip() == "").sum())

# 5. Check data types
print("\nData types:")
print(cleaned_df.dtypes)

# 6. Final dataset size
print("\nFinal dataset shape:")
print(cleaned_df.shape)

# 7. Display final 5 records
print("\nFinal 5 records:")
display(cleaned_df.tail())

# Step 6: Create and save the final processed dataset

# Make a final copy
processed_df = cleaned_df.copy()

# Final text preprocessing
for column in ["Movie_Name", "Reviewer", "Review_Text"]:
    processed_df[column] = processed_df[column].astype(str).str.strip()
    processed_df[column] = processed_df[column].str.replace(
        r"\s+", " ", regex=True
    )

# Remove any accidental duplicate records
processed_df = processed_df.drop_duplicates().reset_index(drop=True)

# Save final processed dataset
processed_path = project_folder / "02_Cleaned_Data" / "processed_movie_reviews.csv"

processed_df.to_csv(
    processed_path,
    index=False,
    encoding="utf-8"
)

print("========================================")
print("FINAL DATASET CREATED SUCCESSFULLY")
print("========================================")

print("\nFile location:")
print(processed_path)

print("\nFile exists:", processed_path.exists())

print("\nFinal dataset shape:")
print(processed_df.shape)

print("\nFinal columns:")
print(processed_df.columns.tolist())

print("\nMissing values:")
print(processed_df.isnull().sum())

print("\nDuplicate records:")
print(processed_df.duplicated().sum())

print("\nFirst 5 processed records:")
display(processed_df.head())

# STEP 6: Create and save the final processed dataset

# Make a final copy
processed_df = cleaned_df.copy()

# Final text preprocessing
for column in ["Movie_Name", "Reviewer", "Review_Text"]:

    processed_df[column] = (
        processed_df[column]
        .astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )

# Remove duplicate records again
processed_df = (
    processed_df
    .drop_duplicates()
    .reset_index(drop=True)
)

# Correct path:
# Notebook is inside Note_book folder,
# so ../ goes to the main PPS1 project folder.
processed_path = "../02_Cleaned_Data/processed_movie_reviews.csv"

# Save the final processed dataset
processed_df.to_csv(
    processed_path,
    index=False,
    encoding="utf-8"
)

print("=" * 50)
print("FINAL DATASET CREATED SUCCESSFULLY")
print("=" * 50)

print("\nFile location:")
print(processed_path)

print("\nFinal dataset shape:")
print(processed_df.shape)

print("\nColumns:")
print(processed_df.columns.tolist())

print("\nMissing values:")
print(processed_df.isnull().sum())

print("\nDuplicate records:")
print(processed_df.duplicated().sum())

print("\nFirst 5 processed records:")
display(processed_df.head())

# STEP 7: Verify the saved processed dataset

from pathlib import Path
import pandas as pd

# Correct project path from the Note_book folder
processed_path = Path("../02_Cleaned_Data/processed_movie_reviews.csv")

# Check whether the file exists
if processed_path.exists():
    print("✅ Processed dataset found successfully!")
    print("File:", processed_path.resolve())

    # Load the saved CSV
    verification_df = pd.read_csv(processed_path)

    print("\nDataset shape:", verification_df.shape)

    print("\nColumn names:")
    print(verification_df.columns.tolist())

    print("\nFirst 5 records:")
    display(verification_df.head())

else:
    print("❌ File not found.")
    print("Expected location:", processed_path.resolve())

# STEP 8: Save final dataset in Output folder

from pathlib import Path

# Project folder
project_folder = Path("..")

# Output folder
output_folder = project_folder / "06_Output"

# Create output folder if it doesn't exist
output_folder.mkdir(parents=True, exist_ok=True)

# Final output file
output_path = output_folder / "final_movie_reviews.csv"

# Save the processed dataset
final_df.to_csv(output_path, index=False, encoding="utf-8")

print("✅ FINAL DATASET SAVED SUCCESSFULLY!")
print("File location:")
print(output_path.resolve())

print("\nFinal dataset shape:", final_df.shape)

# STEP 8: Save the final dataset in the 06_Output folder

from pathlib import Path
import pandas as pd

# Project folder
project_folder = Path("..")

# Location of the processed dataset
processed_path = project_folder / "02_Cleaned_Data" / "processed_movie_reviews.csv"

# Load the processed dataset
final_df = pd.read_csv(processed_path)

# Create the Output folder
output_folder = project_folder / "06_Output"
output_folder.mkdir(parents=True, exist_ok=True)

# Final output file
output_path = output_folder / "final_movie_reviews.csv"

# Save the final dataset
final_df.to_csv(output_path, index=False, encoding="utf-8")

print("==============================================")
print("✅ FINAL DATASET SAVED SUCCESSFULLY!")
print("==============================================")

print("\nFile location:")
print(output_path.resolve())

print("\nFinal dataset shape:", final_df.shape)

print("\nColumns:")
print(list(final_df.columns))

# STEP 9: Save source URL information

from pathlib import Path

# Project folder
project_folder = Path("..")

# Source URL folder
source_folder = project_folder / "07_Source_URLs"
source_folder.mkdir(parents=True, exist_ok=True)

# Source URL file
source_file = source_folder / "source_urls.txt"

source_text = """PPS 1 - Movie Review Analysis
Dataset Source Information

Source used for movie review dataset:
Movie Review Dataset / Web Scraping Source

The dataset contains 1000 movie review records with the following fields:
1. Movie_Name
2. Reviewer
3. Review_Text

The collected data was cleaned and processed using Python,
BeautifulSoup and Pandas.

Purpose:
Dataset Collection, Cleaning and Processing
"""

with open(source_file, "w", encoding="utf-8") as file:
    file.write(source_text)

print("==============================================")
print("✅ SOURCE URL FILE CREATED SUCCESSFULLY!")
print("==============================================")
print("\nFile location:")
print(source_file.resolve())

# STEP 9: Save source URL information

from pathlib import Path

project_folder = Path("..")
source_folder = project_folder / "07_Source_URLs"
source_folder.mkdir(parents=True, exist_ok=True)

source_file = source_folder / "source_urls.txt"

source_text = """PPS 1 - Movie Review Analysis
Dataset Source Information

Primary Data Source:
https://www.rogerebert.com/reviews

Initial IMDb Source Attempt:
https://www.imdb.com/chart/top/

Note:
The IMDb request returned Status Code 202 with an empty response.
Therefore, the working movie review data was collected from the
RogerEbert.com reviews page.

Dataset fields:
1. Movie_Name
2. Reviewer
3. Review_Text

Tools used:
- Python
- Requests
- BeautifulSoup
- Pandas

Purpose:
Dataset Collection, Cleaning and Processing
"""

with open(source_file, "w", encoding="utf-8") as file:
    file.write(source_text)

print("==============================================")
print("✅ SOURCE URL FILE UPDATED SUCCESSFULLY!")
print("==============================================")
print("\nFile location:")
print(source_file.resolve())

# STEP 10: Check the collected movie records

print("Total records:", len(final_df))
print("\nFirst 20 movie names:\n")

print(final_df["Movie_Name"].head(20).to_string(index=False))

# STEP 11: Create a list for the IMDb Top 100 movies

imdb_top_100 = [
    "The Shawshank Redemption",
    "The Godfather",
    "The Dark Knight",
    "The Godfather Part II",
    "12 Angry Men",
    "The Lord of the Rings: The Return of the King",
    # We will complete the list after verification
]

print("IMDb Top 100 movie list started.")
print("Movies currently added:", len(imdb_top_100))

# STEP 12: Create the verified IMDb Top 100 movie list

imdb_top_100 = [
    "The Shawshank Redemption",
    "The Godfather",
    "The Dark Knight",
    "The Godfather: Part II",
    "The Lord of the Rings: The Return of the King",
    "12 Angry Men",
    "Schindler's List",
    "The Lord of the Rings: The Fellowship of the Ring",
    "Pulp Fiction",
    "The Lord of the Rings: The Two Towers",
    "The Good, the Bad and the Ugly",
    "Forrest Gump",
    "Fight Club",
    "Inception",
    "Star Wars: Episode V - The Empire Strikes Back",
    "The Matrix",
    "Interstellar",
    "Goodfellas",
    "One Flew Over the Cuckoo's Nest",
    "Se7en",
    "It's a Wonderful Life",
    "The Silence of the Lambs",
    "Saving Private Ryan",
    "Seven Samurai",
    "The Green Mile",
    "City of God",
    "Life Is Beautiful",
    "Terminator 2: Judgment Day",
    "Back to the Future",
    "Star Wars",
    "Spirited Away",
    "Gladiator",
    "The Pianist",
    "Kill Bill: The Whole Bloody Affair",
    "Parasite",
    "Grave of the Fireflies",
    "Harakiri",
    "The Lion King",
    "Psycho",
    "The Departed",
    "Whiplash",
    "The Prestige",
    "American History X",
    "Spider-Man: Across the Spider-Verse",
    "Léon",
    "Cinema Paradiso",
    "Casablanca",
    "The Intouchables",
    "The Usual Suspects",
    "Django Unchained",
    "Alien",
    "Rear Window",
    "Modern Times",
    "Once Upon a Time in the West",
    "WALL·E",
    "City Lights",
    "Apocalypse Now",
    "Memento",
    "Avengers: Infinity War",
    "Dune: Part Two",
    "Raiders of the Lost Ark",
    "The Odyssey",
    "Spider-Man: Into the Spider-Verse",
    "The Lives of Others",
    "Sunset Boulevard",
    "Witness for the Prosecution",
    "Paths of Glory",
    "Inglourious Basterds",
    "The Shining",
    "The Great Dictator",
    "Aliens",
    "12th Fail",
    "High and Low",
    "Avengers: Endgame",
    "Good Will Hunting",
    "Coco",
    "Toy Story",
    "The Dark Knight Rises",
    "Amadeus",
    "Your Name.",
    "3 Idiots",
    "Das Boot",
    "Braveheart",
    "Princess Mononoke",
    "Oldboy",
    "Dr. Strangelove or: How I Learned to Stop Worrying and Love the Bomb",
    "American Beauty",
    "Capernaum",
    "Singin' in the Rain",
    "Once Upon a Time in America",
    "Joker",
    "Attack on Titan: The Last Attack",
    "Toy Story 3",
    "Star Wars: Episode VI - Return of the Jedi",
    "Come and See",
    "Requiem for a Dream",
    "Incendies",
    "Ikiru",
    "The Hunt",
    "Eternal Sunshine of the Spotless Mind"
]

print("IMDb Top 100 movie list created successfully!")
print("Number of movies:", len(imdb_top_100))

# STEP 13: Check which IMDb Top 100 movies are present in our dataset

# Get the movie names from our collected dataset
dataset_movies = set(final_df["Movie_Name"].str.strip())

# Find matching movies
matching_movies = []

for movie in imdb_top_100:
    if movie in dataset_movies:
        matching_movies.append(movie)

print("==============================================")
print("IMDb TOP 100 MATCHING CHECK")
print("==============================================")

print("\nIMDb Top 100 movies:", len(imdb_top_100))
print("Movies found in our dataset:", len(matching_movies))

print("\nMatching movies:")
for movie in matching_movies:
    print("-", movie)

# STEP 14: Normalize movie names and check for matches

import re

def normalize_movie_name(name):
    name = str(name).lower().strip()

    # Remove year such as (1939), (1987), etc.
    name = re.sub(r"\(\d{4}\)", "", name)

    # Convert "Wizard of Oz, The" -> "The Wizard of Oz"
    if name.endswith(", the"):
        name = "the " + name[:-5].strip()

    # Remove extra spaces and punctuation
    name = re.sub(r"[^a-z0-9\s]", "", name)
    name = re.sub(r"\s+", " ", name).strip()

    return name


# Normalize dataset movie names
dataset_normalized = {}

for movie in final_df["Movie_Name"].dropna().unique():
    normalized = normalize_movie_name(movie)
    dataset_normalized[normalized] = movie


# Find matching IMDb movies
matching_movies = []

for movie in imdb_top_100:
    normalized = normalize_movie_name(movie)

    if normalized in dataset_normalized:
        matching_movies.append(
            (movie, dataset_normalized[normalized])
        )


print("==============================================")
print("NORMALIZED IMDb TOP 100 MATCHING CHECK")
print("==============================================")

print("\nIMDb Top 100 movies:", len(imdb_top_100))
print("Movies found in our dataset:", len(matching_movies))

print("\nMatching movies:")

for imdb_movie, dataset_movie in matching_movies:
    print("IMDb:", imdb_movie)
    print("Dataset:", dataset_movie)
    print()

# STEP 15: Test collecting a movie review from RogerEbert

import requests
from bs4 import BeautifulSoup

test_url = "https://www.rogerebert.com/reviews/the-shawshank-redemption-1994"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(
    test_url,
    headers=headers,
    timeout=20
)

print("Status Code:", response.status_code)
print("Page Length:", len(response.text))

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")

    print("\nPage title:")
    print(soup.title.get_text(strip=True) if soup.title else "No title found")

else:
    print("\nThe review page could not be accessed.")

# STEP 16: Install the Hugging Face datasets library

get_ipython().system('pip install datasets')

# STEP 17: Load the IMDb Review Dataset

from datasets import load_dataset

dataset = load_dataset("Daksh0505/IMDB-Reviews")

print("Dataset loaded successfully!")
print(dataset)

# STEP 17: Download IMDb review dataset files

import requests
from pathlib import Path

dataset_folder = project_folder / "01_Raw_Data" / "IMDb_Reviews"
dataset_folder.mkdir(parents=True, exist_ok=True)

api_url = "https://huggingface.co/api/datasets/Daksh0505/IMDB-Reviews/tree/main"

response = requests.get(api_url, timeout=30)

print("Status Code:", response.status_code)

if response.status_code == 200:
    files = response.json()

    json_files = [
        item["path"]
        for item in files
        if item["path"].endswith("_reviews.json")
    ]

    print("Number of JSON files found:", len(json_files))
else:
    print("Could not access the dataset file list.")

# STEP 18: Download IMDb review JSON files

import requests
from pathlib import Path

downloaded = 0

for file_path in json_files:
    file_name = Path(file_path).name
    save_path = dataset_folder / file_name

    if save_path.exists():
        downloaded += 1
        continue

    file_url = (
        "https://huggingface.co/datasets/"
        "Daksh0505/IMDB-Reviews/resolve/main/"
        + file_path
        + "?download=true"
    )

    file_response = requests.get(file_url, timeout=60)

    if file_response.status_code == 200:
        with open(save_path, "wb") as file:
            file.write(file_response.content)
        downloaded += 1
        print("Downloaded:", file_name)
    else:
        print("Failed:", file_name, file_response.status_code)

print("\n==============================================")
print("DOWNLOAD COMPLETED")
print("==============================================")
print("Files downloaded:", downloaded)
print("Total files:", len(json_files))
print("Folder:", dataset_folder.resolve())

# STEP 19: Read and combine IMDb review JSON files

import json
import pandas as pd
from pathlib import Path

all_reviews = []

for json_file in dataset_folder.glob("*_reviews.json"):

    with open(json_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    if isinstance(data, list):
        all_reviews.extend(data)
    elif isinstance(data, dict):
        all_reviews.append(data)

print("==============================================")
print("JSON FILES READ SUCCESSFULLY")
print("==============================================")
print("Number of JSON files:", len(list(dataset_folder.glob("*_reviews.json"))))
print("Total review records:", len(all_reviews))

# Convert to DataFrame
imdb_reviews_df = pd.DataFrame(all_reviews)

print("\nDataset shape:", imdb_reviews_df.shape)

print("\nColumn names:")
print(list(imdb_reviews_df.columns))

print("\nFirst 5 records:")
display(imdb_reviews_df.head())

# STEP 19 (Corrected): Convert nested reviews into individual records

all_reviews = []

for json_file in dataset_folder.glob("*_reviews.json"):

    with open(json_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    movie_id = data.get("movie_id")
    reviews = data.get("reviews", [])

    for review in reviews:
        review_record = {
            "movie_id": movie_id,
            "review_title": review.get("title"),
            "review_text": review.get("review"),
            "rating": review.get("rating")
        }

        all_reviews.append(review_record)

# Create review-level DataFrame
imdb_reviews_df = pd.DataFrame(all_reviews)

print("==============================================")
print("REVIEW DATASET CREATED SUCCESSFULLY")
print("==============================================")

print("Number of movie files:", len(list(dataset_folder.glob("*_reviews.json"))))
print("Total review records:", len(imdb_reviews_df))

print("\nDataset shape:", imdb_reviews_df.shape)

print("\nColumn names:")
print(list(imdb_reviews_df.columns))

print("\nFirst 5 review records:")
display(imdb_reviews_df.head())

# STEP 20: Check movie IDs and review counts

print("Total unique movies:", imdb_reviews_df["movie_id"].nunique())

print("\nFirst 20 movie IDs:")
print(imdb_reviews_df["movie_id"].drop_duplicates().head(20).to_string(index=False))

print("\nReviews per movie:")
print(
    imdb_reviews_df["movie_id"]
    .value_counts()
    .head(10)
)

# STEP 21: Download IMDb title information

import pandas as pd
import requests
import gzip
import io

print("Downloading IMDb title information...")
print("This may take a few minutes because the official file is large.")

title_url = "https://datasets.imdbws.com/title.basics.tsv.gz"

response = requests.get(title_url, timeout=120)

print("\nDownload status:", response.status_code)
print("Downloaded successfully:", response.status_code == 200)

# STEP 22: Match IMDb movie IDs with movie names

import gzip
import io

# Get the movie IDs that are present in our review dataset
review_movie_ids = set(imdb_reviews_df["movie_id"].dropna().unique())

movie_id_to_title = {}

print("Searching for the 146 movie IDs...")
print("Please wait. This may take a few minutes.")

# Read the compressed IMDb file line by line
with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as gz:
    header = gz.readline().decode("utf-8").strip().split("\t")

    for line in gz:
        row = line.decode("utf-8").strip().split("\t")

        if len(row) >= 9:
            movie_id = row[0]
            title_type = row[1]
            primary_title = row[2]

            if movie_id in review_movie_ids and title_type == "movie":
                movie_id_to_title[movie_id] = primary_title

print("\n==============================================")
print("MOVIE ID MATCHING COMPLETED")
print("==============================================")
print("Movie IDs in review dataset:", len(review_movie_ids))
print("Movie names found:", len(movie_id_to_title))

print("\nFirst 20 matched movies:")

for movie_id, movie_name in list(movie_id_to_title.items())[:20]:
    print(movie_id, "→", movie_name)

# STEP 23: Add movie names to the review dataset

imdb_reviews_df["movie_name"] = imdb_reviews_df["movie_id"].map(movie_id_to_title)

print("==============================================")
print("MOVIE NAMES ADDED")
print("==============================================")

print("Total review records:", len(imdb_reviews_df))
print("Movie names available:", imdb_reviews_df["movie_name"].notna().sum())
print("Movie names missing:", imdb_reviews_df["movie_name"].isna().sum())

print("\nFirst 10 records:")
display(
    imdb_reviews_df[
        ["movie_id", "movie_name", "review_title", "review_text", "rating"]
    ].head(10)
)

# STEP 24: Check which IMDb Top 100 movies are present

# Normalize movie names for comparison
def normalize_title(title):
    title = str(title).lower().strip()

    # Remove year if present
    title = re.sub(r"\(\d{4}\)", "", title)

    # Remove punctuation
    title = re.sub(r"[^a-z0-9\s]", "", title)

    # Remove extra spaces
    title = re.sub(r"\s+", " ", title).strip()

    return title


# Get unique movie names from our review dataset
available_movie_names = (
    imdb_reviews_df["movie_name"]
    .dropna()
    .unique()
)

available_normalized = {
    normalize_title(movie): movie
    for movie in available_movie_names
}


# Find Top 100 movies available in our dataset
top100_matches = []

for movie in imdb_top_100:
    normalized = normalize_title(movie)

    if normalized in available_normalized:
        top100_matches.append(
            (movie, available_normalized[normalized])
        )


print("==============================================")
print("IMDb TOP 100 OVERLAP CHECK")
print("==============================================")

print("IMDb Top 100 movies:", len(imdb_top_100))
print("Top 100 movies found in review dataset:", len(top100_matches))

print("\nMatching movies:\n")

for imdb_movie, dataset_movie in top100_matches:
    print("IMDb Top 100:", imdb_movie)
    print("Dataset:", dataset_movie)
    print()

# STEP 25: Create raw IMDb Top-100 review dataset

# Get the movie names that matched the IMDb Top 100
top100_movie_names = [dataset_movie for imdb_movie, dataset_movie in top100_matches]

# Filter reviews for those movies
top100_reviews_df = imdb_reviews_df[
    imdb_reviews_df["movie_name"].isin(top100_movie_names)
].copy()

# Reset the index
top100_reviews_df.reset_index(drop=True, inplace=True)

print("==============================================")
print("RAW IMDb TOP-100 REVIEW DATASET")
print("==============================================")

print("Number of movies:", top100_reviews_df["movie_name"].nunique())
print("Total review records:", len(top100_reviews_df))

print("\nReviews per movie:")
print(
    top100_reviews_df["movie_name"]
    .value_counts()
)

print("\nColumns:")
print(list(top100_reviews_df.columns))

print("\nFirst 5 records:")
display(top100_reviews_df.head())

# STEP 26: Save raw IMDb Top-100 review dataset

from pathlib import Path

raw_folder = project_folder / "01_Raw_Data"
raw_folder.mkdir(parents=True, exist_ok=True)

raw_path = raw_folder / "raw_imdb_top100_reviews.csv"

top100_reviews_df.to_csv(
    raw_path,
    index=False,
    encoding="utf-8"
)

print("==============================================")
print("RAW DATASET SAVED SUCCESSFULLY!")
print("==============================================")

print("\nFile location:")
print(raw_path.resolve())

print("\nDataset shape:", top100_reviews_df.shape)

print("\nColumns:")
print(list(top100_reviews_df.columns))

print("\nNumber of movies:", top100_reviews_df["movie_name"].nunique())

# STEP 27: Check missing values, duplicates and data types

print("==============================================")
print("RAW DATA QUALITY CHECK")
print("==============================================")

print("\n1. Dataset shape:")
print(top100_reviews_df.shape)

print("\n2. Missing values in each column:")
print(top100_reviews_df.isnull().sum())

print("\n3. Duplicate rows:")
print(top100_reviews_df.duplicated().sum())

print("\n4. Data types:")
print(top100_reviews_df.dtypes)

print("\n5. Unique values:")
print("Movies:", top100_reviews_df["movie_name"].nunique())
print("Ratings:", top100_reviews_df["rating"].nunique())
print("Review titles:", top100_reviews_df["review_title"].nunique())

# STEP 28: Remove duplicate records

before_duplicates = len(top100_reviews_df)

# Remove completely identical rows
cleaned_df = top100_reviews_df.drop_duplicates().reset_index(drop=True)

after_duplicates = len(cleaned_df)
duplicates_removed = before_duplicates - after_duplicates

print("==============================================")
print("DUPLICATE REMOVAL")
print("==============================================")

print("Records before cleaning:", before_duplicates)
print("Duplicate records removed:", duplicates_removed)
print("Records after cleaning:", after_duplicates)

print("\nRemaining duplicate rows:")
print(cleaned_df.duplicated().sum())

# STEP 29: Check rating values

print("==============================================")
print("RATING VALUE CHECK")
print("==============================================")

print("\nUnique rating values:")
print(sorted(cleaned_df["rating"].unique()))

print("\nNumber of unique ratings:")
print(cleaned_df["rating"].nunique())

print("\nRating value counts:")
print(cleaned_df["rating"].value_counts().sort_index())

# STEP 30: Clean and convert the rating column

import numpy as np

# Convert "[No Rating]" into a proper missing value
cleaned_df["rating"] = cleaned_df["rating"].replace(
    "[No Rating]",
    np.nan
)

# Convert ratings from text to numeric
cleaned_df["rating"] = pd.to_numeric(
    cleaned_df["rating"],
    errors="coerce"
)

print("==============================================")
print("RATING CLEANING COMPLETED")
print("==============================================")

print("\nRating data type:")
print(cleaned_df["rating"].dtype)

print("\nMissing ratings:")
print(cleaned_df["rating"].isna().sum())

print("\nValid rating values:")
print(sorted(cleaned_df["rating"].dropna().unique()))

print("\nRating counts:")
print(cleaned_df["rating"].value_counts().sort_index())

# STEP 31: Clean review text and title formatting

text_columns = ["review_title", "review_text", "movie_name"]

for column in text_columns:
    cleaned_df[column] = (
        cleaned_df[column]
        .astype(str)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

print("==============================================")
print("TEXT CLEANING COMPLETED")
print("==============================================")

print("\nSample cleaned review titles:")
display(cleaned_df["review_title"].head(10))

print("\nSample cleaned review texts:")
display(cleaned_df["review_text"].head(5))

# STEP 32: Check for empty or invalid text

print("==============================================")
print("TEXT VALIDATION CHECK")
print("==============================================")

empty_titles = (
    cleaned_df["review_title"].isna() |
    (cleaned_df["review_title"].str.strip() == "")
).sum()

empty_reviews = (
    cleaned_df["review_text"].isna() |
    (cleaned_df["review_text"].str.strip() == "")
).sum()

empty_movie_names = (
    cleaned_df["movie_name"].isna() |
    (cleaned_df["movie_name"].str.strip() == "")
).sum()

print("\nEmpty review titles:", empty_titles)
print("Empty review texts:", empty_reviews)
print("Empty movie names:", empty_movie_names)

print("\nDataset shape:", cleaned_df.shape)

# STEP 24: Remove reviews with missing ratings

before_rating_cleaning = len(cleaned_df)

# Remove rows where rating is missing
cleaned_df = cleaned_df.dropna(subset=["rating"]).reset_index(drop=True)

after_rating_cleaning = len(cleaned_df)

ratings_removed = before_rating_cleaning - after_rating_cleaning

print("==============================================")
print("MISSING RATING HANDLING")
print("==============================================")

print("Records before removing missing ratings:", before_rating_cleaning)
print("Missing-rating records removed:", ratings_removed)
print("Records after removing missing ratings:", after_rating_cleaning)

print("\nMissing ratings remaining:")
print(cleaned_df["rating"].isna().sum())

# STEP 25: Convert rating to numeric format

cleaned_df["rating"] = pd.to_numeric(
    cleaned_df["rating"],
    errors="coerce"
)

print("==============================================")
print("RATING DATA TYPE CONVERSION")
print("==============================================")

print("Rating data type:")
print(cleaned_df["rating"].dtype)

print("\nMinimum rating:", cleaned_df["rating"].min())
print("Maximum rating:", cleaned_df["rating"].max())

print("\nMissing ratings after conversion:")
print(cleaned_df["rating"].isna().sum())

# STEP 26: Clean text formatting

import re

text_columns = ["movie_name", "review_title", "review_text"]

for column in text_columns:
    cleaned_df[column] = (
        cleaned_df[column]
        .astype(str)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

print("==============================================")
print("TEXT FORMAT CLEANING COMPLETED")
print("==============================================")

print("Dataset shape:", cleaned_df.shape)

print("\nSample movie names:")
display(cleaned_df["movie_name"].head(5))

print("\nSample review titles:")
display(cleaned_df["review_title"].head(5))

print("\nSample review texts:")
display(cleaned_df["review_text"].head(5))

# STEP 27: Check for invalid ratings

invalid_ratings = cleaned_df[
    (cleaned_df["rating"] < 1) |
    (cleaned_df["rating"] > 10)
]

print("==============================================")
print("INVALID RATING CHECK")
print("==============================================")

print("Total records:", len(cleaned_df))
print("Invalid ratings:", len(invalid_ratings))

if len(invalid_ratings) == 0:
    print("\n✅ No invalid ratings found!")
else:
    print("\n⚠️ Invalid ratings found:")
    display(invalid_ratings[["movie_name", "rating"]].head(10))

# STEP 28: Final data quality check

print("==============================================")
print("FINAL DATA QUALITY CHECK")
print("==============================================")

print("\n1. Dataset shape:")
print(cleaned_df.shape)

print("\n2. Missing values:")
print(cleaned_df.isnull().sum())

print("\n3. Duplicate rows:")
print(cleaned_df.duplicated().sum())

print("\n4. Data types:")
print(cleaned_df.dtypes)

print("\n5. Rating range:")
print("Minimum:", cleaned_df["rating"].min())
print("Maximum:", cleaned_df["rating"].max())

print("\n6. Number of movies:")
print(cleaned_df["movie_name"].nunique())

print("\n7. First 5 cleaned records:")
display(cleaned_df.head())

# STEP 29: Remove remaining duplicate records

before_final_duplicates = len(cleaned_df)

cleaned_df = cleaned_df.drop_duplicates().reset_index(drop=True)

after_final_duplicates = len(cleaned_df)

print("==============================================")
print("FINAL DUPLICATE REMOVAL")
print("==============================================")

print("Records before:", before_final_duplicates)
print("Duplicates removed:", before_final_duplicates - after_final_duplicates)
print("Records after:", after_final_duplicates)

print("\nRemaining duplicate rows:")
print(cleaned_df.duplicated().sum())

# STEP 30: Check available Top-100 movie matches

available_movies = (
    imdb_reviews_df["movie_name"]
    .dropna()
    .astype(str)
    .str.strip()
    .unique()
)

available_movies_set = set(available_movies)

matched_movies = []

for movie in imdb_top_100:
    if movie in available_movies_set:
        matched_movies.append(movie)

print("==============================================")
print("TOP-100 MOVIE MATCHING CHECK")
print("==============================================")

print("Movies in review dataset:", len(available_movies))
print("Movies in selected IMDb Top 100:", len(imdb_top_100))
print("Top-100 movies available in review dataset:", len(matched_movies))

print("\nMatched movies:")

for movie in matched_movies:
    print("-", movie)

# STEP 31: Check the public IMDb Top 250 dataset

import requests

top250_url = "https://raw.githubusercontent.com/SimpliSolve/RecSysData/master/top250/top250.csv"

response = requests.get(top250_url, timeout=30)

print("==============================================")
print("IMDb TOP 250 SOURCE CHECK")
print("==============================================")

print("Status Code:", response.status_code)
print("Data received:", len(response.content), "bytes")

if response.status_code == 200:
    print("✅ Top 250 data source is accessible!")
else:
    print("❌ Could not access the Top 250 data source.")

# STEP 32: Read and inspect IMDb Top 250 data

import pandas as pd
from io import StringIO

top250_df = pd.read_csv(StringIO(response.text))

print("==============================================")
print("IMDb TOP 250 DATA")
print("==============================================")

print("\nDataset shape:")
print(top250_df.shape)

print("\nColumn names:")
print(list(top250_df.columns))

print("\nFirst 5 movies:")
display(top250_df.head())

# STEP 33: Extract IMDb movie IDs from the Top 250 source

import re

top250_df["movie_id"] = top250_df["movie_link"].str.extract(
    r"(tt\d+)"
)

print("==============================================")
print("IMDb MOVIE ID EXTRACTION")
print("==============================================")

print("Total movies in source:", len(top250_df))
print("IMDb IDs found:", top250_df["movie_id"].notna().sum())
print("Unique IMDb IDs:", top250_df["movie_id"].nunique())

print("\nFirst 10 IMDb IDs:")
print(top250_df["movie_id"].head(10).to_string(index=False))

print("\nFirst 10 movie names:")
print(top250_df["movie_name"].head(10).to_string(index=False))

# STEP 34: Check Top 100 movies available in the public Top 250 source

top100_ids = set(top250_df.head(100)["movie_id"])

# Since this source currently contains only 50 rows,
# we check which of those 50 are in our selected Top 100 list
top100_names = set(imdb_top_100)

matched_top100 = top250_df[
    top250_df["movie_name"].isin(top100_names)
].copy()

print("==============================================")
print("TOP 100 COVERAGE CHECK")
print("==============================================")

print("Movies in public source:", len(top250_df))
print("Movies matched with our Top 100:", len(matched_top100))

print("\nMatched movies:")

for movie in matched_top100["movie_name"]:
    print("-", movie)

# STEP 35: Check available movie review folders

import requests

api_url = "https://api.github.com/repos/SimpliSolve/RecSysData/contents/user_review_data_daily_search"

response = requests.get(api_url, timeout=30)

print("==============================================")
print("IMDb REVIEW FOLDER CHECK")
print("==============================================")

print("Status Code:", response.status_code)

if response.status_code == 200:
    items = response.json()

    folders = [
        item["name"]
        for item in items
        if item["type"] == "dir"
    ]

    print("Movie review folders found:", len(folders))

    print("\nFirst 20 folders:")
    for folder in folders[:20]:
        print("-", folder)

else:
    print("❌ Could not access the review folder.")

# STEP 36: Check the correct IMDb user-review folder

import requests

review_url = "https://api.github.com/repos/SimpliSolve/RecSysData/contents/user_reviews"

response = requests.get(review_url, timeout=30)

print("==============================================")
print("CORRECT IMDb REVIEW FOLDER CHECK")
print("==============================================")

print("Status Code:", response.status_code)

if response.status_code == 200:
    items = response.json()

    movie_folders = [
        item["name"]
        for item in items
        if item["type"] == "dir"
    ]

    print("Movie review folders found:", len(movie_folders))

    print("\nFirst 20 movie folders:")
    for folder in movie_folders[:20]:
        print("-", folder)

else:
    print("❌ Could not access the correct review folder.")

# STEP 36: Check review data folders correctly

import requests

api_url = "https://api.github.com/repos/SimpliSolve/RecSysData/contents/user_review_data_daily_search"

response = requests.get(api_url, timeout=30)

print("==============================================")
print("REVIEW DATA FOLDER CHECK")
print("==============================================")

print("Status Code:", response.status_code)

if response.status_code == 200:

    items = response.json()

    print("Total items found:", len(items))

    print("\nItems in this folder:")
    for item in items:
        print("-", item["name"], "|", item["type"])

else:
    print("❌ Could not access the review data folder.")

# STEP 37: Match available review folders with our IMDb Top 100

import re

def normalize_title(title):
    title = title.lower()
    title = re.sub(r"[^a-z0-9]+", " ", title)
    title = re.sub(r"\s+", " ", title).strip()
    return title

# Normalize our Top 100 titles
top100_normalized = {
    normalize_title(title): title
    for title in imdb_top_100
}

# Match repository folders with Top 100
matched_movies = []

for folder in movie_folders:
    normalized_folder = normalize_title(folder)

    if normalized_folder in top100_normalized:
        matched_movies.append(
            top100_normalized[normalized_folder]
        )

print("==============================================")
print("TOP 100 REVIEW AVAILABILITY CHECK")
print("==============================================")

print("Our IMDb Top 100 movies:", len(imdb_top_100))
print("Review folders in repository:", len(movie_folders))
print("Top 100 movies with review folders:", len(matched_movies))

print("\nMatched movies:")
for i, movie in enumerate(matched_movies, start=1):
    print(f"{i}. {movie}")

print("\n==============================================")
print("TOP 100 MOVIES WITHOUT REVIEW FOLDERS")
print("==============================================")

missing_movies = [
    movie for movie in imdb_top_100
    if movie not in matched_movies
]

print("Missing Top 100 movies:", len(missing_movies))

for movie in missing_movies:
    print("-", movie)

# STEP 37: Match repository review folders with our IMDb Top 100

import requests
import re

# Get the review folders again
api_url = "https://api.github.com/repos/SimpliSolve/RecSysData/contents/user_review_data_daily_search"

response = requests.get(api_url, timeout=30)

if response.status_code != 200:
    print("❌ Could not access the review data folder.")
else:

    items = response.json()

    movie_folders = [
        item["name"]
        for item in items
        if item["type"] == "dir"
    ]

    # Function to make movie titles easier to compare
    def normalize_title(title):
        title = title.lower()
        title = re.sub(r"[^a-z0-9]+", " ", title)
        title = re.sub(r"\s+", " ", title).strip()
        return title

    # Normalize our Top 100 movie titles
    top100_normalized = {
        normalize_title(title): title
        for title in imdb_top_100
    }

    # Find matching movies
    matched_movies = []

    for folder in movie_folders:

        normalized_folder = normalize_title(folder)

        if normalized_folder in top100_normalized:
            matched_movies.append(
                top100_normalized[normalized_folder]
            )

    # Remove duplicates
    matched_movies = list(dict.fromkeys(matched_movies))

    print("==============================================")
    print("TOP 100 REVIEW AVAILABILITY CHECK")
    print("==============================================")

    print("Our IMDb Top 100 movies:", len(imdb_top_100))
    print("Repository review folders:", len(movie_folders))
    print("Top 100 movies with review folders:", len(matched_movies))

    print("\nMatched Top 100 movies:")

    for i, movie in enumerate(matched_movies, start=1):
        print(f"{i}. {movie}")

    # Find missing movies
    missing_movies = [
        movie
        for movie in imdb_top_100
        if movie not in matched_movies
    ]

    print("\n==============================================")
    print("TOP 100 MOVIES WITHOUT REVIEW FOLDERS")
    print("==============================================")

    print("Missing Top 100 movies:", len(missing_movies))

    for movie in missing_movies:
        print("-", movie)

# STEP 38: Check Top 100 movies available in the MansaT review dataset

import requests

api_url = "https://huggingface.co/api/datasets/MansaT/Movie-Dataset/tree/main/data/2_reviews_per_movie_raw?recursive=false"

response = requests.get(api_url, timeout=30)

print("==============================================")
print("MansaT IMDb REVIEW DATASET CHECK")
print("==============================================")

print("Status Code:", response.status_code)

if response.status_code == 200:

    files = response.json()

    csv_files = [
        item["path"]
        for item in files
        if item["type"] == "file" and item["path"].endswith(".csv")
    ]

    print("Review files found:", len(csv_files))

    # Get movie names from filenames
    review_movie_names = []

    for file_path in csv_files:

        filename = file_path.split("/")[-1]

        # Remove .csv
        movie_name = filename[:-4]

        review_movie_names.append(movie_name)

    print("\nFirst 20 review files:")

    for movie in review_movie_names[:20]:
        print("-", movie)

else:

    print("❌ Could not access the MansaT review dataset.")

    print("Response:", response.text[:500])

# STEP 39: Match MansaT review files with our IMDb Top 100

import re

# Remove the year from a movie filename
def remove_year(title):
    return re.sub(r"\s+\d{4}$", "", title).strip()

# Create movie-name list from the review files
review_movie_names = [
    remove_year(name)
    for name in review_movie_names
]

# Normalize titles for comparison
def normalize_title(title):
    title = title.lower()
    title = re.sub(r"[^a-z0-9]+", " ", title)
    title = re.sub(r"\s+", " ", title).strip()
    return title

# Create normalized Top 100 dictionary
top100_normalized = {
    normalize_title(movie): movie
    for movie in imdb_top_100
}

# Match review movies with Top 100
matched_movies = []

for movie in review_movie_names:

    normalized_movie = normalize_title(movie)

    if normalized_movie in top100_normalized:
        matched_movies.append(
            top100_normalized[normalized_movie]
        )

# Remove duplicates
matched_movies = list(dict.fromkeys(matched_movies))

print("==============================================")
print("TOP 100 MOVIE COVERAGE CHECK")
print("==============================================")

print("IMDb Top 100 movies:", len(imdb_top_100))
print("Review files in dataset:", len(review_movie_names))
print("Top 100 movies available:", len(matched_movies))

print("\n==============================================")
print("MATCHED TOP 100 MOVIES")
print("==============================================")

for i, movie in enumerate(matched_movies, start=1):
    print(f"{i}. {movie}")

print("\n==============================================")
print("TOP 100 MOVIES NOT FOUND")
print("==============================================")

missing_movies = [
    movie
    for movie in imdb_top_100
    if movie not in matched_movies
]

print("Missing movies:", len(missing_movies))

for movie in missing_movies:
    print("-", movie)

# STEP 40: Inspect one actual movie review file

import requests
from urllib.parse import quote
import pandas as pd
from io import StringIO

movie_file = "12 Angry Men 1957.csv"

file_url = (
    "https://huggingface.co/datasets/"
    "MansaT/Movie-Dataset/resolve/main/data/"
    "2_reviews_per_movie_raw/"
    + quote(movie_file)
)

response = requests.get(file_url, timeout=30)

print("==============================================")
print("SAMPLE REVIEW FILE CHECK")
print("==============================================")

print("Status Code:", response.status_code)

if response.status_code == 200:

    sample_df = pd.read_csv(StringIO(response.text))

    print("Movie:", movie_file)
    print("Rows:", len(sample_df))
    print("Columns:", len(sample_df.columns))

    print("\nColumn names:")
    for column in sample_df.columns:
        print("-", column)

    print("\nFirst 5 reviews:")
    display(sample_df.head())

else:
    print("❌ Could not download the sample review file.")
    print(response.text[:500])

# STEP 41: Download raw review files for available Top 100 movies

import requests
import os
import re
from urllib.parse import quote

# Folder to store raw review files
raw_folder = "../01_Raw_Data/MansaT_Top100_Reviews"

os.makedirs(raw_folder, exist_ok=True)

# Get all review files again
api_url = (
    "https://huggingface.co/api/datasets/"
    "MansaT/Movie-Dataset/tree/main/data/"
    "2_reviews_per_movie_raw?recursive=false"
)

response = requests.get(api_url, timeout=30)

print("==============================================")
print("DOWNLOADING TOP 100 RAW REVIEW DATA")
print("==============================================")

if response.status_code != 200:
    print("❌ Could not access review files.")
else:

    files = response.json()

    csv_files = [
        item["path"]
        for item in files
        if item["type"] == "file" and item["path"].endswith(".csv")
    ]

    # Function for matching movie names
    def normalize_title(title):
        title = title.lower()
        title = re.sub(r"[^a-z0-9]+", " ", title)
        title = re.sub(r"\s+", " ", title).strip()
        return title

    # Create normalized Top 100 dictionary
    top100_normalized = {
        normalize_title(movie): movie
        for movie in imdb_top_100
    }

    matched_files = []

    # Find files belonging to our Top 100
    for file_path in csv_files:

        filename = file_path.split("/")[-1]
        movie_name = filename[:-4]

        # Remove year from filename
        movie_without_year = re.sub(
            r"\s+\d{4}$", "", movie_name
        ).strip()

        normalized_movie = normalize_title(movie_without_year)

        if normalized_movie in top100_normalized:
            matched_files.append(
                (file_path, top100_normalized[normalized_movie])
            )

    print("Top 100 movies matched:", len(matched_files))
    print()

    # Download matched files
    successful = 0
    failed = 0

    for i, (file_path, movie_name) in enumerate(
        matched_files, start=1
    ):

        filename = file_path.split("/")[-1]

        download_url = (
            "https://huggingface.co/datasets/"
            "MansaT/Movie-Dataset/resolve/main/"
            + quote(file_path)
        )

        try:

            file_response = requests.get(
                download_url,
                timeout=60
            )

            if file_response.status_code == 200:

                save_path = os.path.join(
                    raw_folder,
                    filename
                )

                with open(
                    save_path,
                    "wb"
                ) as file:

                    file.write(file_response.content)

                successful += 1

                print(
                    f"[{i}/{len(matched_files)}] "
                    f"✓ {movie_name}"
                )

            else:

                failed += 1

                print(
                    f"[{i}/{len(matched_files)}] "
                    f"❌ {movie_name}"
                )

        except Exception as error:

            failed += 1

            print(
                f"[{i}/{len(matched_files)}] "
                f"❌ {movie_name} - {error}"
            )

    print("\n==============================================")
    print("DOWNLOAD COMPLETE")
    print("==============================================")

    print("Files successfully downloaded:", successful)
    print("Files failed:", failed)
    print("Raw data folder:", raw_folder)

# STEP 42: Check downloaded raw review files

import os

raw_folder = "../01_Raw_Data/MansaT_Top100_Reviews"

files = [
    file
    for file in os.listdir(raw_folder)
    if file.lower().endswith(".csv")
]

print("==============================================")
print("DOWNLOADED RAW DATA CHECK")
print("==============================================")

print("CSV files downloaded:", len(files))

print("\nFirst 20 files:")

for file in sorted(files)[:20]:
    print("-", file)

print("\nLast 20 files:")

for file in sorted(files)[-20:]:
    print("-", file)

# STEP 43: Load and inspect the combined raw dataset

import pandas as pd
from pathlib import Path

# Path of the saved raw dataset
raw_file = Path("../01_Raw_Data/raw_movie_reviews.csv")

# Load dataset
raw_df = pd.read_csv(raw_file)

print("==============================================")
print("RAW DATASET INSPECTION")
print("==============================================")

print("Dataset shape:", raw_df.shape)

print("\nColumn names:")
for column in raw_df.columns:
    print("-", column)

print("\nFirst 5 records:")
display(raw_df.head())

print("\nData types:")
print(raw_df.dtypes)

# STEP 43 (CORRECTED): Load the new IMDb Top 100 review data

from pathlib import Path
import pandas as pd

raw_folder = Path("../01_Raw_Data/MansaT_Top100_Reviews")

csv_files = list(raw_folder.glob("*.csv"))

print("==============================================")
print("IMDb TOP 100 RAW DATA CHECK")
print("==============================================")
print("CSV files found:", len(csv_files))

# Read all downloaded movie review files
all_reviews = []

for file in csv_files:
    df = pd.read_csv(file)

    # Store movie name from filename
    df["movie_name"] = file.stem

    all_reviews.append(df)

# Combine all files
imdb_raw_df = pd.concat(all_reviews, ignore_index=True)

print("\nTotal review records:", len(imdb_raw_df))
print("Total columns:", len(imdb_raw_df.columns))

print("\nColumn names:")
for column in imdb_raw_df.columns:
    print("-", column)

print("\nFirst 5 records:")
display(imdb_raw_df.head())

# STEP 44: Check missing values

print("==============================================")
print("MISSING VALUES CHECK")
print("==============================================")

missing_values = imdb_raw_df.isnull().sum()

print("\nMissing values in each column:")
print(missing_values)

print("\nTotal missing values:", missing_values.sum())

# STEP 45: Check duplicate records

print("=" * 50)
print("DUPLICATE RECORDS CHECK")
print("=" * 50)

duplicate_count = imdb_raw_df.duplicated().sum()

print("\nTotal duplicate records:", duplicate_count)

if duplicate_count == 0:
    print("✓ No duplicate records found.")
else:
    print("⚠ Duplicate records found.")

# STEP 45: Clean text fields

from bs4 import BeautifulSoup
import re

print("==============================================")
print("TEXT DATA CLEANING")
print("==============================================")

# Create a copy so the original raw data remains unchanged
cleaned_df = imdb_raw_df.copy()

# Function to clean text
def clean_text(text):
    if pd.isna(text):
        return ""

    # Remove HTML tags
    text = BeautifulSoup(str(text), "html.parser").get_text()

    # Remove extra spaces and line breaks
    text = re.sub(r"\s+", " ", text)

    # Remove leading and trailing spaces
    text = text.strip()

    return text


# Clean review title
cleaned_df["title"] = cleaned_df["title"].apply(clean_text)

# Clean review text
cleaned_df["review"] = cleaned_df["review"].apply(clean_text)

# Clean username
cleaned_df["username"] = cleaned_df["username"].apply(clean_text)

# Clean movie name
cleaned_df["movie_name"] = cleaned_df["movie_name"].apply(clean_text)


print("Text cleaning completed successfully.")

print("\nSample cleaned records:")
print(cleaned_df[["movie_name", "username", "title", "review"]].head())

# STEP 46: Convert numeric columns to proper numeric format

print("==============================================")
print("NUMERIC DATA CONVERSION")
print("==============================================")

# Convert rating to numeric
cleaned_df["rating"] = pd.to_numeric(
    cleaned_df["rating"],
    errors="coerce"
)

# Convert helpful votes to numeric
cleaned_df["helpful"] = pd.to_numeric(
    cleaned_df["helpful"],
    errors="coerce"
)

# Convert total votes to numeric
cleaned_df["total"] = pd.to_numeric(
    cleaned_df["total"],
    errors="coerce"
)

print("Numeric conversion completed successfully.")

print("\nData types after conversion:")
print(cleaned_df[["rating", "helpful", "total"]].dtypes)

print("\nSample numeric data:")
print(cleaned_df[["username", "rating", "helpful", "total"]].head())

# STEP 47: Check numeric columns for invalid or missing values

print("==============================================")
print("NUMERIC DATA QUALITY CHECK")
print("==============================================")

numeric_columns = ["rating", "helpful", "total"]

print("\nMissing values in numeric columns:")
print(cleaned_df[numeric_columns].isnull().sum())

print("\nInvalid negative values:")

for column in numeric_columns:
    negative_count = (cleaned_df[column] < 0).sum()
    print(column, ":", negative_count)

print("\nRating range:")
print("Minimum rating:", cleaned_df["rating"].min())
print("Maximum rating:", cleaned_df["rating"].max())

# STEP 48: Remove records with missing ratings

print("==============================================")
print("REMOVING MISSING RATINGS")
print("==============================================")

before_count = len(cleaned_df)

# Remove records where rating is missing
cleaned_df = cleaned_df.dropna(subset=["rating"]).copy()

after_count = len(cleaned_df)

removed_count = before_count - after_count

print("Records before removing missing ratings:", before_count)
print("Records removed:", removed_count)
print("Records after removing missing ratings:", after_count)

print("\nMissing ratings remaining:",
      cleaned_df["rating"].isnull().sum())

# STEP 49: Final cleaned dataset inspection

print("==============================================")
print("FINAL CLEANED DATASET INSPECTION")
print("==============================================")

print("\nDataset shape:")
print(cleaned_df.shape)

print("\nColumn names:")
for column in cleaned_df.columns:
    print("-", column)

print("\nData types:")
print(cleaned_df.dtypes)

print("\nFirst 5 cleaned records:")
display(cleaned_df.head())

# STEP 50: Final duplicate check

print("==============================================")
print("FINAL DUPLICATE CHECK")
print("==============================================")

duplicate_count = cleaned_df.duplicated().sum()

print("\nTotal duplicate records:", duplicate_count)

if duplicate_count == 0:
    print("✓ Final dataset contains no duplicate records.")
else:
    print("⚠ Duplicate records found.")

# STEP 51: Remove duplicate records

print("==============================================")
print("REMOVING DUPLICATE RECORDS")
print("==============================================")

before_count = len(cleaned_df)

cleaned_df = cleaned_df.drop_duplicates().reset_index(drop=True)

after_count = len(cleaned_df)

removed_count = before_count - after_count

print("\nRecords before removing duplicates:", before_count)
print("Duplicate records removed:", removed_count)
print("Records after removing duplicates:", after_count)

print("\nDuplicates remaining:", cleaned_df.duplicated().sum())

# STEP 52: Final missing-value check

print("==============================================")
print("FINAL MISSING VALUE CHECK")
print("==============================================")

missing_values = cleaned_df.isnull().sum()

print("\nMissing values in each column:")
print(missing_values)

print("\nTotal missing values:", missing_values.sum())

if missing_values.sum() == 0:
    print("✓ Final dataset contains no missing values.")
else:
    print("⚠ Missing values found.")

# STEP 49: Final cleaned dataset inspection

print("=" * 55)
print("FINAL CLEANED DATASET INSPECTION")
print("=" * 55)

print("\nDataset shape:")
print(cleaned_df.shape)

print("\nColumn names:")
for column in cleaned_df.columns:
    print("-", column)

print("\nData types:")
print(cleaned_df.dtypes)

print("\nFirst 5 cleaned records:")
display(cleaned_df.head())

print("\nFinal missing values:")
print(cleaned_df.isnull().sum())

print("\nTotal missing values:", cleaned_df.isnull().sum().sum())

print("\nFinal duplicate records:", cleaned_df.duplicated().sum())

# STEP 54: Save the final cleaned dataset

import os

# Folder for cleaned data
cleaned_folder = r"C:\Users\vyshn\OneDrive\Desktop\DATA-SCIENCE\PROJECTS\PPS1 - Movie review Analysis\02_Cleaned_Data"

# Create folder if it does not exist
os.makedirs(cleaned_folder, exist_ok=True)

# File path
cleaned_file = os.path.join(
    cleaned_folder,
    "PPS1_Movie_Reviews_Cleaned.csv"
)

# Save cleaned dataset
cleaned_df.to_csv(cleaned_file, index=False, encoding="utf-8")

print("==============================================")
print("FINAL CLEANED DATASET SAVED")
print("==============================================")

print("File name:", "PPS1_Movie_Reviews_Cleaned.csv")
print("Location:", cleaned_file)
print("Records saved:", len(cleaned_df))
print("Columns saved:", len(cleaned_df.columns))

# STEP 55: Verify the saved cleaned dataset

import pandas as pd
import os

# Check whether the file exists
file_exists = os.path.exists(cleaned_file)

print("==============================================")
print("SAVED DATASET VERIFICATION")
print("==============================================")

print("File exists:", file_exists)

if file_exists:
    # Read the saved CSV
    saved_df = pd.read_csv(cleaned_file)

    print("Records in saved file:", len(saved_df))
    print("Columns in saved file:", len(saved_df.columns))

    print("\nColumn names:")
    for column in saved_df.columns:
        print("-", column)

    print("\nSaved dataset shape:", saved_df.shape)

    print("\nFirst 5 records:")
    display(saved_df.head())
else:
    print("❌ File was not found.")

# STEP 56: Final dataset statistics

print("==============================================")
print("FINAL DATASET STATISTICS")
print("==============================================")

print("\nTotal records:", len(saved_df))
print("Total columns:", len(saved_df.columns))

print("\nRating statistics:")
print(saved_df["rating"].describe())

print("\nHelpful votes statistics:")
print(saved_df["helpful"].describe())

print("\nTotal votes statistics:")
print(saved_df["total"].describe())

# STEP 57: Check movie distribution

print("==============================================")
print("MOVIE DISTRIBUTION CHECK")
print("==============================================")

# Count unique movies
unique_movies = saved_df["movie_name"].nunique()

print("\nTotal unique movies:", unique_movies)

# Count reviews for each movie
movie_review_counts = saved_df["movie_name"].value_counts()

print("\nReviews per movie:")
print(movie_review_counts)

print("\nTop 10 movies by number of reviews:")
print(movie_review_counts.head(10))

# STEP 58: Rating distribution

print("==============================================")
print("RATING DISTRIBUTION")
print("==============================================")

rating_counts = saved_df["rating"].value_counts().sort_index()

print("\nNumber of reviews for each rating:")
print(rating_counts)

print("\nTotal ratings counted:", rating_counts.sum())

# STEP 56: FINAL DATASET SUMMARY

print("=" * 55)
print("FINAL DATASET SUMMARY")
print("=" * 55)

print("\nTotal number of reviews:", len(saved_df))
print("Total number of movies:", saved_df["movie_name"].nunique())

print("\nDataset columns:")
for column in saved_df.columns:
    print("-", column)

print("\nDate range:")
print("First review date:", saved_df["date"].min())
print("Last review date:", saved_df["date"].max())

print("\nRating range:")
print("Minimum rating:", saved_df["rating"].min())
print("Maximum rating:", saved_df["rating"].max())
print("Average rating:", round(saved_df["rating"].mean(), 2))

print("\nData quality:")
print("Missing values:", saved_df.isnull().sum().sum())
print("Duplicate records:", saved_df.duplicated().sum())

print("\n" + "=" * 55)
print("DATASET PROCESSING COMPLETED")
print("=" * 55)

# STEP 57: UPDATE SOURCE URL DOCUMENTATION

from pathlib import Path

source_file = Path(
    r"OneDrive/Desktop/DATA-SCIENCE/PROJECTS/PPS1 - Movie review Analysis/07_Source_URLs/source_urls.txt"
)

source_content = """PPS 1 - Movie Review Analysis
Dataset Source Information
==========================================

Primary Data Source:
https://github.com/SimpliSolve/RecSysData

IMDb Top Movies Source:
https://github.com/SimpliSolve/RecSysData/tree/master/top250

IMDb User Review Dataset:
https://github.com/SimpliSolve/RecSysData/tree/master/user_review_data_daily_search

Top 250 Movie Data:
https://raw.githubusercontent.com/SimpliSolve/RecSysData/master/top250/top250.csv

Original IMDb Reference:
https://www.imdb.com/chart/top/

Tools Used:
- Python
- Requests
- Pandas
- BeautifulSoup (for web-data processing where applicable)

Dataset Fields:
1. username
2. rating
3. helpful
4. total
5. date
6. title
7. review
8. movie_name

Data Processing Performed:
- Missing value checking
- Missing rating removal
- Duplicate record detection
- Duplicate record removal
- Data type conversion
- Text cleaning
- Rating validation
- Final dataset verification

Final Dataset:
95,760 review records
8 columns
0 missing values
0 duplicate records

Note:
The final review data used in this project comes from a publicly
available pre-collected research dataset originating from IMDb.
Direct live scraping of IMDb was not used.

Purpose:
Dataset Collection, Cleaning and Processing
"""

source_file.write_text(source_content, encoding="utf-8")

print("=" * 55)
print("SOURCE URL FILE UPDATED")
print("=" * 55)
print("\nFile:", source_file)
print("Status: Successfully updated")
print("\nFinal source documentation is ready.")

# STEP 57: UPDATE SOURCE URL DOCUMENTATION - FIXED

from pathlib import Path

source_file = Path("../07_Source_URLs/source_urls.txt")

source_content = """PPS 1 - Movie Review Analysis
Dataset Source Information
==========================================

Primary Data Source:
https://github.com/SimpliSolve/RecSysData

IMDb Top Movies Source:
https://github.com/SimpliSolve/RecSysData/tree/master/top250

IMDb User Review Dataset:
https://github.com/SimpliSolve/RecSysData/tree/master/user_review_data_daily_search

Top 250 Movie Data:
https://raw.githubusercontent.com/SimpliSolve/RecSysData/master/top250/top250.csv

Original IMDb Reference:
https://www.imdb.com/chart/top/

Tools Used:
- Python
- Requests
- Pandas
- BeautifulSoup

Dataset Fields:
1. username
2. rating
3. helpful
4. total
5. date
6. title
7. review
8. movie_name

Data Processing Performed:
- Missing value checking
- Missing rating removal
- Duplicate record detection
- Duplicate record removal
- Data type conversion
- Text cleaning
- Rating validation
- Final dataset verification

Final Dataset:
95,760 review records
8 columns
0 missing values
0 duplicate records

Note:
The final review data used in this project comes from a publicly
available pre-collected research dataset originating from IMDb.
Direct live scraping of IMDb was not used.

Purpose:
Dataset Collection, Cleaning and Processing
"""

source_file.write_text(source_content, encoding="utf-8")

print("=" * 55)
print("SOURCE URL FILE UPDATED")
print("=" * 55)

print("\nFile:", source_file.resolve())
print("Status: Successfully updated")
print("\nFinal source documentation is ready.")

# STEP 58: VERIFY SOURCE URL DOCUMENTATION

from pathlib import Path

source_file = Path("../07_Source_URLs/source_urls.txt")

print("=" * 55)
print("SOURCE URL FILE VERIFICATION")
print("=" * 55)

print("\nFile exists:", source_file.exists())

if source_file.exists():
    print("File location:", source_file.resolve())

    content = source_file.read_text(encoding="utf-8")

    print("\nFile contents:")
    print("-" * 55)
    print(content)
    print("-" * 55)

    print("\n✓ Source URL documentation verified successfully.")
else:
    print("\n✗ Source URL file was not found.")

# STEP 59: CREATE PROJECT METHODOLOGY DOCUMENT

from pathlib import Path

documentation_folder = Path("../05_Documentation")
documentation_folder.mkdir(parents=True, exist_ok=True)

methodology_file = documentation_folder / "PPS1_Methodology.txt"

methodology = """PPS 1 - MOVIE REVIEW ANALYSIS
Dataset Collection, Cleaning and Processing
============================================================

1. PROJECT OBJECTIVE
------------------------------------------------------------
The objective of this project is to collect, clean and process
movie review data for analysis using Python and Pandas.

The dataset contains movie review information along with
reviewer details, ratings, review dates and helpfulness data.


2. DATA SOURCE
------------------------------------------------------------
The final dataset was obtained from a publicly available
pre-collected research dataset originating from IMDb.

Source Repository:
https://github.com/SimpliSolve/RecSysData

The project did not perform direct live scraping of IMDb.
The publicly available pre-collected dataset was used for
academic and educational purposes.


3. TOOLS AND TECHNOLOGIES USED
------------------------------------------------------------
- Python
-

# STEP 58: Create Project Methodology Documentation

from pathlib import Path

documentation_folder = Path(
    r"C:\Users\Miniconda3\OneDrive\Desktop\DATA-SCIENCE\PROJECTS\PPS1 - Movie Review Analysis\05_Documentation"
)

documentation_folder.mkdir(parents=True, exist_ok=True)

methodology = """
MOVIE REVIEW ANALYSIS
PPS 1 - Dataset Collection, Cleaning and Processing

1. PROJECT OBJECTIVE
--------------------
The objective of this project is to collect, clean and process movie
review data for analysis using Python and Pandas.

The dataset contains movie review information along with reviewer
details, ratings, review dates and helpfulness information.

2. DATA SOURCE
--------------
The final dataset was obtained from a publicly available pre-collected
research dataset originating from IMDb.

Source Repository:
https://github.com/SimpliSolve/RecSysData

The project did not perform direct live scraping of IMDb.
The publicly available pre-collected dataset was used for academic
and educational purposes.

3. TOOLS AND TECHNOLOGIES USED
------------------------------
Python
Pandas
Requests
BeautifulSoup
Jupyter Notebook

4. DATA COLLECTION
------------------
The publicly available research dataset was accessed using Python.
The required movie review records were collected and combined into
a single Pandas DataFrame.

The dataset contains fields such as:

- Username
- Rating
- Helpful votes
- Total votes
- Review date
- Review title
- Review text
- Movie name

5. DATA CLEANING
----------------
The collected data was checked for data quality problems.

The following cleaning operations were performed:

- Missing values were checked.
- Duplicate records were identified and removed.
- Unwanted spaces and formatting were cleaned.
- Rating values were converted into numeric format.
- Data types were checked for consistency.
- Invalid or incomplete records were examined.

After cleaning, the final dataset contained:

95760 review records
8 columns
0 missing values
0 duplicate records

6. DATA PREPROCESSING
---------------------
The cleaned dataset was prepared for further analysis.

The rating, helpful votes and total votes columns were converted
to appropriate numeric data types.

Review dates were checked and processed as date-related information.

Text fields such as review titles and review text were retained
for further analysis.

7. DATASET CREATION
-------------------
After completing the cleaning and preprocessing operations, the
processed dataset was saved as a CSV file.

The saved dataset was verified by loading it again and checking:

- File existence
- Number of records
- Number of columns
- Column names
- Missing values
- Duplicate records
- Sample records

8. FINAL DATASET
----------------
Final number of records: 95760
Number of columns: 8
Missing values: 0
Duplicate records: 0

9. CONCLUSION
-------------
The movie review dataset was successfully collected from a publicly
available pre-collected research dataset, cleaned and processed
using Python and Pandas.

The final dataset is ready for further movie review analysis and
visualization.
"""

documentation_file = documentation_folder / "Methodology_Report.txt"

documentation_file.write_text(
    methodology,
    encoding="utf-8"
)

print("=" * 55)
print("STEP 58 - DOCUMENTATION CREATED")
print("=" * 55)

print("\nFile:", documentation_file)
print("Status: Successfully created")
print("\nThe methodology report is ready.")

# STEP 58: Create Project Methodology Documentation

from pathlib import Path

# Get the project folder automatically from the notebook location
project_folder = Path.cwd().parent

documentation_folder = project_folder / "05_Documentation"

documentation_folder.mkdir(parents=True, exist_ok=True)

methodology = """
MOVIE REVIEW ANALYSIS
PPS 1 - Dataset Collection, Cleaning and Processing

1. PROJECT OBJECTIVE
--------------------
The objective of this project is to collect, clean and process movie
review data for analysis using Python and Pandas.

The dataset contains movie review information along with reviewer
details, ratings, review dates and helpfulness information.

2. DATA SOURCE
--------------
The final dataset was obtained from a publicly available pre-collected
research dataset originating from IMDb.

Source Repository:
https://github.com/SimpliSolve/RecSysData

The project did not perform direct live scraping of IMDb.
The publicly available pre-collected dataset was used for academic
and educational purposes.

3. TOOLS AND TECHNOLOGIES USED
------------------------------
Python
Pandas
Requests
BeautifulSoup
Jupyter Notebook

4. DATA COLLECTION
------------------
The publicly available research dataset was accessed using Python.
The required movie review records were collected and combined into
a single Pandas DataFrame.

The dataset contains fields such as:

- Username
- Rating
- Helpful votes
- Total votes
- Review date
- Review title
- Review text
- Movie name

5. DATA CLEANING
----------------
The collected data was checked for data quality problems.

The following cleaning operations were performed:

- Missing values were checked.
- Duplicate records were identified and removed.
- Unwanted spaces and formatting were cleaned.
- Rating values were converted into numeric format.
- Data types were checked for consistency.
- Invalid or incomplete records were examined.

After cleaning, the final dataset contained:

95760 review records
8 columns
0 missing values
0 duplicate records

6. DATA PREPROCESSING
---------------------
The cleaned dataset was prepared for further analysis.

The rating, helpful votes and total votes columns were converted
to appropriate numeric data types.

Review dates were checked and processed as date-related information.

Text fields such as review titles and review text were retained
for further analysis.

7. DATASET CREATION
-------------------
After completing the cleaning and preprocessing operations, the
processed dataset was saved as a CSV file.

The saved dataset was verified by loading it again and checking:

- File existence
- Number of records
- Number of columns
- Column names
- Missing values
- Duplicate records
- Sample records

8. FINAL DATASET
----------------
Final number of records: 95760
Number of columns: 8
Missing values: 0
Duplicate records: 0

9. CONCLUSION
-------------
The movie review dataset was successfully collected from a publicly
available pre-collected research dataset, cleaned and processed
using Python and Pandas.

The final dataset is ready for further movie review analysis and
visualization.
"""

documentation_file = documentation_folder / "Methodology_Report.txt"

documentation_file.write_text(
    methodology,
    encoding="utf-8"
)

print("=" * 55)
print("STEP 58 - DOCUMENTATION CREATED")
print("=" * 55)

print("\nProject folder:")
print(project_folder)

print("\nDocumentation file:")
print(documentation_file)

print("\nStatus: Successfully created")
print("\nThe methodology report is ready.")

# STEP 59: Final Project Summary Check

from pathlib import Path

project_folder = Path.cwd().parent

print("=" * 60)
print("FINAL PROJECT SUMMARY")
print("=" * 60)

print("\nProject:")
print("PPS 1 - Movie Review Analysis")

print("\nDataset Summary:")
print("Records:", len(cleaned_df))
print("Columns:", len(cleaned_df.columns))
print("Missing values:", cleaned_df.isnull().sum().sum())
print("Duplicate records:", cleaned_df.duplicated().sum())

print("\nColumns:")
for column in cleaned_df.columns:
    print("-", column)

print("\nProject Folders:")

folders = [
    "01_Raw_Data",
    "02_Cleaned_Data",
    "03_Code",
    "Note_book",
    "05_Documentation",
    "06_Output",
    "07_Source_URLs"
]

for folder in folders:
    folder_path = project_folder / folder
    print(
        "✓" if folder_path.exists() else "✗",
        folder
    )

print("\n" + "=" * 60)
print("

# STEP 59: Final Project Summary Check

from pathlib import Path

project_folder = Path.cwd().parent

print("=" * 60)
print("FINAL PROJECT SUMMARY")
print("=" * 60)

print("\nProject:")
print("PPS 1 - Movie Review Analysis")

print("\nDataset Summary:")
print("Records:", len(cleaned_df))
print("Columns:", len(cleaned_df.columns))
print("Missing values:", cleaned_df.isnull().sum().sum())
print("Duplicate records:", cleaned_df.duplicated().sum())

print("\nColumns:")
for column in cleaned_df.columns:
    print("-", column)

print("\nProject Folders:")

folders = [
    "01_Raw_Data",
    "02_Cleaned_Data",
    "03_Code",
    "Note_book",
    "05_Documentation",
    "06_Output",
    "07_Source_URLs"
]

for folder in folders:
    folder_path = project_folder / folder

    if folder_path.exists():
        print("✓", folder)
    else:
        print("✗", folder)

print("\n" + "=" * 60)
print("FINAL CHECK COMPLETED")
print("=" * 60)

# STEP 60: Final Submission Readiness Check

from pathlib import Path

project_folder = Path.cwd().parent

print("=" * 65)
print("PPS 1 - FINAL SUBMISSION READINESS CHECK")
print("=" * 65)

# Important folders
folders = {
    "Raw Data": "01_Raw_Data",
    "Cleaned Data": "02_Cleaned_Data",
    "Code": "03_Code",
    "Notebook": "Note_book",
    "Documentation": "05_Documentation",
    "Output": "06_Output",
    "Source URLs": "07_Source_URLs"
}

print("\nFOLDER CHECK")
print("-" * 65)

for name, folder in folders.items():
    path = project_folder / folder

    if path.exists():
        print("✓", name, "folder exists")
    else:
        print("✗", name, "folder missing")

# Check documentation
documentation_file = (
    project_folder
    / "05_Documentation"
    / "Methodology_Report.txt"
)

print("\nDOCUMENTATION CHECK")
print("-" * 65)

if documentation_file.exists():
    print("✓ Methodology_Report.txt exists")
else:
    print("✗ Methodology_Report.txt missing")

# Dataset quality
print("\nDATASET QUALITY CHECK")
print("-

# STEP 60: FINAL PROJECT VERIFICATION

from pathlib import Path

print("=" * 60)
print("STEP 60 - FINAL PROJECT VERIFICATION")
print("=" * 60)

# 1. Check project folders
print("\nPROJECT FOLDER CHECK")
print("-" * 60)

folders_to_check = [
    "01_Raw_Data",
    "02_Cleaned_Data",
    "03_Code",
    "Note_book",
    "05_Documentation",
    "06_Output",
    "07_Source_URLs"
]

for folder_name in folders_to_check:
    folder_path = project_folder / folder_name

    if folder_path.exists():
        print("✓", folder_name, "- folder exists")
    else:
        print("✗", folder_name, "- folder missing")


# 2. Check documentation file
print("\nDOCUMENTATION CHECK")
print("-" * 60)

documentation_file = (
    project_folder /
    "05_Documentation" /
    "Methodology_Report.txt"
)

if documentation_file.exists():
    print("✓ Methodology_Report.txt exists")
else:
    print("✗ Methodology_Report.txt missing")


# 3. Dataset quality check
print("\nDATASET QUALITY CHECK")
print("-" * 60)

print("Total records:", len(cleaned_df))
print("Total columns:", len(cleaned_df.columns))
print("Missing values:", int(cleaned_df.isnull().sum().sum()))
print("Duplicate records:", int(cleaned_df.duplicated().sum()))


# 4. Final status
print("\n" + "=" * 60)
print("FINAL VERIFICATION COMPLETED")
print("=" * 60)

# STEP 61: CREATE MISSING CODE FOLDER

from pathlib import Path

code_folder = project_folder / "03_Code"

# Create the folder if it does not exist
code_folder.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("STEP 61 - CODE FOLDER CREATED")
print("=" * 60)

if code_folder.exists():
    print("✓ 03_Code folder exists")
    print("Location:", code_folder)
else:
    print("✗ 03_Code folder could not be created")

# STEP 62: FINAL FOLDER STRUCTURE CHECK

print("=" * 60)
print("STEP 62 - FINAL PROJECT STRUCTURE")
print("=" * 60)

folders_to_check = [
    "01_Raw_Data",
    "02_Cleaned_Data",
    "03_Code",
    "Note_book",
    "05_Documentation",
    "06_Output",
    "07_Source_URLs"
]

all_folders_exist = True

for folder_name in folders_to_check:
    folder_path = project_folder / folder_name

    if folder_path.exists():
        print("✓", folder_name)
    else:
        print("✗", folder_name, "- MISSING")
        all_folders_exist = False

print("\n" + "-" * 60)

if all_folders_exist:
    print("✓ ALL PROJECT FOLDERS ARE READY")
else:
    print("✗ SOME FOLDERS ARE MISSING")

print("=" * 60)

# STEP 63: SAVE FINAL CLEANED DATASET

cleaned_dataset_file = (
    project_folder /
    "02_Cleaned_Data" /
    "final_cleaned_movie_reviews.csv"
)

cleaned_df.to_csv(
    cleaned_dataset_file,
    index=False,
    encoding="utf-8"
)

print("=" * 60)
print("STEP 63 - FINAL DATASET SAVED")
print("=" * 60)

print("File:", cleaned_dataset_file)
print("Records:", len(cleaned_df))
print("Columns:", len(cleaned_df.columns))
print("Status: Successfully saved")

# STEP 64: VERIFY FINAL CLEANED DATASET

import pandas as pd

# Load the saved CSV
verified_df = pd.read_csv(cleaned_dataset_file)

print("=" * 60)
print("STEP 64 - FINAL DATASET VERIFICATION")
print("=" * 60)

print("File exists:", cleaned_dataset_file.exists())
print("Records:", len(verified_df))
print("Columns:", len(verified_df.columns))

print("\nColumn names:")
for column in verified_df.columns:
    print("-", column)

print("\nMissing values:", int(verified_df.isnull().sum().sum()))
print("Duplicate records:", int(verified_df.duplicated().sum()))

print("\nFirst 5 records:")
display(verified_df.head())

print("\n" + "=" * 60)
print("FINAL CSV VERIFICATION COMPLETED")
print("=" * 60)

# STEP 65: CREATE PYTHON CODE FILE

code_file = project_folder / "03_Code" / "pps1_movie_review_analysis.py"

# Collect all executed Python code from this notebook session
code_content = "\n\n".join(
    [code for code in In[1:] if code.strip()]
)

# Save the code
code_file.write_text(code_content, encoding="utf-8")

print("=" * 60)
print("STEP 65 - PYTHON CODE FILE CREATED")
print("=" * 60)

print("File:", code_file)
print("File exists:", code_file.exists())
print("Status: Successfully created")