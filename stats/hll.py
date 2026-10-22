"""HyperLogLog：估算"有多少个不同的设备"，只存寄存器，不存设备编号。

按天汇总时每天存一份，多天合并（逐个寄存器取最大值）就能估算一段时间内的去重设备数，
原始设备编号删掉以后也能算。p=10 时误差约 3%，设备少（几百以内）时基本准确。
"""
import hashlib
import math


class HLL:
    def __init__(self, p=10, data=None):
        self.p = p
        self.m = 1 << p
        self.reg = bytearray(data) if data else bytearray(self.m)
        if len(self.reg) != self.m:
            raise ValueError("寄存器长度不对")

    def add(self, item: str):
        x = int.from_bytes(hashlib.sha1(item.encode()).digest()[:8], "big")
        idx = x >> (64 - self.p)
        w = (x << self.p) & ((1 << 64) - 1)
        rho = 1
        while rho <= 64 - self.p and not (w & (1 << 63)):
            rho += 1
            w = (w << 1) & ((1 << 64) - 1)
        if rho > self.reg[idx]:
            self.reg[idx] = rho

    def merge(self, other):
        if other is None:
            return self
        if isinstance(other, (bytes, bytearray, memoryview)):
            other = HLL(self.p, bytes(other))
        for i in range(self.m):
            if other.reg[i] > self.reg[i]:
                self.reg[i] = other.reg[i]
        return self

    def count(self) -> int:
        m = self.m
        alpha = {16: 0.673, 32: 0.697, 64: 0.709}.get(m, 0.7213 / (1 + 1.079 / m))
        z = sum(2.0 ** -r for r in self.reg)
        e = alpha * m * m / z
        zeros = self.reg.count(0)
        if e <= 2.5 * m and zeros:
            e = m * math.log(m / zeros)
        return int(round(e))

    def dump(self) -> bytes:
        return bytes(self.reg)


def merged_count(blobs, p=10) -> int:
    h = HLL(p)
    for b in blobs:
        if b:
            h.merge(b)
    return h.count()
