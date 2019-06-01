import os
from py2neo import Graph
import ast
from json import dumps
from flask import Flask, render_template, g, Response, request
from neo4j import GraphDatabase, basic_auth

app = Flask(__name__)
app.debug = True

# The password must be changed to your NEO4J password.
driver = GraphDatabase.driver('bolt://localhost',auth=basic_auth("neo4j", '6669'))
hold = '?'
def get_db():
    if not hasattr(g, 'neo4j_db'):
        g.neo4j_db = driver.session()
    return g.neo4j_db

@app.route("/")
def get_index():
    global hold
#   The cypher text between the quotes can be run on the NEO4J Browser with the Movies
#   GraphDatabase.
    hold = "MATCH (a:Person)-[r:ACTED_IN|:DIRECTED|:PRODUCED|:REVIEWED|:WROTE]->(m:Movie) RETURN 'N1L1N2' AS scrn, 'Person' AS N1L, a.name AS N1I, a.name AS N1T, type(r) AS L1L, type(r) AS L1T, 'Movie' AS N2L, m.title AS N2T, m.title AS N2I ORDER BY N1I"
    return render_template("Movies_Exp_index.html")

@app.route("/graph")
def get_graph():
    db = get_db()
    results = db.run(hold)
    nodes = []
    rels = []
    i = 0
    N1_id = '?'
    N2_id = '?'
    N3_id = '?'
    id = ""
    sid = ""
    tid = ""

#  The screen routine below, N1L1N2, is a simple, 
#  generalized procedure for graphing 
#  a returned cypher response for a node, 
#  through a link, to a node query, (n)-[r]->(m).
#  N1 is node 1, L1 is link 1 and N2 is node 2.
#  N1L, L1L, and N2L are the node and link types
#  for the previous 3 items. 
#  N1I and N2I are identifiers for grouping togther 
#  returned response arrays for sorting requirements. 
#  In this case all the links for a paricular person (ie. name) are used
#  for sorting. If you take the cypher query above, 
#  you can follow the logic for doing each returned
#  message array.

#  "id" is the node id <id>
#  "sid" is the id of the start node
#  "tid" is the id of the target node

# The N1T, L1T and N2T variables are text messages that are displayed on nodes and links.
# The text is under program control so it can be tailored.

    for record in results:
        zz = record["scrn"]
        if zz == 'N1L1N2':
            if N1_id != record["N1I"]:
                id = i
                nodes.append({"label": record["N1L"], "id" : i, "title" : record["N1T"]})
                N1_id = record["N1I"]
                x = i
                i = i + 1
            else:
                N1_id = record["N1I"]

            nodes.append({"label": record["N2L"], "id" : i, "title" : record["N2T"] })
            N2_id = record["N2I"]
            y = i
            i = i + 1

            sid = x
            tid = y
            rels.append({"source": x, "target": y, "label": record["L1L"], "title": record["L1T"], "sid" : sid, "tid" : tid})
 
    return Response(dumps({"nodes": nodes, "links": rels}), mimetype="application/json")

app.run(host='127.0.0.1', port= 5000)
