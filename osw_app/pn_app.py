import os
import re
import panel as pn
import pandas as pd
import datetime as dt

from bokeh.models.widgets.tables import NumberFormatter, BooleanFormatter, HTMLTemplateFormatter

from osw.core import OSW
import osw.wiki_tools as wt
import osw.model.entity as model

#from .page_list import SineWave

def createApp():

    osw: OSW = pn.state.cache['osw']
    user = pn.state.cache['osw_user']
    print(user)
    titles = wt.semantic_search(osw.site._site, wt.SearchParam(
        query="[[HasType::Category:OSW92cc6b1a2e6b4bb7bad470dfdcfdaf26]]",
        limit=3,
    ))
    print(titles)

    if hasattr(model, 'Item'):
        print("Item exists")
    if hasattr(model, 'Article'):
        print("Article exists")
    else: osw.fetch_schema(OSW.FetchSchemaParam(schema_title="Category:OSW92cc6b1a2e6b4bb7bad470dfdcfdaf26", mode="replace"))
    if hasattr(model, 'Tutorial'):
        print("Tutorial exists")
    

    results = []
    result_dict = {
        #"index": [],
        "id": [],
        "name": [],
        "link": [],
        "include": [],
    }
    index = 0
    for title in titles:
        article : model.Article = osw.load_entity(title)
        #result_dict["index"].append(index)
        index += 1
        result_dict["id"].append(str(article.uuid))
        result_dict["name"].append(article.label[0].text)
        #result_dict["link"].append({
        #    "url": os.getenv("OSW_SERVER") + "/wiki/",
        #    "value": article.label[0].text
        #})
        result_dict["link"].append(os.getenv("OSW_SERVER") + "/wiki/" + title)
        result_dict["include"].append(True)
        
        #results.append(article.json())
        results.append(result_dict)

    df = pd.DataFrame({
        'int': [1, 2, 3],
        'float': [3.14, 6.28, 9.42],
        'str': ['A', 'B', 'C'],
        'bool': [True, False, True],
        'date': [dt.date(2019, 1, 1), dt.date(2020, 1, 1), dt.date(2020, 1, 10)],
        'datetime': [dt.datetime(2019, 1, 1, 10), dt.datetime(2020, 1, 1, 12), dt.datetime(2020, 1, 10, 13)]
    })#, index=[1, 2, 3])
    df = pd.DataFrame(result_dict)

    bokeh_formatters = {
        'float': NumberFormatter(format='0.00000'),
        'include': BooleanFormatter(),
        'link': HTMLTemplateFormatter(template='<a href="<%= value %>" target="_blank">link</a>')
    }
    """ {
            "_data": results,
            "_columns": [
                {"title":"ID", "field":"id"},
                {"title":"name", "field":"name"},
                {"title":"link", "field":"link"},
                {"title":"include", "field":"include"}
                ]
            } """
    return pn.widgets.Tabulator(df, formatters=bokeh_formatters, buttons={'Print': "<i class='fa fa-print'></i>"})