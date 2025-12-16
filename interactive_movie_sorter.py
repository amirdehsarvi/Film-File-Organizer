import os
import re
# pip install imdbpy beautifulsoup4 requests lxml
from imdb import Cinemagoer
import readline
import glob
import requests
from bs4 import BeautifulSoup
import json
import time

# Enable tab completion for folder paths
def complete_path(text, state):
    return (glob.glob(text + '*') + [None])[state]

readline.set_completer_delims('')
readline.parse_and_bind("tab: complete")
readline.set_completer(complete_path)

# Function to clean and format movie name from the file name
def clean_movie_name(file_name):
    movie_name = os.path.splitext(file_name)[0]
    
    # Extract year if it appears BEFORE the movie name (like "2024 The Other Place")
    year_match = re.match(r'^\s*(19\d{2}|20\d{2})\s+(.+)$', movie_name)
    if year_match:
        year = year_match.group(1)
        movie_name = year_match.group(2)
    else:
        # Look for year elsewhere in the filename
        year_match = re.search(r'\b(19\d{2}|20\d{2})\b', movie_name)
        year = year_match.group(1) if year_match else None
        # Remove year and quality markers only if they're at the end
        movie_name = re.sub(r'\s*\b(19\d{2}|20\d{2})\b\s*.*$', '', movie_name)
    
    # Remove common quality patterns
    patterns_to_remove = [
        r'\b\d{3,4}p\b', r'\bBluRay\b', r'\bWEB-DL\b', r'\bWEB\b', r'\bHD\b', r'\bSD\b',
        r'\bAAC\b', r'\bx264\b', r'\bx265\b', r'\bXviD\b', r'\bHDRip\b',
        r'\bDVDRip\b', r'\bBRRip\b', r'\bH264\b', r'\b10bit\b', r'\b8bit\b',
        r'\bHEVC\b', r'\b@lubokvideo\b', r'\bSoftSub\b', r'\bFW\b', r'\bDream\b',
        r'\bVeDeTT\b', r'\bAvaMovie\b'
    ]
    for pattern in patterns_to_remove:
        movie_name = re.sub(pattern, '', movie_name, flags=re.IGNORECASE)
    
    # Replace dots and underscores with spaces
    movie_name = re.sub(r'[_\.]', ' ', movie_name)
    
    # Clean up whitespace
    movie_name = re.sub(r'\s+', ' ', movie_name).strip()
    
    return movie_name, year

# Function to scrape director from IMDb webpage
def scrape_director_from_imdb(imdb_id):
    """Scrape director information from IMDb webpage when API doesn't have it"""
    try:
        url = f"https://www.imdb.com/title/tt{imdb_id}/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try to find JSON-LD data
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and 'director' in data:
                    directors = data['director']
                    if isinstance(directors, list):
                        return [d.get('name') for d in directors if isinstance(d, dict) and 'name' in d]
                    elif isinstance(directors, dict) and 'name' in directors:
                        return [directors['name']]
            except (json.JSONDecodeError, KeyError, AttributeError):
                continue
        
        # Fallback: Try to find director in the page content
        director_section = soup.find('li', {'data-testid': 'title-pc-principal-credit'})
        if director_section:
            director_links = director_section.find_all('a', {'class': 'ipc-metadata-list-item__list-content-item'})
            if director_links:
                return [link.get_text(strip=True) for link in director_links]
        
    except Exception as e:
        print(f"  Warning: Could not scrape director info: {e}")
    
    return None

# Function to find IMDb ID by searching IMDb website
def find_imdb_id_from_web(movie_name, year=None):
    """Search IMDb website directly to find movie ID"""
    try:
        url = "https://www.imdb.com/find/"
        params = {'q': movie_name, 'exact': 'on', 'title_type': 'movie'}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find movie links
        movie_links = soup.find_all('a', href=lambda h: h and '/title/tt' in h)
        
        for link in movie_links[:10]:
            href = link.get('href')
            if '/title/tt' in href:
                imdb_id = href.split('/title/')[1].split('/')[0].replace('tt', '')
                title = link.get_text(strip=True)
                
                # If year provided, try to match
                if year:
                    year_text = soup.find(string=lambda s: s and f"({year})" in str(s))
                    if year_text:
                        return imdb_id
                else:
                    return imdb_id
        
        return None
    except Exception as e:
        print(f"  Error searching web: {e}")
        return None

# Function to get movie data from IMDb
def get_movie_data(movie_name, year=None):
    ia = Cinemagoer()
    try:
        # Primary: Try web search first (more reliable)
        print(f"  → Searching IMDb website...")
        imdb_id = find_imdb_id_from_web(movie_name, year)
        
        if imdb_id:
            movie = ia.get_movie(imdb_id)
            # Try web scraping for director
            time.sleep(0.5)
            scraped_directors = scrape_director_from_imdb(imdb_id)
            if scraped_directors:
                movie.data['director'] = [{'name': name} for name in scraped_directors]
            return movie
        
        # Fallback: Try Cinemagoer search
        print(f"  → Trying Cinemagoer API...")
        search_results = ia.search_movie(movie_name)
        
        if search_results:
            # If year is provided, try to find matching movie
            if year:
                for result in search_results[:10]:
                    try:
                        movie = ia.get_movie(result.movieID)
                        if movie.get('year') == int(year):
                            # If no director info from API, try web scraping
                            if not movie.get('director'):
                                time.sleep(0.5)
                                scraped_directors = scrape_director_from_imdb(movie.movieID)
                                if scraped_directors:
                                    movie.data['director'] = [{'name': name} for name in scraped_directors]
                            return movie
                    except:
                        continue
            
            # No year filter, use first result
            movie = ia.get_movie(search_results[0].movieID)
            
            # If no director info from API, try web scraping
            if not movie.get('director'):
                time.sleep(0.5)
                scraped_directors = scrape_director_from_imdb(movie.movieID)
                if scraped_directors:
                    movie.data['director'] = [{'name': name} for name in scraped_directors]
            
            return movie
        
        return None
    except Exception as e:
        print(f"  Error searching IMDb: {e}")
        return None

# Function to get movie data by IMDb ID
def get_movie_data_by_id(imdb_id):
    ia = Cinemagoer()
    imdb_id = imdb_id.replace('tt', '')  # Remove the 'tt' prefix
    movie = ia.get_movie(imdb_id)
    
    # If no director info from API, try web scraping
    if not movie.get('director'):
        time.sleep(0.5)  # Be polite to IMDb servers
        scraped_directors = scrape_director_from_imdb(imdb_id)
        if scraped_directors:
            movie.data['director'] = [{'name': name} for name in scraped_directors]
            print(f"  → Scraped director info: {', '.join(scraped_directors)}")
    
    return movie

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

# Get folder path from user with auto-completion
folder_path = input("Please enter the folder path (tab to auto-complete): ").strip()

# Expand ~ to home directory if present
folder_path = os.path.expanduser(folder_path)

# Check if folder exists
if not os.path.exists(folder_path):
    print(f"Error: Folder '{folder_path}' does not exist!")
    exit(1)

if not os.path.isdir(folder_path):
    print(f"Error: '{folder_path}' is not a directory!")
    exit(1)

# Get list of all files in the folder and subfolders
files = get_all_files(folder_path)

print(f"\nFound {len(files)} files in '{folder_path}'")

# Sort files by filename
files.sort()

# Filter out hidden files and show what we're processing
visible_files = [f for f in files if not os.path.basename(f).startswith('.')]
skipped_count = len(files) - len(visible_files)

if skipped_count > 0:
    print(f"Skipping {skipped_count} hidden file(s)")

print(f"Processing {len(visible_files)} file(s)\n")

# Iterate through each file in the folder
for file in visible_files:
    original_file_name = os.path.basename(file)
    movie_name, year = clean_movie_name(original_file_name)
    
    # Skip if movie name is empty
    if not movie_name or len(movie_name) < 2:
        print(f"\n{'='*60}")
        print(f"Original file: {original_file_name}")
        print(f"✗ Skipped: Could not extract valid movie name")
        continue
    
    print(f"\n{'='*60}")
    print(f"Original file: {original_file_name}")
    print(f"Searching for movie: {movie_name}" + (f" ({year})" if year else ""))

    movie_data = get_movie_data(movie_name, year)

    # If not found automatically, ask user for IMDb ID
    if not movie_data:
        print(f"✗ Could not find automatic match for '{movie_name}'")
        imdb_id = input("  Enter IMDb ID (e.g., tt27490099) or press Enter to skip: ").strip()
        if imdb_id:
            try:
                imdb_id = imdb_id.replace('tt', '')
                ia = Cinemagoer()
                movie_data = ia.get_movie(imdb_id)
                # Try web scraping for director
                time.sleep(0.5)
                scraped_directors = scrape_director_from_imdb(imdb_id)
                if scraped_directors:
                    movie_data.data['director'] = [{'name': name} for name in scraped_directors]
                    print(f"  → Scraped director info: {', '.join(scraped_directors)}")
            except Exception as e:
                print(f"  Error fetching IMDb ID: {e}")
                movie_data = None

    if movie_data:
        imdb_url = f"https://www.imdb.com/title/tt{movie_data.movieID}/"
        directors = movie_data.get('director', [])
        director_str = ', '.join(director['name'] for director in directors) if directors else 'Unknown'
        print(f"Found: {movie_data.get('title')} ({movie_data.get('year')}) directed by {director_str}")
        print(f"IMDb URL: {imdb_url}")
        
        # Confirm with user before organizing
        while True:
            confirm = input("  Organize this file? (y/n/search): ").strip().lower()
            if confirm == 'y':
                organize_movie(file, movie_data, folder_path)
                print(f"✓ Organized: {os.path.basename(file)}")
                break
            elif confirm == 'n' or confirm == 'search':
                # Ask for IMDb ID
                imdb_id = input("  Enter IMDb ID (e.g., tt27490099) or press Enter to skip: ").strip()
                if imdb_id:
                    try:
                        imdb_id = imdb_id.replace('tt', '')
                        ia = Cinemagoer()
                        movie_data = ia.get_movie(imdb_id)
                        # Try web scraping for director
                        time.sleep(0.5)
                        scraped_directors = scrape_director_from_imdb(imdb_id)
                        if scraped_directors:
                            movie_data.data['director'] = [{'name': name} for name in scraped_directors]
                            print(f"  → Scraped director info: {', '.join(scraped_directors)}")
                        
                        # Show new movie info and ask again
                        imdb_url = f"https://www.imdb.com/title/tt{movie_data.movieID}/"
                        directors = movie_data.get('director', [])
                        director_str = ', '.join(director['name'] for director in directors) if directors else 'Unknown'
                        print(f"Found: {movie_data.get('title')} ({movie_data.get('year')}) directed by {director_str}")
                        print(f"IMDb URL: {imdb_url}")
                        # Loop will ask for confirmation again
                    except Exception as e:
                        print(f"  Error fetching IMDb ID: {e}")
                        print(f"⊘ Skipped: {original_file_name}")
                        break
                else:
                    print(f"⊘ Skipped: {original_file_name}")
                    break
            else:
                print("  Please enter 'y' (yes), 'n' (no/search), or press Enter to skip")
    else:
        print(f"✗ Skipped: {original_file_name}")

print("\nCleaning up empty folders...")

# Remove empty directories from bottom up
for root, dirs, files in os.walk(folder_path, topdown=False):
    for dir_name in dirs:
        dir_path = os.path.join(root, dir_name)
        try:
            # Check if directory is empty
            if not os.listdir(dir_path):
                os.rmdir(dir_path)
                print(f"  Removed empty folder: {dir_path}")
        except OSError:
            pass

print("\nOrganization complete.")