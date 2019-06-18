#!/usr/bin/env python
import sys
import requests
import json
import pyttanko as osu
import io
from datetime import datetime

COEF1 = 1.15
COEF2 = 0.006

MODS_NOMOD = 0
MODS_NF = 1<<0
MODS_EZ = 1<<1
MODS_TD = MODS_TOUCH_DEVICE = 1<<2
MODS_HD = 1<<3
MODS_HR = 1<<4
MODS_DT = 1<<6
MODS_HT = 1<<8
MODS_NC = 1<<9
MODS_FL = 1<<10
MODS_SO = 1<<12


class config:
    def __init__(self):
        with open("config.json", "r") as file:
            self.configDict = json.loads(file.read())


class beatmapsDataParser:
    def __init__(self):
        self.bmapDict = {}
        with open("bmaps.json", "r") as file:
            self.bmapDict = json.loads(file.read())

    def bmapData(self, mapId, modsInt):
        if self.bmapDict.get("{}+{}".format(mapId, modsInt)) == None:
            map = requests.get("https://osu.ppy.sh/osu/{}".format(mapId))
            map = map.content
            wrapper = io.BufferedReader(io.BytesIO(map))
            wrapper = io.TextIOWrapper(wrapper, encoding="utf-8")
            parser = osu.parser()
            bmap = parser.map(wrapper)
            stars = osu.diff_calc().calc(bmap, modsInt)
            self.bmapDict["{}+{}".format(mapId, modsInt)] = {
            "ar":bmap.ar, 
            "od": bmap.od,
            "maxcombo": bmap.max_combo(),
            "nobjects": len(bmap.hitobjects),
            "nsliders": bmap.nsliders,
            "ncircles": bmap.ncircles,
            "aim": stars.aim, 
            "speed": stars.speed
            }
            with open("bmaps.json", "w") as file:
                file.write(json.dumps(self.bmapDict, indent=4))
            return self.bmapDict["{}+{}".format(mapId, modsInt)]
        else:
            return self.bmapDict["{}+{}".format(mapId, modsInt)]


def modsIntFromString(modsStr):
    modsInt = 0
    if "nomod" in modsStr: modsInt = 0
    if "NF" in modsStr: modsInt += (1<<0)
    if "EZ" in modsStr: modsInt += (1<<1)
    if "TD" in modsStr: modsInt += (1<<2)
    if "HD" in modsStr: modsInt += (1<<3)
    if "HR" in modsStr: modsInt += (1<<4)
    if "DT" in modsStr: modsInt += (1<<6)
    if "HT" in modsStr: modsInt += (1<<8)
    if "NC" in modsStr: modsInt += ((1<<9)+(1<<6))
    if "FL" in modsStr: modsInt += (1<<10)
    if "SO" in modsStr: modsInt += (1<<12)
    return modsInt


def modsStrFromInt(modsInt):
    if modsInt == 0:
        return "nomod"

    modsStr = ""
    if modsInt & MODS_HD != 0: modsStr += "HD"
    if modsInt & MODS_HT != 0: modsStr += "HT"
    if modsInt & MODS_HR != 0: modsStr += "HR"
    if modsInt & MODS_EZ != 0: modsStr += "EZ"
    if modsInt & MODS_TOUCH_DEVICE != 0: modsStr += "TD"
    if modsInt & MODS_NC != 0: modsStr += "NC"
    elif modsInt & MODS_DT != 0: modsStr += "DT"
    if modsInt & MODS_FL != 0: modsStr += "FL"
    if modsInt & MODS_SO != 0: modsStr += "SO"
    if modsInt & MODS_NF != 0: modsStr += "NF"
    return modsStr


def accCalc(n300, n100, n50, nM):
    if (nM + n50 + n100) == 0:
        return 100
    else: 
        return float("%.2f" % (((n50 * 50.0 + n100 * 100.0 + n300 * 300.0) / ((nM + n50 + n100 + n300) * 300.0)) * 100))


def ppCalc(mapId, modsInt, n300, n100, n50):
    bmap = beatmapsDataParser().bmapData(mapId, modsInt)
    pp, _, _, _, _ = osu.ppv2(
    aim_stars=bmap["aim"], speed_stars=bmap["speed"], max_combo=bmap["maxcombo"],
    nsliders=bmap["nsliders"], ncircles=bmap["ncircles"], nobjects=bmap["nobjects"], base_ar=bmap["ar"],
    base_od=bmap["od"], mods=modsInt, n300=n300, n100=n100, n50=n50)
    return float("%.2f" % pp)


def thresholdQualifier(playerPP, maxMapPP):
    q = playerPP / maxMapPP
    q = float("%.2f" % q)
    if q >= 0.80:
        return True
    else:
        return False


def thresholdPassAmoutQualifier(mapScoresList, mapId, modsInt):
    tpAmout = 0
    for a in range(len(mapScoresList)):
        tpQualify = thresholdQualifier(float(mapScoresList[a]["pp"]), ppCalc(mapId, modsInt, 
            int(mapScoresList[a]["count300"]), int(mapScoresList[a]["count100"]), int(mapScoresList[a]["count50"])))
        if tpQualify == True:
            tpAmout += 1
    return tpAmout


def ppReCalc(pp, tpAmout):
    if tpAmout > 50:
        q = pp * (COEF1 - (COEF2 * 50))
        q = float("%.2f" % q)
        return q
    else:
        q = pp * (COEF1 - (COEF2 * tpAmout))
        q = float("%.2f" % q)
        return q


class mapDataReceiver:
    def __init__(self, apiKey, mapId, modsInt):
        self.mapId = mapId
        self.modsInt = modsInt
        self.modsStr = modsStrFromInt(modsInt)
        response = requests.get("https://osu.ppy.sh/api/get_scores", params={"k": apiKey, "b": mapId, "mods": modsInt})
        self.mapScoresList = json.loads(response.text)
        response = requests.get("https://osu.ppy.sh/api/get_beatmaps", params={"k": apiKey, "b": mapId, "mods": modsInt})
        self.mapDataDict = json.loads(response.text)[0]
        self.title = "{} - {} [{}]".format(self.mapDataDict["artist"], self.mapDataDict["title"], self.mapDataDict["version"])
        self.tpAmout = thresholdPassAmoutQualifier(self.mapScoresList, self.mapId, self.modsInt)

    def updateScores(self):
        updatedMapScoresList = []
        place = 0
        for a in range(len(self.mapScoresList)):
            place += 1
            acc = accCalc(
                int(self.mapScoresList[a]["count300"]),
                int(self.mapScoresList[a]["count100"]),
                int(self.mapScoresList[a]["count50"]),
                int(self.mapScoresList[a]["countmiss"]))
            maxPP = ppCalc(
                self.mapId, 
                self.modsInt, 
                int(self.mapScoresList[a]["count300"]), 
                int(self.mapScoresList[a]["count100"]), 
                int(self.mapScoresList[a]["count50"]))

            thresholdPass = thresholdQualifier(float(self.mapScoresList[a]["pp"]), maxPP)
            if thresholdPass == True:
                recalcPP = ppReCalc(float(self.mapScoresList[a]["pp"]), self.tpAmout)
                ppDiff = recalcPP - float(self.mapScoresList[a]["pp"])
                ppDiff = "%.2f" % ppDiff
            else: 
                recalcPP = 0
                ppDiff = 0

            updatedMapScoresDict = {
            "place": place,
            "username": self.mapScoresList[a]["username"],
            "accuracy": acc,
            "maxcombo": self.mapScoresList[a]["maxcombo"],
            "pp": "%.2f" % float(self.mapScoresList[a]["pp"]),
            "thresholdPass": thresholdPass,
            "recalcPP": recalcPP,
            "ppDiff": ppDiff,
            "mods": self.modsStr
            }

            updatedMapScoresList.append(updatedMapScoresDict)
        self.updatedMapScoresList = updatedMapScoresList


class userDataReceiver:
    def __init__(self, apiKey, userId):
        self.userId = userId
        response = requests.get("https://osu.ppy.sh/api/get_user", params={"k": apiKey, "u": self.userId, "m": 0})
        self.userDataDict = json.loads(response.text)[0]

    def getUserScoresData(self):
        response = requests.get("https://osu.ppy.sh/api/get_user_best", params={"k": apiKey, "u": self.userId, "m": 0, "limit": 100})
        self.userScoresList = json.loads(response.text)
        weightedUserPP = 0
        for a in range(len(self.userScoresList)):
            weightedUserPP += (float(self.userScoresList[a]["pp"]) * (0.95 ** a))
        self.weightedUserPP = float("%.2f" % weightedUserPP)
        self.bonusPP = float(self.userDataDict["pp_raw"]) - self.weightedUserPP

    def updateUserScores(self):
        self.updatedPP = 0
        self.updatedUserScores = []
        for a in range(len(self.userScoresList)):
            mapData = mapDataReceiver(apiKey, int(self.userScoresList[a]["beatmap_id"]), int(self.userScoresList[a]["enabled_mods"]))
            thresholdPass = thresholdQualifier(
                float(self.userScoresList[a]["pp"]), ppCalc(
                int(self.userScoresList[a]["beatmap_id"]),
                int(self.userScoresList[a]["enabled_mods"]),
                int(self.userScoresList[a]["count300"]),
                int(self.userScoresList[a]["count100"]),
                int(self.userScoresList[a]["count50"])))
            if thresholdPass == True:
                recalcPP = ppReCalc(float(self.userScoresList[a]["pp"]), mapData.tpAmout)
                ppDiff = (recalcPP - float(self.userScoresList[a]["pp"]))
            else:
                recalcPP = 0
                ppDiff = 0
            self.updatedPP += (recalcPP * (0.95 ** a))

            self.updatedUserScores.append({
            "beatmap_id": self.userScoresList[a]["beatmap_id"],
            "mods": modsStrFromInt(int(self.userScoresList[a]["enabled_mods"])),
            "accuracy": accCalc(
                int(self.userScoresList[a]["count300"]),
                int(self.userScoresList[a]["count100"]),
                int(self.userScoresList[a]["count50"]),
                int(self.userScoresList[a]["countmiss"])),
            "pp": self.userScoresList[a]["pp"],
            "thresholdPass": thresholdPass,
            "recalcPP": recalcPP,
            "ppDiff": float("%.2f" % ppDiff)})
        self.updatedPP += self.bonusPP
        self.updatedPP = float("%.2f" % self.updatedPP)
        self.overallPPDiff = self.updatedPP - float(self.userDataDict["pp_raw"])
        self.overallPPDiff = float("%.2f" % self.overallPPDiff)


if __name__ == "__main__":
    try:
        apiKey = config().configDict["apiKey"]
        
        if sys.argv[1] == "-u":
            playerId = sys.argv[2]
            userData = userDataReceiver(apiKey, playerId)
            userData.getUserScoresData()
            userData.updateUserScores()

            file = open("{}.txt".format(userData.userDataDict["username"]), "a+")

            userInfo = "| {} | live pp: {} | recalcPP: {} | pp difference: {}".format(
                userData.userDataDict["username"],
                userData.userDataDict["pp_raw"],
                userData.updatedPP,
                userData.overallPPDiff)

            file.write(userInfo + "\n")
            print(userInfo)

            for a in range(len(userData.updatedUserScores)):
                userScore = "| {} | +{} | {}% | {}pp | {} | {}pp | {}pp |".format(
                    mapDataReceiver(apiKey, userData.updatedUserScores[a]["beatmap_id"], modsIntFromString(userData.updatedUserScores[a]["mods"])).title,
                    userData.updatedUserScores[a]["mods"],
                    userData.updatedUserScores[a]["accuracy"],
                    userData.updatedUserScores[a]["pp"],
                    userData.updatedUserScores[a]["thresholdPass"],
                    userData.updatedUserScores[a]["recalcPP"],
                    userData.updatedUserScores[a]["ppDiff"])

                file.write(userScore + "\n")
                print(userScore)
            file.close()

        elif sys.argv[1] == "-b":
            mapId = int(sys.argv[2])
            mods = modsIntFromString(sys.argv[3])

            mapData = mapDataReceiver(apiKey, mapId, mods)
            mapData.updateScores()

            file = open("{}+{}.txt".format(mapId, modsStrFromInt(mods)), "a+")

            mapInfo = "| {} | +{} | scores passed threshold: {} |".format(mapData.title, sys.argv[3], mapData.tpAmout)

            file.write(mapInfo + "\n")
            print(mapInfo)

            for a in range(len(mapData.updatedMapScoresList)):
                mapScore = "| #{} | {} | {}% | {}x | {}pp | {} | {}pp | pp difference: {}pp | +{} |".format(
                    mapData.updatedMapScoresList[a]["place"],
                    mapData.updatedMapScoresList[a]["username"],
                    mapData.updatedMapScoresList[a]["accuracy"],
                    mapData.updatedMapScoresList[a]["maxcombo"],
                    mapData.updatedMapScoresList[a]["pp"],
                    mapData.updatedMapScoresList[a]["thresholdPass"],
                    mapData.updatedMapScoresList[a]["recalcPP"],
                    mapData.updatedMapScoresList[a]["ppDiff"],
                    mapData.updatedMapScoresList[a]["mods"])

                file.write(mapScore + "\n")
                print(mapScore)
            file.close()

    except IndexError:
        print("Incorrect arguments.")
