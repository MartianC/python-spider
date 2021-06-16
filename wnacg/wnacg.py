from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import os
from urllib.request import urlretrieve
import re
import requests
import zipfile
import time




def recent_url(idx):
    return 'https://www.wnacg.com/albums-index-page-' + str(idx) + '.html'
def doujin_url(idx):
    return 'https://www.wnacg.com/albums-index-page-' + str(idx) + '-cate-5.html'
def offprint_url(idx):
    return 'https://www.wnacg.com/albums-index-page-' + str(idx) + '-cate-9.html'
def short_url(idx):
    return 'https://www.wnacg.com/albums-index-page-' + str(idx) + '-cate-10.html'
def korea_url(idx):
    return 'https://www.wnacg.com/albums-index-page-' + str(idx) + '-cate-20.html'


manga_type = {
    0: recent_url,      #最近更新
    1: doujin_url,      #同人志
    2: offprint_url,    #单行本
    3: short_url,       #短篇
    4: korea_url,       #韩漫
}

# def requests_get(self, url):
#     https = {'https': 'socks5://127.0.0.1:7890'}
#     http = {'http': 'socks5://127.0.0.1:7890'}
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
#     }
#     if url.split(':')[0] == 'https':
#         r = requests.get(url=url, headers=headers, proxies=https)
#     else:
#         r = requests.get(url=url, headers=headers, proxies=http)
#     return r

def unzip(file_name):
    unzip_path = re.search('.*/', file_name).group()
    zip_file = zipfile.ZipFile(file_name)
    zip_list = zip_file.namelist()
    for f in zip_list:
        zip_file.extract(f, unzip_path)
    zip_file.close()

def downLoad_and_unzip(url, file_name):
    urlretrieve(url, file_name)
    unzip(file_name)


class Manga:
    name = ''
    type = ''
    date = ''
    url = ''

    def __init__(self, name, url, date):
        self.url = url
        self.date = date

        name = name.replace('?','_')
        name = name.replace('\\','_')
        name = name.replace('*','_')
        name = name.replace('|','_')
        name = name.replace('\"','_')
        name = name.replace('<','_')
        name = name.replace('>','_')
        name = name.replace(':','_')
        name = name.replace('/','_')
        self.name = name


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
    manga_type_url = recent_url
    save_path = ''
    sleep_time = 3
    sleep_time_short = 1
    auto_unzip = True

    def find_manga(self, datelenth):
        today = datetime.today()
        pageidx = 1
        findFinish = False
        self.manga_list.clear()
        print('开始查找...')
        while(not findFinish):
            aa = self.manga_type_url(pageidx)
            # r = self.requests_get(aa)
            time.sleep(self.sleep_time)
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
        print('\r共找到'+ str(len(self.manga_list)) + '个结果')

    def download_zip(self):
        for i, manga in enumerate(self.manga_list):
            print('(' + str(i+1) + '/' + str(len(self.manga_list)) +')' + manga.name + '...', end='')
            time.sleep(self.sleep_time)
            r = requests.get(manga.url)
            r.encoding = 'utf-8'
            html = r.text
            soup = BeautifulSoup(html, 'html.parser')
            # 获取分类
            type = soup.find(class_='asTBcell uwconn').label.string
            type = type.replace(' ','')
            manga.type = type[3:len(type)]
            # 创建目录
            path = os.path.join(self.save_path, manga.type, manga.name)
            try:
                os.makedirs(path)
            except OSError:
                if os.path.isdir(path):
                    print('[SKIP]')
                    continue
            # 创建目录
            # path = os.path.join(self.save_path, manga.type)
            # if not (os.path.exists(path)):
            #     os.makedirs(path)
            btns = soup.find_all(class_ = 'btn')
            dldPage_url = url + btns[len(btns) - 1].attrs['href']
            r = requests.get(dldPage_url)
            r.encoding = 'utf-8'
            html = r.text
            soup = BeautifulSoup(html, 'html.parser')
            dld_url = 'https:' + soup.find(class_ = 'down_btn').attrs['href']
            dld_url = re.search('.*\.zip', dld_url).group()
            # FOR macOS
            # dld_path = os.path.join(path, manga.name, '.zip')
            # FOR Windows
            dld_path = path + '/' + manga.name + '.zip'
            if os.path.exists(dld_path):
                print('[SKIP]')
                continue
            try:
                urlretrieve(dld_url, dld_path)
                if self.auto_unzip:
                    unzip(dld_path)
                print('[DONE]')
            except:
                # 下载链接失效，备用按张下载
                try:
                    self.download_backup(i, manga)
                except:
                    print('[Failed]')
        print('全部下载完成')

    def download_backup(self, i, manga):
        time.sleep(self.sleep_time)
        r = requests.get(manga.url)
        r.encoding = 'utf-8'
        html = r.text
        soup = BeautifulSoup(html, 'html.parser')
        # 获取分类
        type = soup.find(class_='asTBcell uwconn').label.string
        type = type.replace(' ', '')
        manga.type = type[3:len(type)]
        # 封面下载
        path = os.path.join(self.save_path, manga.type, manga.name)
        photos_url = soup.find(class_='pic_box tb').a.attrs['href']
        photos_url = url + photos_url
        r = requests.get(photos_url)
        r.encoding = 'utf-8'
        html = r.text
        soup = BeautifulSoup(html, 'html.parser')
        image_url = 'https:' + soup.find('img', id='picarea').attrs['src']
        imgae_idx = soup.find('img', id='picarea').attrs['alt']
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
            time.sleep(self.sleep_time_short)
            r = requests.get(content_url)
            r.encoding = 'utf-8'
            html = r.text
            soup = BeautifulSoup(html, 'html.parser')
            image_url = 'https:' + soup.find('img', id='picarea').attrs['src']
            imgae_idx = soup.find('img', id='picarea').attrs['alt']
            # FOR macOS
            # image_path = os.path.join(path, imgae_idx + '.png')
            # FOR Windows
            image_path = path + '/' + imgae_idx + '.png'
            urlretrieve(image_url, image_path)
            print('\r' + '(' + str(i + 1) + '/' + str(len(self.manga_list)) + ')' + manga.name + '...(' + str(
                j + 1) + '/' + str(len(content_url_list) + 1) + ')', end='')
        print('\r' + '(' + str(i + 1) + '/' + str(len(self.manga_list)) + ')' + manga.name + '...[DONE]', end='\n')



if __name__ == '__main__':

    url = 'https://www.wnacg.com'

    crawl = Crawler()
    crawl.save_path = 'D:/下载/wnacg/'

    str_ = input('设定查找的类型：\n0: 最近更新\n1: 同人\n2: 单行本\n3: 杂志/短篇\n4: 韩漫\n')
    while True:
        try:
            type_key = int(str_)
        except:
            str_ = input()
            continue
        if type_key in manga_type:
            break
        str_ = input()
    crawl.manga_type_url = manga_type.get(type_key)

    str_ = input('设定查找的天数：')
    while True:
        try:
            day = int(str_)
            break
        except:
            str_ = input()
    crawl.find_manga(day)

    str_ = input('下载路径:'+ crawl.save_path +',是否开始下载？(y/n)')
    while str_ != 'y' and str_ != 'n':
        str_ = input()
    if str_ == 'y':
        # crawl.download_highQuality()
        crawl.download_zip()


