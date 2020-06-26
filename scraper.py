import requests
import bs4
import re
import redis
import json
import threading
from queue import Queue




def download(reee,number):
    res = requests.get('http://www.scp-wiki.com/scp-series')
    soup = bs4.BeautifulSoup(res.text, 'lxml')
    links = soup.find_all(criteria)
    short_list = links[:number]  
    return short_list
    
#specific criteria by which the article is taken
def criteria(a):
    return a.has_attr('href') and re.compile("/scp-") and "SCP-" in a.get_text() and not "SCP-001" in a.get_text()

#scrapes article and takes out its title + rating 
def take_article(link, reee):
    res = requests.get(link)
    soup = bs4.BeautifulSoup(res.text, 'lxml')
    ratings = soup.find_all('span', class_="number prw54353")
    titles = soup.find_all(id = 'page-title')
    rating = ""
    title = ""
    for r in ratings:
        rating = r.get_text().replace('+','')

    for t in titles:
        title = t.get_text().strip()
    
    reee.mset({title : rating})

#statistics
def stats(reee):
    keys = reee.keys()
    values = []
    for key in keys:
        values.append(json.loads(reee[key].decode('utf-8')))
    most = max(values)
    populars = []
    for key in keys:
        if most == json.loads(reee[key].decode('utf-8')):
            populars.append(key.decode('utf-8'))
    pop = ','.join(map(str,populars))
    avg = sum(values)/len(values)
    print('Most liked article: '+ pop + ' : ' + str(most))
    print('Average rating: ' + str(avg))

#manifesting database
rediska = redis.Redis()
rediska.flushdb()

#thread
class Downloader(threading.Thread):
    def __init__(self,queue):
        threading.Thread.__init__(self)
        self.queue = queue
    def run(self):
        while True:
            take_article(self.queue.get(),rediska)
            self.queue.task_done()

def main():
    queue = Queue()

    short_list = download(rediska,300)
    
    for i in range(100):
        t = Downloader(queue) 
        t.setDaemon(True)
        t.start()
       
    for link in short_list:
        queue.put('http://www.scp-wiki.com'+link['href'])
    queue.join()
    stats(rediska)

if __name__ == "__main__":
    main()
