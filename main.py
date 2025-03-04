import psycopg2
from flask import Flask, jsonify, request
from psycopg2.extras import RealDictCursor

app = Flask(__name__)


def connect_to_db():
    conn = psycopg2.connect(database='Employee_DataBase', user='administrator', password='root', host='localhost',
                            port='5432')
    return conn


@app.route('/employees', methods=['POST'])
def add_employee():
    data = request.get_json()
    name = data.get('name')
    position = data.get('position')

    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute('INSERT INTO Employee (name, position) VALUES (%s, %s) RETURNING employee_id', (name, position))
    employee_id = cursor.fetchone()[0]
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'id': employee_id, 'name': name, 'position': position}), 201


@app.route('/employees', methods=['GET'])
def get_employees_list():
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute('SELECT employee_id, name, position FROM Employee')
    employees = cursor.fetchall()
    cursor.close()
    connection.close()

    employees_list = [{'id': emp[0], 'name': emp[1], 'position': emp[2]} for emp in employees]
    return jsonify(employees_list), 200


@app.route('/employees/<int:employee_id>', methods=['GET'])
def get_employee(employee_id):
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute('SELECT employee_id, name, position FROM Employee WHERE employee_id = %s', (employee_id,))
    employee = cursor.fetchone()
    cursor.close()
    connection.close()

    if employee is None:
        return jsonify({'Error': 'Employee not found'}), 404

    return jsonify({'id': employee[0], 'name': employee[1], 'position': employee[2]}), 200


@app.route('/employees/<int:employee_id>', methods=['PUT'])
def update_info(employee_id):
    data = request.get_json()
    name = data.get('name')
    position = data.get('position')

    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute('UPDATE Employee SET name = %s, position = %s WHERE employee_id = %s RETURNING employee_id, name, position', (name, position, employee_id))
    updated_employee = cursor.fetchone()
    connection.commit()
    cursor.close()
    connection.close()

    if updated_employee:
        return jsonify({'id': updated_employee[0], 'name': updated_employee[1], 'position': updated_employee[2]}), 200
    else:
        return jsonify({'message': 'Employee not found'}), 404


@app.route('/employees/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute('DELETE FROM Employee WHERE employee_id = %s', (employee_id,))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'message': 'Employee deleted successfully'}), 200


if __name__ == '__main__':
    app.run(debug=True)