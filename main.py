from openai import OpenAI  
from dotenv import load_dotenv
import json
from tools import get_stock_details, currency_conversion_rate
from pydantic import BaseModel, Field

load_dotenv()

client =  OpenAI()

class StockDetails(BaseModel):
    stock_code: str = Field(description="NSE Stock code of a given stock.")
    price: float = Field(description="Latest price of the stock in INR.")
    to_currency: str = Field(description="The currency to which INR needs to be converted")
    exchange_rate: float = Field(description="The exchange rate from INR to the specified currency")

my_tools = [
    {
        "type": "function",
        "name": "get_stock_details",
        "description": "Get the current stock details for a company. Returns stock name and the latest price in INR Currency",
        "parameters": {
            "type": "object", ###   ->   type:object here comes from the standard rules of JSON, which is the format LLM use to communicate tool calls. Had it been type:string it would have been "TCS", had it been array then ["TCS"]. Since, it is type:object it will be key-value mapping
            "properties": {
                "stock_code": {
                    "type": "string",
                    "description": "NSE Stock code of a given stock."
                }
            },
            "required": ["stock_code"]
        }
    },
    {
            "type": "function",
            "name": "currency_conversion_rate",
            "description": "Use this function to get currency conversion rate from INR to any other currency",
            "parameters": {
                "type": "object", 
                "properties": {
                    "to_currency": {
                        "type": "string",
                        "description": "the price to which price in INR needs to be converted"
                                }
                            },
                "required": ["to_currency"]
            }
        }
]
 

user_input = input("Ask the latest stock price of any NSE list company: ")

response = client.responses.create(model="gpt-5.6-luna",input=user_input,tools=my_tools) # type: ignore

tool_mapping = {
    "get_stock_details": get_stock_details,
    "currency_conversion_rate": currency_conversion_rate
}
while True:
    tool_output = []
    llm_output = response.output
    for item in llm_output:
        if item.type == "function_call":
            args = json.loads(item.arguments)
            called_function = tool_mapping[item.name]
            tool_result=called_function(**args)
            tool_output.append({
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": str(tool_result)
            })

    if not tool_output:
        break

    # send tool results back and continue with the new response but commenting it for now as we are not running any loop for input text from user, we are just running a single input and getting the final output in structured format
    response = client.responses.create(model="gpt-5.6-luna", input=tool_output, previous_response_id=response.id, tools=my_tools) # type: ignore  
response_pydantic = client.responses.parse(model='gpt-5.6-luna', input="Return the final details in the required structured format.", previous_response_id=response.id, tools=my_tools,text_format=StockDetails) # type: ignore

result = response_pydantic.output_parsed
if result is None:
    print("No structured output was parsed from the model response.")
    print(response_pydantic.output_text)
    raise RuntimeError("Unable to parse the response into StockDetails.")
else:   
    print(f"The latest price of the stock code {result.stock_code} in INR is {result.price}, and when converted to {result.to_currency} using the exchange rate of {result.exchange_rate:.3f}, the price becomes {result.price * result.exchange_rate:.1f}.")




