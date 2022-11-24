import json
import re
import urllib.request
import datetime

import requests
from requests.exceptions import HTTPError


# funktion för användarens navigering bland SR:s kanaler
def set_input():
    api_url = f'http://api.sr.se/v2/channels?page=1&format=json'
    pages, size = channel_pagination(api_url)
    page = 1
    inner_loop = True
    while inner_loop:
        input_a = input('Välj kanal eller skriv "n/b" för att se fler: ')
        if input_a == 'n': # tar oss till nästa sida av listan av kanaler
            page += 1
            if page > pages:
                print("Listan är slut, startar från början")
                main()
            id_, name = get_channels(page)
            print(name)
        elif input_a == 'b': # backar bland listan med kanaler
            page -= 1
            if page < 1:
                print('Du är redan på första sidan')
                main()
            else:
                id_, name = get_channels(page)
                print(name)

        elif input_a.isdigit(): # returnerar kanalens id
            input_a = int(input_a)
            id_, name = get_channels(page)
            return id_[input_a]


# funktion som behandlar sidans pagination med antal sidor och antal objekt på sidan
def channel_pagination(api_url):

    response = urllib.request.urlopen(api_url)

    answer = response.read()
    json_dict = json.loads(answer)

    pages = json_dict['pagination']['totalpages']
    pages = int(pages)
    size = json_dict['pagination']['size']
    size = int(size)

    return pages, size


# funktion som returnerar kanalens id och namn
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


# funktion som visar vald kanals programschema
def show_channel_scheme(_id):
    api_url = f'http://api.sr.se/v2/scheduledepisodes?channelid={_id}&format=json'

    resp = requests.get(api_url)
    if resp.status_code == 404:
        print("Kanalen har ingen information, testa en annan kanal")
        main()

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
            if time[6] == "-":
                i += 1
            else:
                time = re.findall(r'\d+', time)
                startTime = datetime.datetime.fromtimestamp(int(time[0])/1000)
                startTime = startTime.strftime('%H:%M')
                i += 1
                print(startTime, title)
        j += 1


def get_response_example():
    response = requests.get('https://api.github.com/helloworld')

    print(response.status_code)

    if response.status_code == 200:
        print("Success!")
    if response.status_code == 404:
        print("Not found!")

    if response.status_code:
        print("Success!")
    else:
        print("Error!")


def go_again():
    print("Vill du fortsätta?")
    answer = input("y/n: ")
    if answer == "y":
        main()
    elif answer == "n":
        loop = False
        return loop
    else:
        go_again()


def main():
    loop = True
    while loop:
        id_, name = get_channels(1)
        print(name)
        inp = set_input()
        show_channel_scheme(inp)
        loop = go_again()


if __name__ == '__main__':
    main()
