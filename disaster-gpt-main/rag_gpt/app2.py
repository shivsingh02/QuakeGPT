from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from qa2 import FloodsQASystem
from pdpp_qa import PDPP_QA_System
import prediction

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

folder_path = './disaster_data'
floods_qa_system = FloodsQASystem(folder_path)
bot = PDPP_QA_System('./pdpp_data')

@app.route('/api/answer_question', methods=['POST'])
@cross_origin()
def answer_question():
    data = request.json
    question = data.get('question')
    history = data.get('history')

    if question is None:
        return jsonify({'error': 'Missing question parameter'}), 400
    if history is None:
        history = {}
    
    special = data.get('special')
    if(special):
        result = bot.answer_question(question,history)
    else:
        result = floods_qa_system.answer_question(question,history)
    return jsonify({'result': result})

@app.route('/api/answer_pred_route', methods=['POST'])
@cross_origin()
def answer_pred():
    data=request.json
    question = data.get('question')
    if question is None:
        return jsonify({'error': 'Missing question parameter'}), 400
    result = prediction.answer_pred(question)
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(debug=False,host='10.29.8.94')
    # app.run(debug=True)