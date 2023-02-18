#!/usr/bin/env python3

import os
from os.path import expanduser
import random
import logging

_logger = logging.getLogger(__name__)


class Challenge:
    def __init__(self, new_text, single=True):
        self.raw_text: str = new_text
        self.single: bool = single
        self.pick_count: int = 0

    @property
    def multi(self):
        return not self.single

    @classmethod
    def get_last_passed_owner(cls, passed_challenges):
        return passed_challenges - 2

    @classmethod
    def get_random_passed_owner(cls, passed_challenges):
        return random.randrange(passed_challenges)

    @property
    def num_randoms_required(self) -> int:
        return self.raw_text.count("$RANDOM")

    def _compile(self, passed_challenges: int):
        res = self.raw_text
        if not self.is_vanilla:
            randoms = random.sample(range(passed_challenges), self.num_randoms_required)
            _logger.debug(f"Not a vanilla challenge, picked {self.num_randoms_required} randoms: {randoms}")
            for random_guest_number in randoms:
                res = res.replace("$RANDOM", str(random_guest_number), 1)

            if "$LAST" in res:
                res = res.replace("$LAST", str(Challenge.get_last_passed_owner(passed_challenges)))
        return res

    @classmethod
    def single_from_line(cls, line):
        return Challenge(line)

    @classmethod
    def multi_from_line(cls, line):
        return Challenge(line, False)

    @property
    def is_vanilla(self):
        burned = ["$LAST", "$RANDOM"]
        return not any(b in self.raw_text for b in burned)

    def valid(self, num_passed_challenges: int, needs_vanilla: bool =False):
        if self.multi:
            return True
        if self.num_randoms_required > num_passed_challenges:
            _logger.debug(f"Challenge needs {self.num_randoms_required} randoms but only {num_passed_challenges} have been printed, yet.")
            return False
        return 0 == self.pick_count

    def pick(self, passed_challenges):
        self.pick_count += 1
        return self._compile(passed_challenges)


class ChallengeStack:
    def __init__(self, start_number=0):
        self.challenges: list[Challenge] = []
        self.num_passed_challenges = start_number

    def pick(self):
        found_valid = False
        while not found_valid:
            c = random.choice(self.challenges)
            if c.valid(num_passed_challenges=self.num_passed_challenges):
                found_valid = True
        self.num_passed_challenges+=1
        return c.pick(self.num_passed_challenges)

    def append(self, challenge):
        self.challenges.append(challenge)

    @property
    def num_single_challenges(self):
        count = 0
        for c in self.challenges:
            if c.single:
                count += 1
        return count

    @property
    def num_multi_challenges(self):
        count = 0
        for c in self.challenges:
            if c.multi:
                count += 1
        return count

    @property
    def cur_count(self):
        return self.num_passed_challenges-1

    def __str__(self):
        return (
            f"<ChallengeStack | Single: {self.num_single_challenges}, "
            f"Multi: {self.num_multi_challenges}, "
            f"Passed challenges: {self.num_passed_challenges}>")

    @classmethod
    def from_folder(cls, folder_path, start_number=0):
        stack = ChallengeStack(start_number=start_number)
        with open(folder_path + "/single.txt", "r") as single_challenge_fh:
            for line in filter(None, single_challenge_fh.read().splitlines()):
                stack.append(Challenge(line))
        with open(folder_path + "/multi.txt", "r") as multi_challenge_fh:
            for line in filter(None, multi_challenge_fh.readlines()):
                stack.append(Challenge(line, False))
        return stack


if "__main__" == __name__:
    home = expanduser("~")
    challenges_path = home+"/challenges"
    start_number = int(os.environ.get("CHALLENGE_START_NUMBER", 0))
    stack = ChallengeStack.from_folder(folder_path=challenges_path, start_number=start_number)
    print(stack)

    for i in range(20):
        print("{}: {}".format(stack.num_passed_challenges, stack.pick()))