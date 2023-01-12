import os 
import requests
import time
from bs4 import BeautifulSoup
import re
from pathlib import Path

basePath = '/'
http_headers = {
    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'authority': 'www.coursehero.com',
    'method':'GET',
    'scheme':'https',
    'accept-language':'en-US,en;q=0.5',
    'cache-control':'max-age=0',
}
ERRORZIP_FILE='ERRORS.txt'

def ReadHtml(path):
    with open(path, 'rb') as f:
        return f.read()

def SaveImg(path, img):
    with open(path, 'wb') as f:
        f.write(img)

def SaveHtml(path, html):
    with open(path+'.html', 'w', encoding="utf-8") as f:
        f.write(html)

def get_valid_filename(s):
    s = s.strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)


def SaveErrorZipUrl(url, folderPath):
    data = url+','+folderPath
    path = ERRORZIP_FILE
    with open(path, 'a') as f:
        f.write(data)
        f.write('\n')

def FetchImages(path,root):
    html = ReadHtml(path)
    soup = BeautifulSoup(html, 'html.parser')
    images = soup.findAll('img')
    isModified =0
    fileCounter=0
    imgCounter=0
    for img in images:
        imglink =''
        try:
            imglink = img['src']
            if not imglink.startswith('http'):
                continue
            imgName = DownloadImage(imglink,root)
            img['src'] = imgName
            isModified=1
            imgCounter+=1
            #print(imglink)
        except Exception as e:
            if len(imglink)>0:
                SaveErrorZipUrl(imglink,root)
            #print("Exception:")
            #print(str(e))
    
    hrefs = soup.findAll('a')   
    for href in hrefs:
        link = ''
        try:
            link = href['href']
            if link.endswith('.zip') or link.endswith('.pdf') or link.endswith('.pptx'):
                DownloadImage(link,root)
                fileCounter+=1
        except:
            if len(link)>0:
                SaveErrorZipUrl(link,root)
                print('FileDownload Excption')
    
    if fileCounter >0:
        print(f'File Donwloaded:{fileCounter}')

    if isModified ==1:
        SaveHtml(path,str(soup))
        print(f'Images Download:{imgCounter}')


def DownloadImage(url,path):
    urls = url.split('/')
    imageName = get_valid_filename(urls[len(urls)-1])
    img = ReqImg(url)
    SaveImg(path+'/'+imageName,img)
    return imageName

def ReqImg(url):
    while 1:
        resp = requests.get(url,headers=http_headers)
        if resp.status_code !=200:
            print(f'Img/FileDonwload Error:{url}\nStatusCode:{resp.status_code}')
            raise Exception(f'CanntoDownload Image\r\nUrl:{url}\r\nStatusCode:{resp.status_code}')
        if resp.text.__contains__('Request unsuccessful. Incapsula incident'):
            print("HTML Contains CAPTCHA")
            asd = input('Continue:?')
            continue
        return resp.content

def main():
    counter =1
    topicCouner=0
    pageCounter=1
    paths = []
    for path in Path(basePath).iterdir():
        if path.is_dir():
            paths.append(path)
            print(path)

    for tpath in paths:
        for root, dirs, files in os.walk(tpath):
            for name in files:
                path = os.path.join(root, name)
                if not path.endswith('.html'):
                    continue
                #print(path)
                FetchImages(path,root)
                print(f'Page:{pageCounter}')
                pageCounter+=1
                counter+=1
        print(f'Done Topic:{tpath},Counter:{topicCouner}')
        topicCouner+=1
        pageCounter=1
    print(f'Done!!!\nToTal Amoutn of HTML:{counter}')

if __name__ == "__main__":
    main()
