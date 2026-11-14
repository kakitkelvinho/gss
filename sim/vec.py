"""Tiny 3-vector helpers. Coordinates (y-up): mm, table plane XZ, +Y is height."""

from __future__ import annotations

import math

Vec = tuple[float, float, float]

Y: Vec = (0.0, 1.0, 0.0)


def add(a: Vec, b: Vec) -> Vec:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def sub(a: Vec, b: Vec) -> Vec:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def mul(a: Vec, k: float) -> Vec:
    return (a[0] * k, a[1] * k, a[2] * k)


def dot(a: Vec, b: Vec) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a: Vec, b: Vec) -> Vec:
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def norm(a: Vec) -> float:
    return math.sqrt(dot(a, a))


def unit(a: Vec) -> Vec:
    n = norm(a)
    return (a[0] / n, a[1] / n, a[2] / n)


def yaw_dir(yaw_rad: float) -> Vec:
    """Horizontal unit vector. Yaw is measured in the XZ plane from +x toward +z."""
    return (math.cos(yaw_rad), 0.0, math.sin(yaw_rad))


def rotate(v: Vec, axis: Vec, ang: float) -> Vec:
    """Rodrigues rotation of v about unit axis by ang (rad)."""
    c, s = math.cos(ang), math.sin(ang)
    return add(add(mul(v, c), mul(cross(axis, v), s)), mul(axis, dot(axis, v) * (1 - c)))


def reflect(d: Vec, n: Vec) -> Vec:
    return sub(d, mul(n, 2 * dot(d, n)))


def perp_basis(a: Vec) -> tuple[Vec, Vec]:
    """Transverse basis for a near-horizontal axis a: e1 = unit(Y x a), horizontal, pointing toward
    yaw(a) - 90 deg; e2 = a x e1, which is 'up'."""
    e1 = unit(cross(Y, a))
    e2 = cross(a, e1)
    return e1, e2
