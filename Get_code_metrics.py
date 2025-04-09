import pandas as pd
import os
from CCpredictor.understand_results.Understand_API_Check import understand

def process_excel(input_path, output_path):
    # 读取Excel文件
    xls = pd.ExcelFile(input_path)

    # 创建一个ExcelWriter对象，用于将结果保存到多个工作表中
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        # 遍历所有工作表
        for sheet_name in xls.sheet_names:
            # 读取当前工作表的数据
            data = pd.read_excel(xls, sheet_name=sheet_name)

            # 初始化一个字典来存储文件的度量
            file_metrics = {}

            # 遍历DataFrame中的每一行
            for index, row in data.iterrows():
                file_key = row['File']
                if file_key not in file_metrics:
                    file_metrics[file_key] = {
                        # LOC
                        'CountLineCode': 0,  # file
                        'CountLine': 0,  # file
                        'CountLineComment': 0,  # file
                        'CountLineBlank': 0,  # file
                        'CountLineCodeDecl': 0,  # file
                        'CountLineCodeExe': 0,  # file

                        # CK
                        'MaxInheritanceTree': 0,  # class
                        'CountClassDerived': 0,  # class
                        'CountClassCoupled': 0,  # class
                        'CountDeclMethodAll': 0,  # class
                        'PercentLackOfCohesion': 0,  # class
                        'SumCyclomatic': 0,  # file

                        # McCabe
                        'SumCyclomaticModified': 0,  # file
                        'SumCyclomaticStrict': 0,  # file
                        'SumEssential': 0,  # file
                        'MaxCyclomatic': 0,  # file

                        # Fan-in & Fan-out
                        'CountInput': 0,  # Function
                        'CountOutput': 0  # Function
                    }

                if row['Kind'] == 'File':
                    file_metrics[file_key]['CountLine'] = float(row['CountLine']) if pd.notnull(row['CountLine']) else 0
                    file_metrics[file_key]['CountLineCode'] = float(row['CountLineCode']) if pd.notnull(row['CountLineCode']) else 0
                    file_metrics[file_key]['CountLineComment'] = float(row['CountLineComment']) if pd.notnull(row['CountLineComment']) else 0
                    file_metrics[file_key]['CountLineBlank'] = float(row['CountLineBlank']) if pd.notnull(row['CountLineBlank']) else 0
                    file_metrics[file_key]['CountLineCodeDecl'] = float(row['CountLineCodeDecl']) if pd.notnull(row['CountLineCodeDecl']) else 0
                    file_metrics[file_key]['CountLineCodeExe'] = float(row['CountLineCodeExe']) if pd.notnull(row['CountLineCodeExe']) else 0
                    file_metrics[file_key]['MaxCyclomatic'] = float(row['MaxCyclomatic']) if pd.notnull(row['MaxCyclomatic']) else 0
                    file_metrics[file_key]['AvgCyclomatic'] = float(row['AvgCyclomatic']) if pd.notnull(row['AvgCyclomatic']) else 0
                    file_metrics[file_key]['SumCyclomatic'] = float(row['SumCyclomatic']) if pd.notnull(row['SumCyclomatic']) else 0
                else:
                    file_metrics[file_key]['CountClassCoupled'] += float(row['CountClassCoupled']) if pd.notnull(row['CountClassCoupled']) else 0
                    file_metrics[file_key]['CountClassDerived'] += float(row['CountClassDerived']) if pd.notnull(row['CountClassDerived']) else 0
                    file_metrics[file_key]['CountDeclMethodAll'] += float(row['CountDeclMethodAll']) if pd.notnull(row['CountDeclMethodAll']) else 0
                    file_metrics[file_key]['MaxInheritanceTree'] += float(row['MaxInheritanceTree']) if pd.notnull(row['MaxInheritanceTree']) else 0
                    file_metrics[file_key]['PercentLackOfCohesion'] += float(row['PercentLackOfCohesion']) if pd.notnull(row['PercentLackOfCohesion']) else 0
                    file_metrics[file_key]['CountOutput'] += float(row['CountOutput']) if pd.notnull(row['CountOutput']) else 0
                    file_metrics[file_key]['CountInput'] += float(row['CountInput']) if pd.notnull(row['CountInput']) else 0

            # 将字典转换为DataFrame
            results = pd.DataFrame.from_dict(file_metrics, orient='index',
                                             columns=[
                                                 'CountLineCode',
                                                 'CountLine',
                                                 'CountLineComment',
                                                 'CountLineBlank',
                                                 'CountLineCodeDecl',
                                                 'CountLineCodeExe',
                                                 'MaxInheritanceTree',
                                                 'CountClassDerived',
                                                 'CountClassCoupled',
                                                 'CountDeclMethodAll',
                                                 'PercentLackOfCohesion',
                                                 'SumCyclomatic',
                                                 'MaxCyclomatic',
                                                 'CountInput',
                                                 'CountOutput'
                                             ])

            # 重置索引
            results.reset_index(inplace=True)
            results.rename(columns={'index': 'File'}, inplace=True)

            # 将当前工作表的结果保存到Excel中（每个sheet一个单独的sheet）
            results.to_excel(writer, sheet_name=sheet_name, index=False)

    print(f"处理完毕，结果已保存到 {output_path}")


def process_understand_databases(db_dir, excel_file):
    # 获取数据库文件列表
    db_files = [f for f in os.listdir(db_dir) if f.endswith(".und")]
    # 如果需要处理特定的数据库文件，可以手动指定
    # db_files = ['apollo-1.0.0.und']

    # 创建一个空的ExcelWriter对象
    with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        xls = pd.ExcelFile(excel_file)

        # 遍历每个数据库文件
        for db_file in db_files:
            db_path = os.path.join(db_dir, db_file)
            db = understand.open(db_path)

            if db:
                print(f"Processing {db_file}...")
                version = db_file[:-4]
                temp_df = extract_metrics_from_db(db)
                db.close()
                update_excel_sheet(xls, writer, version, temp_df)
            else:
                print(f"Failed to open {db_file}")

    print("Results saved to Excel file.")


def extract_metrics_from_db(db):
    columns = ["File", "SumCyclomaticModified", "SumCyclomaticStrict", "SumEssential"]
    temp_df = pd.DataFrame(columns=columns)

    for file in db.ents("file"):
        file_path = file.longname()
        metrics = file.metric(["SumCyclomaticModified", "SumCyclomaticStrict", "SumEssential"])

        sum_cyclomatic_modified = metrics.get("SumCyclomaticModified", 0)
        sum_cyclomatic_strict = metrics.get("SumCyclomaticStrict", 0)
        sum_essential = metrics.get("SumEssential", 0)

        temp_df = pd.concat([temp_df, pd.DataFrame({
            "File": [file_path],
            "SumCyclomaticModified": [sum_cyclomatic_modified],
            "SumCyclomaticStrict": [sum_cyclomatic_strict],
            "SumEssential": [sum_essential]
        })], ignore_index=True)

    return temp_df


def update_excel_sheet(xls, writer, version, temp_df):
    if version in xls.sheet_names:
        df_excel = pd.read_excel(xls, sheet_name=version)
        df_combined = pd.merge(df_excel, temp_df, on="File", how="left")
        df_combined.to_excel(writer, sheet_name=version, index=False)
    else:
        print(f"Sheet {version} not found in Excel file.")


def main():
    input_path = input("please input your understand_file directory: ")
    output_path = input("please input your output_file directory: ")
    db_dir = input('please input your database directory: ')
    # example input:
    # db_dir = "understand_results/autoware_und"
    # input_path = pd.ExcelFile('understand_results/autoware_und/autoware.xlsx')
    # output_path = 'Results/autoware_result.xlsx'
    process_excel(input_path, output_path)
    process_understand_databases(db_dir, output_path)
