#!/usr/bin/env python3

from os.path import expanduser
from random import randrange
from random import choice


class Challenge:
    def __init__(self, new_text, single=True):
        self.raw_text = new_text
        self.single = single
        self.pickcount = 0

    @property
    def multi(self):
        return not self.single

    @classmethod
    def get_last_passed_owner(cls, passed_challenges):
        return passed_challenges - 2

    @classmethod
    def get_random_passed_owner(cls, passed_challenges):
        return randrange(passed_challenges)

    def _compile(self, passed_challenges):
        res = self.raw_text
        if not self.is_vanilla:
            res = res.replace("%RANDOM", str(Challenge.get_random_passed_owner(passed_challenges)))
            res = res.replace("%LAST", str(Challenge.get_last_passed_owner(passed_challenges)))
        return res

    @classmethod
    def single_from_line(cls, line):
        return Challenge(line)

    @classmethod
    def multi_from_line(cls, line):
        return Challenge(line, False)

    @property
    def is_vanilla(self):
        burned = ["%LAST", "%RANDOM"]
        return not any(b in self.raw_text for b in burned)

    def valid(self, needs_vanilla=False):
        if needs_vanilla and not self.is_vanilla:
            return False
        if self.multi:
            return True
        return 0 == self.pickcount

    def pick(self, passed_challenges):
        self.pickcount += 1
        return self._compile(passed_challenges)


class ChallengeStack:
    def __init__(self, startnumber=0):
        self.challenges = []
        self.passed = startnumber

    def pick(self):
        need_vanilla = 0 == self.passed
        found_valid = False
        while not found_valid:
            c = choice(self.challenges)
            if c.valid(need_vanilla):
                found_valid = True
        self.passed+=1
        return c.pick(self.passed)

    def append(self, challenge):
        self.challenges.append(challenge)

    @property
    def s_c(self):
        count = 0
        for c in self.challenges:
            if c.single:
                count += 1
        return count

    @property
    def m_c(self):
        count = 0
        for c in self.challenges:
            if c.multi:
                count += 1
        return count

    def __str__(self):
        return "CS<{}s, {}m".format(self.s_c, self.m_c)

    @classmethod
    def from_folder(cls, folderpath, startnumber=0):
        stack = ChallengeStack(startnumber)
        with open(folderpath + "/single.txt", "r") as sc:
            single_raw = sc.readlines()
            for s in single_raw:
                stack.append(Challenge(s))
        with open(folderpath + "/multi.txt", "r") as mc:
            multi_raw = mc.readlines()
            for m in multi_raw:
                stack.append(Challenge(m, False))
        return stack


if "__main__" == __name__:
    home = expanduser("~")
    cf = home+"/challenges"
    stack = ChallengeStack.from_folder(cf)
    print(stack)

    for i in range(20):
        print("{}: {}".format(stack.passed, stack.pick()))