import requests

#данные анкеты на прогноз

X_scaled = [1.71680374, -0.24642938, -1.64475535, -0.1307588,   0.87561735,  2.3542922,
   1.4951332,   0.15316057,  0.44441328, -0.86714509,  0.1513114,   0.37405206,
  -0.24616792, -0.57682947,  2.59947281, -0.32041282]

###### API
api_message = requests.post('http://127.0.0.1:5000/api/v1/add_message/',
                            json={'X_scaled' : [X_scaled]})

print(api_message)
if api_message.ok:
    print(api_message.json())
else:
    print("прогноз недоступен, свяжитесь с администратором")