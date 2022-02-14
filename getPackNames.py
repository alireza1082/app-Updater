import os


def main():
    # directory that checks apks on by relative path
    path = './repo/'
    # direct path = '/home/fdroid/market_source/test/repo'
    apk_lists = list(filter(lambda file: file.split('.')[-1] == 'apk', os.listdir(path)))
    # use hashmap for remove duplicate packageNames and get the latest versionName
    print(apk_lists)
    apk_hashmap = []
    newPackageName = ""
    try:
        for i in range(len(apk_lists)):
            # receive versionName and packageName from apk by aapt command
            PackageName = os.popen("aapt dump badging " + path + apk_lists[
                i] + " | awk -v FS=\"\'\" \'/package: name=/{print $2}\'").read()
            newPackageName = str(PackageName).rstrip()
            # remove excess words
            if newPackageName not in apk_hashmap:
                # compare two version apk of an app
                apk_hashmap.append(newPackageName)
    except Exception as ex:
        print("an error occurred on " + newPackageName)
        print(ex)
    print(apk_hashmap)
    with open('packages.txt', 'w') as pack:
        for row in apk_hashmap:
            pack.write(row + "\n")
    pack.close()


if __name__ == '__main__':
    main()
