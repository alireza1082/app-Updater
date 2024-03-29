import os
import sys

import requests
from bs4 import BeautifulSoup
from clint.textui import progress


def get_apk_from_myket(pkg, path, string):
    url = "https://one-api.ir/myket/"
    # one-api token
    token = '******'
    parameters = {'token': token,
                  'action': 'download',
                  'pack': pkg
                  }
    response = requests.post(url, parameters)
    # print(response.text)
    if response.status_code == 200:
        # check app is available on market
        if response.json()['status'] == 404:
            print("download " + pkg + " failed")
            return
        else:
            print("downloading : " + pkg)
    else:
        print("download " + pkg + " failed")
        return
    link = response.json()['result']['main']
    # request to download link and creating .apk file
    file = requests.get(link.rstrip(), stream=True, allow_redirects=True)
    with open(path + pkg + string + '.apk', 'wb') as files:
        # get total length of file from headers of response
        total_length = int(file.headers.get('content-length'))
        for chunk in progress.bar(file.iter_content(chunk_size=1024), expected_size=(total_length / 1024) + 1):
            if chunk:
                files.write(chunk)
                sys.stdout.flush()
    # check if download is successful or not
    if os.path.getsize(path + pkg + string + '.apk') == total_length:
        print(pkg + " downloaded successfully")
    else:
        print(pkg + " download failed")


def get_apk_from_cafe_bazaar(pkg, path, string):
    url = "https://one-api.ir/cafebazaar/"
    # one-api token
    token = '******'
    parameters = {'token': token,
                  'action': 'download',
                  'pack': pkg
                  }
    response = requests.post(url, parameters)
    # print(response.text)
    if response.status_code == 200:
        # check app is available on market
        if response.json()['status'] == 404:
            print("download " + pkg + " failed")
            return
        else:
            print("downloading : " + pkg)
    elif response.status_code == 524:
        print("server timeout occurred on " + pkg)
        return
    elif response.status_code == 503:
        print("The server is temporarily busy")
        return
    # else:
    #     print("download " + pkg + " failed")
    #     return
    link = response.json()['result']['main']
    # request to download link and creating .apk file
    print(link)
    file = requests.get(link[0].rstrip(), stream=True, allow_redirects=True)
    with open(path + pkg + string + '.apk', 'wb') as files:
        # get total length of file from headers of response
        total_length = int(file.headers.get('content-length'))
        for chunk in progress.bar(file.iter_content(chunk_size=1024), expected_size=(total_length / 1024) + 1):
            if chunk:
                files.write(chunk)
                sys.stdout.flush()
    # check if download is successful or not
    if os.path.getsize(path + pkg + string + '.apk') == total_length:
        print(pkg + " downloaded successfully")
    else:
        print(pkg + " download failed")


def download_from_apkpure(pkg, path, string):
    # create base url pf an app in apkpure site
    url = 'https://m.apkpure.com/store/apps/details?id='
    resp = requests.get(url + pkg)
    soup = BeautifulSoup(resp.text, 'html.parser')
    temp = soup.find("a", {"class": "download_apk_news da no-right-radius"})
    if temp is None:
        temp = soup.find("a", {"class": "go-to-download"})
    if temp is None:
        print(pkg + " is not exists on apkpure, it's a trap:)")
        return
    link = temp.get('href')
    # create second url page of an app for getting download link of the apk
    link2 = 'https://m.apkpure.com' + link
    response = requests.get(link2.rstrip(), stream=True, allow_redirects=True)
    soup2 = BeautifulSoup(response.text, 'html.parser')
    # get download link
    download_link = soup2.find("a", {"class": "download-start-btn pc-download-btn ga"}).get('href')
    # check app is available on market
    if response.status_code == 200:
        print("downloading : " + pkg)
    else:
        print("download " + pkg + " failed")
        return
    form = soup2.find("a", {"class": "info-tag"}).text.upper()
    print(form)
    if form.find("XAPK") != -1:
        print(pkg + " has no compatible format to download")
        return
    # request to download link and creating .apk file
    file = requests.get(download_link, stream=True, allow_redirects=True)
    with open(path + pkg + string + '.apk', 'wb') as files:
        # get total length of file from headers of response
        total_length = int(file.headers.get('content-length'))
        for chunk in progress.bar(file.iter_content(chunk_size=1024), expected_size=(total_length / 1024) + 1):
            if chunk:
                files.write(chunk)
                sys.stdout.flush()
    # check if download is successful or not
    if os.path.getsize(path + pkg + string + '.apk') == total_length:
        print(pkg + " downloaded successfully")
    else:
        print(pkg + " download failed")


def download_from_fdroid(pkg, download_link, path, string):
    file = requests.get(download_link, stream=True, allow_redirects=True)
    with open(path + pkg + string + '.apk', 'wb') as files:
        # get total length of file from headers of response
        total_length = int(file.headers.get('content-length'))
        for chunk in progress.bar(file.iter_content(chunk_size=1024), expected_size=(total_length / 1024) + 1):
            if chunk:
                files.write(chunk)
                sys.stdout.flush()
    # check if download is successful or not
    if os.path.getsize(path + pkg + string + '.apk') == total_length:
        print(pkg + " downloaded successfully")
    else:
        print(pkg + " download failed")
