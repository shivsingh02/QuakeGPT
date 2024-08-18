from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from qa import FloodsQASystem

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

file_path = './floods_in_india.csv'
floods_qa_system = FloodsQASystem(file_path)

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
    
    result = floods_qa_system.answer_question(question,history)
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(debug=False,host='10.29.8.94')
    # app.run(debug=True)
