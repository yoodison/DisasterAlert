from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, send
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

natural_disasters = ['홍수', '화재', '태풍', '지진', '해일', '산사태', '가뭄']
disasters = []

def fetch_disaster_info():
    url = 'https://www.safetydata.go.kr/disaster-data/disasterNotification'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table')
    rows = table.find_all('tr')[1:]

    disaster_list = []
    for row in rows:
        cells = row.find_all('td')
        description = cells[1].text.strip()
        date = cells[2].text.strip()

        category = '사회재난'
        for word in natural_disasters:
            if word in description:
                category = '자연재해'
                break

        search_query = '+'.join(description.split()[:3])

        disaster_list.append({
            'category': category,
            'description': description,
            'date': date,
            'search_query': search_query
        })

    return disaster_list

@app.route('/')
def index():
    global disasters
    disasters = fetch_disaster_info()
    return render_template('index.html', disasters=disasters)

@app.route('/get_disasters', methods=['GET'])
def get_disasters():
    return jsonify(disasters)

@socketio.on('message')
def handle_message(msg):
    send(msg, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
