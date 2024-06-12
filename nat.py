import requests
import os
import sys

def getNATS():
    try:
        return requests.get("https://api.flightplandatabase.com/nav/NATS").json()
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

def printInfo(usedNats, validUntil):
    print("Added NATs:")
    for nat in usedNats:
        print("\tNAT "+nat)
    print(validUntil)

def appendToFile(updatedFile, auroraPath):
    with open(os.path.join(auroraPath + "highairway.awh"),'w') as file:
        file.write(updatedFile)

def addNATS(nats):
    updatedFile = ""
    usedNats = []
    usedFixes = []
    for nat in nats:
        ident = nat['ident']
        if ident in usedNats:
            continue
        usedNats.append(nat['ident'])
        fixes = nat['route']['nodes']
        labeled = False
        secondCol = "NAT"+ident
        for fix in fixes:
            fixId = fix['ident']
            if not labeled:
                updatedFile += "L;"+ident+";"+fixId+";"+fixId+";\n"
                labeled = True
            if fix['type'] == "FIX":
                updatedFile += "T;"+secondCol+";"+fixId+";"+fixId+";\n"
                usedFixes.append(fixId)
            else:
                newFix = ""
                coord = ""
                coordArr = fixId.split("/")
                if len(coordArr[0]) == 2:
                    coord = coordArr[0] + coordArr[1] + "N"
                    newFix = coord+";N0"+str(coordArr[0])+".00.00.000;W0"+str(coordArr[1])+".00.00.000;"
                else:
                    coord = "H"+coordArr[0][0:2] + coordArr[1]
                    newFix = coord+";N0"+str(coordArr[0][0:2])+"."+str(coordArr[0][2:4])+".00.000;W0"+str(coordArr[1])+".00.00.000;"
                usedFixes.append(newFix)
                updatedFile += "T;"+secondCol+";"+coord+";"+coord+";\n"
    
    validUntil = nats[0]['validTo'].split("T")
    hour = validUntil[1].split(":")
    validUntil = "Valid until: "+validUntil[0]+"@"+hour[0]+":"+hour[1]+"Z"
    printInfo(usedNats, validUntil)
    return usedFixes, updatedFile

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
    nats = getNATS()
    usedFixes, updatedFile = addNATS(nats)
    appendToFile(updatedFile, auroraPath)
    verifyMissingFixes(auroraFixes, usedFixes, auroraPath)
    input("Press ENTER to exit")

if __name__ == "__main__":
    main()