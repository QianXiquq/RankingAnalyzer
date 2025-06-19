练手项目。

### 环境依赖

需要安装以下 Python 第三方库：

```bash
pip install pandas matplotlib
```

### 数据格式要求

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

### 使用方式

1. 启动程序（运行 `python 文件名.py`）
2. 程序会自动加载根目录的 `data.csv`（如果存在）
3. 使用上方按钮手动导入其他 CSV 文件
4. 点击按钮切换：

   * `科目趋势`：绘制各科目折线图
   * `总分趋势`：显示每场考试总分趋势
   * `排名趋势`：显示总分排名，默认从高到低绘制（即排名数越小越靠上）
5. 可在右侧编辑并保存备注，内容保存在 `note.txt`

### 界面预览

![RankingAnalyzer](https://cdn.luogu.com.cn/upload/image_hosting/d8l7fklh.png)


### 开源协议

MIT License，可自由使用和修改。
