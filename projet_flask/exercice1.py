from flask import Flask, jsonify
import requests
import csv

app = Flask(__name__)

# Function to fetch todos from the API
def fetch_todos():
    url = "https://jsonplaceholder.typicode.com/todos"
    response = requests.get(url)
    if response.status_code == 200:
        print("Todos fetched successfully!")
        return response.json()
    else:
        return []

# Function to save todos into a CSV file
def save_todos_to_csv(todos, file_name="todos.csv"):
    with open(file_name, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["userId", "id", "title", "completed"])
        writer.writeheader()
        writer.writerows(todos)

@app.route("/fetch-todos", methods=["GET"])
def get_todos():
    print("Fetching todos...")
    todos = fetch_todos()
    if todos:
        save_todos_to_csv(todos)
        return jsonify({"message": "Todos fetched and saved to CSV successfully!"}), 200
    else:
        return jsonify({"message": "Failed to fetch todos."}), 500

if __name__ == "__main__":
    app.run(debug=True)
