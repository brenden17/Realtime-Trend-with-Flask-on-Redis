from redis import Redis

from json import dumps

from flask import Flask, request, jsonify, render_template

from resource import suggest_keyword
redis = Redis()


app = Flask(__name__, template_folder=".")

@app.route("/")
def index():
    return render_template('example.html')

@app.route("/query")
def query():
    keyword = request.args.get('q', 0, type=str)
    suggests = suggest_keyword(keyword.strip())
    return dumps(suggests)


if __name__ == "__main__":
    app.debug = True
    app.run()
