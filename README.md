
# Film File Organizer

This script helps you automatically sort and rename your collection of film files by their **Director**, **Release Year**, and **Title** using data from the IMDB database.

## Features

- **Automatic File Sorting**: Sorts your film files into directories by `/Director/ReleaseYear - Title/FilmFile`.
- **Multi-Format Support**: Works with a variety of film file formats including `.mp4`, `.mkv`, `.avi`, and more.
- **IMDB Integration**: Fetches relevant movie details (director, title, release year) from the IMDB database to ensure accurate sorting.
- **File Renaming**: Renames files to follow the format: `ReleaseYear - Title`.
- **User Confirmation**: Before applying changes, the script asks for user confirmation to verify the retrieved information.

## Prerequisites

- **Python 3.x**
- **IMDBpy** (Python package for accessing the IMDB database)

### Installation of Required Packages

To install the necessary dependencies, run:

```bash
pip install IMDbPY
```

## Usage

1. Place your unsorted film files in a folder.
2. Run the script in the same directory as your film files.
3. The script will:
    - Fetch details from IMDB for each film file.
    - Ask you to confirm the details.
    - Sort the files into directories using the format `/Director/ReleaseYear - Title/FilmFile`.

### Example

Given a folder with the following files:

```
/Unsorted/
    ├── random_film_1.mp4
    ├── another_movie.mkv
    ├── yet_another.avi
```

After running the script and confirming the details, the structure will be reorganized to:

```
/Sorted/
    ├── Steven Spielberg/
    │   ├── 1993 - Schindler's List/
    │   │   └── SchindlersList.mp4
    ├── Quentin Tarantino/
    │   ├── 1994 - Pulp Fiction/
    │   │   └── PulpFiction.mkv
```

## Configuration

The script is configurable to handle various file formats and has options to tweak IMDB search queries or exclude certain films. Check the script comments for more details on customization.

## Confirmation Prompt

For each film, the script will show the retrieved IMDB information, such as:

```
Title: Schindler's List
Director: Steven Spielberg
Release Year: 1993
Is this correct? [Y/n]:
```

Upon confirmation, the script will proceed to sort and rename the file accordingly.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
