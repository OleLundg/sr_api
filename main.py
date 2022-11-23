import json
import re
import urllib.request

import requests
from requests.exceptions import HTTPError
import datetime


def set_input():
    page = 1
    loop = True
    while loop:
        input_a = input('Välj kanal, skriv "next" eller "back": ')
        if input_a == 'next':
            page += 1
            id_, name = get_channels(page)
            print(name)
        elif input_a == 'back':
            page -= 1
            if page < 1:
                print('Du är redan på första sidan')
                page += 1
            else:
                id_, name = get_channels(page)
                print(name)

        elif input_a.isdigit():
            input_a = int(input_a)
            id_, name = get_channels(page)
            return id_[input_a]


def channel_pagination(api_url):

    response = urllib.request.urlopen(api_url)

    answer = response.read()
    json_dict = json.loads(answer)

    pages = json_dict['pagination']['totalpages']
    pages = int(pages)
    size = json_dict['pagination']['size']
    size = int(size)

    return pages, size


def get_channels(page):
    api_url = f'http://api.sr.se/v2/channels?page={page}&format=json'

    pages, size = channel_pagination(api_url)

    response = urllib.request.urlopen(api_url)

    answer = response.read()
    json_dict = json.loads(answer)

    i = 0
    name = {}
    id_ = {}

    while i < size:
        name[i] = json_dict['channels'][i]['name']
        id_[i] = json_dict['channels'][i]['id']
        i += 1

    return id_, name


def show_channel_scheme(_id):
    api_url = f'http://api.sr.se/v2/scheduledepisodes?channelid={_id}&format=json'

    pages, size = channel_pagination(api_url)

    if size == 0:
        print('Det finns inga omnämnda program i denna kanal, testa en annan kanal')
        main()

    j = 1
    while j <= pages:
        api_url = f'http://api.sr.se/v2/scheduledepisodes?channelid={_id}&page={j}&format=json'
        pages, size = channel_pagination(api_url)

        response = urllib.request.urlopen(api_url)

        answer = response.read()
        json_dict = json.loads(answer)

        i = 0
        while i < size:
            title = json_dict['schedule'][i]['title']
            time = json_dict['schedule'][i]['starttimeutc']
            time = re.findall(r'\d+', time)
            startTime = datetime.datetime.fromtimestamp(int(time[0])/1000)
            startTime = startTime.strftime('%H:%M')
            i += 1
            print(startTime, title)
        j += 1


def get_response(api):
    response = requests.get(api)

    print(response.status_code)

    if response.status_code == 200:
        print("Success!")
    if response.status_code == 404:
        print("Not found!")

    if response.status_code:
        print("Success!")
    else:
        print("Error!")


def main():
    id_, name = get_channels(1)
    print(name)
    inp = set_input()
    show_channel_scheme(inp)


if __name__ == '__main__':
    main()
