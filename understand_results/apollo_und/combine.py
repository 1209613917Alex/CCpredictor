import pandas as pd
import os

# 设置包含CSV文件的目录
csv_dir = '../apollo_und'  # 替换为你的CSV文件所在的目录
output_excel = 'apollo.xlsx'  # 输出的Excel文件名

# 获取目录下所有的CSV文件
csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]

# 创建一个ExcelWriter对象
with pd.ExcelWriter(output_excel, engine='xlsxwriter') as writer:
    for csv_file in csv_files:
        # 构建完整的文件路径
        file_path = os.path.join(csv_dir, csv_file)

        # 读取CSV文件
        df = pd.read_csv(file_path)

        # 将DataFrame写入Excel文件的一个新工作表中
        # 工作表名称为CSV文件的名称（不含扩展名）
        sheet_name = os.path.splitext(csv_file)[0]
        df.to_excel(writer, sheet_name=sheet_name, index=False)

print(f"所有CSV文件已成功合并到 {output_excel} 中。")