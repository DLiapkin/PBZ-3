from rdflib import Graph
import io

from tkinter import *
from tkinter import messagebox as mb, scrolledtext
from tkinter import Tk, Label, Button, Entry, END, Frame, NO, W, WORD, Text
import tkinter.ttk as ttk
from tkinter.filedialog import askopenfilename, asksaveasfile


class OClass:
    name = ''
    subClasses = []
    individuals = []

    def __init__(self):
        self.name = ''
        self.subClasses = []
        self.individuals = []


dictionary = []


def find_root_class():
    root_classes = dictionary.copy()
    for c in dictionary:
        for cl in dictionary:
            if cl.subClasses.__contains__(c.name):
                root_classes.remove(c)
    return root_classes


def update_table():
    temp: list = []
    rt_classes = find_root_class()
    for oc in rt_classes:
        if not temp.__contains__(oc.name):
            create_node(temp, oc.name, '')


def create_node(temp: list, current_class: str, old_id: str):
    for cl in dictionary:
        if not temp.__contains__(cl.name) and cl.name == current_class:
            ID = vocabularyTree.insert(old_id, index="end", text=cl.name, values=[cl.name, cl.individuals])
            temp.append(cl.name)
            if len(cl.subClasses) != 0:
                for sub_cl in cl.subClasses:
                    for c in dictionary:
                        if c.name == sub_cl and not temp.__contains__(c.name):
                            # vocabularyTree.insert(ID, index='end', text=c.name, values=[c.name, c.individuals])
                            create_node(temp, sub_cl, ID)


def clear_table():
    vocabularyTree.delete(*vocabularyTree.get_children())
    dictionary.clear()


def load_ontology():
    filename = askopenfilename(filetypes=(("owl file", "*.owl"),), defaultextension=("owl file", "*.owl"))
    if filename is None:
        return
    g = Graph()
    # g.parse("C:/Users/D_Lia/Desktop/PBZ_2.owl")
    g.parse(filename)

    for s, p, o in g:
        s_str = s.__repr__()
        if o.__repr__() == 'rdflib.term.URIRef(\'http://www.w3.org/2002/07/owl#Class\')' and \
                p.__repr__() == 'rdflib.term.URIRef(\'http://www.w3.org/1999/02/22-rdf-syntax-ns#type\')':
            oc = OClass()
            oc.name = s_str.replace('rdflib.term.URIRef(\'http://www.semanticweb.org/d_lia/ontologies/2022/1/pbz_2#',
                                    '')[:-2]
            for sub, pre, obj in g:
                if pre.__repr__() == 'rdflib.term.URIRef(\'http://www.w3.org/2000/01/rdf-schema#subClassOf\')' and \
                        obj.__repr__() == s_str:
                    oc.subClasses.append(
                        sub.__repr__().replace(
                            'rdflib.term.URIRef(\'http://www.semanticweb.org/d_lia/ontologies/2022/1/pbz_2#', '')[:-2])
                if pre.__repr__() == 'rdflib.term.URIRef(\'http://www.w3.org/1999/02/22-rdf-syntax-ns#type\')' and \
                        obj.__repr__() == s_str:
                    oc.individuals.append(
                        sub.__repr__().replace(
                            'rdflib.term.URIRef(\'http://www.semanticweb.org/d_lia/ontologies/2022/1/pbz_2#', '')[:-2])

            dictionary.append(oc)
    update_table()


if __name__ == '__main__':
    gr = Graph()
    gr.parse("C:/Users/D_Lia/Desktop/PBZ_2.owl")
    for s, p, o in gr:
        s_str = s.__repr__()
        s_str = s_str.replace(
            'rdflib.term.URIRef(\'', '')[:-2]
        p_str = p.__repr__()
        p_str = p_str.replace(
            'rdflib.term.URIRef(\'', '')[:-2]
        o_str = o.__repr__()
        o_str = o_str.replace(
            'rdflib.term.URIRef(\'http://www.semanticweb.org/d_lia/ontologies/2022/1/pbz_2#', '')[:-2]
        print((s_str, p_str, o_str))

    # q = """
    #     PREFIX inv: <http://www.semanticweb.org/d_lia/ontologies/2022/1/pbz_2#>
    #
    #     SELECT ?class_name
    #     WHERE { ?class_name rdf:type owl:Class }
    # """
    #
    # name = []
    # # Apply the query to the graph and iterate through results
    # for r in g.query(q):
    #     ref = r.class_name
    #     temp = ref.__repr__()
    #     name.append(
    #         temp.replace('rdflib.term.URIRef(\'http://www.semanticweb.org/d_lia/ontologies/2022/1/pbz_2#', '')[:-2]
    #     )
    #
    # print(name)

root = Tk()

space0 = Label(root)
buttonFrame = Frame(root, bd=2)
updateButton = Button(buttonFrame, text="Update")
updateButton.config(command=update_table)
createButton = Button(buttonFrame, text="Load")
createButton.config(command=load_ontology)

space1 = Label(root)
vocabularyFrame = Frame(root, bd=2)
# vocabularyTree = ttk.Treeview(vocabularyFrame, show='tree',
#                               columns=("Класс", "Экземпляр"), height=11)
# vocabularyTree.heading('Класс', text="Класс", anchor='center')
# vocabularyTree.heading('Экземпляр', text="Экземпляр", anchor='center')
# vocabularyTree.column('#0', stretch=NO, minwidth=0, width=20)
# vocabularyTree.column('#1', stretch=NO, minwidth=347, width=400)
# vocabularyTree.column('#2', stretch=NO, minwidth=347, width=400)
vocabularyTree = ttk.Treeview(vocabularyFrame, show='tree', height=25)
vocabularyTree.column('#0', stretch=YES, minwidth=0, width=600)
vocabularyTree.grid_rowconfigure(0, weight=1)
vocabularyTree.grid_columnconfigure(0, weight=1)
vocabularyTree.grid(row=0, column=0, sticky='nsew')

space0.pack()
buttonFrame.pack()
updateButton.pack(side="left")
createButton.pack(side="left")

space1.pack()
vocabularyFrame.pack()
vocabularyTree.pack()

root.mainloop()
