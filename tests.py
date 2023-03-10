import unittest
import json
import requests
import api
from unittest.mock import patch

import models
from api import cbr_json_api
from api import cbr_xml_api


# def get_pbank_response(*newargs, **newkeywargs):

#     class Response:
#         def __init__(self, response):
#             self.text = json.dumps(response)
        
#         def json(self):
#             return json.loads(self.text)
    
#     return Response([{"ccy":"USD","base_ccy":"UAH","sale":"30"}])

class Test(unittest.TestCase):
    def setUp(self):
        models.init_db()
    
    def test_pbank_usd(self):

        xrate = models.XRate.get(id=1)
        updated_before = xrate.updated
        self.assertEqual(xrate.rate, 1.0)

        cbr_json_api.Api().update_rate(840, 980)

        xrate = models.XRate.get(id=1)
        updated_after = xrate.updated

        self.assertGreater(xrate.rate, 25)
        self.assertGreater(updated_after, updated_before)

        api_log = models.ApiLog.select().order_by(models.ApiLog.created.desc()).first()

        self.assertIsNotNone(api_log)
        self.assertEqual(api_log.request_url, "https://www.cbr-xml-daily.ru/daily_json.js")
        self.assertIsNotNone(api_log.response_text)

        self.assertIn('{"ccy":"USD","base_ccy":"UAH",', api_log.response_text)
    
    def test_pbank_btc(self):

        xrate = models.XRate.get(from_currency=1000, to_currency=840)
        updated_before = xrate.updated
        self.assertEqual(xrate.rate, 1.0)

        cbr_json_api.Api().update_rate(1000, 840)

        xrate = models.XRate.get(from_currency=1000, to_currency=840)
        updated_after = xrate.updated

        self.assertGreater(xrate.rate, 5000)
        self.assertGreater(updated_after, updated_before)

        api_log = models.ApiLog.select().order_by(models.ApiLog.created.desc()).first()

        self.assertIsNotNone(api_log)
        self.assertEqual(api_log.request_url, "https://www.cbr-xml-daily.ru/daily_json.js")
             

    def test_cbr(self):
        xrate = models.XRate.get(from_currency=840, to_currency=643)
        updated_before = xrate.updated
        self.assertEqual(xrate.rate, 1.0)
        
        cbr_xml_api.Api().update_rate(840, 643)

        xrate = models.XRate.get(from_currency=840, to_currency=643)
        updated_after = xrate.updated

        self.assertGreater(xrate.rate, 60)
        self.assertGreater(updated_after, updated_before)   

        api_log = models.ApiLog.select().order_by(models.ApiLog.created.desc()).first()

        self.assertIsNotNone(api_log)
        self.assertEqual(api_log.request_url, "http://www.cbr.ru/scripts/XML_daily.asp")
        self.assertIsNotNone(api_log.response_text)

        self.assertIn("<NumCode>840</NumCode>", api_log.response_text) 

    @patch('api._Api._send', new=get_pbank_response)
    def test_pbank_mock(self):
        
        xrate = models.XRate.get(id=1)
        updated_before = xrate.updated
        self.assertEqual(xrate.rate, 1.0)

        pbank_api.Api().update_rate(840, 980)

        xrate = models.XRate.get(id=1)
        updated_after = xrate.updated

        self.assertEqual(xrate.rate, 30)
        self.assertGreater(updated_after, updated_before)

        api_log = models.ApiLog.select().order_by(models.ApiLog.created.desc()).first()

        self.assertIsNotNone(api_log)
        self.assertEqual(api_log.request_url, "https://www.cbr-xml-daily.ru/daily_json.js")
        self.assertIsNotNone(api_log.response_text)

        self.assertEqual('[{"ccy":"USD","base_ccy":"UAH","sale":"30"}]', api_log.response_text)

    def test_api_error(self):
        api.HTTP_TIMEOUT = 15
        xrate = models.XRate.get(id=1)
        updated_before = xrate.updated
        self.assertEqual(xrate.rate, 1.0)

        self.assertRaises(requests.exceptions.RequestException, cbr_json_api.Api().update_rate, 840, 980)

        xrate = models.XRate.get(id=1)
        updated_after = xrate.updated

        self.assertEqual(xrate.rate, 1.0) 
        self.assertGreater(updated_after, updated_before)
          
        api_log = models.ApiLog.select().order_by(models.ApiLog.created.desc()).first()

        self.assertIsNotNone(api_log)
        self.assertEqual(api_log.request_url, "https://www.cbr-xml-daily.ru/daily_json.js")
        self.assertIsNone(api_log.response_text)
        self.assertIsNotNone(api_log.error)

        error_log = models.ApiLog.select().order_by(models.ErrorLog.created.desc()).first()
        self.assertIsNotNone(error_log)
        self.assertEqual(error_log.request_url, "https://www.cbr-xml-daily.ru/daily_json.js")
        self.assertIsNotNone(error_log.traceback)
        self.assertEqual(api_log.error, error_log.error)
        self.assertIn("Connection to api.pbank timed out", error_log.error)

        api.HTTP_TIMEOUT = 15

if __name__ == '__main__':
    unittest.main()        