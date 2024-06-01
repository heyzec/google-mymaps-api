import re
import json


def parse_cookie_input(cookie_input):
    cookies = {}
    for key in ('SID', 'HSID', 'SSID', '__Secure-1PSIDTS'):
        if key not in cookie_input:
            print(f"{key} is missing")
            return None

        regex = rf'{key}=(?P<value>.+?)(?=[\s;])'
        match = re.search(regex, cookie_input)

        cookies[key] = match.group('value')

    return cookies

def save_cookie_input():
    print('Paste cookie here and press enter >')

    n_newlines = 0
    cookie_input = ""
    while True:
        line = input()
        if line:
            cookie_input += line
        else:
            n_newlines += 1

        if n_newlines >= 2:
            break

    cookies = parse_cookie_input(cookie_input)
    with open('cookies.json', 'w') as f:
        json.dump(cookies, f)

def get_cookies():
    with open('cookies.json', 'r') as f:
        cookies = json.load(f)
    return cookies


if __name__ == '__main__':
    save_cookie_input()
