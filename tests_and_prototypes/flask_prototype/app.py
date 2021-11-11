from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

@app.route("/") # Root route
def home_page():
    example_embed = "This string is from python"
    return render_template("index.html", embed = example_embed)

@app.route('/test.html', methods=['GET','POST'])
def testfn():
    # GET request
    if request.method == 'GET':
        message = {'greeting': 'hello from Flask!'}
        return jsonify(message)

    # POST request
    if request.method == 'POST':
        print(request.get_json())
        return 'Success', 200

if __name__ == "__main__":
    app.run(debug=False)