from enum import Enum


class Discount(str, Enum):
    early65 = "早鳥65折"
    early80 = "早鳥8折"
    early90 = "早鳥9折"
    student50 = "學生5折"
    student75 = "學生75折"
    student88 = "學生88折"
