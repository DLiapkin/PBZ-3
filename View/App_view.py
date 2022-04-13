from typing import List

import rdflib
from rdflib import Graph
from rdflib.namespace import OWL, RDF, RDFS

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
        notebook_lists = ["Classes", "Object properties", "Subject-Predicate-Object", "Individuals"]
        self.notebook = ttk.Notebook(self, width=600, height=600)
        vocabulary_frame = Frame(self.notebook, bd=2)
        obj_prop_frame = Frame(self.notebook, bd=2)
        subj_pred_obj_frame = Frame(self.notebook, bd=2)
        individuals_tree_frame = Frame(self.notebook, bd=2)
        self.notebook.add(vocabulary_frame, text=notebook_lists[0], underline=0, sticky=tkinter.NE + tkinter.SW)
        self.notebook.add(obj_prop_frame, text=notebook_lists[1], underline=0, sticky=tkinter.NE + tkinter.SW)
        self.notebook.add(subj_pred_obj_frame, text=notebook_lists[2], underline=0, sticky=tkinter.NE + tkinter.SW)
        self.notebook.add(individuals_tree_frame, text=notebook_lists[3], underline=0, sticky=tkinter.NE + tkinter.SW)
        self.notebook.enable_traversal()
        # self.notebook.bind("<<NotebookTabChanged>>", self.select_tab)

        self.vocabularyTree = ttk.Treeview(vocabulary_frame, show='tree', height=30)
        self.vocabularyTree.column('#0', stretch=YES, minwidth=0, width=600)
        self.vocabularyTree.grid_rowconfigure(0, weight=1)
        self.vocabularyTree.grid_columnconfigure(0, weight=1)
        self.vocabularyTree.grid(row=0, column=0, sticky='nsew')

        self.objPropTree = ttk.Treeview(obj_prop_frame, show='tree', height=30)
        self.objPropTree.column('#0', stretch=YES, minwidth=0, width=600)
        self.objPropTree.grid_rowconfigure(0, weight=1)
        self.objPropTree.grid_columnconfigure(0, weight=1)
        self.objPropTree.grid(row=0, column=0, sticky='nsew')

        self.subjPredObjTree = ttk.Treeview(subj_pred_obj_frame, columns=("Subject", "Predicate", "Object"),
                                            selectmode='browse', height=30)
        self.subjPredObjTree.heading('Subject', text="Subject", anchor='center')
        self.subjPredObjTree.heading('Predicate', text="Predicate", anchor='center')
        self.subjPredObjTree.heading('Object', text="Object", anchor='center')
        self.subjPredObjTree.column('#0', stretch=NO, minwidth=0, width=0)
        self.subjPredObjTree.column('#1', stretch=NO, minwidth=100, width=200)
        self.subjPredObjTree.column('#2', stretch=NO, minwidth=100, width=200)
        self.subjPredObjTree.column('#3', stretch=NO, minwidth=100, width=200)
        self.subjPredObjTree.grid(row=0, column=0, sticky='nsew')

        self.individualsTree = ttk.Treeview(
            individuals_tree_frame, columns="Individuals", selectmode='browse', height=30)
        self.individualsTree.heading('Individuals', text="Individuals", anchor='center')
        self.individualsTree.column('#0', stretch=NO, minwidth=0, width=0)
        self.individualsTree.column('#1', stretch=NO, minwidth=100, width=600)
        self.individualsTree.grid(row=0, column=0, sticky='nsew')
        self.individualsTree.bind("<Double-1>", self.open_individuals_attributes)

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

    def open_individuals_attributes(self, event):
        item = self.individualsTree.identify('item', event.x, event.y)
        item_name = self.individualsTree.item(item, "value")[0]
        prop_name = '-'
        prop_obj = '-'
        data_prop_name = '-'
        data_prop_value = '-'
        for s, p, o in self.graph:
            if p != RDF.type and s == rdflib.URIRef(self.ontology_iri + item_name):
                for sub, pre, obj in self.graph:
                    if sub == p and obj == OWL.ObjectProperty:
                        prop_name = p.__repr__().replace(f'rdflib.term.URIRef(\'{self.ontology_iri}', '')[:-2]
                        prop_obj = o.__repr__().replace(f'rdflib.term.URIRef(\'{self.ontology_iri}', '')[:-2]
                    if sub == p and obj == OWL.DatatypeProperty:
                        data_prop_name = p.__repr__().replace(f'rdflib.term.URIRef(\'{self.ontology_iri}', '')[:-2]
                        temp: str = o.__repr__().replace(f'rdflib.term.Literal(\'', '')
                        if temp.__contains__(','):
                            index_of_comma = temp.index(',')
                            data_prop_value = temp[0:index_of_comma-1]
                        else:
                            data_prop_value = temp[:-2]

        ind_attr_win = Toplevel()
        ind_frame = Frame(ind_attr_win, bd=2)
        name_label = Label(ind_frame, text="Name", width=10)
        name_value = Label(ind_frame, text=item_name, width=30)

        prop_label = Label(ind_frame, text="Properties", width=30)
        property_value = Label(ind_frame, text=prop_name + ' ' + prop_obj)
        data_prop_value = Label(ind_frame, text=data_prop_name + ' ' + data_prop_value)

        ind_frame.grid(row=0, column=0)
        name_label.grid(row=1, column=0)
        name_value.grid(row=1, column=1)
        prop_label.grid(row=2, column=0)
        property_value.grid(row=2, column=1)
        data_prop_value.grid(row=3, column=1)

        ind_attr_win.grab_set()

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
            selected = self.subjPredObjTree.focus()
            temp = self.subjPredObjTree.item(selected, 'values')
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

    def update_tables(self):
        self.vocabularyTree.delete(*self.vocabularyTree.get_children())
        self.objPropTree.delete(*self.objPropTree.get_children())
        self.subjPredObjTree.delete(*self.subjPredObjTree.get_children())
        self.individualsTree.delete(*self.individualsTree.get_children())
        self.update_classes_table()
        self.update_obj_prop_table()
        self.update_subj_pred_obj_table()
        self.update_individuals_table()

    def find_root_class(self) -> List:
        root_classes = self.class_dictionary.copy()
        for c in self.class_dictionary:
            for cl in self.class_dictionary:
                if cl.subClasses.__contains__(c.name):
                    root_classes.remove(c)
        return root_classes

    def update_classes_table(self):
        temp: list = []
        rt_classes = self.find_root_class()
        for oc in rt_classes:
            if not temp.__contains__(oc.name):
                self.create_class_node(temp, oc.name, '')

    def create_class_node(self, temp: list, current_class: str, old_id: str):
        for cl in self.class_dictionary:
            if not temp.__contains__(cl.name) and cl.name == current_class:
                node_id = self.vocabularyTree.insert(old_id, index="end", text=cl.name, values=[cl.individuals])
                temp.append(cl.name)
                if len(cl.subClasses) != 0:
                    for sub_cl in cl.subClasses:
                        for c in self.class_dictionary:
                            if c.name == sub_cl and not temp.__contains__(c.name):
                                self.create_class_node(temp, sub_cl, node_id)

    def find_root_obj_prop(self) -> List:
        root_properties = []
        for s, p, o in self.graph:
            if o == OWL.ObjectProperty:
                root_properties.append(s)
        for prop in root_properties:
            for sub, pred, obj in self.graph:
                if sub == prop and pred == RDFS.subPropertyOf:
                    root_properties.remove(prop)
        return root_properties

    def update_obj_prop_table(self):
        temp: list = []
        rt_prop = self.find_root_obj_prop()
        for pr in rt_prop:
            if not temp.__contains__(pr):
                self.create_prop_node(temp, pr, '')

    def create_prop_node(self, temp: list, current_prop: str, old_id: str):
        for s, p, o in self.graph:
            if not temp.__contains__(s) and s == current_prop:
                temp_str = s.__repr__().replace(f'rdflib.term.URIRef(\'{self.ontology_iri}', '')[:-2]
                node_id = self.objPropTree.insert(old_id, index="end", text=temp_str)
                temp.append(s)
                for sub, pred, obj in self.graph:
                    if pred == RDFS.subPropertyOf and obj == s:
                        self.create_prop_node(temp, sub, node_id)
                # if len(cl.subClasses) != 0:
                #     for sub_cl in cl.subClasses:
                #         for c in self.class_dictionary:
                #             if c.name == sub_cl and not temp.__contains__(c.name):
                #                 self.create_prop_node(temp, sub_cl, node_id)

    def update_subj_pred_obj_table(self):
        # self.subjPredObjTree.delete(*self.subjPredObjTree.get_children())
        for ob in self.obj_properties:
            self.subjPredObjTree.insert('', 'end', values=(ob.subject, ob.name, ob.object))

    def update_individuals_table(self):
        # self.individualsTree.delete(*self.individualsTree.get_children())
        for ind in self.individuals_dictionary:
            self.individualsTree.insert('', 'end', values=ind)

    def clear_table(self):
        self.vocabularyTree.delete(*self.vocabularyTree.get_children())
        self.objPropTree.delete(*self.objPropTree.get_children())
        self.subjPredObjTree.delete(*self.subjPredObjTree.get_children())
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
        for s, p, o in self.graph:
            s_str = s.__repr__()
            if o == OWL.ObjectProperty and p == RDF.type:
                for sub, pre, obj in self.graph:
                    if pre.__repr__() == s_str:
                        ob = oP.ObjectProperty()
                        ob.name = s_str.replace(f'rdflib.term.URIRef(\'{self.ontology_iri}', '')[:-2]
                        ob.subject = sub.__repr__().replace(f'rdflib.term.URIRef(\'{self.ontology_iri}', '')[:-2]
                        ob.object = obj.__repr__().replace(f'rdflib.term.URIRef(\'{self.ontology_iri}', '')[:-2]
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
        self.update_tables()
        # creation_win.grab_set()
        # creation_win.protocol("WM_DELETE_WINDOW", func=self.update_tables)

    # сохраняет онтологию в файл
    # да, вот так просто)
    def save_ontology(self):
        file = asksaveasfile(filetypes=(("owl file", "*.owl"),), defaultextension=("owl file", "*.owl"))
        if file is None:
            return
        self.graph.serialize(destination=file.name, format="xml")
