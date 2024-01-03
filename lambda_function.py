import os
import logging
import json

import requests
from dotenv import load_dotenv
import signal

from webdriver_client import chrome_headless, chrome_testing
from tasks import customers_today, daily_scrape, weekly_scrape, monthly_scrape, year_orders, year_appointments, \
    test_response, daily_completed_appointments, create_customer, all_customers, new_typeform_customer
from tempfile import TemporaryDirectory
import segment.analytics as analytics
from invalid_file_handler import InvalidFileHandler

seg_logger = logging.getLogger('segment')
seg_logger.setLevel(logging.DEBUG)
seg_logger.addHandler(logging.StreamHandler())


logger = logging.getLogger()
# logger.addHandler(logging.StreamHandler(sys.stdout))
# logger.setLevel(logging.INFO)
load_dotenv()

MISSING_ENVIRONMENT_VARIABLES = []


def get_env_variable(var_name, default=None):
    value = os.getenv(var_name, default)
    if not value:
        MISSING_ENVIRONMENT_VARIABLES.append(var_name)
    return value


BOOKER_ACCOUNT = get_env_variable('BOOKER_ACCOUNT')
BOOKER_USERNAME = get_env_variable('BOOKER_USERNAME')
BOOKER_PASSWORD = get_env_variable('BOOKER_PASSWORD')
SEGMENT_WRITE_KEY = get_env_variable('SEGMENT_WRITE_KEY')
ENVIRONMENT = get_env_variable('ENVIRONMENT', 'test')
S3_BUCKET_NAME = get_env_variable('S3_BUCKET_NAME')
S3_AWS_REGION = get_env_variable('S3_AWS_REGION')
SENDER_EMAIL = get_env_variable('SENDER_EMAIL')
RECEIVER_EMAIL = get_env_variable('RECEIVER_EMAIL')
TYPEFORM_OBJECTS_URL = get_env_variable('TYPEFORM_OBJECTS_URL')

analytics.write_key = SEGMENT_WRITE_KEY
analytics.debug = True
analytics.send = True


def timeout_handler(signum, frame):
    raise TimeoutError("Timout reached")


# Set the signal handler
signal.signal(signal.SIGALRM, timeout_handler)


def check_internet_connection(url="https://www.google.com", timeout=5):
    """Return True if there's an active internet connection."""
    try:
        response = requests.get(url, timeout=timeout)
        return True if response.status_code == 200 else False
    except requests.ConnectionError:
        return False


TASKS = {
    'customers_today': customers_today,
    'daily': daily_scrape,
    'completed_appointments': daily_completed_appointments,
    'weekly': weekly_scrape,
    'monthly': monthly_scrape,
    'year_orders': year_orders,
    'year_appointments': year_appointments,
    'test': test_response,
    'create_customer': create_customer,
    'all_customers': all_customers,
    'new_typeform_customer': new_typeform_customer
}


def handler(event, context):
    if len(MISSING_ENVIRONMENT_VARIABLES) > 0:
        error = f'Internal Server Error - Missing environment variables: {", ".join(MISSING_ENVIRONMENT_VARIABLES)}'
        logger.error(error)
        return {
            'statusCode': 500,
            'message': error
        }
    # if not check_internet_connection():
    #     return {
    #         'statusCode': 500,
    #         'message': 'Internal Server Error - No internet connection'
    #     }
    # logger.debug('Internet connection is established')

    inval_file_handler = InvalidFileHandler(S3_BUCKET_NAME, S3_AWS_REGION, SENDER_EMAIL, RECEIVER_EMAIL, logger)

    body = event.get('body', None)
    if body is not None:
        event = json.loads(body)

    task = event.get('task', None)
    if task is None:
        return {
            'statusCode': 400,
            'message': 'Bad Request - No task specified'
        }
    task_func = TASKS.get(task, None)
    if task_func is None:
        return {
            'statusCode': 400,
            'message': 'Bad Request - Task not found'
        }

    with TemporaryDirectory() as download_dir:
        if ENVIRONMENT == 'test':
            driver = chrome_testing(download_dir)
        else:
            driver = chrome_headless(logger, download_dir)

        args = [driver, download_dir, analytics]
        additional_args = []
        if task == 'create_customer':
            customer_data = event.get('customer', None)
            if customer_data is None:
                return {
                    'statusCode': 400,
                    'message': 'Bad Request - No customer answers provided'
                }
            args.append(customer_data)
            logger.debug(f'Customer data: {customer_data}')
        elif task == 'new_typeform_customer':
            additional_args = [
                event.get('customer', None),
                event.get('typeform', None),
                event.get('source_key', None),
                TYPEFORM_OBJECTS_URL
            ]
            if not all(additional_args):
                return {
                    'statusCode': 400,
                    'message': 'Bad Request - Missing required parameters'
                }
            args.extend(additional_args)
        elif task == 'order_from_appointment':
            additional_args = [
                event.get('appointment_id', None),
                event.get('location', None)
            ]
        if not all(additional_args):
            return {
                'statusCode': 400,
                'message': 'Bad Request - Missing required parameters'
            }
        args.extend(additional_args)
        try:
            response = task_func(*args)
        except Exception as e:
            driver.quit()
            logger.error(f'Error in task {task}: {e}')
            return {
                'statusCode': 500,
                'message': f'Internal Server Error - Error in task {task}: {e}'
            }

    driver.quit()

    try:
        signal.alarm(10)
        analytics.shutdown()
    except TimeoutError as e:
        logger.error("Analytics shutdown took too long")
        return {
            'statusCode': 500,
            'message': 'Internal Server Error - Analytics shutdown took too long'
        }
    if inval_file_handler is not None and inval_file_handler.has_errors():
        logger.error(f'Task completed with errors: {inval_file_handler.error_count()} errors')
        return {
            'statusCode': 200,
            'message': 'Task completed with errors',
            'error_count': inval_file_handler.error_count()
        }

    if response:
        return response
    else:
        return {
            'statusCode': 200,
            'body': 'success'
        }


if __name__ == '__main__':
    # typeform_event = {
    #     "task": "new_typeform_customer",
    #     "customer": {
    #         "firstName": "Test",
    #         "lastName": "User",
    #         "email": "test12@sarahhamiltonface.com",
    #         "phone": "2345678902"
    #     },
    #     "typeform": {
    #         "type": "track",
    #         "event": "Anonymous Typeform Submission",
    #         "anonymousId": "asdf",
    #         "properties": {
    #             "Phone number": "+1234567890",
    #             "Great! Now which treatment's are you most interested in?": "Skin Tightening,Wrinkle Reduction,Skin Clarity/Texture Improvements,Tattoo Removal",
    #             "First name": "Test",
    #             "Email": "test@sarahhamiltonface.com",
    #             "WELCOME!\n\nFirst off we'd love to know which Sarah Hamilton Face location you're closest to?": "Liberty Lake, Washington",
    #             "Last name": "User",
    #             "Alright, what's the best time for our team to reach out to you?": "Afternoon",
    #             "WELCOME!\n\nWhich location is closest to you?": "Liberty Lake, Washington",
    #             "Great! Now what types of treatment's are you most interested in?": "Wrinkle Reduction,Skin Clarity/Texture Improvements"
    #         }
    #     },
    #     "source_key": "Bs5XZk0MOOADDUaFYbWBJC1MCOhyPEeV",
    #     "callback_object": "https://ed41-66-27-6-67.ngrok-free.app"
    # }
    # handler(typeform_event, {})
    handler({
        "task": "monthly"
    }, {})

    # handler({
    #     "task": "create_customer",
    #     "customer": {
    #         "first_name": "Test",
    #         "last_name": "User",
    #         "email": "test@test.com",
    #         "phone": "1234567899"
    #     }
    # }, {})
