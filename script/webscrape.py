import requests
import sys

def get_related_images(arg1):
    
    # check for topic
    if len(sys.argv) < 2:
        print "You need to supply an argument to search."
    else:
        # create the page url
        page = requests.get('https://www.bing.com/images/search?q='+arg1.encode(encoding='UTF-8',errors='strict')+'&FORM=HDRSC2')

        urls = []
        flag = True
        limiter = 10
        itter = 0
        html = page.content
        while (flag):
            a = find_between(html, '<a class="thumb" target="_blank" href="', '" h="ID=images')
            if a != "":
                urls.append(a)
                html = html.replace('<a class="thumb" target="_blank" href="'+a+'" h="ID=images', "<TAKEN>")
            else:
                flag = False

            if (limiter < itter):
                flag = False

            itter += 1
    
    return urls

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""