import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

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
        tk.Button(btn_frame, text="导入 CSV", command=self.load_csv, width=15, height=2, font=("SimHei", 14)
            ).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="导出 CSV", command=self.save_csv, width=15, height=2, font=("SimHei", 14)
            ).pack(side=tk.LEFT, padx=5)   
        # tk.Button(btn_frame, text="绘制图表", command=self.plot, width=15, height=2).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="科目趋势", command=self.plot_subjects, width=15, height=2, font=("SimHei", 14)
            ).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="总分趋势", command=self.plot_total, width=15, height=2, font=("SimHei", 14)
            ).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="排名趋势", command=self.plot_rank, width=15, height=2, font=("SimHei", 14)
            ).pack(side=tk.LEFT, padx=5)

        # 创建主区域：左右布局（使用 grid 控制宽度比例）
        main_frame = tk.Frame(self, bg="#f8f8f8")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 设置列权重：左侧更宽，右侧窄
        main_frame.columnconfigure(0, weight=6)  # 左侧图表区域占 4 份
        main_frame.columnconfigure(1, weight=1)  # 右侧备注区域占 1 份
        main_frame.rowconfigure(0, weight=1)

        # 左侧图表区域
        chart_frame = tk.Frame(main_frame, bg="#ffffff", bd=2, relief="groove")
        chart_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        chart_frame.grid_propagate(False) 
        chart_frame.columnconfigure(0, weight=1) 
        chart_frame.rowconfigure(0, weight=1)  


        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.fig.patch.set_facecolor("#f8f8f8")
        self.ax.set_facecolor("#ffffff")

        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")  # 改为grid布局
        self.canvas.get_tk_widget().configure(bg="#f8f8f8")

        # 右侧备注区域
        side_frame = tk.Frame(main_frame, bg="#f8f8f8")
        side_frame.grid(row=0, column=1, sticky="nsew")
        side_frame.grid_propagate(False)  # 禁止自动调整大小
        side_frame.columnconfigure(0, weight=1)  # 让内容填满整个备注区域
        side_frame.rowconfigure(1, weight=1)     # 让文本框可扩展

        # 备注标签（放在第0行）
        tk.Label(side_frame, text="备注", font=('SimHei', 20, 'bold'), 
                 bg="#f8f8f8").grid(row=0, column=0, pady=(20, 5), sticky="w")  # 左对齐

        # 备注文本框（放在第1行，可扩展）
        self.notes_text = tk.Text(side_frame, height=25, font=('SimHei', 18), 
                wrap=tk.WORD, state='disabled')
        self.notes_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        # 按钮框架（放在第2行，底部固定高度）
        button_frame = tk.Frame(side_frame, bg="#f8f8f8")
        button_frame.grid(row=2, column=0, sticky="ew", pady=5)  # 水平填充
        tk.Button(button_frame, text="编辑备注", font=('SimHei', 16), command=self.edit_notes
            ).pack(side=tk.LEFT, padx=5)  # 按钮仍可用pack，因为它们在button_frame内部
        tk.Button(button_frame, text="保存备注", font=('SimHei', 16), command=self.save_notes
            ).pack(side=tk.LEFT, padx=5)

        # 加载备注
        self.notes_editing = False  # 是否正在编辑备注
        self.load_notes()

        # 自动加载 CSV
        self.auto_load_csv()

    def auto_load_csv(self): #尝试自动搜寻并加载 data.csv
        default_path = "data.csv"
        if os.path.exists(default_path):
            try:
                self.df = pd.read_csv(default_path, parse_dates=["exam"])
                self.plot_subjects()
            except Exception as e:
                messagebox.showinfo("提示", f"读取 data.csv 失败，请手动导入。\n错误：{e}")
        else:
            messagebox.showinfo("提示", "没有搜寻到成绩信息，请手动导入。")

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


    def edit_notes(self):
        if not self.notes_editing:
            self.notes_text['state'] = 'normal'
            self.notes_editing = True
        else:
            # 保存文本并设为只读
            self.save_notes()
            self.notes_text['state'] = 'disabled'
            self.notes_editing = False

    def load_notes(self):
        try:
            with open("note.txt", "r", encoding="utf-8") as f:
                content = f.read()
            self.notes_text.config(state='normal')  # 先解锁以插入内容
            self.notes_text.delete("1.0", tk.END)
            self.notes_text.insert(tk.END, content)
            self.notes_text.config(state='disabled')  # 再设回只读
        except FileNotFoundError:
            self.notes_text.config(state='normal')
            self.notes_text.insert(tk.END, "暂无备注")
            self.notes_text.config(state='disabled')

    def save_notes(self):
        note_content = self.notes_text.get("1.0", tk.END).strip()
        with open("note.txt", "w", encoding="utf-8") as f:
            f.write(note_content)
        messagebox.showinfo("提示", "备注保存成功")
        self.notes_editing = False
        self.notes_text['state'] = 'disabled'

if __name__ == "__main__":
    app = ScoreVisualizer()
    app.mainloop()
