from django.shortcuts import render

# Create your views here.
import pickle

import pandas as pd
from benedict import benedict

from django.db import transaction

from .models import SensorNode, SpectrumData

from django.http import HttpResponse,JsonResponse
import uuid

def create_benedict_from_excel(file_path):

    data = benedict()

    sheets = pd.read_excel(
        file_path,
        sheet_name=None
    )
    for sheet_name, df in sheets.items():
        for i, column in enumerate(df.columns):
            path = str(column).strip()
            
            if "Unnamed" in path:
                continue

            #print(path)

            path = ".".join(part for part in path.split("/") if part)

            data[path] = {
                        "f": df[column].tolist()[1:],
                        "v": df[df.columns[i + 1]].tolist()[1:]
                        }

            #print(data[path])
    return data

def traverse_and_insert(data, name, year, sensor_name=None,full_name=None, parent=None):
    
    #s_name=""
    spectrum_objects=[]
    for key, value in data.items():
       # s_name=s_name+"~"+key

        #print(sensor_name)

        

        # -----------------------------
        # SPECTRUM
        # -----------------------------
        if key == "spectrum":

            #print("inside spectrum",name,year,sensor_name,full_name,parent)

            if parent is not None:
                
                #SpectrumData.objects.create(name=name,sensor_name=sensor_name,year=year,node_id=parent,data=pickle.dumps(value))
                spectrum_objects.append(SpectrumData(name=name,sensor_name=sensor_name,year=year,node_id=parent,data=pickle.dumps(value)))

            continue

        # -----------------------------
        # NORMAL NODE
        # -----------------------------
        #print("outside spectrum",name,year,sensor_name,full_name,parent)
        
        node = SensorNode.objects.filter(name=name,node_name=key,parent=parent,year=year).first()
        #print(node)
        # -----------------------------
        # CREATE NODE
        # -----------------------------
        if node is None:
            node = SensorNode.objects.create(node=uuid.uuid4(),parent=parent,name=name,node_name=key,year=year)


        
        # -----------------------------
        # RECURSE
        # -----------------------------
        
        if isinstance(value, dict):
            traverse_and_insert(data=value,name=name,year=year,sensor_name=sensor_name+"~"+key if sensor_name else key,parent=node.node)

    if spectrum_objects:
        
        SpectrumData.objects.bulk_create(spectrum_objects,batch_size=500)
