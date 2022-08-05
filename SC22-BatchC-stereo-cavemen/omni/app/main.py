# Run by typing python3 main.py

# **IMPORTANT:** only collaborators on the project where you run
# this can access this web server!

"""
    Bonus points if you want to have internship at AI Camp
    1. How can we save what user built? And if we can save them, like allow them to publish, can we load the saved results back on the home page? 
    2. Can you add a button for each generated item at the frontend to just allow that item to be added to the story that the user is building? 
    3. What other features you'd like to develop to help AI write better with a user? 
    4. How to speed up the model run? Quantize the model? Using a GPU to run the model? 
"""

# import basics
import os
import requests
from bs4 import BeautifulSoup


# import stuff for our web server
from flask import Flask, request, redirect, url_for, render_template, session
from utils import get_base_url
# import stuff for our models
from aitextgen import aitextgen

# load up a model from memory. Note you may not need all of these options.
# ai = aitextgen(model_folder="model/",
#                tokenizer_file="model/aitextgen.tokenizer.json", to_gpu=False)

#

# setup the webserver
# port may need to be changed if there are multiple flask servers running on same server
port = 12345
base_url = get_base_url(port)

# if the base url is not empty, then the server is running in development, and we need to specify the static folder so that the static files are served
if base_url == '/':
    app = Flask(__name__)
else:
    app = Flask(__name__, static_url_path=base_url+'static')

app.secret_key = os.urandom(64)

# set up the routes and logic for the webserver

@app.route(f'{base_url}')
def home():
    return render_template('index.html')

@app.route(f'{base_url}/make_recipe/')
def make_recipe():
    # data = "alex"
    # data = "<img src="https://alex.com">"
    return render_template('make_recipe.html', generated="<h2 class='m-0 text-center text-black'>Your recipe will be displayed here.</h2>")

# define additional routes here
# for example:
@app.route(f'{base_url}/team_members/')
def team_members():
    return render_template('team_members.html') # would need to actually make this page

@app.route(f'{base_url}/about/')
def documentation():
    return render_template('about.html')

##Checks if there is a title or not so that the recipe is valid
def hasTitle(generated):
    generated = str(generated)
    generated += '√'
    tempStr = ""
    tempGenerated = []
    symbols = ["Ω",'π','√']
    for char in generated:
        tempStr += char
        if char in symbols:
            tempGenerated.append(tempStr)
            tempStr = ""
    if len(tempGenerated) > 2:
        for element in tempGenerated:
            if symbols[1] in element:
                return True
            else:
                return False
    else:
        return False
    
def get_google_img(query):
    """
    gets a link to the first google image search result
    :param query: search query string
    :result: url string to first result
    """
    url = "https://www.google.com/search?q=" + str(query) + "&source=lnms&tbm=isch"
    headers={'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}

    html = requests.get(url, headers=headers).text

    soup = BeautifulSoup(html, 'html.parser')
    image = soup.find_all("img") # ,{"class":"t0fcAb"}

    if not image:
        return 
    return image[1]['src']

@app.route(f'{base_url}/generate_text/', methods=["POST"])
def generate_text():
    prompt = request.form['prompt']
    choice = request.form['type']
    print(str(choice) + '|' + str(prompt))

    ai = aitextgen(model_folder='./model/' + str(choice) + '/', to_gpu=False)

    if prompt is not None and choice is not None:
        generated = ai.generate_one(
            batch_size=3,
            prompt='√' + str(prompt) + 'Ω',
            max_length=300,
            temperature=0.7,
        )
        print(str(generated)) #do we need the print statment?

        #re ordering so that the title comes first
        #works most of the time, but sometimes it gets duplicated for some reason and only the bottom half is in the correct format
        generated = str(generated)
        component_list = []
        # √ChickenΩMoulard-Braised Chicken with Caramelized EggπMix together mustard, mayonnaise, and salt (if using). Chill turkey, uncovered, at least 30 minutes and up to 1 hour.
        tempList = generated.split("Ω")
        # √Chicken, Moulard-Braised Chicken with Caramelized EggπMix together mustard, mayonnaise, and salt (if using). Chill turkey, uncovered, at least 30 minutes and up to 1 hour.
        component_list = [tempList[0]]
        component_list.append(tempList[1].split("π"))
        component_list[0] = component_list[0][1:]
        print(component_list)
        
        # component_list[0] => ingredients
        # component_list[1][0] => name
        # component_list[1][1] => instructions
        generated = "<h3 style='font-family:Copperplate;'>" + str(component_list[1][0]) + "</h3>" + str(component_list[0]) + '<br>' + str(component_list[1][1]) + '<br>' +"<img src=\"" + str(get_google_img(component_list[1][0])) + "\" alt=\"recipe picture\">"
        # <img src=\" + str(get_google_img(component_list[1][0])) + \" alt="Girl in a jacket" width="500" height="600">

#         tempStr = ""
#         tempGenerated = []
#         symbols = ["Ω",'π','√']
#         for char in generated:
#             tempStr += char
#             if char in symbols:
#             ##separates the ingredients, title, and instructions into sepearate elements
#                 tempGenerated.append(tempStr)
#                 tempStr = ""
#                 print(tempGenerated)
#             ##sometimes the resulting list is only the title and instructions, or sometimes it has all three components
#             ##This checks to see which output it falls under, the one with two or three elements
#             for idx, item in enumerate(tempGenerated):
#                 if idx == 0:
#                     generated = "<h3 style='font-family:Copperplate;'>" + str(item) + "</h3>"
#                 else:
#                     generated += str(item)
# #         if len(tempGenerated) > 2: #if it consistently produces a title then it will ALWAYS be longer than 2
# #             if (len(tempGenerated[1]) < len(tempGenerated[0])):
# #                 ##checks to make sure that the title is the one that is going first by making sure that it is shorter
# #                 generated = "<h3 style='font-family:Copperplate;'>" + str(tempGenerated[1] + "</h3>" + tempGenerated[0] + tempGenerated[2])
# #             else:
# #                 generated = "<h3 style='font-family:Copperplate;'>" + str(tempGenerated[0] + "</h3>" + tempGenerated[1] + tempGenerated[2])
# #         else:
# #             ##loops through the two elements and for the first one it gives it the special font because it has to be the title
# #             for i in range(len(tempGenerated)):
# #                 if i == 0:
# #                     generated += "<h3 style='font-family:Copperplate;'>" + str(tempGenerated[i]) + "</h3>"
# #                 else:
# #                     generated += tempGenerated[i]
#         # <br> functions as a line break
        x = generated.replace("Ω", "<br> \n <br>")
        y = x.replace('π', '<br> \n <br>')
        z = y.replace('√', '<br>')
        generated = z
        
        #check for title and regenerate if invalid

        session['data'] = generated
        if 'data' in session:
            data = session['data']
            return render_template('make_recipe.html', generated=data)
        else:
            return render_template('make_recipe.html', generated=None)



if __name__ == '__main__':
    # IMPORTANT: change url to the site where you are editing this file.
    website_url = 'cocalc10.ai-camp.dev'

    print(f'Try to open\n\n    https://{website_url}' + base_url + '\n\n')
    app.run(host='0.0.0.0', port=port, debug=True)
