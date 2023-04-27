import pandas as pd
import os
# from options import XPATH_KEYS
KEYS = ['outbound', 'inbound', 'codes', 'price', 'company', 'info', 'duration', 'stops']

class ReadResult():
    def __init__(self, filename) -> None:
        self.filename = filename
        self.df = pd.read_csv(filename, header=None)      
        # Check if number of columns in the file is greater than the length of the header KEYS
        if len(self.df.columns) > len(KEYS):
            new_header = KEYS + [f"return_{col}" for col in KEYS[2:]]
            self.df.columns = new_header
        else:
            self.df.columns = KEYS[:len(self.df.columns)]
        # print(self.df)
        # Drop rows with NaN values in the 'price' column
        # self.df = self.df.dropna(subset=['price'])    
        
    def sort_by_price(self, col_name='price'):
        def extract_price(s):
            if isinstance(s, str):
                return int(float((s.split(' ')[0]).replace('.','')))
            elif pd.isna(s):
                return 0
            else:
                return int(s)
        self.df[col_name] = self.df[col_name].fillna('0 €')
        self.df[col_name] = self.df[col_name].apply(extract_price)
        sorted_df = self.df[self.df[col_name] != 0].sort_values(col_name)
        print(f'\nSorted by price:\n{sorted_df.head()}')
        return sorted_df
        
    def sort_by_duration(self, col_name='duration'):
        pass
                
                
# res_path = os.getcwd() + '\\results'
# filename = 'NAPtoVIE_20230413141058.csv'
# file_path = os.path.join(res_path, filename)
# rr = ReadResult(file_path)
# sorted_df = rr.sort_by_price()
# # # Salva il dataframe ordinato in un file Excel
# sorted_dur = rr.sort_by_duration()
# sorted_df.to_excel('sorted_by_price2.xlsx', index=False)




        
