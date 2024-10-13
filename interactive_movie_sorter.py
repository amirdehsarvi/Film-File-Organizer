# Iterate through each file in the folder
for file in files:
    if os.path.basename(file).startswith('.'):
        continue

    original_file_name = os.path.basename(file)
    movie_name = clean_movie_name(original_file_name)
    print(f"Original file: {original_file_name}")
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
