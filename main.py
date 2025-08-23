#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Pure PyQt5 + QtCharts implementation of RankingAnalyzer.
Exam-time labels on the x-axis fixed (use QCategoryAxis and avoid createDefaultAxes()).
Requires: PyQt5, PyQtChart (QtCharts), pandas, numpy
pip install PyQt5 PyQtChart pandas numpy
"""

import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QFileDialog, QMessageBox, QTextEdit, QLabel, QSplitter
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QPointF

# QtCharts imports (ensure PyQtChart / PyQt5.QtChart is installed)
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis, QCategoryAxis

import pandas as pd
import numpy as np
from datetime import datetime

# ---------------- UI / Behavior Constants ----------------
DEFAULT_FONT = "Microsoft YaHei"
BASE_FONT_SIZES = {
    'btn': 9,
    'title': 11,
    'notes': 10,
    'notes_btn': 9,
    'legend': 9,
    'ticks': 9,
    'annot': 9
}


class ChartWidget(QChartView):
    """Wrapper around QChartView to simplify plotting series with category x-axis."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.chart = QChart()
        self.setChart(self.chart)
        self.chart.setBackgroundBrush(Qt.white)
        self.chart.legend().setVisible(True)
        self.chart.setAnimationOptions(QChart.AllAnimations)
        self.series_list = []

    def clear(self):
        for s in list(self.series_list):
            try:
                self.chart.removeSeries(s)
            except Exception:
                pass
        self.series_list.clear()
        # remove axes
        for ax in list(self.chart.axes()):
            try:
                self.chart.removeAxis(ax)
            except Exception:
                pass

    def plot_lines(self, x_labels, series_dict, title=""):
        """
        x_labels: list[str] labels for x positions [0..N-1]
        series_dict: { "label": [y0, y1, ...], ...}
        """
        self.clear()
        n = len(x_labels)
        self.chart.setTitle(title)

        # Build X axis as category axis (map index -> label)
        axis_x = QCategoryAxis()
        # Place labels at their value positions
        axis_x.setLabelsPosition(QCategoryAxis.AxisLabelsPositionOnValue)
        # Add labels for each index
        for i, lab in enumerate(x_labels):
            # Append label at the numeric position i
            axis_x.append(lab, float(i))
        # Set the numeric range to cover all indices
        if n > 0:
            axis_x.setRange(0.0, float(max(0, n - 1)))
        axis_x.setTitleText("考试")

        # Build Y axis (value)
        axis_y = QValueAxis()
        axis_y.setLabelFormat("%.0f")
        axis_y.setTitleText("分数 / 值")

        # Add series
        y_min, y_max = None, None
        for name, ys in series_dict.items():
            series = QLineSeries()
            series.setName(str(name))
            # add points (x=index, y=value)
            for i, v in enumerate(ys):
                # If value is NaN or None, skip point
                if v is None or (isinstance(v, float) and np.isnan(v)):
                    continue
                try:
                    series.append(QPointF(float(i), float(v)))
                except Exception:
                    # skip bad values
                    continue
                if y_min is None or v < y_min:
                    y_min = v
                if y_max is None or v > y_max:
                    y_max = v
            self.chart.addSeries(series)
            self.series_list.append(series)

        # Attach axes (must attach after adding series)
        self.chart.addAxis(axis_x, Qt.AlignBottom)
        self.chart.addAxis(axis_y, Qt.AlignLeft)
        for s in self.series_list:
            s.attachAxis(axis_x)
            s.attachAxis(axis_y)

        # Set Y axis range with small padding
        if y_min is None:
            y_min, y_max = 0, 10
        span = max(1.0, (y_max - y_min) * 0.1) if (y_max is not None and y_min is not None) else 1.0
        axis_y.setRange(y_min - span, y_max + span)

        # Legend font
        font = self.chart.legend().font()
        font.setPointSize(BASE_FONT_SIZES['legend'])
        self.chart.legend().setFont(font)

        # IMPORTANT: DO NOT call createDefaultAxes() here — it will override our custom axes
        # If you want label rotation and your Qt version supports it, you can call:
        # axis_x.setLabelsAngle(45)  # Qt >= 5.11 may support this

        self.update()


class ScoreVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RankingAnalyzer ")
        self.setMinimumSize(1000, 700)

        # Screen DPI (best-effort)
        screen = QApplication.primaryScreen()
        try:
            self.screen_dpi = screen.logicalDotsPerInch()
        except Exception:
            self.screen_dpi = 96.0
        print("Screen DPI:", self.screen_dpi)

        self.df = pd.DataFrame(columns=["exam", "subject", "score", "total_rank"])
        self.notes_editing = False

        central = QWidget()
        self.setCentralWidget(central)

        # Top buttons
        top_buttons = QHBoxLayout()
        self.btn_import = QPushButton("导入 CSV")
        self.btn_export = QPushButton("导出 CSV")
        self.btn_subjects = QPushButton("科目趋势")
        self.btn_total = QPushButton("总分趋势")
        self.btn_rank = QPushButton("排名趋势")

        for b in (self.btn_import, self.btn_export, self.btn_subjects, self.btn_total, self.btn_rank):
            b.setFont(QFont(DEFAULT_FONT, BASE_FONT_SIZES['btn']))

        self.btn_import.clicked.connect(self.load_csv)
        self.btn_export.clicked.connect(self.save_csv)
        self.btn_subjects.clicked.connect(self.plot_subjects)
        self.btn_total.clicked.connect(self.plot_total)
        self.btn_rank.clicked.connect(self.plot_rank)

        top_buttons.addWidget(self.btn_import)
        top_buttons.addWidget(self.btn_export)
        top_buttons.addWidget(self.btn_subjects)
        top_buttons.addWidget(self.btn_total)
        top_buttons.addWidget(self.btn_rank)
        top_buttons.addStretch()

        # Chart (left)
        self.chartview = ChartWidget()
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(self.chartview)

        # Notes (right)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        self.notes_label = QLabel("备注")
        self.notes_label.setFont(QFont(DEFAULT_FONT, BASE_FONT_SIZES['title']))
        right_layout.addWidget(self.notes_label)

        self.notes_text = QTextEdit()
        self.notes_text.setReadOnly(True)
        self.notes_text.setFont(QFont(DEFAULT_FONT, BASE_FONT_SIZES['notes']))
        right_layout.addWidget(self.notes_text)

        notes_buttons = QHBoxLayout()
        self.btn_edit = QPushButton("编辑备注")
        self.btn_save = QPushButton("保存备注")
        self.btn_edit.setFont(QFont(DEFAULT_FONT, BASE_FONT_SIZES['notes_btn']))
        self.btn_save.setFont(QFont(DEFAULT_FONT, BASE_FONT_SIZES['notes_btn']))
        self.btn_edit.clicked.connect(self.edit_notes)
        self.btn_save.clicked.connect(self.save_notes)
        notes_buttons.addWidget(self.btn_edit)
        notes_buttons.addWidget(self.btn_save)
        right_layout.addLayout(notes_buttons)

        # Splitter
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(left_widget)
        self.splitter.addWidget(right_widget)
        self.splitter.setStretchFactor(0, 6)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes([800, 300])
        self.splitter.splitterMoved.connect(lambda pos, idx: self.chartview.update())

        # Outer layout
        outer = QVBoxLayout(central)
        outer.addLayout(top_buttons)
        outer.addWidget(self.splitter)

        # Load notes and optionally auto-load data.csv
        self.load_notes()
        QtCore.QTimer.singleShot(50, self.auto_load_csv)

    def auto_load_csv(self):
        default_path = "data.csv"
        if os.path.exists(default_path):
            try:
                self.df = pd.read_csv(default_path, parse_dates=["exam"])
            except Exception:
                try:
                    self.df = pd.read_csv(default_path)
                except Exception:
                    QMessageBox.warning(self, "提示", "自动加载 data.csv 时出错。")
                    return
            # plot subjects by default
            self.plot_subjects()

    def load_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "打开 CSV", filter="CSV 文件 (*.csv);;All Files (*)")
        if not path:
            return
        try:
            self.df = pd.read_csv(path, parse_dates=["exam"])
        except Exception:
            # 如果 parse_dates 失败，再读一次不解析
            self.df = pd.read_csv(path)
        QMessageBox.information(self, "提示", f"导入成功：共 {len(self.df)} 条记录")
        self.plot_subjects()

    def save_csv(self):
        if self.df is None or self.df.empty:
            QMessageBox.information(self, "提示", "当前没有数据可导出。")
            return
        path, _ = QFileDialog.getSaveFileName(self, "保存 CSV", filter="CSV 文件 (*.csv);;All Files (*)")
        if not path:
            return
        if not path.lower().endswith(".csv"):
            path += ".csv"
        try:
            self.df.to_csv(path, index=False, date_format="%Y-%m-%d")
            QMessageBox.information(self, "提示", "导出成功")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败：{e}")

    def prepare_data(self):
        """返回 (score_pivot, total_series, rank_series, x_labels)
        score_pivot: DataFrame indexed by exam (sorted) with subjects as columns
        total_series: Series of total per exam (index aligned)
        rank_series: Series of rank per exam (if available)
        x_labels: list of strings for x-axis (aligned with pivot index)
        """
        if self.df is None or self.df.empty:
            return pd.DataFrame(), pd.Series(dtype=float), pd.Series(dtype=float), []

        df = self.df.copy()
        # try to parse exam column to datetime if not already
        if 'exam' in df.columns and not np.issubdtype(df['exam'].dtype, np.datetime64):
            try:
                df['exam'] = pd.to_datetime(df['exam'])
            except Exception:
                # leave as-is (string)
                pass

        # pivot: rows = exam, cols = subject
        try:
            score_pivot = df.pivot_table(index='exam', columns='subject', values='score', aggfunc='first').sort_index()
        except Exception:
            score_pivot = pd.DataFrame()

        # total per exam
        total = None
        if not score_pivot.empty:
            try:
                total = score_pivot.sum(axis=1)
            except Exception:
                total = pd.Series(dtype=float)

        # rank series (from original df)
        rank = pd.Series(dtype=float)
        if 'total_rank' in df.columns:
            try:
                rank = df.groupby('exam')['total_rank'].first().sort_index()
            except Exception:
                rank = pd.Series(dtype=float)

        # x labels: format exam dates to 'YYYY-MM' or string if not datetime
        x_labels = []
        if not score_pivot.empty:
            for idx in score_pivot.index:
                if isinstance(idx, (pd.Timestamp, datetime)):
                    x_labels.append(idx.strftime("%Y-%m-%d"))  # show full date (YYYY-MM-DD)
                else:
                    x_labels.append(str(idx))

        return score_pivot, total, rank, x_labels

    def plot_subjects(self):
        score_pivot, total, rank, x_labels = self.prepare_data()
        if score_pivot.empty:
            QMessageBox.information(self, "提示", "没有可绘制的科目数据，请先导入 CSV。")
            return

        # build series dict
        series_dict = {}
        for col in score_pivot.columns:
            series_dict[col] = score_pivot[col].tolist()

        self.chartview.plot_lines(x_labels, series_dict, title="各科分数趋势")

    def plot_total(self):
        score_pivot, total, rank, x_labels = self.prepare_data()
        if total is None or total.empty:
            QMessageBox.information(self, "提示", "没有可绘制的总分数据。")
            return
        series_dict = {'总分': total.tolist()}
        self.chartview.plot_lines(x_labels, series_dict, title="总分趋势")

    def plot_rank(self):
        score_pivot, total, rank, x_labels = self.prepare_data()
        if rank is None or rank.empty:
            QMessageBox.information(self, "提示", "没有可绘制的排名数据（total_rank 列缺失或为空）。")
            return
        series_dict = {'排名': rank.tolist()}
        self.chartview.plot_lines(x_labels, series_dict, title="排名趋势")

    def edit_notes(self):
        if not self.notes_editing:
            self.notes_text.setReadOnly(False)
            self.notes_editing = True
        else:
            self.save_notes()
            self.notes_text.setReadOnly(True)
            self.notes_editing = False

    def load_notes(self):
        try:
            with open("note.txt", "r", encoding="utf-8") as f:
                content = f.read()
            self.notes_text.setPlainText(content)
            self.notes_text.setReadOnly(True)
        except FileNotFoundError:
            self.notes_text.setPlainText("暂无备注")
            self.notes_text.setReadOnly(True)

    def save_notes(self):
        note_content = self.notes_text.toPlainText().strip()
        try:
            with open("note.txt", "w", encoding="utf-8") as f:
                f.write(note_content)
            QMessageBox.information(self, "提示", "备注保存成功")
            self.notes_editing = False
            self.notes_text.setReadOnly(True)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存备注失败：{e}")


def main():
    app = QApplication(sys.argv)
    win = ScoreVisualizer()
    win.showMaximized()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
