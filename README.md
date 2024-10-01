
# Film File Organizer

This repository contains two Python scripts that help you automatically sort and rename your collection of film files by their **Director**, **Release Year**, and **Title** using data from the IMDb database.

## Features

- **Automatic File Sorting**: Sorts your film files into directories by `/Director/ReleaseYear - Title/Film File`.
- **Multi-Format Support**: Works with a variety of film file formats including `.mp4`, `.mkv`, `.avi`, and more.
- **IMDB Integration**: Fetches relevant movie details (director, title, release year) from the IMDB database to ensure accurate sorting.
- **File Renaming**: Renames the movie file to its official IMDb title while retaining the original file extension.
- **Two Modes**: 
  - **Interactive Mode**: Prompts the user to confirm the IMDb data or provide alternative search input.
  - **Automatic Mode**: Runs automatically, organizing files without user interaction.

## Prerequisites

- **Python 3.x**
- **IMDBpy** (Python package for accessing the IMDB database)

### Installation of Required Packages

To install the necessary dependencies, run:

```
pip install IMDbPY
```

## Usage

### Interactive Mode

In the **Interactive Mode**, the script will:

1. **Search for IMDb Data**: Fetch details for each film file from IMDb.
2. **Prompt for Confirmation**: Ask the user to confirm the fetched details (title, director, year). The user can input alternative titles or IMDb IDs if needed.
3. **File Sorting**: Organize the files into directories following the structure: `/Director/ReleaseYear - Title/FilmFile`.
4. **File Renaming**: Rename the file based on its IMDb title.

#### Example

Given a folder with the following files:

```

/Film File Organizer
    ├── /Unsorted
    │   ├── random_website_1993_sch_list.mkv
    │   ├── another_telegram_channel_munich2005.mp4
    │   └── 2017_Dunkirk.avi
    
```

After running the script and confirming the details, the structure will be reorganized to:

```

/Film File Organizer
  ├── /Sorted
    │   ├── Steven Spielberg
    │   │   ├── 1993 - Schindler's List
    │   │   │   └── Schindler's List.mkv
    │   │   └── 2005 - Munich
    │   │       └── Munich.mp4
    │   ├── Quentin Tarantino
    │   │   ├── 1994 - Pulp Fiction
    │   │   │   └── PulpFiction.mkv
    │   │   └── 2009 - Inglourious Basterds
    │   │       └── Inglourious Basterds.mkv
    │   └── Christopher Nolan
    │       ├── 2010 - Inception
    │       │   └── Inception.mp4
    │       └── 2017 - Dunkirk
    │           └── Dunkirk.avi
    
```

### Automatic Mode

In **Automatic Mode**, the script will run without user input, using the first search result from IMDb to sort and rename the files. It:

1. **Automatically Searches for IMDb Data**: Uses the file name to search IMDb.
2. **File Sorting and Renaming**: Organizes and renames the files in the same way as the interactive mode but without confirmation prompts.

### Running the Scripts

- **Interactive Mode**: Use `interactive_movie_sorter.py` to manually confirm movie data.
- **Automatic Mode**: Use `automatic_movie_sorter.py` for automatic sorting without prompts.

## Confirmation Prompt (Interactive Mode)

For each film in **Interactive Mode**, the script will display the IMDb data retrieved:

\`\`\`
Title: Schindler's List
Director: Steven Spielberg
Release Year: 1993
Is this correct? [Y/n]:
\`\`\`

Upon confirmation, the script will sort and rename the file accordingly.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
