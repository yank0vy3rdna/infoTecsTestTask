from flask import Flask, jsonify, abort, request, make_response, url_for
import csv, arrow

fields = ['geonameid', 'name', 'asciiname', 'alternatenames',
          'latitude', 'longitude', 'feature class', 'feature code',
          'country code', 'cc2', 'admin1 code', 'admin2 code', 'admin3 code',
          'admin4 code', 'population', 'elevation', 'dem', 'timezone', 'modification date']

reader = csv.DictReader(open('RU.txt', 'r'), fieldnames=fields, delimiter='\t')

towns = [dict(row) for row in reader]


def sort_by_population(x):
    return x['population']


def find_town_by_name(name):
    res = sorted(list(filter(lambda x: x['name'] == str(name), towns)), key=sort_by_population, reverse=True)
    if len(res) == 0:
        abort(404)
    return res[0]


def find_town_by_id(geonameid):
    if len(list(filter(lambda x: x['geonameid'] == str(geonameid), towns))) == 0:
        abort(404)
    return list(filter(lambda x: x['geonameid'] == str(geonameid), towns))[0]


app = Flask(__name__, static_url_path="")


@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/geonames/api/v1.0/gettowninfo/<int:geonameid>', methods=['GET'])
def get_town_info(geonameid):
    return jsonify(find_town_by_id(geonameid))


@app.route('/geonames/api/v1.0/getpage', methods=['GET'])
def get_page():
    page = int(request.args.get('page'))
    count = int(request.args.get('count'))
    if len(towns) < page * count:
        abort(400)
    return jsonify(towns[(page - 1) * count:page * count])


@app.route('/geonames/api/v1.0/compare', methods=['GET'])
def compare():
    name1 = request.args.get('name1')
    name2 = request.args.get('name2')
    print(name2)
    town1 = find_town_by_name(name1)
    town2 = find_town_by_name(name2)
    same_timezone = town1['timezone'] == town2['timezone']
    utc = arrow.utcnow()
    timezones_difference = ':'.join(str((utc.to(town2['timezone'])-utc.to(town1['timezone']))).split(':')[:2])
    north_town_name = town1['name'] if float(town1['latitude']) > float(town2['latitude']) else town2['name']
    return jsonify({'town1': town1,
                    'town2': town2,
                    'diff': {'same_timezone': same_timezone, 'north_town_name': north_town_name,'timezones_difference': timezones_difference}})


app.config['JSON_AS_ASCII'] = False
if __name__ == '__main__':
    app.run()
