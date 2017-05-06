#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json; charset=utf-8'
    return r


def processRequest(req):
    if req.get("result").get("action") != "yahooWeatherForecast":
        return {}
    baseurl = "https://query.yahooapis.com/v1/public/yql?"
    yql_query = makeYqlQuery(req)
    if yql_query is None:
        return {}
    yql_url = baseurl + urlencode({'q': yql_query}) + "&format=json"
    result = urlopen(yql_url).read()
    data = json.loads(result)
    res = makeWebhookResult(data)
    return res


def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None

    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')and u=\"c\""


def makeWebhookResult(data):
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}

    # print(json.dumps(item, indent=4))
#    iConditionsRus = [u'торнадо',u'тропический шторм ','ураган','сильные грозы','грозы','смешанный дождь и снег','смешанные дождь и мокрый снег','переменная облачность','переменная облачность','морось','ледяной дождь''метель','метель','легкая метель','переменная облачность','поземка','снег','град','гололедица','пыль','туманно','дымка','смог','порывистый ветер','ветрено','холодно','облачно','переменная облачность','переменная облачность','переменная облачность','переменная облачность','ясно','солнечно','ясно','ясно','смешанные дождь и град ','жара','местами грозы''возможна гроза','возможна гроза','местами дождии','сильный снег','дождь со снегом','сильный снег','облачно с прояснениями''гроза','снег с дождем','местами грозы']
    iConditionsRus = [u"торнадо",u"тропический шторм ",u"ураган",u"сильные грозы",u"грозы",u"смешанный дождь и снег",u"смешанные дождь и мокрый снег",u"переменная облачность",u"переменная облачность",u"морось",u"ледяной дождь",u"метель",u"метель",u"легкая метель",u"переменная облачность",u"поземка",u"снег",u"град",u"гололедица",u"пыль",u"туманно",u"дымка",u"смог",u"порывистый ветер",u"ветрено",u"холодно",u"облачно",u"переменная облачность",u"переменная облачность",u"переменная облачность",u"переменная облачность",u"ясно",u"солнечно",u"ясно",u"ясно",u"смешанные дождь и град ",u"жара",u"местами грозы",u"возможна гроза",u"возможна гроза",u"местами дождии",u"сильный снег",u"дождь со снегом",u"сильный снег",u"облачно с прояснениями",u"гроза",u"снег с дождем",u"местами грозы"]
#    speech = "Сегодня в " + location.get('city') + ": " + condition.get('text') + ", температура " + condition.get('temp') + " " + units.get('temperature')
    speech = u"Сегодня в " + location.get('city') + ": " + unicode(iConditionsRus[int(condition.get('code')])) + u", температура " + condition.get('temp') + " " + units.get('temperature')
#    print("Response:")
#    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
