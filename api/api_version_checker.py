import requests
from bs4 import BeautifulSoup
from persiantools import digits


def get_cafebazaar_version(package_name, version_name):
    server_name = "cafebazaar"
    url = "https://cafebazaar.ir/app/" + str(package_name)
    if version_name == '':
        print("VersionName of " + package_name + " is invalid")
        return 0
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


def get_myket_version(package_name, version_name):
    url = "https://myket.ir/app/"
    server_name = "myket"
    if version_name == '':
        print("VersionName of " + package_name + " is invalid")
        return 0
    try:
        url = url + package_name
        # newVersionName = ''.join((ch if ch in '0123456789.' else '') for ch in VersionName)
        app_version = list(map(int, version_name.split('.')))
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
