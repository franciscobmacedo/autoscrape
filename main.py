import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
import os
import time
import sys

class Scrape():
    def __init__(self, main_url):
        self.visited_urls = []
        self.main_url = main_url
        if 'http' in self.main_url:
            self.main_url_clean = self.main_url
        else:
            self.main_url_clean = 'https://' + self.main_url

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

    def check_useful_url(self, url):
        if self.main_url in url or self.main_url_clean in url:
            return url, True
        elif not 'http' in url:
            return self.main_url_clean + url, True 
        else:
            return '', False

    def get_urls(self, url):
        page = requests.get(url)
        # print(page.status_code)
        soup = BeautifulSoup(page.text, 'html.parser')
        all_anchors = soup.find_all('a',  href=True)
        useful_ulrs = []
        for a in all_anchors:
            url, result = self.check_useful_url(a['href'])
            if result:
                useful_ulrs.append(url)
        
        # useful_ulrs = [a['href'] for a in all_anchors if check_useful_url(url)]
        return useful_ulrs

    def get_contents(self, parent_url):
        f = self.f
        useful_ulrs = self.get_urls(parent_url)
        if parent_url not in self.visited_urls:
            useful_ulrs.append(parent_url) 

        useful_ulrs = list(set(useful_ulrs))
        if useful_ulrs:
            print(f'\ntrying url {parent_url} ...')

        for url in useful_ulrs:
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

    def main(self):
        files_dir = 'files'
        if not os.path.exists(files_dir):
            os.mkdir(files_dir)
        f_name = self.main_url.replace('.', '_').replace(':', '').replace('/', '_') + '.txt'
        
        f_name = os.path.join(files_dir, f_name)
        if os.path.exists(f_name):
            os.remove(f_name)
        # time.sleep(2)
       

        self.f = open(f_name, mode='w+', encoding='utf-8')
        try:
            print(f'Trying with https')
            
            self.get_contents(self.main_url_clean)
        except Exception as e:
            print(f'cant do it with https: {e}')

            try:
                print(f' Trying with http')
                self.main_url_clean = 'http://' + self.main_url
                self.get_contents(self.main_url_clean)
            except Exception as e:
                print(f' cant do it with http: {e}')

        self.f.close()
        print('Data written in file.')


if __name__ == '__main__':
    url = sys.argv[1]
    print(url)
    # url = "https://loqr.io/"

    scrape = Scrape(url)
    scrape.main()
    # scrape.f.close()