#!/usr/bin/env python
#-*- coding: utf-8 -*-
'''
Created on 27.05.2011

@author: dik
'''

import pygtk
import MySQLdb
pygtk.require('2.0')
import gtk
import re
import db_engine
import settings

class MainForm(gtk.Builder):
    """Форменный класс, заодно все склейки должен содержать"""
    dbs = None
    attempts = []
    std = {}


    def __init__(self):
        """Конструктор формы"""
        super(MainForm, self).__init__()
        self.add_from_file("ui.glade")
        self.connect_signals(self)
        self.get_object("filefilter1").add_pattern("*.rule")
        self.get_object("filechooserbutton1").select_filename("settings.py")
    
    @staticmethod
    def main():
        """Запускалка основного процесса обработки GTKv2.0
        """
        gtk.main()
    
    @classmethod
    def on_window1_destroy(cls, _):
        """Закрытие формы при нажатие крестика в главном окне
        """
        gtk.main_quit()
        
    def on_connect_im_activate(self, _):
        """Выполнение диалога подлючения к базе данных
        """
        self.get_object("host_liststore").append(row=["localhost"])
        self.get_object("host_comboboxentry").set_active(0)
        self.get_object("db_liststore").append(row=["moodle"])
        self.get_object("db_comboboxentry").set_active(0)
        self.get_object("connect_dialog").show()
    
    def on_cancel_cond_button_clicked(self, _):
        """Закрытие диалога подключения
        """
        self.get_object("connect_dialog").hide()
    
    def on_connect_cond_button_clicked(self, _):
        """Подключение к базе данных по информации из формы
        и заполнение кучи не очень полезных таблиц, нужных только 
        для промотра того что есть в базе
        """
        host = self.get_object("host_comboboxentry").get_active_text()
        dbs = self.get_object("db_comboboxentry").get_active_text()
        user = self.get_object("login_entry").get_text()
        passwd = self.get_object("password_entry").get_text()
        try:
            self.dbs = db_engine.MoodleDBEngine(host, dbs, user, passwd)
            #Заполнение таблиц в программе
            self.dbs.cur.execute("""SELECT id, course, name, intro, questions 
                                FROM mdl_quiz""")
            for i in self.dbs.cur.fetchall():
                self.get_object("test_liststore").append(row=[i[0], 
                                                              i[1], 
                                                              i[2], 
                                                              i[3], 
                                                              i[4]])
            self.dbs.cur.execute("""SELECT id, name, questiontext, defaultgrade,
                                penalty FROM mdl_question""")
            for i in self.dbs.cur.fetchall():
                self.get_object("test_content_liststore").append(row=[i[0], 
                                                                      i[1], 
                                                                      i[2], 
                                                                      i[3], 
                                                                      i[4]])
            self.dbs.cur.execute("""SELECT id, attempt, question, answer, grade 
                                FROM mdl_question_states""")
            for i in self.dbs.cur.fetchall():
                self.get_object("qestion_states_liststore").append(row=[i[0], 
                                                                        i[1], 
                                                                        i[2], 
                                                                        i[3], 
                                                                        i[4]])
            self.dbs.cur.execute("""SELECT id, userid, sumgrades 
                                FROM mdl_quiz_attempts""")
            for i in self.dbs.cur.fetchall():
                self.get_object("quiz_attempts_liststore").append(row=[i[0], 
                                                                       i[1], 
                                                                       i[2]])
            self.dbs.cur.execute("""SELECT id, question, answer, fraction 
                                FROM mdl_question_answers""")
            for i in self.dbs.cur.fetchall():
                self.get_object("answers_liststore").append(row=[i[0], 
                                                                 i[1], 
                                                                 i[2], 
                                                                 i[3]])
            #Видоизменение заголовка окна
            self.get_object("window1").set_title("Moodle Re-Tester [" + 
                                                 dbs + "]")
            self.get_object("select_menuitem").props.sensitive = True
            self.get_object("connect_dialog").hide()
        except MySQLdb.Error, db_conn_exception:
            self.dbs = None
            self.get_object("select_menuitem").props.sensitive = False
            conn_label = self.get_object("info_connect_dialog_label")
            conn_label.set_text(str(db_conn_exception))
    
    def on_settings_im_activate(self, _):
        """Открываем диалог настроек
        """
        self.get_object("settings_dialog").show()
    
    def on_cancel_setd_button_clicked(self, _):
        """Закрываем диалог настроек
        """
        self.get_object("settings_dialog").hide()
    
    def on_save_setd_button_clicked(self, _):
        """Закрываем диалог настроек другой кнопкой
        """
        self.get_object("settings_dialog").hide()
    
    def on_about_imagemenuitem_activate(self, _):
        """Отобразим диалог "О программе"
        """
        self.get_object("aboutdialog").show()
    
    def on_aboutdialog_response(self, _, response):
        """Закрываем диалог "О программе"
        """
        if response == -4:
            self.get_object("aboutdialog").hide()
        else:
            self.get_object("aboutdialog").hide()
    
    def on_select_menuitem_activate(self, _):
        """Отображение диалога выбора теста и попыток сделанных учениками
        """
        treeview = self.get_object("treeview8")
        treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.dbs.cur.execute("""SELECT id, name FROM mdl_quiz""")
        for i in self.dbs.cur.fetchall():
            self.get_object("testing_liststore").append(row=[i[1], i[0]])
        self.get_object("testing_combobox").set_active(0)
        self.get_object("select_dialog").show()
    
    def on_cancel_sd_button_clicked(self, _):
        """Закрываем диалог выбора теста
        """
        self.get_object("select_dialog").hide()
       
    def on_testing_combobox_changed(self, _):
        """Заполнение полей попыток при выборе теста
        """
        tals = self.get_object("test_attempts_liststore")
        tals.clear()
        tcmd = self.get_object("testing_combobox")
        test_id = self.get_object("testing_liststore")[tcmd.get_active()][1]
        self.dbs.cur.execute("""SELECT u.id, d.firstname, d.lastname, 
                            u.timestart, u.userid FROM mdl_quiz_attempts u 
                            LEFT OUTER JOIN mdl_user d ON u.userid = d.id 
                            WHERE u.quiz=%s""", (test_id,))
        for i in self.dbs.cur.fetchall():
            tals.append(row=[i[0], i[1] + " " + i[2], i[3], i[4]])
    
    def on_select_sd_button_clicked(self, _):
        """Формирование структур 
        [вопрос, ответ, эталон, доп.информация] по каждой попытке. 
        Заполнение TreeView-компонента с теми же структурами.
        """
        treeview = self.get_object("treeview8")
        selected = treeview.get_selection().get_selected_rows()[1]
        self.attempts = []
        part0 = re.compile("^random[0-9]*-.*")
        part1 = re.compile("^random[0-9]*-")
        for i in selected:
            attempt_id = self.get_object("test_attempts_liststore")[i[0]][0]
            self.dbs.cur.execute("""SELECT u.id, u.attempt, u.question, 
                                u.answer, u.grade, d.questiontext 
                                FROM mdl_question_states u 
                                LEFT OUTER JOIN mdl_question d 
                                ON u.question = d.id WHERE u.attempt = %s 
                                AND u.seq_number >= 1 
                                AND (d.qtype='random' 
                                OR d.qtype='shortanswer')""", (attempt_id,))
            sals = self.get_object("selected_attempts_liststore")
            for j in self.dbs.cur.fetchall():
                if part0.match(j[3]) != None:
                    qnum = part1.match(j[3]).group()[6:-1]
                    self.dbs.tcur.execute("""SELECT qtype FROM mdl_question 
                                         WHERE id=%s""", (qnum,))
                    qtype = self.dbs.tcur.fetchone()[0]
                    if qtype == 'shortanswer':
                        answ = j[3][len(part1.match(j[3]).group()):]
                        self.dbs.tcur.execute("""SELECT questiontext 
                                            FROM mdl_question WHERE id=%s""", 
                                            (qnum,))
                        qtext = self.dbs.tcur.fetchone()[0]
                        sals.append(row=[j[0], j[1], qtext, j[2], answ, j[4]])
                        self.dbs.tcur.execute("""SELECT answer 
                                            FROM mdl_question_answers 
                                            WHERE question=%s 
                                            AND fraction='1'""", (qnum,))
                        orig_answ = []
                        for k in self.dbs.tcur.fetchall():
                            orig_answ.append(k[0])
                        self.attempts.append([j[0], #id
                                        j[1], #№Попытки в Moodle
                                        qtext, #Текст вопроса
                                        j[2], #№Вопроса
                                        answ, #Текст ответа
                                        j[4], #Оценка от системы Moodle
                                        orig_answ #Эталонный ответ
                                        ])
                else:
                    self.dbs.tcur.execute("""SELECT answer 
                                        FROM mdl_question_answers 
                                        WHERE question=%s 
                                        AND fraction='1'""", (j[2],))
                    orig_answ = []
                    for k in self.dbs.tcur.fetchall():
                        orig_answ.append(k[0])
                    sals.append(row=[j[0], 
                                   j[1], 
                                   j[5], 
                                   j[2], 
                                   j[3], 
                                   j[4]])
                    self.attempts.append([j[0], 
                                    j[1], 
                                    j[5], 
                                    j[2], 
                                    j[3], 
                                    j[4], 
                                    orig_answ])
        self.get_object("notebook1").set_current_page(3)
        self.get_object("select_dialog").hide()
    
    def on_correct_toolbutton_clicked(self, _):
        """Выполняем коррекцию при нажатии кнопки тулбара
        """
        self.load_sinonyms_voc()
        self.correct_moodle_grades()
        
    def load_sinonyms_voc(self):
        """Загружаем наборы синонимов
        """
        path = self.get_object("filechooserbutton1").get_filename()
        print path
        
    def correct_moodle_grades(self):
        """Исправление оценок Moodle
        """
        out_file = open("out.txt", "wb")
        for otvet in self.attempts:
            rea = otvet[5]
            tea = otvet[4]
            for i in settings.podst:
                first = i[0][0]
                for part in i:
                    if part[0] == otvet[4]:
                        rea = part[1]
                        tea = first
            otvet = [otvet[0], 
                     otvet[1], 
                     otvet[2], 
                     otvet[3], 
                     otvet[4], 
                     otvet[5], 
                     otvet[6], 
                     tea, 
                     rea]
            if otvet[4] != '':
                rowx = [otvet[0], 
                        otvet[1], 
                        otvet[2], 
                        otvet[4], 
                        otvet[6][0], 
                        otvet[5], 
                        otvet[7]]
                if otvet[8] > 0:
                    rowx.append(1)
                else:
                    rowx.append(0)
                rowx.append(otvet[8])
                if otvet[8] == 1:
                    rowx.append(0.973)
                elif otvet[8] == 0.5:
                    rowx.append(0.633)
                else:
                    rowx.append(0.0295)
                self.get_object("main_liststore").append(row=rowx)
                etal_otv = ""
                for otv in otvet[6]:
                    etal_otv += otv + ";"
                out_file.write(str(otvet[0]) + "\n" 
                        + str(otvet[1]) 
                        + "\n" + str(otvet[2]) 
                        + "\n" + str(otvet[3]) 
                        + "\n" + str(otvet[4]) 
                        + "\n" + str(otvet[5]) 
                        + "\n" + str(etal_otv) 
                        + "\n" + str(otvet[7])
                        + "\n" + "1.000000"
                        + "\n" + str(otvet[8]) + "\n\n")
#            if otvet[1] not in self.std.keys():
#                self.dbs.tcur.execute("""SELECT b.firstname, b.lastname 
#                                    FROM mdl_quiz_attempts a 
#                                    LEFT OUTER JOIN mdl_user b 
#                                    ON a.userid = b.id WHERE a.id=%s""", 
#                                    (otvet[1],))
#                name = self.dbs.tcur.fetchone()
#                self.std[otvet[1]] = {"name": name[0] + " " + name[1], #ФИО
#                                      "kol": 0, #Сколько вопросов с ответом
#                                      "sum": otvet[8], #Сколько за них баллов
#                                      "k": 1.0 #Сколько всего вопросов
#                                      } 
#                if otvet[8] > 0:
#                    self.std[otvet[1]]["kol"] += 1
#            else:
#                self.std[otvet[1]]["sum"] += otvet[8]
#                self.std[otvet[1]]["k"] += 1.0
#                if otvet[8] > 0:
#                    self.std[otvet[1]]["kol"] += 1
#        out_file.close()
#        out_file2 = open("out2.txt", "wb")
#        tetal = self.get_object("teta_liststore")
#        for i in self.std.keys():
#            rowx = [i, #№ Попытки
#                    self.std[i]["name"], #ФИО
#                    self.std[i]["kol"] / self.std[i]["k"], # тета_1
#                    self.std[i]["sum"] / self.std[i]["k"] # тета_2
#                    ]
#            tetal.append(row=rowx)
#            out_file2.write(str(rowx[0]) + "; " 
#                            + rowx[1] + "; " 
#                            + str(rowx[2]) + "; " 
#                            + str(rowx[3]) + ";\n")
#        out_file2.close()


if __name__ == "__main__":
    FORM = MainForm()
    FORM.main()