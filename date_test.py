from datetime import datetime

def convert_date(input_date):
    # Parse the input date
    date_obj = datetime.strptime(input_date, '%Y-%m-%d')
    
    # Format it to the desired output
    output_date = date_obj.strftime('%Y%m%d-%H%M%S')
    return output_date

# Example usage
input_date = '2024-07-24'
converted_date = convert_date(input_date)
print(converted_date)
