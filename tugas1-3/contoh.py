"""Modul contoh untuk Tugas 3."""
import os
import sys, json
from pathlib import Path
from collections import Counter as Hitung
from . import utils
import os.path as osp


def tambah(a, b):
    """Menjumlahkan dua angka."""
    return a + b


def sapa(nama, salam="Halo", *args, **kwargs):
    print(salam, nama)
    return f"{salam} {nama}"


def kosong():
    pass


class Toko:
    def __init__(self, nama):
        "Docstring kutip satu."
        self.nama = nama

    def cetak(self, *, tebal: bool = False):
        print(self.nama)
        print("tebal" if tebal else "biasa")

        def dalam(x):
            return x

        return dalam


print("selesai")
log.print("bukan print bawaan")
pesan = "print('ini string, bukan pemanggilan')"
# print("ini komentar")
