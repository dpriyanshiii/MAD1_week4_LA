from flask import Flask, render_template, request
import csv
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

app = Flask(__name__)

def read_csv_data():
    """Read data from CSV file and return as list of dictionaries"""
    data = []
    try:
        with open('data.csv', 'r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                data.append({
                    'Student ID': row['Student ID'],
                    'Course ID': row['Course ID'],
                    'Marks': int(row['Marks'])
                })
    except FileNotFoundError:
        print("data.csv file not found!")
    return data

@app.route('/', methods=['GET', 'POST'])
def index():
    # Handle GET requests with URL parameters (for test cases)
    if request.method == 'GET':
        student_id = request.args.get('student_id')
        course_id = request.args.get('course_id')
        
        if student_id:
            id_type = 'student_id'
            id_value = student_id
        elif course_id:
            id_type = 'course_id' 
            id_value = course_id
        else:
            return render_template('index.html')
    
    # Handle POST requests (form submissions)
    elif request.method == 'POST':
        id_type = request.form.get('ID')
        id_value = request.form.get('id_value', '').strip()
    
    # If we have ID to process (from GET or POST)
    if 'id_type' in locals() and id_value:
        if not id_value:
            return render_template('error.html', message="Please enter an ID value")
        
        data = read_csv_data()
        
        if id_type == 'student_id':
            student_data = [row for row in data if row['Student ID'] == id_value]
            
            if not student_data:
                return render_template('error.html', message=f"Student {id_value} not found"), 404
            
            total_marks = sum(row['Marks'] for row in student_data)
            
            return render_template('student.html', 
                                 student_data=student_data, 
                                 total_marks=total_marks,
                                 student_id=id_value)
        
        elif id_type == 'course_id':
            course_data = [row for row in data if row['Course ID'] == id_value]
            
            if not course_data:
                return render_template('error.html', message=f"Course {id_value} not found"), 404
            
            marks = [row['Marks'] for row in course_data]
            average_marks = round(sum(marks) / len(marks), 2)
            maximum_marks = max(marks)
            
            # Create histogram
            plt.figure(figsize=(8, 6))
            plt.hist(marks, bins=10, edgecolor='black', alpha=0.7)
            plt.title(f'Marks Distribution for Course {id_value}')
            plt.xlabel('Marks')
            plt.ylabel('Number of Students')
            plt.grid(True, alpha=0.3)
            
            plot_filename = f'histogram_{id_value}.png'
            plot_path = os.path.join('static', plot_filename)
            plt.savefig(plot_path)
            plt.close()
            
            return render_template('course.html',
                                 average_marks=average_marks,
                                 maximum_marks=maximum_marks,
                                 course_id=id_value,
                                 plot_filename=plot_filename)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)