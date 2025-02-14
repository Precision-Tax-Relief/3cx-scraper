import os
from scraper import Scraper


def scrape_3cx(driver, logger):
    try:
        scraper = Scraper(
            driver=driver
        )
        scraper.login(
            os.environ.get('ACCOUNT'),
            os.environ.get('PASSWORD'),
        )
        logger.info("Logged in")
    except Exception as e:
        driver.quit()
        raise (e)
    
    

    # for location in scraper.locations.values():
    #     with TemporaryDirectory() as dest_dir:
    #         scraper.destination_dir = dest_dir
    #         scraper.appointments_flow(location, date_type='date_created')
    #         parser = BookerParser(dest_dir)
    #         a_df, t_df = parser.import_appointments()
    #     send_appointments(a_df, t_df, analytics)
    # 
    #     with TemporaryDirectory() as dest_dir:
    #         scraper.destination_dir = dest_dir
    #         scraper.orders_flow(location)
    #         parser = BookerParser(dest_dir)
    #         df = parser.import_orders()
    #     send_orders(df, analytics)


# def string_to_uuid(s):
#     sha1 = hashlib.sha1(s.encode())
#     # Take the first 16 bytes from the SHA-1 hash to create the UUID.
#     return str(uuid.UUID(bytes=sha1.digest()[:16]))
# 
# 
# def send_customers(dataframe, analytics):
#     i = 0
#     for row in dataframe.iterrows():
#         data = dict(row[1])
#         analytics.object(object_id=data['guid'], collection='customers', properties=data)
#         i += 1
#         if i % 200 == 0:
#             analytics.flush()
# 
# 
# def send_appointments(appointment_dataframe, treatment_dataframe, analytics):
#     for row in appointment_dataframe.iterrows():
#         data = dict(row[1])
#         analytics.object(object_id=str(data['booking_number']), collection='appointments', properties=data)
# 
#     for row in treatment_dataframe.iterrows():
#         data = dict(row[1])
#         analytics.object(object_id=string_to_uuid(f'{data["appointment"]}{data["appointment_on"]}'),
#                          collection='treatments',
#                          properties=data)
#     analytics.flush()
# 
# 
# def update_appointment_order(appointment_id, order_id, analytics):
#     analytics.object(object_id=str(appointment_id), collection='appointments', properties={'order_number': order_id})
# 
# 
# def send_orders(dataframe, analytics):
#     for row in dataframe.iterrows():
#         data = dict(row[1])
#         analytics.object(object_id=str(data['order_number']), collection='orders', properties=data)
#     analytics.flush()
# 
# 
# def create_customer(driver, download_dir, analytics, customer_data):
#     try:
#         scraper = BookerScraper(
#             driver=driver,
#             start_date=datetime.date.today() - datetime.timedelta(days=1),
#             end_date=datetime.date.today() + datetime.timedelta(days=1),
#         )
#         scraper.login(
#             os.environ.get('BOOKER_ACCOUNT'),
#             os.environ.get('BOOKER_USERNAME'),
#             os.environ.get('BOOKER_PASSWORD')
#         )
#         customer_id = scraper.customer_create_flow(customer_data)
#         message = {
#             'customer_id': customer_id,
#             'message': f'Created customer with id {customer_id}'
#         }
#         from json import dumps
#         return {
#             'statusCode': 201,
#             'body': dumps(message)
#         }
#     except Exception as e:
#         driver.quit()
#         raise (e)
# 
# 
# def new_typeform_customer(driver, download_dir, analytics, customer, typeform, source_key, callback_object):
#     try:
#         scraper = BookerScraper(
#             driver=driver,
#             start_date=datetime.date.today() - datetime.timedelta(days=1),
#             end_date=datetime.date.today() + datetime.timedelta(days=1),
#         )
#         scraper.login(
#             os.environ.get('BOOKER_ACCOUNT'),
#             os.environ.get('BOOKER_USERNAME'),
#             os.environ.get('BOOKER_PASSWORD')
#         )
#         customer_id = scraper.customer_create_flow(customer)
#         logging.debug(f'Created customer with id {customer_id}')
#         print(f'Created customer with id {customer_id}')
# 
#         object_json = {
#             "event_type": "assign_id",
#             "form_id": typeform['anonymousId'],
#             "customer_id": customer_id,
#         }
#         response = requests.post(callback_object, json=object_json)
#         assert response.status_code == 200
# 
#         analytics.default_client = None
#         analytics.write_key = source_key
#         analytics.identify(user_id=customer_id, traits=customer)
#         analytics.flush()
#         sleep(3)
#         analytics.track(user_id=customer_id, event="Typeform Submission", properties=typeform['properties'])
#         analytics.shutdown()
#         analytics.default_client = None
# 
#         message = {
#             'customer_id': customer_id,
#             'message': f'Created customer with id {customer_id}'
#         }
#         from json import dumps
#         return {
#             'statusCode': 201,
#             'body': dumps(message)
#         }
#     except Exception as e:
#         driver.quit()
#         raise (e)
# 
# 
# def customers_today(driver, download_dir, analytics):
#     # TODO: Add check if multiple pages of customers exist, and then loop through them
#     with TemporaryDirectory() as dest_dir:
#         try:
#             scraper = BookerScraper(
#                 driver=driver,
#                 start_date=datetime.date.today() - datetime.timedelta(days=1),
#                 end_date=datetime.date.today() + datetime.timedelta(days=1),
#                 download_dir=download_dir,
#                 destination_dir=dest_dir,
#             )
#             scraper.login(
#                 os.environ.get('BOOKER_ACCOUNT'),
#                 os.environ.get('BOOKER_USERNAME'),
#                 os.environ.get('BOOKER_PASSWORD')
#             )
#             scraper.customer_added_today_flow()
#         except Exception as e:
#             driver.quit()
#             raise (e)
# 
#         parser = BookerParser(dest_dir)
#         df = parser.parse_customers()
#     send_customers(df, analytics)
#     return f'Imported {len(df)} customers from today.'
# 
# 
# def daily_scrape(driver, download_dir, analytics):
#     with TemporaryDirectory() as dest_dir:
#         try:
#             scraper = BookerScraper(
#                 driver=driver,
#                 start_date=datetime.date.today() - datetime.timedelta(days=2),
#                 end_date=datetime.date.today(),
#                 download_dir=download_dir,
#                 destination_dir=dest_dir,
#                 export_period=2
#             )
#             scraper.login(
#                 os.environ.get('BOOKER_ACCOUNT'),
#                 os.environ.get('BOOKER_USERNAME'),
#                 os.environ.get('BOOKER_PASSWORD')
#             )
#         except Exception as e:
#             driver.quit()
#             raise (e)
# 
#     for location in scraper.locations.values():
#         with TemporaryDirectory() as dest_dir:
#             scraper.destination_dir = dest_dir
#             scraper.appointments_flow(location, date_type='date_created')
#             parser = BookerParser(dest_dir)
#             a_df, t_df = parser.import_appointments()
#         send_appointments(a_df, t_df, analytics)
# 
#         with TemporaryDirectory() as dest_dir:
#             scraper.destination_dir = dest_dir
#             scraper.orders_flow(location)
#             parser = BookerParser(dest_dir)
#             df = parser.import_orders()
#         send_orders(df, analytics)
# 
# 
# def daily_appointments_booked(driver, download_dir, analytics):
#     with TemporaryDirectory() as dest_dir:
#         try:
#             scraper = BookerScraper(
#                 driver=driver,
#                 start_date=datetime.date.today() - datetime.timedelta(days=2),
#                 end_date=datetime.date.today(),
#                 download_dir=download_dir,
#                 destination_dir=dest_dir,
#                 export_period=2
#             )
#             scraper.login(
#                 os.environ.get('BOOKER_ACCOUNT'),
#                 os.environ.get('BOOKER_USERNAME'),
#                 os.environ.get('BOOKER_PASSWORD')
#             )
#         except Exception as e:
#             driver.quit()
#             raise (e)
# 
#     for location in scraper.locations.values():
#         with TemporaryDirectory() as dest_dir:
#             scraper.destination_dir = dest_dir
#             scraper.appointments_flow(location, date_type='date_created')
#             parser = BookerParser(dest_dir)
#             a_df, t_df = parser.import_appointments()
#         send_appointments(a_df, t_df, analytics)
# 
# 
# def daily_orders(driver, download_dir, analytics):
#     with TemporaryDirectory() as dest_dir:
#         try:
#             scraper = BookerScraper(
#                 driver=driver,
#                 start_date=datetime.date.today() - datetime.timedelta(days=2),
#                 end_date=datetime.date.today(),
#                 download_dir=download_dir,
#                 destination_dir=dest_dir,
#                 export_period=2
#             )
#             scraper.login(
#                 os.environ.get('BOOKER_ACCOUNT'),
#                 os.environ.get('BOOKER_USERNAME'),
#                 os.environ.get('BOOKER_PASSWORD')
#             )
#         except Exception as e:
#             driver.quit()
#             raise (e)
# 
#     for location in scraper.locations.values():
#         with TemporaryDirectory() as dest_dir:
#             scraper.destination_dir = dest_dir
#             scraper.orders_flow(location)
#             parser = BookerParser(dest_dir)
#             df = parser.import_orders()
#         send_orders(df, analytics)
# 
# 
# def daily_completed_appointments(driver, download_dir, analytics):
#     with TemporaryDirectory() as dest_dir:
#         try:
#             scraper = BookerScraper(
#                 driver=driver,
#                 start_date=datetime.date.today() - datetime.timedelta(days=1),
#                 end_date=datetime.date.today(),
#                 download_dir=download_dir,
#                 destination_dir=dest_dir,
#                 export_period=1
#             )
#             scraper.login(
#                 os.environ.get('BOOKER_ACCOUNT'),
#                 os.environ.get('BOOKER_USERNAME'),
#                 os.environ.get('BOOKER_PASSWORD')
#             )
#         except Exception as e:
#             driver.quit()
#             raise (e)
# 
#     for location in scraper.locations.values():
#         with TemporaryDirectory() as dest_dir:
#             scraper.destination_dir = dest_dir
#             scraper.appointments_flow(location)
#             parser = BookerParser(dest_dir)
#             a_df, t_df = parser.import_appointments()
# 
#         send_appointments(a_df, t_df, analytics)
# 
# 
# def weekly_scrape(driver, download_dir, analytics):
#     with TemporaryDirectory() as dest_dir:
#         try:
#             scraper = BookerScraper(
#                 driver=driver,
#                 start_date=datetime.date.today() - datetime.timedelta(days=7),
#                 end_date=datetime.date.today() + datetime.timedelta(days=7),
#                 download_dir=download_dir,
#                 destination_dir=dest_dir,
#                 export_period=8
#             )
#             scraper.login(
#                 os.environ.get('BOOKER_ACCOUNT'),
#                 os.environ.get('BOOKER_USERNAME'),
#                 os.environ.get('BOOKER_PASSWORD')
#             )
#             scraper.customer_added_last_week_flow()
#             parser = BookerParser(dest_dir)
#             df = parser.parse_customers()
#         except Exception as e:
#             driver.quit()
#             raise (e)
#     send_customers(df, analytics)
# 
#     for location in scraper.locations.values():
#         with TemporaryDirectory() as dest_dir:
#             scraper.destination_dir = dest_dir
#             scraper.appointments_flow(location)
#             parser = BookerParser(dest_dir)
#             a_df, t_df = parser.import_appointments()
#         send_appointments(a_df, t_df, analytics)
# 
#         with TemporaryDirectory() as dest_dir:
#             scraper.destination_dir = dest_dir
#             scraper.orders_flow(location)
#             parser = BookerParser(dest_dir)
#             df = parser.import_orders()
#         send_orders(df, analytics)
# 
# 
# def custom_order(driver, download_dir, analytics):
#     with TemporaryDirectory() as dest_dir:
#         try:
#             scraper = BookerScraper(
#                 driver=driver,
#                 start_date=datetime.date.today() - datetime.timedelta(days=365),
#                 end_date=datetime.date.today() + datetime.timedelta(days=62),
#                 download_dir=download_dir,
#                 destination_dir=dest_dir,
#                 export_period=7
#             )
#             scraper.login(
#                 os.environ.get('BOOKER_ACCOUNT'),
#                 os.environ.get('BOOKER_USERNAME'),
#                 os.environ.get('BOOKER_PASSWORD')
#             )
#         except Exception as e:
#             driver.quit()
#             raise (e)
# 
#     # for location in scraper.locations.values():
#     location = scraper.locations['ll']
#     with TemporaryDirectory() as dest_dir:
#         scraper.destination_dir = dest_dir
#         scraper.orders_flow(location)
#         parser = BookerParser(dest_dir)
#         df = parser.import_orders()
#     send_orders(df, analytics)
# 
# 
# def custom_appointments(driver, download_dir, analytics):
#     with TemporaryDirectory() as dest_dir:
#         try:
#             scraper = BookerScraper(
#                 driver=driver,
#                 start_date=datetime.date.today() - datetime.timedelta(days=0),
#                 end_date=datetime.date.today() + datetime.timedelta(days=60),
#                 download_dir=download_dir,
#                 destination_dir=dest_dir,
#                 export_period=21,
#                 wait_time=120,
#             )
#             scraper.login(
#                 os.environ.get('BOOKER_ACCOUNT'),
#                 os.environ.get('BOOKER_USERNAME'),
#                 os.environ.get('BOOKER_PASSWORD')
#             )
#         except Exception as e:
#             driver.quit()
#             raise (e)
# 
#     # for location in scraper.locations.values():
#     location = scraper.locations['ll']
#     with TemporaryDirectory() as dest_dir:
#         scraper.destination_dir = dest_dir
#         scraper.appointments_flow(location)
#         parser = BookerParser(dest_dir)
#         a_df, t_df = parser.import_appointments()
#     send_appointments(a_df, t_df, analytics)
# 
# 
# def all_customers(driver, download_dir, analytics):
#     with TemporaryDirectory() as dest_dir:
#         try:
#             scraper = BookerScraper(
#                 driver=driver,
#                 start_date=datetime.date.today() - datetime.timedelta(days=35),
#                 end_date=datetime.date.today() + datetime.timedelta(days=32),
#                 download_dir=download_dir,
#                 destination_dir=dest_dir,
#                 export_period=10
#             )
#             scraper.login(
#                 os.environ.get('BOOKER_ACCOUNT'),
#                 os.environ.get('BOOKER_USERNAME'),
#                 os.environ.get('BOOKER_PASSWORD')
#             )
#             scraper.customer_flow()
#             parser = BookerParser(dest_dir)
#             df = parser.parse_customers()
#             send_customers(df, analytics)
#         except Exception as e:
#             driver.quit()
#             raise (e)
# 
# 
# def monthly_scrape(driver, download_dir, analytics):
#     with TemporaryDirectory() as dest_dir:
#         try:
#             scraper = BookerScraper(
#                 driver=driver,
#                 start_date=datetime.date.today() - datetime.timedelta(days=32),
#                 end_date=datetime.date.today() + datetime.timedelta(days=1),
#                 download_dir=download_dir,
#                 destination_dir=dest_dir,
#                 export_period=10
#             )
#             scraper.login(
#                 os.environ.get('BOOKER_ACCOUNT'),
#                 os.environ.get('BOOKER_USERNAME'),
#                 os.environ.get('BOOKER_PASSWORD')
#             )
#             # scraper.customer_flow()
#             # parser = BookerParser(dest_dir)
#             # df = parser.parse_customers()
#         except Exception as e:
#             driver.quit()
#             raise (e)
#     # send_customers(df, analytics)
# 
#     for location in scraper.locations.values():
#         with TemporaryDirectory() as dest_dir:
#             scraper.destination_dir = dest_dir
#             scraper.appointments_flow(location)
#             parser = BookerParser(dest_dir)
#             a_df, t_df = parser.import_appointments()
#         send_appointments(a_df, t_df, analytics)
# 
#         with TemporaryDirectory() as dest_dir:
#             scraper.destination_dir = dest_dir
#             scraper.orders_flow(location)
#             parser = BookerParser(dest_dir)
#             df = parser.import_orders()
#         send_orders(df, analytics)
# 
# 
# def customer_weekly_scrape(driver, download_dir, analytics):
#     with TemporaryDirectory() as dest_dir:
#         try:
#             scraper = BookerScraper(
#                 driver=driver,
#                 start_date=datetime.date.today() + datetime.timedelta(days=30),
#                 end_date=datetime.date.today() + datetime.timedelta(days=30),
#                 download_dir=download_dir,
#                 destination_dir=dest_dir,
#             )
#             scraper.login(
#                 os.environ.get('BOOKER_ACCOUNT'),
#                 os.environ.get('BOOKER_USERNAME'),
#                 os.environ.get('BOOKER_PASSWORD')
#             )
#             scraper.customer_added_last_week_flow()
#         except Exception as e:
#             driver.quit()
#             raise (e)
#         parser = BookerParser(dest_dir)
#         df = parser.parse_customers()
#         send_customers(df, analytics)
# 
# 
# def appointments_test(driver, download_dir, analytics):
#     with TemporaryDirectory() as dest_dir:
#         try:
#             scraper = BookerScraper(
#                 driver=driver,
#                 start_date=datetime.date.today() - datetime.timedelta(days=60),
#                 end_date=datetime.date.today() + datetime.timedelta(days=30),
#                 download_dir=download_dir,
#                 destination_dir=dest_dir,
#             )
#             scraper.login(
#                 os.environ.get('BOOKER_ACCOUNT'),
#                 os.environ.get('BOOKER_USERNAME'),
#                 os.environ.get('BOOKER_PASSWORD')
#             )
#             scraper.appointments_flow(scraper.locations['cda'])
#             scraper.appointments_flow(scraper.locations['ll'])
#         except Exception as e:
#             driver.quit()
#             raise (e)
#         parser = BookerParser(dest_dir)
#         a_df, t_df = parser.import_appointments()
# 
#     send_appointments(a_df, t_df, analytics)
# 
# 
# def order_for_appointment(driver, download_dir, analytics, appointment_id, location_id):
#     with TemporaryDirectory() as dest_dir:
#         try:
#             scraper = BookerScraper(
#                 driver=driver,
#                 start_date=datetime.date.today() - datetime.timedelta(days=14),
#                 end_date=datetime.date.today() + datetime.timedelta(days=2),
#                 download_dir=download_dir,
#                 destination_dir=dest_dir,
#             )
#             scraper.login(
#                 os.environ.get('BOOKER_ACCOUNT'),
#                 os.environ.get('BOOKER_USERNAME'),
#                 os.environ.get('BOOKER_PASSWORD')
#             )
#             map = scraper.appointment_map_booking_numbers_to_orders(
#                 {'id': location_id},
#                 [appointment_id]
#             )
#             update_appointment_order(appointment_id, map[appointment_id], analytics)
#         except Exception as e:
#             driver.quit()
#             raise (e)
#         return map
# 
# 
# def order_test(driver, download_dir, analytics):
#     with TemporaryDirectory() as dest_dir:
#         try:
#             scraper = BookerScraper(
#                 driver=driver,
#                 start_date=datetime.date.today() - datetime.timedelta(days=14),
#                 end_date=datetime.date.today() + datetime.timedelta(days=2),
#                 download_dir=download_dir,
#                 destination_dir=dest_dir,
#             )
#             scraper.login(
#                 os.environ.get('BOOKER_ACCOUNT'),
#                 os.environ.get('BOOKER_USERNAME'),
#                 os.environ.get('BOOKER_PASSWORD')
#             )
#             scraper.orders_flow(scraper.locations['cda'])
#             scraper.orders_flow(scraper.locations['ll'])
#         except Exception as e:
#             driver.quit()
#             raise (e)
#         parser = BookerParser(dest_dir)
#         df = parser.import_orders()
# 
# 
# def appointment_map(driver, download_dir, analytics):
#     from models import get_unmapped_appointments
#     appointments = get_unmapped_appointments()
# 
#     time_limit = datetime.datetime.now() + datetime.timedelta(minutes=10)
# 
#     with TemporaryDirectory() as dest_dir:
#         amount = 0
#         try:
#             scraper = BookerScraper(
#                 driver=driver,
#                 start_date=datetime.date.today() - datetime.timedelta(days=14),
#                 end_date=datetime.date.today() + datetime.timedelta(days=2),
#                 download_dir=download_dir,
#                 destination_dir=dest_dir,
#             )
#             scraper.login(
#                 os.environ.get('BOOKER_ACCOUNT'),
#                 os.environ.get('BOOKER_USERNAME'),
#                 os.environ.get('BOOKER_PASSWORD')
#             )
#             for location in appointments.keys():
#                 for booking_number, order_number in scraper.appointment_map_booking_numbers_to_orders(
#                     {"id": location},
#                     appointments[location]
#                 ):
#                     update_appointment_order(booking_number, order_number, analytics)
#                     amount += 1
#                     if datetime.datetime.now() > time_limit:
#                         break
#         except Exception as e:
#             driver.quit()
#             raise (e)
#         return f"Updated {amount} appointments"
# 
# 
# def test_response(driver, download_dir, analytics):
#     return {
#         'statusCode': 200,
#         'body': 'Hello from Lambda!'
#     }