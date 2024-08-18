from langchain_community.document_loaders import CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.prompts.few_shot import FewShotPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.chains import RetrievalQA
from langchain_together import Together
from langchain.chains import LLMChain
import pprint
import os


class FloodsQASystem:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.docs = self.load_csv_data()

        texts, data = self.preprocess_data()

        self.setup_openai_api_key()

        self.embeddings = self.create_embeddings()

        self.vector_index = self.create_vector_index(texts)

        self.store = self.create_store(data)
        self.persist_store()
        
        self.qa_with_source = self.create_qa_chain()

        self.llm_chain = self.create_llm_chain()
        self.llm_chain_integrated=self.llm_chain_together()

    def setup_openai_api_key(self):
        # OPENAI_API_KEY = getpass("Enter your OpenAI API Key: ")
        OPENAI_API_KEY = ''
        os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
        

    def load_csv_data(self):
        loader1 = CSVLoader(file_path=self.folder_path+"/"+"natural_disasters2.csv")
        loader2 = CSVLoader(file_path=self.folder_path+"/"+"new_data.csv")
        loader=loader1.load()+loader2.load()
        return loader
    
    #def load_pdf_data(self):
        #loader = PyPDFDirectoryLoader(self.folder_path)
        #return loader.load()
        
    def preprocess_data(self):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=0)
        context = "\n\n".join(str(p.page_content) for p in self.docs)
        texts = text_splitter.split_text(context)
        data = text_splitter.split_documents(self.docs)
        return texts, data

    def create_embeddings(self):
        return OpenAIEmbeddings()

    def create_vector_index(self, texts):
        return Chroma.from_texts(texts, self.embeddings).as_retriever()

    def create_store(self, data):
        return Chroma.from_documents(
            data,
            self.embeddings,
            ids=[f"{item.metadata['source']}-{index}" for index, item in enumerate(data)],
            collection_name="Floods",
            persist_directory='data/',
        )

    def persist_store(self):
        self.store.persist()

    def create_prompt_template(self, template, input_variables):
        return PromptTemplate(template=template, input_variables=input_variables)

    def create_qa_chain(self):
        template = """You are a bot that answers questions about natural disasters: 
        floods,earthquakes,landslides and cyclones using only the context provided.
        The context provided is from a wikipedia page on natural disasters in 
        India which contains information about all the natural disasters.
        If you don't know the answer, simply state that you don't know.

        {context}

        Question: {question}"""

        PROMPT = self.create_prompt_template(
            template=template, input_variables=["context", "question"]
        )

        llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0125")

        return RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.store.as_retriever(),
            chain_type_kwargs={"prompt":PROMPT,"verbose":False},
            return_source_documents=False,
        )

    def create_chat_openai(self, temperature, model):
        return ChatOpenAI(temperature=temperature, model=model)    
    
    def llm_chain_together(self):
        
        examples = [
        {"chat_history":"query: Tell me about the natural disasters in Uttarakhand ?\nresponse: In Uttarakhand, natural disasters such as floods and landslides have occurred due to various factors such as glacier bursts, heavy rainfall, and avalanches. The 2021 Uttarakhand floods were caused by a glacier burst and heavy rainfall in the Chamoli district, leading to massive flooding along the Alaknanda and Dhauliganga rivers. The flash floods damaged hydropower projects, resulted in over 200 deaths, and caused significant damage to infrastructure. Similarly, the June 2013 North Indian floods were triggered by heavy monsoon rainfall that destabilized mountain slopes, leading to landslides and flooding in areas like Kedarnath. These disasters highlighted the vulnerabilities of the Himalayan region to extreme weather events linked to climate change.","follow_up_query":"Have any landslides occured there? " ,"standalone_question": "Have any landslides occured in Uttarakhand?"},
        {"chat_history":"query: When did the Gujarat earthquake occur ?\nresponse: Gujarat earthquake occured on January 26, 2001.","follow_up_query":"What was its magnitude?", "standalone_question": "What was the magnitude of Gujarat earthquake of 26 January, 2001?"},
        {"chat_history":"query: What can you do?\nresponse: I can provide information and answer questions about natural disasters such as floods, earthquakes, landslides, and cyclones based on the context provided from the Wikipedia page on natural disasters in India. If you have any specific questions about floods in India, feel free to ask!","follow_up_query": "Okay","standalone_question":"Tell me about natural disasters in India."}
        ]
        example_prompt = PromptTemplate(template="Chat History: [{chat_history}]\nFollow Up Query: {follow_up_query}\nStandalone question: {standalone_question}",input_variables=["chat_history","follow_up_query","standalone_question"])

        few_shot_prompt = FewShotPromptTemplate(
        examples=examples,
        example_prompt=example_prompt,
        prefix="""You are a helpful assistant whose task is to write standalone question.
            You have been provided with chat history and follow up query of user.
            You need to rephrase the given follow up query by using the context of chat history. 
            Provide standalone question only.Do not write any other text.""",
        suffix="Chat History:[{chat_history}]\nFollow Up Query: {follow_up_query}\nStandalone question:",
        input_variables=["chat_history","follow_up_query"]
        )
        
        llm_summarize = Together(
        model="Qwen/Qwen1.5-72B-Chat",
        top_k=50,
        top_p=1,
        temperature=0,
        together_api_key="7294b9c3f54b31ac6a9a7a1c6e36e42fc1ee2675e848300500c7127ba3ce5229"
        )
        LLMChain(llm=llm_summarize,prompt=few_shot_prompt)
        
        return LLMChain(llm=llm_summarize, prompt=few_shot_prompt)
        
    
    def create_llm_chain(self):
        template_summarize = """"Given the following conversation and a follow-up question, rephrase the follow-up question to be a standalone 
        question. The question should contain as much information as possible about the context.
    
        Chat History:
        {chat_history}
        Follow Up Input: {query}
        Standalone question:
        """
        prompt_summarize = self.create_prompt_template(
            template=template_summarize, input_variables=["chat_history", "query"]
        )

        llm_summarize = self.create_chat_openai(
            temperature=0, model="gpt-3.5-turbo-0125"
        )

        return LLMChain(llm=llm_summarize, prompt=prompt_summarize)
    
    def answer_question(self, ques, history):
        if not history:
            response = self.qa_with_source.invoke({'query':ques})
        else:
            last_entries = list(history.values())[-5:]
            history_string = "\n".join([f"query: {entry['query']}\nresponse: {entry['response']}" for entry in last_entries])
            standalone_question = self.llm_chain_integrated.invoke({'chat_history':history_string,'follow_up_query':ques})
            print(history_string)
            print(standalone_question.get('text'))
            response = self.qa_with_source.invoke({'query':standalone_question.get('text')})
            
        return response["result"]
    
    def run_qa_system(self):
        flag = True
        i = 1

        print("\n\n")

        while flag:
            if i == 1:
                question = input("Enter your query. Press 0 to exit.\n")
                if question == "0":
                    flag = False
                    break
                result = self.answer_question(question)
                pprint.pprint(result)

            else:
                question = input("Enter your query. Press 0 to exit.\n")
                if question == "0":
                    flag = False
                    break

                result = self.answer_question(question)
                pprint.pprint(result)

            i += 1  


if __name__ == "__main__":
    folder_path = './disaster_data'
    floods_qa_system = FloodsQASystem(folder_path)

    history  =  {'0': 
        {
            'query': 'Hello. What can you do?',
            'response': 'I can provide information and answer questions about natural disasters such as floods, earthquakes, landslides, and cyclones based on the context provided. If you have any specific questions, feel free to ask!'}
        }
    print(floods_qa_system.answer_question('Okay, tell me about landslides.',history))
