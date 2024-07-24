from urllib.parse import urlparse


a = urlparse('http://web.archive.org/web/20030105231203/http://www.maine.gov:80/ifw/')

a_i = a.path.find('http')

b = a.path[a_i:]

b_u = urlparse(b)


print(b_u)