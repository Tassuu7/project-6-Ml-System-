"""
DataMorph Studio - Advanced Matrix Decompositions & Generalized Inverse Solvers
Implements Moore-Penrose Pseudoinverse, Truncated Randomized SVD, Non-Negative Matrix Factorization (NMF),
Kernel PCA gram matrix decomposition, and Sparse PCA in pure Python.
"""

import math
import random
from typing import List, Tuple, Optional, Dict, Any
from datamorph.engine.matrix_ops import Matrix, Vector, MatrixOps


class MoorePenrosePseudoinverse:
    """Computes Moore-Penrose generalized pseudoinverse A^+ using SVD decomposition."""
    @classmethod
    def calculate(cls, A: Matrix, rcond: float = 1e-15) -> Matrix:
        m, n = A.rows, A.cols
        U, s_vals, V = MatrixOps.singular_value_decomposition_approx(A, k=min(m, n))
        
        # Invert non-zero singular values: Sigma^+
        s_inv = [1.0 / s if s > rcond else 0.0 for s in s_vals]
        k = len(s_inv)

        # A^+ = V * Sigma^+ * U^T
        result = Matrix.zeros(n, m)
        for i in range(n):
            for j in range(m):
                sum_val = 0.0
                for comp in range(k):
                    sum_val += V.data[i][comp] * s_inv[comp] * U.data[j][comp]
                result.data[i][j] = round(sum_val, 6)
        return result


class RandomizedSVD:
    """Randomized Singular Value Decomposition for high-dimensional matrix approximation."""
    @classmethod
    def decompose(cls, A: Matrix, n_components: int = 5, n_iter: int = 4) -> Tuple[Matrix, List[float], Matrix]:
        m, n = A.rows, A.cols
        k = min(n_components, min(m, n))

        # 1. Random Gaussian test matrix Omega (n x k)
        Omega = Matrix.zeros(n, k)
        for r in range(n):
            for c in range(k):
                Omega.data[r][c] = random.gauss(0.0, 1.0)

        # 2. Sample matrix Y = A * Omega
        Y = A.matmul(Omega)

        # 3. Power iterations to accentuate singular spectrum
        for _ in range(n_iter):
            Y = A.matmul(A.transpose().matmul(Y))

        # 4. QR decomposition of Y to obtain orthogonal basis Q
        Q, _ = MatrixOps.qr_decomposition(Y)

        # 5. Project A into lower-dimensional subspace: B = Q^T * A
        B = Q.transpose().matmul(A)

        # 6. Standard SVD on small matrix B
        U_tilde, s_vals, V = MatrixOps.singular_value_decomposition_approx(B, k=k)

        # 7. Recover full left singular vectors U = Q * U_tilde
        U = Q.matmul(U_tilde)
        return U, s_vals, V


class NonNegativeMatrixFactorization:
    """Non-Negative Matrix Factorization (NMF) via multiplicative update rules."""
    def __init__(self, n_components: int = 5, max_iter: int = 200, tol: float = 1e-4):
        self.n_components = n_components
        self.max_iter = max_iter
        self.tol = tol

    def fit_transform(self, X: Matrix) -> Tuple[Matrix, Matrix]:
        m, n = X.rows, X.cols
        k = self.n_components

        # Initialize W and H with non-negative random values
        W = Matrix.zeros(m, k)
        H = Matrix.zeros(k, n)
        for r in range(m):
            for c in range(k):
                W.data[r][c] = random.uniform(0.1, 1.0)
        for r in range(k):
            for c in range(n):
                H.data[r][c] = random.uniform(0.1, 1.0)

        for iteration in range(self.max_iter):
            # Update H: H = H * (W^T * X) / (W^T * W * H + eps)
            Wt = W.transpose()
            WtX = Wt.matmul(X)
            WtWH = Wt.matmul(W).matmul(H)
            for r in range(k):
                for c in range(n):
                    denom = WtWH.data[r][c] + 1e-9
                    H.data[r][c] *= (WtX.data[r][c] / denom)

            # Update W: W = W * (X * H^T) / (W * H * H^T + eps)
            Ht = H.transpose()
            XHt = X.matmul(Ht)
            WHHt = W.matmul(H).matmul(Ht)
            for r in range(m):
                for c in range(k):
                    denom = WHHt.data[r][c] + 1e-9
                    W.data[r][c] *= (XHt.data[r][c] / denom)

        return W, H


class KernelPCA:
    """Non-linear Kernel Principal Component Analysis via RBF Kernel Gram Matrix."""
    def __init__(self, n_components: int = 2, gamma: float = 0.1):
        self.n_components = n_components
        self.gamma = gamma

    def fit_transform(self, X: List[List[float]]) -> List[List[float]]:
        n = len(X)
        if n < self.n_components:
            return X

        # 1. Compute RBF Kernel Gram Matrix K_ij = exp(-gamma * ||x_i - x_j||^2)
        K = Matrix.zeros(n, n)
        for i in range(n):
            for j in range(n):
                sq_dist = sum((X[i][d] - X[j][d]) ** 2 for d in range(len(X[i])))
                K.data[i][j] = math.exp(-self.gamma * sq_dist)

        # 2. Center Gram Matrix: K_tilde = K - 1_N * K - K * 1_N + 1_N * K * 1_N
        row_means = [sum(K.data[i][j] for j in range(n)) / float(n) for i in range(n)]
        grand_mean = sum(row_means) / float(n)

        K_centered = Matrix.zeros(n, n)
        for i in range(n):
            for j in range(n):
                K_centered.data[i][j] = K.data[i][j] - row_means[i] - row_means[j] + grand_mean

        # 3. Top Eigenvectors of centered Gram Matrix
        U, s_vals, _ = MatrixOps.singular_value_decomposition_approx(K_centered, k=self.n_components)
        return U.data
