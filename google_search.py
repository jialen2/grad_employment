import urllib.request
import re
def get_links_on_google(query, forbidden=[]):
    possibleURLs = []
    url = 'https://www.google.com/search?q=' + query.replace(' ', '+').replace('/', "%2F").replace('–', '')
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.google.com/'})
    with urllib.request.urlopen(req) as response:
        r = response.read()
    plaintext = r.decode('utf8')
    links = re.findall("href=[\"\'](.*?)[\"\']", plaintext)
    for i in links:
        k = '/url?q=http'
        flag = True
        for j in forbidden:
            if j in i:
                flag = False
        if len(i) > len(k) and i[:len(k)] == k and flag:
            link = i[7:].split('&amp')[0]
            link = urllib.parse.unquote(link)
            possibleURLs.append(link)
    return possibleURLs