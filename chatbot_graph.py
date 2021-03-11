from question_classifier import *
from question_parser import *
from answer_search import *

'''将以上三个模块的所有内容导入到当前命名空间'''

class ChatBotGraph:
    def __init__(self):
        self.classifier = QuestionClassifier()  # 创建 问题分类 对象 classifier
        self.parser = QuestionParser()          # 创建 问题解析 对象 parser
        self.searcher = AnswerSearcher()        # 创建 问题查询 对象 searcher

    def chat_main(self, sent):
        answer = '没能理解您的问题，我数据量有限。。。能不能问的标准点'
        res_classify = self.classifier.classify(sent)
        if not res_classify:
            return answer
        res_sql = self.parser.parser_main(res_classify)
        final_answers = self.searcher.search_main(res_sql)
        if not final_answers:
            return answer
        else:
            return '\n'.join(final_answers)


if __name__ == '__main__':
    handler = ChatBotGraph()
    while 1:
        question = input('咨询:')               # 输入要查询的问题
        answer = handler.chat_main(question)    # 进行查询
        print('客服机器人:', answer)             # 输出查询结果

