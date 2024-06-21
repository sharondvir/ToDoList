import argparse
import json
import time
import pickle
from datetime import datetime

class TaskEntry:
        def __init__(self, taskID: int, task_name: str, priority: str, status: str = "Not Done"):
            self.taskID = taskID
            self.task_name = task_name
            self.priority = priority
            self._status = status

        @property
        def status(self):
            return self._status

        @status.setter
        def status(self, value):
            self._status = value

        def to_dict(self):
            return {"id": self.taskID, "task": self.task_name, "status": self.status, "priority": self.priority}

        @staticmethod
        def from_dict(data):
            return TaskEntry(data["id"], data["task"], data["priority"], data.get("status", "Not Done"))

        def __repr__(self):
            return f"The task is : {self.task_name} , priority: {self.priority}, status: {self.status}"


class TaskDb:
        def __init__(self, filename='tasks.pkl'):
             self.filename = filename

        def load_tasks(self):
            '''Load tasks from a pickle file,
             handling missing 'status' keys with a default
            ,or return an empty list if file not found.'''
            try:
                with open(self.filename, 'rb') as file:
                   tasks_data = pickle.load(file)
                   for task in tasks_data:
                       if 'status' not in task:
                            task['status'] = 'Not done'  #Declaring default status
                   return [TaskEntry.from_dict(task) for task in tasks_data]
            except FileNotFoundError:
             return []

        def save_tasks(self, tasks):
             '''Save all tasks to a pickle file'''
             with open(self.filename, 'wb') as file:
                pickle.dump([task.to_dict() for task in tasks], file)

class TaskManager:
        def __init__(self):
            self.tasksDB = TaskDb()
            self.todo_list = self.tasksDB.load_tasks()
            self.task_id_counter = max((task.taskID for task in self.todo_list), default=0) + 1

        def get_current_time(self):
            '''Get the current time as a form : HH:MM:SS'''
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            return current_time

        def add_task(self,task_name,priority):
            '''Add a task to the to-do list'''
            new_task = TaskEntry(self.task_id_counter,task_name,priority)
            self.todo_list.append(new_task)
            self.tasksDB.save_tasks(self.todo_list)
            print(f" Added: {task_name} to the To Do list, time task added: {self.get_current_time()}")
            self.task_id_counter+=1

        def delete_task(self, taskID):
            '''Delete a task from the to-do list by ID'''
            found = False
            for task in self.todo_list:
                if taskID == task.taskID:
                    self.todo_list.remove(task)
                    found = True
                    print(f"Task with ID: {taskID} deleted successfully")
                    break

            if not found:
                print(f"Task with ID {taskID} not found.")
            self.tasksDB.save_tasks(self.todo_list)

        def sortTasksByPriority(self):
            '''Sort tasks in the to-do list by priority'''
            priority_dict = {"High": 3, "Medium": 2, "Low": 1}
            self.todo_list = sorted(self.todo_list, key=lambda task: priority_dict.get(task.priority, 0), reverse=True)

        def modify_taskName(self,taskID, newTaskName):
            '''Modify the name of a task identified by taskID'''
            for task in self.todo_list:
                if taskID == task.taskID:
                    task.task_name = newTaskName
                    self.tasksDB.save_tasks(self.todo_list)
                    print(f"task with id: {taskID} has been modified successfuly")
                    return
            else:
                print(f"task with id: {taskID} was not found")

        def printToDoList(self):
            '''Print the to-do list'''
            if not self.todo_list:
                print("There are no tasks in the list..")
            else:
                self.sortTasksByPriority()
                for task in self.todo_list:
                   print(f"Task ID: {task.taskID}, Task Name: {task.task_name}, priority: {task.priority} ,status: {task.status}")

        def modify_task_status(self,taskID,wantedStatus):
                '''Modify the status of a task identified by taskID'''
                exist = False
                for task in self.todo_list:
                    if task.taskID == taskID:
                        exist = True
                        task.status = wantedStatus
                        self.tasksDB.save_tasks(self.todo_list)
                        print(f"Task status was updated to {wantedStatus}! Time of update: {self.get_current_time()}")
                        return
                if not exist:
                    print(f'Task number {taskID} does not exist in the list')


        def show_status(self):
            '''Show the status of all tasks'''
            for task in self.todo_list:
                 print(f"Task name: {task.task_name}, status: {task.status}")

class ToDoList:
    def main(self):
             parser = argparse.ArgumentParser(description='To do list program')
             parser.add_argument('--command', choices=['add', 'show_list','modify_name','modify_status','show_statuses','delete_task'],
                                 help='Command to execute')
             parser.add_argument('--task', help='Name of the task')
             parser.add_argument('--taskID', type=int, help='ID of the task')
             parser.add_argument('--new_name', help='New name for the task')
             parser.add_argument('--priority', help='Priority of the task')
             parser.add_argument('--status', help='Status for the task')
             parser.add_argument('--show_statuses', help = 'show statuses of all the tasks')
             parser.add_argument('--delete_task', help = 'Delete task by given id')

             #Parse the arguments from command line
             args = parser.parse_args()

             #Create Task manager instance
             task_manager = TaskManager()

             #Process different commands based on the provided arguments
             if args.command == 'add':
                 # Check if task name and priority are provided,then add the task
                 if args.task and args.priority:
                     task_manager.add_task(args.task, args.priority)
                 else:
                     print("For adding task to ToDo list task name and priority are reqired")

             elif args.command == 'modify_name':
                 #Check if task id and new task name are provided,then modify task's name
                 if args.taskID and args.new_name:
                     task_manager.modify_taskName(args.taskID, args.new_name)
                 else:
                     print("Modifing task name reqired task name and task ID")

             elif args.command == 'modify_status':
                 # Check if task id and status are provided,then modify task's status
                 if args.taskID and args.status:
                     task_manager.modify_task_status(args.taskID, args.status)
                 else:
                     print("Updating task reqired task ID and wanted status")

             elif args.command == 'delete_task':
                 #Check if task id is provided,then delete the task
                 if args.taskID:
                     task_manager.delete_task(args.taskID)

             elif args.command == 'show_list':
                 #Call print to-do list method
                 task_manager.printToDoList()

             elif args.command == 'show_statuses':
                 #Call show statuses method
                 task_manager.show_status()
             else:
                 parser.print_help()


if __name__ == "__main__":
    todo_list = ToDoList()
    todo_list.main()