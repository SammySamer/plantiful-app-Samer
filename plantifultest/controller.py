#all data fetching logic goes here
from .models import *
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

    fig=go.Figure(data=go.Scatter(x=chart_sensor_data[4], y=chart_sensor_data[0][:144:n],mode='lines+markers',marker_color='mediumspringgreen'))
    fig.update_layout(title='Soil Moisture over the Last Week',
                   xaxis_title='DateTime',
                   yaxis_title='Soil Moisture %')
    SMplot=plot(fig,output_type='div',include_plotlyjs=False)

    fig=go.Figure(data=go.Scatter(x=chart_sensor_data[4], y=chart_sensor_data[1][:144:n],mode='lines+markers',marker_color='gold'))
    fig.update_layout(title='pH over the Last Week',
                   xaxis_title='DateTime',
                   yaxis_title='pH')
    phPlot=plot(fig,output_type='div',include_plotlyjs=False)


    fig=go.Figure(data=go.Scatter(x=chart_sensor_data[4], y=chart_sensor_data[2][:144:n],mode='lines+markers',marker_color='royalblue'))
    fig.update_layout(title='Temperature over the Last Week',
                   xaxis_title='DateTime',
                   yaxis_title='Temperature °C')
   
    Tplot=plot(fig,output_type='div',include_plotlyjs=False)

    fig=go.Figure(data=go.Scatter(x=chart_sensor_data[4], y=chart_sensor_data[3][:144:n],mode='lines+markers',marker_color='darkturquoise'))
    fig.update_layout(title='Humidity over the Last Week',
                   xaxis_title='DateTime',
                   yaxis_title='Humidity %')
    Hplot=plot(fig,output_type='div',include_plotlyjs=False)

  
    return Tplot,SMplot,Hplot,phPlot


def getPrediction(selected_group_id):
    growth=""
    health=""
    img_path=""
    print("in prediction controller")
    if(selected_group_id!=False):
        growth="No images were taken yet."
        health="No"
        img_path=False
        print("group")
        print(selected_group_id)
        predict = prediction.objects.filter(group_id=selected_group_id).order_by('-created_at')
        if(len(predict)>0):
            growth=getattr(predict[0],'growth_stage')
            health=getattr(predict[0],'health')
            img_path="https://cloud-cube-us2.s3.amazonaws.com/"+getattr(predict[0],'image_path')
    return growth,health,img_path



