import sys
import os
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = r"C:/Users/浅曦/AppData/Local/Programs/Python/Python311/Lib/site-packages/PyQt5/Qt5/plugins/platforms"

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QFileDialog, QMessageBox, QTextEdit, QLabel, QFrame
)
from PyQt5.QtGui import QFont
import pandas as pd
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 微软雅黑


class ScoreVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RankingAnalyzer")
        self.setMinimumSize(1000, 700)
        self.base_w = 1000
        self.base_h = 700
        self.base_font_sizes = {
            'btn': 9,
            'title': 11,
            'ylabel': 10,
            'notes': 10,
            'notes_btn': 9,
            'legend': 9,
            'ticks': 9,
            'annot': 9
        }
        
        # 获取屏幕DPI信息
        screen = QApplication.primaryScreen()
        self.screen_dpi = screen.logicalDotsPerInch()
        self.base_dpi = 96  # 基准DPI (1080p屏幕)
        print(f"Screen DPI: {self.screen_dpi}")

        self.df = pd.DataFrame(columns=["exam", "subject", "score", "rank"])
        self.notes_editing = False

        central = QWidget()
        self.setCentralWidget(central)

        # 顶部按钮栏
        top_buttons = QHBoxLayout()
        self.btn_import = QPushButton("导入 CSV")
        self.btn_export = QPushButton("导出 CSV")
        self.btn_subjects = QPushButton("科目趋势")
        self.btn_total = QPushButton("总分趋势")
        self.btn_rank = QPushButton("排名趋势")

        for b in (self.btn_import, self.btn_export, self.btn_subjects, self.btn_total, self.btn_rank):
            b.setFont(QFont("Microsoft YaHei", self.base_font_sizes['btn']))

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

        # 左侧图表
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.fig.patch.set_facecolor("#f8f8f8")
        self.ax.set_facecolor("#ffffff")
        self.canvas = FigureCanvas(self.fig)

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.canvas)

        # 右侧备注
        right_layout = QVBoxLayout()
        self.notes_label = QLabel("备注")
        self.notes_label.setFont(QFont("Microsoft YaHei", self.base_font_sizes['title']))
        right_layout.addWidget(self.notes_label)

        self.notes_text = QTextEdit()
        self.notes_text.setReadOnly(True)
        self.notes_text.setFont(QFont("Microsoft YaHei", self.base_font_sizes['notes']))
        right_layout.addWidget(self.notes_text)

        notes_buttons = QHBoxLayout()
        self.btn_edit = QPushButton("编辑备注")
        self.btn_save = QPushButton("保存备注")
        self.btn_edit.setFont(QFont("Microsoft YaHei", self.base_font_sizes['notes_btn']))
        self.btn_save.setFont(QFont("Microsoft YaHei", self.base_font_sizes['notes_btn']))
        self.btn_edit.clicked.connect(self.edit_notes)
        self.btn_save.clicked.connect(self.save_notes)
        notes_buttons.addWidget(self.btn_edit)
        notes_buttons.addWidget(self.btn_save)
        right_layout.addLayout(notes_buttons)

        # 布局
        main_layout = QHBoxLayout()
        left_frame = QFrame()
        left_frame.setLayout(left_layout)
        left_frame.setFrameShape(QFrame.StyledPanel)
        right_frame = QFrame()
        right_frame.setLayout(right_layout)
        right_frame.setFrameShape(QFrame.StyledPanel)
        right_frame.setFixedWidth(360)

        main_layout.addWidget(left_frame, 6)
        main_layout.addWidget(right_frame, 1)

        outer = QVBoxLayout(central)
        outer.addLayout(top_buttons)
        outer.addLayout(main_layout)

        self.load_notes()
        QtCore.QTimer.singleShot(50, self.auto_load_csv)

    def calculate_scale_factor(self, width, height):
        """计算缩放因子，考虑DPI和窗口大小"""
        # 计算基于窗口大小的缩放
        size_scale = min(width / self.base_w, height / self.base_h)
        
        # 计算基于DPI的缩放
        dpi_scale = self.screen_dpi / self.base_dpi
        
        # 组合缩放因子 - 使用更平缓的缩放曲线
        # 基础缩放因子
        base_scale = min(size_scale, 1.5)  # 限制最大缩放为1.5倍
        
        # 对更大的缩放使用更平缓的曲线
        if size_scale > 1.2:
            adjusted_scale = 1.0 + (size_scale - 1.0) * 0.4  # 更小的缩放比例
        else:
            adjusted_scale = size_scale
            
        # DPI调整 - 对高DPI屏幕使用更小的缩放
        if dpi_scale > 1.2:
            dpi_adjust = 1.0 + (dpi_scale - 1.0) * 0.5  # 进一步减小高DPI缩放
        else:
            dpi_adjust = dpi_scale
            
        # 最终缩放因子
        total_scale = min(adjusted_scale * dpi_adjust, 1.5)  # 绝对上限设为1.5
        
        # 允许更小的缩放因子 - 最小设为0.6（原为0.8）
        return max(total_scale, 0.6)  # 允许更小的字体

    def resizeEvent(self, event):
        try:
            w = self.width()
            h = self.height()
            total_scale = self.calculate_scale_factor(w, h)
            print(f"Window size: {w}x{h}, Scale factor: {total_scale:.2f}")

            # 计算字体大小 - 降低最小字体限制
            # 按钮字体：最小6pt（原7pt），最大14pt
            btn_size = max(6, min(14, int(self.base_font_sizes['btn'] * total_scale)))
            # 标题字体：最小7pt（原8pt），最大16pt
            title_size = max(7, min(16, int(self.base_font_sizes['title'] * total_scale)))
            # Y轴标签字体：最小6pt（原7pt），最大14pt
            ylabel_size = max(6, min(14, int(self.base_font_sizes['ylabel'] * total_scale)))
            # 备注字体：最小7pt（原7pt），最大14pt
            notes_size = max(7, min(14, int(self.base_font_sizes['notes'] * total_scale)))
            # 备注按钮字体：最小6pt（原7pt），最大14pt
            notes_btn_size = max(6, min(14, int(self.base_font_sizes['notes_btn'] * total_scale)))
            # 图例字体：最小6pt（原7pt），最大14pt
            legend_size = max(6, min(14, int(self.base_font_sizes['legend'] * total_scale)))
            # 刻度字体：最小6pt（原7pt），最大14pt
            ticks_size = max(6, min(14, int(self.base_font_sizes['ticks'] * total_scale)))
            # 注解字体：最小6pt（原7pt），最大14pt
            annot_size = max(6, min(14, int(self.base_font_sizes['annot'] * total_scale)))

            # 按钮
            for b in (self.btn_import, self.btn_export, self.btn_subjects, self.btn_total, self.btn_rank):
                b.setFont(QFont("Microsoft YaHei", btn_size))
                b.setFixedHeight(int(26 * total_scale))
                b.setFixedWidth(int(90 * total_scale))

            # 备注
            self.notes_label.setFont(QFont("Microsoft YaHei", title_size))
            self.notes_text.setFont(QFont("Microsoft YaHei", notes_size))
            self.btn_edit.setFont(QFont("Microsoft YaHei", notes_btn_size))
            self.btn_save.setFont(QFont("Microsoft YaHei", notes_btn_size))
            self.btn_edit.setFixedHeight(int(24 * total_scale))
            self.btn_save.setFixedHeight(int(24 * total_scale))

            # Matplotlib
            if hasattr(self.ax, 'title'):
                self.ax.title.set_fontsize(title_size)
            if hasattr(self.ax, 'yaxis') and hasattr(self.ax.yaxis, 'label'):
                self.ax.yaxis.label.set_fontsize(ylabel_size)
            self.ax.tick_params(axis='both', which='major', labelsize=ticks_size)
            if hasattr(self.ax, 'get_legend'):
                legend = self.ax.get_legend()
                if legend:
                    for text in legend.get_texts():
                        text.set_fontsize(legend_size)
            # 保存注解字体大小
            self.annot_fontsize = annot_size

            self.canvas.draw()
        except Exception as e:
            print(f"Resize error: {e}")
        super().resizeEvent(event)

    def auto_load_csv(self):
        default_path = "data.csv"
        if os.path.exists(default_path):
            try:
                self.df = pd.read_csv(default_path, parse_dates=["exam"])
                self.plot_subjects()
            except Exception as e:
                QMessageBox.information(self, "提示", f"读取 data.csv 失败，请手动导入。\n错误：{e}")
        else:
            QMessageBox.information(self, "提示", "没有搜寻到成绩信息，请手动导入。")

    def load_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "打开 CSV", filter="CSV 文件 (*.csv)")
        if not path:
            return
        try:
            self.df = pd.read_csv(path, parse_dates=["exam"])
            QMessageBox.information(self, "提示", f"导入成功：共{len(self.df)}条记录")
            self.plot_subjects()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法导入：{e}")

    def save_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "保存 CSV", filter="CSV 文件 (*.csv)")
        if not path:
            return
        try:
            if not path.lower().endswith('.csv'):
                path += '.csv'
            self.df.to_csv(path, index=False, date_format="%Y-%m-%d")
            QMessageBox.information(self, "提示", "导出成功")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法导出：{e}")

    def prepare_data(self):
        score_pivot = (self.df
                       .pivot(index="exam", columns="subject", values="score")
                       .sort_index())
        total = score_pivot.sum(axis=1).rename('总分')
        try:
            rank = self.df.groupby("exam")["total_rank"].first().sort_index()
        except Exception:
            rank = pd.Series(index=score_pivot.index, data=[0]*len(score_pivot), name='rank')
        return score_pivot, total, rank

    def clear_axes(self):
        self.ax.clear()
        for spine in self.ax.spines.values():
            spine.set_linewidth(2)

    def format_axis(self, dates):
        """设置等间距的x轴"""
        if len(dates) == 0:
            return
        
        # 创建等间距索引 (0,1,2,...)
        x_ticks = np.arange(len(dates))
        
        # 设置等间距的刻度位置
        self.ax.set_xticks(x_ticks)
        
        # 设置日期格式的标签
        date_labels = [date.strftime('%Y-%m') for date in dates]
        self.ax.set_xticklabels(date_labels)
        
        # 设置x轴范围，使点之间有空间
        if len(x_ticks) > 1:
            self.ax.set_xlim(-0.5, len(x_ticks)-0.5)
        
        # 旋转标签并调整对齐方式
        for lbl in self.ax.get_xticklabels():
            lbl.set_rotation(45)
            lbl.set_ha('right')
        
        self.ax.tick_params(axis='both', which='major', labelsize=self.annot_fontsize)

    def plot_subjects(self):
        self.clear_axes()
        if self.df.empty:
            QMessageBox.information(self, "提示", "当前没有数据，请先导入 CSV。")
            return
        score_pivot, total, rank = self.prepare_data()
        dates = score_pivot.index
        
        # 创建等间距索引 (0,1,2,...)
        x_ticks = np.arange(len(dates))
        
        for subj in score_pivot.columns:
            y = score_pivot[subj]
            # 使用等间距索引绘图
            self.ax.plot(x_ticks, y, marker='o', label=subj, linewidth=2)
            for i, (x_val, y_val) in enumerate(zip(x_ticks, y)):
                try:
                    self.ax.annotate(
                        f"{y_val:.0f}",
                        xy=(x_val, y_val),
                        xytext=(-20, 20),
                        textcoords='offset points',
                        fontsize=self.annot_fontsize,
                        ha='left',
                        va='top'
                    )
                except Exception:
                    pass

        self.ax.set_title("各科分数趋势", fontsize=self.annot_fontsize)
        self.ax.set_ylabel("分数", fontsize=self.annot_fontsize)
        self.ax.legend(fontsize=self.annot_fontsize, loc='best', frameon=True, borderaxespad=1.5)
        self.format_axis(dates)
        self.canvas.draw()

    def plot_total(self):
        self.clear_axes()
        if self.df.empty:
            QMessageBox.information(self, "提示", "当前没有数据，请先导入 CSV。")
            return
        score_pivot, total, rank = self.prepare_data()
        dates = score_pivot.index
        
        # 创建等间距索引 (0,1,2,...)
        x_ticks = np.arange(len(dates))
        
        # 使用等间距索引绘图
        self.ax.plot(x_ticks, total.values, marker='s', linestyle='-', linewidth=2, label='总分')

        for i, (x_val, y_val) in enumerate(zip(x_ticks, total.values)):
            try:
                self.ax.annotate(
                    f"{y_val:.0f}",
                    xy=(x_val, y_val),
                    xytext=(-20, 20),
                    textcoords='offset points',
                    fontsize=self.annot_fontsize,
                    ha='left',
                    va='top'
                )
            except Exception:
                pass

        self.ax.set_title("总分趋势", fontsize=self.annot_fontsize)
        self.ax.set_ylabel("总分", fontsize=self.annot_fontsize)
        self.format_axis(dates)
        self.canvas.draw()

    def plot_rank(self):
        self.clear_axes()
        if self.df.empty:
            QMessageBox.information(self, "提示", "当前没有数据，请先导入 CSV。")
            return
        score_pivot, total, rank = self.prepare_data()
        dates = score_pivot.index
        
        # 创建等间距索引 (0,1,2,...)
        x_ticks = np.arange(len(dates))
        
        # 使用等间距索引绘图
        self.ax.plot(x_ticks, rank.values, marker='^', linestyle='--', linewidth=2, label='排名')

        for i, (x_val, y_val) in enumerate(zip(x_ticks, rank.values)):
            try:
                self.ax.annotate(
                    f"{int(y_val)}",
                    xy=(x_val, y_val),
                    xytext=(-20, 20),
                    textcoords='offset points',
                    fontsize=self.annot_fontsize,
                    ha='left',
                    va='top'
                )
            except Exception:
                pass

        self.ax.invert_yaxis()
        self.ax.set_title("排名趋势", fontsize=self.annot_fontsize)
        self.ax.set_ylabel("排名", fontsize=self.annot_fontsize)
        self.format_axis(dates)
        self.canvas.draw()

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = ScoreVisualizer()
    win.showMaximized()
    sys.exit(app.exec_())
