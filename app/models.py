from app import db

class Task(db.Model):
    task_id = db.Column(db.String(56), index=True, primary_key=True)
    task_status = db.Column(db.String(10),index=True)
    row_no = db.Column(db.Integer)
    cel_id = db.Column(db.String(56),index=True)

    def __repr__(self):
        return '<taskId:{}, status:{}, row:{}, cel_id:{}>'.format(self.task_id,self.task_status,self.row_no,self.cel_id)

class Team(db.Model):
    team_id = db.Column(db.String(56), index=True, primary_key=True)
    team_name = db.Column(db.String(50),index=True)
    team_count = db.Column(db.Integer)

    def __repr__(self):
        return '<teamId:{}, teamName:{}, teamCount:{}>'.format(self.team_id,self.team_name,self.team_count)