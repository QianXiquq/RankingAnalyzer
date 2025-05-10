# 🎓 RankingAnalyzer 成绩趋势分析工具

一个用于绘制考试分数与排名趋势图、查看备注的桌面应用程序，基于 Python `tkinter` 和 `matplotlib` 开发。

## ✨ 功能介绍

* 📂 导入/导出 CSV 格式成绩数据
* 📊 绘制各科成绩趋势图（含数据标注）
* 📈 总分趋势与排名趋势分析
* 📝 右侧支持备注编辑与保存
* 🧠 自动加载 `data.csv` 和 `note.txt`，方便快速启动

## 📦 环境依赖

需要安装以下 Python 第三方库：

```bash
pip install pandas matplotlib
```

Python 版本推荐：**3.8+**

## 📁 数据格式要求

CSV 文件应包含以下列（列名区分大小写）：

| exam    | subject | score | rank | total\_rank（总分排名） |
| ------- | ------- | ----- | ---- | ----------------- |
| 2023-01 | 数学      | 120   | 10   | 15                |
| 2023-01 | 英语      | 110   | 12   | 15                |

* `exam`：考试日期，建议使用 `YYYY-MM` 格式
* `subject`：科目名称
* `score`：该科分数
* `rank`：该科排名
* `total_rank`：每场考试的总分排名

✅ 支持同一场考试多条记录，不同科目分别占行。

## 🚀 使用方式

1. 启动程序（运行 `python 文件名.py`）
2. 程序会自动加载根目录的 `data.csv`（如果存在）
3. 使用上方按钮手动导入其他 CSV 文件
4. 点击按钮切换：

   * `科目趋势`：绘制各科目折线图
   * `总分趋势`：显示每场考试总分趋势
   * `排名趋势`：显示总分排名，默认从高到低绘制（即排名数越小越靠上）
5. 可在右侧编辑并保存备注，内容保存在 `note.txt`

## 📸 界面预览

![RankingAnalyzer](https://cdn.luogu.com.cn/upload/image_hosting/d8l7fklh.png)

## 📁 文件结构说明

```
RankingAnalyzer/
│
├── main.py           # 主程序
├── data.csv          # 成绩数据文件
└── note.txt          # 备注内容
```


## 📄 License

MIT License，可自由使用和修改。
