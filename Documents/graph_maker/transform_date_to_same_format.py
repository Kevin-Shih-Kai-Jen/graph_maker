"""將日期轉成統一 datetime 格式

    因為日期的格式太多變
    且有些是 parse, datetime 無法辨認的格式
    因此需要自己建一個模組來轉變
    
    其他目標
    將不要的資料行數刪除：
    將日期的名稱通通改成 Date、順便把資料的名稱改成 Desired_data
    """
    
    
import pandas as pd
import os
from pathlib import Path

def input_parameter() -> tuple[str, ]:
    inner_file_path = input("請輸入檔案位置：")
    input_sheet_name = input("請輸入 Sheet Name : ")
    inner_skiprow = input("請輸入您想跳過幾行：")

    return inner_file_path, input_sheet_name, inner_skiprow


def read_data(inner_data: str, inner_sheet_name: str, inner_skiprow: str):

    _, filetype = os.path.splitext(inner_data)

    match filetype:
        case ".csv":
            data = pd.read_csv(inner_data, skiprows=int(inner_skiprow))

        case ".xlsx" | ".xls":
            try:
                data = pd.read_csv(inner_data, sheet_name=inner_sheet_name, skiprows=int(inner_skiprow))

            except:
                data = pd.read_csv(inner_data, skiprows=int(inner_skiprow))  ### 有些沒有 sheet_name，所以這樣才可

    return data


def set_title_name():
    """幫日期設成想要的格式"""


file_path, sheet_name, skiprow = input_parameter()
data = read_data(file_path, sheet_name, skiprow)

