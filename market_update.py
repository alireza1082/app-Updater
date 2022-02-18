# coding= utf-8

import api_downloader as api
import os
import requests
import sys

from bs4 import BeautifulSoup
from persiantools import digits

sys.path.append('../')


def main():
    # directory that checks apks on by relative path
    path = './repo/'
    # direct path = '/home/fdroid/market_source/test/repo'
    apk_lists = list(filter(lambda file: file.split('.')[-1] == 'apk', os.listdir(path)))
    # use hashmap for remove duplicate packageNames and get the latest versionName
    print(apk_lists)
    apk_hashmap = {}
    new_package_name = ""
    try:
        for i in range(len(apk_lists)):
            # receive versionName and packageName from apk by aapt command
            version_name = os.popen("aapt dump badging " + path + apk_lists[
                i] + "| grep VersionName | sed -e \"s/.*versionName='//\" ""-e \"s/' .*//\"").read()
            package_name = os.popen("aapt dump badging " + path + apk_lists[
                i] + " | awk -v FS=\"\'\" \'/package: name=/{print $2}\'").read()
            new_package_name = str(package_name).rstrip()
            # remove excess words
            new_version_name = ''.join((ch if ch in '0123456789.' else '') for ch in version_name).rstrip()
            if new_version_name is None:
                continue
            else:
                if new_package_name in apk_hashmap:
                    final_version_name = list(map(int, new_version_name.split('.')))
                    version = list(map(int, apk_hashmap[new_package_name].split('.')))
                    # compare two version apk of an app
                    if final_version_name > version:
                        # if an apk exists with upper versionName will be changed to upper
                        apk_hashmap.update(dict({new_package_name: new_version_name}))
                else:
                    # if app is not in list will add
                    apk_hashmap.update(dict({new_package_name: new_version_name}))
    except Exception as ex:
        print("an error occurred on " + new_package_name)
        print(ex)
    print(apk_hashmap)
    for package_name, version_name in apk_hashmap.items():
        apkpure(package_name, version_name)
    print("finished")


def cafebazaar(package_name, version_name):
    server_name = "cafebazaar"
    url = "https://cafebazaar.ir/app/" + str(package_name)
    if version_name == '':
        print("VersionName of " + package_name + " is invalid")
        return
    try:
        resp = requests.get(url.rstrip())
        # newVersionName = ''.join((ch if ch in '0123456789.' else '') for ch in VersionName)
        app_version = list(map(int, version_name.split('.')))
        # arrange file by html tags
        soup = BeautifulSoup(resp.text, features="lxml").find("div", {"class": "AppSubtitles"}).next
        version = soup.text
        print(version)
        if resp.status_code == 404:
            print(package_name.strip() + " is not exists on " + server_name)
        elif version is not None:
            version_en = digits.fa_to_en(version.rstrip())
            # check version name if it has words and remove words
            new_version = ''.join((ch if ch in '0123456789.' else '') for ch in version_en)
            # build array of versionName split by .
            web_version = list(map(int, new_version.split('.')))
            print(package_name.rstrip() + " checked on " + server_name)
            # print newest versionName exists on web of an app
            if web_version > app_version:
                print(
                    package_name.rstrip() + ":has an update version on " + server_name + " with version name:"
                    + new_version)
                api.get_apk_from_cafe_bazaar(package_name.rstrip())
    except Exception as ex:
        print("an error occurred on " + package_name + " in checking cafebazaar")
        print(ex)


def google_play(package_name, version_name):
    google_url = "https://play.google.com/store/apps/details?id=" + str(package_name)
    server_name = "google play"
    version = ""
    if version_name == '':
        print("VersionName of " + package_name + " is invalid")
        return
    try:
        app_version = list(map(int, version_name.split('.')))
        google_resp = requests.get(google_url.rstrip())
        if google_resp.status_code == 404:
            print(package_name.strip() + " is not exists on " + server_name)
        else:
            soup = BeautifulSoup(google_resp.text, 'html.parser')
            version = soup.find(text="Current Version").parent.next_sibling.string
        if version == "Varies with device":
            print(server_name + " writes Varies with device on version for " + package_name.strip())
            return
        new_version = ''.join((ch if ch in '0123456789.' else '') for ch in version)
        web_version = list(map(int, new_version.split('.')))
        print(package_name.rstrip() + " checked on " + server_name)
        if web_version > app_version:
            print(package_name.rstrip() + ":has an update on " + server_name + " with version name:" + new_version)
    except Exception as ex:
        print("an error occurred on " + package_name + " in checking google play")
        print(ex)


def apkpure(package_name, version_name):
    server_name = "apkpure"
    if version_name == '':
        print("VersionName of " + package_name + " is invalid")
        return
    try:
        url = "https://m.apkpure.com"
        resp = requests.get(url, timeout=3)
        if resp.status_code == 403:
            print("you can't reach to apkpure servers")
            return
    except Exception as ex:
        print("apkpure is note reachable.")
        print(ex)
        return
    try:
        app_version = list(map(int, version_name.split('.')))
        url = 'https://m.apkpure.com/store/apps/details?id=' + package_name
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        if resp.status_code == 404:
            print(package_name.strip() + " is not exists on " + server_name)
        else:
            tag = soup.find("span", {"itemprop": "version"})
            version = tag.text.rstrip()
            if version is None:
                return
            # remove excess words
            new_version = ''.join((ch if ch in '0123456789.' else '') for ch in version)
            # build array of versionName split by .
            web_version = list(map(int, new_version.split('.')))
            print(package_name.rstrip() + " checked on " + server_name)
            # print newest versionName exists on web of an app
            if web_version > app_version:
                print(package_name.rstrip() + ":has an update on " + server_name + " with version name:" + new_version)
                api.download_from_apkpure(package_name.rstrip())
    except Exception as ex:
        print("an error occurred on " + package_name + " in checking apkpure")
        print(ex)


def myket(package_name, version_name):
    url = "https://myket.ir/app/"
    server_name = "myket"
    if version_name == '':
        print("VersionName of " + package_name + " is invalid")
        return
    try:
        url = url + package_name
        # newVersionName = ''.join((ch if ch in '0123456789.' else '') for ch in VersionName)
        app_version = list(map(int, version_name.split('.')))
        resp = requests.get(url)
        # arrange file by html tags
        soup = BeautifulSoup(resp.text, 'html.parser')
        # get version by text of before element
        version = soup.find(text="نسخه").parent.next_sibling.string
        version_en = digits.fa_to_en(version)
        # check version name if it has words and remove words
        new_version = ''.join((ch if ch in '0123456789.' else '') for ch in version_en)
        # build array of versionName split by .
        web_version = list(map(int, new_version.split('.')))
        print(package_name.rstrip() + " checked on " + server_name)
        # print newest versionName exists on web of an app
        if web_version > app_version:
            print(
                package_name.rstrip() + ":has an update version on " + server_name +
                " with version name:" + new_version)
            api.get_apk_from_myket(package_name.rstrip())
    except Exception as ex:
        print(ex)
        print("an error occurred on " + package_name + " in checking on " + server_name)


if __name__ == '__main__':
    # cafebazaar("ir.mci", "5.3.2")
    apkpure("com.whatsapp", "2.1.1")
    # main()
