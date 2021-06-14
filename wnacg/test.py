import  re

url = ' 24張照片，創建於2021-06-3 '
aa = re.search('[0-9]*-[0-9]*-[0-9]*', url).group()
print(aa)
# print(re.match('(.*)id-', url).group())