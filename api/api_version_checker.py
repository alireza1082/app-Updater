# coding= utf-8

import requests
from bs4 import BeautifulSoup
from persiantools import digits


def get_cafebazaar_version(package_name):
    server_name = "cafebazaar"
    url = "https://cafebazaar.ir/app/" + str(package_name)
    try:
        resp = requests.get(url.rstrip())
        # arrange file by html tags
        if resp.status_code == 404:
            print(package_name.strip() + " is not exists on " + server_name)
            return 0
        soup = BeautifulSoup(resp.text, features="lxml").find("div", {"class": "AppSubtitles"}).next
        version = soup.text
        if version is not None:
            version_en = digits.fa_to_en(version.rstrip())
            # check version name if it has words and remove words
            new_version = ''.join((ch if ch in '0123456789.' else '') for ch in version_en)
            print(package_name.rstrip() + " checked on " + server_name)
            return new_version
        else:
            return 0
    except Exception as ex:
        print("an error occurred on " + package_name + " in checking " + server_name)
        print(ex)
        return 0


def get_myket_version(package_name):
    url = "https://myket.ir/app/"
    server_name = "myket"
    try:
        url = url + package_name
        resp = requests.get(url)
        if resp.status_code == 404:
            print(package_name.strip() + " is not exists on " + server_name)
            return 0
        # arrange file by html tags
        soup = BeautifulSoup(resp.text, 'html.parser')
        # get version by text of before element
        version = soup.find(text="نسخه").parent.next_sibling.string
        version_en = digits.fa_to_en(version)
        # check version name if it has words and remove words
        new_version = ''.join((ch if ch in '0123456789.' else '') for ch in version_en)
        # build array of versionName split by .
        print(package_name.rstrip() + " checked on " + server_name)
        return new_version
    except Exception as ex:
        print("an error occurred on " + package_name + " in checking " + server_name)
        print(ex)
        return 0


def get_fdroid_version(package_name):
    url = "https://f-droid.org/en/packages/"
    server_name = "F-droid"
    try:
        url = url + package_name
        resp = requests.get(url)
        if resp.status_code == 404:
            print(package_name.strip() + " is not exists on " + server_name)
            return 0
        # arrange file by html tags
        soup = BeautifulSoup(resp.text, 'html.parser')
        version = soup.find("div", {"class": "package-version-header"}).find("a")['name']
        link = soup.find("p", {"class": "package-version-download"}).find("a")['href']
        return [version, link]
    except Exception as ex:
        print("an error occurred on " + package_name + " in checking " + server_name)
        print(ex)
        return 0
