import os
import pandas as pd

# 设置文件夹路径
folder_path = '../autoware_und'  # 请替换为你的文件夹路径
output_file = 'autoware_combined.xlsx'  # 输出文件名

# 获取文件夹中所有CSV文件的列表
files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

# 创建一个新的Excel写入器
with pd.ExcelWriter(os.path.join(folder_path, output_file), engine='openpyxl') as writer:
    for file in files:
        # 读取CSV文件
        file_path = os.path.join(folder_path, file)
        df = pd.read_csv(file_path)

        # 获取文件名（不含扩展名）作为工作表名
        sheet_name = os.path.splitext(file)[0]

        # 将数据写入新的工作表
        df.to_excel(writer, sheet_name=sheet_name, index=False)

print("所有文件已成功汇总到一个新的Excel文件中。")