
import re
from logging import Logger


class Body:

    def __init__(self, lines: list[str], name: str):
        self.name = name
        self.body = lines
        self.text = self.formatBody()
        self.parent = None
        self.start, self.end = -1, -1
        self.ul = False

    def genChild(self, childName: str, start: int, end: int):
        name = self.name + '-' + childName
        child = Body(self.body[start:end], name)
        child.parent = self
        child.start, child.end = start, end + 1
        return child

    def extractLines(self, name: str, tag: str = '', items: list = [],
                     startFrom: int = -1, targetOcc: int = 1,
                     flexible: bool = False):
        lines = self.body if (startFrom == -1) else self.body[startFrom:]
        char = '.*' if (flexible) else ''
        patterns = [f'<{tag}{char}>', f'</{tag}>']
        matchRows = []
        for i in range(len(lines)):
            pair = len(matchRows) // 2 + 1
            patternIndex = len(matchRows) % 2
            pattern = patterns[patternIndex]
            line = lines[i]
            if re.search(pattern, line) != None:
                matchRows.append(i)
                if (targetOcc != -1) and (pair == targetOcc) and (patternIndex == 1):
                    break
        matches = [self.genChild(name, matchRows[i], matchRows[i + 1])
                   for i in range(0, len(matchRows), 2)]
        return matches

    def formatBody(self):
        content = [line.strip() for line in self.body
                   if ('<' not in line) and ('>' not in line)]
        return content

    def outputPara(self, logger: Logger, prefix: str = '', suffix: str = ''):
        for i in range(len(self.text)):
            s = self.text[i]
            logger.info(prefix + s + suffix)

    def outputBullets(self, logger: Logger):
        for i in range(len(self.text)):
            line = f'[{i}] {self.text[i]}'
            logger.info(line)

    def check(self, logger: Logger):
        for i in range(len(self.body)):
            s = self.body[i].strip()
            logger.debug(s)
        logger.info('-' * 20)
