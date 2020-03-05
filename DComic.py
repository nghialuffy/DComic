from bs4 import BeautifulSoup
import requests
import sys, getopt
import urllib.request
import os
from time import gmtime, strftime
from concurrent.futures import ThreadPoolExecutor, as_completed

def print_usage():
    print("Dcomic.py -u $URL -p $PATH")

#Argument -p path -u url -l listurl -h help
PATH = os.getcwd()+r"/"
url = ""
flist = ""
path = ""
help = """
============================Downloader Comic============================
Usage:  Dcomic.py [-u|--url] $URL [-p|--path] $PATH
        Dcomic.py [-l|--list] $FILE [-p|--path] $PATH
First run: You need to install requirements:
------------------------------------------------------------------------
|                    pip install -r requirements.txt                    |
------------------------------------------------------------------------

Options:
--------------------------------    -----------------------------------
|    -h                          :  |   Show this help message and exit |
--------------------------------    -----------------------------------
|    -p                          :  |   PATH                            |
--------------------------------    -----------------------------------
|    -u URL, --url=URL           :  |   URL target                      |
--------------------------------    -----------------------------------
|    -l URLLIST, --list=URLLIST  :  |   URL list target                 |
--------------------------------    -----------------------------------

"""
try:
    opts, args = getopt.getopt(sys.argv[1:], 'hp:u:l:', ['path=', 'url=', 'list='])
except getopt.GetoptError:
    print_usage()
    sys.exit(2)
# print(opts)   Debut

for opt, arg in opts:
    if opt == '-h':
        print(help)
        sys.exit(2)
    elif opt in ("-p", "--path"):
        path = arg
    elif opt in ("-u", "--url"):
        url = arg
    elif opt in ("-l", "--list"):
        flist = arg

if (path==""):
    print("Error: not found the path")
    print("Please add -p argument")
    print("-h to display help")
    sys.exit(2)

if (url=="" and flist==""):
    print("Error: not found the url or list urls")
    print("Please add -u or -l argument")
    print("-h to display help")
    sys.exit(2)

urls=[]
if (flist!=""):
    try:
        file = open(flist,"r")
        # print(file.read())
        while True:
            line = file.readline()
            if not line:
                break
            urls.append(line.rstrip("\n"))
        file.close()
    except Exception as e:
        print("Not read the list file")
        sys.exit(2)
else:
    urls.append(url)

def download_file(url):
    with open(url.split('/')[-1], 'wb') as f:
        getreq =requests.get(url, stream = True)
        f.write(getreq.content)
    return getreq.status_code


for url in urls:
    print("Handling "+ url)
    #Get elements, images
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
    req = requests.get(url, headers)
    if (req.status_code == 200):
        soup = BeautifulSoup(req.text, 'lxml')
    elements = soup.find_all("img")
    imgs=[]

    for element in elements:
        if(element['src'].find("jpg")!=-1 or element['src'].find("png")!=-1):
            imgs.append(element['src'])

    #Download mutilthread

    # with ThreadPoolExecutor(max_workers=5) as executor:
    #     future_to_img = {executor.submit(download_file, img): img for img in imgs}
    #     for future in as_completed(future_to_img):
    #         img = future_to_img[future]
    #         try:
    #             data = future.result()
    #         except Exception as e:
    #             print("--Error--: "+str(e))
    #             imgs.remove(img)
    #         else:
    #             print("Downloading...")
    # print("Downloaded...")

    print("Downloading...")
    processec = []
    with ThreadPoolExecutor(max_workers=12) as executor:
        for img in imgs:
            try:
                processec.append(executor.submit(download_file,img))
                # print(img)
            except Exception as e:
                print("--Error--: "+str(e))
                imgs.remove(img)
    print("Downloaded...")


    #Creative folder and Move images to folder
    namefolder = strftime("%Y%m%d%H%M%S", gmtime())
    try:
        print("Creativing folder...")
        os.mkdir(path+r"/"+namefolder)
    except:
        print("Error: Not creative folder " + namefolder)
        pass
    print("Moving images...")
    for img in imgs:
        try:
            os.rename(PATH + img.split('/')[-1], path + r"/" + namefolder + r"/" + img.split('/')[-1])
        except Exception as e:
            pass
print("Done...")
