import pandas as pd
import plotly.graph_objects as go
from HLL import HyperLogLog
from typing import List, Any

class OLA:
    def __init__(self, widget: go.FigureWidget):
        self.widget = widget

    def process_slice(df_slice: pd.DataFrame) -> None:
        pass

    def update_widget(self, groups_list: List[Any], values_list: List[Any]) -> None:
        self.widget.data[0]['x'] = groups_list
        self.widget.data[0]['y'] = values_list

class AvgOla(OLA):
    def __init__(self, widget: go.FigureWidget, mean_col: str):
        super().__init__(widget)
        self.mean_col = mean_col
        self.sum = 0
        self.count = 0

    def process_slice(self, df_slice: pd.DataFrame) -> None:
        self.sum += df_slice.sum()[self.mean_col]
        self.count += df_slice.count()[self.mean_col]
        self.update_widget([""], [self.sum / self.count])

class FilterAvgOla(OLA):
    def __init__(self, widget: go.FigureWidget, filter_col: str, filter_value: Any, mean_col: str):
        super().__init__(widget)
        self.filter_col = filter_col
        self.filter_value = filter_value
        self.mean_col = mean_col
        self.filtered_sum = 0
        self.filtered_count = 0

    def process_slice(self, df_slice: pd.DataFrame) -> None:
        filtered_df = df_slice[df_slice[self.filter_col] == self.filter_value]
        self.filtered_sum += filtered_df.sum()[self.mean_col]
        self.filtered_count += filtered_df.count()[self.mean_col]
        self.update_widget([""], [self.filtered_sum / self.filtered_count])

class GroupByAvgOla(OLA):
    def __init__(self, widget: go.FigureWidget, groupby_col: str, mean_col: str):
        super().__init__(widget)
        self.groupby_col = groupby_col
        self.mean_col = mean_col
        self.grouped_data = {}

    def process_slice(self, df_slice: pd.DataFrame) -> None:
        grouped_df = df_slice.groupby(self.groupby_col)
        for group, group_df in grouped_df:
            if group in self.grouped_data:
                self.grouped_data[group][0] += group_df.sum()[self.mean_col]
                self.grouped_data[group][1] += group_df.count()[self.mean_col]
            else:
                self.grouped_data[group] = [group_df.sum()[self.mean_col], group_df.count()[self.mean_col]]
        
        groups = list(self.grouped_data.keys())
        values = [(self.grouped_data[group][0] / self.grouped_data[group][1]) for group in groups]
        self.update_widget(groups, values)

class GroupBySumOla(OLA):
    def __init__(self, widget: go.FigureWidget, original_df_num_rows: int, groupby_col: str, sum_col: str):
        super().__init__(widget)
        self.original_df_num_rows = original_df_num_rows
        self.groupby_col = groupby_col
        self.sum_col = sum_col
        self.grouped_sums = {}

    def process_slice(self, df_slice: pd.DataFrame) -> None:
        grouped_df = df_slice.groupby(self.groupby_col)
        for group, group_df in grouped_df:
            if group in self.grouped_sums:
                self.grouped_sums[group] += group_df.sum()[self.sum_col]
            else:
                self.grouped_sums[group] = group_df.sum()[self.sum_col]
        
        groups = list(self.grouped_sums.keys())
        values = [self.grouped_sums[group] for group in groups]
        self.update_widget(groups, values)

class GroupByCountOla(OLA):
    def __init__(self, widget: go.FigureWidget, original_df_num_rows: int, groupby_col: str, count_col: str):
        super().__init__(widget)
        self.original_df_num_rows = original_df_num_rows
        self.groupby_col = groupby_col
        self.count_col = count_col
        self.grouped_counts = {}

    def process_slice(self, df_slice: pd.DataFrame) -> None:
        grouped_df = df_slice.groupby(self.groupby_col)
        for group, group_df in grouped_df:
            if group in self.grouped_counts:
                self.grouped_counts[group] += group_df[self.count_col].count()
            else:
                self.grouped_counts[group] = group_df[self.count_col].count()
        
        groups = list(self.grouped_counts.keys())
        values = list(self.grouped_counts.values())
        self.update_widget(groups, values)

class FilterDistinctOla(OLA):
    def __init__(self, widget: go.FigureWidget, filter_col: str, filter_value: Any, distinct_col: str):
        super().__init__(widget)
        self.filter_col = filter_col
        self.filter_value = filter_value
        self.distinct_col = distinct_col
        self.hll = HyperLogLog(p=2, seed=123456789)

    def process_slice(self, df_slice: pd.DataFrame) -> None:
        filtered_df = df_slice[df_slice[self.filter_col] == self.filter_value]
        for index, row in filtered_df.iterrows():
            self.hll.add(str(row[self.distinct_col]))

        distinct_count = self.hll.cardinality()  # Corrected here
        self.update_widget([""], [distinct_count])

