# import
import sys
import requests
from PyQt6.QtWidgets import (QApplication,
                             QDialog,
                             QDialogButtonBox, 
                             QFormLayout,
                             QLineEdit, 
                             QVBoxLayout, 
                             QGroupBox,
                             QLabel,
                             QMessageBox,
                             QPushButton)

print("import success")

#создание окна с формой и кнопками

class Dialog(QDialog):
    def __init__(self):
        super(Dialog, self).__init__()
        self.createFormGroupBox()
        self.x_for_predict = {} # сюда помещаем массив для прогноза
        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                     QDialogButtonBox.StandardButton.Cancel)
        buttonBox.accepted.connect(self.get_predict)
        buttonBox.rejected.connect(self.rejected)

        mainLayout  = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)
        self.setWindowTitle('desktop ML app')

    def createFormGroupBox(self):
        self.formGroupBox = QGroupBox('Заполните анкету')
        self.layout =QFormLayout()

        button_list = ['job',
                        'marital',
                        'education',
                        'default',
                        'housing',
                        'loan',
                        'contact',
                        'month',
                        'poutcome',
                        'age', 
                        'balance', 
                        'day', 
                        'duration', 
                        'campaign', 
                        'pdays', 
                        'previous']

        for index, label in enumerate(button_list):
            x = QLineEdit()
            x.textEdited.connect(self.create_x_for_predict(index+1))
            self.layout.addRow(QLabel(label), x)
        self.formGroupBox.setLayout(self.layout)

    def create_x_for_predict(self, x):
        #функция собирает X для прогноза
        def savedX(text):
            self.x_for_predict[x] = text 
        return savedX
    
#получение данных

    #predict
    def get_predict(self):
        rslt = QMessageBox(self)
        rslt.setWindowTitle('ВАШ РЕЗУЛЬТАТ')
        try:
            x_list = list(self.x_for_predict.values())
            ###### API
            api_message = requests.post('http://127.0.0.1:5000/api/v2/add_message/',
                                json={'X_from_desktop' : [x_list]})
            result = api_message.json()
            rslt.setText(result)
            rslt.exec()
        except:
            print('Введите данные')


#запуск и закрытие приложения
app = QApplication(sys.argv)
dialog = Dialog()
dialog.exec() # исполнитель
app.exit()

