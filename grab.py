import requests
from bs4 import BeautifulSoup

urls = open('./about.html', 'r').read().split('\n')
titles = []
for idx, i in enumerate(urls):
    if 'https' in i and i[-1] == ',': 
        yt = i.split('\"')[1]
        page = requests.get(yt)
        soup = BeautifulSoup(page.content, 'html.parser')
        results = soup.find("title")
        t = results.text[:-10]
        titles.append(t)
        print(idx, t)

print(titles)
