import tkinter as tk
from tkinter import Radiobutton, Label, Button, Entry, Frame, IntVar, messagebox
import tkinter.ttk as ttk

from rdflib import Graph, URIRef
from rdflib.namespace import OWL, RDF, RDFS


class Creation(tk.Toplevel):
    ontology = Graph()
    ontology_iri = ''
    class_dictionary = []
    obj_properties = []
    individuals_dictionary = []

    def __init__(self, parent, graph):
        super().__init__(parent)
        ttk.Style().configure("TButton", padding=(0, 5, 0, 5), font='serif 10')
        self.creation_frame = Frame(self, bd=2)

        # создание и добавление основного окна и ввода названия сущности
        name_label = Label(self.creation_frame, text="Name", width=10)
        self.name_text = Entry(self.creation_frame, width=30)
        self.create_button = Button(self.creation_frame, text="Create", width=15)
        self.create_button.config(command=self.add_new_item)

        self.creation_frame.grid(row=0, column=0)
        name_label.grid(row=1, column=0)
        self.name_text.grid(row=1, column=2, columnspan=2)

        # создание радиокнопок с переменной статуса
        self.choosing_value = IntVar()
        self.choosing_value.set(0)
        create_class = Radiobutton(
            self.creation_frame, text="Class", variable=self.choosing_value, value=0
        )
        create_obj_prop = Radiobutton(
            self.creation_frame, text="Object property", variable=self.choosing_value, value=1
        )
        create_individual = Radiobutton(
            self.creation_frame, text="Individual", variable=self.choosing_value, value=2
        )
        choose_button = Button(self.creation_frame, text="Choose", width=15)
        choose_button.config(command=self.change_status)

        # добавление радиокнопок
        create_class.grid(row=2, column=2)
        create_obj_prop.grid(row=3, column=2)
        create_individual.grid(row=4, column=2)
        choose_button.grid(row=5, column=2)

        # создание компонентов панели для создания класса
        self.create_class_frame = Frame(self.creation_frame, bd=2)
        is_subclass_label = Label(self.create_class_frame, text="Subclass of")
        self.is_subclass_of_entry = Entry(self.create_class_frame, width=30)
        subclasses_label = Label(self.create_class_frame, text="Subclasses")
        self.subclasses_entry = Entry(self.create_class_frame, width=30)

        # добавление компонентов панели для создания класса
        is_subclass_label.grid(row=0, column=0)
        self.is_subclass_of_entry.grid(row=0, column=2)
        subclasses_label.grid(row=1, column=0)
        self.subclasses_entry.grid(row=1, column=2)

        # создание компонентов панели для создания object property
        self.create_objprop_frame = Frame(self.creation_frame, bd=2)
        who_is_subject_label = Label(self.create_objprop_frame, text="Subject")
        self.subject_entry = Entry(self.create_objprop_frame, width=30)
        who_is_object_label = Label(self.create_objprop_frame, text="Object")
        self.object_entry = Entry(self.create_objprop_frame, width=30)

        # добавление компонентов панели для создания класса
        who_is_subject_label.grid(row=0, column=0)
        self.subject_entry.grid(row=0, column=2)
        who_is_object_label.grid(row=1, column=0)
        self.object_entry.grid(row=1, column=2)

        # создание компонентов панели для создания экземпляра класса (individual)
        self.create_individual_frame = Frame(self.creation_frame, bd=2)
        parent_class_label = Label(self.create_individual_frame, text="Parent")
        self.parent_entry = Entry(self.create_individual_frame, width=30)

        # добавление компонентов панели для создания экземпляра класса
        parent_class_label.grid(row=0, column=0)
        self.parent_entry.grid(row=0, column=2)

        self.ontology = graph
        for s, p, o in graph:
            if p == RDF.type and \
                    o == OWL.Ontology:
                self.ontology_iri = s.__repr__().replace(
                    'rdflib.term.URIRef(\'', '')[:-2] + '#'

        self.wait_window()

    def change_status(self):
        if self.choosing_value.get() == 0:
            # очистка окна от других панелей
            self.create_objprop_frame.grid_forget()
            self.create_individual_frame.grid_forget()
            self.create_button.grid_forget()

            # добавление нужной панели и кнопки
            self.create_class_frame.grid(row=6, column=0, columnspan=4)
            self.create_button.grid(row=9, column=2)
        if self.choosing_value.get() == 1:
            self.create_class_frame.grid_forget()
            self.create_individual_frame.grid_forget()
            self.create_button.grid_forget()

            self.create_objprop_frame.grid(row=6, column=0, columnspan=4)
            self.create_button.grid(row=9, column=2)
        if self.choosing_value.get() == 2:
            self.create_class_frame.grid_forget()
            self.create_objprop_frame.grid_forget()
            self.create_button.grid_forget()

            self.create_individual_frame.grid(row=6, column=0, columnspan=4)
            self.create_button.grid(row=8, column=2)

    def add_new_class(self):
        name = self.name_text.get()
        subclass_of = self.is_subclass_of_entry.get()
        temp = self.subclasses_entry.get()

        while subclass_of.__contains__(' '):
            subclass_of.replace(' ', '')

        while temp.__contains__(' '):
            temp.replace(' ', '')
        subclasses = temp.split(',')

        # создаю объекты-ссылки rdf для класса и его родителя
        class_uri = URIRef(self.ontology_iri + name)

        # есть ли добавляемый класс в онтологии
        is_present = False
        for sub, pred, obj in self.ontology:
            if sub == class_uri:
                is_present = True

        if is_present:
            messagebox.showerror(title="Ошибка создания класса",
                                 message="Класс с таким названием уже находится в онтологии!")
            return

        # добавляю тройку Subject Predicate Object в текущую онтологию
        # тройка для добавляемого класса
        self.ontology.add((class_uri, RDF.type, OWL.Class))
        if len(subclass_of) != 0:
            subclass_of_uri = URIRef(self.ontology_iri + subclass_of)
            # тройка для отношения subClassOf между добавляемым классом и его родителем
            self.ontology.add((class_uri, RDFS.subClassOf, subclass_of_uri))

        # добавляю аналогичные тройки для подклассов добавляемого класса
        if len(subclasses) != 1 or (subclasses[0] != '' and subclasses[0] != ' '):
            for sub in subclasses:
                sub_uri = URIRef(self.ontology_iri + sub)
                is_present = False
                for s, p, o in self.ontology:
                    if s == sub_uri:
                        is_present = True
                if is_present:
                    self.ontology.add((sub_uri, RDFS.subClassOf, class_uri))
                else:
                    self.ontology.add((sub_uri, RDF.type, OWL.Class))
                    self.ontology.add((sub_uri, RDFS.subClassOf, class_uri))

    def add_new_obj_property(self):
        name = self.name_text.get()
        subject_op = self.subject_entry.get()
        object_op = self.object_entry.get()

        while subject_op.__contains__(' '):
            subject_op.replace(' ', '')

        while object_op.__contains__(' '):
            object_op.replace(' ', '')

        name_uri = URIRef(self.ontology_iri + name)

        is_present = False
        for s, p, o in self.ontology:
            if s == name_uri:
                is_present = True

        if not is_present:
            self.ontology.add((name_uri, RDF.type, OWL.ObjectProperty))
        if len(subject_op) != 0 and len(object_op):
            subject_uri = URIRef(self.ontology_iri + subject_op)
            object_uri = URIRef(self.ontology_iri + object_op)

            is_present1 = False
            is_present2 = False
            for s, p, o in self.ontology:
                if s == subject_uri:
                    is_present1 = True
                if s == object_uri:
                    is_present2 = True

            if not is_present1 or not is_present2:
                messagebox.showerror(title="Ошибка создания отношения",
                                     message="Экземпляра с таким названием не существует в онтологии!")
                return

            self.ontology.add((subject_uri, name_uri, object_uri))

    def add_new_individual(self):
        name = self.name_text.get()
        parent = self.parent_entry.get()

        while parent.__contains__(' '):
            parent.replace(' ', '')

        name_uri = URIRef(self.ontology_iri + name)
        parent_uri = URIRef(self.ontology_iri + parent)

        for s, p, o in self.ontology:
            if s == name_uri:
                messagebox.showerror(title="Ошибка создания экземпляра",
                                     message="Экземпляр с таким названием уже находится в онтологии!")
                return

        is_present = False
        for s, p, o in self.ontology:
            if s == parent_uri:
                is_present = True

        if not is_present:
            messagebox.showerror(title="Ошибка создания экземпляра",
                                 message="Класса с таким названием не существует в онтологии!")
            return

        self.ontology.add((name_uri, RDF.type, OWL.NamedIndividual))
        self.ontology.add((name_uri, RDF.type, parent_uri))

    def add_new_item(self):
        if self.choosing_value.get() == 0:
            self.add_new_class()

        if self.choosing_value.get() == 1:
            self.add_new_obj_property()

        if self.choosing_value.get() == 2:
            self.add_new_individual()

        self.destroy()
