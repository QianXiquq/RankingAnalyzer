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

        # 数据容器
        self.df = pd.DataFrame(columns=["exam","subject","score","rank"])

        # 按钮
        btn_frame = tk.Frame(self)
        btn_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        # btn_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        tk.Button(btn_frame, text="导入 CSV", command=self.load_csv, width=15, height=2).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="导出 CSV", command=self.save_csv, width=15, height=2).pack(side=tk.LEFT, padx=5)   
        tk.Button(btn_frame, text="绘制图表", command=self.plot, width=15, height=2).pack(side=tk.LEFT, padx=5)
        
        # Matplotlib 图表区
        self.fig, (self.ax1, self.ax2) = plt.subplots(2,1, figsize=(6,6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def load_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV文件","*.csv")])
        if not path: return
        try:
            self.df = pd.read_csv(path, parse_dates=["exam"])
            messagebox.showinfo("提示", "导入成功")
            
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

    def plot(self):
        if self.df.empty:
            messagebox.showwarning("警告", "请先导入数据")
            return

        # 清空旧图
        self.ax1.clear()
        self.ax2.clear()

        # 准备数据：按 exam pivot
        # 各科分数折线
        score_pivot = self.df.pivot(index="exam", columns="subject", values="score").sort_index()
        # 考试排名
        rank_series = ( self.df.groupby("exam")["rank"]
                        .first().sort_index() )

        # 加粗边框
        for ax in (self.ax1, self.ax2):
            for spine in ax.spines.values():
                spine.set_linewidth(2)

        # 绘图
        for subj in score_pivot.columns:
            self.ax1.plot(score_pivot.index, score_pivot[subj], marker='o', label=subj)
        self.ax1.set_title("各科分数折线图", fontsize=22)
        self.ax1.set_ylabel("分数", fontsize=22)
        self.ax1.legend()

        self.ax2.plot(rank_series.index, rank_series.values, marker='s', linestyle='--')
        self.ax2.invert_yaxis()  # 排名越小越好
        self.ax2.set_title("总排名折线图", fontsize=22)
        self.ax2.set_ylabel("排名", fontsize=22)

        # 调整刻度文字大小
        for ax in (self.ax1, self.ax2):
            ax.tick_params(axis='both', which='major', labelsize=18)

        # 刻度日期设置
        dates = score_pivot.index
        for ax in (self.ax1, self.ax2):
            ax.set_xticks(dates)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

        # 旋转刻度
        for ax in (self.ax1, self.ax2):
            for label in ax.get_xticklabels():
                label.set_rotation(45)
                label.set_ha('right')

        # 刷新画布
        self.canvas.draw()

if __name__ == "__main__":
    app = ScoreVisualizer()
    app.mainloop()
