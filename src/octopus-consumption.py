import json
import base64
from urllib import request


class OctopusMeter:

    API_ROOT ='https://api.octopus.energy/v1/electricity-meter-points/'

    def __init__(self,_mpan ,_serial_number,_api_key,_factor=1):
        self.api_key = _api_key
        self.factor = _factor
        self.mpan = _mpan
        self.readings=[]
        self.consumption_URL = f'{self.API_ROOT}{_mpan}/meters/{_serial_number}/consumption'

    def get_readings(self, group_by='', direct_url=''):

        if direct_url:
            url = direct_url
        else:
            url = f'{self.consumption_URL}/?page_size=1000&group_by={group_by}'

        req = request.Request(url)  # this will make the method "POST"
        base64string = base64.b64encode(bytes('%s:%s' % (self.api_key, ''), 'ascii'))
        req.add_header("Authorization", "Basic %s" % base64string.decode('utf-8'))
        self.readings = []

        with request.urlopen(req) as resp:
            response_data = json.load(resp)
            self.readings += (response_data['results'])

        if response_data['next']:
            print(".",end='')
            self.readings += self.get_readings(group_by, response_data['next'])

    def csv_results(self, headers=True):
        csv = 'MPAN,Date,Time,Reading\n' if headers else ''
        for reading in self.readings:
            result = reading['consumption'] * self.factor
            csv += f"{self.mpan},{','.join(reading['interval_start'].split('T'))},{result}\n"
        return csv


if __name__=='__main__':
    consumption_MPAN = "123456789876"
    export_MPAN = "1234567891234"
    serial_number = "12A1234567"
    API_key = "sk_live_ab123456789abcdef1234567"
    GROUP_BY = 'day'  # options= '' (for half-hourly),'hour','day','week','month','quarter'

    consumption_meter = OctopusMeter(consumption_MPAN,serial_number, API_key)
    export_meter = OctopusMeter(export_MPAN, serial_number, API_key, _factor=-1)

    consumption_meter.get_readings(group_by=GROUP_BY)
    export_meter.get_readings(group_by=GROUP_BY)

    print(consumption_meter.csv_results(), end='')
    print(export_meter.csv_results(headers=False))

