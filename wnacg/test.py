import  re

url = 'https://www.wnacg.com/photos-view-id-10697193.html'
print(re.match('(.*)id-', url).group())