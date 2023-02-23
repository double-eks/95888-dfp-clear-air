
import re


class Body:

    def __init__(self, lines: list[str], name: str, ul: bool = False):
        self.name = name
        self.body = lines
        self.parent = None
        self.start, self.end = -1, -1
        if (ul):
            self.items = self.formatBody()

    def genChild(self, childName: str, start: int, end: int, ul: bool):
        name = self.name + '-' + childName
        child = Body(self.body[start:end], name, ul)
        child.parent = self
        child.start, child.end = start, end
        return child

    def extractByTag(self, tag: str, name: str,
                     startFrom: int = -1, targetOcc: int = 1,
                     flexible: bool = False, ul: bool = False):
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
                if (pair == targetOcc) and (patternIndex == 1):
                    break
        start, end = matchRows[-2], matchRows[-1] + 1
        return self.genChild(name, start, end, ul)

    def formatBody(self):
        content = []
        for line in self.body:
            if ('<' not in line) and ('>' not in line):
                content.append(line.strip())
        return content

    def output(self):
        content = self.formatBody()
        return '\n'.join(content)
