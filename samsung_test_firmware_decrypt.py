from genericpath import exists
import concurrent.futures
import time
import requests
from requests.exceptions import ProxyError, RequestException
import hashlib
from lxml import etree
import os
import random
from datetime import datetime
from datetime import timezone
from datetime import timedelta
import json
import telegram
import pymysql
from copy import deepcopy
from func_timeout import func_set_timeout
import func_timeout
from dotenv import load_dotenv
import string
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import threading
from rich.console import Console
from collections import OrderedDict

load_dotenv()
thread_local = threading.local()
isDebug = False
isFirst = True
oldMD5Dict = {}
console = Console()
current_latest_version = "16"  # Current latest Android version number


def getConnect():
    """
    Get database connection
    """
    prefix = os.getenv("PREFIX")
    if prefix != None:
        cert_path = f"{prefix}/etc/tls/cert.pem"
    else:
        cert_path = "/etc/ssl/certs/ca-certificates.crt"
    connection = pymysql.connect(
        host=os.getenv("HOST"),
        user=os.getenv("DBUSER"),
        passwd=os.getenv("PASSWORD"),
        db=os.getenv("DATABASE"),
        charset="utf8mb4",
        port=21777,
        autocommit=True,
        cursorclass=pymysql.cursors.DictCursor,
    )
    return connection


def printStr(msg):
    console.log(msg)


def getModelDictsFromDB():
    """Read models from database"""
    ModelDic = {}
    ModelsQuery = "SELECT * FROM models"
    connect = getConnect()
    cursor = connect.cursor()
    cursor.execute(ModelsQuery)
    models = cursor.fetchall()
    cursor.close()
    connect.close()
    for model in models:
        name = model["name"]
        modelCode = model["code"]
        countryCode = []
        for cc in model["cc"].split("|"):
            countryCode.append(cc)
        ModelDic[modelCode] = {"CC": countryCode, "name": name}
    return ModelDic


def getModelDicts():
    """Read models from file"""
    ModelDic = {}
    with open("models.txt", "r", encoding="utf-8") as models:
        for model in models:
            if model.startswith("#"):
                continue
            model = model.strip().split(",")
            name = model[0]
            modelCode = model[1]
            countryCode = []
            for cc in model[2].split("|"):
                countryCode.append(cc)
            ModelDic[modelCode] = {"CC": countryCode, "name": name}
    return ModelDic


def getCountryName(cc):
    """
    Get region name by device code
    """
    cc2Country = {
        "CHC": "China",
        "CHN": "China",
        "TGY": "Hong Kong",
        "KOO": "Korea",
        "EUX": "Europe",
        "INS": "India",
        "XAA": "USA",
        "ATT": "USA",
        "TPA": "Panama",
    }
    if cc in cc2Country.keys():
        return cc2Country[cc]
    else:
        return "Unknown Region"


def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
    return thread_local.session


def requestXML(url, max_retries=3, sleep_sec=1):
    """
    Request XML content
    """
    UA_list = [
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.0.0",
        "Mozilla/5.0 (Linux; Android 9; SAMSUNG SM-T825Y) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/15.0 Chrome/90.0.4430.210 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36",
        "Mozilla/5.0 (Linux; U; Android 8.1.0; zh-cn; vivo X20A Build/OPM1.171019.011) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/12.0 Mobile Safari/537.36 COVC/045730",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0_3 like Mac OS X) AppleWebKit/604.3.5 (KHTML, like Gecko) Version/11.0 MQQBrowser/11.8.3 Mobile/15B87 Safari/604.1 QBWebViewUA/2 QBWebViewType/1 WKType/1",
        "Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10.5; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15",
    ]
    headers = {"User-Agent": random.choice(UA_list), "Connection": "close"}
    for attempt in range(1, max_retries + 1):
        try:
            session = get_session()
            response = session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.content
        except ProxyError as e:
            printStr(f"ProxyError({attempt}/{max_retries}): {e}")
        except RequestException as e:
            printStr(f"RequestException({attempt}/{max_retries}): {e}")
        except Exception as e:
            printStr(f"Error occurred ({attempt}/{max_retries}): {e}")
        if attempt < max_retries:
            time.sleep(sleep_sec)
    return None


def readXML_worker(args):
    """XML read task for a single CC"""
    model, cc = args
    md5list = []
    url = f"https://fota-cloud-dn.ospserver.net/firmware/{cc}/{model}/version.test.xml"
    content = requestXML(url)
    if content is not None:
        xml = etree.fromstring(content)
        if len(xml.xpath("//value//text()")) == 0:
            printStr(f"<{model}> Region code <{cc}> input error!!!")
        else:
            for node in xml.xpath("//value//text()"):
                md5list.append(node)
    return cc, md5list


def readXML(model, modelDic):
    """
    Get MD5 values of official website version codes (multi-threaded version)
    """
    md5Dic = {}
    cc_list = modelDic[model]["CC"]
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = pool.map(readXML_worker, [(model, cc) for cc in cc_list])
        for cc, md5list in results:
            if md5list:
                md5Dic[cc] = md5list
    return md5Dic


def char_to_number(char):
    """
    Convert character to corresponding number
    """
    if char.isdigit():
        return int(char)
    elif char.isalpha() and char.isupper():
        return ord(char) - ord("A") + 10
    else:
        raise ValueError("Input must be a character between 0-9 or A-Z")


def get_letters_range(start: str, end: str) -> str:
    """Return string in given range (including end character)"""
    # Get all uppercase letters A-Z
    letters = "0123456789" + string.ascii_uppercase + string.ascii_lowercase
    start_index = letters.find(start)
    end_index = letters.find(end)
    if start_index == -1 or end_index == -1:
        raise ValueError(f"get_letters_range: '{start}' or '{end}' is not in valid character range")
    end_index += 1
    if letters[start_index:end_index] == "":
        raise Exception("String start and end error, please check")
    else:
        return letters[start_index:end_index].upper()


def getFirmwareAddAndRemoveInfo(oldJson: list, newJson: list) -> dict:
    """
    Get firmware version add/remove information
    Args:
        oldJson(dict): Dictionary containing old version MD5s
        newJson(dict): Dictionary containing new version MD5s
    Returns:
        dict: Get added firmware versions via key "added"; get removed firmware versions via key "removed"
    """
    oldSet = set(oldJson)
    newSet = set(newJson)
    info = {}
    info["added"] = newSet - oldSet
    info["removed"] = oldSet - newSet
    return info


def LoadOldMD5Firmware() -> dict:
    """
    Get previously saved firmware version MD5 information
    Returns:
        Historical MD5 encoded firmware information
    """
    MD5VerFilePath = "md5_encoded_firmware_versions.json"

    try:
        # Ensure file exists, create and write empty dict if not
        if not os.path.isfile(MD5VerFilePath):
            with open(MD5VerFilePath, "w", encoding="utf-8") as file:
                json.dump({}, file)
        # Load JSON data from file
        with open(MD5VerFilePath, "r", encoding="utf-8") as file:
            oldFirmwareJson = json.load(file)
    except json.JSONDecodeError as e:
        # If file content is not valid JSON, return empty dict
        printStr(f"JSON parsing error, error message: {e}")
        oldFirmwareJson = {}

    return oldFirmwareJson


def UpdateOldFirmware(newDict: dict):
    """
    Update historical firmware version MD5 information
    Args:
        newDict(dict): New MD5 encoded firmware version numbers
    """
    global oldMD5Dict
    MD5VerFilePath = "md5_encoded_firmware_versions.json"
    # First read historical data
    if os.path.exists(MD5VerFilePath):
        with open(MD5VerFilePath, "r", encoding="utf-8") as f:
            try:
                old_data = json.load(f)
            except Exception:
                old_data = {}
    else:
        old_data = {}

    # Update historical data
    for k, v in newDict.items():
        old_data[k] = v

    # Save
    with open(MD5VerFilePath, "w", encoding="utf-8") as f:
        f.write(json.dumps(old_data, indent=4, ensure_ascii=False))


def WriteInfo(model: str, cc: str, AddAndRemoveInfo: dict, modelDic: dict):
    """
    Record server firmware change information
    Args:
        model(str): Device model information
        cc(str): Device region code
        AddAndRemoveInfo(str): Contains add/remove firmware version information
    """
    global isFirst
    MD5InfoFilePath = "test_firmware_changes.txt"
    if not os.path.exists(MD5InfoFilePath):
        with open(MD5InfoFilePath, "w") as file:
            file.write("")
    with open(MD5InfoFilePath, "a+", encoding="utf-8") as f:
        if (
            isFirst
            and len(AddAndRemoveInfo["added"]) != 0
            or len(AddAndRemoveInfo["removed"]) != 0
        ):
            f.write(f"***** Record time: {getNowTime()} *****\n")
            isFirst = False
        for addVer in AddAndRemoveInfo["added"]:
            f.write(
                f"{modelDic[model]['name']}-{getCountryName(cc)} version server added firmware, corresponding version MD5 encoding: <{addVer}>\n"
            )
        for removeVer in AddAndRemoveInfo["removed"]:
            f.write(
                f"{modelDic[model]['name']}-{getCountryName(cc)} version server removed firmware, corresponding version MD5 encoding: <{removeVer}>\n"
            )


def getNowTime() -> str:
    SHA_TZ = timezone(
        timedelta(hours=8),
        name="Asia/Shanghai",
    )
    now = (
        datetime.utcnow()
        .replace(tzinfo=timezone.utc)
        .astimezone(SHA_TZ)
        .strftime("%Y-%m-%d %H:%M")
    )
    return now


def get_next_char(char, alphabet="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    """
    Return next character, return None if does not exist
    """
    index = alphabet.find(char)
    if index == -1:
        return None
    # If not the last character, return next character, otherwise return first character
    return alphabet[(index + 1) % len(alphabet)]


def get_pre_char(char, alphabet="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    """
    Return previous character, return None if does not exist
    """
    index = alphabet.find(char)
    if index == -1:
        return None
    # If not the first character, return previous character, otherwise return last character
    return alphabet[(index - 1) % len(alphabet)]


# @func_set_timeout(2000)
def DecryptionFirmware(
    model: str, md5Dic: dict, cc: str, modelDic: dict, oldJson
) -> dict:
    """Decode firmware number by brute force
    Args:
        model(str): Device model
        md5Dic(dict): Dictionary of firmware version MD5s to decode
        cc(str): Device region code
    Returns:
        dict: Dictionary of decoded firmware version numbers for the device model
    """
    printStr(
        f"Starting decryption of <{model} {getCountryName(cc)} version> test firmware",
    )
    md5list = md5Dic[cc]
    url = f"https://fota-cloud-dn.ospserver.net/firmware/{cc}/{model}/version.xml"
    content = requestXML(url)
    if content == None:
        return None
    try:
        xml = etree.fromstring(content)
        if len(xml.xpath("//latest//text()")) == 0:
            # Initialize version number for new device
            ccList = {
                "CHC": ["ZC", "CHC", "ZC"],
                "CHN": ["ZC", "CHC", ""],
                "TGY": ["ZH", "OZS", "ZC"],
                "XAA": ["UE", "OYM", "UE"],
                "ATT": ["SQ", "OYN", "SQ"],
                "KOO": ["KS", "OKR", "KS"],
                "TPA": ["PA", "TPA", "PA"],
            }  # CHC corresponds to China, the following dictionaries represent AP version number prefix, carrier CSC version number prefix, and whether it has baseband version number; CHN is without version number
            if cc in ccList.keys():
                latestVer = ""
                latestVerStr = "No official version yet"
                currentOS = "Unknown"
                FirstCode = model.replace("SM-", "") + ccList[cc][0]
                SecondCode = model.replace("SM-", "") + ccList[cc][1]
                ThirdCode = model.replace("SM-", "") + ccList[cc][2]
                latestVer = ""
                startYear = chr(
                    datetime.now().year - 2001 - 1 + ord("A")
                )  # Set default start year for version number, A represents 2001, set to start decryption from one year before current year
            else:
                printStr(f"Device <{model}> has no <{cc}> initialization version number information, please add manually before trying again!")
                return
        else:
            # Directly get current latest version number information from server
            latestVerStr = xml.xpath("//latest//text()")[0]  # Get current latest version number array
            latestVer = xml.xpath("//latest//text()")[0].split(
                "/"
            )  # Get current latest version number array
            currentOS = xml.xpath("//latest//@o")[0]  # Get current operating system version number
            FirstCode = latestVer[0][:-6]  # e.g.: N9860ZC
            SecondCode = latestVer[1][:-5]  # e.g.: N9860OZL
            ThirdCode = latestVer[2][:-6]  # e.g.: N9860OZC
            startYear = chr(
                datetime.now().year - 2001 - 4 + ord("A")
            )  # Set default start year for version number, A represents 2001, set to start decryption from 3 years before current year
        Dicts = {}  # Create a new dictionary
        Dicts[model] = {}
        Dicts[model][cc] = {}
        Dicts[model][cc]["versions"] = {}
        Dicts[model][cc]["latest_test_upload_time"] = ""
        DecDicts = {}  # Save decoded firmware version numbers
        oldDicts = {}
        oldDicts[model] = {}
        oldDicts[model][cc] = {}  # Cached firmware version numbers
        CpVersions = []  # Previous baseband version numbers
        # Initialization start
        startUpdateCount = "A"  # Set update count in version number to A, i.e., 1st update
        endUpdateCount = "B"
        endYear = get_next_char(startYear)
        startBLVersion = "0"  # Set default BL version number to 0
        endBLVersion = "2"
        # Initialization end
        lastVersion1 = ""    # Last regular version number
        lastVersion2 = ""    # Last major version number
        if (
            model in oldJson.keys()
            and cc in oldJson[model].keys()
            and "regular_update_test" in oldJson[model][cc].keys()
        ):
            if "None" in oldJson[model][cc]["major_version_test"].split("/")[0]:
                lastVersion1 = oldJson[model][cc]["regular_update_test"].split("/")[0]
            else:
                lastVersion1 = oldJson[model][cc]["regular_update_test"].split("/")[0]
                lastVersion2 = oldJson[model][cc]["major_version_test"].split("/")[0]
            oldDicts[model][cc] = deepcopy(oldJson[model][cc]["versions"])
            # CpVersions saves the most recent 3 baseband versions
            seen = set()
            modelVersion = [
                x.split("/")[-1] for x in list(oldJson[model][cc]["versions"].values())
            ]
            newMV = [x for x in modelVersion if not (x in seen or seen.add(x))][
                -12:
            ]  # Save the most recent 12 baseband versions
            CpVersions = newMV
        if lastVersion1 != "":
            startBLVersion = lastVersion1[-5]
            if latestVer != "":
                startUpdateCount = latestVer[0][-4]
            startYear = lastVersion1[-3]  #'A' representa 2001
        if latestVer != "":
            endBLVersion = get_next_char(
                latestVer[0][-5], "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            )  # Decrypt until current bootloader version +1, possible value is 1
            endUpdateCount = get_next_char(latestVer[0][-4])  # Decrypt until current major version number +1
        updateLst = get_letters_range(startUpdateCount, endUpdateCount)
        updateLst += "Z"  # Algunas versiones beta tienen 'Z' como cuarto carácter desde el final
        if latestVer != "":
            if latestVer[0][-2] in "JKL":
                endYear = get_next_char(
                    latestVer[0][-3], "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                )  # Si el mes del firmware de prueba actual es diciembre, aumentar el año del firmware de prueba en 1
            else:
                endYear = latestVer[0][-3]  # Obtener el año actual, tercer carácter desde el final
        starttime = time.perf_counter()
        for i1 in "US":
            for bl_version in get_letters_range(
                startBLVersion, endBLVersion
            ):  # Anti-downgrade version
                for update_version in updateLst:
                    for yearStr in get_letters_range(startYear, endYear):
                        for monthStr in get_letters_range("A", "L"):
                            tempCP = CpVersions[-12:].copy()
                            if ThirdCode != "":
                                for i in range(1, 3):
                                    initCP = (
                                        ThirdCode
                                        + i1
                                        + bl_version
                                        + update_version
                                        + yearStr
                                        + monthStr
                                        + str(i)
                                    )  # Manually specify current month baseband version
                                    tempCP.append(initCP)
                            for serialStr in "".join(
                                string.digits[1:] + string.ascii_uppercase
                            ):
                                # Add baseband using unused AP version number
                                initCP1 = (
                                    ThirdCode
                                    + i1
                                    + bl_version
                                    + update_version
                                    + yearStr
                                    + monthStr
                                    + get_pre_char(serialStr)
                                )
                                initCP2 = (
                                    ThirdCode
                                    + i1
                                    + bl_version
                                    + update_version
                                    + yearStr
                                    + monthStr
                                    + get_pre_char(get_pre_char(serialStr))
                                )
                                if initCP1 not in tempCP:
                                    tempCP.append(initCP1)
                                if initCP2 not in tempCP:
                                    tempCP.append(initCP2)
                                randomVersion = (
                                    bl_version
                                    + update_version
                                    + yearStr
                                    + monthStr
                                    + serialStr
                                )  # Combine version number
                                tempCode = (
                                    ""
                                    if ThirdCode == ""
                                    else ThirdCode + i1 + randomVersion
                                )  # WiFi version has no baseband version number
                                version1 = (
                                    FirstCode
                                    + i1
                                    + randomVersion
                                    + "/"
                                    + SecondCode
                                    + randomVersion
                                    + "/"
                                    + tempCode
                                )
                                if (
                                    model in oldJson.keys()
                                    and cc in oldJson[model].keys()
                                    and "versions" in oldJson[model][cc].keys()
                                    and version1
                                    in oldJson[model][cc]["versions"].values()
                                ):
                                    continue
                                md5 = hashlib.md5()
                                md5.update(version1.encode(encoding="utf-8"))
                                # When baseband and firmware versions are consistent
                                if md5.hexdigest() in md5list:
                                    DecDicts[md5.hexdigest()] = version1
                                    printStr(
                                        f"Added <{model} {getCountryName(cc)} version> test firmware: {version1}"
                                    )
                                    if (version1.split("/")[2] != "") and (
                                        version1.split("/")[2] not in CpVersions
                                        and version1.split("/")[2] not in tempCP
                                    ):
                                        CpVersions.append(version1.split("/")[2])
                                        tempCP.append(version1.split("/")[2])
                                # Firmware updated but baseband not updated
                                if len(CpVersions) > 0:
                                    for tempCpVersion in tempCP:
                                        version2 = (
                                            FirstCode
                                            + i1
                                            + randomVersion
                                            + "/"
                                            + SecondCode
                                            + randomVersion
                                            + "/"
                                            + tempCpVersion
                                        )
                                        if version1 == version2:
                                            continue
                                        if (
                                            model in oldJson.keys()
                                            and cc in oldJson[model].keys()
                                            and "versions" in oldJson[model][cc].keys()
                                        ) and version2 in oldJson[model][cc][
                                            "versions"
                                        ].values():
                                            continue
                                        md5 = hashlib.md5()
                                        md5.update(version2.encode(encoding="utf-8"))
                                        if md5.hexdigest() in md5list:
                                            DecDicts[md5.hexdigest()] = version2
                                            printStr(
                                                f"<Baseband> Added <{model} {getCountryName(cc)} version> test firmware: {version2}"
                                            )
                                            if (version2.split("/")[2] != "") and (
                                                version2.split("/")[2] not in CpVersions
                                                and version2.split("/")[2] not in tempCP
                                            ):
                                                CpVersions.append(
                                                    version2.split("/")[2]
                                                )
                                                tempCP.append(version2.split("/")[2])
                                # Beta version uses 'Z' as the 4th character from the end
                                vc2 = (
                                    bl_version + "Z" + yearStr + monthStr + serialStr
                                )  # Version number
                                tempCode = (
                                    ""
                                    if ThirdCode == ""
                                    else ThirdCode + i1 + randomVersion
                                )
                                version3 = (
                                    FirstCode
                                    + i1
                                    + vc2
                                    + "/"
                                    + SecondCode
                                    + vc2
                                    + "/"
                                    + tempCode
                                )
                                if (
                                    model in oldJson.keys()
                                    and cc in oldJson[model].keys()
                                    and "versions" in oldJson[model][cc].keys()
                                ) and version3 in oldJson[model][cc]["versions"].values():
                                    continue
                                md5 = hashlib.md5()
                                md5.update(version3.encode(encoding="utf-8"))
                                if md5.hexdigest() in md5list:
                                    DecDicts[md5.hexdigest()] = version3
                                    if (version3.split("/")[2] != "") and (
                                        version3.split("/")[2] not in CpVersions
                                        and version3.split("/")[2] not in tempCP
                                    ):
                                        CpVersions.append(version3.split("/")[2])
                                        tempCP.append(version3.split("/")[2])
                                if len(CpVersions) > 0:
                                    for tempCpVersion in tempCP:
                                        version4 = (
                                            FirstCode
                                            + i1
                                            + vc2
                                            + "/"
                                            + SecondCode
                                            + vc2
                                            + "/"
                                            + tempCpVersion
                                        )
                                        if version1 == version4:
                                            continue
                                        if (
                                            model in oldJson.keys()
                                            and cc in oldJson[model].keys()
                                            and "versions" in oldJson[model][cc].keys()
                                        ) and version4 in oldJson[model][cc][
                                            "versions"
                                        ].values():
                                            continue
                                        md5 = hashlib.md5()
                                        md5.update(version4.encode(encoding="utf-8"))
                                        if md5.hexdigest() in md5list:
                                            DecDicts[md5.hexdigest()] = version4
                                            printStr(
                                                f"<Z> Added <{model} {getCountryName(cc)} version> test firmware: {version4}"
                                            )
                                            if (version4.split("/")[2] != "") and (
                                                version4.split("/")[2]
                                                and version4.split("/")[2]
                                                not in CpVersions
                                                and version4.split("/")[2] not in tempCP
                                            ):
                                                CpVersions.append(
                                                    version4.split("/")[2]
                                                )
                                                tempCP.append(version4.split("/")[2])

        # Add decryption data
        oldDicts[model][cc].update(DecDicts)
        key_func = make_sort_key(oldDicts[model][cc].values())
        sortedList = sorted(oldDicts[model][cc].values(), key=key_func)
        if latestVerStr != "No official version yet" and latestVerStr!=None:
            stableVersion = latestVerStr.split("/")[0]
            currentChar = stableVersion[-4]
            majorChar = get_next_char(stableVersion[-4])  # Get next character of major version number
            minorVersion = getLatestVersion(sortedList, currentChar)  # Get daily system update
            majorVerison = getLatestVersion(sortedList, majorChar)  # Get major version update
            if majorVerison == None:
                majorVerison = "No major version test yet"
            else :
                majorChar = get_next_char(stableVersion[-4])+"Z" 
                majorVerison = getLatestVersion(sortedList, majorChar) 
            Dicts[model][cc]["regular_update_test"] = minorVersion
            Dicts[model][cc]["major_version_test"] = majorVerison
        else:
            Dicts[model][cc]["regular_update_test"] = sortedList[-1]
            Dicts[model][cc]["major_version_test"] = "No major version test yet"
        # Dicts[model][cc]["major_version_test"]
        Dicts[model][cc]["versions"] = DecDicts
        Dicts[model][cc]["latest_test_upload_time"] = ""
        if len(DecDicts) > 0:
            new_latest1 = Dicts[model][cc]["regular_update_test"].split("/")[0]
            new_latest2 = Dicts[model][cc]["major_version_test"].split("/")[0]
            if new_latest1 != lastVersion1 or new_latest2 != lastVersion2:
                Dicts[model][cc]["latest_test_upload_time"] = getNowTime()
        Dicts[model][cc]["latest_official"] = latestVerStr
        Dicts[model][cc]["official_android_version"] = currentOS
        if currentOS != "Unknown":
            if Dicts[model][cc]["major_version_test"].split("/")[0][-4] == "Z":
                Dicts[model][cc]["test_android_version"] = str(int(currentOS) + 1)
            else:
                if 'None' in Dicts[model][cc]["major_version_test"].split("/")[0]:
                    Dicts[model][cc]["test_android_version"] = str(
                        int(currentOS)
                        + ord(Dicts[model][cc]["regular_update_test"].split("/")[0][-4])
                        - ord(Dicts[model][cc]["latest_official"].split("/")[0][-4])
                    )
                else:
                    Dicts[model][cc]["test_android_version"] = str(
                        int(currentOS)
                        + ord(Dicts[model][cc]["major_version_test"].split("/")[0][-4])
                        - ord(Dicts[model][cc]["latest_official"].split("/")[0][-4])
                    )
        else:
            Dicts[model][cc]["official_android_version"] = current_latest_version
            Dicts[model][cc]["test_android_version"] = current_latest_version
        endtime = time.perf_counter()
        # If there is cached data
        if (
            model in oldJson.keys()
            and cc in oldJson[model].keys()
            and "versions" in oldJson[model][cc].keys()
            and len(oldJson[model][cc]["versions"]) > 0
        ):
            sumCount = len(Dicts[model][cc]["versions"]) + len(
                oldJson[model][cc]["versions"]
            )
            rateOfSuccess = round(sumCount / len(md5list) * 100, 2)
        else:
            rateOfSuccess = round(
                len(Dicts[model][cc]["versions"]) / len(md5list) * 100, 2
            )
        Dicts[model][cc]["decryption_percentage"] = f"{rateOfSuccess}%"
        printStr(
            f"<{modelDic[model]['name']} {getCountryName(cc)} version> test firmware version decryption completed, time taken: {round(endtime - starttime, 2)}s, decryption success rate: {rateOfSuccess}%"
        )
        if len(DecDicts) > 0:
            printStr(
                f"<{modelDic[model]['name']} {getCountryName(cc)} version> added {len(DecDicts)} test firmware(s)."
            )
        return Dicts
    except Exception as e:
        printStr(f"Error occurred: {e}")
        return None


# def make_sort_key(strings):
#     order = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
#     order_map = {c: i for i, c in enumerate(order)}

#     def get_tail4(s):
#         first_part = s.split("/")[0]
#         return first_part[-4:] if len(first_part) >= 4 else first_part

#     # 统计所有非Z开头的后三位
#     non_z_strings = [s for s in strings if len(get_tail4(s)) == 4 and get_tail4(s)[0] != "Z"]
#     non_z_last3 = [get_tail4(s)[1:] for s in non_z_strings]

#     # 统计所有Z开头的后三位
#     z_strings = [s for s in strings if len(get_tail4(s)) == 4 and get_tail4(s)[0] == "Z"]
#     z_last3 = [get_tail4(s)[1:] for s in z_strings]

#     def last3_key(last3):
#         return tuple(order_map.get(c, -1) for c in last3)

#     # 计算非Z开头的最大后三位和Z开头的最大后三位
#     max_non_z_last3 = max([last3_key(x) for x in non_z_last3], default=None)
#     max_z_last3 = max([last3_key(x) for x in z_last3], default=None)

#     def key_func(s):
#         tail4 = get_tail4(s)
#         if len(tail4) < 4:
#             # 长度不足4位，排最前
#             return (0, tuple(order_map.get(c, -1) for c in tail4))

#         head = tail4[0]
#         last3 = tail4[1:]
#         last3_tuple = last3_key(last3)

#         if head == "Z":
#             # 如果存在非Z字符串且Z的后三位大于非Z最大后三位，排最后
#             if max_non_z_last3 is not None and last3_tuple > max_non_z_last3:
#                 # 如果同时是Z中的最大值，则排在最最后
#                 if max_z_last3 is not None and last3_tuple == max_z_last3:
#                     return (3, last3_tuple)
#                 return (2, last3_tuple)
#             else:
#                 # 如果Z的后三位小于等于非Z最大后三位，排最前
#                 return (0, last3_tuple)
#         else:
#             # 非Z开头字符串正常排序
#             return (1, tuple(order_map.get(c, -1) for c in tail4))

#     return key_func


def make_sort_key(strings):
    order = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    order_map = {c: i for i, c in enumerate(order)}

    def get_tail4(s):
        first_part = s.split("/")[0]
        return first_part[-4:] if len(first_part) >= 4 else first_part

    def key_func(s):
        tail4 = get_tail4(s)
        if len(tail4) < 4:
            return (-1, -1, -1, -1)
        last3 = tail4[-3:]
        fourth = tail4[-4]
        # Z排前面，其余按顺序
        z_priority = 0 if fourth == "Z" else 1
        return tuple(order_map.get(c, 98) for c in last3) + (
            z_priority,
            order_map.get(fourth, 98),
        )

    return key_func


def getLatestVersion(version_list, chars):
    """
    Filter version numbers where the 4th character from the end is in the specified character set, sort by last 3 characters in ascending order, and return the maximum version number.
    :param version_list: List of version number strings
    :param chars: Specified character set for the 4th character from the end (e.g. "ZAB")
    :return: Maximum version number string (None if not found)
    """
    order = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    order_map = {c: i for i, c in enumerate(order)}

    def get_tail4(s):
        first_part = s.split("/")[0]
        return first_part[-4:] if len(first_part) >= 4 else first_part

    # Support filtering by multiple characters
    filtered = [
        s for s in version_list if len(get_tail4(s)) == 4 and get_tail4(s)[0] in chars
    ]
    if not filtered:
        return None

    def last3_key(s):
        tail4 = get_tail4(s)
        return tuple(order_map.get(c, -1) for c in tail4[1:])

    return max(filtered, key=last3_key)


def sendMessageByTG_Bot(title: str, content: str) -> None:
    """
    Send message using TG bot
    """
    if not push_config.get("TG_BOT_TOKEN") or not push_config.get("TG_USER_ID"):
        printStr("TG service bot_token or user_id not set!!\nCancelling push")
        return
    bot = telegram.Bot(token=push_config.get("TG_BOT_TOKEN"))
    # Send to personal user
    message1 = bot.send_message(
        chat_id=push_config.get("TG_USER_ID"),
        text=f"{title}\n{content}",
        parse_mode=telegram.ParseMode.MARKDOWN,
        disable_web_page_preview="true",
    )
    if message1.message_id > 0:
        printStr("TG personal message sent successfully!")
    # Send to channel
    if push_config.get("TG_CHAT_ID"):
        message2 = bot.send_message(
            chat_id=push_config.get("TG_CHAT_ID"),
            text=f"{title}\n{content}",
            parse_mode=telegram.ParseMode.MARKDOWN,
            disable_web_page_preview="true",
        )
        if message2.message_id > 0:
            printStr("TG channel message sent successfully!")


def fcm(title: str, content="", link="") -> None:
    """
    Send message using FCM
    """
    if link == "":
        data2 = {"title": title, "message": content}
        data1 = {"text": data2}
    else:
        data2 = {"title": title, "url": link}
        data1 = {"link": data2}

    data = {
        "to": push_config.get("FCM_KEY"),
        "time_to_live": 60,
        "priority": "high",
        "data": data1,
    }
    headers = {
        "authorization": f'key={push_config.get("FCM_API_KEY")}',
        "Content-Type": "application/json",
    }
    url = "https://fcm.googleapis.com/fcm/send"
    response = requests.post(url=url, data=json.dumps(data), headers=headers)
    if response.status_code == 200:
        printStr("FCM sent successfully")


push_config = {
    "FCM_API_KEY": "",
    "FCM_KEY": "",
    "PUSH_KEY": "",  # Server chan PUSH_KEY, compatible with old and Turbo versions
    "TG_BOT_TOKEN": "",  # Bot token, e.g.: 1407203283:AAG9rt-6RDaaX0HBLZQq0laNOh898iFYaRQ
    "TG_USER_ID": "",  # Bot's TG_USER_ID, e.g.: -1001234567890
    "TG_API_HOST": "",  # Proxy api
    "TG_PROXY_AUTH": "",  # Proxy authentication parameters
    "TG_PROXY_HOST": "",  # Bot's proxy host address
    "TG_PROXY_PORT": "",  # Bot's proxy port
    "TG_CHAT_ID": "",  # Channel ID
}


def run():
    # Get related parameter variable data
    for k in push_config:
        if os.getenv(k):
            v = os.getenv(k)
            push_config[k] = v
    global modelDic, oldMD5Dict, isFirst
    jsonStr = ""
    decDicts = {"last_update_time": getNowTime()}
    VerFilePath = "firmware.json"
    Ver_mini_FilePath = "firmware_mini.json"
    AddTxtPath = "test_firmware_changelog.txt"
    startTime = time.perf_counter()
    if not os.path.exists(VerFilePath):
        with open(VerFilePath, "w") as file:
            file.write("{}")

    with open(VerFilePath, "r", encoding="utf-8") as f:
        jsonStr = f.read()
        oldJson = {}
        if jsonStr != "":
            oldJson = json.loads(jsonStr)
        hasNewVersion = False
        with ProcessPoolExecutor(max_workers=4) as pool:
            future_to_model = {
                pool.submit(getNewVersions, oldJson, model, modelDic, oldMD5Dict): model
                for model in modelDic
            }
            for future in concurrent.futures.as_completed(future_to_model):
                model = future_to_model[future]
                result = future.result()
                if result is not None:
                    hasNew, newMDic = result
                    if hasNew:
                        hasNewVersion = True
                    for m, cc_dict in newMDic.items():
                        if m not in decDicts:
                            decDicts[m] = {}
                        for cc, cc_data in cc_dict.items():
                            decDicts[m][cc] = cc_data
        if hasNewVersion:
            # Firmware update log
            with open(AddTxtPath, "a+", encoding="utf-8") as file:
                for model in modelDic:
                    if (model in decDicts) and (model in oldJson):
                        for cc in modelDic[model]["CC"]:
                            if not cc in oldJson[model] or not cc in decDicts[model]:
                                continue
                            md5Keys = (
                                decDicts[model][cc]["versions"].keys()
                                - oldJson[model][cc]["versions"].keys()
                            )
                            if len(md5Keys) > 0:
                                if isFirst:
                                    file.write(f"***** Record time: {getNowTime()} *****\n")
                                    isFirst = False
                                Str = ""
                                newVersions = {}
                                for md5key in md5Keys:
                                    newVersions[md5key] = decDicts[model][cc]["versions"][
                                        md5key
                                    ]
                                newVersions = dict(
                                    sorted(newVersions.items(), key=lambda x: x[1])
                                )
                                for key, value in newVersions.items():
                                    textStr = "\n" + value
                                    Str += f"{modelDic[model]['name']}-{getCountryName(cc)} version added test firmware version: {value}, corresponding MD5 value: {key}\n"
                                file.write(Str)
                                sendMessageByTG_Bot(
                                    f"#{modelDic[model]['name']}—{getCountryName(cc)} added beta firmware",
                                    textStr.strip(),
                                )
            # Update latest version for all models
            with open("latest_versions_by_model.md", "w", encoding="utf-8") as f:
                textStr = ""
                for model in sorted(modelDic.keys()):
                    if (model not in decDicts) or (model not in oldJson):
                        continue
                    for cc in modelDic[model]["CC"]:
                        if not cc in decDicts[model].keys():
                            continue
                        textStr += f"#### {modelDic[model]['name']} {getCountryName(cc)} version: \nOfficial: {decDicts[model][cc]['latest_official']}  \nRegular update test: {decDicts[model][cc]['regular_update_test']}  \nMajor version test: {decDicts[model][cc]['major_version_test']} \n"
                f.write(textStr)
    endTime = time.perf_counter()
    printStr(f"Total time: {round(endTime - startTime, 2)}s")
    # Create deep copy to avoid destroying original data
    firmware_info_mini = deepcopy(decDicts)
    for model_data in firmware_info_mini.values():
        if isinstance(model_data, dict):
            for region_data in model_data.values():
                if isinstance(region_data, dict):
                    region_data.pop("versions", None)
    sorted_firmware_info_mini = OrderedDict()
    for model in sorted(firmware_info_mini.keys()):
        sorted_firmware_info_mini[model] = firmware_info_mini[model]
    with open(Ver_mini_FilePath, "w", encoding="utf-8") as f:
        f.write(json.dumps(sorted_firmware_info_mini, indent=4, ensure_ascii=False))
    # Before writing firmware.json, sort version numbers for each model/region
    for model in decDicts:
        if model == "last_update_time":
            continue
        for region in decDicts[model]:
            if "versions" in decDicts[model][region]:
                ver_dict = decDicts[model][region]["versions"]
                # Get all values
                values = list(ver_dict.values())
                # Generate sort key
                key_func = make_sort_key(values)
                # Sort by value and rebuild dictionary
                sorted_items = sorted(
                    ver_dict.items(), key=lambda item: key_func(item[1])
                )
                decDicts[model][region]["versions"] = dict(sorted_items)
    sorted_decDicts = OrderedDict()
    for model in sorted(decDicts.keys()):
        sorted_decDicts[model] = decDicts[model]
    with open(VerFilePath, "w", encoding="utf-8") as f:
        f.write(json.dumps(sorted_decDicts, indent=4, ensure_ascii=False))


def process_cc(cc, modelDic, oldMD5Dict, md5Dic, oldJson, model):
    newMDic = {model: {}}
    newMD5Dict = {model: {}}
    hasNewVersion = False
    if model in oldJson.keys() and cc in oldJson[model].keys():
        # Copy existing device firmware version content
        newMDic[model][cc] = deepcopy(oldJson[model][cc])
        # Initialize if following keys don't exist
        newMDic[model][cc].setdefault("latest_test_upload_time", "None")
        newMDic[model][cc].setdefault("official_android_version", "")
        newMDic[model][cc].setdefault("test_android_version", "")
    else:
        # Initialize content for new device
        newMDic[model][cc] = {
            "versions": {},
            "major_version_test": "",
            "latest_official": "",
            "latest_version_description": "",
            "decryption_percentage": "",
            "latest_test_upload_time": "None",
            "official_android_version": "",
            "test_android_version": "",
            "region": "",
            "model": "",
            "decryption_count": 0,
        }
    if model in oldMD5Dict and cc in oldMD5Dict[model]:
        # Get add/remove information of MD5 encoded firmware version numbers
        newMD5Dict[model][cc] = deepcopy(oldMD5Dict[model][cc])
        oldMD5Vers = oldMD5Dict[model][cc]["versions"]
        newMD5Vers = md5Dic[cc]
        addAndRemoveInfo = getFirmwareAddAndRemoveInfo(
            oldJson=oldMD5Vers, newJson=newMD5Vers
        )
        WriteInfo(
            model=model, cc=cc, AddAndRemoveInfo=addAndRemoveInfo, modelDic=modelDic
        )
    else:
        # Initialize content for new device
        newMD5Dict[model][cc] = {"versions": {}, "firmware_count": 0}
    newMD5Dict[model][cc]["versions"] = md5Dic[cc]
    newMD5Dict[model][cc]["firmware_count"] = len(md5Dic[cc])

    verDic = DecryptionFirmware(model, md5Dic, cc, modelDic, oldJson)  # Decrypt to get new data
    if verDic is None or model not in verDic or cc not in verDic[model] or "versions" not in verDic[model][cc]:
        return False, {}, {}
    if (
        newMDic[model][cc]["latest_official"] != ""
        and verDic != None
        and verDic[model][cc]["latest_official"] != newMDic[model][cc]["latest_official"]
    ):
        if (
            verDic[model][cc]["latest_official"].split("/")[0][-4:]
            > newMDic[model][cc]["latest_official"].split("/")[0][-4:]
        ):
            # Send notification when official version is updated
            sendMessageByTG_Bot(
                f"#{model.split('-')[1]} - <{newMDic[model][cc]['model']} {getCountryName(cc)} version> pushed update",
                f"Version: {verDic[model][cc]['latest_official']}\n[View update log](https://doc.samsungmobile.com/{model}/{cc}/doc.html)",
            )
            # fcm(f"#{model} {getCountryName(cc)} version pushed update, version: {verDic[model][cc]['latest_official']}",
            #     link=f"https://doc.samsungmobile.com/{model}/{cc}/doc.html")
        else:
            # Send notification when server rolls back firmware
            sendMessageByTG_Bot(
                f"#Firmware rollback - <{newMDic[model][cc]['model']} {getCountryName(cc)} version>",
                f"{newMDic[model][cc]['latest_official'].split('/')[0]} ➡️ {verDic[model][cc]['latest_official'].split('/')[0]}",
            )
        newMDic[model][cc]["latest_official"] = verDic[model][cc]["latest_official"]

    newMDic[model][cc]["region"] = getCountryName(cc)
    newMDic[model][cc]["model"] = modelDic[model]["name"]
    if verDic[model][cc]["major_version_test"] != "":
        newMDic[model][cc]["major_version_test"] = verDic[model][cc]["major_version_test"]
    if verDic[model][cc]["regular_update_test"] != "":
        newMDic[model][cc]["regular_update_test"] = verDic[model][cc]["regular_update_test"]
    if verDic[model][cc]["latest_official"] != "":
        newMDic[model][cc]["latest_official"] = verDic[model][cc]["latest_official"]
    if verDic[model][cc]["latest_test_upload_time"] != "":
        newMDic[model][cc]["latest_test_upload_time"] = verDic[model][cc][
            "latest_test_upload_time"
        ]
    newMDic[model][cc]["official_android_version"] = verDic[model][cc]["official_android_version"]
    newMDic[model][cc]["test_android_version"] = verDic[model][cc]["test_android_version"]

    # Version number description
    ver = newMDic[model][cc]["major_version_test"].split("/")[0]
    ver2 = newMDic[model][cc]["regular_update_test"].split("/")[0]
    if "None" not in ver:
        yearStr = ord(ver[-3]) - 65 + 2001  # Get update year
        monthStr = ord(ver[-2]) - 64  # Get update month
        countStr = char_to_number(ver[-1])  # Get update number
        definitionStr = f"Year {yearStr} Month {monthStr} #{countStr} major version test"
        newMDic[model][cc]["latest_version_description"] = definitionStr
    elif "None" not in ver2:
        yearStr = ord(ver2[-3]) - 65 + 2001  # Get update year
        monthStr = ord(ver2[-2]) - 64  # Get update month
        countStr = char_to_number(ver2[-1])  # Get update number
        definitionStr = f"Year {yearStr} Month {monthStr} #{countStr} regular update test"
        newMDic[model][cc]["latest_version_description"] = definitionStr
    else:
        newMDic[model][cc]["latest_version_description"] = "None"
    if verDic[model][cc]["decryption_percentage"] != "":
        newMDic[model][cc]["decryption_percentage"] = verDic[model][cc]["decryption_percentage"]
        # If there is cached data, get the difference
    if len(verDic[model][cc]["versions"]) == 0:
        # If no version number was decrypted, return directly
        return False, newMDic, newMD5Dict
    diffModel = set(verDic[model][cc]["versions"].keys()) - set(
        newMDic[model][cc]["versions"].keys()
    )
    if diffModel:
        hasNewVersion = True
        for key in diffModel:
            # Store new version number
            newMDic[model][cc]["versions"][key] = verDic[model][cc]["versions"][key]
    newMDic[model][cc]["versions"] = dict(
        sorted(
            newMDic[model][cc]["versions"].items(), key=lambda x: x[1].split("/")[0][-3:]
        )
    )
    newMDic[model][cc]["decryption_count"] = len(newMDic[model][cc]["versions"])
    return hasNewVersion, newMDic, newMD5Dict


def getNewVersions(oldJson, model, modelDic, oldMD5Dict):
    md5Dic = readXML(model, modelDic)  # Return md5 dictionary containing multiple regional versions
    if len(md5Dic) == 0:
        return
    newMDic = {model: {}}
    md5Dicts_list = []  # Used to collect newMD5Dict from each thread
    hasNewVersion = False
    with ThreadPoolExecutor(max_workers=4) as pool:
        future_to_cc = {
            pool.submit(
                process_cc, cc, modelDic, oldMD5Dict, md5Dic, oldJson, model
            ): cc
            for cc in md5Dic.keys()
        }
        for future in as_completed(future_to_cc):
            result = future.result()
            if result is None:
                continue
            hasNew, newMDic_part, newMD5Dict_part = result
            if hasNew:
                hasNewVersion = True
            for m, cc_dict in newMDic_part.items():
                if m not in newMDic:
                    newMDic[m] = {}
                for cc, cc_data in cc_dict.items():
                    newMDic[m][cc] = cc_data
            md5Dicts_list.append(newMD5Dict_part)
    # Merge newMD5Dict
    mergedMD5Dict = {"last_update_time": getNowTime()}
    mergedMD5Dict[model] = {}
    for md5Dict in md5Dicts_list:
        if model in md5Dict:
            mergedMD5Dict[model].update(md5Dict[model])
    UpdateOldFirmware(mergedMD5Dict)  # Update historical firmware Json information
    return hasNewVersion, newMDic


def init_globals(q):
    global log_queue
    log_queue = q


if __name__ == "__main__":
    try:
        oldMD5Dict = LoadOldMD5Firmware()  # Get last MD5 encoded version number data
        if isDebug:
            # modelDic = dict(list(getModelDictsFromDB().items())[:5])  # Use for testing
            modelDic = {"SM-S731U": {"name": "S25 FE", "CC": ["ATT"]}}  # Use for testing
        else:
            try:
                modelDic = getModelDictsFromDB()  # Get model information from database
            except Exception as db_error:
                printStr(f"Database connection failed: {db_error}")
                printStr("Falling back to file-based model reading...")
                modelDic = getModelDicts()  # Fall back to file-based model reading
        run()
    except func_timeout.exceptions.FunctionTimedOut:
        printStr("Task timeout, execution exited!")
    except Exception as e:
        printStr(f"Error occurred: {e}")
