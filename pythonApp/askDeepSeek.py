import requests

#данные анкеты на прогноз

with open('bank.csv', 'r', encoding='utf-8') as f:
    file_for_analyze = f.read()

###### API
api_message = requests.post('http://127.0.0.1:5000/api/v3/add_message/',
                            json={'file' : [file_for_analyze[:10000]]})
if api_message.ok:
    with open('report.md', 'w', encoding='utf-8') as f:
        f.write(api_message.json())
else:
    print("ошибка анализа обратитесь к администратору")