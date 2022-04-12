import tkinter

from rdflib import Graph
from rdflib.namespace import OWL, RDF

from tkinter import Button, END, Frame, NO, WORD, Text
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
        self.result_tree.column('#0', stretch=NO, minwidth=0, width=0)
        self.result_tree.column('#1', stretch=NO, minwidth=10, width=200)
        self.result_tree.column('#2', stretch=NO, minwidth=10, width=200)
        self.result_tree.column('#3', stretch=NO, minwidth=10, width=200)

        for s, p, o in graph:
            if p == RDF.type and \
                    o == OWL.Ontology:
                self.ontology_iri = s.__repr__().replace('rdflib.term.URIRef(\'', '')[:-2] + '#'

        q = f"""PREFIX pref:<{self.ontology_iri}>""" + """\nSELECT ?class_name 
        WHERE { ?class_name rdf:type owl:Class }
        """
        self.query_text.insert(0.0, q)
        input_frame.pack()
        self.query_text.pack()
        query_button.pack()
        self.result_tree.pack()

        # выдаёт ошибку, но по крайней мере не блокирует главное окно во время использования этого
        self.attributes(self.callback)

    def callback(self):
        pass

    def get_query_result(self):
        q: str = self.query_text.get('1.0', END)
        temp = q.replace('?', '')
        temp = temp.replace('\n', ' ')
        temp = temp.replace('\t', ' ')
        temp = temp.split(' ')
        while temp.__contains__(''):
            temp.remove('')
        sel_index = temp.index('SELECT') + 1
        if temp.__contains__('DISTINCT'):
            sel_index = temp.index('DISTINCT') + 1
        where_index = temp.index('WHERE')
        headers = temp[sel_index:where_index]
        name = []
        for r in self.ontology.query(q):
            new_triple = []
            t = list(r)
            for obj in t:
                new_triple.append(obj.__repr__().replace(f'rdflib.term.URIRef(\'{self.ontology_iri}', '')[:-2])
            name.append(new_triple)
        self.update_result_tree(name, headers)

    def update_result_tree(self, result, headers):
        self.result_tree.delete(*self.result_tree.get_children())
        self.result_tree.heading('Subject', text='', anchor='center')
        self.result_tree.heading('Predicate', text='', anchor='center')
        self.result_tree.heading('Object', text='', anchor='center')

        self.result_tree.heading('Subject', text=headers[0], anchor='center')
        if len(headers) == 2:
            self.result_tree.heading('Predicate', text=headers[1], anchor='center')
        elif len(headers) == 3:
            self.result_tree.heading('Predicate', text=headers[1], anchor='center')
            self.result_tree.heading('Object', text=headers[2], anchor='center')
        elif len(headers) > 3:
            return

        for obj in result:
            self.result_tree.insert('', 'end', values=obj)
