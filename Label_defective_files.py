import xml.dom.minidom
import os
import pandas as pd


def extract_diff_lines(xml_file):
    # 解析 XML 文件
    dom = xml.dom.minidom.parse(xml_file)
    document = dom.documentElement

    # 初始化结果列表
    diff_lines = []
    # 遍历每个 <commit> 节点
    for commit in document.getElementsByTagName('commit'):
        bug_flag = 0
        corrective_word_list = ['bug', 'fix', 'wrong', 'error', 'fail', 'problem', 'patch', 'correct']
        commit_msg = commit.getElementsByTagName('msg')[0].firstChild.nodeValue
        for word in corrective_word_list:
            if word.lower() in commit_msg.lower():
                bug_flag = 1
                break
        # 获取 <modified_files> 节点
        modified_files = commit.getElementsByTagName('modified_files')
        if not modified_files:
            continue
        modified_files = modified_files[0]
        # 遍历每个 <file> 节点
        for file in modified_files.getElementsByTagName('file'):
            file_path = file.getAttribute('old_path')
            diff_lines.append(
                (file_path, bug_flag))

    # 初始化结果字典
    bug_info = {}

    # 遍历 diff_lines，统计每个文件的信息
    for line in diff_lines:
        file_path = line[0]
        bug_flag = line[1]
        if file_path not in bug_info:
            bug_info[file_path] = {'bug_flag': bug_flag}
        else:
            bug_info[file_path]['bug_flag'] |= bug_flag

    return bug_info

def lable(excel_path, bug_info, sheet_name):
    # 读取Excel文件
    try:
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
    except Exception as e:
        print(f"读取Excel文件失败：{e}")
        return

    # 检查是否已经存在新列，如果不存在则添加
    new_columns = ['Bug']
    for col in new_columns:
        if col not in df.columns:
            df[col] = 0  # 初始化新列为0

    # 遍历bug_commit，更新表格
    for file_path, info in bug_info.items():
        # 假设文件路径的前缀是"prefix_"，根据实际情况修改
        prefix = "D:\\download\\" + sheet_name + '\\' + sheet_name + '\\'
        # 去掉前缀后进行匹配
        file_name = prefix + file_path
        # 找到匹配的行
        matched_rows = df[df['File'] == file_name]
        if not matched_rows.empty:
            # 遍历匹配的行，检查代码范围是否有交集
            for index, row in matched_rows.iterrows():
                # 假设没有代码范围信息，直接根据bug_flag更新
                df.loc[index, 'Bug'] = info['bug_flag']

    # 将更新后的数据写回Excel文件
    try:
        with pd.ExcelWriter(excel_path, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        print(f"Excel文件已更新：{excel_path}")
    except Exception as e:
        print(f"写入Excel文件失败：{e}")

def get_versions(directory):
    versions = []
    for file_name in os.listdir(directory):
        if file_name.endswith('_commit.xml'):
            new_file_name = file_name.replace('_commit.xml', '')
            versions.append(new_file_name)
    return versions

import pandas as pd

def merge_all_sheets(excel_path):
    all_data = pd.DataFrame()
    try:
        xls = pd.ExcelFile(excel_path)
        sheet_names = xls.sheet_names
        for sheet_name in sheet_names:
            df = xls.parse(sheet_name)
            if 'File' in df.columns:
                df = df[df['File'].str.endswith(('.h', '.c', '.cpp', '.hpp', '.cc'))]
            all_data = pd.concat([all_data, df], ignore_index=True)
    except FileNotFoundError:
        print(f"The file {excel_path} does not exist.")
    return all_data

def merge():
    input_path = 'Results/autoware_result.xlsx'
    merged_output_path = 'Results/apollo_merged.xlsx'

    # 合并所有工作表的数据
    merged_data = merge_all_sheets(input_path)
    if not merged_data.empty:
        # 保存合并后的数据
        merged_data.to_excel(merged_output_path, index=False)
        print(f"Merged data saved to {merged_output_path}")


def main():
    directory = input("please input your root directory: ")
    excel_path = input("please input your output_file directory: ")
    # example input:
    # directory = 'all_commit/autoware'
    # excel_path = 'Results/autoware_result.xlsx'
    versions = get_versions(directory)
    print(versions)
    for version in versions:
        parts = version.split("_")
        sheet_name = parts[0] + "-" + parts[1]
        # 遍历目录，找到对应的XML文件
        for file_name in os.listdir(directory):
            if file_name == f"{version}_commit.xml":
                file_path = os.path.join(directory, file_name)
                bug_info = extract_diff_lines(file_path)
                print(f"Parsed {file_path} for version {sheet_name}")
                lable(excel_path, bug_info, sheet_name)

    merge()