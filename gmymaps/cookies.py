from http.cookiejar import MozillaCookieJar

import browser_cookie3


COOKIE_FILE = 'cookies.txt'

def save_cookie_input():
    key = input('Are you sure to extract Google cookies from your browser? [y/N] ')
    if key.lower() != 'y':
        exit()

    cj = browser_cookie3.load()
    mcj = MozillaCookieJar(COOKIE_FILE)
    for cookie in cj:
        mcj.set_cookie(cookie)
    mcj.save()
    print(f"Cookies saved to {COOKIE_FILE}")


def get_cookies():
    cj = MozillaCookieJar(COOKIE_FILE)
    cj.load()
    return cj


if __name__ == '__main__':
    save_cookie_input()
