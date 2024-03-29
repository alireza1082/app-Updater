# coding= utf-8

__version_prog__ = '1.1.0'

import argparse
import os
import sys
import time

import requests
from bs4 import BeautifulSoup

from api import api_version_checker as checker, api_downloader as api

sys.path.append('../')


def main():
    parser = arg_parser()
    args = parser.parse_args()
    # directory that checks apks on by relative path
    path = args.dir[0].rstrip() if args.dir else './repo/'
    append = args.string.rstrip() if args.string else ""
    verbose = True if args.v else False
    single_append = args.Name[0].rstrip() if args.Name else ""
    server = args.serverName if args.serverName else "cafebazaar"
    if server != "cafebazaar":
        server = args.serverName[0].rstrip()

    if args.id:
        single_download(server.rstrip(), args.id, path, single_append)
        return

    # direct path = '/home/fdroid/market_source/test/repo'
    apk_lists = list(filter(lambda file: file.split('.')[-1] == 'apk', os.listdir(path)))

    # use hashmap for remove duplicate packageNames and get the latest versionName
    print(apk_lists)
    apk_hashmap = get_apk_hashmap(apk_lists, path=path)
    print(apk_hashmap)

    print("downloading with server " + server)

    for package_name, version_name in apk_hashmap.items():
        if server == 'apkpure':
            # os.popen("sudo route add -net 192.168.0.0 gw 192.168.1.1 netmask 255.255.192.0 dev ens18 metric 1")
            # try_reach_apkpure(4)
            apkpure(package_name, version_name, path=path, string=append)
        elif server == 'cafebazaar':
            cafebazaar(package_name, version_name, path=path, string=append)
            time.sleep(1)
        elif server == 'myket':
            myket(package_name, version_name, path=path, string=append)
        elif server == 'fdroid':
            fdroid(package_name, version_name, path=path, string=append)
        elif server == 'google_play':
            google_play(package_name, version_name)
        else:
            print("downloading with default server cafebazaar")
            cafebazaar(package_name, version_name, path=path, string=append)
            time.sleep(1)
    print("finished")
    if args.update:
        print("updating server")
        os.popen("sudo fdroid update -c")


def arg_parser():
    parser = argparse.ArgumentParser(prog="Market Updater",
                                     description="script for download new versions of apk files.")
    parser.add_argument('-s', '--serverName',
                        help='choose that server you want to check and download apks from it.',
                        default='cafebazaar', nargs=1,
                        choices=['apkpure', 'cafebazaar', 'myket', 'google_play', 'fdroid'])
    parser.add_argument('--version', action='version', version='%(prog)s ' + __version_prog__)
    parser.add_argument('-d', '--dir', nargs=1, help='location of apks and new apk downloads')
    parser.add_argument('-a', '--string', type=str,
                        help='append the string to packageName for apk files name')
    parser.add_argument('-i', '--id', type=str, help='check a single packageName')
    parser.add_argument('update', help='update server after update')
    parser.add_argument('-v', help="verbose logs")
    parser.add_argument('-N', '--Name', nargs=1, help='rename apk file to entered string')
    return parser


def check_reaching_apkpure():
    try:
        url = "https://m.apkpure.com"
        resp = requests.get(url, timeout=3)
        if resp.status_code == 403:
            print("you can't reach to apkpure servers")
            return False
    except Exception as ex:
        print("apkpure is note reachable.")
        print(ex)
        return False
    return True


def try_reach_apkpure(tries):
    tried_times = 0
    while tries > tried_times:
        if check_reaching_apkpure():
            return True
        else:
            print("trying connect to apkpure.com try num: " + str(tried_times))
            if tried_times == 0:
                os.popen("occ boa")
            tried_times += 1
            time.sleep(6)


def single_download(server, package_name, path, append):
    if server == 'apkpure':
        print("downloading with server apkpure")
        api.download_from_apkpure(package_name.rstrip(), path=path, string=append)
    elif server == 'cafebazaar':
        print("downloading with server cafebazaar")
        api.get_apk_from_cafe_bazaar(package_name.rstrip(), path=path, string=append)
    elif server == 'myket':
        print("downloading with server myket")
        api.get_apk_from_myket(package_name.rstrip(), path=path, string=append)
    elif server == 'fdroid':
        print("downloading with server fdroid")
        app = checker.get_fdroid_version(package_name=package_name.rstrip())
        if app == 0:
            return
        web_version = ''.join((ch if ch in '0123456789.' else '') for ch in app[0]).rstrip()
        web_version = list(map(int, web_version.split('.')))
        if check_version(web_version=web_version, app_version=get_single_app_version(package_name, path)):
            api.download_from_fdroid(package_name.rstrip(), app[1], path=path, string=append)
        else:
            print("server hasn't newer version")
    elif server == 'google_play':
        print("downloading with server google_play")
        google_play(package_name, "0")
    else:
        print("downloading with default server cafebazaar")
        api.get_apk_from_cafe_bazaar(package_name.rstrip(), path=path, string=append)


def get_apk_hashmap(apk_lists, path):
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
    print(len(apk_hashmap))
    return apk_hashmap


def cafebazaar(package_name, version_name, path, string):
    server_name = "cafebazaar"
    if version_name == '':
        print("VersionName of " + package_name + " is invalid")
        return
    try:
        version_name = ''.join((ch if ch in '0123456789.' else '') for ch in version_name)
        app_version = list(map(int, version_name.split('.')))
        # build array of versionName split by .
        new_version = checker.get_cafebazaar_version(package_name)
        if new_version == 0:
            return
        web_version = list(map(int, new_version.split('.')))
        if check_version(web_version, app_version):
            print(package_name.rstrip() + ":has an update version on " + server_name + " with version name:"
                  + new_version)
            api.get_apk_from_cafe_bazaar(package_name.rstrip(), path=path, string=string)
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
            print(package_name.rstrip() + ":has an update on " + server_name + " with version name:" + web_version)
    except Exception as ex:
        print("an error occurred on " + package_name + " in checking google play")
        print(ex)


def apkpure(package_name, version_name, path, string):
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
            if soup.find("div", {"class": "p404"}) is not None:
                print(package_name + " is not exists on apkpure")
                return
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
            if check_version(web_version, app_version):
                print(package_name.rstrip() + ":has an update on " + server_name + " with version name:" + new_version)
                api.download_from_apkpure(package_name.rstrip(), path=path, string=string)
    except Exception as ex:
        print("an error occurred on " + package_name + " in checking apkpure")
        print(ex)


def myket(package_name, version_name, path, string):
    server_name = "myket"
    if version_name == '':
        print("VersionName of " + package_name + " is invalid")
        return
    try:
        version_name = ''.join((ch if ch in '0123456789.' else '') for ch in version_name)
        app_version = list(map(int, version_name.split('.')))
        new_version = checker.get_myket_version(package_name)
        if new_version == 0:
            return
        web_version = list(map(int, new_version.split('.')))
        # print newest versionName exists on web of an app
        if check_version(web_version, app_version):
            print(package_name.rstrip() + ":has an update version on " + server_name +
                  " with version name:" + new_version)
            api.get_apk_from_myket(package_name.rstrip(), path=path, string=string)
    except Exception as ex:
        print(ex)
        print("an error occurred on " + package_name + " in checking on " + server_name)


def fdroid(package_name, version_name, path, string):
    server_name = "fdroid"
    if version_name == '':
        print("VersionName of " + package_name + " is invalid")
        return
    try:
        version_name = ''.join((ch if ch in '0123456789.' else '') for ch in version_name)
        app_version = list(map(int, version_name.split('.')))
        app = checker.get_fdroid_version(package_name)
        if app == 0:
            return
        web_version = ''.join((ch if ch in '0123456789.' else '') for ch in app[0])
        web_version = list(map(int, web_version.split('.')))
        # print newest versionName exists on web of an app
        if check_version(web_version, app_version):
            print(package_name.rstrip() + ":has an update version on " + server_name +
                  " with version name:" + app[0])
            api.download_from_fdroid(package_name.rstrip(), app[1], path=path, string=string)
    except Exception as ex:
        print(ex)
        print("an error occurred on " + package_name + " in checking on " + server_name)


def check_version(web_version, app_version):
    if web_version[0] > app_version[0]:
        print(web_version, app_version)
        return True
    if web_version > app_version:
        return True
    return False


def get_single_app_version(package_name, path):
    version_name = os.popen("aapt dump badging " + path + package_name
                            + "| grep VersionName | sed -e \"s/.*versionName='//\" ""-e \"s/' .*//\"").read()
    version_name = ''.join((ch if ch in '0123456789.' else '') for ch in version_name)
    return list(map(int, version_name.split('.')))


if __name__ == '__main__':
    main()
