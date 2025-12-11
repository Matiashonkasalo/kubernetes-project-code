from flask import Flask, send_file, render_template, request, redirect
import requests
import time
import os

app = Flask(__name__)

#reading port using environmental variable
MAX_AGE = 600
port = int(os.getenv("PORT",8000))
CACHE_IMAGE = os.getenv("CACHE_IMAGE", "image not found")
CACHE_TIMESTAMP = os.getenv("CACHE_TIMESTAMP", "timestamp not found")
TODO_BACKEND_URL = os.getenv("TODO_BACKEND_URL", "Backend URL not found")
IMAGE_SOURCE_URL = os.getenv("IMAGE_SOURCE_URL", "Image source not found")


print(f"Server started in port {port}")

def valid_cache():
    if not os.path.exists(CACHE_IMAGE):
        return False
    if not os.path.exists(CACHE_TIMESTAMP):
        return False
    try:
        with open(CACHE_TIMESTAMP,"r") as f:
            ts = float(f.read().strip())
    except:
        return False
    return (time.time() - ts) < MAX_AGE

def update_image():
    response = requests.get(IMAGE_SOURCE_URL)
    with open(CACHE_IMAGE, "wb") as f:
        f.write(response.content)
    with open(CACHE_TIMESTAMP, "w") as f:
        f.write(str(time.time()))

@app.get("/")
def home():
    print("Request received!")
    if not valid_cache():
        print("Cache expired -> fetching new image")
        update_image()
    todos = requests.get(TODO_BACKEND_URL).json()
    return render_template("index.html", todos=todos)


@app.get("/image")
def image():
    return send_file(CACHE_IMAGE, mimetype="image/jpeg")

@app.post("/todos")
def todos_to_back():
    content = request.form.get("content") #gets the todo from browser

    ###send the content to backend 
    requests.post(
        TODO_BACKEND_URL,
    json={"content": content}
    )
    ##redirect the page
    return redirect("/")


@app.post("/todos/<id>")
def update_todo_frontend(id):
    """
    This receives the form submission from the HTML.
    It converts it into a real PUT request for the backend.
    """

    # Check if the form requests a PUT
    method = request.form.get("_method", "").upper()
    if method != "PUT":
        return "Invalid method", 400

    # Read the new "done" value from the form
    done_value = request.form.get("done", "false").lower() == "true"

    # Forward the update to the backend
    requests.put(
        f"{TODO_BACKEND_URL}/{id}",
        json={"done": done_value}
    )
    # Go back to the main page
    return redirect("/")


    
@app.get("/healthz")
def healthz():
    return "OK", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port)
