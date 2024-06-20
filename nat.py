import requests
import os
import sys
import time

def findTimes(response: list):
    months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]
    month = months[time.gmtime().tm_mon-1]
    if time.gmtime().tm_hour < 10:
        hour = "0"+str(time.gmtime().tm_hour)
    else:
        hour = str(time.gmtime().tm_hour)
    if time.gmtime().tm_min < 10:
        mins = "0"+str(time.gmtime().tm_min)
    else:
        mins = str(time.gmtime().tm_min)
    hour = int(hour+mins)
    validNatsPos = []
    toBeUpdated = 0
    i = 0
    for arr in response:
        if month in arr:
            validFrom = int(arr[1].split("/")[1][0:4])
            validTo = int(arr[4].split("<")[0].split("/")[1][0:4])
            if hour > validFrom and hour < validTo:
                toBeUpdated = validTo
                validNatsPos.append(i+2) #Adds the index where the nexts NATs info are located
        i += 1
    return validNatsPos, toBeUpdated

def getNATS():
    try:
        response = requests.get("https://www.notams.faa.gov/common/nat.html").content.decode("UTF-8").split("\n")
        formattedResponse = []
        NATS = []
        for val in response:
            formattedResponse.append(val.split(" "))
        indexes, validUntil = findTimes(formattedResponse)
        if len(indexes) == 0:
            print("No NATs are active at the moment.")
            input("Press ENTER to exit")
            raise SystemExit()
        for index in indexes:
            counter = 0
            while len(formattedResponse[index+counter][0]) == 1:
                NATS.append(formattedResponse[index+counter])
                counter += 5 #Dismiss East and West Levels, NARs and EURs
        return NATS, validUntil
    except Exception as e:
        print("Script couldn't download necessary data. Please check your internet connection!")
        input("Press ENTER to exit")
        raise SystemExit()

def getAuroraPath():
    if getattr(sys, 'frozen', False):
        absolute_path = os.path.dirname(sys.executable)
    elif __file__:
        absolute_path = os.path.dirname(__file__)
    auroraPathFile = absolute_path+"/path.txt"
    if os.path.isfile(auroraPathFile):
        file = open(auroraPathFile,"r")
        auroraPath = file.read()
    else:
        auroraPath = input('Paste "Aurora" folder path: ').rstrip("\\")
        os.system('cls')
        auroraPath = auroraPath+"\\SectorFiles\\Include\\CA\\czqx\\"
        file = open(auroraPathFile,"w")
        file.write(auroraPath)
        file.close()
        print("Created file with Aurora path in this directory: "+auroraPathFile+"\n")

    return auroraPath

def getAuroraFixes(auroraPath):
    auroraFixes = []
    with open(os.path.join(auroraPath + "fixes.fix"),'r') as file:
        data = file.read().split("\n")
    for fixInfo in data:
        if "//" not in fixInfo and fixInfo != "":
            fixInfo = fixInfo.split(";")
            auroraFixes.append(fixInfo[0])
    
    return auroraFixes

def printInfo(usedNATS, validUntil):
    print("Added NATs:")
    for nat in usedNATS:
        print("\tNAT "+nat)
    if len(str(validUntil)) == 3:
        print("To be updated after: 0"+str(validUntil)[0]+":"+str(validUntil)[1:3]+"Z")
    else:
        print("To be updated after: "+str(validUntil)[0:2]+":"+str(validUntil)[2:4]+"Z")

def appendToFile(updatedFile, auroraPath):
    with open(os.path.join(auroraPath + "highairway.awh"),'w') as file:
        file.write(updatedFile)

def addNATS(nats):
    updatedFile = ""
    usedNATS = []
    usedFixes = []
    for nat in nats:
        ident = nat[0]
        usedNATS.append(ident)
        fixes = nat[1:]
        labeled = False
        secondCol = "NAT"+ident
        for fix in fixes:
            if not labeled:
                updatedFile += "L;"+ident+";"+fix+";"+fix+";\n"
                labeled = True
            if len(fix.split("/")) == 1:
                updatedFile += "T;"+secondCol+";"+fix+";"+fix+";\n"
                usedFixes.append(fix)
            else:
                newFix = ""
                coord = ""
                coordArr = fix.split("/")
                if len(coordArr[0]) == 2:
                    coord = coordArr[0] + coordArr[1] + "N"
                    newFix = coord+";N0"+str(coordArr[0])+".00.00.000;W0"+str(coordArr[1])+".00.00.000;"
                else:
                    coord = "H"+coordArr[0][0:2] + coordArr[1]
                    newFix = coord+";N0"+str(coordArr[0][0:2])+"."+str(coordArr[0][2:4])+".00.000;W0"+str(coordArr[1])+".00.00.000;"
                usedFixes.append(newFix)
                updatedFile += "T;"+secondCol+";"+coord+";"+coord+";\n"
    return usedFixes, updatedFile, usedNATS

def verifyMissingFixes(auroraFixes, usedFixes, auroraPath):
    manualFixes = []
    added = False
    with open(os.path.join(auroraPath + "fixes.fix"),'a') as file:
        for fix in usedFixes:
            splittedFix = str(fix).split(";")
            if splittedFix[0] not in auroraFixes:
                if not added:
                    print("\nFixes that were added:")
                    added = True
                if len(splittedFix)>1:
                    print("\t"+splittedFix[0])
                    file.write(fix+"\n")
                else:
                    manualFixes.append(splittedFix[0])
        if not added:
            print("\nNo additional fixes were added.")
        else:
            print("Fixes that have to be added manualy:")
            for fix in manualFixes:
                print("\t"+fix)
def main():
    auroraPath = getAuroraPath()
    auroraFixes = getAuroraFixes(auroraPath)
    nats, validUntil = getNATS()
    usedFixes, updatedFile, usedNATS = addNATS(nats)
    printInfo(usedNATS, validUntil)
    appendToFile(updatedFile, auroraPath)
    verifyMissingFixes(auroraFixes, usedFixes, auroraPath)
    input("Press ENTER to exit")

if __name__ == "__main__":
    main()