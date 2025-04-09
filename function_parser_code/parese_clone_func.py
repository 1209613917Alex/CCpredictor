import os
from xml.dom.minidom import parse
import chardet
from tree_sitter_parser.tree_sitter_parser import TreeSitterParser
from xml.dom.minidom import parseString

def func_parse(codes):
    tree_sitter_parser = TreeSitterParser()
    tree_sitter_parser.functions = []
    tree_sitter_parser.tree_parser(codes)
    return tree_sitter_parser.functions

def read_cpp(cpp_adr):
    try:
        with open(cpp_adr, 'rb') as f:
            data = f.read()
            encoding = chardet.detect(data)['encoding']
        if encoding is None:
            encoding = 'utf-8'
        with open(cpp_adr, encoding=encoding) as f:
            codes = f.read()
            return codes
    except UnicodeDecodeError as e:
        print(f"Decode error with encoding {encoding}, trying 'utf-8' instead.")
        with open(cpp_adr, encoding='utf-8') as f:
            codes = f.read()
            return codes
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def xml_read(xml_name):
    file_functions = {}
    DOMTree = parse(xml_name)
    collection = DOMTree.documentElement
    if collection.hasAttribute("version"):
        print("Root element : %s" % collection.getAttribute("version"))

    dups_func_list = []
    dups = collection.getElementsByTagName("set")
    print("************duplications*************")
    i = 0
    for dup in dups:
        print("*****duplication" + str(i) + "*****")
        blocks = dup.getElementsByTagName('block')
        j = 0
        clone_funcs_list = []
        for block in blocks:
            print("dup" + str(j) + "读取中")
            sourceFile = block.getAttribute("sourceFile")
            sourceFile_cc = block.getAttribute("sourceFile").replace(".cpp", ".cc")
            functions = []
            if not os.path.exists(sourceFile):
                sourceFile = sourceFile_cc
            if not os.path.exists(sourceFile) and not os.path.exists(sourceFile_cc):
                print("the file didn't match:", sourceFile)
                continue
            if not file_functions.get(sourceFile):
                codes = read_cpp(sourceFile)
                functions = func_parse(codes)
                file_functions[sourceFile] = functions
            else:
                functions = file_functions.get(sourceFile)
            startLineNumber = int(block.getAttribute("startLineNumber"))
            endLineNumber = int(block.getAttribute("endLineNumber"))
            clone_functions = []
            k = 0
            for function in functions:
                end = int(function[1][0]) + 1
                if end > startLineNumber:
                    start = int(function[0][0]) + 1
                    if endLineNumber < start:
                        break
                    if endLineNumber < end:
                        end = endLineNumber - start + 1
                    else:
                        end = end - start + 1
                    if startLineNumber - start > 0:
                        start = startLineNumber - start + 1
                    else:
                        start = 1
                    k = functions.index(function)
                    clone_functions.append({'function_info': function, 'start': start, 'end': end})
                    break
            if not len(clone_functions) > 0:
                break
            for function in functions[k + 1:]:
                end = int(function[1][0]) + 1
                start = int(function[0][0]) + 1
                if end <= endLineNumber:
                    clone_functions.append({'function_info': function, 'start': 1, 'end': end - start + 1})
                elif start <= endLineNumber:
                    clone_functions.append({'function_info': function, 'start': 1, 'end': endLineNumber - start + 1})
                    break
                else:
                    break
            j += 1
            if len(clone_functions) > 0:
                clone_funcs_list.append({'sourceFile': sourceFile, 'functions': clone_functions})
        i += 1
        if len(clone_funcs_list) > 1:
            dups_func_list.append(clone_funcs_list)
    return dups_func_list

def clone_func_generate(xml_name):
    dups_func_list = xml_read(xml_name)
    dups_func_info_list = []
    for clone_funcs_list in dups_func_list:
        count = len(min(clone_funcs_list, key=lambda x: len(x.get('functions'))).get('functions'))
        for i in range(count):
            clone_func_info_list = []
            for clone_funcs in clone_funcs_list:
                sourceFile = clone_funcs.get('sourceFile')
                function = clone_funcs.get('functions')[i]
                clone_func_info_list.append({'sourceFile': sourceFile, 'function': function})
            dups_func_info_list.append(clone_func_info_list)
    return dups_func_info_list

def write_in_xml(dups_func_info_list, save_name):
    dom = parseString('<Func_Clone></Func_Clone>')
    root = dom.documentElement

    for clones in dups_func_info_list:
        root_element = dom.createElement('dup')
        for clone in clones:
            element = dom.createElement('source')
            text_element = dom.createElement('code')
            text_element.setAttribute('function_name', clone['function']['function_info'][3])
            text_element.appendChild(dom.createTextNode(clone['function']['function_info'][2]))
            element.appendChild(text_element)
            element.setAttribute('sourceFile', clone['sourceFile'])
            element.setAttribute('startLine', str(clone['function']['function_info'][0]))
            element.setAttribute('endLine', str(clone['function']['function_info'][1]))
            element.setAttribute('clone_start', str(clone['function']['start']))
            element.setAttribute('clone_end', str(clone['function']['end']))
            root_element.appendChild(element)
        root_element.setAttribute('count', str(len(clones)))
        root.appendChild(root_element)
    summary_element = dom.createElement('summary')
    summary_element.setAttribute("count", str(len(dups_func_info_list)))
    root.appendChild(summary_element)
    with open(save_name, 'w', encoding='utf-8') as f:
        f.write(dom.toprettyxml(indent='\t'))

def process_all_versions(xml_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(xml_dir):
        if filename.endswith("-dup.xml"):
            xml_path = os.path.join(xml_dir, filename)
            output_path = os.path.join(output_dir, filename.replace("-dup.xml", "-dup-func.xml"))
            dups_func_info_list = clone_func_generate(xml_path)
            write_in_xml(dups_func_info_list, output_path)
            print(f"Processed {filename} and saved results to {output_path}")

if __name__ == "__main__":
    xml_dir = "../clone_xml/autoware"
    output_dir = "../clone_xml/autoware_func_cc"
    process_all_versions(xml_dir, output_dir)