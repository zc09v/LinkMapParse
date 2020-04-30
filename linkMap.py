# -*- coding: UTF-8 -*-
import sys
import getopt
from  enum import Enum
import re
import os
import prettytable as pt

class ParseStatus(Enum):
    NONE = 0
    OBJECTS = 1
    SECTIONS = 2
    SYMBOLS = 3
    FINISH = 4

class ModuleInfo:
    @property
    def size(self):
        # unit KB
        return self._size / 1024.0
    def __init__(self, name, size):
        self.name = name
        self._size = size

def parseLinkMap():
    print("parse start ....")
    filePath = ""
    for file in os.listdir("./"):
        if file.find("LinkMap") != -1:
            filePath = "./" + file
    if filePath is "":
        print("can't find LinkMap file")
        return
    try:
        linkMapFile = open(filePath)
    except IOError, error:
        print "fileOpen fail error: {}".format(error)
    line = linkMapFile.readline()
    state = ParseStatus.NONE
    # key: moduleName value: fileNums
    moduleFiles = {}
    # key: fileNum value: size
    filesSize = {}
    # __DATA __bss address range
    bssAddressRange = ()
    while 1:
        line = linkMapFile.readline()
        if line.startswith("# Object files:"):
            state = ParseStatus.OBJECTS
        elif line.startswith("# Sections:"):
            state = ParseStatus.SECTIONS
        elif line.startswith("# Symbols:"):
            state = ParseStatus.SYMBOLS
        elif line.startswith("# Dead Stripped Symbols:"):
            state = ParseStatus.FINISH

        if state == ParseStatus.OBJECTS:
            handleObjects(line, moduleFiles)
        elif state == ParseStatus.SECTIONS:
            getRange = handleSections(line)
            if getRange is not None:
                bssAddressRange = getRange
        elif state == ParseStatus.SYMBOLS:
            handleSymbols(line, filesSize, bssAddressRange)
        elif state == ParseStatus.FINISH:
            moduleInfos = handleFinish(moduleFiles, filesSize)
            generateTableAndOutput(moduleInfos)
            break
        else:
            pass

def handleObjects(line, moduleFiles):
    matched = re.match(r"\[\s*(\d+)\].*/(.*)\(.*\)", line, 0)
    if matched:
        handleObjectsMatched(moduleFiles, matched)
    else:
        matched = re.match(r"\[\s*(\d+)\].*/(.*)", line, 0)
        if matched:
            handleObjectsMatched(moduleFiles, matched)

def handleObjectsMatched(moduleFiles, matched):
    fileNum = matched.group(1)
    module = matched.group(2)
    if module in moduleFiles:
        files = list(moduleFiles[module])
        files.append(fileNum)
        moduleFiles[module] = files
    else:
        moduleFiles[module] = [fileNum]

def handleSections(line):
    if line.find("__bss") != -1:
        pattern = re.compile(r"(0x[0-9a-fA-F]+)\s(0x[0-9a-fA-F]+).*")
        matched = re.match(pattern, line, 0)
        if matched:
            start = int(matched.group(1), 16)
            size = int(matched.group(2), 16)
            return (start, start + size - 1)

def handleSymbols(line, filesSize, bssAddressRange):
    matched = re.match(r"(0x[0-9a-fA-F]+)\s(0x[0-9a-fA-F]+).*\[\s*(\d+)\].*", line, 0)
    if matched:
        address = int(matched.group(1), 16)
        if address >= bssAddressRange[0] and address <= bssAddressRange[1]:
            pass
        else:
            size = int(matched.group(2), 16)
            fileNum = matched.group(3)
            if fileNum in filesSize:
                existSize = int(filesSize[fileNum])
                filesSize[fileNum] = existSize + size
            else:
                filesSize[fileNum] = size

def handleFinish(moduleFiles, filesSize):
    moduleInfos = []
    for module in moduleFiles:
        fileNums = list(moduleFiles[module])
        totalSize = 0
        for fileNum in fileNums:
            if fileNum in filesSize:
                size = int(filesSize[fileNum])
                totalSize = totalSize + size
        moduleInfo = ModuleInfo(module, totalSize)
        moduleInfos.append(moduleInfo)
    return sorted(moduleInfos, key= lambda x:x.size, reverse=True)

def generateTableAndOutput(moduleInfos):
    tb = pt.PrettyTable(["Module", "size"])
    for module in moduleInfos:
        tb.add_row([module.name, "%.2f KB"%(module.size)])
    outputFilePath = "./parseResult.txt"
    file = open(outputFilePath, "w+")
    file.write(str(tb))
    print("parse finish")

if __name__ == "__main__":
    parseLinkMap()
