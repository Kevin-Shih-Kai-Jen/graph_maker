""" 把檔案轉直

因為有部分檔案的格式是橫的（日期從左到右，而非上到下）
因此要透過把檔案轉直
才能用 graph_maker 生成圖片

例子：
/Users/coolguy/Desktop/經濟指標/數據/StateMortgagesPercent-30-89DaysLate-thru-2024-06.csv, StateMortgagesPercent-30-89Days
/Users/coolguy/Desktop/經濟指標/程式/UNRATE.csv, UNRATE 
"""

import pandas as pd
import os
from pathlib import Path


def input_name() -> tuple[str, list[str]]:
    inner_file_path = input("請輸入檔案位置：")
    input_sheet_name = input("請輸入 Sheet Name : ")

    return inner_file_path, input_sheet_name


def read_data(inner_data: str, sheet_name: str):

    _, filetype = os.path.splitext(inner_data)

    match filetype:
        case ".csv":
            data = pd.read_csv(inner_data)

        case ".xlsx" | ".xls":
            try:
                data = pd.read_csv(inner_data, sheet_name=sheet_name)

            except:
                data = pd.read_csv(inner_data)  ### 有些沒有 sheet_name，所以這樣才可

    return data


def output_file_name(original_path: str):
    """生成新檔案名稱

    因為如果沿用舊檔名可能會有問題
    """

    path = Path(original_path)
    new_file_name = path.parent / ("transposed_" + path.name)

    return new_file_name


# Load the uploaded CSV file
file_path, sheet_name = input_name()
data = read_data(file_path, sheet_name)

# Transpose the data to make it vertical (columns to rows)
transposed_data = data.transpose()

# Remove empty cells/rows/columns
transposed_data_cleaned = transposed_data.dropna(
    how="all"
)  # Remove rows/columns with all NaNs

# Save the cleaned and transposed data to a new CSV file
output_file_path = output_file_name(file_path)
final_data = transposed_data_cleaned.to_csv(output_file_path, index=True, header=True)

print("transposed_file_path = ", output_file_path)  # 這樣比較好查找轉完的檔案
