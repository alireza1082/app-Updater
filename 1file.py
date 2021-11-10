import api_downloader as api


def main():
    # directory that checks apks on by relative path
    path = './repo/'
    Package_name = 'com.sec.android.app.shealth'
    api.get_apk_from_cafe_bazaar(Package_name.rstrip())


if __name__ == '__main__':
    main()
