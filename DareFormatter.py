#!/usr/bin/env python3
import datetime


class Dare:
    def __init__(self, new_text):
        self.raw_text = new_text

    @classmethod
    def british_date(cls):
        return datetime.date.today()

    @classmethod
    def from_file(cls, path):
        with open(path, 'r') as darefile:
            lines = darefile.readlines()
            return Dare("\n".join(lines))

    def compile(self, dare_content, num):
        res = self.raw_text
        res = res.replace("$DARE", str(dare_content))
        res = res.replace("$DATE", str(Dare.british_date()))
        res = res.replace("$NUM", str(num))
        return res
