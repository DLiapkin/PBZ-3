from rdflib import Graph

import tkinter
from tkinter import *
from tkinter import Tk, Label, Button, Entry, END, Frame, NO, W, WORD, Text
import tkinter.ttk as ttk
from tkinter.filedialog import askopenfilename, asksaveasfile

from View import query_view as que, creation_view as crv
from Models import ontoClass as ocl, ontoObjProperty as obp


# class OClass:
#     name = ''
#     subClasses = []
#     individuals = []
#
#     def __init__(self):
#         self.name = ''
#         self.subClasses = []
#         self.individuals = []


# class ObjectProperty:
#     name = ''
#     subject = ''
#     object = ''
#
#     def __init__(self):
#         self.name = ''
#         self.subject = ''
#         self.object = ''


class_dictionary = []
obj_properties = []
individuals_dictionary = []

graph = Graph()


def find_root_class():
    root_classes = class_dictionary.copy()
    for c in class_dictionary:
        for cl in class_dictionary:
            if cl.subClasses.__contains__(c.name):
                root_classes.remove(c)
    return root_classes


def update_tables():
    vocabularyTree.delete(*vocabularyTree.get_children())
    temp: list = []
    rt_classes = find_root_class()
    for oc in rt_classes:
        if not temp.__contains__(oc.name):
            create_node(temp, oc.name, '')
    update_obj_property_table()
    update_individuals_table()


def update_obj_property_table():
    objPropTree.delete(*objPropTree.get_children())
    for ob in obj_properties:
        objPropTree.insert('', 'end', values=(ob.subject, ob.name, ob.object))


def update_individuals_table():
    individualsTree.delete(*individualsTree.get_children())
    for ind in individuals_dictionary:
        individualsTree.insert('', 'end', values=ind)


def create_node(temp: list, current_class: str, old_id: str):
    for cl in class_dictionary:
        if not temp.__contains__(cl.name) and cl.name == current_class:
            ID = vocabularyTree.insert(old_id, index="end", text=cl.name, values=[cl.individuals])
            temp.append(cl.name)
            if len(cl.subClasses) != 0:
                for sub_cl in cl.subClasses:
                    for c in class_dictionary:
                        if c.name == sub_cl and not temp.__contains__(c.name):
                            create_node(temp, sub_cl, ID)


# def clear_table():
#     vocabularyTree.delete(*vocabularyTree.get_children())
#     class_dictionary.clear()


def load_ontology():
    filename = askopenfilename(filetypes=(("owl file", "*.owl"),), defaultextension=("owl file", "*.owl"))
    if filename is None:
        return
    graph.parse(filename)

    ontology_iri = ""
    for s, p, o in graph:
        if p.__repr__() == 'rdflib.term.URIRef(\'http://www.w3.org/1999/02/22-rdf-syntax-ns#type\')' and \
                o.__repr__() == 'rdflib.term.URIRef(\'http://www.w3.org/2002/07/owl#Ontology\')':
            ontology_iri = s.__repr__().replace(
                'rdflib.term.URIRef(\'', '')[:-2] + '#'
    load_classes(ontology_iri, graph)
    load_properties(ontology_iri, graph)
    load_individuals(ontology_iri, graph)
    update_tables()


def load_classes(ontology_iri: str, g: Graph):
    for s, p, o in g:
        s_str = s.__repr__()
        if o.__repr__() == 'rdflib.term.URIRef(\'http://www.w3.org/2002/07/owl#Class\')' and \
                p.__repr__() == 'rdflib.term.URIRef(\'http://www.w3.org/1999/02/22-rdf-syntax-ns#type\')':
            oc = ocl.OClass()
            oc.name = s_str.replace(f'rdflib.term.URIRef(\'{ontology_iri}', '')[:-2]
            for sub, pre, obj in g:
                if pre.__repr__() == 'rdflib.term.URIRef(\'http://www.w3.org/2000/01/rdf-schema#subClassOf\')' and \
                        obj.__repr__() == s_str:
                    oc.subClasses.append(
                        sub.__repr__().replace(f'rdflib.term.URIRef(\'{ontology_iri}', '')[:-2])
                if pre.__repr__() == 'rdflib.term.URIRef(\'http://www.w3.org/1999/02/22-rdf-syntax-ns#type\')' and \
                        obj.__repr__() == s_str:
                    oc.individuals.append(
                        sub.__repr__().replace(f'rdflib.term.URIRef(\'{ontology_iri}', '')[:-2])
            class_dictionary.append(oc)


def load_properties(ontology_iri: str, g: Graph):
    repeats = []
    for s, p, o in g:
        s_str = s.__repr__()
        if o.__repr__() == 'rdflib.term.URIRef(\'http://www.w3.org/2002/07/owl#ObjectProperty\')' and \
                p.__repr__() == 'rdflib.term.URIRef(\'http://www.w3.org/1999/02/22-rdf-syntax-ns#type\')':
            for sub, pre, obj in g:
                if not repeats.__contains__(
                        sub.__repr__().replace(f'rdflib.term.URIRef(\'{ontology_iri}', '')[:-2]) and \
                        pre.__repr__() == s_str:
                    ob = obp.ObjectProperty()
                    ob.name = s_str.replace(f'rdflib.term.URIRef(\'{ontology_iri}', '')[:-2]
                    ob.subject = sub.__repr__().replace(f'rdflib.term.URIRef(\'{ontology_iri}', '')[:-2]
                    ob.object = obj.__repr__().replace(f'rdflib.term.URIRef(\'{ontology_iri}', '')[:-2]
                    repeats.append(sub.__repr__().replace(f'rdflib.term.URIRef(\'{ontology_iri}', '')[:-2])
                    obj_properties.append(ob)


def load_individuals(ontology_iri: str, g: Graph):
    repeats = []
    for s, p, o in g:
        s_str = s.__repr__()
        if o.__repr__() == 'rdflib.term.URIRef(\'http://www.w3.org/2002/07/owl#NamedIndividual\')' and \
                p.__repr__() == 'rdflib.term.URIRef(\'http://www.w3.org/1999/02/22-rdf-syntax-ns#type\')':
            ind = s_str.replace(f'rdflib.term.URIRef(\'{ontology_iri}', '')[:-2]
            repeats.append(ind)
            individuals_dictionary.append(ind)


def query_window():
    query_win = que.Query(root, graph)
    query_win.grab_set()
    # query_win = Toplevel(root)
    # input_frame = Frame(query_win, bd=2)
    # query_text = Text(input_frame, height=10, width=70, wrap=WORD)
    # query_button = Button(input_frame, text="Query", width=30, height=3)
    # result_tree = ttk.Treeview(input_frame, columns=("Subject", "Predicate", "Object"), selectmode='browse', height=5)
    # result_tree.heading('Subject', text="Subject", anchor='center')
    # result_tree.heading('Predicate', text="Predicate", anchor='center')
    # result_tree.heading('Object', text="Object", anchor='center')
    # result_tree.column('#0', stretch=NO, minwidth=0, width=0)
    # result_tree.column('#1', stretch=NO, minwidth=10, width=200)
    # result_tree.column('#2', stretch=NO, minwidth=10, width=200)
    # result_tree.column('#3', stretch=NO, minwidth=10, width=200)
    # input_frame.pack()
    # query_text.pack()
    # query_button.pack()
    # result_tree.pack()
    # query_win.grab_set()


def creation_window():
    creation_win = crv.Creation(root, graph, class_dictionary, obj_properties, individuals_dictionary)
    creation_win.grab_set()
    # creation_win = Toplevel(root)
    # creation_frame = Frame(creation_win, bd=2)
    # name_text = Entry(creation_frame, height=1, width=70, wrap=WORD)
    #
    # choosing_value = 0
    # create_class = Radiobutton(creation_frame, text="Class", variable=choosing_value, value=0)
    # create_obj_prop = Radiobutton(creation_frame, text="Object property", variable=choosing_value, value=1)
    # create_individual = Radiobutton(creation_frame, text="Individual", variable=choosing_value, value=2)
    # choose_button = Button(creation_frame, text="Choose", width=30)
    #
    # create_class_frame = Frame(creation_frame, bd=2)
    # is_subclass_of_entry = Entry(create_class_frame, width=70)
    # subclasses_entry = Entry(create_class_frame, width=70, wrap=WORD)
    # create_button = Button(creation_frame, text="Create", width=30, height=3)
    #
    # # добавление радиокнопок
    # create_class.pack(side="left")
    # create_obj_prop.pack(side="left")
    # create_individual.pack(side="left")
    # choose_button.pack(side="center")
    #
    # is_subclass_of_entry.pack()
    # subclasses_entry.pack()
    # create_class_frame.pack()
    #
    # creation_frame.pack()
    # name_text.pack()
    # create_button.pack()
    # creation_win.grab_set()

# сохраняет онтологию в файл
# да, вот так просто)
def save_ontology():
    file = asksaveasfile(filetypes=(("owl file", "*.owl"),), defaultextension=("owl file", "*.owl"))
    if file is None:
        return
    graph.serialize(destination=file.name, format="xml")


root = Tk()
main_menu = Menu(root)
main_menu.add_command(label='Загрузить', command=load_ontology)
main_menu.add_command(label='Сохранить', command=save_ontology)
main_menu.add_command(label='Обновить онтологию', command=update_tables)
main_menu.add_command(label="SPARQL query", command=query_window)
main_menu.add_command(label="Добавление сущностей", command=creation_window)
root.config(menu=main_menu)

space1 = Label(root)
notebook_lists = ["Classes", "Object properties", "Individuals"]
notebook = ttk.Notebook(root, width=600, height=500)
vocabularyFrame = Frame(notebook, bd=2)
objPropFrame = Frame(notebook, bd=2)
individualsTreeFrame = Frame(notebook, bd=2)
notebook.add(vocabularyFrame, text=notebook_lists[0], underline=0, sticky=tkinter.NE + tkinter.SW)
notebook.add(objPropFrame, text=notebook_lists[1], underline=0, sticky=tkinter.NE + tkinter.SW)
notebook.add(individualsTreeFrame, text=notebook_lists[2], underline=0, sticky=tkinter.NE + tkinter.SW)

vocabularyTree = ttk.Treeview(vocabularyFrame, show='tree', height=25)
vocabularyTree.column('#0', stretch=YES, minwidth=0, width=600)
vocabularyTree.grid_rowconfigure(0, weight=1)
vocabularyTree.grid_columnconfigure(0, weight=1)
vocabularyTree.grid(row=0, column=0, sticky='nsew')

objPropTree = ttk.Treeview(objPropFrame, columns=("Subject", "Predicate", "Object"), selectmode='browse', height=25)
objPropTree.heading('Subject', text="Subject", anchor='center')
objPropTree.heading('Predicate', text="Predicate", anchor='center')
objPropTree.heading('Object', text="Object", anchor='center')
objPropTree.column('#0', stretch=NO, minwidth=0, width=0)
objPropTree.column('#1', stretch=NO, minwidth=100, width=200)
objPropTree.column('#2', stretch=NO, minwidth=100, width=200)
objPropTree.column('#3', stretch=NO, minwidth=100, width=200)
objPropTree.grid(row=0, column=0, sticky='nsew')

individualsTree = ttk.Treeview(individualsTreeFrame, columns="Individuals", selectmode='browse', height=25)
individualsTree.heading('Individuals', text="Individuals", anchor='center')
individualsTree.column('#0', stretch=NO, minwidth=0, width=0)
individualsTree.column('#1', stretch=NO, minwidth=100, width=600)
individualsTree.grid(row=0, column=0, sticky='nsew')

# space1.pack()
notebook.pack()
# vocabularyFrame.pack()
# vocabularyTree.pack()

root.mainloop()
