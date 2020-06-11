from flask import render_template, Flask, escape, url_for, make_response
from app import app 
from . import extract
import glob 
import datetime 
import os

def optional_read(path):
    """
    Read files if they're in 
    metadata .txt format
    """
    if '.txt' in path:
        return open('app/' + path, 'r').read()
    else:
        return path 


def get_path_dictionary(parent_dir, file_list, deliver_link=False):
    """
    This is a helper function 
    to assemble dictionaries of relevant files to pass 
    onto html templates. 
    """
    finder = extract.FilePathFinder(parent_dir)

    # Initialise list of dictionaries
    first_path = finder.all_file_paths(file_list[0]) 
    dictionary_list = [{ file_list[0]: optional_read(item)} for item in first_path]

    # Do the rest 
    for item in file_list[1:]: 
        
        # unpack files of a specific type 
        paths = finder.all_file_paths(item)

        # assign this to the right place in the dictionary 
        for index, path in enumerate(paths):
            dictionary_list[index][item] = optional_read(path) 

    if deliver_link == True: 

        subfolder_names =  finder.all_topic_names()
        for index, item in enumerate(dictionary_list):
            item['link'] = subfolder_names[index]

    return dictionary_list


@app.route('/') 
@app.route('/index.html') 
def index():
    """
    This page is a landing page 
    for recent activity!
    It's really simple, we render the index page through the index.html template. 
    """
    # Get the date 
    date = datetime.datetime.now()
    date = date.strftime("%d/%m/%Y %H:%M:%S")
    return render_template('index.html', date=date)


@app.route('/notes.html') 
def notes(): 
    """
    A page dedicated to notes in Latex pdf format.
    This route takes us to a page where file paths are extracted which each correspond to a certain
    set of notes in a course. 
    """

    # Extract paths, titles and abstracts of main pdf notes.
    file_paths = get_path_dictionary('notes', ['title.txt', 'abstract.txt', 'article.pdf'])

     # take one path forward! We do this by hackily removing the app word : / 
    return render_template('notes.html', paths=file_paths)


@app.route('/writing.html')
def writing(): 
    """
    The home page dedicated for articles, not including course lecture notes. 
    We simply look in the 'writing' directory, then pull out the important data
    which we need. 
    """
    
    # The base directory needs to include the root which is why this starts from app
    base_dir = 'app/static/writing' 
    dirs = os.listdir(base_dir)
    content = []
    for directory in dirs:

        # We create a dictionary which contains the titles, abstracts and the directory name which acts as the 
        # post html. 
        data = {'title': open('{base}/{directory}/title.txt'.format(base=base_dir,directory=directory), 'r').read(),  
                'abstract': open('{base}/{directory}/abstract.txt'.format(base=base_dir,directory=directory), 'r').read(),  
                'link': directory, 
               }
        content.append(data) 
    return render_template('writing.html', content=content)


@app.route('/<postname>.html')
def post(postname):
    """
    This is the API to return a writing post in html format 
    """
    # get path to the content 
    content = open('app/static/writing/{}/content.html'.format(escape(postname)),'r').read() 
    title = open('app/static/writing/{}/title.txt'.format(escape(postname)), 'r').read()
    return render_template('post.html', title=title, content=content)  


@app.route('/about.html')
def about(): 
    """
    An about page containing some bio information 
    """
    return render_template('about.html') 
