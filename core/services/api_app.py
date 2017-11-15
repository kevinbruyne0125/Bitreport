from flask import Flask
from flask_restful import Resource, Api, reqparse
from influxdb import InfluxDBClient
import json


# Internal import
from services import internal
from ta import patterns
from ta import indicators
from ta import levels

app = Flask(__name__)
api = Api(app)

# PARAMETERS
db = 'test'
client = InfluxDBClient('localhost', 8086, 'root', 'root', db)

# to post data without NaN values indicators are calculated on period of length: limit + magic_limit
# next posted data has length = limit
magic_limit = 51

#########################################################################################

class get_ohlc(Resource):
    def get(self, pair, timeframe):
        global client, db
        parser = reqparse.RequestParser()

        parser.add_argument('limit', type = int)
        args = parser.parse_args()
        limit = args.get('limit')

        # Perform query and return JSON data
        dict = {}
        data = internal.import_numpy(client, db, pair, timeframe, limit)
        print(data)


        dict['dates'] = data['date'],
        dict['candles'] = {'open': data['open'].tolist(),
                           'high': data['high'].tolist(),
                           'close': data['close'].tolist(),
                           'low': data['low'].tolist(),
                           }
        print(dict)
        return dict


class get_all(Resource):
    def get(self, pair, timeframe):
        global client, db

        ################################## PARSER #######################################
        parser = reqparse.RequestParser()

        parser.add_argument('limit', type=int, help='Limit must be int')
        args = parser.parse_args()
        limit = args.get('limit')

        parser.add_argument('indicators', action='append', help='Indicators must be line or ALL')
        args = parser.parse_args()
        indicators_list = args.get('indicators')

        parser.add_argument('patterns', action='append')
        args = parser.parse_args()
        patterns_list = args.get('patterns')

        parser.add_argument('levels')
        args = parser.parse_args()
        levels_ask = args.get('levels')

        ############################### DATA REQUEST #####################################

        dict = {}
        data = internal.import_numpy(client, db, pair, timeframe, limit+magic_limit)

        dict['dates'] = data['date'][magic_limit:]

        dict['candles'] = { 'open': data['open'].tolist()[magic_limit:],
                            'high': data['high'].tolist()[magic_limit:],
                            'close': data['close'].tolist()[magic_limit:],
                            'low': data['low'].tolist()[magic_limit:],
                            'volume': data['volume'].tolist()[magic_limit:]
                        }

        ################################ INDICATORS ######################################

        if indicators_list != None:
            try:
                indicators_list = indicators_list[0].split(',')
            except:
                pass

            indidict = {}
            for indic in indicators_list:
                try:
                    indidict[indic] = getattr(indicators, indic)(data, start = magic_limit)
                except:
                    pass

            dict['indicators'] = indidict

        ################################ PATTERNS ########################################
        # Short data for patterns:
        pat_data = internal.import_numpy(client, db, pair, timeframe, limit)

        if patterns_list != None:
            try:
                patterns_list = patterns_list[0].split(',')
            except:
                pass

            value = 0
            if patterns_list == ['ALL']:
                try:
                    dict['patterns'] = patterns.CheckAllPatterns(pat_data, 'none', 1)
                except:
                    pass
            else:
                try:
                    dict['patterns'] = patterns.CheckAllPatterns(pat_data, patterns_list, 0)
                except:
                  pass

        ################################ LEVELS ##########################################

        if levels_ask == 'ALL':
            dict['levels'] = levels.srlevels(data)

        return dict



##################### ENDPOINTS ############################
# Table with name 'pair'
# api.add_resource(get_pair, '/')
api.add_resource(get_all, '/data/<string:pair>/<string:timeframe>/')
api.add_resource(get_ohlc, '/test/<string:pair>/<string:timeframe>/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
