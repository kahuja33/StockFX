from bharatstock import BharatStock
import os
from dotenv import load_dotenv
import requests
from requests.structures import CaseInsensitiveDict

load_dotenv()

client=BharatStock()

headers = CaseInsensitiveDict()

headers["apikey"] = os.getenv("FREECURRENCY_API_KEY")

url = "https://api.freecurrencyapi.com/v1/latest"

params = {
    "base_currency": "INR",
    "currencies": "" # Specify comma-separated currency codes you need, or leave empty for all
}

resp = requests.get(url, headers=headers, params=params)
# print(resp.json())
# print("")
exchange_rate=resp.json()["data"]
# print(exchange_rate)


"""  Tool 1 to get the stock price details   """
def get_stock_details(stock_code:str):
    """
    It will call this function to get stock price details in INR currency

    args : NSE Stock code for the company

    return Company name and Stoack price details
    """

    stock = client.stocks.get(stock_code)
    #print(f"{stock.company_name} has the latest stock price of {stock.latest_price}",stock.company_name,stock.latest_price)
    #return stock.company_name,stock.latest_price

    #print(stock.company_name)
    #print("")
    #print(stock.latest_price.trade_date,stock.latest_price.close)
    #print("")
    #print(stock)

    return stock.company_name,stock.latest_price.close,stock.latest_price.trade_date # type: ignore
    
#get_stock_details("RELIANCE")



# tool 2 to get the currency rate
def currency_conversion_rate(to_currency:str):
    """
    Use this function to get currency conversion rate from INR to any other currency

    args: 

    to_currency: the currency to which price in INR needs to be converted

    returns conversion rate
    
    """
    rate=exchange_rate
    return rate[to_currency]


#print(currency_conversion_rate('USD'))




