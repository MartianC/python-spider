import  re

url = 'D:/下载/wnacg/aaa.zip'
aa = re.search('.*/', url).group()
print(aa)
# print(re.match('(.*)id-', url).group())