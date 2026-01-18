#import
import pickle

from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from flask import (Flask, # сервер
                   render_template, # отображение шаблонов 
                   request, #обработка запросов
                   jsonify)  #для отработки APi запросов и возвращение в фомрате JSON
print("import success")

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
        le_list = [job_LE,
                        marital_LE,
                        education_LE,
                        default_LE,
                        housing_LE,
                        loan_LE,
                        contact_LE,
                        month_LE,
                        poutcome_LE]
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
            result = "Извините мы не можем выдать вам кредит"
        else:
            result = "Поздравляем, кредит одобрен!"
        
        return render_template('result.html', result = result)

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
    return jsonify(str(result))


@app.route('/api/v2/add_message/', methods = ['POST', 'GET'])
def api_message_v2():
    return 'api в  разрабоке'

if __name__ == '__main__':
    app.run(debug=True)