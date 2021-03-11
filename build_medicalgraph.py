import os
import json
from py2neo import Graph, Node


class MedicalGraph:
    def __init__(self):
        cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])  # os.path.abspath(__file__)命令是获取的当前执行脚本的完整路径 ，join() 方法用于将序列中的元素以指定的字符连接生成一个新的字符串。
        self.data_path = os.path.join(cur_dir, 'data/medical2.json')  # 从倒数第一个，以‘/’开头的参数开始拼接，之前的参数全部丢弃。
        self.g = Graph("http://localhost:7474", username="neo4j", password="@")

    '''读取文件'''
    def read_nodes(self):  # 使用一个 for 循环将 json 文件中数据一行一行读入， 通过一次性调用本函数可以将将 json 文件中的数据全部读入
        # 共７类节点
        drugs = []  # 药品
        foods = []  # 食物
        checks = []  # 检查
        departments = []  # 科室
        producers = []  # 药品大类
        diseases = []  # 疾病
        symptoms = []  # 症状

        disease_infos = []  # 疾病信息

        # 构建节点实体关系
        rels_department = []  # 科室－科室关系
        rels_noteat = []  # 疾病－忌吃食物关系
        rels_doeat = []  # 疾病－宜吃食物关系
        rels_recommandeat = []  # 疾病－推荐吃食物关系
        rels_commonddrug = []  # 疾病－通用药品关系
        rels_recommanddrug = []  # 疾病－热门药品关系
        rels_check = []  # 疾病－检查关系
        rels_drug_producer = []  # 厂商－药物关系

        rels_symptom = []  # 疾病症状关系
        rels_acompany = []  # 疾病并发关系
        rels_category = []  #　疾病与科室之间的关系


        count = 0
        for data in open(self.data_path, encoding="utf-8"):
            disease_dict = {}  # disease_dict字典中的内容是关于一种病的所有信息，最后作为一个整体元素添加到 disease_info 列表中；每开始一次循环 diseases_dict 都会进行清空初始化。
            count += 1  # 统计疾病种数
            print(count)
            data_json = json.loads(data)  # 这个data是一条json数据，通过loads函数将data中的键值对分离。可以理解为是将json数据格式转化为字典（也是由键值对组成）
            disease = data_json['name']  # 从字典data_json中取出字段名称为name的值赋给disease
            disease_dict['name'] = disease  # 填充字典disease_dict中name字段
            diseases.append(disease)  # 疾病名称填入diseases列表尾部
            disease_dict['desc'] = ''  # 声明字典disease_dict中 desc 字段，等待填充
            disease_dict['prevent'] = ''
            disease_dict['cause'] = ''
            disease_dict['easy_get'] = ''
            disease_dict['cure_department'] = ''
            disease_dict['cure_way'] = ''
            disease_dict['cure_lasttime'] = ''
            disease_dict['symptom'] = ''
            disease_dict['cured_prob'] = ''

            ''' if语句对 data_json 中相关字段是否存在进行判断是为了在赋值给 disease_dict{} 对应字段的时候确保字段存在
                结果就是 disease_dict 中的字段是 data_json 中字段的子集， disease_dict 中的字段都是我们关心的字段'''

            if 'symptom' in data_json:
                symptoms += data_json['symptom']  # 对于每一种疾病的症状分批次收录到列表symptoms中
                for symptom in data_json['symptom']:
                    rels_symptom.append([disease, symptom])  # rels_symptom[] 疾病症状关系 创建一种疾病多种症状的数组长度为2的列表

            if 'acompany' in data_json:
                for acompany in data_json['acompany']:
                    rels_acompany.append([disease, acompany])  # rels_acompany[] 在疾病和并发症之间建立关系 将疾病和其对应的每一个并发症生成长度为2的数组填充到列表中

            if 'desc' in data_json:
                disease_dict['desc'] = data_json['desc']

            if 'prevent' in data_json:
                disease_dict['prevent'] = data_json['prevent']

            if 'cause' in data_json:
                disease_dict['cause'] = data_json['cause']

            if 'get_prob' in data_json:
                disease_dict['get_prob'] = data_json['get_prob']

            if 'easy_get' in data_json:
                disease_dict['easy_get'] = data_json['easy_get']

            if 'cure_department' in data_json:
                cure_department = data_json['cure_department']  # 取出cure_department字段下的值赋给cure_department
                if len(cure_department) == 1:  # 如果相关治疗科室没有下辖
                    rels_category.append([disease, cure_department[0]])  # 疾病与科室之间构成的二元列表作为元素添加到rels_category()列表中
                if len(cure_department) == 2:  # 如果相关治疗科室有下辖分支
                    big = cure_department[0]
                    small = cure_department[1]
                    rels_department.append([small, big])  # 将科室与其下辖分支构成的二元列表作为元素添加到rels_department()列表中，构建部门与部门之间关系
                    rels_category.append([disease, small])  # 疾病与具体科室分支之间构成的二元列表作为元素添加到rels_category()列表中； 建构具体科室与疾病之间的关系

                ''' 以此为界:
                    以上是建立 cure_department 中科室上下级关系、疾病与科室之间的关系
                    以下是在 disease_dict 列表已经声明好的字段中填入各种值 '''

                disease_dict['cure_department'] = cure_department
                departments += cure_department # departments（列表）在此处被定义并被赋值 

            if 'cure_way' in data_json:
                disease_dict['cure_way'] = data_json['cure_way']

            if  'cure_lasttime' in data_json:
                disease_dict['cure_lasttime'] = data_json['cure_lasttime']

            if 'cured_prob' in data_json:
                disease_dict['cured_prob'] = data_json['cured_prob']

            if 'common_drug' in data_json:
                common_drug = data_json['common_drug']  # 并不是 data_json 中相关的字段都放到 disease_dict 对应字段中，有的直接赋值给初定义列表 。json文件中第一条的 '肺泡蛋白质沉积症' 并不存在 common_drug 所以这个 if 之后的代码就没有执行
                for drug in common_drug:
                    rels_commonddrug.append([disease, drug])
                drugs += common_drug

            if 'recommand_drug' in data_json:
                recommand_drug = data_json['recommand_drug']
                drugs += recommand_drug
                for drug in recommand_drug:
                    rels_recommanddrug.append([disease, drug])

            if 'not_eat' in data_json:
                not_eat = data_json['not_eat']
                for _not in not_eat:
                    rels_noteat.append([disease, _not])  # 建立疾病与忌食之间的关系列表

                foods += not_eat
                do_eat = data_json['do_eat']
                for _do in do_eat:
                    rels_doeat.append([disease, _do])

                foods += do_eat
                recommand_eat = data_json['recommand_eat']

                for _recommand in recommand_eat:
                    rels_recommandeat.append([disease, _recommand])
                foods += recommand_eat

            if 'check' in data_json:
                check = data_json['check']
                for _check in check:
                    rels_check.append([disease, _check])
                checks += check
            if 'drug_detail' in data_json:
                drug_detail = data_json['drug_detail']  # producer(drug) ~ 福森双黄连(双黄连)
                producer = [i.split('(')[0] for i in drug_detail]  # 使用 split 函数提取出 producer（生产厂商）； split()[n]中的 n 指的是取切片的位置 ; n = -1 代表所有分片的倒数第一个位置
                rels_drug_producer += [[i.split('(')[0], i.split('(')[-1].replace(')', '')] for i in drug_detail]
                producers += producer
            
            '''最后将 disease_dict 字典中的内容放置到 disease_info 列表中, 通过 return disease_info 整体返回'''
            disease_infos.append(disease_dict)  # 把疾病字典放入disease_info列表中
            
            '''set()汇总去重，删除列表中多余的数据'''
        return set(drugs), set(foods), set(checks), set(departments), set(producers), set(symptoms), set(diseases), disease_infos,\
               rels_check, rels_recommandeat, rels_noteat, rels_doeat, rels_department, rels_commonddrug, rels_drug_producer, \
               rels_recommanddrug,rels_symptom, rels_acompany, rels_category

    '''建立节点'''
    def create_node(self, label, nodes):
        count = 0  # 统计相关节点个数，可能的方面有 drug，food，check，department，
        for node_name in nodes:
            node = Node(label, name=node_name)
            self.g.create(node)
            count += 1
            print(count, len(nodes))  # len(nodes)从一开始就已经固定不会随着程序运行而改变，比如 drug 的 nodes 长度 len() 从一开始就是 88
        return

    '''创建以疾病为中心的知识图谱结点'''
    def create_diseases_nodes(self, disease_infos):
        count = 0
        for disease_dict in disease_infos:  # 再将 disease_info 中作为元素的 disease_dict 字典依次取出
            node = Node("Disease", name=disease_dict['name'], desc=disease_dict['desc'],
                        prevent=disease_dict['prevent'] ,cause=disease_dict['cause'],
                        easy_get=disease_dict['easy_get'],cure_lasttime=disease_dict['cure_lasttime'],
                        cure_department=disease_dict['cure_department'],
                        cure_way=disease_dict['cure_way'] , cured_prob=disease_dict['cured_prob'])
            self.g.create(node)
            count += 1
            print(count)
        return

    '''创建知识图谱实体节点类型'''
    def create_graphnodes(self):
        Drugs, Foods, Checks, Departments, Producers, Symptoms, Diseases, disease_infos,rels_check, rels_recommandeat, rels_noteat, rels_doeat, rels_department, rels_commonddrug, rels_drug_producer, rels_recommanddrug,rels_symptom, rels_acompany, rels_category = self.read_nodes()
        self.create_diseases_nodes(disease_infos)  # 以疾病属性的不同方向作为划分创建节点
        self.create_node('Drug', Drugs)
        print(len(Drugs))  # 数据中一共涉及 88 种药物
        self.create_node('Food', Foods)
        print(len(Foods))
        self.create_node('Check', Checks)
        print(len(Checks))
        self.create_node('Department', Departments)
        print(len(Departments))
        self.create_node('Producer', Producers)
        print(len(Producers))
        self.create_node('Symptom', Symptoms)
        return

    '''创建实体关系边'''
    def create_graphrels(self):
        Drugs, Foods, Checks, Departments, Producers, Symptoms, Diseases, disease_infos, rels_check, rels_recommandeat, rels_noteat, rels_doeat, rels_department, rels_commonddrug, rels_drug_producer, rels_recommanddrug,rels_symptom, rels_acompany, rels_category = self.read_nodes()
        self.create_relationship('Disease', 'Food', rels_recommandeat, 'recommand_eat', '推荐食谱')
        self.create_relationship('Disease', 'Food', rels_noteat, 'no_eat', '忌吃')
        self.create_relationship('Disease', 'Food', rels_doeat, 'do_eat', '宜吃')
        self.create_relationship('Department', 'Department', rels_department, 'belongs_to', '属于')
        self.create_relationship('Disease', 'Drug', rels_commonddrug, 'common_drug', '常用药品')
        self.create_relationship('Producer', 'Drug', rels_drug_producer, 'drugs_of', '生产药品')
        self.create_relationship('Disease', 'Drug', rels_recommanddrug, 'recommand_drug', '好评药品')
        self.create_relationship('Disease', 'Check', rels_check, 'need_check', '诊断检查')
        self.create_relationship('Disease', 'Symptom', rels_symptom, 'has_symptom', '症状')
        self.create_relationship('Disease', 'Disease', rels_acompany, 'acompany_with', '并发症')
        self.create_relationship('Disease', 'Department', rels_category, 'belongs_to', '所属科室')

    '''创建实体关联边'''
    def create_relationship(self, start_node, end_node, edges, rel_type, rel_name):
        count = 0
        # 去重处理
        set_edges = []  # 
        for edge in edges:
            set_edges.append('###'.join(edge))
        all = len(set(set_edges))
        for edge in set(set_edges):
            edge = edge.split('###')
            p = edge[0]
            q = edge[1]
            query = "match(p:%s),(q:%s) where p.name='%s'and q.name='%s' create (p)-[rel:%s{name:'%s'}]->(q)" % (start_node, end_node, p, q, rel_type, rel_name)
            try:
                self.g.run(query)
                count += 1
                print(rel_type, count, all)
            except Exception as e:
                print(e)
        return

    '''导出数据'''
    def export_data(self):
        Drugs, Foods, Checks, Departments, Producers, Symptoms, Diseases, disease_infos, rels_check, rels_recommandeat, rels_noteat, rels_doeat, rels_department, rels_commonddrug, rels_drug_producer, rels_recommanddrug, rels_symptom, rels_acompany, rels_category = self.read_nodes()
        f_drug = open('drug.txt', 'w+')  # w+: 可读可写，若文件不存在，创建
        f_food = open('food.txt', 'w+')
        f_check = open('check.txt', 'w+')
        f_department = open('department.txt', 'w+')
        f_producer = open('producer.txt', 'w+')
        f_symptom = open('symptoms.txt', 'w+')
        f_disease = open('disease.txt', 'w+')

        f_drug.write('\n'.join(list(Drugs)))
        f_food.write('\n'.join(list(Foods)))
        f_check.write('\n'.join(list(Checks)))
        f_department.write('\n'.join(list(Departments)))
        f_producer.write('\n'.join(list(Producers)))
        f_symptom.write('\n'.join(list(Symptoms)))
        f_disease.write('\n'.join(list(Diseases)))

        f_drug.close()
        f_food.close()
        f_check.close()
        f_department.close()
        f_producer.close()
        f_symptom.close()
        f_disease.close()
        return

    
        
    
if __name__ == '__main__':
    handler = MedicalGraph()
    #handler.export_data()
    handler.create_graphnodes()
    handler.create_graphrels()
