import sys
import vk_api
import pymorphy2
import string
import pyperclip
import json
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QColorDialog, QCheckBox, QLCDNumber
from PyQt5.QtWidgets import QLabel, QTextEdit, QLineEdit, QInputDialog, QMessageBox, QFileDialog, QSlider
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class vk_login_error(Exception):
    pass


class vk_password_error(Exception):
    pass


class Journalist(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.k = True
        try:
            with open('main.json', 'r', encoding='utf-8') as f_obj:
                a = json.load(f_obj)
                self.font = QFont()
                self.font.setFamily('Arial')
                self.font.setPointSize(a['FontSize'])
                self.font.setBold(a['FontBold'])
                self.font.setItalic(a['FontItalic'])
                self.boldQcheckBox = QCheckBox('Сделать Текст Жирным(Чуть жирнее , чем ты)', self)
                self.boldQcheckBox.setChecked(a['FontBold'])
                self.boldQcheckBox.move(1440, 40)
                self.boldQcheckBox.stateChanged.connect(self.set_bold)

                self.italicQcheckBox = QCheckBox('ItalyText(Да , я из франции)', self)
                self.italicQcheckBox.move(1440, 60)
                self.italicQcheckBox.setChecked(a['FontItalic'])
                self.italicQcheckBox.stateChanged.connect(self.set_italic)

                self.color_btn = a['ButtonFon']

                self.main_text = QTextEdit('Текст статьи', self)
                self.main_text.setFont(self.font)
                self.main_text.move(480, 20)
                self.main_text.resize(960, 540)
                self.k = False
                if a['MainTextFon']:
                    self.main_text.setStyleSheet(
                        'background-image:url({});background-position: center;background-norepeat'.format(
                            a['MainTextFon']))
                else:
                    self.main_color = a['MainTextColor']
                    self.main_text.setStyleSheet(
                        "background-color: {}".format(self.main_color)
                    )

        except Exception as ex:
            if self.k:
                with open('main.json', 'w', encoding='utf-8') as f_obj:
                    slovar = {'FontSize': 8, 'FontBold': False, 'FontItalic': False,
                              'ButtonFon': '#ffffff', 'MainTextColor': '#ffffff', 'MainTextFon': ''}
                    json.dump(slovar, f_obj, ensure_ascii=False)
                    self.font = QFont()
                    self.font.setFamily('Arial')
                    self.font.setPointSize(slovar['FontSize'])
                    self.boldQcheckBox = QCheckBox('Сделать Текст Жирным(Чуть жирнее , чем ты)', self)
                    self.boldQcheckBox.move(1440, 40)
                    self.boldQcheckBox.stateChanged.connect(self.set_bold)
                    self.italicQcheckBox = QCheckBox('ItalyText(Да , я из франции)', self)
                    self.italicQcheckBox.move(1440, 60)
                    self.italicQcheckBox.stateChanged.connect(self.set_italic)
                    self.color_btn = slovar['ButtonFon']

                    self.main_text = QTextEdit('Текст статьи', self)
                    self.main_text.setFont(self.font)
                    self.main_text.move(480, 20)
                    self.main_text.resize(960, 540)

            else:
                print(ex)
                QMessageBox.critical(QWidget(), 'Произошол троллинг',
                                     'Картинка , которая ранее использовалась вами как фон была потеряна')

        self.text = ''
        self.alz = QFont()
        self.alz.setFamily('Arial')
        self.alz.setBold(True)
        self.alz.setPointSize(24)
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowTitle('Journalist')
        self.setFixedSize(1920, 1080)

        self.name_text = QLineEdit('Название статьи', self)
        self.name_text.move(480, 0)
        self.name_text.resize(960, 20)

        self.buttons = []
        self.vkButton = QPushButton(self)
        self.vkButton.setText('Авторизироваться в VK')
        self.vkButton.move(0, 0)
        self.vkButton.resize(130, 20)
        self.vkButton.clicked.connect(self.vk_auth)
        self.buttons.append(self.vkButton)

        self.vk_authed = False

        self.btn_analiz = QPushButton('Анализировать тафтологию', self)
        self.btn_analiz.move(0, 20)
        self.btn_analiz.clicked.connect(self.analiz_taftalogy)
        self.buttons.append(self.btn_analiz)

        posx = 80
        posy = 100
        butts = '©™®°$¢€£‰µ≠§←↓↑→'
        self.btn = []
        for i in range(16):
            self.btn = QPushButton(butts[i], self)
            self.btn.resize(posx, posy)
            self.btn.move(i % 4 * posx, i // 4 * posy + 40)
            self.btn.clicked.connect(self.add_symbol)
            self.buttons.append(self.btn)
        buttns = '123*456=789/+0-C'
        for i in range(16):
            self.btn = QPushButton(buttns[i], self)
            self.btn.resize(posx, posy)
            self.btn.move(i % 4 * posx + 1440, i // 4 * posy + 200)
            self.btn.clicked.connect(self.calculat)
            self.buttons.append(self.btn)
        self.LCD_count = QLCDNumber(self)
        self.LCD_count.resize(320, 100)
        self.LCD_count.move(1440, 100)

        self.create_mark = QPushButton('Добавить оценок', self)
        self.create_mark.move(480, 560)
        self.create_mark.resize(480, 20)
        self.create_mark.clicked.connect(self.create_mark_func)
        self.buttons.append(self.create_mark)

        self.save_as_button = QPushButton('Сохранить как', self)
        self.save_as_button.move(1440, 0)
        self.save_as_button.clicked.connect(self.saveFileNamesDialog)
        self.buttons.append(self.save_as_button)

        self.main_text_color_button = QPushButton('Изменить цвет главного текста', self)
        self.main_text_color_button.move(1525, 0)
        self.main_text_color_button.clicked.connect(self.main_text_color)
        self.buttons.append(self.main_text_color_button)

        self.main_text_fon_button = QPushButton('Изменить фон главного текста', self)
        self.main_text_fon_button.move(1525, 20)
        self.main_text_fon_button.resize(170, 20)
        self.main_text_fon_button.clicked.connect(self.main_text_fon)
        self.buttons.append(self.main_text_fon_button)

        self.button_color_btn = QPushButton('Изменить фон всех кнопок', self)
        self.button_color_btn.move(1692, 0)
        self.button_color_btn.clicked.connect(self.button_color)
        self.buttons.append(self.button_color_btn)

        self.btn_set_font_size = QPushButton('Изменить шрифт главного текста', self)
        self.btn_set_font_size.move(1692, 20)
        self.btn_set_font_size.clicked.connect(self.set_font_size)
        self.buttons.append(self.btn_set_font_size)

        self.vkButton_post = QPushButton(self)
        self.vkButton_post.setText('Выпустить статью в ВК')
        self.vkButton_post.move(195, 0)
        self.vkButton_post.resize(130, 20)
        self.vkButton_post.clicked.connect(self.send_vk)
        self.vkButton_post.setVisible(False)
        self.buttons.append(self.vkButton)
        self.mark_ready = False
        self.final_mark_text = QLabel('', self)
        self.text_alz = QLabel('', self)
        self.text_alz.move(0, 440)

        for i in self.buttons:
            i.setStyleSheet(
                "background-color: {}".format(self.color_btn)
            )

    def analiz_taftalogy(self):
        try:
            morph = pymorphy2.MorphAnalyzer()
            worlds = []
            worlds_true = []
            translator = str.maketrans('', '', string.punctuation)
            a = str(self.main_text.toPlainText()).split()
            for i in a:
                i = i.translate(translator)
                worlds.extend(map(lambda x: x.lower(), i.split()))
            worlds_set = list(set(morph.parse(i)[0].normal_form for i in worlds))
            worlds_normal = [morph.parse(i)[0].normal_form for i in worlds]
            for i in worlds_set:
                worlds_true.append(
                    (morph.parse(i)[0].normal_form, int(worlds_normal.count(morph.parse(i)[0].normal_form))))

            worlds_true = sorted(worlds_true, key=lambda x: x[1], reverse=True)
            b = []
            for i in range(len(worlds_true)):
                if i < 10:
                    b.append(str('{} {} : {}'.format(i + 1, worlds_true[i][0], worlds_true[i][1])))
                else:
                    break
            self.text_alz.setFont(self.alz)
            self.text_alz.setText('\n'.join(b))
            self.text_alz.resize(self.text_alz.sizeHint())
        except Exception as ex:
            print(ex)

    def calculat(self):
        try:
            a = str(self.btn.sender().text())
            if a == '=':
                result = str(eval(self.text))
                self.text = result
                self.LCD_count.display(self.text)
                pyperclip.copy(self.text)
                QMessageBox.information(self, 'Результат', 'Результат скопирован в Буфер обмена'
                                        , QMessageBox.Ok | QMessageBox.Cancel)

            elif a == 'C':
                self.text = self.text[:len(self.text) - 1]
                self.LCD_count.display(self.text)
            else:
                self.text = self.text + a
                self.LCD_count.display(self.text)
        except ZeroDivisionError:
            self.text = ''
            self.LCD_count.display('FATALERROR')
        except Exception as ex:
            print(ex)

    def set_bold(self, state):
        try:
            if state == Qt.Checked:
                self.font.setBold(True)
                self.main_text.setFont(self.font)
                with open("main.json", "r") as jsonFile:
                    data = json.load(jsonFile)
                data["FontBold"] = True
                with open("main.json", "w") as jsonFile:
                    json.dump(data, jsonFile)

            else:
                self.font.setBold(False)
                self.main_text.setFont(self.font)
                with open("main.json", "r") as jsonFile:
                    data = json.load(jsonFile)
                data["FontBold"] = False
                with open("main.json", "w") as jsonFile:
                    json.dump(data, jsonFile)
        except Exception as ex:
            print(ex)

    def set_italic(self, state):
        if state == Qt.Checked:
            self.font.setItalic(True)
            self.main_text.setFont(self.font)
            with open("main.json", "r") as jsonFile:
                data = json.load(jsonFile)
            data["FontItalic"] = True
            with open("main.json", "w") as jsonFile:
                json.dump(data, jsonFile)
        else:
            self.font.setItalic(False)
            self.main_text.setFont(self.font)
            with open("main.json", "r") as jsonFile:
                data = json.load(jsonFile)
            data["FontItalic"] = False
            with open("main.json", "w") as jsonFile:
                json.dump(data, jsonFile)

    def set_font_size(self):
        b = ['8', '14', '20', '24', '28', '32', '36', '46', '58', '64', '72']
        i, okBtnpressed = QInputDialog.getItem(self,
                                               'Выберите размер', 'Тут выбирай, если не дебил', b, 0, False)
        if okBtnpressed:
            self.font.setPointSize(int(i))
            self.main_text.setFont(self.font)
            with open("main.json", "r") as jsonFile:
                data = json.load(jsonFile)
            data["FontSize"] = int(i)
            with open("main.json", "w") as jsonFile:
                json.dump(data, jsonFile)

    def button_color(self):
        try:
            self.color_btn = QColorDialog.getColor()
            with open("main.json", "r") as jsonFile:
                data = json.load(jsonFile)
            data["ButtonFon"] = self.color_btn.name()
            with open("main.json", "w") as jsonFile:
                json.dump(data, jsonFile)
            if self.color_btn.isValid():
                for i in self.buttons:
                    i.setStyleSheet(
                        "background-color: {}".format(self.color_btn.name())
                    )
        except Exception as ex:
            print(ex)

    def main_text_fon(self):
        try:
            options = QFileDialog.Options()
            options = QFileDialog.DontUseNativeDialog
            photo, _ = QFileDialog.getOpenFileName(self, "JournalistOpen", "journalist.png",
                                                   "*.png;;*.jpg;;*bmp", options=options)
            if photo:
                print(photo)
                self.main_text.setStyleSheet(
                    'background-image:url({});background-position: center;background-norepeat'.format(photo))
                with open("main.json", "r") as jsonFile:
                    data = json.load(jsonFile)
                data["MainTextFon"] = photo
                with open("main.json", "w") as jsonFile:
                    json.dump(data, jsonFile)
        except Exception as ex:
            print(ex)

    def main_text_color(self):
        self.main_color = QColorDialog.getColor()
        if self.main_color.isValid():
            with open("main.json", "r") as jsonFile:
                data = json.load(jsonFile)
            data["MainTextColor"] = self.main_color.name()
            with open("main.json", "w") as jsonFile:
                json.dump(data, jsonFile)
            self.main_text.setStyleSheet(
                "background-color: {}".format(self.main_color.name())
            )

    def add_symbol(self):
        try:
            self.main_text.setText(self.main_text.toPlainText() + self.btn.sender().text())
        except Exception as ex:
            print(ex)

    def create_mark_func(self):
        self.final_mark_text.setText('')
        a = list(range(1, 11))
        b = []
        for i in a:
            b.append(str(i))
        i, okBtnpressed = QInputDialog.getItem(self,
                                               'Количество кнопок', 'Выберите кол-во кнопок', b, 4, False)

        try:
            if okBtnpressed:
                self.marks = []
                self.final_mark = []
                for j in range(int(i)):
                    self.marks.append(QLineEdit('Введите название оценки под номером {}'.format(j + 1), self))
                    self.marks[j].resize(470, 40)
                    self.marks[j].move(480 + j % 2 * 480, 560 + j // 2 * 50)
                    self.marks[j].setVisible(True)
                    print(self.marks[j].pos())
                self.create_mark.setVisible(False)
                self.create_sliders = QPushButton('Создать Оценки', self)
                self.create_sliders.move(960, 800)
                self.create_sliders.setVisible(True)
                self.create_sliders.clicked.connect(self.sliders_func)
                self.create_sliders.setStyleSheet(
                    "background-color: {}".format(self.color_btn)
                )
                self.buttons.append(self.create_sliders)

        except Exception as ex:
            print(ex)

    def sliders_func(self):
        try:
            i = len(self.marks)
            self.sliders = []
            for j in range(i):
                self.sliders.append(QSlider(Qt.Horizontal, self))
                self.sliders[j].resize(470, 20)
                self.sliders[j].move(480 + j % 2 * 480, 590 + j // 2 * 50)
                self.sliders[j].setMaximum(10)
                self.sliders[j].setMinimum(0)
                self.sliders[j].setVisible(True)
                print(self.sliders[j].pos())
            for j in self.marks:
                j.setVisible(False)
            self.markstext = []
            for j in range(i):
                a = self.marks[j].text()
                self.markstext.append(QLabel(a, self))
                self.markstext[j].resize(470, 20)
                self.markstext[j].move(480 + j % 2 * 480, 560 + j // 2 * 50)
                self.markstext[j].setVisible(True)
            self.create_sliders.setVisible(False)
            self.slider_ready = QPushButton('Готово', self)
            self.slider_ready.setVisible(True)
            self.slider_ready.move(960, 820)
            self.slider_ready.clicked.connect(self.marks_ready)
            self.slider_ready.setStyleSheet(
                "background-color: {}".format(self.color_btn)
            )
            self.buttons.append(self.slider_ready)

        except Exception as ex:
            print(ex)

    def marks_ready(self):
        try:
            self.final_mark = []
            for i, j in zip(self.markstext, self.sliders):
                self.final_mark.append('{} : {}'.format(i.text(), j.value()))
            self.final_mark_text = QLabel('\n'.join(self.final_mark), self)
            self.final_mark_text.setVisible(True)
            self.final_mark_text.move(480, 560)
            self.final_mark_text.resize(480, 560)
            for i in self.sliders:
                i.setVisible(False)
            for i in self.markstext:
                i.setVisible(False)
            self.mark_ready = True
            del (self.marks[:])
            del (self.sliders[:])
            del (self.markstext[:])
            self.create_mark = QPushButton('Добавить оценок', self)
            self.create_mark.move(480, 560)
            self.create_mark.resize(480, 20)
            self.create_mark.clicked.connect(self.create_mark_func)
            self.create_mark.setVisible(True)
            self.create_mark.setStyleSheet(
                "background-color: {}".format(self.color_btn)
            )
            self.buttons.append(self.create_mark)
            self.slider_ready.setVisible(False)
        except Exception as ex:
            print(ex)

    def make_form_vk_login(self):
        i, okBtnPressed = QInputDialog.getText(self, "Введите логин", "Ваш логин")
        if okBtnPressed:
            self.vkLogin = i

    def make_form_vk_paswd(self):
        i, okBtnPressed = QInputDialog.getText(self, "Введите пароль", "Ваш пароль")

        if okBtnPressed:
            self.vkPaswd = i

    def vk_auth(self):
        try:
            if not self.vk_authed:
                self.make_form_vk_login()
                self.make_form_vk_paswd()
                if not self.vkLogin:
                    raise vk_login_error
                if not self.vkPaswd:
                    raise vk_password_error
                self.vk_session = vk_api.VkApi(self.vkLogin, self.vkPaswd)
                self.vk_session.auth()
                self.vk = self.vk_session.get_api()
                self.vkButton_post.setVisible(True)
                self.vkButton_post.setStyleSheet("background-color: {}".format(self.color_btn))
                self.vk_authed = True
                self.vkButton.setText('Авторизировано')
            else:
                self.vkLogin = ''
                self.vkLogin = ''
                self.vk_authed = False
                self.vkButton_post.setVisible(False)
        except vk_api.BadPassword:
            QMessageBox.critical(QWidget(), 'Ошибка авторизации!', "Неверный логин или пароль!")
        except vk_login_error:
            QMessageBox.critical(QWidget(), 'Вы не ввели логин', "Прошу вас извиниться за это")
        except vk_password_error:
            QMessageBox.critical(QWidget(), 'Вы не ввели пароль', 'Прошу вас извиниться за это')

    def send_vk(self):
        if self.vk_authed:
            if self.mark_ready:
                k = str('\n'.join(self.final_mark))
                a = self.name_text.text() + '\n' + self.main_text.toPlainText() + '\n' + k
            else:
                a = self.name_text.text() + '\n' + self.main_text.toPlainText()
            self.vk.wall.post(message=a)

    def saveFileNamesDialog(self):
        options = QFileDialog.Options()

        options = QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "JournalistSave", "journalist.txt",
                                                  "Text Files (*.txt)", options=options)
        if fileName:
            try:
                self.saveFileName = open('{}.txt'.format(fileName), 'w')
                print(fileName)
                if self.mark_ready:
                    k = str('\n'.join(self.final_mark))
                    a = self.name_text.text() + '\n' + self.main_text.toPlainText() + '\n' + k
                else:
                    a = self.name_text.text() + '\n' + self.main_text.toPlainText()

                self.saveFileName.write(a)
                self.saveFileName.close()

            except Exception as ex:
                print(ex)

    def closeEvent(self, QCloseEvent):
        closeornot = QMessageBox.question(self, 'Ты дурак, зачем тебе выходить? ',
                                          "Хочешь сохранить файл напоследок?",
                                          QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Cancel)

        if closeornot == QMessageBox.Yes:
            self.saveFileNamesDialog()
            QCloseEvent.accept()

        if closeornot == QMessageBox.No:
            QCloseEvent.accept()
        if closeornot == QMessageBox.Cancel:
            QCloseEvent.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Journalist()
    ex.show()
    sys.exit(app.exec())
