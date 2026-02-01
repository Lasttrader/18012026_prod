#import
import pickle
import openai

from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from flask import (Flask, # сервер
                   render_template, # отображение шаблонов 
                   request, #обработка запросов
                   jsonify)  #для отработки APi запросов и возвращение в фомрате JSON
print("import success")

YANDEX_CLOUD_FOLDER = ""
YANDEX_CLOUD_API_KEY = ""
YANDEX_CLOUD_MODEL = "aliceai-llm/latest"

DEEPSEEK_API_KEY = ''

yaGPTinstruction = '''ты очень приветливый специалист банка, 
                      твоя задача формировать ответные письма клиентам
                      ты очень дружелюбный и отвечаешь всегда стихами. 
                      если тебе придет сообщение ДА, то тогда напиши восторженный стишок, 
                      для клиента о том что ему одобрен кредит.
                      Если придет ответ НЕТ, то напиши грустный стишок для клиента, 
                      и рекомендации обратиться попозже. 
                      Не забывай в сответе каждую строку делать с новой строки.
                      '''

deepseekInstruction = '''Ты очень классный специалист банка, который готовит ответы для клиентов,
                        тебе будут приходить два ответа, да или нет. 
                        если придет ДА, то напиши восторженный грузинский тост, 
                        пожеланием использовать полученный кредит в самом лучшем виде. 
                        Если получишь ответ НЕТ, то напиши грузинсккий тост о том, что всё еще в переди'''

deepseekanalytics = '''Ты супер аналитик твоя заача анализировать банковские документы и выдавать сводынй отчет, 
            чтобы убедиться, что данные о заемщиках верные, 
            также ты генерируещшь отчет в ледующем виде:
            1. о чем эти данные?
            2. какие основные закономенрности ты видишь?
            3. какие выводы и рекомендации ты можешь сделать относительно анализа данных'''

#load models
job_LE = pickle.load(open('../flaskApp/tech_models/job_LE.pkl', 'rb'))
marital_LE = pickle.load(open('../flaskApp/tech_models/marital_LE.pkl', 'rb'))	
education_LE = pickle.load(open('../flaskApp/tech_models/education_LE.pkl', 'rb'))	
default_LE = pickle.load(open('../flaskApp/tech_models/default_LE.pkl', 'rb'))	
housing_LE = pickle.load(open('../flaskApp/tech_models/housing_LE.pkl', 'rb'))	
loan_LE	= pickle.load(open('../flaskApp/tech_models/loan_LE.pkl', 'rb'))
contact_LE = pickle.load(open('../flaskApp/tech_models/contact_LE.pkl', 'rb'))	
month_LE = pickle.load(open('../flaskApp/tech_models/month_LE.pkl', 'rb'))	
poutcome_LE	= pickle.load(open('../flaskApp/tech_models/poutcome_LE.pkl', 'rb'))
y_LE = pickle.load(open('../flaskApp/tech_models/y_LE.pkl', 'rb'))
num_scaler = pickle.load(open('../flaskApp/tech_models/num_scaler.pkl', 'rb'))
kNN =  pickle.load(open('../flaskApp/ml_models/kNN.pkl', 'rb'))
print("models loeaded success")

le_list = [job_LE,
            marital_LE,
            education_LE,
            default_LE,
            housing_LE,
            loan_LE,
            contact_LE,
            month_LE,
            poutcome_LE]

#YaGPT client
clientYa = openai.OpenAI(
    api_key=YANDEX_CLOUD_API_KEY,
    base_url="https://rest-assistant.api.cloud.yandex.net/v1",
    project=YANDEX_CLOUD_FOLDER)
#deepseekclient client
clientDS = openai.OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

#app
app = Flask(__name__)
#route
@app.route('/', methods=['POST', 'GET'])
def main():
    #отображегние формы анкеты по умолчанию
    if request.method == 'GET':
        return render_template('main.html')
    #если пользователь отпарвил форму с веб страницы
    if request.method == 'POST':
        #get data from form
        job = request.form['job']
        marital = request.form['marital']
        education = request.form['education']
        default = request.form['default']
        housing = request.form['housing']
        loan = request.form['loan']
        contact = request.form['contact']
        month = request.form['month']
        poutcome  = request.form['poutcome']
        age = request.form['age']
        balance = request.form['balance']
        day = request.form['day']
        duration = request.form['duration']
        campaign= request.form['campaign']
        pdays= request.form['pdays']
        previous= request.form['previous']

        #get preprocessing
        #categorical
        x_cat_list = [job,
                        marital,
                        education,
                        default,
                        housing,
                        loan,
                        contact,
                        month,
                        poutcome]
        x_le_list = [] # под закодированные признаки
        for i in range(len(x_cat_list)):
            x_cat = le_list[i].transform([x_cat_list[i]])[0] #0 чтобы забрать значение из массива
            x_le_list.append(x_cat)
        print("x_le_list", x_le_list)
        
        #num
        x_num = [age, balance, day, duration, campaign, pdays, previous]

        #собираем общий X
        X = [] 
        X.extend(x_le_list)
        X.extend(x_num)
        #scaler
        X_scaled = num_scaler.transform([X])
        print('X_scaled:', X_scaled)

        #predict
        pediction = kNN.predict(X_scaled)
        
        #return result
        if pediction == 0:
            result = "НЕТ"
        else:
            result = "ДА"

        # generate GPT answer

        response = clientYa.responses.create(
            model=f"gpt://{YANDEX_CLOUD_FOLDER}/{YANDEX_CLOUD_MODEL}",
            temperature=0.94,
            instructions=yaGPTinstruction,
            input = result,
            max_output_tokens=500)

        
        return render_template('result.html', result=response.output_text)

@app.route('/api/v1/add_message/', methods = ['POST', 'GET'])
def api_message():
    get_message_x = request.json
    X = get_message_x['X_scaled']
    pediction = kNN.predict(X)
    #return result
    if pediction == 0:
        result = "Извините мы не можем выдать вам кредит"
    else:
        result = "Поздравляем, кредит одобрен!"
    response = clientDS.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", 
             "content": deepseekInstruction},
             {"role": "user", 
              "content": result},],
              stream=False)
    return jsonify(str(response.choices[0].message.content))


@app.route('/api/v2/add_message/', methods = ['POST', 'GET'])
def api_message_v2():
    get_message_x = request.json
    X_api = get_message_x['X_from_desktop'][0]
    x_cat_list = X_api[:9]
    print(x_cat_list)
    x_num = X_api[9:]
    print(x_num)
    x_le_list = [] # под закодированные признаки
    for i in range(len(x_cat_list)):
        x_cat = le_list[i].transform([x_cat_list[i]])[0] #0 чтобы забрать значение из массива
        x_le_list.append(x_cat)
    print("x_le_list", x_le_list)
        #собираем общий X
    X = [] 
    X.extend(x_le_list)
    X.extend(x_num)
    #scaler
    X_scaled = num_scaler.transform([X])
    print('X_scaled:', X_scaled)
    #predict
    pediction = kNN.predict(X_scaled)
    
    #return result
    if pediction == 0:
        result = "Извините мы не можем выдать вам кредит"
    else:
        result = "Поздравляем, кредит одобрен!"
    return jsonify(str(result))

@app.route('/api/v3/add_message/', methods = ['POST', 'GET'])
def api_message_v3():
    get_file = request.json
    file_for_analyze = get_file['file'][0]
    
    response = clientDS.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", 
             "content": deepseekanalytics},
             {"role": "user", 
              "content": file_for_analyze},],
              stream=False)
    return jsonify(str(response.choices[0].message.content))





if __name__ == '__main__':
    app.run(debug=True)