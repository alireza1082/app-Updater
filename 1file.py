import api_downloader as api


def main():
    # directory that checks apks on by relative path
    path = './repo/'
    package_name = 'com.sec.android.app.shealth'
    api.get_apk_from_cafe_bazaar(package_name.rstrip(), path, "")


if __name__ == '__main__':
    main()
