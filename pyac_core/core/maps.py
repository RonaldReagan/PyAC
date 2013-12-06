import os

OfficialMaps = []
ServerMaps = []
IncomingMaps = []

for i in os.listdir(os.path.join('.','packages','maps','official')):
    if i.endswith('.cgz'):
        OfficialMaps.append(i[:-4])

for i in os.listdir(os.path.join('.','packages','maps','servermaps')):
    if i.endswith('.cgz'):
        ServerMaps.append(i[:-4])

for i in os.listdir(os.path.join('.','packages','maps','servermaps','incoming')):
    if i.endswith('.cgz'):
        IncomingMaps.append(i[:-4])