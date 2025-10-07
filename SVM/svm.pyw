import matplotlib
matplotlib.use('Agg') 

from flask import Flask, render_template, request, jsonify
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from sklearn.svm import SVC
from mpl_toolkits.mplot3d import Axes3D

app = Flask(__name__)

model = None
X_global = None
y_global = None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/calculate", methods=["POST"])
def calculate():
    global model, X_global, y_global
    try:
        data = request.get_json()
        table = data.get("table")
        if not table or not isinstance(table, list):
            return jsonify({"error": "Tableau de données invalide."})

        X = np.array([row[:-1] for row in table])
        y = np.array([row[-1] for row in table])

        if len(set(y)) != 2:
            return jsonify({"error": "Pour SVM, Y doit contenir exactement deux classes."})

        model = SVC(kernel="linear")
        model.fit(X, y)

        X_global = X
        y_global = y

        fig = plt.figure(figsize=(8, 6))
        if X.shape[1] == 2:
            ax = fig.add_subplot(111)
            plot_2d_svm(X, y, model, ax)
        elif X.shape[1] == 3:
            ax = fig.add_subplot(111, projection="3d")
            plot_3d_svm(X, y, model, ax)
        else:
            return jsonify({"error": "Seulement données 2D ou 3D supportées."})

        buf = BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        plt.close(fig)

        return jsonify({"image": "data:image/png;base64," + base64.b64encode(buf.read()).decode("utf-8")})

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/classify", methods=["POST"])
def classify():
    global model, X_global, y_global
    try:
        data = request.get_json()
        point = data.get("point")
        if not point or model is None:
            return jsonify({"error": "Point invalide ou modèle non entraîné."})

        point_arr = np.array(point).reshape(1, -1)
        prediction = model.predict(point_arr)[0]

        return jsonify({"class": int(prediction)})
    except Exception as e:
        return jsonify({"error": str(e)})

def plot_2d_svm(X, y, model, ax):
    ax.scatter(X[:, 0], X[:, 1], c=y, s=50, cmap="coolwarm")
    ax.set_xlabel("X1")
    ax.set_ylabel("X2")
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    xx, yy = np.meshgrid(np.linspace(xlim[0], xlim[1], 30),
                         np.linspace(ylim[0], ylim[1], 30))
    Z = model.decision_function(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)
    ax.contour(xx, yy, Z, colors="k", levels=[0], alpha=0.7, linestyles=["-"])
    ax.contourf(xx, yy, Z > 0, alpha=0.1)

def plot_3d_svm(X, y, model, ax):
    ax.scatter(X[:, 0], X[:, 1], X[:, 2], c=y, s=50, cmap="coolwarm")
    ax.set_xlabel("X1")
    ax.set_ylabel("X2")
    ax.set_zlabel("X3")
    coef = model.coef_[0]
    intercept = model.intercept_[0]
    xx, yy = np.meshgrid(np.linspace(X[:,0].min(), X[:,0].max(), 10),
                         np.linspace(X[:,1].min(), X[:,1].max(), 10))
    zz = (-coef[0] * xx - coef[1] * yy - intercept) / coef[2]
    ax.plot_surface(xx, yy, zz, alpha=0.3)

if __name__ == "__main__":
    app.run(debug=True,port=5002)
