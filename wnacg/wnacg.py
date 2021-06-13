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

    def downLoad(self):
        for manga in self.manga_list:
            print(manga.name)
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
                    print('已有，跳过')
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
            for content_url in content_url_list:
                r = requests.get(content_url)
                r.encoding = 'utf-8'
                html = r.text
                soup = BeautifulSoup(html, 'html.parser')
                image_url = 'https:' + soup.find('img', id='picarea').attrs['src']
                imgae_idx = soup.find('img', id='picarea').attrs['alt']
                image_path = os.path.join(path, imgae_idx + '.png')
                urlretrieve(image_url, image_path)
            return


if __name__ == '__main__':

    today = datetime.today()
    datelenth = 3


    url = 'https://www.wnacg.com'
    url_albums = 'https://www.wnacg.com/albums.html'
    r = requests.get(url_albums)
    r.encoding = 'utf-8'
    html = r.text
    # print(html)
    print('开始')
    soup = BeautifulSoup(html, 'html.parser')
    manga_div_list = soup.findAll(class_ = 'li gallary_item')
    manga_obj_list = []
    for manga_div in manga_div_list :
        manga_date = manga_div.find(class_ = 'info_col').string
        manga_date = manga_date[-12:-2]
        datetime = datetime.strptime(manga_date, '%Y-%m-%d')
        if(today - datetime > timedelta(days = datelenth)):
            print('finish')
            break
        manga_name = manga_div.a.attrs['title']
        manga_url = manga_div.a.attrs['href']
        manga_url = url + manga_url
        manga_obj = Manga(manga_name, manga_url, manga_date)
        #manga_obj.getInfo()
        manga_obj_list.append(manga_obj)
        #manga_obj.toString()
    print('找到'+ str(len(manga_obj_list)) + '个结果')
    crawl = Crawler()
    crawl.manga_list = manga_obj_list
    crawl.save_path = '/Users/chengyuren/Documents/'
    crawl.downLoad()

