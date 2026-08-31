"""
DataMorph Studio - Pure Python N-Dimensional Tensor & Autograd Engine
Implements dynamic reverse-mode automatic differentiation computation graphs without PyTorch/NumPy.
"""

import math
from typing import List, Tuple, Union, Optional, Set, Callable


class Tensor:
    """N-Dimensional Autograd Tensor with dynamic backward graph construction."""
    def __init__(self, data: Union[float, List[Any]], _children: Tuple["Tensor", ...] = (), _op: str = ""):
        self.data: Any = data
        self.grad: Any = 0.0
        self._backward: Callable[[], None] = lambda: None
        self._prev: Set["Tensor"] = set(_children)
        self._op: str = _op

    def __repr__(self) -> str:
        return f"Tensor(data={self.data}, grad={self.grad})"

    def __add__(self, other: Union["Tensor", float]) -> "Tensor":
        other = other if isinstance(other, Tensor) else Tensor(other)
        out = Tensor(self.data + other.data, (self, other), "+")

        def _backward():
            self.grad += 1.0 * out.grad
            other.grad += 1.0 * out.grad
        out._backward = _backward
        return out

    def __mul__(self, other: Union["Tensor", float]) -> "Tensor":
        other = other if isinstance(other, Tensor) else Tensor(other)
        out = Tensor(self.data * other.data, (self, other), "*")

        def _backward():
            self.grad += other.data * out.grad
            other.grad += self.data * out.grad
        out._backward = _backward
        return out

    def __pow__(self, other: Union[int, float]) -> "Tensor":
        assert isinstance(other, (int, float)), "only supporting int/float powers for now"
        out = Tensor(self.data ** other, (self,), f"**{other}")

        def _backward():
            self.grad += (other * (self.data ** (other - 1))) * out.grad
        out._backward = _backward
        return out

    def relu(self) -> "Tensor":
        out = Tensor(self.data if self.data > 0 else 0.0, (self,), "ReLU")

        def _backward():
            self.grad += (1.0 if self.data > 0 else 0.0) * out.grad
        out._backward = _backward
        return out

    def gelu(self) -> "Tensor":
        """Gaussian Error Linear Unit (GELU) activation."""
        x = self.data
        cdf = 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))
        out = Tensor(x * cdf, (self,), "GELU")

        def _backward():
            pdf = (1.0 / math.sqrt(2.0 * math.pi)) * math.exp(-0.5 * (x ** 2))
            d_gelu = cdf + x * pdf
            self.grad += d_gelu * out.grad
        out._backward = _backward
        return out

    def backward(self):
        """Topological sort execution for full backpropagation gradient accumulation."""
        topo: List[Tensor] = []
        visited: Set[Tensor] = set()

        def build_topo(v: Tensor):
            if v not in visited:
                visited.add(v)
                for child in v._prev:
                    build_topo(child)
                topo.append(v)

        build_topo(self)
        self.grad = 1.0
        for node in reversed(topo):
            node._backward()
