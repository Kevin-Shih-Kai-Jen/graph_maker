""""輸入參數即可生成圖片

例子：
/Users/coolguy/Desktop/經濟指標/數據/transposed_StateMortgagesPercent-30-89DaysLate-thru-2024-06.csv, transposed_StateMortgagesPercen,  Date, US, 6, 0
/Users/coolguy/Desktop/經濟指標/數據/
"""

from matplotlib import pyplot as plt
from matplotlib import dates as mdate

import pandas as pd
import os
from typing import Tuple
from copy import deepcopy
from dateutil.parser import parse  # 解析各種日期形式


have_read_path_data = []


def parameter_input() -> list[list[str]]:
    """參數樣子

    path_1, sheet_name, line_1, which_line_1

    """

    """raw_data = []
    while 1:
        data = input(
            "請輸入以下格式 path_1, sheet_name（沒有的話請輸入0）, 日期名稱, 主要數據名稱, 第幾行, 跳過幾行: "
        )
        raw_data.append([data])

        stop_inserting = input("不想要繼續輸入請輸入stop: ")
        if stop_inserting == "stop":
            break"""

    raw_data = [
        [
            "/Users/coolguy/Desktop/經濟指標/數據/transposed_StateMortgagesPercent-30-89DaysLate-thru-2024-06.csv, transposed_StateMortgagesPercen,  FIPSCode, -----, 0, 4"
        ]
    ]
    return raw_data


def clear_white_space(raw_data: list[list[str]]) -> list[list[str]]:
    new_data = []

    for item in raw_data:
        new_data.append([item[0].replace(" ", "")])

    return new_data


def string_to_array(data: list[list[str]]) -> list[list[str]]:
    """
    因為 input 是 string，要將 string 轉成可用資料
    """

    array_data = []

    for item in data:
        temp = []

        for char in item[0]:
            if char != ",":
                temp.append(char)
            else:
                array_data.append("".join(temp))  # 遇到逗號時將 temp 加入 array_data
                temp.clear()

        # 處理最後一段無逗號的字串
        if len(temp) != 0:
            array_data.append("".join(temp))

    array_data = combine_six_data(array_data)

    return array_data


def combine_six_data(inner_data: list[str]) -> list[list[str]]:
    combined_data = []

    for i in range(len(inner_data) // 6):
        combined_data.append(
            [
                inner_data[i * 6],
                inner_data[i * 6 + 1],
                inner_data[i * 6 + 2],
                inner_data[i * 6 + 3],
                inner_data[i * 6 + 4],
                inner_data[i * 6 + 5],
            ]
        )

    return combined_data


def read_data(imported_data: list[list[str]]) -> list[pd.DataFrame]:

    def find_file_type(data):
        """分別檔案類別

        因為檔案類別會影響pd.read
        """
        _, filetype = os.path.splitext(data)

        return filetype

    path_data = []
    sheets = sheet_name(imported_data)
    for i in range(len(imported_data)):
        file_type = find_file_type(imported_data[i][0])
        str_skip = (lambda x: 0 if x is None else x)(imported_data[i][5])
        int_skip = int(str_skip)

        match file_type:
            case ".csv":
                path_data.append(pd.read_csv(imported_data[i][0], skiprows=int_skip))

            case ".xlsx" | ".xls":
                path_data.append(
                    pd.read_excel(
                        imported_data[i][0], sheet_name=sheets[i], skiprows=int_skip
                    )
                )

    return path_data


def sheet_name(original_data: list[list[str]]) -> list[str]:
    sheets = []

    for item in original_data:
        sheets.append(item[1])

    for stuff in sheets:
        if stuff == "0":
            stuff = int("0")

    return sheets


# bulid date list
def find_data(
    pd_data: list[pd.DataFrame], original_data_list: list[list[str]]
) -> Tuple[list[list[pd.DataFrame]], list[list[pd.DataFrame]]]:
    """找出想要的 data 的範圍

    先從 original data 找出直行、橫列的值，
    然後再分析範圍，找出要的值

    column_parameters: [[日期, 數據], ......]
    """
    column_parameters = []
    which_line = []

    ############################ 找出直行、橫列的值 ############################
    for item in original_data_list:
        column_parameters.append([item[2], item[3]])
        which_line.append(item[4])

    date_data, other_than_date_data = parse_data(pd_data, column_parameters, which_line)

    return date_data, other_than_date_data


def parse_data(
    pd_data: list[pd.DataFrame],
    column_parameters: list[list[str]],
    which_line: list[pd.DataFrame],
) -> Tuple[list[pd.DataFrame], list[pd.DataFrame]]:
    """分析是否是日期和轉成 pd.DataFrame

    用 dateuil.parser 來解析這段資料是否為日期：
    是和不是的，個別儲存到不同的 List
    """

    date = []
    other_than_date_data = []

    for i in range(len(column_parameters)):
        line_length = len(pd_data[i][column_parameters[i][0]])
        actual_data = [
            pd_data[i]
            .loc[which_line[i] : line_length, column_parameters[i][0]]
            .reset_index(drop=True),
            pd_data[i]
            .loc[which_line[i] : line_length, column_parameters[i][1]]
            .reset_index(drop=True),
        ]

        if determine_whether_the_timeline_is_reverse_or_not(actual_data):
            actual_data = reverse_data(deepcopy(actual_data))

        date.append(actual_data[0])
        other_than_date_data.append(actual_data[1])

    return date, other_than_date_data


def determine_whether_the_timeline_is_reverse_or_not(
    inner_actual_data: list[pd.DataFrame],
) -> bool:
    inner_date = inner_actual_data[0]
    middle_data = len(inner_date) // 2

    try:
        intermediate_date = pd.to_datetime(
            inner_actual_data, format="None", errors="raise"
        )

    except Exception:
        try:
            intermediate_date = inner_date.apply(lambda x: parse(x))

        except Exception as e:
            print(f"這個日期格式是錯誤的, {e}")

    first_line = intermediate_date[middle_data]
    second_line = intermediate_date[middle_data + 1]

    if first_line > second_line:
        return True

    else:
        return False


def reverse_data(inner_selected_data: list[pd.DataFrame]) -> list[pd.DataFrame]:

    reversed_date = []
    reversed_number = []
    date_dataframe = inner_selected_data[0]
    number_dataframe = inner_selected_data[1]

    for date in date_dataframe[::-1]:
        reversed_date.append(date)

    for number in number_dataframe[::-1]:
        reversed_number.append(number)

    final_date = pd.Series(reversed_date)
    final_number = pd.Series(reversed_number)

    return [final_date, final_number]


class DrawGraph:
    "用 matplotlib 畫圖"

    def __init__(
        self,
        inner_date_data: list[pd.Series],
        inner_other_data: list[pd.DataFrame],
    ):

        self.inner_other_data = inner_other_data
        
        """
        因為 inner_date_data 是 pd.Series
        所以要轉換為 datetime 才能讓系統讀懂
        因為有些功能能讀懂
        但有些會讀錯
        """
        self.inner_date_data = [pd.to_datetime(date, errors="coerce") for date in inner_date_data]

    def plot_data(self):
        """先 plot 要畫的圖形"""

        line_name = self.input_lines_name()

        for i in range(len(self.inner_date_data)):  # 因為兩種 data 的數目肯定一樣
            plt.plot(
                self.inner_date_data[i],
                self.inner_other_data[i],
                label=line_name[i],
                linewidth=2,
            )

    def label_names(self):
        x_label = input("請輸入您的 X 座標軸的名字 :")
        y_label = input("請輸入您的 Y 座標軸的名字 :")

        plt.xlabel(x_label)
        plt.ylabel(y_label)

    def title(self):
        title_name = input("請輸入本表格的名稱 :")
        plt.title(title_name)

    def figtext(self):
        text = input("請輸入要額外說明的字詞 :")
        plt.figtext(0.3, 0.01, text, fontsize=5, color="black")

    def other_settings(self):
        plt.style.use("seaborn-v0_8-darkgrid")
        plt.legend()
        plt.grid(True)

        plt.show()

    def input_lines_name(self) -> list[str]:
        names = []

        for i in range(len(self.inner_date_data)):
            name = input(f"請輸入第{i}條線的名稱 :")
            names.append(name)

        return names

    
    def set_date_gaps():
        ######### 改變黑壓壓的日期 #########
        axis = plt.gca()# 獲得當前的x,y軸
        axis.xaxis.set_major_locator(mdate.YearLocator(interval=1))# 日期為每3個月顯示一次
        axis.xaxis.set_major_formatter(mdate.DateFormatter("%Y-%m"))
        
        
    def execute_necessary_functions(self):
        self.plot_data()
        self.label_names()
        self.title()
        self.figtext()
        self.set_date_gaps
        self.other_settings()

    def data_times_multiplier(self) -> pd.DataFrame:
        "要讓一些變化小的數據的變化能明顯顯現"

        pass


###############################################################
############################ 主程式 ############################
###############################################################

if __name__ == "__main__":
    raw_data = parameter_input()
    raw_data_list = clear_white_space(raw_data)
    array_data = string_to_array(raw_data_list)
    have_read_path_data = read_data(array_data)
    main_date_data, main_other_than_date_data = find_data(
        have_read_path_data, array_data
    )

    draw_graph = DrawGraph(main_date_data, main_other_than_date_data)
    draw_graph.execute_necessary_functions()
