import api.api_downloader as api
import market_update as checker


def main():
    # directory that checks apks on by relative path
    path = '../repo/'
    package_name = 'com.instagram.android'
    api.download_from_apkpure(package_name.rstrip(), path, "")
    # api.download_from_apkpure(package_name.rstrip(), path, "")
    # checker.cafebazaar(package_name, "1.0.0", path, "")


if __name__ == '__main__':
    main()
