from flask import Flask, render_template, request, jsonify
from math import isclose

app = Flask(__name__)

class Matrice:
    def __init__(self, data):
        if not all(len(ligne) == len(data[0]) for ligne in data):
            raise ValueError("Toutes les lignes doivent avoir la même longueur.")
        self.data = [list(map(float, ligne)) for ligne in data]
        self.lignes = len(data)
        self.colonnes = len(data[0])

    def __repr__(self):
        return "\n".join(["[" + " ".join(f"{v:8.3f}" for v in ligne) + "]" for ligne in self.data])

    def transposee(self):
        trans = [[self.data[j][i] for j in range(self.lignes)] for i in range(self.colonnes)]
        return Matrice(trans)

    def __matmul__(self, autre):
        if not isinstance(autre, Matrice):
            raise TypeError("Le produit matriciel doit être effectué entre deux matrices.")
        if self.colonnes != autre.lignes:
            raise ValueError("Dimensions incompatibles pour le produit matriciel.")
        resultat = []
        for i in range(self.lignes):
            ligne = []
            for j in range(autre.colonnes):
                somme = sum(self.data[i][k] * autre.data[k][j] for k in range(self.colonnes))
                ligne.append(somme)
            resultat.append(ligne)
        return Matrice(resultat)

    def inverse(self):
        if self.lignes != self.colonnes:
            raise ValueError("Seules les matrices carrées peuvent être inversées.")
        n = self.lignes
        A = [row[:] + [1 if i == j else 0 for j in range(n)] for i, row in enumerate(self.data)]
        for i in range(n):
            pivot = A[i][i]
            if isclose(pivot, 0.0):
                for r in range(i+1, n):
                    if not isclose(A[r][i], 0.0):
                        A[i], A[r] = A[r], A[i]
                        pivot = A[i][i]
                        break
                else:
                    raise ValueError("Matrice non inversible.")
            A[i] = [x / pivot for x in A[i]]
            for j in range(n):
                if j != i:
                    facteur = A[j][i]
                    A[j] = [A[j][k] - facteur * A[i][k] for k in range(2*n)]
        inverse = [row[n:] for row in A]
        return Matrice(inverse)

def preparer_donnees(table):
    X = [ligne[:-1] for ligne in table]
    Y = [ligne[-1] for ligne in table]
    for ligne in X:
        ligne.append(1.0)
    M = Matrice(X)
    Yv = Matrice([[y] for y in Y])
    return M, Yv

def regression_generale(table):
    M, Y = preparer_donnees(table)
    Mt = M.transposee()
    ab = (Mt @ M).inverse() @ Mt @ Y
    return ab

def afficher_equation(coeffs):
    equation = "Y = "
    for i in range(coeffs.lignes - 1):
        equation += f"{coeffs.data[i][0]:.3f}*X{i+1} + "
    equation += f"{coeffs.data[-1][0]:.3f}"
    return equation

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/calculate", methods=["POST"])
def calculate():
    try:
        data = request.json.get("table")
        coeffs = regression_generale(data)
        equation = afficher_equation(coeffs)
        return jsonify({"coeffs": coeffs.data, "equation": equation})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True,port=5001)
