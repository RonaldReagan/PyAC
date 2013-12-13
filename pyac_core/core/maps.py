import os

OfficalMapPath = os.path.join('.','packages','maps','official')
ServerMapPath = os.path.join('.','packages','maps','servermaps')
IncomingMapPath = os.path.join('.','packages','maps','servermaps','incoming')

OfficialMaps = []
ServerMaps = []
IncomingMaps = []

for i in os.listdir(OfficalMapPath):
    if i.endswith('.cgz'):
        OfficialMaps.append(i[:-4])

for i in os.listdir(ServerMapPath):
    if i.endswith('.cgz'):
        ServerMaps.append(i[:-4])

for i in os.listdir(IncomingMapPath):
    if i.endswith('.cgz'):
        IncomingMaps.append(i[:-4])