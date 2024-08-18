import pandas as pd
import spacy
import re
import pandas as pd
from langchain.prompts import PromptTemplate
from langchain_together import Together
from langchain.chains import LLMChain

def get_disaster_name(query):
        nlp=spacy.load("en_core_web_sm")
        doc = nlp(query)
        disaster_names = [ent.text for ent in doc.ents if ent.label_ in ["ORG", "NORP", "GPE"]]
        if not disaster_names:  
            disaster_names = [token.text for token in doc if token.dep_ in ["nsubj", "dobj"]]
        return disaster_names
    
def find_first_disaster(text):
    pattern = re.compile(r'(flood|cyclone|earthquake|landslide)', re.IGNORECASE)
    match = re.search(pattern, text)
    return match.group(0).capitalize() if match else None


def predict_month(disaster_name,disaster_type):
    # Month number mapping
    month_numbers = {
        'January': 1,
        'February': 2,
        'March': 3,
        'April': 4,
        'May': 5,
        'June': 6,
        'July': 7,
        'August': 8,
        'September': 9,
        'October': 10,
        'November': 11,
        'December': 12
    }
    df = pd.read_excel("./disaster_data/natural disaster final.xlsx")
    # Extract months and their corresponding weights
    months = []
    if(disaster_type!=None):
        disaster_data = df[(df['Name'].str.contains(disaster_name)) & (df['Disaster Type'].str.contains(disaster_type))]
    else:
        disaster_data = df[(df['Name'].str.contains(disaster_name))] 
        

    for month_range in disaster_data['Month']:
            if '-' in month_range:  # if there's a range of months
                start_month, end_month = month_range.split('-')
                months.extend([month_numbers[start_month], month_numbers[end_month]])
            else:
                months.append(month_numbers[month_range])
    
    if not months:
            return "NA"
    # If the frequency of the most frequent month is less than 3, calculate the weighted average
    most_common_month = max(set(months), key=months.count)
    if months.count(most_common_month) <= 3:
        total_months = len(months)
        weighted_sum = sum(month * (1 / total_months) for month in months)
        weighted_average = round(weighted_sum)

        # Convert the weighted average back to the month
        predicted_month = weighted_average if weighted_average <= 12 else 12
        predicted_month_name = [month for month, number in month_numbers.items() if number == predicted_month][0]

        return predicted_month_name
    else:
        return max(set(months), key=months.count)
    
def create_llm_chain():
    template_ans= """You are a helpful chatbot answers users questions on natural disasters
    related predictions. You have been provided with user query and the predicted month of disaster from a machine learning
    model. Use this result to answer user query.Do not write anything else.
    If you dont know the answer, simply state that you don't know.
    User Query:{Query}
    Predicted month by model: {Prediction}
    Response:
    """
    llm_summarize = Together(
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        top_k=50,
        top_p=0.7,
        temperature=0,
        repetition_penalty=1,
        together_api_key="7294b9c3f54b31ac6a9a7a1c6e36e42fc1ee2675e848300500c7127ba3ce5229"
        )
    
    prompt_summarize = PromptTemplate(
        template=template_ans, input_variables=["Query", "Prediction"]
    )
    return LLMChain(llm=llm_summarize, prompt=prompt_summarize,verbose=True)

def answer_pred(query):

    disaster_name=get_disaster_name(query)
    if(disaster_name):
        disaster_type=find_first_disaster(query)
        prediction=predict_month(disaster_name[0],disaster_type)
        prediction_chain=create_llm_chain()
        ans=prediction_chain.invoke({'Query':query, 'Prediction':prediction})
        return ans.get('text')
    else:
        return("No location found in query. Make sure to check your query and look for spelling errors.")
    
