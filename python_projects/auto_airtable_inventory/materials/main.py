# imports
import requests, os, smtplib, logging, re
from datetime import datetime, timedelta
from email.mime.text import MIMEText

# set current time for comparison and logging  
CURRENT_TIMESTAMP = datetime.now()

# start logging
logging.basicConfig(level=logging.DEBUG,
                    filename=f'logs/inventory_log_{CURRENT_TIMESTAMP}.txt',
                    encoding='utf-8',
                    filemode='a',
                    format='{asctime} - {levelname}\t- {message}',
                    style='{',
                    datefmt='%H:%M'
)


class APIHandler():
    
    __slots__ = ('api_token', 'headers')
    
    def __init__(self, api_token: str) -> None:
        '''
        Init APIHandler with an API token and headers.
        
        Parameters:
        - api_token (str): authentication token
        
        Returns:
        - none
        
        Raises:
        - ValueError: api_token not provided
        '''
        
        logging.debug('APIHandler.init: Init started.')
        if not api_token:
            logging.error('APIHandler.init: API token is missing or invalid.')
            raise ValueError('APIHandler.init: API token is required.')
        
        self.api_token = api_token
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        logging.debug('APIHandler.init: Init complete.')

    def request(self, endpoint: str) -> dict|None:
        '''
        Make a GET request to specified endpoint.
        
        Parameters:
        - endpoint (str): API endpoint to send request to
        
        Returns:
        - response (dict): json response from API if successful.
        - none: if request failed or there was an error
        
        Raises:
        - ValueError: invalid json from response
        - Timeout: request timed out
        - TooManyRedirects: request had too many redirects
        - RequestException: general request error
        - Exception: request failed
        '''
        logging.debug(f'APIHandler.request: Request started to {endpoint}...')
        
        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            
            logging.debug('APIHandler.request: Request successful. Response received.')
            
            # attempt to return response
            try:
                return response.json()
            except ValueError as e:
                logging.error('APIHandler.request: Failed to decode JSON from response.', exc_info=True)
                raise
                
        except requests.exceptions.Timeout as timeout_error:
            logging.error(f'APIHandler.request: Request to {endpoint} timed out: {timeout_error}.', exc_info=True)
            return None
        except requests.exceptions.TooManyRedirects as redirects_error:
            logging.error(f'APIHandler.request: Too many redirects while requesting {endpoint}: {redirects_error}.', exc_info=True)
            return None
        except requests.exceptions.RequestException as req_error:
            logging.error(f'APIHandler.request: General request error while contacting {endpoint} : {req_error}.', exc_info=True)
            return None
        except Exception as e:
            logging.error(f'APIHandler.request: Unexpected error during request: {e}.', exc_info=True)
            return None

class EmailHandler():
    
    __slots__ = ('email_smtp_address', 'email_address', 'email_password')
    
    def __init__(self, email_smtp_address: str, email_address: str, email_password: str) -> None:
        '''
        Init EmailHandler with SMTP server details and login credentials.
        
        Parameters:
        - email_smtp_address (str): SMTP server address
        - email_address (str): email address to send and recieve emails from
        - email_password (str): app password for email address
        
        Returns:
        - none
        
        Raises:
        - ValueError: email details not provided
        '''
        logging.debug('EmailHandler.init: Init started.')
        
        if not all([email_smtp_address, email_address, email_password]):
            logging.error('EmailHandler.init: Missing required parameters for SMTP configuration.')
            raise ValueError('EmailHandler.init: SMTP address, email address, and password are required.')
        
        self.email_smtp_address = email_smtp_address
        self.email_address = email_address
        self.email_password = email_password
        logging.debug('EmailHandler.init: Init complete.')

    def send_email(self, message: MIMEText) -> bool:
        '''
        Send an email using SMTP server and credential details.

        Parameters:
        - message (MIMEText): formatted email to be sent
        
        Returns:
        - bool: true if email was sent successfully
        
        Raises:
        - SMTPAuthenticationError: email login failed
        - SMTPException: general smtp error
        - Exception: email failed to send
        - SMTPConnectError: smtp server not reached
        '''
        try:
            # set to and from in email
            message['From'] = self.email_address
            message['To'] = self.email_address
            
            logging.debug('EmailHandler.send_email: Connecting to SMTP server.')
            with smtplib.SMTP(self.email_smtp_address, 587) as smtp_server:
                try:
                    logging.debug('EmailHandler.send_email: Encrypting SMTP connection.')
                    smtp_server.starttls()

                    logging.debug('EmailHandler.send_email: Logging into SMTP.')
                    smtp_server.login(self.email_address, self.email_password)
                    
                    logging.debug('EmailHandler.send_email: Sending email.')
                    smtp_server.sendmail(self.email_address, self.email_address, message.as_string())

                    logging.debug('EmailHandler.send_email: Email sent successfully.')
                    
                    logging.debug('EmailHandler.send_email: Closing SMTP connection.')
                    
                    return True
                
                except smtplib.SMTPAuthenticationError as auth_error:
                    logging.error(f'EmailHandler.send_email: Email login failed: {auth_error}.')
                    return False
                except smtplib.SMTPException as smtp_error:
                    logging.error(f'EmailHandler.send_email: Failed to send email: {smtp_error}.')
                    return False
                except Exception as e:
                    logging.error(f'EmailHandler.send_email: Unexpected error sending email: {e}.')
                    return False
                
        except smtplib.SMTPConnectError as conn_error:
            logging.error(f'EmailHandler.send_email: Failed to connect to SMTP server. Check SMTP address and network: {conn_error}.')
            return False
        except smtplib.SMTPException as smtp_error:
            logging.error(f'EmailHandler.send_email: General SMTP error occurred: {smtp_error}.')
            return False
        except Exception as e:
            logging.error(f'EmailHandler.send_email: Unexpected error sending email: {e}.')
            return False


def get_env_var(var_name: str, expected_type: type=str, log_sensitive: bool=False) -> any:
    '''
    Retrieve and validate an environment variable.

    Parameters:
    - var_name (str): name of environment variable
    - expected_type (type): expected type of environment variable
    - log_sensitive (bool): true to censor value in logs

    Returns:
    - cast_value (any): environment variable in expected type
    
    Raises:
    - ValueError: environment variable not set | invalid type cast
    '''

    # log start
    logging.info(f'get_env_var: Retrieving environment variable "{var_name}".')
    
    # get variable
    value = os.getenv(var_name)
    
    # format for logging
    if log_sensitive:
        parsed_value = '*' * len(value)
    else:
        parsed_value = value
    
    if len(parsed_value) > 6:
        parsed_value = f'{parsed_value[:3]}...{parsed_value[-3:]}'
    
    # check environment variable present
    if value is None:
        logging.error(f'get_env_var: Environment variable "{var_name}" not set.')
        raise ValueError (f'get_env_var: Environment variable "{var_name}" not set.')
    
    # log found value before casting
    logging.debug(f'get_env_var: Retrieved value for "{var_name}": {parsed_value}.')
    
    # cast value to expected type
    if expected_type != str:
        try:
            cast_value = expected_type(value)
            logging.info(f'get_env_var: Environment variable "{var_name}" cast to {expected_type.__name__}: {parsed_value}.')
        except ValueError as e:
            logging.error(f'get_env_var: Error casting environment variable "{var_name}" to {expected_type.__name__}: {e}.')
            raise
    else:
        logging.info(f'get_env_var: Environment variable "{var_name}" left as {expected_type.__name__}: {parsed_value}.')
        cast_value = value
    
    # log end
    logging.info(f'get_env_var: Environment variable "{var_name}" validated and returned: {parsed_value}.')
    return cast_value

def parse_api_response(response: dict, fields_to_extract: list) -> dict:
    '''
    Extract specified fields from API response.
    
    Parameters:
    - response (dict): response from API request
    - fields_to_extract (list): list of field names
    
    Returns:
    - parsed_response (dict): dict of values for each field
    
    Raises:
    - Exception: API response not parsed
    '''
    
    # dict comprehension to extract given fields
    try:
        parsed_response = {record['id']: {field: record['fields'][field] for field in fields_to_extract} for record in response['records']}
        return parsed_response
    
    except KeyError as e:
        logging.error(f'parse_api_response: Invalid key found when parsing API response.', exc_info=True)
        raise
    except Exception as e:
        logging.error('parse_api_response: Error extracting fields from API response.', exc_info=True)
        raise

def check_expiration(parsed_orders: dict, id_name: dict, warn_days: int) -> list:
    '''
    Check expiration dates in order history.

    Parameters:
    - parsed_order_history (dict): product order history and related info
    - id_name (dict): product ids and names
    - warn_days (int): days allowed till expiration date 

    Returns:
    - alerts (list): list of expiration alerts
    
    Raises:
    - ValueError: warn_days not valid | order history contained unexpected data type
    - KeyError: product not found with id
    '''
    
    # init alerts list
    alerts = []
    
    # check warn_days for positive int
    if not isinstance(warn_days, int) or warn_days <= 0:
        logging.error('check_expiration: warn_days must be a positive integer.')
        raise ValueError('check_expiration: warn_days must be a positive integer.')
    
    # for each order get id and info
    for order_id, order_info in parsed_orders.items():
        try:
            # extract specifics from order_info
            product_id = order_info['Product'][0]
            expiration_date = order_info['Expiration Date']
            order_date = order_info['Order Date']
            
            # get product name from id
            product_name = id_name.get(product_id, {}).get('Name', 'Unknown Product')
            
            # turn dates into datetime objects
            expiration_datetime = datetime.strptime(expiration_date, '%Y-%m-%d')
            order_datetime = datetime.strptime(order_date, '%Y-%m-%d')
            
            # check days till expiration
            days_till_exp = (expiration_datetime - datetime.today()).days
            
            # make alert if expiration is close
            if 0 <= days_till_exp <= warn_days:
                alert_message = f'{product_name} ordered on {order_datetime.strftime('%B %d, %Y')} is {days_till_exp} days from expiring on {expiration_datetime.strftime('%B %d, %Y')}.'
                alerts.append(alert_message)
                logging.info(f'check_expiration: {alert_message}')
            
        except KeyError as e:
            logging.error(f'check_expiration: Missing expected key in order {order_id}: {e}.')
            raise
        except ValueError as e:
            logging.error(f'check_expiration: Invalid data in order {order_id}: {e}.')
            raise
            
    
    if not alerts:
        logging.info('check_expiration: No products are near expiration.')
        
    return alerts

def project_usage(parsed_orders: dict, parsed_usage: dict, id_name: dict, warn_days: int) -> list:
    '''
    Project when products will run out.

    Parameters:
    - parsed_orders (dict): product order history and related info
    - parsed_usage (dict): product usage history
    - id_name (dict): product ids and names
    - warn_days (int): days allowed till projected runout

    Returns:
    - alerts (list): list of projected runout alerts
    
    Raises:
    - ValueError: warn_days not valid
    - Exception: inventory projection failed
    '''
    
    # init alerts list
    alerts = []
    
    # check warn_days for positive int
    if not isinstance(warn_days, int) or warn_days <= 0:
        logging.error('project_usage: warn_days must be a positive integer.')
        raise ValueError('project_usage: warn_days must be a positive integer.')

    try:
        # init temp dicts for projection calculations 
        product_usage = {product_id: {'total_used': 0, 'first_used': None} for product_id in id_name}
        product_stock = {product_id: {'total_ordered': 0, 'first_ordered': None} for product_id in id_name}

        # populate product_usage with total and earliest usage
        for _, usage_info in parsed_usage.items():
            product_id = usage_info['Product'][0]
            usage_amount = usage_info['Amount Used']
            usage_date = datetime.strptime(usage_info['Usage Date'], '%Y-%m-%d')

            product_usage[product_id]['total_used'] += usage_amount
            
            # update earliest with earlier usage
            if product_usage[product_id]['first_used'] is None or usage_date < product_usage[product_id]['first_used']:
                product_usage[product_id]['first_used'] = usage_date

        # populate product_stock with total and earliest bought
        for _, order_info in parsed_orders.items():
            product_id = order_info['Product'][0]
            order_amount = order_info['Amount Bought']
            order_date = datetime.strptime(order_info['Order Date'], '%Y-%m-%d')

            product_stock[product_id]['total_ordered'] += order_amount
            
            # update earliest bought with earlier purchase
            if product_stock[product_id]['first_ordered'] is None or order_date < product_stock[product_id]['first_ordered']:
                product_stock[product_id]['first_ordered'] = order_date

        # project inventory usage
        for product_id in id_name:
            # get days since first use
            if product_usage[product_id]['first_used'] is not None:
                days_since_first_used = (CURRENT_TIMESTAMP - product_usage[product_id]['first_used']).days
            else:
                days_since_first_used = 0

            # get average use per day
            if days_since_first_used > 0:
                avg_use_per_day = product_usage[product_id]['total_used'] / days_since_first_used
            else:
                avg_use_per_day = None

            # check how long current stock will last based on average usage
            remaining_stock = product_stock[product_id]['total_ordered'] - product_usage[product_id]['total_used']
            if avg_use_per_day and remaining_stock > 0:
                days_till_out = remaining_stock / avg_use_per_day
                # get projected runout date
                adjusted_run_out_day = CURRENT_TIMESTAMP + timedelta(days=days_till_out)

                logging.info(f'project_usage: {id_name[product_id]['Name']} remaining stock: {remaining_stock}, use per day: {avg_use_per_day}, days till out: {days_till_out}.')
                
                # if product is projected to run out within warn_days
                if 0 < days_till_out <= warn_days:
                    alert_message = f'{id_name[product_id]['Name']} is projected to run out in {int(days_till_out)} days on {adjusted_run_out_day.strftime('%B %d, %Y')}.'
                    alerts.append(alert_message)

    except Exception as e:
        logging.warning('project_usage: Failed to calculate low inventory projections.', exc_info=True)
        raise

    if not alerts:
        logging.info('project_usage: No products are projected to run out soon.')
    
    return alerts

def compile_email_report(reports: list) -> MIMEText:
    '''
    Compile email report in HTML.

    Parameters:
    - reports (list): list of inventory alerts

    Returns:
    - msg (MIMEText): email message in HTML
    
    Raises:
    - ValueError: reports was invalid | 
    - Exception: compiling email failed
    '''
    try:
        # check reports for valid type
        if reports is not None and not isinstance(reports, list):
            logging.error(f'compile_email_report: Invalid input for reports. Expected list but got {type(reports)}.')
            raise ValueError('compile_email_report: reports parameter should be a list.')
        
        # message body in HTML
        msg_body = f'''
        <html>
            <body>
                <p>This is your automated inventory report generated on {CURRENT_TIMESTAMP.strftime('%B %d, %Y')}.</p>
                <p><strong>Inventory Alerts:</strong></p>
        '''
        
        # if there are reports
        if reports:
            # dark circle bullets
            msg_body += '<ul style="list-style-type: disc; color: black;">'  
            for r in reports:
                # italicize product name using regex
                r = re.sub(r'([a-zA-Z0-9\s]+)(?=\s(ordered|is\sprojected))', r'<em>\1</em>', r)
                msg_body += f'<li>{r}</li>'
            msg_body += '</ul>'
        else:
            msg_body += '<p><em>No inventory alerts.</em></p>'
        
        # close HTML tags
        msg_body += '</body></html>'
        
        # cast HTML content to MIMEText
        msg = MIMEText(msg_body, 'html')
        msg['Subject'] = f'Inventory Report: {CURRENT_TIMESTAMP.strftime('%B %d, %Y')}'
        
        logging.info('compile_email_report: Email report compiled successfully.')
        logging.info(f'compile_email_report: Email content: {msg}\n')
        
        return msg
    
    except ValueError as e:
        logging.error(f'compile_email_report: Error while compiling email report: {e}.')
        raise  
    except Exception as e:
        logging.error(f'compile_email_report: Unexpected error occurred: {e}.')
        raise

def main() -> None:
    '''
    Run inventory checks and send email report.

    Parameters: 
    - none
    
    Returns:
    - none
    
    Raises:
    - Exception: running checks and sending report failed
    '''
    
    try:
        # get environment variables
        logging.debug('main: Retrieving environment variables.')
        exp_warn_days = get_env_var('DAYS_BEFORE_EXPIRATION_ALERT', int)
        runout_warn_days = get_env_var('DAYS_BEFORE_PROJECTED_RUN_OUT_ALERT', int)
        api_token = get_env_var('API_TOKEN', log_sensitive=True)
        inv_base_id = get_env_var('INVENTORY_BASE_ID')
        product_table_id = get_env_var('PRODUCT_TABLE_ID')
        order_table_id = get_env_var('ORDER_TABLE_ID')
        usage_table_id = get_env_var('USAGE_TABLE_ID')
        email_address = get_env_var('EMAIL_ADDRESS')
        email_password = get_env_var('EMAIL_APP_PASSWORD', log_sensitive=True)
        email_smtp = get_env_var('EMAIL_SMTP_ADDRESS')

        # init handler classes
        logging.debug('main: Initializing API and email handlers.')
        api_handler = APIHandler(api_token=api_token)
        email_handler = EmailHandler(email_smtp_address=email_smtp,
                                     email_address=email_address,
                                     email_password=email_password)

        # request and parse product list
        logging.debug(f'main: Requesting product list from API.')
        product_request = api_handler.request(f'https://api.airtable.com/v0/{inv_base_id}/{product_table_id}')
        if product_request is None:
            logging.error('main: Failed to fetch product list.')
            return
        product_id_name = parse_api_response(product_request, ['Name'])


        # request and parse product order history
        logging.debug(f'main: Requesting order history from API.')
        orders_request = api_handler.request(f'https://api.airtable.com/v0/{inv_base_id}/{order_table_id}')
        if orders_request is None:
            logging.error('main: Failed to fetch order history.')
            return
        order_history = parse_api_response(orders_request, ['Product', 'Amount Bought', 'Expiration Date', 'Order Date'])

        # request and parse product usage history
        logging.debug(f'main: Requesting usage history from API.')
        usage_request = api_handler.request(f'https://api.airtable.com/v0/{inv_base_id}/{usage_table_id}')
        if usage_request is None:
            logging.error('main: Failed to fetch usage history.')
            return
        usage_history = parse_api_response(usage_request, ['Product', 'Amount Used', 'Usage Date'])

        # get expiration and low inventory alerts
        logging.debug('main: Checking for expiration alerts.')
        reports = check_expiration(order_history, product_id_name, exp_warn_days)
        
        logging.debug('main: Checking for projected runout alerts.')
        reports += project_usage(order_history, usage_history, product_id_name, runout_warn_days)

        # compile email report
        logging.debug('main: Compiling email report.')
        compiled_report = compile_email_report(reports)

        # send email with compiled report
        logging.debug('main: Sending email report.')
        email_sent = email_handler.send_email(compiled_report)
        if email_sent:
            logging.info('main: Email report sent successfully.')
        else:
            logging.error('main: Failed to send email report.')

    except Exception as e:
        logging.error('main: An unexpected error occurred.', exc_info=True)
        raise


if __name__ =='__main__':
    main()

