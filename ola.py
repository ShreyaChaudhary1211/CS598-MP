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
        self.grouped_mean = {}
        self.grouped_counts ={}

    def process_slice(self, df_slice: pd.DataFrame) -> None:
        grouped_df = df_slice.groupby(self.groupby_col)
        for group, group_df in grouped_df:
            grouped_sum = sum(group_df[self.mean_col].values)
            grouped_count = len(group_df[self.mean_col].values)

            if group not in self.grouped_mean:
                self.grouped_mean[group]= 0
                self.grouped_counts[group]= 0
            
            self.grouped_mean[group]+= grouped_sum
            self.grouped_counts[group]+=grouped_count
        
        grouped_keys = list(self.grouped_data.keys())
        grouped_mean= [(self.grouped_means[group] / 
                   self.grouped_counts[group]) if self.group_counts[group] > 0 else 0 for group in grouped_keys]
        self.update_widget(grouped_keys, grouped_mean)

class GroupBySumOla(OLA):
    def __init__(self, widget: go.FigureWidget, original_df_num_rows: int, groupby_col: str, sum_col: str):
        super().__init__(widget)
        self.original_df_num_rows = original_df_num_rows
        self.groupby_col = groupby_col
        self.sum_col = sum_col
        self.grouped_sums = {}
        self.count = 0
        

    def process_slice(self, df_slice: pd.DataFrame) -> None:
        grouped_df = df_slice.groupby(self.groupby_col)
        for group, group_df in grouped_df:
            grouped_sum = sum(group_df[self.sum_col].values)

            if group not in self.grouped_sums:
                self.grouped_sums[group] = 0
            self.grouped_sums[group] += grouped_sum

        self.count+= len(df_slice)
        scale = self.original_df_num_rows / self.count
        grouped_key = list(self.grouped_sums.keys())
        grouped_sum = [self.grouped_sums[group]*scale for group in grouped_key]
        self.update_widget(grouped_key, grouped_sum)

class GroupByCountOla(OLA):
    def __init__(self, widget: go.FigureWidget, original_df_num_rows: int, groupby_col: str, count_col: str):
        super().__init__(widget)
        self.original_df_num_rows = original_df_num_rows
        self.groupby_col = groupby_col
        self.count_col = count_col
        self.grouped_counts = {}
        self.count =0

    def process_slice(self, df_slice: pd.DataFrame) -> None:
        grouped_df = df_slice.groupby(self.groupby_col)
        for group, group_df in grouped_df:
            count_values = group_df[self.count_col].dropna().values
            grouped_count = len(count_values)
                
            if group not in self.grouped_counts:
                self.grouped_counts [group] = 0

            self.grouped_counts[group] += grouped_count

        self.count+= len(df_slice)   
        scale = self.original_df_num_rows / self.count
        grouped_key = list(self.grouped_counts.keys())
        grouped_counts = list(x*scale for x in self.grouped_counts.values())
        self.update_widget(grouped_key, grouped_counts)

class FilterDistinctOla(OLA):
    def __init__(self, widget: go.FigureWidget, filter_col: str, filter_value: Any, distinct_col: str):
        super().__init__(widget)
        self.filter_col = filter_col
        self.filter_value = filter_value
        self.distinct_col = distinct_col
        self.hll = HyperLogLog(p=2, seed=123456789)

    def process_slice(self, df_slice: pd.DataFrame) -> None:
        filtered_df = df_slice[df_slice[self.filter_col] == self.filter_value]
        distinct_values = filtered_df[self.distinct_col].astype(str).values
        for data in distinct_values: 
            self.hll.add(data)

        distinct_count = self.hll.cardinality()  # Corrected here
        self.update_widget([""], [distinct_count])

