from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import os
from urllib.request import urlretrieve
import re


class Manga:
    name = ''
    type = ''
    date = ''
    url = ''

    def __init__(self, name, url, date):
        self.name = name
        self.url = url
        self.date = date

    def toString(self):
        print('\nname=' + self.name + '\nurl=' + self.url + '\ntype=' + self.type + '\ndate=' + self.date)

    def getInfo(self):
        r = requests.get(self.url)
        r.encoding = 'utf-8'
        html = r.text
        soup = BeautifulSoup(html, 'html.parser')
        type = soup.find(class_ = 'asTBcell uwconn').label.string
        self.type = type[3:len(type)]

class Crawler():

    manga_list = []
    save_path = ''

    def albums_url(self, idx):
        return 'https://www.wnacg.com/albums-index-page-' + str(idx) + '.html'
    def offprint_url(self, idx):
        return 'https://www.wnacg.com/albums-index-page-' + str(idx) + '-cate-6.html'

    def find_manga(self, datelenth):
        today = datetime.today()
        pageidx = 1
        findFinish = False
        self.manga_list.clear()
        print('开始查找')
        while(not findFinish):
            aa = self.albums_url(pageidx)
            r = requests.get(aa)
            r.encoding = 'utf-8'
            html = r.text
            soup = BeautifulSoup(html, 'html.parser')
            manga_div_list = soup.findAll(class_='li gallary_item')
            for manga_div in manga_div_list:
                manga_date = manga_div.find(class_='info_col').string
                manga_date = re.search('[0-9]*-[0-9]*-[0-9]*', manga_date).group()
                manga_date_format = datetime.strptime(manga_date, '%Y-%m-%d')
                if (today - manga_date_format > timedelta(days=datelenth)):
                    findFinish = True
                    break
                manga_name = manga_div.a.attrs['title']
                manga_url = manga_div.a.attrs['href']
                manga_url = url + manga_url
                manga_obj = Manga(manga_name, manga_url, manga_date)
                self.manga_list.append(manga_obj)
            pageidx = pageidx + 1
            print('\r找到' + str(len(self.manga_list)) + '个结果...', end='')
        print('\r找到'+ str(len(self.manga_list)) + '个结果 查找结束')

    def download(self):
        for i, manga in enumerate(self.manga_list):
            print('(' + str(i+1) + '/' + str(len(self.manga_list)+1) +')' + manga.name + '...', end='')
            r = requests.get(manga.url)
            r.encoding = 'utf-8'
            html = r.text
            soup = BeautifulSoup(html, 'html.parser')
            # 获取分类
            type = soup.find(class_='asTBcell uwconn').label.string
            manga.type = type[3:len(type)]
            path = os.path.join(self.save_path, manga.type, manga.name)
            # 创建目录
            try:
                os.makedirs(path)
            except OSError:
                if os.path.isdir(path):
                    print(' 已有，跳过')
                    continue
            photos_url = soup.find(class_ = 'pic_box tb').a.attrs['href']
            photos_url = url + photos_url
            # 封面下载
            r = requests.get(photos_url)
            r.encoding = 'utf-8'
            html = r.text
            soup = BeautifulSoup(html, 'html.parser')
            image_url = 'https:' + soup.find('img', id = 'picarea').attrs['src']
            imgae_idx = soup.find('img', id = 'picarea').attrs['alt']
            image_path = os.path.join(path, imgae_idx + '.png')
            urlretrieve(image_url, image_path)
            # 剩余页
            url_prefix = re.match('(.*)id-', photos_url).group()
            content_opt_list = soup.findAll('option')
            content_url_list = []
            idx = 1
            while (idx < len(content_opt_list)):
                content_url = url_prefix + content_opt_list[idx].attrs['value'] + '.html'
                content_url_list.append(content_url)
                idx = idx + 1
            for j, content_url in enumerate(content_url_list):
                r = requests.get(content_url)
                r.encoding = 'utf-8'
                html = r.text
                soup = BeautifulSoup(html, 'html.parser')
                image_url = 'https:' + soup.find('img', id='picarea').attrs['src']
                imgae_idx = soup.find('img', id='picarea').attrs['alt']
                image_path = os.path.join(path, imgae_idx + '.png')
                urlretrieve(image_url, image_path)
                print('\r' + '(' + str(i+1) + '/' + str(len(self.manga_list)+1) +')' + manga.name + '...(' + str(j+1) + '/' + str(len(content_url_list)+1) +')', end='')
            print('\r' + '(' + str(i+1) + '/' + str(len(self.manga_list)+1) +')' + manga.name + '...DONE', end='\n')
        print('全部下载完成')


if __name__ == '__main__':

    url = 'https://www.wnacg.com'

    crawl = Crawler()
    crawl.save_path = '/Users/chengyuren/Documents/'
    crawl.find_manga(1)
    str_ = input('下载路径:'+ crawl.save_path +',是否开始下载？(y/n)')
    while str_ != 'y' and str_ != 'n':
        str_ = input()
    if str_ == 'y':
        crawl.download()


