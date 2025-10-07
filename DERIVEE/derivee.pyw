from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def descente_gradient_multi(table, alpha=0.01, iterations=1000, show_all=False):
    X = [ligne[:-1] for ligne in table]
    Y = [ligne[-1] for ligne in table]
    n = len(X)
    m = len(X[0])
    a = [0.0] * m
    b = 0.0
    logs = []

    for it in range(1, iterations + 1):
        Y_pred = [sum(a[j] * X[i][j] for j in range(m)) + b for i in range(n)]
        residus = [Y_pred[i] - Y[i] for i in range(n)]
        da = [(2 / n) * sum(residus[i] * X[i][j] for i in range(n)) for j in range(m)]
        db = (2 / n) * sum(residus)

        for j in range(m):
            a[j] -= alpha * da[j]
        b -= alpha * db

        cout = (1 / n) * sum((Y_pred[i] - Y[i]) ** 2 for i in range(n))

        if show_all:
            logs.append(f"Itération {it}: Coefficients={[round(ai,4) for ai in a]}, b={b:.4f}, Cout={cout:.6f}")
        else:
            if it <= 10 or it > iterations - 10:
                logs.append(f"Itération {it}: Coefficients={[round(ai,4) for ai in a]}, b={b:.4f}, Cout={cout:.6f}")
            elif it == 11:
                logs.append("…")

    return a, b, logs

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/calculate", methods=["POST"])
def calculate():
    try:
        data = request.get_json()
        table = data.get("table")
        alpha = float(data.get("alpha", 0.01))
        iterations = int(data.get("iterations", 1000))
        show_all = bool(data.get("show_all", False))

        if not table or not isinstance(table, list):
            return jsonify({"error": "Tableau de données invalide."})

        a, b, logs = descente_gradient_multi(table, alpha, iterations, show_all)
        eq = " + ".join([f"{a[j]:.4f}*X{j+1}" for j in range(len(a))])
        equation = f"Y = {eq} + {b:.4f}"

        return jsonify({"equation": equation, "coefficients": a, "b": b, "logs": logs})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True,port=5000)
