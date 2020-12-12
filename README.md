# Task
Long-running tasks require time and resources on the servers. Once a long-running task is triggered there is no way to pause/resume/terminate the process. The task was to design a system that can handle such operations on long-running jobs in order to utilize resources efficiently. For this, we have to make REST API endpoints that can manage pause/resume/terminate options.

## Tools Used
1. Flask  (Framework)
2. Redis  (Broker)
3. Celery (Asynchronous task queue)
4. Docker-Compose (Multi-Container Docker application)

## API Endpoints
1. /create_team:

    This endpoint expects a .csv file for team creation. The key of the file attribute should be ‘Teams’. On receiving the team file, an asynchronous task is created and the task id is returned.

    Sample .csv file is uploaded in the project with the name ‘sample_data.csv’. 

2. /pause/\<id>

    This endpoint is to pause the task with the given task ID.

3. /resume/\<id>

    This endpoint is to resume the task with the given task ID.

4. /terminate/\<id>

    This endpoint is to terminate the task with the given task ID.

5. /status/\<id>

    This endpoint shows the status of the task with the given task ID.

6. /taskdb

    This endpoint reveals all the tasks so far received. 

7. /taskdb

    This endpoint reveals all the teams so far created.

8. /cleardb

    This endpoint clears all the entries in Team and Task DB. 

## Deployment

To build docker images

```docker-compose build```

To run multiple docker images

```docker-compose up```

    Local host:
[http://localhost:5000/](http://localhost:5000/)

To stop running docker images

```docker-compose stop``` 
