import pandas as pd

# This is a one-time script, not part of your Streamlit app.
file_path = "C:\Users\ppriy\Dash\data\historical_data.csv" 
output_path = 'data/clean_historical_data.csv'

try:
    df = pd.read_csv(file_path, encoding='latin1', on_bad_lines='skip', low_memory=False)

    # Save the cleaned DataFrame to a new file
    df.to_csv(output_path, index=False)
    print("Successfully created a clean historical data file!")

except Exception as e:
    print(f"An error occurred during cleaning: {e}")