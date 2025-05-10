import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['SimHei']  # 黑体

class ScoreVisualizer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RankingAnalyzer")
        # self.geometry("1080x1080")
        self.state('zoomed')
        self.configure(bg="#f8f8f8")  # 设置柔和背景色
        # 数据容器
        self.df = pd.DataFrame(columns=["exam","subject","score","rank"])

        # 按钮
        btn_frame = tk.Frame(self)
        btn_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        # btn_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        tk.Button(btn_frame, text="导入 CSV", command=self.load_csv, width=15, height=2, font=("SimHei", 14)).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="导出 CSV", command=self.save_csv, width=15, height=2, font=("SimHei", 14)).pack(side=tk.LEFT, padx=5)   
        # tk.Button(btn_frame, text="绘制图表", command=self.plot, width=15, height=2).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="科目趋势", command=self.plot_subjects, width=15, height=2, font=("SimHei", 14)).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="总分趋势", command=self.plot_total, width=15, height=2, font=("SimHei", 14)).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="排名趋势", command=self.plot_rank, width=15, height=2, font=("SimHei", 14)).pack(side=tk.LEFT, padx=5)

        # Matplotlib 图表区
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        # self.fig, (self.ax1, self.ax2) = plt.subplots(2,1, figsize=(6,6))
        self.fig.patch.set_facecolor("#f8f8f8")
        self.ax.set_facecolor("#ffffff")

        # 窗口美化
        canvas_frame = tk.Frame(self, bg="#ffffff", bd=2, relief="groove")
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.canvas = FigureCanvasTkAgg(self.fig, master=canvas_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas.get_tk_widget().configure(bg="#f8f8f8")


        # self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        # self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def load_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV文件","*.csv")])
        if not path: return
        try:
            self.df = pd.read_csv(path, parse_dates=["exam"])
            messagebox.showinfo("提示", f"导入成功：共{len(self.df)}条记录")
            self.plot_subjects()
            
        except Exception as e:
            messagebox.showerror("错误", f"无法导入：{e}")

    def save_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV文件","*.csv")])
        if not path: return
        try:
            self.df.to_csv(path, index=False, date_format="%Y-%m-%d")
            messagebox.showinfo("提示", "导出成功")
        except Exception as e:
            messagebox.showerror("错误", f"无法导出：{e}")

    def prepare_data(self):
        # 各科成绩 pivot
        score_pivot = (self.df
                    .pivot(index="exam", columns="subject", values="score")
                    .sort_index())
        # 总分
        total = score_pivot.sum(axis=1).rename('总分')
        # 排名
        rank = self.df.groupby("exam")["total_rank"].first().sort_index()
        return score_pivot, total, rank

    def clear_axes(self):
        self.ax.clear()
        for spine in self.ax.spines.values():
            spine.set_linewidth(2)

    def format_axis(self):
        # 只用考试日期做刻度，格式 YYYYMM，旋转并调整字号
        score_pivot, total, rank = self.prepare_data()
        dates = score_pivot.index
        self.ax.set_xticks(dates)
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        for lbl in self.ax.get_xticklabels():
            lbl.set_rotation(45)
            lbl.set_ha('right')
        self.ax.tick_params(axis='both', which='major', labelsize=18)

    def plot_subjects(self):
        # 清理、绘制各科成绩
        self.clear_axes()
        score_pivot, total, rank = self.prepare_data()

        for subj in score_pivot.columns:
            self.ax.plot(score_pivot.index, score_pivot[subj],
                        marker='o', label=subj, linewidth=2)
            
        # 添加具体数字注释    
        for subj in score_pivot.columns:
            y = score_pivot[subj]
            self.ax.plot(score_pivot.index, y, marker='o', label=subj, linewidth=2)
            for x_val, y_val in zip(score_pivot.index, y):
                self.ax.annotate(
                    f"{y_val:.0f}",
                    xy=(x_val, y_val),
                    xytext=(-20, 20),
                    textcoords='offset points',
                    fontsize=20,
                    ha='left',
                    va='top'
                )

        self.ax.set_title("各科分数趋势", fontsize=22)
        self.ax.set_ylabel("分数", fontsize=20)
        self.ax.legend()
        self.format_axis()
        self.canvas.draw()

    def plot_total(self):
        self.clear_axes()
        score_pivot, total, rank = self.prepare_data()
        self.ax.plot(total.index, total.values,
                     marker='s', linestyle='-', color='r', linewidth=2)
        
        # 添加具体数字注释          
        self.ax.plot(total.index, total.values, marker='s', linestyle='-', color='r', linewidth=2)
        for x_val, y_val in zip(total.index, total.values):
            self.ax.annotate(
                f"{y_val:.0f}",
                xy=(x_val, y_val),
                xytext=(-20, 20),
                textcoords='offset points',
                fontsize=20,
                ha='left',
                va='top'
            )

        self.ax.set_title("总分趋势", fontsize=22)
        self.ax.set_ylabel("总分", fontsize=20)
        self.format_axis()
        self.canvas.draw()

    def plot_rank(self):
        self.clear_axes()
        score_pivot, total, rank = self.prepare_data()
        self.ax.plot(rank.index, rank.values,
                    marker='^', linestyle='--', color='g', linewidth=2)
        
        # 添加具体数字注释          
        self.ax.plot(rank.index, rank.values, marker='^', linestyle='--', color='g', linewidth=2)
        for x_val, y_val in zip(rank.index, rank.values):
            self.ax.annotate(
                f"{int(y_val)}",
                xy=(x_val, y_val),
                xytext=(-20, 20),
                textcoords='offset points',
                fontsize=20,
                ha='left',
                va='top'
            )

        self.ax.invert_yaxis()
        self.ax.set_title("排名趋势", fontsize=22)
        self.ax.set_ylabel("排名", fontsize=20)
        self.format_axis()
        self.canvas.draw()


if __name__ == "__main__":
    app = ScoreVisualizer()
    app.mainloop()
