from flask import Flask, render_template, jsonify, request
from random import randint
import json


app = Flask(__name__)
app.secret_key = "ae4g92h1c0f6qbn5tyj"
app.debug = True


@app.route("/", methods=["GET"])
def index():
    """Route for index page."""
    return render_template("index.html")

@app.route("/career-jobs", methods=["GET"])
def career_jobs():
    """Route to retrieve career jobs."""
    file = open("career-jobs.txt", "r")
    result = json.loads(file.read())
    file.close()

    return jsonify(result), 200

@app.route("/teaching-styles", methods=["GET"])
def teaching_styles():
    """Route to retrieve teaching styles."""
    file = open("teaching-styles.txt", "r")
    result = json.loads(file.read())
    file.close()

    return jsonify(result), 200

@app.route("/data-set", methods=["GET"])
def data_set():
    """Route for data-set page."""
    return render_template("data-set.html")


@app.route("/generate-data", methods=["GET"])
def generate_data():
    """Route to generate dummy data-set"""

    file = open("career-jobs.txt", "r")
    jobs = json.loads(file.read())
    file.close()

    file = open("teaching-styles.txt", "r")
    teach_styles = json.loads(file.read())
    file.close()

    grades = ["A", "B", "C", "D"]
    subjects = [
        ("142", "Advanced Mathematics"),
        ("131", "Physics"),
        ("132", "Chemistry")
    ]
    programmes = [
        ("Bachelor of Science in Software Engineering", ("131", "132", "142")),
        ("Bachelor of Science in Telecommunications Engineering", ("131", "132", "142")),
        ("Bachelor of Science in Computer Engineering", ("131", "132", "142")),
        ("Bachelor of Science in Computer Science", ("131", "132", "142")),
        ("Bachelor of Science in Business Information Systems", ("131", "132", "142")),
        ("Bachelor of Science in Information Systems", ("131", "132", "142")),
    ]

    results = []
    entries = int(request.args.get("entries")) if request.args.get("entries") else 25

    for i in range(0, entries):
        j = randint(0, len(programmes)-1) # programme index
        p = programmes[j][0] # programme name
        r = programmes[j][1] # programme prerequisites

        s = [] # random subject results
        while len(s) < len(r):
            t = randint(0, len(subjects)-1) # random subject index
            if (subjects[t][0] in r) and (subjects[t][0] not in list(map(lambda z: z["subject_code"], s))):
                u = randint(0, len(grades)-1)  # random grade index
                s.append({"subject_code": subjects[t][0], "subject_name": subjects[t][1], "grade": grades[u]})

        v = [] # random career jobs
        for w in range(0, randint(1, len(jobs)-1)):
            z = jobs[randint(0, len(jobs) - 1)]
            if z not in v:
                v.append(z)

        x = []  # random teaching styles
        for y in range(0, randint(1, len(teach_styles) - 1)):
            z = teach_styles[randint(0, len(teach_styles) - 1)]
            if z not in x:
                x.append(z)

        result = {"programme": p, "subjects": s, "jobs": v, "teaching-styles": x}
        results.append(result)

    file = open("data-set.txt", "w")
    file.write(json.dumps(results))
    file.close()

    return jsonify(results), 200


@app.route("/get-data-set", methods=["GET"])
def get_data_set():
    """Route to retrieve data-set."""
    file = open("data-set.txt", "r")
    result = json.loads(file.read())
    file.close()

    return jsonify(result), 200

@app.route("/recommend", methods=["POST"])
def recommend():
    """Route to recommend a degree programme(s)"""

    response = {
        "status": 0,
        "programmes": []
    }

    file = open("data-set.txt", "r")
    data = file.read()
    file.close()

    training_set = json.loads(data)
    user_input = request.get_json(force=True)
    subjects = sorted(user_input["subjects"], key=lambda k: k["subject_code"])
    job = user_input["job"] if "job" in user_input else ""
    teach_styles = user_input["teaching_styles"]
    subjects = list(map(lambda x: "{0} {1}".format(x["subject_code"], x["grade"]), subjects))

    # group each programme with their results in a matrix-like representation
    # [{"programme": "BSc SE", "subjects": [[], [], []]}]
    programmes = []
    for p in range(0, len(training_set)):
        r = training_set[p]
        if r["programme"] not in list(map(lambda x: x["programme"], programmes)):
            programmes.append({"programme": r["programme"], "subjects": [], "jobs": [], "teaching-styles": []})
        else:
            for s in range(0, len(programmes)):
                t = programmes[s]
                if r["programme"] == t["programme"]:
                    programmes[s]["subjects"].append(list(map(lambda x: "{0} {1}".format(x["subject_code"], x["grade"]), sorted(r["subjects"], key=lambda k: k["subject_code"]))))
                    programmes[s]["jobs"].append(r["jobs"])
                    programmes[s]["teaching-styles"].append(r["teaching-styles"])

    # after grouping, look for similar results to the supplied user input
    recommendations = []

    for p in range(0, len(programmes)):
        recommendations.append({
            "programme": programmes[p]["programme"],
            "total": len(programmes[p]["subjects"]),
            "matched": 0,
            "matched_jobs": 0,
            "matched_teaching_styles": 0,
            "score": 0
        })

        for s in programmes[p]["subjects"]:
            if set(s).issubset(set(subjects)):
                recommendations[p]["matched"] += 1

        for s in programmes[p]["jobs"]:
            if job in s:
                recommendations[p]["matched_jobs"] += 1

        for s in programmes[p]["teaching-styles"]:
            for t in teach_styles:
                if t in s:
                    recommendations[p]["matched_teaching_styles"] += 1

    # now we have a data structure of the form
    """
    [
        {
            "matched": 22, 
            "matched_jobs": 309, 
            "matched_teaching_styles": 695, 
            "programme": "Bachelor of Science in Computer Science", 
            "total": 844,
            "score": 0
        }, 
        {
            "matched": 19, 
            "matched_jobs": 302, 
            "matched_teaching_styles": 638, 
            "programme": "Bachelor of Science in Software Engineering", 
            "total": 830,
            "score": 0
        }, 
        {
            "matched": 17, 
            "matched_jobs": 320, 
            "matched_teaching_styles": 660, 
            "programme": "Bachelor of Science in Telecommunications Engineering", 
            "total": 818,
            "score": 0
        }
    ]
    """

    # we finally calculate scores for each recommendation
    for i in range(0, len(recommendations)):
        r = recommendations[i]
        mean = (r["matched"] + r["matched_jobs"] + r["matched_teaching_styles"]) / r["total"]
        mean_squares = pow((r["matched"] - mean), 2) + pow((r["matched_jobs"] - mean), 2) + pow((r["matched_teaching_styles"] - mean), 2)
        var = mean_squares / r["total"]
        r["score"] = pow(var, 0.5)

        if r["matched"] > 0:
            response["status"] = 1

    recommendations = sorted(recommendations, key=lambda k: k["score"], reverse=False)  # sort in descending order
    recommendations = recommendations[:3]  # limit to 3 items
    response["programmes"] = recommendations

    return jsonify(response), 200


@app.errorhandler(404)
def page_not_found(e):
    return "404"


if __name__ == "__main__":
    app.run()
