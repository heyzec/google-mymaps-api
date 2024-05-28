#!/usr/bin/env python

import enum
import random
import requests
import json
from lxml import html
import base64
from datetime import datetime

from cookies import get_cookies



def b64encode(s):
    return base64.b64encode(s.encode()).decode()
def b64decode(s):
    return base64.b64decode(s.encode()).decode()


def dump_debug(filename, s):
    with open(f'debug/{filename}', 'w') as f:
        f.write(s)



class PointAttrType(enum.Enum):
    """
    cGxhY2VfcmVm place_ref
    Z3hfbWV0YWZlYXR1cmVpZA== gx_metafeatureid%
    bmFtZQ== name
    ZGVzY3JpcHRpb24= description
    """

    NAME = 'name'
    DESCRIPTION = 'description'
    COORD = 'coord'


class PointAttrs:
    def __init__(self):
        self.attrs = {}

    def __str__(self) -> str:
        output = ', '.join(f"{k.value}: {v}" for k, v in self.attrs.items())
        return f"PointAttrs({output})"

    def add_attr(self, attr_type: PointAttrType, attr_value):
        self.attrs[attr_type] = attr_value
        return self

    def encode(self):
        output = []
        for attr_type, attr_value in self.attrs.items():
            attr: list[object] = [None] * 10

            match attr_type:
                case PointAttrType.NAME:
                    attr[4] = attr_value
                    attr[9] = f"str:{b64encode(attr_type.value)}"
                case PointAttrType.DESCRIPTION:
                    attr[5] = attr_value
                    attr[9] = f"str:{b64encode(attr_type.value)}"
                case PointAttrType.COORD:
                    attr[6] = [[attr_value]]
                    attr[9] = f"strgeo:{b64encode('gme_geometry_')}"
            output.append(attr)

        return output

    @classmethod
    def decode(cls, attrs):
        output = cls()

        for attr in attrs:
            attr_type = b64decode(attr[9].split(':')[1])

            if attr_type in PointAttrType.NAME.value:
                output.add_attr(PointAttrType.NAME, attr[4])
            elif attr_type in PointAttrType.DESCRIPTION.value:
                output.add_attr(PointAttrType.DESCRIPTION, attr[5])
            elif attr_type == 'gme_geometry_':
                output.add_attr(PointAttrType.COORD, attr[6][0][0])

        return output



def extract_map_data(html_string):
    tree = html.fromstring(html_string)
    xpathselector = "//body/script[not(@src)]"
    scripts = tree.xpath(xpathselector)

    for script in scripts:
        if '_pageData' in script.text:
            break
    else:
        print("Script with _pageData not found!")
        exit()

    page_data_json = script.text.split('_pageData = ')[1][:-1]
    page_data = json.loads(page_data_json)
    dump_debug('page_data.json', json.dumps(page_data, indent=4))

    global csrf_token
    csrf_token = page_data['xsrfToken']

    map_data_json = page_data['mapdataJson']
    map_data = json.loads(map_data_json)
    dump_debug('map_data.json', json.dumps(map_data, indent=4))

    return map_data


def parse_map_data(map_data):
    title = map_data[0][1]
    print(f"Map title {title}")
    layers = map_data[1]
    for layer in layers:
        name = layer[1]
        print(f"Layer {name}")

        if len(layer) < 17:
            print("no points")
            continue

        points = layer[17]
        for point in points:
            point_data = point[11]

            attrs = PointAttrs.decode(point_data)
            print(attrs)


def get_map_data(map_id):
    url = f"https://www.google.com/maps/d/u/0/edit?mid={map_id}"
    r = requests.get(url,cookies=cookies)
    if b'Sign in' in r.content:
        print("Please update cookie")
        exit()

    html_string = r.content.decode() 
    dump_debug('get.html', html_string)

    map_data = extract_map_data(html_string)
    parse_map_data(map_data)


def update(payload):
    url = "https://www.google.com/maps/d/u/0/mutate?cid=mp&rt=j"
    body = {
        "f.req": json.dumps(payload),
        "at": csrf_token
    }
    r = requests.post(url, data=body, cookies=cookies)
    print(r.status_code)

    # The resulting json response will be malformed
    response = '[' + r.content.decode().split('[', maxsplit=1)[1]

    response = json.loads(response)
    return response


def create_point(map_id, layer_id, attrs=PointAttrs()):
    # Generate a random hex string of length 16
    point_id = hex(random.getrandbits(16 * 4))[2:].upper()

    payload = [map_id] + [None] * 29 + [[
        [map_id, [None, [[point_id, None, None, None, None, None, None, None, None, None, None, attrs.encode()]], None, layer_id]]
    ]]

    update(payload)
    return point_id


def update_point(map_id, layer_id, point_id, attrs):
    payload = [map_id] + [None] * 29 + [[
        [map_id, None, None, None, [None, [[point_id, None, None, None, None, None, None, None, None, None, None, attrs.encode()]], None, layer_id]]
    ]]

    update(payload)

def delete_point(map_id, layer_id, point_id):
    payload = [map_id] + [None] * 29 + [[
        [map_id, None, [None, [point_id], layer_id]]
    ]]

    update(payload)

def create_layer(map_id):
    payload = [map_id] + [None] * 29 + [[
        [map_id] + [None] * 8 + [[None, 1]]
    ]]

    response = update(payload)
    layer_id = response[0][0][3][0][6][0][0]
    return layer_id

def update_layer(map_id, layer_id, layer_name):
    payload = [map_id] + [None] * 29 + [[
        [map_id] + [None] * 10 + [[layer_id, layer_name]]
    ]]

    update(payload)

def delete_layer(map_id, layer_id):
    payload = [map_id] + [None] * 29 + [[
        [map_id] + [None] * 9 + [[layer_id]]
    ]]

    update(payload)



def main():
    get_map_data(map_id)

    layer_id = create_layer(map_id)
    update_layer(map_id, layer_id, layer_name='sup')

    point_id = create_point(map_id, layer_id)
    attrs = (PointAttrs()
        .add_attr(PointAttrType.NAME, str(datetime.now()))
        .add_attr(PointAttrType.COORD, [1.37, 103.75]))
    update_point(map_id, layer_id, point_id, attrs)

    delete_point(map_id, layer_id, point_id)
    delete_layer(map_id, layer_id)


if __name__ == '__main__':
    map_id = '1XCtx-LuzBvM7z6KuKnzHluFx9mJBIY4'
    cookies = get_cookies()
    main()

