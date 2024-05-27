#read_summaries.py
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/read-summary', methods=['POST'])
def read_summary():
    data = request.json
    summary = data['summary']
    rate = data.get('rate', 2)  # 요청된 속도가 없으면 기본값은 1.5로 설정
    # 클라이언트로부터 받은 텍스트와 읽는 속도를 사용하여 음성을 생성
    generate_speech(summary, rate)
    return jsonify({'message': 'Text received successfully'}), 200

# 음성 생성 함수
def generate_speech(text, rate=1):
    # SpeechSynthesis API를 사용하여 음성을 생성하는 코드
    speech = f"new SpeechSynthesisUtterance('{text}');"
    speech += f"speech.lang = 'ko-KR';"
    speech += f"speech.rate = {rate};"
    speech += f"speechSynthesis.speak(speech);"
    # JavaScript 코드를 실행하는 방법은 여러 가지가 있습니다.
    # 여기서는 웹 브라우저의 콘솔에 출력합니다.
    print(speech)

if __name__ == '__main__':
    app.run(debug=True)
