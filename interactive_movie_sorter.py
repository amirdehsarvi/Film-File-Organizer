import os
import re
from imdb import IMDb

# Function to clean and format movie name from the file name
def clean_movie_name(file_name):
    movie_name = os.path.splitext(file_name)[0]
    patterns_to_remove = [
        r'\b\d{3,4}p\b', r'\bBluRay\b', r'\bWEB\b', r'\bHD\b', r'\bSD\b', 
        r'\bAAC\b', r'\bx264\b', r'\bx265\b', r'\bXviD\b', r'\bHDRip\b', 
        r'\bDVDRip\b', r'\bBRRip\b', r'\bH264\b', r'\b10bit\b', r'\b8bit\b', 
        r'\bHEVC\b', r'\b@lubokvideo\b', r'\bSoftSub\b', r'\bFW\b', r'\bDream\b',
        r'\bVeDeTT\b', r'\bAvaMovie\b'
    ]
    for pattern in patterns_to_remove:
        movie_name = re.sub(pattern, '', movie_name, flags=re.IGNORECASE)
    movie_name = re.sub(r'[_\.]', ' ', movie_name)
    movie_name = re.sub(r'\s+', ' ', movie_name).strip()
    movie_name = re.sub(r'\b\d{4}\b.*$', '', movie_name).strip()
    return movie_name

# Function to get movie data from IMDb
def get_movie_data(movie_name):
    ia = IMDb()
    search_results = ia.search_movie(movie_name)
    if search_results:
        return ia.get_movie(search_results[0].movieID)  # Return the first search result
    return None

# Function to get movie data by IMDb ID
def get_movie_data_by_id(imdb_id):
    ia = IMDb()
    imdb_id = imdb_id.replace('tt', '')  # Remove the 'tt' prefix
    return ia.get_movie(imdb_id)

# Function to create directory structure and move files
def organize_movie(file, movie_data, folder_path):
    directors = movie_data.get('director', [])
    director_names = ', '.join(director['name'] for director in directors) if directors else "Unknown"
    release_year = movie_data.get('year', 'Unknown')
    movie_name = movie_data.get('title', 'Unknown')
    
    dir_structure = os.path.join(folder_path, director_names, f"{release_year} - {movie_name}")
    
    if not os.path.exists(dir_structure):
        os.makedirs(dir_structure)
    
    source_file_path = file
    dest_file_path = os.path.join(dir_structure, os.path.basename(file))
    
    os.rename(source_file_path, dest_file_path)
    
    new_file_name = f"{movie_name}{os.path.splitext(file)[1]}"
    os.rename(dest_file_path, os.path.join(dir_structure, new_file_name))

    # Delete the now empty folders
    parent_dir = os.path.dirname(source_file_path)
    while parent_dir != folder_path and not os.listdir(parent_dir):
        os.rmdir(parent_dir)
        parent_dir = os.path.dirname(parent_dir)

# Function to get all files in the folder, including subfolders
def get_all_files(folder_path):
    all_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            all_files.append(os.path.join(root, file))
    return all_files

# Get folder path from user
folder_path = input("Please enter the folder path: ")

# Get list of all files in the folder and subfolders
files = get_all_files(folder_path)

# Iterate through each file in the folder
for file in files:
    if os.path.basename(file).startswith('.'):
        continue

    movie_name = clean_movie_name(os.path.basename(file))
    print(f"Searching for movie: {movie_name}")

    movie_data = get_movie_data(movie_name)

    while True:
        if movie_data:
            imdb_url = f"https://www.imdb.com/title/tt{movie_data.movieID}/"
            print(f"Found: {movie_data.get('title')} ({movie_data.get('year')}) directed by {', '.join(director['name'] for director in movie_data.get('director', [{'name': 'Unknown'}]))}")
            print(f"IMDb URL: {imdb_url}")
        else:
            print(f"No data found for movie: {movie_name}")
        
        confirm = input("Is this the correct movie? (y/n/skip): ").strip().lower()
        
        if confirm == 'y':
            break
        elif confirm == 'skip':
            print(f"Skipping {file}")
            movie_data = None
            break
        else:
            alternative_title = input("Enter an alternative title or IMDb ID for the search: ").strip()
            if alternative_title.startswith("tt"):
                movie_data = get_movie_data_by_id(alternative_title)
            else:
                movie_data = get_movie_data(alternative_title)

    if movie_data:
        organize_movie(file, movie_data, folder_path)
        print(f"Moved and renamed file: {os.path.basename(file)}")

print("Organization complete.")
