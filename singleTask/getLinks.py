import os


def main():
    # directory that checks apks on by relative path
    path = './repo/'
    # direct path = '/home/fdroid/market_source/test/repo'
    apk_lists = list(filter(lambda file: file.split('.')[-1] == 'apk', os.listdir(path)))
    # use hashmap for remove duplicate packageNames and get the latest versionName
    print(apk_lists)
    apk_hashmap = []
    for i in range(len(apk_lists)):
        apk_hashmap.append("https://market.batna.ir/public/" + apk_lists[i])
    print(apk_hashmap)
    with open('packages.txt', 'w') as pack:
        for row in apk_hashmap:
            pack.write(row + "\n")
    pack.close()


if __name__ == '__main__':
    main()
