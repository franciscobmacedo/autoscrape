import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
import os
import time
import sys

class Scrape():
    def __init__(self):
        self.visited_urls = []

    def tag_visible(self, element):
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        if isinstance(element, Comment):
            return False
        return True


    def text_from_html(self, body):
        soup = BeautifulSoup(body, 'html.parser')
        texts = soup.findAll(text=True)
        visible_texts = filter(self.tag_visible, texts)  
        return u"\n".join(t.strip() for t in visible_texts if t != '\n')


    def get_urls(self, url):
        page = requests.get(url)
        print(page.status_code)
        soup = BeautifulSoup(page.text, 'html.parser')
        all_anchors = soup.find_all('a',  href=True)
        usefull_ulrs = [a['href'] for a in all_anchors if a['href'].startswith(url)]
        return usefull_ulrs

    def get_contents(self, main_url):
        f = self.f
        usefull_ulrs = self.get_urls(main_url)
        if main_url not in self.visited_urls:
            usefull_ulrs.append(main_url) 

        usefull_ulrs = list(set(usefull_ulrs))
        if usefull_ulrs:
            print(f'\ntrying url {main_url} ...')

        for url in usefull_ulrs:
            if url in self.visited_urls:
                continue
            page = requests.get(url)
            if page.status_code >= 300 or page.status_code < 200:
                continue
            f.write('\n'*2)
            f.write('\\'*200)
            f.write('\\'*200)
            f.write('\n')
            f.write(f'{url}')
            f.write('\n')
            f.write('\\'*200)
            f.write('\\'*200)
            f.write('\n'*2)
            page_text = self.text_from_html(page.text)
            self.f.write(page_text)
            self.f.flush()
            print('success!')
            self.visited_urls.append(url)
            self.get_contents(url)

    def main(self, url):
        files_dir = 'files'
        if not os.path.exists(files_dir):
            os.mkdir(files_dir)
        f_name = url.replace('.', '_').replace(':', '').replace('/', '_') + '.txt'
        
        f_name = os.path.join(files_dir, f_name)
        if os.path.exists(f_name):
            os.remove(f_name)
        # time.sleep(2)
        if 'http' not in url:
            url = 'http://' + url
        self.f = open(f_name, mode='w+', encoding='utf-8')
        try:
            self.get_contents(url)
        except Exception as e:
            print(e)
        # print('Vou fechar!')
        self.f.close()
        print('Data written in file.')


if __name__ == '__main__':
    url = sys.argv[1]
    print(url)
    # url = "https://loqr.io/"
    # url = "www.nunogsousa.com"

    scrape = Scrape()
    scrape.main(url)
    # scrape.f.close()