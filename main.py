import os
import json
import requests
import folium
from geopy import distance
from flask import Flask


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon


def interval(point1, point2):
    return distance.distance(point1, point2).km


def compare_by_distance(coffee_dict):
    return coffee_dict['distance']


def coffe_map():
    with open('index.html') as coffee_file:
        return coffee_file.read()


def make_coffee_list(coords1, coffee):
    keys_list = ['title', 'distance', 'latitude', 'longitude']
    coffees_list = []
    for i in range(len(coffee)):
        distance = interval(coords1, (
                                      coffee[i]['geoData']['coordinates'][1],
                                      coffee[i]['geoData']['coordinates'][0]
                                     )
                            )
        new_coffee = [coffee[i]['Name'],
                      distance,
                      coffee[i]['geoData']['coordinates'][1],
                      coffee[i]['geoData']['coordinates'][0],
                      ]
        coffees_list.append(new_coffee)
    new_coffees_list = [dict(zip(keys_list, coffee)) for coffee in coffees_list]
    return new_coffees_list


def get_nearest_cafe(coords1, coffee, num):
    nearest_cafe = sorted(make_coffee_list(coords1, coffee), key=compare_by_distance)[:num]
    return nearest_cafe


def get_marker():
    folium.Marker(
        location=list(coords1),
        popup="Я здесь!!!",
        icon=folium.Icon(color="red", icon="user"),
    ).add_to(m)
    for i in range(len(get_nearest_cafe(coords1, coffee, num))):
        folium.Marker(
            location=[get_nearest_cafe(coords1, coffee, num)[i]['latitude'],
                      get_nearest_cafe(coords1, coffee, num)[i]['longitude'],
                      ],
            popup=get_nearest_cafe(coords1, coffee, num)[i]['title'],
            icon=folium.Icon(color="black", icon="glass"),
            ).add_to(m)


if __name__ == '__main__':
    key_api = os.environ['KEY_YANDEX_API']
    with open('coffee.json', 'r', encoding='CP1251') as coffee_file:
        coffee = coffee_file.read()
    coffee = json.loads(coffee)
    coords1 = fetch_coordinates(key_api, input('В каком месте вы находитесь? '))
    num = int(input('Сколько кафе вам предложить? '))
    m = folium.Map(location=list(coords1))
    get_marker()
    m.save("index.html")
    app = Flask(__name__)
    app.add_url_rule('/', 'hello', coffe_map)
    app.run('0.0.0.0')
