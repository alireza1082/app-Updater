import market_update as checker


def main():
    # directory that checks apks on by relative path
    path = '../repo/'
    package_name = 'org.torproject.torbrowser'
    # api.get_apk_from_cafe_bazaar(package_name.rstrip(), path, "")
    # api.download_from_apkpure(package_name.rstrip(), path, "")
    checker.myket(package_name, "1.0.0", path, "")


if __name__ == '__main__':
    main()
