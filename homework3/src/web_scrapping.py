__author__ = 'dorjan hitaj'
import dryscrape
from bs4 import BeautifulSoup
# these are the keywords I use to extract triples for the following relations (as the name of the list of keywords)
colorKeys = [' color ', ' pattern ', 'patern' ' texture ', ' red', ' blue', ' white', ' black', ' yellow', ' orange', ' stripped', ' green']
similarityKeys = [' similar ', ' looks ', ' looks like ', ' like ', ' confused with ', ' confused ', ' resemble ']
activityKeys = [' bark ', ' run ', ' fly ', ' hunt ', ' roar ', ' bite ', ' swim ', ' crawl ', ' jump ', ' can ', ' able to ']
shapeKeys = [' form ', ' shape ', ' has form ', ' is shaped as ', ' ball ', ' round', ' circular', ' hollow']

url = "https://a-z-animals.com/animals/"
to_concatenate_url = "https://a-z-animals.com"
usl_list = list()

session = dryscrape.Session()
session.visit(url)
response = session.body()
soup = BeautifulSoup(response)
all_links = soup.find_all('a')
count = 0
#get all the main page url and store them in a list, I ignore first 25 ones since they are header links and are not relevant in information extraction
for link in all_links:
    if link.get('href') is not None:
        s = link.get('href')
        count += 1
        if s.startswith('/animals/') and count >= 25:
            usl_list.append(s)
# open the url of each animal one by one and extract all the triples I can get
for u in usl_list:
    to_open = to_concatenate_url+u
    session.visit(to_open)
    response = session.body()
    soup = BeautifulSoup(response)
    # remove all the script and style elements so that I can deal with text only
    for script in soup(["script", "style"]):
        script.extract()
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    d = text.encode('utf8')
    k = d.split('.')
    for line in k:
        for c in colorKeys:
            if c in line:
                #the files writen are not the final ones, after that I have used heuristics and manual inspection to clean them
                filehandle = open('color.txt', 'a')
                filehandle.write(u +" | colorPattern | "+ line)
                filehandle.write('\n')
        for s in similarityKeys:
            if s in line:
                filehandle = open('similarity.txt', 'a')
                filehandle.write(u +" | similarity | "+ line)
                filehandle.write('\n')
        for a in activityKeys:
            if a in line:
                filehandle = open('activity.txt', 'a')
                filehandle.write(u +" | activity | "+ line)
                filehandle.write('\n')
        for sh in shapeKeys:
            if sh in line:
                filehandle = open('shape.txt', 'a')
                filehandle.write(u +" | shape | "+ line)
                filehandle.write('\n')
