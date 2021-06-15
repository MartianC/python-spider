from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import os
from urllib.request import urlretrieve
import re
import requests
import zipfile
from multiprocessing import Pool


def albums_url(idx):
    return 'https://www.wnacg.com/albums-index-page-' + str(idx) + '.html'
def offprint_url(idx):
    return 'https://www.wnacg.com/albums-index-page-' + str(idx) + '-cate-9.html'

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

    def find_manga(self, datelenth):
        today = datetime.today()
        pageidx = 1
        findFinish = False
        self.manga_list.clear()
        print('开始查找')
        while(not findFinish):
            aa = albums_url(pageidx)
            # r = self.requests_get(aa)
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

    def download_highQuality(self):
        for i, manga in enumerate(self.manga_list):
            print('(' + str(i+1) + '/' + str(len(self.manga_list)) +')' + manga.name + '...', end='')
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
                # FOR macOS
                # image_path = os.path.join(path, imgae_idx + '.png')
                # FOR Windows
                image_path = path + '/' + imgae_idx + '.png'
                urlretrieve(image_url, image_path)
                print('\r' + '(' + str(i+1) + '/' + str(len(self.manga_list)) +')' + manga.name + '...(' + str(j+1) + '/' + str(len(content_url_list)+1) +')', end='')
            print('\r' + '(' + str(i+1) + '/' + str(len(self.manga_list)) +')' + manga.name + '...DONE', end='\n')
        print('全部下载完成')

    def download_zip(self):
        p = Pool(6)
        for i, manga in enumerate(self.manga_list):
            print('(' + str(i+1) + '/' + str(len(self.manga_list)) +')' + manga.name + '...', end='')
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
                    print(' 已有，跳过')
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
                # 提交到子进程
                p.apply(downLoad_and_unzip, args=(dld_url, dld_path))
                print('[DONE]')
            except:
                print('[Failed]')
        p.close()
        p.join()
        print('全部下载完成')

if __name__ == '__main__':

    url = 'https://www.wnacg.com'

    crawl = Crawler()
    crawl.save_path = 'D:/下载/wnacg/'
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


