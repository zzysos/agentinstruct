import os
import json
import re;
from queue import Queue
from src.agentinstruct.agent.agent_instr_generation import *
from langchain.prompts import  ChatPromptTemplate
from langchain.chat_models import ChatOpenAI

Data_Path='../mydataset'

openai_api_key='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'

def boolQ_metric(input_string):
    # 将输入字符串转换为小写，以便不区分大小写
    lowercase_string = input_string.lower()
    # 检查字符串中是否包含 'no'
    if 'no' in lowercase_string or 'false' in lowercase_string:
        return False
    elif 'yes' in lowercase_string or 'true' in lowercase_string:
        return True
    return input_string
class BoolQ():
    """


    """
    def __init__(self,file='boolQ.jsonl'):
        self.dataset_name='BoolQ'
        self.dataset_phrase='The dataset name is BoolQ'
        self.instance_format=(f"(1).\nPassage:Phantom pain sensations are described as perceptions that an individual experiences relating to a limb or an organ that is not physically part of the body. Limb loss is a result of either removal by amputation or congenital limb deficiency. However, phantom limb sensations can also occur following nerve avulsion or spinal cord injury.\n"+
                              "Question:is pain experienced in a missing body part or paralyzed area\n"+
                              "(2).\nPassage:Barq's /ˈbɑːrks/ is an American soft drink. Its brand of root beer is notable for having caffeine. Barq's, created by Edward Barq and bottled since the turn of the 20th century, is owned by the Barq family but bottled by the Coca-Cola Company. It was known as Barq's Famous Olde Tyme Root Beer until 2012.\n"+
                              "Question:is barq's root beer a pepsi product")
        self.possible_outputs='[true/false or yes/no]'
        self.instruction=''
        self.path=os.path.join(Data_Path,file)
        self.data=[]
        with open(self.path, 'r',encoding='utf-8') as file:
            all_triplets = list(file)
            for item in all_triplets:
                triplet = json.loads(item)
                self.data.append(triplet)

    def __len__(self)->int:
        return len(self.data)

    def test_data(self):
        print (self.data[0]["question"])


    def generate_instr(self):
        dict={}
        self.instruction,dict,agent=generate_and_save_instructions(dataset_name=self.dataset_name,dataset_phrase=self.dataset_phrase,instance_format=self.instance_format,possible_outputs=self.possible_outputs,sources_dict=dict)
        file_path='../instructions/myinstructions/boolQ_instr.txt'
        with open(file_path, "w") as file:
            file.write(self.instruction)
        # print(dict[self.dataset_name]['input_prompt'])
        # print(dict[self.dataset_name]['intermediate_steps'])
        return agent

    #原始方法
    def run(self):
        file_path = '../instructions/myinstructions/boolQ_instr.txt'
        with open(file_path, "r") as file:
            self.instruction = file.read()

        if (self.instruction == ""):
            print("新生成instruction")
            agent = self.generate_instr()

        print(self.instruction)


        cot_prompt=(f"You will be provided instructions for completing a task followed by a task to complete.\n"+"instructions:\n"+
        "{instructions}\n"+"The passage and question will be presented below:\n"+"Passage:{Passage}\n"+"Question:{Question}\n"+"Then you need to follow the provided instructions to generate an explanation that reasons towards the correct answer to the task above." +
        "End the explanation with the correct answer.The final answer needs to be presented on the last line and follow the format:Answer:[your answer]."+
        "Be careful not to add spaces between : and [your answer]")

        promp_template=ChatPromptTemplate.from_template(cot_prompt)

        chat = ChatOpenAI(temperature=0.0,openai_api_key=openai_api_key)

        count=0
        sucess=0
        for entry in self.data:
            count = count + 1
            passage=entry["passage"].strip()
            question = entry["question"].strip()
            answer=str(entry["answer"])

            msg = promp_template.format_messages(instructions=self.instruction, Question=question,Passage=passage)

            response=chat(msg)
            content=response.content
            '''处理结果格式'''
            lines = content.splitlines()
            last_line = lines[-1]
            result = last_line.split(':')[-1].strip()
            result=str(boolQ_metric(result))
            # print(str(count) + '. result:' + result + " " + 'answer:' + answer + " " + str(result==answer))
            if (result == answer):
                sucess=sucess+1

            if(count>=200):
                break

        print("准确率:", sucess / count)

    # 加入反思
    def run_with_reflexion(self):
        file_path = '../instructions/myinstructions/boolQ_instr.txt'
        with open(file_path, "r") as file:
            self.instruction=file.read()

        if(self.instruction==""):
            print("新生成instruction")
            agent=self.generate_instr()

        print(self.instruction)

        cot_prompt=(f"You will be provided instructions for completing a task followed by a task to complete.\n"+"instructions:\n"+
        "{instructions}\n"+"And these are some experiences based on your previous mistakes, and you need to refer to these experiences to better complete the task:\n"+
        "{reflexions}"
        +"The passage and question will be presented below:\n"+"Passage:{Passage}\n"+"Question:{Question}\n"+"Then you need to follow the provided instructions to generate an explanation that reasons towards the correct answer to the task above." +
        "End the explanation with the correct answer.The final answer needs to be presented on the last line and follow the format:Answer:[your answer]."+
        "Be careful not to add spaces between : and [your answer]")

        reflexion_prompt=(f"You will be provided some information of a task and one execution process of the task."+
                          "But the result obtained from this execution process is incorrect"+
                          "You need to analyze the reasons for the error in this execution process based on the provided information and summarize the experiences that can guide the next tasks.Try to use general language to obtain a universal method and summarize it in two to three sentences.\n"+
                          "Here is overall task description:\n"+"Task name:{task_name}\n"+"Some input instance:\n{input_instance}\n"+"Possible output:{possible_output}\n"+
                          "Here is the information for this task:\n"+"Passage:{Passage}\n"+"Question:{Question}\n"+
                          "The execution process:\n"+"{process}\n"+"The final answer to the above process:{result}\n"+"The correct answer:{answer}\n"+
                          "Give your analysis on the last line and follow the format:analysis:[your analysis]")

        promp_template=ChatPromptTemplate.from_template(cot_prompt)
        reflexion_template=ChatPromptTemplate.from_template(reflexion_prompt)

        chat = ChatOpenAI(model='gpt-3.5-turbo-0613',temperature=0.0,openai_api_key=openai_api_key)
        #反思存储队列
        reflexions_queue=Queue()
        count=0
        sucess=0
        for entry in self.data:
            count = count + 1
            passage=entry["passage"].strip()
            question = entry["question"].strip()
            answer=str(entry["answer"])
            n=1
            re_str=""
            for refletion in reflexions_queue.queue:
                re_str+=str(n)+"."+refletion+"\n"
                n=n+1

            msg = promp_template.format_messages(instructions=self.instruction, Question=question,Passage=passage,reflexions=re_str)

            response=chat(msg)
            content=response.content
            '''处理结果格式'''
            lines = content.splitlines()
            last_line = lines[-1]
            result = last_line.split(':')[-1].strip()
            result=str(boolQ_metric(result))
            # print(str(count) + '. result:' + result + " " + 'answer:' + answer + " " + str(result==answer))
            if (result == answer):
                sucess=sucess+1
            else:
            #出现错误，加入reflexion， model='gpt-4-0613',
                reflect_llm = ChatOpenAI(model='gpt-4-0613',temperature=0.0, openai_api_key=openai_api_key)
                reflect_msg=reflexion_template.format_messages(task_name=self.dataset_name,input_instance=self.instance_format,possible_output=self.possible_outputs,Question=question,Passage=passage,process=content,result=result,answer=answer)
                re_content=reflect_llm(reflect_msg).content
                re_lines=re_content.splitlines()
                re_last_line=re_lines[-1]
                reflexion=re_last_line.split(':')[-1].strip()
                print("新的反思："+reflexion)
                reflexions_queue.put(reflexion)
                #反思队列最大容量为8
                if len(reflexions_queue.queue)>8:
                    reflexions_queue.get()

            if(count>=200):
                break

        print("准确率:", sucess / count)



boolq=BoolQ()
boolq.run_with_reflexion()
