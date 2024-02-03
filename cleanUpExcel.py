#cleaning the files created from extractor.py!

from cities import get_cities as extracted_cities
import pandas as pd
import os
import shutil

cities = extracted_cities()
cities = [city.replace('%20', '') for city in cities]
cities = [city.replace(' ', '') for city in cities]

for city in cities:
    try:
        file_path = f'RawData/{city}Output.xlsx'
        new_file_path = f'Outputs/{city}Cleaned.xlsx' 
        if os.path.exists(file_path):
            os.makedirs('Outputs', exist_ok=True)
            if os.path.exists(new_file_path):
                df = pd.read_excel(new_file_path)
                columns_to_drop = ['Registration Number', 'Commonly Used First Name', 'Commonly Used Last Name', 'Province', 'Country']
            
                df = df.drop(columns=columns_to_drop, errors='ignore')
            
                column_widths = {col: max(len(str(value)) for value in df[col]) for col in df.columns}
                
                with pd.ExcelWriter(new_file_path, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False)
                
                    workbook = writer.book
                    worksheet = writer.sheets['Sheet1']  # Assuming your sheet name is 'Sheet1'
                    
                    for col, width in column_widths.items():
                        worksheet.set_column(df.columns.get_loc(col), df.columns.get_loc(col), width)
                    
                print(f"Specified columns deleted and column widths adjusted in {new_file_path}")
            else:
                shutil.copy(file_path, new_file_path)
                print(f"File duplicated to {new_file_path}")
    except Exception as e:
        print(f"{city} file not found!!! Error: {e}")

