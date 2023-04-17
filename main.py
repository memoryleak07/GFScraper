import csv
import os
import sys
import json
import datetime
from datetime import timedelta
from userinput import *
from xpathscraper import XpathScraper
from options import *
# from readresults import ReadCSVResult
# embed file to the exe
# pyinstaller --onefile --console --add-data='airport_codes.xls.xlsx;.' main.py


def print_welcome_message():
    print(f'''
                GoogleFlightsScraper 
                    version 1.1
                     fly high
                     
                Press CTRL+C to exit
          ''')


def update_settings_file(data: dict):
    try:
        with open(settings_file, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        raise (f'Error: {e}')


def read_settings_file():
    try:
        with open(settings_file, 'r') as f:
            data = json.load(f)
            for d in data:
                if data[d] in ("", " ", []):
                    print(
                        f"[Exception] No value in \'{d}\' of JSON settings file")
                    raise json.JSONDecodeError("", "", 0)
            return data
    except FileNotFoundError:
        with open(settings_file, 'w+', encoding='utf-8') as f:
            json.dump(json.loads(DEFATULT_SETTINGS), f, indent=4)
            f.seek(0)
            return json.load(f)
    except json.JSONDecodeError:
        print("[Exception] JSON settings file not readable.")
        if ui.yes_or_not("Do you want to restore default settings?"):
            os.remove(settings_file)
            return read_settings_file()
        exit_app(
            message=f'\n[Error] Script terminated. Please fix JSON settings file or restore to default settings.')
    except Exception as e:
        exit_app(message=f'[Error] {e}')


def exit_app(message=None, filename=None):
    if message:
        print(message)
    if filename and is_file_not_empty(filename):
        print(f'\n[-] Results file name: {filename}\n')
    print("\nExiting.")
    sys.exit(1)


def add_days(date: str | datetime.datetime | datetime.date, delta: int):
    '''return always a datetime.date obj'''
    if isinstance(date, (datetime.datetime, datetime.date)):
        return date + datetime.timedelta(days=delta)
    elif isinstance(date, str):
        return (datetime.datetime.strptime(date, '%Y-%m-%d') + datetime.timedelta(days=delta)).date()


def datetime_to_str(date: datetime.datetime | datetime.date):
    if isinstance(date, (datetime.datetime, datetime.date)):
        date_str = date.strftime('%Y-%m-%d')
        return date_str


def get_first_weekend_day(date: datetime.datetime | datetime.date):
    day_of_week = date.weekday()
    if day_of_week == 5:  # Saturday
        first_day_of_weekend = date
    elif day_of_week == 6:  # Sunday
        first_day_of_weekend = date - datetime.timedelta(days=1)
    else:
        days_until_saturday = 5 - day_of_week
        first_day_of_weekend = date + \
            datetime.timedelta(days=days_until_saturday)
    return first_day_of_weekend


def url_builder(from_: str, to_: str, outbound_: str, inbound_: str, tclass: str = None):
    base_url = f'https://www.google.com/travel/flights?q=Flights+to+{to_}+from+{from_}+on+{outbound_}+through+{inbound_}'
    if tclass in ['first', 'business', 'economy']:
        base_url = f'{base_url}%20{tclass}%20class'
    return base_url


def print_search_info(from_, to_, outbound_, flexdays_, weekend_, lastdate_, fastmode_, timeout_):
    print(f'''
          From {from_} to {to_}
          Departure: {outbound_}
          Days: {delta_}
          Flexibility: {flexdays_}
          Only weekends: {weekend_}
          Last date: {lastdate_}
          Fast mode: {fastmode_}
          Timeout: {timeout_}
          ''')


def print_end_info(start_time: datetime, end_time: datetime, count: int):
    time_elapsed = end_time - start_time
    print(f'''
          Start at: {start_time}
          End at: {end_time}
          Time elapsed: {time_elapsed}
          Total flights: {count}
          ''')


def is_file_not_empty(file_path):
    return os.path.isfile(file_path) and os.path.getsize(file_path) > 0


def add_list_to_csv_file(my_list: list, filename: str):
    try:
        with open(filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(my_list)
    except Exception as e:
        print(f'{e}')


def format_result(outbound_: str, inbound_: str, results: list):
    # Add outbound and inbound date to my list
    results = [outbound_, inbound_] + results
    # Replace newline characters with /
    results = [str(s).replace('\n', '/') for s in results]
    print(results)
    return results


def scrape_go(from_: str, to_: str, outbound_: str, inbound_: str, fast=False, tclass=None):
    results = []
    try:
        # Build the url
        url = url_builder(from_, to_, outbound_, inbound_, tclass)
        # Take outbound info for the first flight sorted and append to list
        results = results + scraper.get_elements_from_xpath_list(
            url, XPATH_LIST)
        # If results list is empty, try catch the cause message
        if not results:
            results = [scraper.scrape(None, XP_NOT_FOUND_MESSAGE)]
            not_found.append(1)
            return format_result(outbound_, inbound_, [f'{from_}-{to_}'] + results)
        else:
            # Clean too_far list
            not_found.clear()
        # Check if fast mode skip inbound flight information (duration, stops)
        if fast:
            return format_result(outbound_, inbound_, results)
        # Click on first flight sorted
        new_url = scraper.click_switch_page(None, XP_CLICK_FIRST_SORTED)
        # Take inbound info for the first flight sorted and append to list
        results = results + scraper.get_elements_from_xpath_list(
            new_url, XPATH_LIST)
    except Exception as e:
        results = results + ['Exception', f'{e.__class__}']
    # Return a unique list with outbound and inbound flights information or about non-exit exception
    return format_result(outbound_, inbound_, results)


def start_search(from_: list, to_: list, outbound_: datetime, inbound_: datetime, flexdays: int, lastdate_: datetime, fastmode_=False, weekend=False):
    start_time = datetime.datetime.now()
    delta = inbound_ - outbound_
    period = lastdate_ - outbound_
    i_weekend = 0
    count = 0
    try:
        # Iterate over from_ and to_ airport codes list
        for f in from_:
            for t in to_:
                for i in range(period.days):
                    # If found too many "date too far" break loop
                    if len(not_found) >= 5:
                        not_found.clear()
                        break
                    # Reset i_weekend counter
                    if i == 0:
                        i_weekend = 0
                    # Departure flight date is given by "outbound_" (date) + index (int) + (if True) index_weekend (int)
                    outbound_date = add_days(outbound_, i+i_weekend)
                    # If weekend increment index i_weekend +5
                    if weekend:
                        outbound_date = get_first_weekend_day(
                            date=outbound_date)
                        i_weekend += 5
                    # Convert out and in dates for scraper
                    outbound_dt = datetime_to_str(outbound_date)
                    inbound_dt = datetime_to_str(
                        add_days(outbound_date, delta.days))
                    # Check for last avaiable departure date, if True skip to next destination
                    if lastdate_ == outbound_date:
                        break
                    # Pass converted str to scraper and append to CSV file
                    add_list_to_csv_file(
                        scrape_go(f, t, outbound_dt, inbound_dt, fastmode_), filename)
                    # Count +1
                    count += 1
                    # If flexibiliy iterate over flexdays for the return flight date
                    if flexdays:
                        for j in range(flexdays):
                            inbound_date = add_days(outbound_date, j+1)
                            inbound_dt = datetime_to_str(
                                add_days(inbound_date, delta.days))
                            # Pass converted str to scraper and append to CSV file
                            add_list_to_csv_file(
                                scrape_go(f, t, outbound_dt, inbound_dt, fastmode_), filename)
                            # Count +1
                            count += 1
    except KeyboardInterrupt:
        pass
    finally:
        end_time = datetime.datetime.now()
        print_end_info(start_time, end_time, count)


if __name__ == "__main__":
    ui = UserInput()
    today = datetime.datetime.now().date()
    print_welcome_message()
    filename = None
    not_found = []
    from_ = []
    to_ = []
    try:
        while True:
            if ui.yes_or_not("\n[>] Do you want to read parameters from settings.json file?"):
                # Read settings file parameters
                data = read_settings_file()
                from_ = data['from']
                to_ = data['to']
                outbound_ = add_days(data['outbound'], 0)
                delta_ = data['delta']
                inbound_ = add_days(outbound_, delta_)
                flexdays_ = data['flexdays']
                weekend_ = data['weekend']
                lastdate_ = add_days(data['lastdate'], 0)
                fastmode_ = data['fastmode']
                timeout_ = data['timeout']
                # Check datetime inputs
                if outbound_ < today or lastdate_ < today:
                    raise ValueError("\n[Error] Past dates are not allowed in settings.json file.")
            else:
                # Prompt user to enter data for search
                from_ = ui.select_airport(
                    "\n[>] Select a list of departure destination cities.")
                to_ = ui.select_airport(
                    "\n[>] Select a list of arrival destination cities")
                outbound_ = ui.get_date_from_input(
                    "\n[>] Select the first available date for departure flight.")
                delta_ = ui.get_integer(
                    "\n[>] Select how many days you want to stay.", allow_zero=False)
                inbound_ = add_days(outbound_, delta_)
                flexdays_ = ui.get_integer(
                    "\n[>] Select return departure date flexibility.", allow_skip=True, allow_zero=False)
                weekend_ = ui.yes_or_not(
                    "\n[>] Do you want to depart only on weekends?", allow_skip=True)
                lastdate_ = ui.get_date_from_input(
                    "\n[>] Select the last available date for departure flight.", allow_skip=True)
                fastmode_ = ui.yes_or_not(
                    "\n[>] Do you want to execute script in fast mode?", allow_skip=True)
                timeout_ = ui.get_integer(
                    "\n[>] Default timeout between each search is 10 seconds.", allow_skip=True, allow_zero=False)
                # If no limit is given, set lastdate to +1 year.
                if not lastdate_:
                    lastdate_ = add_days(outbound_, 365)
                if not timeout_:
                    timeout_ = 10
                # Update settings file
                update_settings_file({
                    'from': from_,
                    'to': to_,
                    'outbound': datetime_to_str(outbound_),
                    'delta': delta_,
                    'flexdays': flexdays_,
                    'weekend': weekend_,
                    'lastdate': datetime_to_str(lastdate_),
                    'fastmode': fastmode_,
                    'timeout': timeout_
                })
            # Print info about search configuration
            print_search_info(from_, to_, outbound_, flexdays_, weekend_,
                              lastdate_, fastmode_, timeout_)
            # Prompt for start search, else go to begin
            if ui.yes_or_not("\n[>] Do you want to start search?"):
                prefix = '-'.join(from_) + 'to' + '-'.join(to_)
                filename = f"{results_path}{prefix}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
                # Init the xpath scraper driver
                scraper = XpathScraper(timeout=timeout_)
                # Start search
                start_search(from_, to_, outbound_, inbound_,
                             flexdays_, lastdate_, fastmode_, weekend_)
                # Quit the driver
                scraper.quit()
            else:
                continue
    except KeyboardInterrupt:
        exit_app('\n\nScript terminated by user.', filename)
    except Exception as e:
        exit_app(str(e), filename)