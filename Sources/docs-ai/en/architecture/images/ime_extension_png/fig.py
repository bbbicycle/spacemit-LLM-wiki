import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# -------------------------- 全局样式设置 --------------------------
plt.rcParams['font.size'] = 12
plt.rcParams['font.weight'] = 'bold'
fig = plt.figure(figsize=(14, 10), dpi=100)

# -------------------------- 辅助函数：画一个网格块 --------------------------
def draw_grid(ax, data, x0, y0, cell_size=0.8, 
              arrow_dirs=None, label=None, version=None):
    """
    data: 二维列表，网格数字
    x0, y0: 网格左下角坐标
    cell_size: 单元格大小
    arrow_dirs: 箭头方向列表，每个元素是 (i,j, di, dj) 表示从 (i,j) 连到 (i+di, j+dj)
    label: 右下角标签（如A、B、C）
    version: 版本号（如v16, v17）
    """
    n_rows = len(data)
    n_cols = len(data[0]) if n_rows > 0 else 0
    
    # 画单元格
    for i in range(n_rows):
        for j in range(n_cols):
            x = x0 + j * cell_size
            y = y0 + (n_rows - 1 - i) * cell_size  # 行从上到下
            # 橙色边框+浅底色
            rect = Rectangle((x, y), cell_size, cell_size,
                            facecolor='#fff5e6', edgecolor='#d2691e', lw=2)
            ax.add_patch(rect)
            # 数字
            ax.text(x + cell_size/2, y + cell_size/2, str(data[i][j]),
                    ha='center', va='center', fontsize=11, color='black')
    
    # 画蓝色箭头
    if arrow_dirs is not None:
        for (i, j, di, dj) in arrow_dirs:
            # 起点中心
            x_start = x0 + j * cell_size + cell_size/2
            y_start = y0 + (n_rows - 1 - i) * cell_size + cell_size/2
            # 终点中心
            x_end = x0 + (j + dj) * cell_size + cell_size/2
            y_end = y0 + (n_rows - 1 - (i + di)) * cell_size + cell_size/2
            # 箭头
            ax.annotate('', xy=(x_end, y_end), xytext=(x_start, y_start),
                        arrowprops=dict(arrowstyle='->', color='#1f77b4', lw=2))
    
    # 标签（右下角）
    if label is not None:
        ax.text(x0 - 0.3, y0 - 0.2, label, fontsize=16, fontweight='bold')
    # 版本号（右侧）
    if version is not None:
        ax.text(x0 + n_cols * cell_size + 0.2, 
                y0 + n_rows * cell_size / 2, version, fontsize=14)
    return n_rows, n_cols

# -------------------------- 辅助函数：画双向箭头标注（λ, σ） --------------------------
def draw_annotation(ax, x_start, x_end, y, text, arrow_color='black'):
    # 水平双向箭头
    ax.annotate('', xy=(x_end, y), xytext=(x_start, y),
                arrowprops=dict(arrowstyle='<->', color=arrow_color, lw=1.5))
    ax.text((x_start + x_end)/2, y + 0.1, text, ha='center', fontsize=16)

def draw_vertical_annotation(ax, x, y_start, y_end, text, arrow_color='black'):
    # 垂直双向箭头
    ax.annotate('', xy=(x, y_end), xytext=(x, y_start),
                arrowprops=dict(arrowstyle='<->', color=arrow_color, lw=1.5))
    ax.text(x - 0.2, (y_start + y_end)/2, text, va='center', fontsize=16, rotation=90)

# -------------------------- 1. 绘制左上角 B 块 (v17) --------------------------
ax1 = fig.add_subplot(2, 2, 2)
ax1.set_xlim(0, 10)
ax1.set_ylim(0, 6)
ax1.axis('off')

data_B = [
    [0, 4, 8, 12, 16, 20, 24, 28],
    [1, 5, 9, 13, 17, 21, 25, 29],
    [2, 6, 10, 14, 18, 22, 26, 30],
    [3, 7, 11, 15, 19, 23, 27, 31]
]
# B块箭头：每列向下 (i,j) → (i+1,j)
arrows_B = [(i, j, 1, 0) for i in range(3) for j in range(8)]
rows_B, cols_B = draw_grid(ax1, data_B, x0=1, y0=1, arrow_dirs=arrows_B, label='B', version='v17')

# B块标注 σ 和 λ
draw_annotation(ax1, 1, 1 + cols_B*0.8, 5.5, r'$\sigma$')
draw_vertical_annotation(ax1, 0.5, 1, 1 + rows_B*0.8, r'$\lambda$')

# -------------------------- 2. 绘制左下角 A 块 (v16) --------------------------
ax2 = fig.add_subplot(2, 2, 3)
ax2.set_xlim(0, 6)
ax2.set_ylim(0, 9)
ax2.axis('off')

data_A = [
    [0, 1, 2, 3],
    [4, 5, 6, 7],
    [8, 9, 10, 11],
    [12, 13, 14, 15],
    [16, 17, 18, 19],
    [20, 21, 22, 23],
    [24, 25, 26, 27],
    [28, 29, 30, 31]
]
# A块箭头：(i,0)→(i,3)，(i,1)→(i,0)，(i,2)→(i,3)，(i,3)→(i,0)
arrows_A = []
for i in range(8):
    arrows_A.append((i, 0, 0, 3))  # 0→3
    arrows_A.append((i, 1, 0, -1)) # 5→4
    arrows_A.append((i, 2, 0, 1))  # 10→11
    arrows_A.append((i, 3, 0, -3)) # 15→12
rows_A, cols_A = draw_grid(ax2, data_A, x0=1, y0=1, arrow_dirs=arrows_A, label='A', version='v16')

# A块标注 λ 和 σ
draw_annotation(ax2, 1, 1 + cols_A*0.8, 8.5, r'$\lambda$')
draw_vertical_annotation(ax2, 0.5, 1, 1 + rows_A*0.8, r'$\sigma$')

# -------------------------- 3. 绘制右下角 C 块 (v2, v3) --------------------------
ax3 = fig.add_subplot(2, 2, 4)
ax3.set_xlim(0, 12)
ax3.set_ylim(0, 9)
ax3.axis('off')

# 左边 C1 (v2)
data_C1 = [row.copy() for row in data_A]
arrows_C1 = arrows_A.copy()
rows_C1, cols_C1 = draw_grid(ax3, data_C1, x0=1, y0=1, arrow_dirs=arrows_C1, label=None, version='v2')
# 右边 C2 (v3)
data_C2 = [row.copy() for row in data_A]
arrows_C2 = arrows_A.copy()
rows_C2, cols_C2 = draw_grid(ax3, data_C2, x0=1 + cols_C1*0.8 + 0.2, y0=1, arrow_dirs=arrows_C2, label=None, version='v3')
# C块总标签
ax3.text(0.7, 0.8, 'C', fontsize=16, fontweight='bold')

# C块标注 λ 和 λ
draw_annotation(ax3, 1, 1 + cols_C1*0.8, 8.5, r'$\lambda$')
draw_annotation(ax3, 1 + cols_C1*0.8 + 0.2, 1 + cols_C1*0.8 + 0.2 + cols_C2*0.8, 8.5, r'$\lambda$')

# -------------------------- 调整布局并显示 --------------------------
plt.tight_layout()
plt.show()