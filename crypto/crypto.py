import os
import base64
import time

from abc import ABC, abstractmethod

class Crypto(ABC):
    def __init__(self, key):
        self.key = key

    @abstractmethod
    def encrypt(self, data):
        return "Belum diimplementasikan"

    @abstractmethod
    def decrypt(self, data):
        return "Belum diimplementasikan"