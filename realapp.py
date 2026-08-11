from flask import Flask, g, redirect, render_template, request, url_for
import sqlite3

DATABASE = 'wordsdata.db'

app = Flask(__name__)

# retriving everything from the database
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


# connecting everything from wordsdata.db

@app.route("/")
def hello_world():
    sql = """
                SELECT Japan.JapanID,Makers.Name, Japan.Letter,Japan.ImageURL,Japan.English
                FROM Japan
                JOIN Makers ON Makers.MakerID=Japan.MakerID;"""
    results = query_db(sql)
    return render_template("home.html", results=results)
#rendering template
@app.route("/japan/<int:id>")
def japan(id):
    sql="""SELECT * FROM Japan 
    JOIN Makers on Makers.MakerID=Japan.MakerID
    WHERE Japan.JapanID = ?;"""
    result = query_db(sql, [id], one=True)
    return render_template("japan.html", result=result)


 #for my maker, when clicked on each alphabet, all of the following should pop up.  
@app.route("/maker/<int:id>")
def maker(id):
    sql="""SELECT Japan.JapanID,Makers.Name, Japan.Letter,Japan.ImageURL,Japan.English
                FROM Japan
                JOIN Makers ON Makers.MakerID=Japan.MakerID
                WHERE Makers.MakerID = ?;"""
    results = query_db(sql, [id])
    return render_template("maker.html", results=results, id=id)

#sending to my contact page
@app.route('/contact')
def contact():
    return render_template("contact.html")

#sending to my histroy page
@app.route('/history')
def history():
    return render_template("history.html")
#search bar for alphabets
@app.route("/search")
def search():
    query = request.args.get("query")
    maker_id = request.args.get("id")

    if query and maker_id:
        query = query.lower()

        sql = """
        SELECT JapanID
        FROM Japan
        WHERE LOWER(English) = ?
        AND MakerID = ?;
        """

        result = query_db(sql, [query, maker_id], one=True)

        if result:
            return redirect(url_for("japan", id=result[0]))

    return "Letter not found"



#login page
@app.route("/submit", methods=["POST"])
def submit():
    username = request.form.get("username")
    password = request.form.get("password")

    return f"Data Received - Username: {username}, Password: {password}"

if __name__ == "__main__":
    app.run(debug=True)