from flask import render_template
from app import app,celery,db
from app.models import Task,Team
from flask import request,jsonify
import uuid, time
import csv

db.create_all()

def process(row):
    if(Team.query.filter_by(team_id=str(row[0])).first() != None):
        return
    print(row)
    tm = Team(team_id = str(row[0]), team_name = str(row[1]), team_count = int(row[2]))
    time.sleep(10)
    db.session.add(tm)
    db.session.commit()
    return

@celery.task(bind = True)
def create_team(self, row_no, cel_id):

    # Task started  
    self.update_state(state='STARTED',meta={'status':'started', 'row': row_no})

    # Reading the csv file containing teams   
    with open('data/' + cel_id.__str__() + '.csv') as fullCSV:
        teamReader = csv.reader(fullCSV)
        for (i,row) in enumerate(teamReader):
            if(i <= row_no and row_no != 0):
                continue
            process(row)
            self.update_state(state='RUNNING',meta={'status':'running', 'row': i})      

    # Task completed         
    self.update_state(state='COMPLETED',meta={'status':'finished'})
    return "Task Completed"

@app.route('/create_team', methods=['GET','POST'])
def createTeam():
    try:
        # Assigning ID to the uploaded CSV file
        uId = uuid.uuid4()

        # Saving the CSV file
        request.files['Teams'].save('data/'+ str(uId) + '.csv')

        # Creation of the task
        task = create_team.apply_async(args=[0,uId])

        # Updating DB for the new entry in table Task
        t = Task(task_id=str(uId), task_status="STARTED", row_no=0, cel_id=str(task))
        db.session.add(t)
        db.session.commit()
    except:
        return jsonify({'status':'failed','message':'file not found'})

    return jsonify({'status':'success','message':'Task successfully created with id:' + str(uId)})

@app.route('/pause/<id>',methods=['GET'])
def pause_task(id):

    # Getting Celery ID from DB for the given ID
    t = Task.query.filter_by(task_id=str(id)).first()
    if(t == None):
        return jsonify({'status':'failed','message': 'Task does not exist'})
    if(t.task_status == "PAUSED"):
        return jsonify({'status':'failed','message': 'Task already paused'})    
    if(t.task_status == "TERMINATED"):
        return jsonify({'status':'failed','message': 'Task terminated'})        
    cel_task = create_team.AsyncResult(t.cel_id)
    row = cel_task.info.get('row')
    t.task_status = "PAUSED"
    t.row_no = row 
    db.session.commit()

    # Revoking the current Celery Task of the given ID  
    cel_task.revoke(terminate=True,signal='SIGKILL')
    return jsonify({'status':'success','message':str(t.task_id) + ' paused at row_index: ' + str(row)})

@app.route('/resume/<id>',methods=['GET'])
def resume_task(id):

    # Getting the info of the task to be resumed
    t = Task.query.filter_by(task_id=str(id)).first()
    if(t == None):
        return jsonify({'status':'failed','message': 'Task does not exist'})
    if(t.task_status == "STARTED"):
        return jsonify({'status':'failed','message': 'Task already running'})    
    if(t.task_status == "TERMINATED"):
        return jsonify({'status':'failed','message': 'Task terminated'})
    prev_row = t.row_no
    t.task_status = "STARTED"

    # Creating a new celery task to continue team creation from the prev row  
    task = create_team.apply_async(args=[prev_row,id])
    t.cel_id = str(task)
    db.session.commit()
    return jsonify({'status':'success','message':str(t.task_id)+ ' resumed from row_index: ' + str(prev_row)})

@app.route('/terminate/<id>',methods=['GET'])
def terminate(id):

    t = Task.query.filter_by(task_id=str(id)).first()
    if(t == None):
        return jsonify({'status':'failed','message': 'Task does not exist'})
    if(t.task_status == "TERMINATED"):
        return jsonify({'status':'failed','message': 'Task already terminated'})

    # Revoke task if not in a paused state 
    if t.task_status != "PAUSED":
        cel_task = create_team.AsyncResult(t.cel_id)
        cel_task.revoke(terminate=True,signal='SIGKILL')
        t.task_status = "PAUSED"
        t.row = cel_task.info.get('row')
        db.session.commit()

    # Reverting changes
    with open('data/' + str(t.task_id) + '.csv') as fullCSV:
        teamReader = csv.reader(fullCSV)
        for (i,row) in enumerate(teamReader):
            if(i <= t.row_no):
                del_task = Team.query.filter_by(team_id=row[0]).first()
                if(del_task is not None):
                    db.session.delete(del_task)
            else:
                break
    t.task_status = "TERMINATED"            
    db.session.commit()                
    return jsonify({'status':'success','message':str(t.task_id)+ 'successfully terminated and changes were reverted'})

@app.route('/taskdb',methods=['GET','POST'])
def show_taskdb():

    # Display all the entries in table Task
    tasks = Task.query.all()
    lis = []
    for task in tasks:
        lis.append(task.__repr__())
    return jsonify({'status':lis})

@app.route('/teamdb',methods=['GET','POST'])
def show_teamdb():

    # Display all the entries in table Team
    teams = Team.query.all()
    lis = []
    for team in teams:
        lis.append(team.__repr__())
        print(team.__repr__())
    return jsonify({'status':lis})

# Clear databases
@app.route('/cleardb',methods=['GET'])
def clear_db():
    db.session.query(Task).delete()
    db.session.query(Team).delete()
    db.session.commit()
    return jsonify({'status':'success'})

@app.route('/status/<id>',methods=['GET'])
def status(id):
    
    # Get the status of the given taskID 
    t = Task.query.filter_by(task_id=str(id)).first()
    cel_task = create_team.AsyncResult(t.cel_id)
    try:
        return jsonify({'status':str(t.task_status),'task_id':id,'cel_id':str(t.cel_id),'row':str(cel_task.info.get('row'))})
    except:
        return jsonify({'status':str(t.task_status),'task_id':id,'row':str(t.row_no)})    




        
