import pandas as pd
import datetime

file_name = 'airport_codes.xls.xlsx'


class UserInput():
    def __init__(self) -> None:
        pass

    def yes_or_not(self, message, prompt='Enter \'y\' or \'n\': ', allow_skip=False):
        print(message)
        if allow_skip:
            prompt = f'{prompt} (press enter to skip): '
        while True:
            try:
                choice = input(prompt).lower()
                if choice in ['n', 'no']:
                    return False
                elif allow_skip and choice == '' or choice in ['y', 'yes']:
                    return True
            except ValueError:
                print('Invalid date format, please try again.')

    def get_date_from_input(self, message, prompt='Enter a date in the format yyyy-mm-dd: ', allow_skip=False):
        print(message)
        if allow_skip:
            prompt = f'{prompt} (press enter to skip): '
        while True:
            try:
                date_str = input(prompt)
                if allow_skip and not date_str:
                    return None
                year, month, day = map(int, date_str.split('-'))
                date = datetime.date(year, month, day)
                return date
            except ValueError:
                print('Invalid date format, please try again.')

    def get_integer(self, message, prompt="Enter an integer: ", allow_skip=False):
        print(message)
        if allow_skip:
            prompt = f'{prompt} (press enter to skip): '
        while True:
            try:
                choice = input(prompt)
                if allow_skip and choice == '':
                    return None
                return int(choice)
            except ValueError:
                print('Invalid input, please enter an integer.')

    def select_airport(self, message):
        print(message)
        codes = []
        # Load the data from the Excel file
        df = pd.read_excel(file_name)
        while True:
            # Prompt the user for the string to search for and the country to filter by
            airport = input(
                'Enter a city to search for (press enter to skip): ').lower()
            country = input(
                'Enter a country to filter by (press enter to skip): ').lower()
            # Create a boolean mask to filter by country
            if country:
                mask = (df['Country'].str.lower() == country)
            else:
                mask = True
            # Look up the airports that start with the specified string and match the country (if specified)
            result_df = df.loc[mask & df['Airport'].str.lower(
            ).str.startswith(airport), 'Airport']
            # Check if the result is empty
            if result_df.empty:
                print(
                    f'No airports found that start with \'{airport}\' in \'{country}\'.')
                continue
            else:
                print(
                    f'The following airports start with \'{airport}\' in \'{country}\':')
                # Print airports
                for i, airport in enumerate(result_df):
                    print(f'{i} - {airport}')
                # Prompt the user to select an airport by index
                while True:
                    try:
                        indices = input(
                            'Enter a comma-separated list of indices of the airports you want to select: ')
                        indices = [int(index.strip())
                                   for index in indices.split(',')]
                        selected_airports = result_df.iloc[indices]
                        break
                    except (ValueError, IndexError):
                        print('Invalid input, please try again.')
                # Look up the airport codes in the DataFrame and print them

                for airport in selected_airports:
                    code = df.loc[df['Airport'] == airport, 'Code'].iloc[0]
                    codes.append(code)
                    print(f'The code for {airport} is {code}.')

                print(
                    f'The codes for the selected airports are: {", ".join(codes)}.')

                if not self.yes_or_not('\n[>] Enter \'y\' to go next step. Enter \'n\' to add more airports.'):
                    continue

                return codes
            
    # def select_days_number(self, message, prompt='Enter the total number of nights: '):
    #     print(message)
    #     while True:
    #         try:
    #             days = int(input(prompt))
    #             return days
    #         except ValueError:
    #             print('Invalid input, please enter an integer.')

    # def select_flex_days(self, message, prompt='Enter how many days of flexibiliy (press enter to skip): '):
    #     print(message)
    #     while True:
    #         try:
    #             choice = input(prompt)
    #             if not choice:
    #                 return None
    #             return int(choice)
    #         except ValueError:
    #             print('Invalid input, please enter an integer.')