import tkinter

from rdflib import Graph
from tkinter import Tk, Label, Button, Entry, END, Frame, NO, W, WORD, Text
import tkinter.ttk as ttk


class Query(tkinter.Toplevel):
    query_text: Text
    result_tree: ttk.Treeview
    ontology = Graph()
    ontology_iri = ''

    def __init__(self, parent, graph):
        super().__init__(parent)
        self.ontology = graph
        input_frame = Frame(self, bd=2)
        self.query_text = Text(input_frame, height=10, width=70, wrap=WORD)
        query_button = Button(input_frame, text="Query", width=30, height=3)
        query_button.config(command=self.get_query_result)
        self.result_tree = ttk.Treeview(input_frame, columns=("Subject", "Predicate", "Object"), selectmode='browse',
                                        height=5)
        self.result_tree.heading('Subject', text="Subject", anchor='center')
        self.result_tree.heading('Predicate', text="Predicate", anchor='center')
        self.result_tree.heading('Object', text="Object", anchor='center')
        self.result_tree.column('#0', stretch=NO, minwidth=0, width=0)
        self.result_tree.column('#1', stretch=NO, minwidth=10, width=200)
        self.result_tree.column('#2', stretch=NO, minwidth=10, width=200)
        self.result_tree.column('#3', stretch=NO, minwidth=10, width=200)

        for s, p, o in graph:
            if p.__repr__() == 'rdflib.term.URIRef(\'http://www.w3.org/1999/02/22-rdf-syntax-ns#type\')' and \
                    o.__repr__() == 'rdflib.term.URIRef(\'http://www.w3.org/2002/07/owl#Ontology\')':
                self.ontology_iri = s.__repr__().replace(
                    'rdflib.term.URIRef(\'', '')[:-2] + '#'

        input_frame.pack()
        self.query_text.pack()
        query_button.pack()
        self.result_tree.pack()

    def get_query_result(self):
        q = self.query_text.get('1.0', END)
        name = []
        for r in self.ontology.query(q):
            name.append(r)
        self.update_result_tree(name)

    def update_result_tree(self, result):
        for obj in result:
            temp = obj.__repr__().replace(f'rdflib.term.URIRef(\'{self.ontology_iri}', '')[:-2]
            self.result_tree.insert('', 'end', values=temp)
