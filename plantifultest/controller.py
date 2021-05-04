#all data fetching logic goes here
from .models import users,user_token,user_access,notification,sensor_block,sensor_block_reading,grp,project,health,growth,settings
from django.forms.models import model_to_dict
from pprint import pprint
from plotly.offline import plot
import plotly.graph_objs as go
from plotly.graph_objs import Scatter
import statistics


#sensorblk is a queryset of records with the specified group_id
def getSensorBlockIDSForGroup(group_id):
    sensorblk = sensor_block.objects.filter(group_id=group_id)
    sensor_block_ids=set()
    for i in range(len(sensorblk)):
        sensor_block_ids.add(sensorblk[i].id)
    return sensor_block_ids

def getSensorBlockReadings(sensor_block_id):
    readings = sensor_block_reading.objects.filter(sensor_block_id=sensor_block_id)
    
    readings=readings.order_by('-created_at')
    sensor_data = {new_list: [] for new_list in range(5)}

    # 0 -> SOIL MOISTURE
    # 1 -> PH
    # 2 -> TEMPERATURE
    # 3 -> HUMIDITY
    # 4 -> DATE
    for index in range(len(readings)):
        sensor_data[0].append(readings[index].moisture)
        sensor_data[1].append(readings[index].ph)
        sensor_data[2].append(readings[index].temperature)
        sensor_data[3].append(readings[index].humidity)
        sensor_data[4].append(readings[index].created_at)
    return sensor_data

def getAvgChartData(group_id):
    sensor_block_ids=list(getSensorBlockIDSForGroup(group_id))
    sensor_data_perblock = {}
    ii=0
    for i in range(len(sensor_block_ids)):
        sensor_data_perblock[ii] = getSensorBlockReadings(sensor_block_ids[i])
        ii=ii+1
    sensor_data = {new_list: [] for new_list in range(5)}
    for i in range(4): #number of readings per block
        data=[]
        for j in range(len(sensor_data_perblock)): #number of sensor blocks
            data.append(sensor_data_perblock[j][i])

        sensor_data[i]=[statistics.mean(k) for k in zip(*data)]
    sensor_data[4]=sensor_data_perblock[0][4]
    for i in range(len(sensor_data)):
        sensor_data[i].reverse()

    return sensor_data


def getChartData(group_id,sensor_block_name):
    #get 30 most recent readings
    sensorblk = sensor_block.objects.filter(group_id=group_id)

    sensorblk=sensorblk.filter(sensor_block_name=sensor_block_name)
    
    sensor_block_id=getattr(sensorblk[0],'id')

    sensor_data = getSensorBlockReadings(sensor_block_id)

    for i in range(len(sensor_data)):
        sensor_data[i].reverse()
    
    return sensor_data

#get most recent reading (avg or for one block)
def getSensorReadings(group_id,sensor_block_name):
    sensor_data = {new_list: [] for new_list in range(5)}
    
    if(sensor_block_name!='Average'):
        sensor_data=getChartData(group_id, sensor_block_name)
    else:
        sensor_data=getAvgChartData(group_id)
    
    sensor_data2 = {'sm':0,'ph':0,'temp':0,'hum':0}

    sensor_data2['sm']=(sensor_data[0][-1])
    sensor_data2['ph']=(sensor_data[1][-1])
    sensor_data2['temp']=(sensor_data[2][-1])
    sensor_data2['hum']=(sensor_data[3][-1])

    pprint(sensor_data2)

    return sensor_data2
    

def generateReport(type,start_date,end_date,project_id,group_id):
    return


def getDisplayedProjects(user_id):
    project_ids = user_access.objects.filter(usr_id=user_id)
    #get project names
    p_ids=[]
    for p in project_ids:
        p_ids.append(p.project_id)
    projects=project.objects.filter(id__in=p_ids).order_by('project_name')
    return projects

def getDisplayedGroups(project_id):
    groups = grp.objects.filter(project_id=project_id).order_by('id')
    return groups

def getDisplayedSensorBlocks(group_id):
    sb_names = sensor_block.objects.filter(group_id=group_id).order_by('sensor_block_name')
    return sb_names

#this should return: 
    #selected_project (id)
    #selected_group (id)
    #selected_sensor_block (name)
def getSelectedData(request, user_id):
    if (request.method == "POST"):
        selected_sb_name = request.POST.get('select_blocks',False)
        selected_project_id = request.POST.get('select_project',False)
        selected_group_id = request.POST.get('select_group',False)

    return selected_sb_name,selected_project_id,selected_group_id

def getPlots(chart_sensor_data,n):

    SMplot =  plot([Scatter(x=chart_sensor_data[4], y=chart_sensor_data[0][:144:n],mode='lines+markers', name='test',marker_color='red')],
            output_type='div', include_plotlyjs=False)
    phPlot =  plot([Scatter(x=chart_sensor_data[4], y=chart_sensor_data[1][:144:n],mode='lines+markers', name='test',marker_color='blue')],
            output_type='div', include_plotlyjs=False)
    Tplot =  plot([Scatter(x=chart_sensor_data[4], y=chart_sensor_data[2][:144:n],mode='lines+markers', name='test',marker_color='green')],
            output_type='div', include_plotlyjs=False)
    Hplot =  plot([Scatter(x=chart_sensor_data[4], y=chart_sensor_data[3][:144:n],mode='lines+markers', name='test',marker_color='yellow')],
            output_type='div', include_plotlyjs=False)
    return Tplot,SMplot,Hplot,phPlot


