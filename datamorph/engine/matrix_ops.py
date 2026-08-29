"""
DataMorph Studio - Pure-Python Linear Algebra & Matrix Engine
Implements fundamental matrix operations, decompositions (LU, QR, SVD, Cholesky),
eigenvalue solvers, vector spaces, and linear system solvers.
"""

import math
from typing import List, Tuple, Optional, Union, Dict, Any


class Vector:
    """
    1-Dimensional Dense Numerical Vector with Vector Space Operations.
    """
    def __init__(self, data: List[float]):
        self.data = [float(x) for x in data]
        self.size = len(self.data)

    def __len__(self) -> int:
        return self.size

    def __getitem__(self, idx: int) -> float:
        return self.data[idx]

    def __setitem__(self, idx: int, value: float):
        self.data[idx] = float(value)

    def __iter__(self):
        return iter(self.data)

    def __repr__(self) -> str:
        if self.size > 8:
            preview = ", ".join(f"{x:.4f}" for x in self.data[:4]) + ", ..., " + ", ".join(f"{x:.4f}" for x in self.data[-2:])
            return f"Vector(size={self.size}, [{preview}])"
        return f"Vector([{', '.join(f'{x:.4f}' for x in self.data)}])"

    def __add__(self, other: "Vector") -> "Vector":
        if len(self) != len(other):
            raise ValueError(f"Vector dimension mismatch: {len(self)} vs {len(other)}")
        return Vector([a + b for a, b in zip(self.data, other.data)])

    def __sub__(self, other: "Vector") -> "Vector":
        if len(self) != len(other):
            raise ValueError(f"Vector dimension mismatch: {len(self)} vs {len(other)}")
        return Vector([a - b for a, b in zip(self.data, other.data)])

    def __mul__(self, scalar: float) -> "Vector":
        return Vector([x * scalar for x in self.data])

    def __rmul__(self, scalar: float) -> "Vector":
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float) -> "Vector":
        if scalar == 0:
            raise ZeroDivisionError("Division by zero in vector scaling")
        return Vector([x / scalar for x in self.data])

    def __neg__(self) -> "Vector":
        return Vector([-x for x in self.data])

    def dot(self, other: "Vector") -> float:
        """Calculates inner dot product with another vector."""
        if len(self) != len(other):
            raise ValueError(f"Vector dimension mismatch: {len(self)} vs {len(other)}")
        return sum(a * b for a, b in zip(self.data, other.data))

    def norm(self, p: Union[int, float, str] = 2) -> float:
        """Calculates vector Lp norm (p=1, p=2 Euclidean, p='inf' Chebyshev)."""
        if p == 1:
            return sum(abs(x) for x in self.data)
        elif p == 2:
            return math.sqrt(sum(x * x for x in self.data))
        elif p == "inf" or p == float("inf"):
            return max(abs(x) for x in self.data) if self.data else 0.0
        else:
            return sum(abs(x) ** p for x in self.data) ** (1.0 / p)

    def normalize(self) -> "Vector":
        """Returns unit vector with Euclidean norm 1.0."""
        n = self.norm(2)
        if n == 0:
            return Vector([0.0] * self.size)
        return self / n

    def cosine_similarity(self, other: "Vector") -> float:
        """Computes cosine similarity in [-1.0, 1.0]."""
        n1 = self.norm(2)
        n2 = other.norm(2)
        if n1 == 0 or n2 == 0:
            return 0.0
        return self.dot(other) / (n1 * n2)

    def distance_to(self, other: "Vector", metric: str = "euclidean") -> float:
        """Computes metric distance (euclidean, manhattan, chebyshev)."""
        if metric == "manhattan":
            return (self - other).norm(1)
        elif metric == "chebyshev":
            return (self - other).norm("inf")
        else:
            return (self - other).norm(2)

    def mean(self) -> float:
        return sum(self.data) / self.size if self.size > 0 else 0.0

    def variance(self, ddof: int = 1) -> float:
        if self.size <= ddof:
            return 0.0
        m = self.mean()
        return sum((x - m) ** 2 for x in self.data) / (self.size - ddof)

    def std(self, ddof: int = 1) -> float:
        return math.sqrt(self.variance(ddof=ddof))

    def to_list(self) -> List[float]:
        return list(self.data)


class Matrix:
    """
    2-Dimensional Dense Matrix with Complete Linear Algebra Subsystem.
    """
    def __init__(self, data: List[List[float]]):
        if not data or not data[0]:
            self.data = []
            self.rows = 0
            self.cols = 0
        else:
            self.rows = len(data)
            self.cols = len(data[0])
            self.data = [[float(val) for val in row] for row in data]

    @classmethod
    def zeros(cls, rows: int, cols: int) -> "Matrix":
        return cls([[0.0 for _ in range(cols)] for _ in range(rows)])

    @classmethod
    def ones(cls, rows: int, cols: int) -> "Matrix":
        return cls([[1.0 for _ in range(cols)] for _ in range(rows)])

    @classmethod
    def identity(cls, n: int) -> "Matrix":
        mat = cls.zeros(n, n)
        for i in range(n):
            mat.data[i][i] = 1.0
        return mat

    @classmethod
    def diagonal(cls, diag_values: List[float]) -> "Matrix":
        n = len(diag_values)
        mat = cls.zeros(n, n)
        for i in range(n):
            mat.data[i][i] = float(diag_values[i])
        return mat

    @property
    def shape(self) -> Tuple[int, int]:
        return (self.rows, self.cols)

    def __getitem__(self, idx: int) -> List[float]:
        return self.data[idx]

    def __setitem__(self, idx: int, value: List[float]):
        self.data[idx] = [float(v) for v in value]

    def get(self, row: int, col: int) -> float:
        return self.data[row][col]

    def set(self, row: int, col: int, value: float):
        self.data[row][col] = float(value)

    def row(self, r: int) -> Vector:
        return Vector(self.data[r])

    def col(self, c: int) -> Vector:
        return Vector([self.data[r][c] for r in range(self.rows)])

    def copy(self) -> "Matrix":
        return Matrix([list(row) for row in self.data])

    def transpose(self) -> "Matrix":
        """Computes matrix transpose A^T."""
        trans = Matrix.zeros(self.cols, self.rows)
        for r in range(self.rows):
            for c in range(self.cols):
                trans.data[c][r] = self.data[r][c]
        return trans

    def __add__(self, other: "Matrix") -> "Matrix":
        if self.shape != other.shape:
            raise ValueError(f"Matrix shape mismatch for addition: {self.shape} vs {other.shape}")
        result = Matrix.zeros(self.rows, self.cols)
        for r in range(self.rows):
            for c in range(self.cols):
                result.data[r][c] = self.data[r][c] + other.data[r][c]
        return result

    def __sub__(self, other: "Matrix") -> "Matrix":
        if self.shape != other.shape:
            raise ValueError(f"Matrix shape mismatch for subtraction: {self.shape} vs {other.shape}")
        result = Matrix.zeros(self.rows, self.cols)
        for r in range(self.rows):
            for c in range(self.cols):
                result.data[r][c] = self.data[r][c] - other.data[r][c]
        return result

    def __mul__(self, scalar: float) -> "Matrix":
        result = Matrix.zeros(self.rows, self.cols)
        for r in range(self.rows):
            for c in range(self.cols):
                result.data[r][c] = self.data[r][c] * float(scalar)
        return result

    def __rmul__(self, scalar: float) -> "Matrix":
        return self.__mul__(scalar)

    def matmul(self, other: "Matrix") -> "Matrix":
        """Performs standard matrix multiplication A @ B."""
        if self.cols != other.rows:
            raise ValueError(f"Incompatible shapes for matmul: {self.shape} @ {other.shape}")
        result = Matrix.zeros(self.rows, other.cols)
        for i in range(self.rows):
            for k in range(self.cols):
                r_ik = self.data[i][k]
                if r_ik == 0.0:
                    continue
                for j in range(other.cols):
                    result.data[i][j] += r_ik * other.data[k][j]
        return result

    def dot_vector(self, vec: Vector) -> Vector:
        """Matrix-vector multiplication A * x."""
        if self.cols != len(vec):
            raise ValueError(f"Dimension mismatch for matrix-vector product: cols {self.cols} vs vec {len(vec)}")
        result = []
        for r in range(self.rows):
            s = 0.0
            for c in range(self.cols):
                s += self.data[r][c] * vec[c]
            result.append(s)
        return Vector(result)

    def trace(self) -> float:
        """Calculates matrix trace (sum of diagonal entries)."""
        if self.rows != self.cols:
            raise ValueError("Trace is only defined for square matrices")
        return sum(self.data[i][i] for i in range(self.rows))

    def frobenius_norm(self) -> float:
        """Calculates Frobenius matrix norm."""
        s = 0.0
        for r in range(self.rows):
            for c in range(self.cols):
                s += self.data[r][c] ** 2
        return math.sqrt(s)


class MatrixOps:
    """
    High-Level Numerical Matrix Decompositions and Equation Solvers.
    """
    @staticmethod
    def lu_decomposition(A: Matrix) -> Tuple[Matrix, Matrix, List[int]]:
        """
        Computes PLU decomposition with partial pivoting: P * A = L * U.
        Returns (L, U, permutation_vector).
        """
        n = A.rows
        if n != A.cols:
            raise ValueError("LU decomposition requires square matrix")

        U = A.copy()
        L = Matrix.identity(n)
        P = list(range(n))

        for k in range(n - 1):
            # Pivot selection
            max_val = abs(U.data[k][k])
            pivot_row = k
            for i in range(k + 1, n):
                if abs(U.data[i][k]) > max_val:
                    max_val = abs(U.data[i][k])
                    pivot_row = i

            if max_val < 1e-12:
                continue

            if pivot_row != k:
                # Swap rows in U
                U.data[k], U.data[pivot_row] = U.data[pivot_row], U.data[k]
                # Swap rows in L (up to k-1)
                for j in range(k):
                    L.data[k][j], L.data[pivot_row][j] = L.data[pivot_row][j], L.data[k][j]
                # Swap in P
                P[k], P[pivot_row] = P[pivot_row], P[k]

            for i in range(k + 1, n):
                factor = U.data[i][k] / U.data[k][k]
                L.data[i][k] = factor
                U.data[i][k] = 0.0
                for j in range(k + 1, n):
                    U.data[i][j] -= factor * U.data[k][j]

        return L, U, P

    @staticmethod
    def determinant(A: Matrix) -> float:
        """Calculates determinant of square matrix via LU decomposition."""
        if A.rows != A.cols:
            raise ValueError("Determinant is only defined for square matrices")
        n = A.rows
        try:
            L, U, P = MatrixOps.lu_decomposition(A)
            det = 1.0
            for i in range(n):
                det *= U.data[i][i]
            # Count permutations
            swaps = 0
            for i in range(n):
                if P[i] != i:
                    swaps += 1
            if (swaps // 2) % 2 == 1:
                det = -det
            return det
        except Exception:
            return 0.0

    @staticmethod
    def solve_linear_system(A: Matrix, b: Vector) -> Vector:
        """Solves linear system A * x = b via LU decomposition."""
        if A.rows != A.cols:
            raise ValueError("Square matrix required for solving linear system")
        if A.rows != len(b):
            raise ValueError("Matrix and vector dimension mismatch")

        n = A.rows
        L, U, P = MatrixOps.lu_decomposition(A)

        # Forward substitution: L * y = P * b
        pb = [b[P[i]] for i in range(n)]
        y = [0.0] * n
        for i in range(n):
            s = sum(L.data[i][j] * y[j] for j in range(i))
            y[i] = pb[i] - s

        # Back substitution: U * x = y
        x = [0.0] * n
        for i in range(n - 1, -1, -1):
            if abs(U.data[i][i]) < 1e-12:
                x[i] = 0.0
            else:
                s = sum(U.data[i][j] * x[j] for j in range(i + 1, n))
                x[i] = (y[i] - s) / U.data[i][i]

        return Vector(x)

    @staticmethod
    def inverse(A: Matrix) -> Matrix:
        """Computes matrix inverse A^-1 by solving A * x_i = e_i for each standard basis."""
        if A.rows != A.cols:
            raise ValueError("Matrix inverse requires square matrix")
        n = A.rows
        inv = Matrix.zeros(n, n)
        for j in range(n):
            e_j = Vector([1.0 if i == j else 0.0 for i in range(n)])
            x_j = MatrixOps.solve_linear_system(A, e_j)
            for i in range(n):
                inv.data[i][j] = x_j[i]
        return inv

    @staticmethod
    def cholesky_decomposition(A: Matrix) -> Matrix:
        """
        Computes Cholesky decomposition of symmetric positive-definite matrix A = L * L^T.
        """
        if A.rows != A.cols:
            raise ValueError("Cholesky decomposition requires square matrix")
        n = A.rows
        L = Matrix.zeros(n, n)

        for i in range(n):
            for j in range(i + 1):
                s = sum(L.data[i][k] * L.data[j][k] for k in range(j))
                if i == j:
                    val = A.data[i][i] - s
                    if val <= 0:
                        val = 1e-8
                    L.data[i][j] = math.sqrt(val)
                else:
                    denom = L.data[j][j]
                    L.data[i][j] = (A.data[i][j] - s) / (denom if abs(denom) > 1e-12 else 1e-8)

        return L

    @staticmethod
    def qr_decomposition(A: Matrix) -> Tuple[Matrix, Matrix]:
        """
        Computes QR decomposition using Modified Gram-Schmidt orthogonalization: A = Q * R.
        """
        m, n = A.rows, A.cols
        Q = Matrix.zeros(m, n)
        R = Matrix.zeros(n, n)

        # Copy columns of A as candidate vectors
        V = [A.col(j) for j in range(n)]

        for j in range(n):
            R.data[j][j] = V[j].norm(2)
            if R.data[j][j] > 1e-12:
                q_j = V[j] / R.data[j][j]
            else:
                q_j = Vector([0.0] * m)
            
            for i in range(m):
                Q.data[i][j] = q_j[i]

            for k in range(j + 1, n):
                R.data[j][k] = q_j.dot(V[k])
                V[k] = V[k] - (q_j * R.data[j][k])

        return Q, R

    @staticmethod
    def power_iteration_eigen(A: Matrix, max_iter: int = 100, tol: float = 1e-7) -> Tuple[float, Vector]:
        """
        Finds dominant eigenvalue and eigenvector via Power Iteration method.
        """
        n = A.rows
        b_k = Vector([1.0 / math.sqrt(n)] * n)

        for _ in range(max_iter):
            b_k1 = A.dot_vector(b_k)
            norm = b_k1.norm(2)
            if norm < 1e-12:
                return 0.0, b_k
            b_k1_norm = b_k1 / norm
            if (b_k1_norm - b_k).norm(2) < tol:
                b_k = b_k1_norm
                break
            b_k = b_k1_norm

        # Rayleigh quotient: lambda = (b^T * A * b) / (b^T * b)
        eigenvalue = b_k.dot(A.dot_vector(b_k))
        return eigenvalue, b_k

    @staticmethod
    def singular_value_decomposition_approx(A: Matrix, k: int = 2) -> Tuple[Matrix, List[float], Matrix]:
        """
        Approximates top-k SVD decomposition A ~ U * Sigma * V^T using power iteration on A^T * A.
        """
        m, n = A.rows, A.cols
        k = min(k, min(m, n))
        AtA = A.transpose().matmul(A)

        singular_values = []
        V_cols = []
        U_cols = []

        deflated = AtA.copy()
        for comp in range(k):
            eigval, v = MatrixOps.power_iteration_eigen(deflated)
            s_val = math.sqrt(max(0.0, eigval))
            singular_values.append(s_val)
            V_cols.append(v)

            # u_j = A * v_j / s_j
            if s_val > 1e-8:
                u = A.dot_vector(v) / s_val
            else:
                u = Vector([0.0] * m)
            U_cols.append(u)

            # Deflate: AtA = AtA - lambda * (v * v^T)
            for r in range(n):
                for c in range(n):
                    deflated.data[r][c] -= eigval * v[r] * v[c]

        U = Matrix.zeros(m, k)
        for r in range(m):
            for c in range(k):
                U.data[r][c] = U_cols[c][r]

        V = Matrix.zeros(n, k)
        for r in range(n):
            for c in range(k):
                V.data[r][c] = V_cols[c][r]

        return U, singular_values, V
