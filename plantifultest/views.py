from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.core import serializers
from django.forms.models import formset_factory, model_to_dict, modelformset_factory
from django.db import models
from .models import *
from django.contrib import messages
from django.urls import reverse_lazy
from django.urls import reverse
from passlib.hash import pbkdf2_sha256
from plotly.offline import plot
import plotly.graph_objs as go
from plotly.graph_objs import Scatter
import datetime
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string

def register(request):
    # return HttpResponse('register')
    if (request.method == "POST"):
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        pwd = request.POST["pwd"]
        rpwd = request.POST["rpwd"]
        security_token = request.POST["security_token"]

        try:
            obj = users.objects.get(email=email)
        except users.DoesNotExist:
            print(email)
            try:
                usr_token = user_token.objects.get(invited_email=email)
                token = getattr(usr_token, 'token')
                if(security_token != token):
                    messages.error(request, 'Invalid Token.')
                    return HttpResponseRedirect(reverse_lazy('register'))
                dt = getattr(usr_token, 'created_at').date()
                dt_now = datetime.date.today()
                diff = abs((dt_now - dt).days)
                if(diff > 7):
                    messages.error(request, 'Token has expired.')
                    return HttpResponseRedirect(reverse_lazy('register'))

                if(pwd == rpwd):
                    enc_pwd = pbkdf2_sha256.encrypt(
                        pwd, rounds=12000, salt_size=32)
                    create_usr = users(first_name=first_name,
                                       last_name=last_name, email=email, pwd=enc_pwd)
                    create_usr.save()
                    return redirect('login')
                else:
                    # enter error message here
                    messages.error(request, 'Passwords do not match.')
                    return HttpResponseRedirect(reverse_lazy('register'))
            except user_token.DoesNotExist:
                messages.error(request, 'No token exists for this user.')
                return HttpResponseRedirect(reverse_lazy('register'))
    else:
        return render(request, 'register.html')


def login(request):
    if (request.method == "POST"):
        email = request.POST["email"]
        pwd = request.POST["pwd"]

        try:
            obj = users.objects.get(email=email)

            if(pbkdf2_sha256.verify(pwd, obj.pwd)):
                # user_data = serializers.serialize('json', obj)
                user_data = model_to_dict(obj)
                request.session['user'] = user_data
                return redirect('dashboard')
            else:
                messages.error(request, 'Password/email is incorrect.')
                return HttpResponseRedirect(reverse_lazy('login'))
        except users.DoesNotExist:
            messages.error(request, 'This email does not have an account.')
            return HttpResponseRedirect(reverse_lazy('login'))
    else:
        return render(request, 'login.html')


def share(request):
    notifications_not_read = notification.objects.filter(if_read=False)
    notifications_all = notification.objects.all().order_by('-created_at')

    if(request.method == "POST"):
        email = request.POST["email"]
        access_type_string = request.POST["access_type"]
        access_type = -1

        if(access_type_string == "editor"):
            access_type = 1
        elif(access_type_string == "viewer"):
            access_type = 2

        try:
            obj = users.objects.get(email=email)
            usr_id = obj.id

            share_project = user_access(
                usr_id=usr_id, project_id=1, access_type=usr_id)
            share_project.save()

            # send email to that user that the project is added to their account
        except users.DoesNotExist:
            messages.error(request, 'This email does not have an account.')
            return HttpResponseRedirect(reverse_lazy('share'))

    else:
        return render(request, 'share-project.html', {'notifications_not_read': notifications_not_read, 'notifications_all': notifications_all})


def dashboard(request):
    user_data = request.session.get('user')
    sensor_data = {
        'temp': 20,
        'sm': 70,
        'hum': 30,
        'ph': 5.6
    }

    x_data = [0, 1, 2, 3]
    y_data = [x**2 for x in x_data]
    Tplot = plot([Scatter(x=x_data, y=y_data,
                          mode='lines+markers', name='test',
                          marker_color='green')],
                 output_type='div', include_plotlyjs=False)

    # selected_project = request.POST.get('select_project', None)  
    # print(selected_project)
    return render(request, 'home.html', {'user': user_data, 'sensor_data': sensor_data, 'temp_plot': Tplot})


def newproject(request):
    currUser = request.session.get('user')
    userID = currUser['id']
    request.session['group_index'] = 0
    request.session['extra_index'] = 0
    request.session['createdGroups'] = []

    if(request.method == "POST"):
        project_name = request.POST["project_name"]
        start_date = request.POST["start_date"]
        end_date = request.POST["end_date"]
        groups_num = request.POST["groups_num"]

        if(end_date < start_date):
            messages.error(request, 'Cannot enter end date before start date')
            return HttpResponseRedirect(reverse_lazy('newproject'))

        else:
            create_project = project(
                project_name=project_name, start_date=start_date, end_date=end_date)
            create_project.save()
            project_id = create_project.id

            create_usr_access = user_access(usr_id=userID, project_id=project_id, access_type=0)
            create_usr_access.save()

        return redirect(reverse("newgroup", kwargs={'project_id': str(project_id), 'groups_num': str(groups_num)}))

    else:
        return render(request, 'newproject.html')


def newgroup(request, project_id, groups_num):
    
    # --- Start of Project Selection Options --- #

    currUser = request.session.get('user')
    userID = currUser['id']
    
    userSettings = []
    settingsNames = []
    settingsIDs = []

    userProjects = user_access.objects.filter(usr_id = userID).only('project_id')
 
    try:
        settingsCounter = 0
        for proj in userProjects:
            projID = proj.project_id
            query = grp.objects.filter(project_id = projID)
            for i in range (len(query)):
                currQuery = query[i].settings_id

                noAdd = True
                for checkDups in userSettings:
                    if checkDups == currQuery:
                        noAdd = False

                if noAdd:
                    userSettings.append(currQuery)
 
        namesCounter = 0    
        for setts in userSettings:
            query = settings.objects.filter(id = setts)
 
            for i in range (len(query)):
                currQueryName = query[i].name
                settingsNames.append(currQueryName)
                currQueryID = query[i].id
                settingsIDs.append(currQueryID)
                namesCounter = namesCounter + 1      
 
 
    except grp.DoesNotExist: 
        userSettings = None
        settingsNames = None  
        settingsIDs = None  
        settingsInfo = None
 
    settingsInfo = list(zip(settingsNames, settingsIDs))

    # --- End of Project Selection Options --- #
    group_ids = []
    num_sensors = []

    project_obj = project.objects.get(id=project_id)
    project_name = project_obj.project_name

    SettingsFormSet = modelformset_factory(settings, exclude=(), extra = int(groups_num))
    form_set = SettingsFormSet(queryset=settings.objects.none())

    if request.method == "POST" and 'group_btn' in request.POST:
        form_set = SettingsFormSet(request.POST or None, request.FILES or None)
        camera_ids = request.POST.getlist('camera_id')
        x = 0
        for form in form_set:
            if form_set.is_valid:
                val = form.save(commit=False)
                val.save()
                sId = int(val.id)
                camera_id = camera_ids[x]
                create_grp = grp(project_id = int(project_id), settings_id = sId, camera_id = camera_id)
                x = x + 1
                create_grp.save()
                number_of_sensor_blocks = form.cleaned_data['number_of_sensor_blocks']
                group_ids.append(int(create_grp.id))
                num_sensors.append(int(number_of_sensor_blocks))

        request.session['group_ids'] = group_ids
        request.session['num_sensors'] = num_sensors

        # First sensor form
        SensorFormSet = modelformset_factory(sensor_block, exclude=('group_id','sensor_block_name'), extra = num_sensors[0])
        sensor_set = SensorFormSet(queryset = sensor_block.objects.none())
        return render(request, 'sensors.html',{'sensor_set':sensor_set})
    
    if request.method != "POST":
        return render(request, 'newgroup.html',{'project_name':project_name, 'form_set':form_set, 
        'namesCounter':range(namesCounter), 'settingsInfo':settingsInfo})

    # Rest of sensor forms
    num_sensors = request.session.get('num_sensors')
    group_ids = request.session.get('group_ids')
    SensorFormSet = modelformset_factory(sensor_block, exclude=('group_id','sensor_block_name'), extra = num_sensors[0])
    sensor_set = SensorFormSet(queryset = sensor_block.objects.none())

    if request.method == "POST" and 'sensor_btn' in request.POST:
        sensor_set = SensorFormSet(request.POST or None, request.FILES or None)
        page_num = request.session.get('page_num')
        sensor_names = request.POST.getlist('sensor_block_name')
        group_index = request.session.get('group_index')
        sensor_index = 0

        for sensor in sensor_set:
            create_sensor = sensor_block(group_id = group_ids[group_index], sensor_block_name = sensor_names[sensor_index]).save()
            sensor_index = sensor_index + 1
        request.session['group_index'] = request.session.get('group_index') + 1

    request.session['extra_index'] = request.session.get('extra_index') + 1
    extra_index = request.session.get('extra_index')
    length = len(num_sensors)
    if extra_index == len(num_sensors):
        return redirect('/app/')
    else:
        SensorFormSet = modelformset_factory(sensor_block, exclude=('group_id','sensor_block_name',), extra = num_sensors[extra_index])
        sensor_set = SensorFormSet(queryset = sensor_block.objects.none())
        return render(request, 'sensors.html',{'sensor_set':sensor_set})
    

def update_settings_dropdown(request, project_id, groups_num):
    dropdownValue = request.GET.get('dropdownValue')

    if dropdownValue != 0: 
        create_grp = grp(project_id = project_id, settings_id = dropdownValue)
        create_grp.save()
        grpBool = True
        print("YES")

    return render(request, 'update_settings_drop.html', {'grpBool':grpBool})

def project_settings(request, project_id):

    project_obj = project.objects.get(id = project_id)
    project_name = project_obj.project_name

    ProjectSettings = modelformset_factory(model=project,form = projectForm, exclude = (), extra = 0)
    form_set = ProjectSettings(queryset=project.objects.filter(id=project_id))
    
    if request.method == "POST":
        form_set = ProjectSettings(request.POST or None, request.FILES or None)
        if form_set.is_valid:
            form_set.save()
            return redirect('/app/')

    return render(request, 'project_settings.html',{'project_name':project_name, 'form_set':form_set})

def group_settings(request, project_id, group_id):
    
    grp_obj = grp.objects.get(id = group_id)
    project_name = project.objects.get(id = project_id).project_name
    settings_id = grp_obj.settings_id
    grp_name = settings.objects.get(id = group_id).name

    GroupSettings = modelformset_factory(settings, exclude = (), extra = 0)
    form_set = GroupSettings(queryset=settings.objects.filter(id=settings_id))
    
    if request.method == "POST":
        form_set = GroupSettings(request.POST or None, request.FILES or None)
        if form_set.is_valid:
            form_set.save()
            return redirect('/app/')

    return render(request, 'group_settings.html',{'project_name':project_name, 'group_name':grp_name, 'form_set':form_set})

def change_password(request):
    currUser = request.session.get('user')
    user_id = currUser['id']

    user_password = users.objects.get(id = user_id).pwd
    user_email = users.objects.get(id = user_id).email
    print(user_email)

    if (request.method == "POST"):
        old_password = request.POST["old_password"]
        new_password = request.POST["new_password"]
        repeat_password = request.POST["repeat_password"]

        if(pbkdf2_sha256.verify(old_password, user_password)):
            if(new_password == repeat_password):
                enc_pwd = pbkdf2_sha256.encrypt(new_password, rounds=12000, salt_size=32)
                users.objects.filter(id = user_id).update(pwd = enc_pwd)
                return redirect('/app/')
            else:
                messages.error(request, 'Password and repeat password are different')
        else:
            messages.error(request, 'Old password is incorrect')
        
    return render(request, 'change_password.html')