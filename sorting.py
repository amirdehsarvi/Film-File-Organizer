import os
import requests
import json
from bs4 import BeautifulSoup

# Get folder path from user
folder_path = input("Please enter the folder path: ")

# Get list of files in the folder 
# files = os.listdir(folder_path)
files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

# Iterate through each file in the folder 
for file in files:

    if file.startswith('.'):
        continue

    # Get movie name from file name 
    movie_name = file.split('.')[0:5]
    a1 = " "
    for i in range(len(movie_name)):
        if movie_name[i] == ' ':
            a1 = a1 + '+'
        else:
            if i != 0:
                a1 = a1 + '+' + movie_name[i]
            else:
                a1 = movie_name[i]
    movie_name1 = a1
    print("The movie name is: " + movie_name1)

    confirmTitle = input("What is your preffered film title for the search: " + "\n" + movie_name1 + "\nEnter with +: " )

    # Search movie on IMDB and get its details 
    # url = 'https://www.imdb.com/find?ref_=nv_sr_fn&q=' + movie_name + '&s=all'
    url = 'http://www.omdbapi.com/?apikey=a34d4e1f&t=' + confirmTitle
    response = requests.get(url)
    
    if response.status_code == 200:
        # Parse response as JSON
        data = json.loads(response.text)

        var_exists = data['Director'] in locals() or data['Director'] in globals()


        # Ask user to confirm correct film with a URL 
        imdbUrl = "https://www.imdb.com/title/" + data['imdbID'] + "/"
        confirmMovie = input("Please confirm if this is the correct film by visiting this URL: " + imdbUrl + "\nEnter y/n: " )
        url = 'http://www.omdbapi.com/?apikey=a34d4e1f&t=' + movie_name1
        response = requests.get(url)
        if confirmMovie == 'n':
            ID = input("Please enter the correct imdb ID ONLY: ")
            imdbUrl = "https://www.imdb.com/title/" + ID + "/"
            
            url = 'http://www.omdbapi.com/?apikey=a34d4e1f&i=' + ID
            response = requests.get(url)
            data = json.loads(response.text)

            # Get director name and release year from response
            director_name = data['Director']
            release_year = data['Year']
            movie_name = data['Title']
            
            # Create directory structure based on director name and release year
            dir_structure = os.path.join(folder_path, director_name, release_year + ' - ' + movie_name)
            
            if not os.path.exists(dir_structure):
                os.makedirs(dir_structure)
                
                # Move the file to new directory structure
                sourceFilePath = os.path.join(folder_path, file)
                
                destFilePath = os.path.join(dir_structure, file)
                
                os.rename(sourceFilePath, destFilePath)
                os.chdir(dir_structure)
                
                
                new_file_name = movie_name + os.path.splitext(file)[1]
                
                os.rename(file, new_file_name)
                os.chdir(folder_path)

        else:
            print('Movie confirmed!')
                        
            # Get director name and release year from response
            director_name = data['Director']
            release_year = data['Year']
            movie_name = data['Title']
            
            # Create directory structure based on director name and release year
            dir_structure = os.path.join(folder_path, director_name, release_year + ' - ' + movie_name)
            
            if not os.path.exists(dir_structure):
                os.makedirs(dir_structure)
                
                # Move the file to new directory structure
                sourceFilePath = os.path.join(folder_path, file)
                
                destFilePath = os.path.join(dir_structure, file)
                
                os.rename(sourceFilePath, destFilePath)
                os.chdir(dir_structure)
                
                
                new_file_name = movie_name + os.path.splitext(file)[1]
                
                os.rename(file, new_file_name)
                os.chdir(folder_path)
                
print("Moved %s to %s" % (file, dir_structure))  

