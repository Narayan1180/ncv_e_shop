import pickle


from django.db import transaction

from .models import SensorNode, SpectrumData
from .helpers import create_benedict_from_excel,traverse_and_insert
from django.http import HttpResponse,JsonResponse
from .helpers2 import iter_blocks

def dump_excel(request):
    path="/Users/ncvhome/NodeApp/Ecommerce/core/data_inegstion/data_set1/product1_2026.xlsx"
    l=path.split("/")
    product_name_detail=l[-1].split(".")[0]

    product_info=product_name_detail.split("_")
    name=product_info[0]
    year=product_info[1]
    s1=SensorNode.objects.filter(name=name,year=year)
    s2=SpectrumData.objects.filter(name=name,year=year)
    s1.delete()
    s2.delete()
    print(product_name_detail,product_info,name,year,s1,s2)

    data=create_benedict_from_excel(path)
    #print(data)
    traverse_and_insert(data,name,year,sensor_name="",parent=None)

    return HttpResponse("data imported successfully")

def get_info(request):
    spectrum_data=SpectrumData.objects.all()[:10]
    data=[]
    for sensor in spectrum_data:
        unpack_data=pickle.loads(sensor.data)
        data.append({"sensor_id":sensor.id,"name":sensor.sensor_name,"data":unpack_data})



    return JsonResponse(data,safe=False)

