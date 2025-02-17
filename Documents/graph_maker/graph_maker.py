""""輸入參數即可生成圖片

例子：
/Users/coolguy/Desktop/經濟指標/數據/transposed_StateMortgagesPercent-30-89DaysLate-thru-2024-06.csv, transposed_StateMortgagesPercen,  Date, US, 6, 0
/Users/coolguy/Desktop/經濟指標/數據/MORTGAGE30US.xlsx, WeeklyEndingThursday, observation_date, MORTGAGE30US, 1, 0
/Users/coolguy/Desktop/經濟指標/數據/fredgraph.xlsx, Monthly, observation_date, HSN1F, 1, 0
/Users/coolguy/Desktop/經濟指標/數據/GDP.xls, FREDGraph, date, GDP, 1, 0
"""
import os
from typing import Optional
import itertools
from matplotlib import pyplot as plt
import pandas as pd
from copy import deepcopy
from dateutil.parser import parse  # 解析各種日期形式


have_read_path_data = []


def parameter_input() -> list[list[str]]:
    """參數樣子

    path_1, sheet_name, line_1, which_line_1

    """

    raw_data = []
    while 1:
        data = input(
            "請輸入以下格式 path_1, sheet_name（沒有的話請輸入0）, 日期名稱, 主要數據名稱, 第幾行, 跳過幾行: "
        )
        raw_data.append([data])

        stop_inserting = input("不想要繼續輸入請輸入stop: ")
        if stop_inserting == "stop":
            break

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
                path_data.append(
                    pd.read_csv(
                        imported_data[i][0],
                        skiprows=int_skip,
                        dtype=str,
                        parse_dates=True,
                    )
                )

            case ".xlsx" | ".xls":
                path_data.append(
                    pd.read_excel(
                        imported_data[i][0],
                        sheet_name=sheets[i],
                        skiprows=int_skip,
                        dtype=str,
                        parse_dates=True,
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
) -> tuple[list[list[pd.DataFrame]], list[list[pd.DataFrame]]]:
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
    which_line: list[str],
) -> tuple[list[pd.Series], list[pd.Series]]:
    """分析是否是日期和轉成 pd.DataFrame

    用 dateuil.parser 來解析這段資料是否為日期：
    是和不是的，個別儲存到不同的 List
    """

    date = []
    other_than_date_data = []

    for i in range(len(column_parameters)):
        actual_data = [
            pd_data[i]
            .iloc[
                int(which_line[i]) :,
                pd_data[i].columns.get_loc(column_parameters[i][0]),
            ]
            .reset_index(drop=True),
            pd_data[i]
            .iloc[
                int(which_line[i]) :,
                pd_data[i].columns.get_loc(column_parameters[i][1]),
            ]
            .reset_index(drop=True),
        ]

        value = determine_whether_the_timeline_is_reverse_or_not(actual_data)
        if value:
            actual_data = reverse_data(deepcopy(actual_data))

        elif value == "Wrong":
            continue

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
            inner_date = deepcopy(inner_date).apply(lambda x: str(x))
            intermediate_date = inner_date.apply(lambda x: parse(x))

        except Exception as e:
            print(
                f"\n\n這個日期格式是錯誤的, \n{e}\n\n",
                "該檔案的資料內容： ",
                inner_date,
            )
            return "Wrong"

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


def classify_other_data_big_or_small(
    inner_other_data: list[pd.Series], inner_date_data: list[pd.Series]
) -> tuple[list[tuple[pd.Series, pd.Series]]]:
    """區分成兩個 list

    因為不同量級的數據需要兩個 y 座標
    所以要分出量級
    以有無超出 10 倍為基準
    """
    inner_other_data = [item.apply(lambda x: float(x)) for item in inner_other_data]

    if len(inner_other_data) == 1:
        print("\n\n推薦建立單座標\n\n")
        return None, None

    if len(inner_other_data) == 2:
        print("\n\n推薦建立雙座標\n\n")
        return [(inner_other_data[0], inner_date_data[0])], [
            (
                inner_other_data[1],
                inner_date_data[1],
            )
        ]  # 形式是為了滿足另一個雙座標的格式，這樣程式比較統一

    mean_lst = [[i, inner_other_data[i].mean()] for i in range(len(inner_other_data))]
    inner_big_data = max(mean_lst, key=lambda x: x[1])[1]
    inner_small_data = min(mean_lst, key=lambda x: x[1])[1]

    if any(item[1] < inner_big_data / 10 for item in mean_lst) or any(
        item[1] > inner_small_data * 10 for item in mean_lst
    ):
        print("\n\n推薦建立單座標\n\n")

        for i in range(len(mean_lst)):
            print(f"\n第{i}個建議乘上倍數為\n：", inner_big_data / mean_lst[i][1])

        return None, None

    else:
        print("推薦建立雙座標")
        big_lst_index = [item[0] for item in mean_lst if item[1] >= inner_big_data / 10]
        small_lst_index = [
            item[0] for item in mean_lst if item[1] <= inner_small_data * 10
        ]

        new_inner_big_lst = [
            (inner_date_data[num], inner_other_data[num]) for num in big_lst_index
        ]
        new_inner_small_lst = [
            (inner_date_data[num], inner_other_data[num]) for num in small_lst_index
        ]
    return new_inner_big_lst, new_inner_small_lst


class DrawGraphBasics:
    "用 matplotlib 畫圖"

    def __init__(
        self,
        inner_date_data: list[pd.Series],
        inner_other_data: list[pd.Series],
    ):

        self.inner_other_data = inner_other_data

        """
        因為 inner_date_data 是 pd.Series
        所以要轉換為 datetime 才能讓系統讀懂
        因為有些功能能讀懂
        但有些會讀錯
        """
        self.inner_date_data = [
            pd.to_datetime(date, errors="coerce") for date in inner_date_data
        ]

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

    def input_lines_name(
        self, data_a: list[pd.DataFrame], data_b: Optional[list[pd.DataFrame]] = None
    ) -> list[str]:
        names = []

        """
        因為會不清楚資料是哪一筆
        所以需要透過印出前幾筆資料來浪使用者知道樣為哪條線取什麼名字
        """
        try:
            for item in data_a:
                print(item[0].head())

            if data_b is not None:
                for item in data_b:
                    print(item[0].head())

        except:
            pass

        for i in range(len(self.inner_date_data)):
            name = input(f"請輸入第{i}條線的名稱 :")
            names.append(name)

        return names

    def execute_necessary_functions(self):
        self.label_names()
        self.title()
        self.figtext()
        self.other_settings()

    def data_times_multiplier(self) -> pd.DataFrame:
        """要讓一些變化小的數據的變化能明顯顯現"""

        multiplied_data = []
        for item in deepcopy(self.inner_other_data):
            num = input("請輸入要給某數據乘上的倍數：")

            if num not in [None, "0", "1", ""]:  # 確保輸入值是正確的
                transitioning_data = item.apply(lambda data: float(data) * float(num))

            else:
                transitioning_data = item

            multiplied_data.append(pd.Series(transitioning_data))

        self.inner_other_data = multiplied_data


class DrawGraphOneYAxis(DrawGraphBasics):

    def __init__(self, inner_date_data, inner_other_data):
        super().__init__(inner_date_data, inner_other_data)

    def plot_data(self):
        """先 plot 要畫的圖形"""

        line_name = self.input_lines_name(self.inner_other_data)
        for i in range(len(self.inner_date_data)):  # 因為兩種 data 的數目肯定一樣
            plt.plot(
                self.inner_date_data[i],
                self.inner_other_data[i],
                label=line_name[i],
                linewidth=2,
            )


class DrawGraphTwoYAxis(DrawGraphBasics):

    def __init__(
        self, inner_date_data, inner_other_data, inner_big_lst, inner_small_lst
    ):
        super().__init__(inner_date_data, inner_other_data)

        self.inner_big_lst = inner_big_lst
        self.inner_small_lst = inner_small_lst
        self.color_lst = [
            "#1f77b4",
            "#ff7f0e",
            "#2ca02c",
            "#d62728",
            "#9467bd",
            "#8c564b",
            "#e377c2",
            "#7f7f7f",
            "#bcbd22",
            "#17becf",
        ]

    def plot_data(self):
        _, ax1 = plt.subplots()
        ax2 = ax1.twinx()
        color_iter = itertools.cycle(
            self.color_lst
        )  # 讓顏色自動循環，不然twinx()會讓線的顏色都一樣

        line_name = self.input_lines_name(self.inner_big_lst, self.inner_small_lst)

        for i in range(len(self.inner_big_lst)):
            ax1.plot(
                self.inner_big_lst[i][1],
                self.inner_big_lst[i][0],
                label=line_name[i],
                linewidth=2,
                color=next(color_iter),
            )

        for i in range(len(self.inner_small_lst)):
            ax2.plot(
                self.inner_small_lst[i][1],
                self.inner_small_lst[i][0],
                label=line_name[i],
                linewidth=2,
                color=next(color_iter),
            )


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

    ####### 把資料型態改正 #######
    main_date_data = [
        date.apply(lambda x: parse(x)) for date in deepcopy(main_date_data)
    ]
    main_other_than_date_data = [
        data.apply(lambda x: float(x)) for data in deepcopy(main_other_than_date_data)
    ]
    ############################

    big_lst, small_lst = classify_other_data_big_or_small(
        main_other_than_date_data, main_date_data
    )

    if big_lst is None:  # 如果值是None的話big_lst和small_lst一樣，只要檢查一個就好了
        draw_graph = DrawGraphOneYAxis(main_date_data, main_other_than_date_data)

    else:
        draw_graph = DrawGraphTwoYAxis(
            main_date_data, main_other_than_date_data, big_lst, small_lst
        )

    draw_graph.data_times_multiplier()
    draw_graph.plot_data()
    draw_graph.execute_necessary_functions()
