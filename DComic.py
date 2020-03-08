from bs4 import BeautifulSoup
import requests
import sys, getopt
import urllib.request
import shutil
import os
from fpdf import FPDF
from PIL import Image
from time import gmtime, strftime
from concurrent.futures import ThreadPoolExecutor, as_completed

def print_usage():
    print("DComic.py -u $URL -p $PATH")

def download_file(url):
    with open(url.split('/')[-1].split('.')[0]+".jpg", 'wb') as f:
        getreq =requests.get(url, stream = True)
        f.write(getreq.content)
    return getreq.status_code

def makePdf(pdfFileName, listPages, dir = ''):
    # if (dir):
    #     dir += "\\"
    mwidth = 0
    mheight = 0


    for page in listPages:
        try:
            cover = Image.open(os.path.join(dir, str(page.split('/')[-1]).split('.')[0]+".jpg"))
            width, height = cover.size
            if(width > mwidth):
                mwidth = width
            if(height > mheight):
                mheight = height
        except Exception as e:
            # pass
            print(e)
        # print(dir + str(page.split('/')[-1])) Debut
    pdf = FPDF(unit = "pt", format = [mwidth, mheight])
    # print(listPages)
    for page in listPages:
        try:
            pdf.add_page()
            pdf.image(os.path.join(dir, str(page.split('/')[-1].split('.')[0]+".jpg")), 0, 0)
        except Exception as e:
            # pass
            print(e)
    pdf.output(os.path.join(dir, pdfFileName) + ".pdf", "F")

#Argument -p path -u url -l listurl -h help
PATH = os.getcwd()
url = ""
flist = ""
path = ""
help = """
============================Downloader Comic============================
Usage:  DComic.py [-u|--url] $URL [-p|--path] $PATH
        DComic.py [-l|--list] $FILE [-p|--path] $PATH
First run: You need to install requirements:
------------------------------------------------------------------------
|                    python -m pip install --upgrade pip                |
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

for url in urls:
    print("Handling "+ url)
    #Get elements, images
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
    req = requests.get(url, headers)
    if (req.status_code == 200):
        soup = BeautifulSoup(req.text, 'lxml')
    elements = soup.find_all("img")
    imgs=[]
    try:
        for element in elements:
            if(element['src'].find("jpg")!=-1 or element['src'].find("png")!=-1 or element['src'].find("webp")!=-1  or element['src'].find("jpeg")!=-1):
                if(element['src'].find("http")!=-1 or element['src'].find("s.fanfox.net")!=-1):
                    imgs.append(element['src'].rstrip("\r\n"))
    except Exception as e:
        print(e)
    
    #Download mutilthread

    # with ThreadPoolExecutor(max_workers=12) as executor:
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
    nameFilePdf = strftime("%Y%m%d%H%M%S", gmtime())

    # try:
    #     print("Creativing folder...")
    #     os.mkdir(path+r"/"+namefolder)
    # except:
    #     print("Error: Not creative folder " + namefolder)
    #     pass
    
    print("Creativing PDF...")
    try:
        makePdf(nameFilePdf, imgs, PATH)
    except Exception as e:
        print(e)

    print("Moving PDF...")
    try:
        shutil.move(os.path.join(PATH,nameFilePdf+".pdf"), os.path.join(path,nameFilePdf+".pdf"))
    except Exception as e:
        print(e)
    print("Removing Images...")
    for img in imgs:
        try:
            os.remove(os.path.join(PATH, img.split("/")[-1].split('.')[0]+".jpg"))
        except Exception as e:
            print(e)

print("Done...")
