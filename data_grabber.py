import urllib2
from bs4 import BeautifulSoup

# placeholder, just a quick example script about data grabbing

url = 'http://www.bbc.co.uk/radio1/chart/singles'
x = urllib2.urlopen(url)
html_doc = x.read()
soup = BeautifulSoup(html_doc)
foo = soup.findAll('div', attrs={'class': 'cht-entry-artist'})
for item in foo:
    print item.string



