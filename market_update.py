import os
import requests
import sys

from bs4 import BeautifulSoup
from persiantools import digits

sys.path.append('../')
import api_downloader as api

def main():
    # directory that checks apks on by relative path
    path = './repo/'
    # direct path = '/home/fdroid/market_source/test/repo'
    apk_lists = list(filter(lambda file: file.split('.')[-1] == 'apk', os.listdir(path)))
    # use hashmap for remove duplicate packageNames and get the latest versionName
    print(apk_lists)
    apk_hashmap = {}
    try :
        for i in range(len(apk_lists)):
            # receive versionName and packageName from apk by aapt command
            VersionName = os.popen("aapt dump badging " + path + apk_lists[i] + "| grep VersionName | sed -e \"s/.*versionName='//\" ""-e \"s/' .*//\"").read()
            PackageName = os.popen("aapt dump badging " + path + apk_lists[i] + " | awk -v FS=\"\'\" \'/package: name=/{print $2}\'").read()
            newPackageName = str(PackageName).rstrip()
            # remove excess words
            newVersionName = ''.join((ch if ch in '0123456789.' else '') for ch in VersionName).rstrip()
            if newVersionName is None:
                continue
            else:
                if newPackageName in apk_hashmap:
                    finalVersionName = list(map(int, newVersionName.split('.')))
                    Version = list(map(int, apk_hashmap[newPackageName].split('.')))
                    # compare two version apk of an app
                    if finalVersionName > Version:
                        # if an apk exists with upper versionName will changed to upper
                        apk_hashmap.update(dict({newPackageName: newVersionName}))
                else:
                    # if app is not in list will added
                    apk_hashmap.update(dict({newPackageName: newVersionName}))
    except:
        print("an error occurred on " + newPackageName)
    print(apk_hashmap)
    for PackageName, VersionName in apk_hashmap.items():
        apkpure(PackageName, VersionName)
    print("finished")


switcher={
    'cafebazaar':'cafebazaar',
    'googleplay':'googleplay',
    'apkpure':'apkpure',
    'myket':'myket'
              }

def apk_checker(serverName):
    function = switcher.get(serverName, lambda: "please write a valid server name.")
    print function()
    
    
def cafebazaar(PackageName, VersionName):
    serverName = "cafebaazar"
    url = "https://cafebazaar.ir/app/" + str(PackageName)
    if VersionName == '':
        print("VersionName of " + PackageName + " is invalid")
        return
    try:
        resp = requests.get(url.rstrip())
        # newVersionName = ''.join((ch if ch in '0123456789.' else '') for ch in VersionName)
        app_Version = list(map(int, VersionName.split('.')))
        # arrange file by html tags
        soup = BeautifulSoup(resp.text, features="lxml")
        version = soup.find("div", {"class": "AppVersion AppVersion--linked"})
        if resp.status_code == 404:
            print(PackageName.strip() + " is not exists on " + serverName)
        elif version is not None:
            version_en = digits.fa_to_en(version.text)
            # check version name if has words and remove words
            newVersion = ''.join((ch if ch in '0123456789.' else '') for ch in version_en)
            # build array of versionName split by .
            web_Version = list(map(int, newVersion.split('.')))
            print(PackageName.rstrip() + " checked on " + serverName)
            # print newest versionName exists on web of an app
            if web_Version > app_Version:
                print(PackageName.rstrip() + ":has an update version on " + serverName + " with version name:" + newVersion)
                api.get_apk_from_cafe_bazaar(PackageName.rstrip())
    except :
        print("an error occurred on " + PackageName + " in checking cafebazaar")


def googleplay(PackageName, VersionName):
    google_url = "https://play.google.com/store/apps/details?id=" + str(PackageName)
    serverName = "google play"
    if VersionName == '':
        print("VersionName of " + PackageName + " is invalid")
        return
    try :
        app_Version = list(map(int, VersionName.split('.')))
        google_resp = requests.get(google_url.rstrip())
        if google_resp.status_code == 404:
            print(PackageName.strip() + " is not exists on " + serverName)
        else:
            soup = BeautifulSoup(google_resp.text, 'html.parser')
            version = soup.find(text="Current Version").parent.next_sibling.string
        if version == "Varies with device":
            print(serverName + " writes Varies with device on version for " + PackageName.strip())
            return
        newVersion = ''.join((ch if ch in '0123456789.' else '') for ch in version)
        web_Version = list(map(int, newVersion.split('.')))
        print(PackageName.rstrip() + " checked on " + serverName)
        if web_Version > app_Version:
            print(PackageName.rstrip() + ":has an update on " + serverName + " with version name:" + newVersion)
    except :
        print("an error occurred on " + PackageName + " in checking google play")


def apkpure(PackageName, VersionName):
    serverName = "apkpure"
    if VersionName == '':
        print("VersionName of " + PackageName + " is invalid")
        return
    try:
        url = "https://m.apkpure.com"
        resp = requests.get(url, timeout=3)
        if resp.status_code == 403:
            print("you can't reach to apkpure servers")
            return
    except Exception as ex :
        print("apkpure is note reachable.")
        print(ex)
        return
    try:
        app_Version = list(map(int, VersionName.split('.')))
        url = 'https://m.apkpure.com/store/apps/details?id=' + PackageName
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        if resp.status_code == 404:
            print(PackageName.strip() + " is not exists on " + serverName)
        else:
            tag = soup.find("span", {"itemprop": "version"})
            version = tag.text.rstrip()
            if version is None:
                return
            # remove excess words
            newVersion = ''.join((ch if ch in '0123456789.' else '') for ch in version)
            # build array of versionName split by .
            web_Version = list(map(int, newVersion.split('.')))
            print(PackageName.rstrip() + " checked on " + serverName)
            # print newest versionName exists on web of an app
            if web_Version > app_Version:
                print(PackageName.rstrip() + ":has an update on " + serverName + " with version name:" + newVersion)
                api.download_from_apkpure(PackageName.rstrip())
    except Exception as ex :
        print("an error occurred on " + PackageName + " in checking apkpure")
        print(ex)


def myket(PackageName, VersionName):
    print(4)


main()
