import xml.dom.minidom as minidom


def write_to_xml(clone_list, save_name):
    dom = minidom.getDOMImplementation().createDocument(None, 'Root', None)     # 创建树
    root = dom.documentElement  # 创建root节点

    i = 0
    for clones in clone_list:   # 遍历克隆函数列表
        root_element = dom.createElement('dup' + str(i))    # 克隆对的父节点
        for clone in clones:
            element = dom.createElement('source')   # 克隆函数的节点
            text_element = dom.createElement('code')    # 函数代码信息的节点
            text_element.setAttribute('function_name', clone['function'][3])    # 函数名
            text_element.appendChild(dom.createTextNode(clone['function'][2]))  # 函数代码
            element.appendChild(text_element)   # 将函数代码信息的节点添加到克隆函数节点上
            element.setAttribute('sourseFile', clone['sourseFile'])     # 文件路径
            element.setAttribute('startLine', str(clone['function'][0]))    # 函数开始行号以及列号
            element.setAttribute('endLine', str(clone['function'][1]))  # 函数结束行号以及列号
            root_element.appendChild(element)   # 将函数信息节点添加到克隆对父节点上
        root_element.setAttribute('count', str(len(clones)))    # 该克隆对中涉及的函数总数
        root.appendChild(root_element)  # 将克隆对信息节点添加到文档父节点上
        i += 1
    summary_element = dom.createElement('summary')  # 总结节点
    summary_element.setAttribute("count", str(len(clone_list)))     # 克隆对总数
    root.appendChild(summary_element)   # 将总结节点添加到文档父节点上
    # 保存文件
    with open(save_name, 'w', encoding='utf-8') as f:
        dom.writexml(f, addindent='\t', newl='\n', encoding='utf-8')


if __name__ == '__main__':
    function_code = '''
        template <typename T>
        bool UDPBridgeSenderComponent<T>::Proc(const std::shared_ptr<T> &pb_msg) {
          if (remote_port_ == 0 || remote_ip_.empty()) {
            AERROR << "remote info is invalid!";
            return false;
          }

          if (pb_msg == nullptr) {
            AERROR << "proto msg is not ready!";
            return false;
          }
        '''
    function = [(1, 2), (3, 4), function_code, 'function_name']
    clone_list = [
        [
            {
                'sourseFile': r'D:\download\apollo-master-1\apollo-master\modules\localization\msf\local_pyramid_map\base_map\base_map.cpp',
                'function': function},
            {
                'sourseFile': r'D:\download\apollo-master-1\apollo-master\modules\localization\msf\local_pyramid_map\base_map\base_map.cpp',
                'function': function}
        ],
        [
            {
                'sourseFile': r'D:\download\apollo-master-1\apollo-master\modules\perception\lidar\lib\object_filter_bank\object_filter_bank.cpp',
                'function': function},
            {
                'sourseFile': r'D:\download\apollo-master-1\apollo-master\modules\perception\lidar\lib\object_filter_bank\object_filter_bank.cpp',
                'function': function},
        ]
    ]
    write_to_xml(clone_list, 'function.xml')
