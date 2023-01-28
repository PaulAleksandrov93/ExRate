from api import _Api 

class Api(_Api):
    def __init__(self):
        super().__init__("CbrJsonApi")

    def _update_rate(self, xrate):
        rate = self._get_pbank_rate(xrate.from_currency)
        return rate

    def _get_pbank_rate(self, from_currency):
        response = self._send_request(url="https://www.cbr-xml-daily.ru/daily_json.js", method="get")

        response_json = response.json()
        self.log.debug("CbrJson response: %s" % response_json)
        rate = self._find_rate(response_json, from_currency)

        return rate

    def _find_rate(self, response_data, from_currency):
        pbank_aliases_map = {840: "USD"}
        currency_alias = pbank_aliases_map[from_currency]
        for Valute in response_data:
            if Valute == currency_alias:
                return float('Value')

        raise ValueError("Invalid PBank response: {currency_pbank_alias} not found")







