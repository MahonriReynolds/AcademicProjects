

# Only offers expiration alerts in this version

from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import json
import requests
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('API_KEY')
BASE = os.getenv('BASE')
PRODUCTS = os.getenv('PRODUCTS')
CATEGORIES = os.getenv('CATEGORIES')
ORDERS = os.getenv('ORDERS')
USAGES = os.getenv('USAGES')

CRITICAL_DAYS = int(os.getenv('CRITICAL_DAYS'))
WARNING_DAYS = int(os.getenv('WARNING_DAYS'))
USAGE_PERIOD_DAYS = int(os.getenv('USAGE_PERIOD_DAYS'))

HEADERS ={ 
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def airtable_read(table: str):
    url = f'https://api.airtable.com/v0/{BASE}/{table}'
    response = requests.get(url, headers=HEADERS)
    return response.json()

def airtable_write(table: str, data: dict):
    url = f'https://api.airtable.com/v0/{BASE}/{table}'
    response = requests.post(url, headers=HEADERS, data=json.dumps(data))
    
    return response.status_code, response.json()

# JSON to be passed to the front end:
    # {
    #   "charts": [
    #     {
    #       "category": "category-1",
    #       "data": [
    #         {"month": "2025-02", "orders": 5, "usages": 4},
    #         {"month": "2025-03", "orders": 3, "usages": 2}
    #       ]
    #     },
    #     {
    #       "category": "category-2",
    #       "data": [
    #         {"month": "2025-02", "orders": 4, "usages": 3},
    #         {"month": "2025-03", "orders": 2, "usages": 1}
    #       ]
    #     }
    #   ]
    # }
def parse_chart_json(categories_data, orders_data, usages_data):
    # map product IDs to categories
    category_map = {}
    category_names = {}
    
    for category in categories_data['records']:
        category_id = category['fields']['id']
        category_name = category['fields']['name']
        category_names[category_id] = category_name
        for product in category['fields'].get('products', []):
            category_map[product] = category_id

    # extract year-month from a date
    def extract_month(date_str):
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m")

    # count orders per category per month
    category_orders = defaultdict(lambda: defaultdict(int))
    
    for order in orders_data['records']:
        product_ids = order['fields'].get('product', [])
        order_month = extract_month(order['fields']['order-date'])
        for product_id in product_ids:
            category_id = category_map.get(product_id)
            if category_id:
                category_orders[category_id][order_month] += 1

    # count usages per category per month
    category_usages = defaultdict(lambda: defaultdict(int))
    
    for usage in usages_data['records']:
        product_ids = usage['fields'].get('product', [])
        usage_month = extract_month(usage['fields']['usage-date'])
        for product_id in product_ids:
            category_id = category_map.get(product_id)
            if category_id:
                category_usages[category_id][usage_month] += 1

    # construct JSON response
    charts = []
    for category_id, category_name in category_names.items():
        months = set(category_orders[category_id].keys()) | set(category_usages[category_id].keys())
        data = [
            {
                "month": month,
                "orders": category_orders[category_id].get(month, 0),
                "usages": category_usages[category_id].get(month, 0)
            }
            for month in sorted(months)
        ]
        
        if data:
            charts.append({"category": category_name, "data": data})
    return {"charts": charts}

# JSON to be passed to the front end:
    # {
    #   "alerts": [
    #     {
    #       "urgency": "Critical",
    #       "type": "Low Inventory",
    #       "category": "category-3",
    #       "product": "Product A",
    #       "effective-date": "2025-04-01"
    #     },
    #     {
    #       "urgency": "Warning",
    #       "type": "Projected Run Out",
    #       "category": "category-2",
    #       "product": "Product B",
    #       "effective-date": "2025-04-03"
    #     }
    #   ]
    # }
def parse_table_json(categories_data, products_data, orders_data, usages_data):
    # init alerts list
    alerts = []

    # map products to categories
    product_to_category = {}
    for category in categories_data['records']:
        category_name = category['fields']['name']
        category_products = category['fields'].get('products', [])
        for product_id in category_products:
            product_to_category[product_id] = category_name
    
    # get product info
    product_info = {}  
    for product in products_data['records']:
        product_id = product['id']
        product_name = product['fields'].get('name', 'Unknown Product')
        unit_of_measurement = product['fields'].get('unit-of-measurement', 'unit')  # default to 'unit'
        product_info[product_id] = {"name": product_name, "unit": unit_of_measurement}
    
    
    # get order amounts
    product_purchases = defaultdict(float)  
    for order in orders_data['records']:
        product_ids = order['fields'].get('product', [])
        order_amount = order['fields'].get('amount', 0)  # default to 0
        for product_id in product_ids:
            product_purchases[product_id] += order_amount  

    # get usage amounts
    product_usages = defaultdict(float)  
    for usage in usages_data['records']:
        product_ids = usage['fields'].get('product', [])
        usage_amount = usage['fields'].get('amount', 0)  # default to 0
        for product_id in product_ids:
            product_usages[product_id] += usage_amount  

    # get expiration dates
    product_expiration_dates = {}
    for order in orders_data['records']:
        for product_id in order['fields']['product']:
            try:
                expiration_date = order['fields']['expiration-date']
            except:
                expiration_date = None
            # store latest expiration
            if product_id not in product_expiration_dates:
                product_expiration_dates[product_id] = expiration_date
            else:
                # keep the earliest expiration date
                if expiration_date:
                    if expiration_date < product_expiration_dates[product_id]:
                        product_expiration_dates[product_id] = expiration_date

    # track product usage dates
    product_usage_dates = {}
    for usage in usages_data['records']:
        for product_id in usage['fields']['product']:
            usage_date = usage['fields']['usage-date']
            if product_id not in product_usage_dates:
                product_usage_dates[product_id] = []
            product_usage_dates[product_id].append(usage_date)

    # generate alerts
    current_date = datetime.now()
    for product_id, category_name in product_to_category.items():        
        product_name = product_info.get(product_id, {}).get("name", "Unknown")
        unit_of_measurement = product_info.get(product_id, {}).get("unit", "unit")
        
        expiration_alert = None
        expiration_date_str = None
        expiration_date = None
        days_to_expire = None

        # check expiration date
        for order in orders_data['records']:
            if product_id in order['fields'].get('product', []):
                expiration_date_str = order['fields'].get('expiration-date')
                if expiration_date_str:
                    expiration_date = datetime.strptime(expiration_date_str, "%Y-%m-%d")
                    days_to_expire = (expiration_date - current_date).days
                    break

        if days_to_expire:
            if days_to_expire <= CRITICAL_DAYS:
                urgency = "Critical"
            elif days_to_expire <= WARNING_DAYS:
                urgency = "Warning"
            else:
                urgency = None

            if urgency:
                expiration_alert = {
                    "urgency": urgency,
                    "type": "Expiration",
                    "category": category_name,
                    "product": product_name,
                    "unit-of-measurement": unit_of_measurement,
                    "effective-date": expiration_date_str
                }
                alerts.append(expiration_alert)


        runout_alert = None
        total_purchases = product_purchases.get(product_id, 0)
        total_usages = product_usages.get(product_id, 0)

        # average usage
        avg_daily_usage = total_usages / USAGE_PERIOD_DAYS if total_usages > 0 else 0

        # remaining
        remaining_stock = total_purchases - total_usages
        
        if avg_daily_usage > 0 and remaining_stock > 0:
            days_until_runout = remaining_stock / avg_daily_usage
            runout_date = current_date + timedelta(days=days_until_runout)
            days_to_runout = (runout_date - current_date).days

            if days_to_runout <= CRITICAL_DAYS:
                urgency = "Critical"
            elif days_to_runout <= WARNING_DAYS:
                urgency = "Warning"
            else:
                urgency = None

            if urgency:
                runout_alert = {
                    "urgency": urgency,
                    "type": "Projected Run Out",
                    "category": category_name,
                    "product": product_name,
                    "unit-of-measurement": unit_of_measurement,
                    "effective-date": runout_date.strftime("%Y-%m-%d")
                }
                alerts.append(runout_alert)
                
    # return sorted alerts
    alerts.sort(key=lambda alert: datetime.strptime(alert["effective-date"], "%Y-%m-%d"))
    return {"alerts": alerts}


app = FastAPI()

@app.get("/favicon.ico")
async def favicon():
    return FileResponse('frontend/images/favicon.ico')

@app.get("/")
async def redirect_to_dashboard():
    return RedirectResponse(url="/dashboard")

@app.get("/dashboard")
async def get_dashboard():
    return FileResponse('frontend/dashboard.html')

@app.get("/api/dashboard-chart-data")
async def dashboard_chart_data():
    categories_data = airtable_read(CATEGORIES)
    orders_data = airtable_read(ORDERS)
    usages_data = airtable_read(USAGES)

    chart_json = parse_chart_json(categories_data, orders_data, usages_data)
    return JSONResponse(content=chart_json)

@app.get("/api/dashboard-table-data")
async def dashboard_table_data():
    categories_data = airtable_read(CATEGORIES)
    products_data = airtable_read(PRODUCTS)
    orders_data = airtable_read(ORDERS)
    usages_data = airtable_read(USAGES)

    table_json = parse_table_json(categories_data, products_data, orders_data, usages_data)
    return JSONResponse(content=table_json)
@app.get("/api/form-product-data")
async def dashboard_table_data():
    products_data = airtable_read(PRODUCTS)
    # extract id, name, and unit-of-measurement for each product
    products_json = {
        "products": sorted(
            [
                {
                    "id": product['id'],
                    "name": product['fields']['name'],
                    "unit": product['fields'].get('unit-of-measurement', '')
                }
                for product in products_data['records']
            ],
            key=lambda x: x['name']  # Sort by 'name' field in alphabetical order
        )
    }
    return JSONResponse(content=products_json)


def get_product_record_id(product_name):
    """Retrieve the record ID for the product from the 'Products' table based on the product name."""
    url = f'https://api.airtable.com/v0/{BASE}/{PRODUCTS}?filterByFormula={{Name}}="{product_name}"'
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        data = response.json()
        records = data.get("records", [])
        
        if len(records) > 0:
            return records[0]["id"]  # return ID of first match
        else:
            raise HTTPException(status_code=400, detail=f"Product '{product_name}' not found in Airtable.")
    else:
        raise HTTPException(status_code=500, detail="Error retrieving product data from Airtable.")

def format_date_to_airtable(date_string: str) -> str:
    try:
        # convert string to datetime
        date_obj = datetime.strptime(date_string, "%Y-%m-%d")
        # mm/dd/yyyy
        return date_obj.strftime("%m/%d/%Y")
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {date_string}")

@app.post("/api/purchase-report")
async def purchase_report(data: Dict):
    # check data
    if "items" in data and isinstance(data["items"], list) and len(data["items"]) > 0:
        for item in data["items"]:
            
            product_id = item.get("product")
            if not product_id:
                raise HTTPException(status_code=400, detail="Missing product")
            
            order_date = item.get("orderDate")
            if not order_date:
                raise HTTPException(status_code=400, detail="Missing order date")
            
            expiration_date = item.get("expirationDate") or None
            
            amount = item.get("amount")
            if not amount:
                raise HTTPException(status_code=400, detail="Missing amount")
            try:
                amount = float(amount)
                if amount <= 0:
                    raise ValueError("Amount must be greater than 0.")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid amount")

            # mm/dd/yyyy
            formatted_order_date = format_date_to_airtable(order_date)
            formatted_expiration_date = format_date_to_airtable(expiration_date) if expiration_date else None

            # check date
            if expiration_date and expiration_date < order_date:
                raise HTTPException(status_code=400, detail="Expiration date cannot be earlier than order date")

            # format response
            airtable_data = {
                "fields": {
                    "product": [product_id],
                    "order-date": formatted_order_date,
                    "expiration-date": formatted_expiration_date if formatted_expiration_date else None,
                    "amount": amount
                }
            }

            # write to airtable
            status_code, response_data = airtable_write(ORDERS, airtable_data)

            # handle errors
            if status_code != 200:
                raise HTTPException(status_code=500, detail=f"Error writing to Airtable: {response_data.get('message')}")

        # success response
        return JSONResponse(content={
            "status": 200,  # success status code
            "message": "Report submitted successfully"  # success message
        })
    
    else:
        # failure response
        raise HTTPException(status_code=400, detail="Invalid data or missing items")

@app.post("/api/usage-report")
async def usage_report(data: Dict):
    # check data
    if "items" in data and isinstance(data["items"], list) and len(data["items"]) > 0:
        for item in data["items"]:
            
            product_id = item.get("product")
            if not product_id:
                raise HTTPException(status_code=400, detail="Missing product")
            
            usage_date = item.get("usageDate")
            if not usage_date:
                raise HTTPException(status_code=400, detail="Missing usage date")
            
            amount = item.get("amount")
            if not amount:
                raise HTTPException(status_code=400, detail="Missing amount")
            try:
                amount = float(amount)
                if amount <= 0:
                    raise ValueError("Amount must be greater than 0.")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid amount")

            # mm/dd/yyyy
            formatted_usage_date = format_date_to_airtable(usage_date)

            # format airtable write
            airtable_data = {
                "fields": {
                    "product": [product_id],
                    "usage-date": formatted_usage_date,
                    "amount": amount
                }
            }

            # write to airtable
            status_code, response_data = airtable_write(USAGES, airtable_data)

            # handle errors
            if status_code != 200:
                raise HTTPException(status_code=500, detail=f"Error writing to Airtable: {response_data.get('message')}")

        # success response
        return JSONResponse(content={
            "status": 200,  # success status code
            "message": "Usage report submitted successfully"  # success message
        })
    
    else:
        # failure response
        raise HTTPException(status_code=400, detail="Invalid data or missing items")

@app.get("/purchase-report")
async def get_purchase_report():
    return FileResponse('frontend/purchase-report.html')

@app.get("/usage-report")
async def get_usage_report():
    return FileResponse('frontend/usage-report.html')

app.mount("/styles", StaticFiles(directory="frontend/styles"), name="styles")
app.mount("/scripts", StaticFiles(directory="frontend/scripts"), name="scripts")
app.mount("/images", StaticFiles(directory="frontend/images"), name="images")


if __name__ == '__main__':
    print()
    os.system('uvicorn main:app --reload --host 0.0.0.0 --port 8000')
    

    
