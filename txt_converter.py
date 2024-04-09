import pandas as pd
import numpy as np

def csv_to_txt(csv_file):
    df = pd.read_csv(csv_file)
    
    # Drop rows with NaN values in any of the columns
    df.dropna(subset=['date', 'title', 'link', 'content'], inplace=True)

    if df.empty:
        return "No valid data to convert to text."

    txt_content = ""
    for index, row in df.iterrows():
        txt_content += f"Title: {row['title']}\n"
        txt_content += f"Date: {row['date']}\n"
        txt_content += f"Link: {row['link']}\n"
        txt_content += f"Content: {row['content']}\n\n"
    return txt_content
