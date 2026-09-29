import benedict

data=benedict.benedict()

data["se1.2021.water_sensor.t1.spectrum"]=[1,2,3,4,5,6]
data["se1.2021.water_sensor.t2.spectrum"]=[6,7,8,9,10,11]
data["se1.2021.water_sensor.t3.spectrum"]=[11,12,13,14,15,16]
for key,val in data.items():
    print(key)

print(data)