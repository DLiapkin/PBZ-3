from typing import List

import rdflib
from rdflib import Graph
from rdflib.namespace import OWL, RDF

import tkinter
from tkinter import *
from tkinter import Tk, Frame, NO
import tkinter.ttk as ttk
from tkinter.filedialog import askopenfilename, asksaveasfile

from View import query_view as que, creation_view as crv
from Models import ontoClass as oCl, ontoObjProperty as oP


class App(Tk):
    class_dictionary = []
    obj_properties = []
    individuals_dictionary = []
    graph = Graph()
    ontology_iri = ''

    def __init__(self):
        super().__init__()
        main_menu = Menu(self)
        main_menu.add_command(label='Загрузить', command=self.load_ontology)
        main_menu.add_command(label='Сохранить', command=self.save_ontology)
        main_menu.add_command(label='Обновить', command=self.update_tables)
        main_menu.add_command(label="SPARQL query", command=self.query_window)
        main_menu.add_command(label="Добавление", command=self.creation_window)
        main_menu.add_command(label="Удаление", command=self.delete_item)
        self.config(menu=main_menu)

        self.tab_label = Label(self, text="Текущая страница:")
        # self.tab_label.pack()
        notebook_lists = ["Classes", "Object properties", "Individuals"]
        self.notebook = ttk.Notebook(self, width=600, height=600)
        vocabulary_frame = Frame(self.notebook, bd=2)
        obj_prop_frame = Frame(self.notebook, bd=2)
        individuals_tree_frame = Frame(self.notebook, bd=2)
        self.notebook.add(vocabulary_frame, text=notebook_lists[0], underline=0, sticky=tkinter.NE + tkinter.SW)
        self.notebook.add(obj_prop_frame, text=notebook_lists[1], underline=0, sticky=tkinter.NE + tkinter.SW)
        self.notebook.add(individuals_tree_frame, text=notebook_lists[2], underline=0, sticky=tkinter.NE + tkinter.SW)
        self.notebook.enable_traversal()
        # self.notebook.bind("<<NotebookTabChanged>>", self.select_tab)

        self.vocabularyTree = ttk.Treeview(vocabulary_frame, show='tree', height=30)
        self.vocabularyTree.column('#0', stretch=YES, minwidth=0, width=600)
        self.vocabularyTree.grid_rowconfigure(0, weight=1)
        self.vocabularyTree.grid_columnconfigure(0, weight=1)
        self.vocabularyTree.grid(row=0, column=0, sticky='nsew')

        self.objPropTree = ttk.Treeview(obj_prop_frame, columns=("Subject", "Predicate", "Object"),
                                        selectmode='browse', height=30)
        self.objPropTree.heading('Subject', text="Subject", anchor='center')
        self.objPropTree.heading('Predicate', text="Predicate", anchor='center')
        self.objPropTree.heading('Object', text="Object", anchor='center')
        self.objPropTree.column('#0', stretch=NO, minwidth=0, width=0)
        self.objPropTree.column('#1', stretch=NO, minwidth=100, width=200)
        self.objPropTree.column('#2', stretch=NO, minwidth=100, width=200)
        self.objPropTree.column('#3', stretch=NO, minwidth=100, width=200)
        self.objPropTree.grid(row=0, column=0, sticky='nsew')

        self.individualsTree = ttk.Treeview(
            individuals_tree_frame, columns="Individuals", selectmode='browse', height=30)
        self.individualsTree.heading('Individuals', text="Individuals", anchor='center')
        self.individualsTree.column('#0', stretch=NO, minwidth=0, width=0)
        self.individualsTree.column('#1', stretch=NO, minwidth=100, width=600)
        self.individualsTree.grid(row=0, column=0, sticky='nsew')

        self.notebook.pack()

    # def select_tab(self, event):
    #     tab_id = self.notebook.select()
    #     tab_name = self.notebook.tab(tab_id, "text")
    #     text = "Текущая страница: {}".format(tab_name)
    #     self.tab_label.config(text=text)

    def select_tab(self):
        tab_id = self.notebook.select()
        tab_name = self.notebook.tab(tab_id, "text")
        return tab_name

    def delete_item(self):
        curr_tab = self.select_tab()
        if curr_tab == "Classes":
            selected = self.vocabularyTree.focus()
            temp = self.vocabularyTree.item(selected, 'text')
            for cl in self.class_dictionary:
                if cl.name == temp:
                    self.class_dictionary.remove(cl)
            del_uri = rdflib.URIRef(self.ontology_iri + temp)
            self.graph.remove((del_uri, None, None))
            self.graph.remove((None, None, del_uri))
        if curr_tab == "Object properties":
            selected = self.objPropTree.focus()
            temp = self.objPropTree.item(selected, 'values')
            for ob in self.obj_properties:
                if ob.subject == temp[0] and ob.name == temp[1] and \
                        ob.object == temp[2]:
                    self.obj_properties.remove(ob)
            del_sub = rdflib.URIRef(self.ontology_iri + temp[0])
            del_pre = rdflib.URIRef(self.ontology_iri + temp[1])
            del_obj = rdflib.URIRef(self.ontology_iri + temp[2])
            self.graph.remove((del_sub, del_pre, del_obj))
        if curr_tab == "Individuals":
            selected = self.individualsTree.focus()
            temp = self.individualsTree.item(selected, 'values')
            self.individuals_dictionary.remove(temp[0])
            del_uri = rdflib.URIRef(self.ontology_iri + temp[0])
            for ob in self.obj_properties:
                if ob.subject == temp[0] or ob.object == temp[0]:
                    self.obj_properties.remove(ob)
            self.graph.remove((del_uri, None, None))
            self.graph.remove((None, None, del_uri))

    def find_root_class(self) -> List:
        root_classes = self.class_dictionary.copy()
        for c in self.class_dictionary:
            for cl in self.class_dictionary:
                if cl.subClasses.__contains__(c.name):
                    root_classes.remove(c)
        return root_classes

    def update_tables(self):
        self.vocabularyTree.delete(*self.vocabularyTree.get_children())
        temp: list = []
        rt_classes = self.find_root_class()
        for oc in rt_classes:
            if not temp.__contains__(oc.name):
                self.create_node(temp, oc.name, '')
        self.update_obj_property_table()
        self.update_individuals_table()

    def update_obj_property_table(self):
        self.objPropTree.delete(*self.objPropTree.get_children())
        for ob in self.obj_properties:
            self.objPropTree.insert('', 'end', values=(ob.subject, ob.name, ob.object))

    def update_individuals_table(self):
        self.individualsTree.delete(*self.individualsTree.get_children())
        for ind in self.individuals_dictionary:
            self.individualsTree.insert('', 'end', values=ind)

    def create_node(self, temp: list, current_class: str, old_id: str):
        for cl in self.class_dictionary:
            if not temp.__contains__(cl.name) and cl.name == current_class:
                node_id = self.vocabularyTree.insert(old_id, index="end", text=cl.name, values=[cl.individuals])
                temp.append(cl.name)
                if len(cl.subClasses) != 0:
                    for sub_cl in cl.subClasses:
                        for c in self.class_dictionary:
                            if c.name == sub_cl and not temp.__contains__(c.name):
                                self.create_node(temp, sub_cl, node_id)

    def clear_table(self):
        self.vocabularyTree.delete(*self.vocabularyTree.get_children())
        self.objPropTree.delete(*self.objPropTree.get_children())
        self.individualsTree.delete(*self.individualsTree.get_children())
        self.class_dictionary.clear()
        self.obj_properties.clear()
        self.individuals_dictionary.clear()

    def load_ontology(self):
        filename = askopenfilename(filetypes=(("owl file", "*.owl"),), defaultextension=("owl file", "*.owl"))
        if filename is None:
            return

        self.graph = Graph().parse(filename)
        self.title(filename)
        self.clear_table()
        for s, p, o in self.graph:
            if p == RDF.type and o == OWL.Ontology:
                self.ontology_iri = s.__repr__().replace('rdflib.term.URIRef(\'', '')[:-2] + '#'
        self.load_classes()
        self.load_properties()
        self.load_individuals()
        self.update_tables()

    def load_classes(self):
        for s, p, o in self.graph:
            s_str = s.__repr__()
            if o == OWL.Class and p == RDF.type:
                oc = oCl.OClass()
                oc.name = s_str.replace(f'rdflib.term.URIRef(\'{self.ontology_iri}', '')[:-2]
                for sub, pre, obj in self.graph:
                    if pre.__repr__() == 'rdflib.term.URIRef(\'http://www.w3.org/2000/01/rdf-schema#subClassOf\')' and \
                            obj.__repr__() == s_str:
                        oc.subClasses.append(
                            sub.__repr__().replace(f'rdflib.term.URIRef(\'{self.ontology_iri}', '')[:-2])
                    if pre.__repr__() == 'rdflib.term.URIRef(\'http://www.w3.org/1999/02/22-rdf-syntax-ns#type\')' and \
                            obj.__repr__() == s_str:
                        oc.individuals.append(
                            sub.__repr__().replace(f'rdflib.term.URIRef(\'{self.ontology_iri}', '')[:-2])
                self.class_dictionary.append(oc)

    def load_properties(self):
        # repeats = []
        for s, p, o in self.graph:
            s_str = s.__repr__()
            if o == OWL.ObjectProperty and p == RDF.type:
                for sub, pre, obj in self.graph:
                    # if not repeats.__contains__(
                    #         sub.__repr__().replace(f'rdflib.term.URIRef(\'{self.ontology_iri}', '')[:-2]) and \
                    #         pre.__repr__() == s_str:
                    if pre.__repr__() == s_str:
                        ob = oP.ObjectProperty()
                        ob.name = s_str.replace(f'rdflib.term.URIRef(\'{self.ontology_iri}', '')[:-2]
                        ob.subject = sub.__repr__().replace(f'rdflib.term.URIRef(\'{self.ontology_iri}', '')[:-2]
                        ob.object = obj.__repr__().replace(f'rdflib.term.URIRef(\'{self.ontology_iri}', '')[:-2]
                        # repeats.append(sub.__repr__().replace(f'rdflib.term.URIRef(\'{self.ontology_iri}', '')[:-2])
                        self.obj_properties.append(ob)

    def load_individuals(self):
        repeats = []
        for s, p, o in self.graph:
            s_str = s.__repr__()
            if o == OWL.NamedIndividual and p == RDF.type:
                ind = s_str.replace(f'rdflib.term.URIRef(\'{self.ontology_iri}', '')[:-2]
                repeats.append(ind)
                self.individuals_dictionary.append(ind)

    def query_window(self):
        query_win = que.Query(self, self.graph)
        query_win.grab_set()

    def creation_window(self):
        creation_win = crv.Creation(
            self, self.graph, self.class_dictionary, self.obj_properties, self.individuals_dictionary
        )
        creation_win.grab_set()

    # сохраняет онтологию в файл
    # да, вот так просто)
    def save_ontology(self):
        file = asksaveasfile(filetypes=(("owl file", "*.owl"),), defaultextension=("owl file", "*.owl"))
        if file is None:
            return
        self.graph.serialize(destination=file.name, format="xml")
