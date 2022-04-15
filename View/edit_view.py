import tkinter as tk
from tkinter import Radiobutton, Label, Button, Entry, Frame, IntVar, messagebox
import tkinter.ttk as ttk

from rdflib import Graph, URIRef
from rdflib.namespace import OWL, RDF, RDFS


class Edit(tk.Toplevel):
    ontology = Graph()
    ontology_iri = ''

    def __init__(self, parent, graph):
        super().__init__(parent)
        ttk.Style().configure("TButton", padding=(0, 5, 0, 5), font='serif 10')
        self.edit_frame = Frame(self, bd=2)

        # создание и добавление основного окна и ввода названия сущности
        name_label = Label(self.edit_frame, text="Name", width=10)
        self.name_text = Entry(self.edit_frame, width=30)
        self.edit_button = Button(self.edit_frame, text="Edit", width=15)
        self.edit_button.config(command=self.edit_item)

        self.edit_frame.grid(row=0, column=0)
        name_label.grid(row=1, column=0)
        self.name_text.grid(row=1, column=2, columnspan=2)

        # создание радиокнопок с переменной статуса
        self.choosing_value = IntVar()
        self.choosing_value.set(0)
        edit_class = Radiobutton(
            self.edit_frame, text="Class", variable=self.choosing_value, value=0
        )
        edit_obj_prop = Radiobutton(
            self.edit_frame, text="Object property", variable=self.choosing_value, value=1
        )
        edit_individual = Radiobutton(
            self.edit_frame, text="Individual", variable=self.choosing_value, value=2
        )
        choose_button = Button(self.edit_frame, text="Choose", width=15)
        choose_button.config(command=self.change_status)

        # добавление радиокнопок
        edit_class.grid(row=2, column=2)
        edit_obj_prop.grid(row=3, column=2)
        edit_individual.grid(row=4, column=2)
        choose_button.grid(row=5, column=2)

        # создание компонентов панели для редактирования класса
        self.edit_class_frame = Frame(self.edit_frame, bd=2)
        class_name_change_label = Label(self.edit_class_frame, text="New name")
        self.class_name_change_entry = Entry(self.edit_class_frame, width=30)
        parent_change_label = Label(self.edit_class_frame, text="Parent of:")
        self.parent_change_entry = Entry(self.edit_class_frame, width=30)

        # добавление компонентов панели для редактирования класса
        class_name_change_label.grid(row=0, column=0)
        self.class_name_change_entry.grid(row=0, column=2)
        parent_change_label.grid(row=1, column=0)
        self.parent_change_entry.grid(row=1, column=2)

        # создание компонентов панели для редактирования object property
        self.edit_objprop_frame = Frame(self.edit_frame, bd=2)
        change_objprop_name_label = Label(self.edit_objprop_frame, text="New name")
        self.change_objprop_name_entry = Entry(self.edit_objprop_frame, width=30)
        new_subject_label = Label(self.edit_objprop_frame, text="New subject")
        self.new_subject_entry = Entry(self.edit_objprop_frame, width=30)
        new_object_label = Label(self.edit_objprop_frame, text="New object")
        self.new_object_entry = Entry(self.edit_objprop_frame, width=30)
        who_is_subject_label = Label(self.edit_objprop_frame, text="Subject")
        self.subject_entry = Entry(self.edit_objprop_frame, width=30)
        who_is_object_label = Label(self.edit_objprop_frame, text="Object")
        self.object_entry = Entry(self.edit_objprop_frame, width=30)

        # добавление компонентов панели для редактирования object property
        who_is_subject_label.grid(row=0, column=0)
        self.subject_entry.grid(row=0, column=2)
        who_is_object_label.grid(row=1, column=0)
        self.object_entry.grid(row=1, column=2)
        change_objprop_name_label.grid(row=2, column=0)
        self.change_objprop_name_entry.grid(row=2, column=2)
        new_subject_label.grid(row=3, column=0)
        self.new_subject_entry.grid(row=3, column=2)
        new_object_label.grid(row=4, column=0)
        self.new_object_entry.grid(row=4, column=2)

        # создание компонентов панели для редактирования экземпляра класса (individual)
        self.edit_individual_frame = Frame(self.edit_frame, bd=2)
        change_ind_name = Label(self.edit_individual_frame, text="New name")
        self.change_ind_name_entry = Entry(self.edit_individual_frame, width=30)
        parent_class_label = Label(self.edit_individual_frame, text="Parent")
        self.parent_entry = Entry(self.edit_individual_frame, width=30)

        # добавление компонентов панели для редактирования экземпляра класса
        change_ind_name.grid(row=0, column=0)
        self.change_ind_name_entry.grid(row=0, column=2)
        parent_class_label.grid(row=1, column=0)
        self.parent_entry.grid(row=1, column=2)

        self.ontology: Graph = graph
        for s, p, o in graph:
            if p == RDF.type and \
                    o == OWL.Ontology:
                self.ontology_iri = s.__repr__().replace(
                    'rdflib.term.URIRef(\'', '')[:-2] + '#'

        self.wait_window()

    def change_status(self):
        if self.choosing_value.get() == 0:
            # очистка окна от других панелей
            self.edit_objprop_frame.grid_forget()
            self.edit_individual_frame.grid_forget()
            self.edit_button.grid_forget()

            # добавление нужной панели и кнопки
            self.edit_class_frame.grid(row=6, column=0, columnspan=4)
            self.edit_button.grid(row=9, column=2)
        if self.choosing_value.get() == 1:
            # очистка окна от других панелей
            self.edit_class_frame.grid_forget()
            self.edit_individual_frame.grid_forget()
            self.edit_button.grid_forget()

            # добавление нужной панели и кнопки
            self.edit_objprop_frame.grid(row=6, column=0, columnspan=4)
            self.edit_button.grid(row=12, column=2)
        if self.choosing_value.get() == 2:
            # очистка окна от других панелей
            self.edit_class_frame.grid_forget()
            self.edit_objprop_frame.grid_forget()
            self.edit_button.grid_forget()

            # добавление нужной панели и кнопки
            self.edit_individual_frame.grid(row=6, column=0, columnspan=4)
            self.edit_button.grid(row=9, column=2)

    def edit_class(self):
        name: str = self.name_text.get()
        new_name: str = self.class_name_change_entry.get()
        new_parent: str = self.parent_change_entry.get()

        class_uri = URIRef(self.ontology_iri + name)

        while new_name.__contains__(' '):
            new_name = new_name.replace(' ', '')

        while new_parent.__contains__(' '):
            new_parent = new_parent.replace(' ', '')

        if len(new_parent) != 0:
            new_parent_uri = URIRef(self.ontology_iri + new_parent)
            is_present = False
            for s, p, o in self.ontology:
                if s == new_parent_uri:
                    is_present = True

            if not is_present:
                messagebox.showerror(title="Ошибка редактирования класса",
                                     message="Родительского класса с таким названием не существует в онтологии!")
                return

            for s, p, o in self.ontology:
                if s == class_uri and p == RDFS.subClassOf:
                    self.ontology.remove((s, p, o))

            self.ontology.add((class_uri, RDFS.subClassOf, new_parent_uri))

        if len(new_name) != 0:
            new_name_uri = URIRef(self.ontology_iri + new_name)

            is_present = False
            for s, p, o in self.ontology:
                if s == class_uri or o == class_uri:
                    is_present = True

            if not is_present:
                messagebox.showerror(title="Ошибка редактирования класса",
                                     message="Класса с таким названием не существует в онтологии!")
                return

            old_class_sub_rel = []
            old_class_obj_rel = []
            for sub, pred, obj in self.ontology:
                if sub == class_uri:
                    old_class_sub_rel.append((sub, pred, obj))
                if obj == class_uri:
                    old_class_obj_rel.append((sub, pred, obj))

            self.ontology.remove((class_uri, None, None))
            self.ontology.remove((None, None, class_uri))

            for tr in old_class_sub_rel:
                new_tr = (new_name_uri, tr[1], tr[2])
                self.ontology.add(new_tr)

            for tr in old_class_obj_rel:
                new_tr = (tr[0], tr[1], new_name_uri)
                self.ontology.add(new_tr)

    def edit_obj_property(self):
        name = self.name_text.get()
        subject_op = self.subject_entry.get()
        object_op = self.object_entry.get()

        new_name = self.change_objprop_name_entry.get()
        new_subject = self.new_subject_entry.get()
        new_object = self.new_object_entry.get()

        name_uri = URIRef(self.ontology_iri + name)
        subject_uri = URIRef(self.ontology_iri + subject_op)
        object_uri = URIRef(self.ontology_iri + object_op)

        if (len(new_subject) != 0 or len(new_object) != 0) and \
                (len(subject_op) != 0 and len(object_op) != 0):
            is_present1 = False
            is_present2 = False
            for s, p, o in self.ontology:
                if s == subject_uri and o == OWL.NamedIndividual:
                    is_present1 = True
                if s == object_uri and o == OWL.NamedIndividual:
                    is_present2 = True

            if not is_present1 or not is_present2:
                messagebox.showerror(title="Ошибка создания отношения",
                                     message="Экземпляров с такими названиями не существует в онтологии!")
                return

            is_present = False
            for s, p, o in self.ontology:
                if s == subject_uri and p == name_uri and o == object_uri:
                    is_present = True

            if not is_present:
                messagebox.showerror(title="Ошибка создания отношения",
                                     message="Такого отношения не существует в онтологии!")
                return
        else:
            is_present = False
            for s, p, o in self.ontology:
                if p == name_uri or s == name_uri:
                    is_present = True

            if not is_present:
                messagebox.showerror(title="Ошибка создания отношения",
                                     message="Такого отношения не существует в онтологии!")
                return

        if len(new_subject) != 0 and len(new_object) == 0:
            new_subject_uri = URIRef(self.ontology_iri + new_subject)
            for s, p, o in self.ontology:
                if s == subject_uri and p == name_uri and o == object_uri:
                    self.ontology.remove((s, p, o))
                    self.ontology.add((new_subject_uri, p, o))
        if len(new_subject) == 0 and len(new_object) != 0:
            new_object_uri = URIRef(self.ontology_iri + new_object)
            for s, p, o in self.ontology:
                if s == subject_uri and p == name_uri and o == object_uri:
                    self.ontology.remove((s, p, o))
                    self.ontology.add((s, p, new_object_uri))
        if len(new_subject) != 0 and len(new_object) != 0:
            new_subject_uri = URIRef(self.ontology_iri + new_subject)
            new_object_uri = URIRef(self.ontology_iri + new_object)
            for s, p, o in self.ontology:
                if s == subject_uri and p == name_uri and o == object_uri:
                    self.ontology.remove((s, p, o))
                    self.ontology.add((new_subject_uri, p, new_object_uri))
        if len(new_name) != 0:
            new_name_uri = URIRef(self.ontology_iri + new_name)

            old_prop_rel = []
            old_prop_sub_rel = []
            old_prop_obj_rel = []
            for sub, pred, obj in self.ontology:
                if pred == name_uri:
                    old_prop_rel.append((sub, pred, obj))

            for sub, pred, obj in self.ontology:
                if sub == name_uri:
                    old_prop_sub_rel.append((sub, pred, obj))

            for sub, pred, obj in self.ontology:
                if obj == name_uri:
                    old_prop_obj_rel.append((sub, pred, obj))

            self.ontology.remove((None, name_uri, None))
            self.ontology.remove((name_uri, None, None))
            self.ontology.remove((None, None, name_uri))

            for tr in old_prop_rel:
                new_tr = (tr[0], new_name_uri, tr[2])
                self.ontology.add(new_tr)

            for tr in old_prop_sub_rel:
                new_tr = (new_name_uri, tr[1], tr[2])
                self.ontology.add(new_tr)

            for tr in old_prop_obj_rel:
                new_tr = (tr[0], tr[1], new_name_uri)
                self.ontology.add(new_tr)

    def edit_individual(self):
        name = self.name_text.get()
        new_name = self.change_ind_name_entry.get()
        parent = self.parent_entry.get()

        name_uri = URIRef(self.ontology_iri + name)

        while new_name.__contains__(' '):
            new_name = new_name.replace(' ', '')

        while parent.__contains__(' '):
            parent = parent.replace(' ', '')

        is_present = False
        for s, p, o in self.ontology:
            if s == name_uri or o == name_uri:
                is_present = True

        if not is_present:
            messagebox.showerror(title="Ошибка редактирования экземпляра",
                                 message="Экземпляра с таким названием не существует в онтологии!")
            return

        if len(parent) != 0:
            new_parent_uri = URIRef(self.ontology_iri + parent)
            is_present = False
            for s, p, o in self.ontology:
                if s == new_parent_uri:
                    is_present = True

            if not is_present:
                messagebox.showerror(title="Ошибка редактирования экземпляра",
                                     message="Родительского класса с таким названием не существует в онтологии!")
                return

            for s, p, o in self.ontology:
                if s == name_uri and p == RDF.type and not o == OWL.NamedIndividual:
                    self.ontology.remove((s, p, o))

            self.ontology.add((name_uri, RDF.type, new_parent_uri))

        if len(new_name) != 0:
            new_name_uri = URIRef(self.ontology_iri + new_name)

            old_ind_sub_rel = []
            old_ind_obj_rel = []
            for sub, pred, obj in self.ontology:
                if sub == name_uri:
                    old_ind_sub_rel.append((sub, pred, obj))
                if obj == name_uri:
                    old_ind_obj_rel.append((sub, pred, obj))

            self.ontology.remove((name_uri, None, None))
            self.ontology.remove((None, None, name_uri))

            for tr in old_ind_sub_rel:
                new_tr = (new_name_uri, tr[1], tr[2])
                self.ontology.add(new_tr)

            for tr in old_ind_obj_rel:
                new_tr = (tr[0], tr[1], new_name_uri)
                self.ontology.add(new_tr)

    def edit_item(self):
        if self.choosing_value.get() == 0:
            self.edit_class()

        if self.choosing_value.get() == 1:
            self.edit_obj_property()

        if self.choosing_value.get() == 2:
            self.edit_individual()

        self.destroy()
