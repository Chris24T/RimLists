import xml.etree.ElementTree

import requests
from bs4 import BeautifulSoup
import winreg
import os
import xml.etree.ElementTree as ET

# repo_url = "https://github.com/Chris24T/RimLists"

rimworld_id = "294100"
rimworld_version = ""  # "1.4.3641 rev649"
rimworld_package_id = "ludeon.rimworld"
rimworld_install_path = ""  # "steamapps\common\RimWorld"

steam_install_path = ""  # "C:\Program Files (x86)\Steam"
steam_workshop_content_path = "" # C:\Program Files (x86)\Steam\steamapps\workshop\content

modlist_title = ""
modlist_save_path = ""

# util to get valid path from user input
def getValidPath( prompt, default_path):
    # _prompt = "\n"+prompt
    path = input(prompt) or default_path

    while not os.path.exists(path):
        if path == default_path:
            print(f"ERROR: Could not auto-resolve path at: {path}", end="\n")
        else:
            print(f"ERROR: The given path does not exist: {path} ", end="\n\n" )
        print(prompt, end="")
        path = input() or default_path
    print("     " + path)
    return path

# read a collection url
def input_collection_url():

    url = input("\nEnter RimWorld Steam workshop collection URL: ")
    return url

# read modlist target save location
def input_modlist_save_path():
    global modlist_save_path

    rimpy_modlist_folder = os.path.normpath(os.path.join(os.environ["APPDATA"], "../LocalLow", "RimPy Mod Manager\ModLists"))
    modlist_save_path = getValidPath("Enter modlist save location path (leave empty for auto-resolve RimPy Modlists folder): ",  rimpy_modlist_folder)

# read steam install path - for Rimworld & workshop
def get_steam_path():
    try:
        hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\WOW6432Node\Valve\Steam")
        return os.path.join(winreg.QueryValueEx(hkey, "InstallPath")[0])
    except:
        return "*CANNOT RESOLVE STEAM PATH*"

# read workshop content path
def input_steam_workshop_content_path():
    global steam_workshop_content_path

    default_workshop_path = os.path.join(get_steam_path(), "steamapps\workshop\content")

    steam_workshop_content_path = getValidPath("Enter Steam workshop content path (leave empty for auto-resolve): ", default_workshop_path)

# read rimworld install path (for package ids)
def input_rimworld_path():
    global steam_rimworld_path
    rimworld_manifest_path = os.path.join(get_steam_path(), f"steamapps/appmanifest_{rimworld_id}.acf")

    # Read the installation directory from the appmanifest file
    try:
        with open(rimworld_manifest_path, "r") as f:
            for line in f.readlines():
                if "installdir" in line:
                    default_rimworld_path = os.path.join(get_steam_path(), "steamapps\common", line.strip().split('"')[3])
    except FileNotFoundError:
        default_rimworld_path = "CANNOT RESOLVE RIMWORLD PATH"

    steam_rimworld_path = getValidPath("Enter your full RimWorld install path (leave empty for auto-resolve): ", default_rimworld_path)

# read rimworld version
def set_rimworld_version():
    global rimworld_version
    try:
        with open(os.path.join(steam_rimworld_path, "Version.txt"), "r") as f:
            rimworld_version = f.readlines()[0]

    except FileNotFoundError:
        print("Unable to automatically find RimWorld 'Version.txt' in RimWorld install dir")
        rimworld_version = input("Please enter your RimWorld version (e.g. '1.4.3641 rev649'): ")
    # print("    "+rimworld_version)

# read string for modlist title or use collection title
def input_modlist_title(default_title):
    global modlist_title
    modlist_title = input("Enter modlist name (leave empty for collection title): ") or default_title
    print("     " + modlist_title)

# parse collection html contents to find mod ids
def parse(content):
    soup = BeautifulSoup(content, "html.parser")
    id_nodes = soup.find_all("div", class_="collectionItem")
    ids = [node.get("id")[11::] for node in id_nodes if node.has_attr("id")]

    if not len(ids):
        print(
            f"ERROR:No mod collection could be found at provided URL", end="\n")
        return ids

    modlist_title = soup.find("div", class_="workshopItemTitle").decode_contents()
    input_modlist_title(modlist_title)

    return ids

# (unused)
def persistUntilSuccess(attempt, onFailAttempt, onSuccessAttempt, validate=None):

    _validate = lambda x: validate(x) if validate else x

    attempt_results = attempt()
    isSuccessful = _validate(attempt)

    while not isSuccessful:
        terminate, modifiedAttempt = onFailAttempt(attempt_results)
        if terminate:
            exit(1)
        attempt = modifiedAttempt if modifiedAttempt else attempt
        attempt_results = attempt()
        isSuccessful = _validate(attempt_results)

    return onSuccessAttempt(attempt_results)

# get details about a given collection:
# user input provides collection url
# collection html is parsed
def get_collection_details():

    # persistUntilSuccess(lambda: requests.get(input("Enter a Steam workshop collection URL: ")), ... )

    while True:
        try:

            url = input_collection_url()
            response = requests.get(url)
            if response.status_code == 200:
                result = parse(response.content)
                if len(result):
                    return result
            else:
                print(
                    "ERROR: Can't fetch URL content. Please make sure the URL is correct and you are connected to a network.", end="\n")
        except:
            print(
                "ERROR: Can't fetch URL. Please make sure the URL is a valid RimWorld Steam workshop collection.", end="\n")


# convert mod ids (numerical) to mod package ids (string)
def findModPackageIds(ids):
    dir_path = os.path.join(steam_workshop_content_path, rimworld_id)
    dir_contents = os.listdir(dir_path)
    packages = [rimworld_package_id]

    for item in ids:
        if item in dir_contents:
            about_path = os.path.join(dir_path, item, "About\About.xml")

            if os.path.isfile(about_path):
                try:
                    tree = ET.parse(about_path)
                    root = tree.getroot()
                    packages.append(root.find("packageId").text.lower())
                except xml.etree.ElementTree.ParseError:
                    print(f"There was an error in parsing 'About.xml' of mod with id: {item} ")
                    print(f"Press enter to skip mod, or enter any key to abort process:")
                    if input():
                        print(f"Exiting...")
                        exit(1)
            else:
                print(f"Mod {item} is missing an 'About.xml' or is not downloaded into {steam_workshop_content_path}, skipping...")

    return packages

# build the modlist.xml
def buildXMLModlist(package_ids):
    root = ET.Element("ModsConfigData")

    version = ET.Element("version")
    version.text = rimworld_version
    root.append(version)

    active_mods = ET.Element('activeMods')

    for id in package_ids:
        li = ET.Element("li")
        li.text = id
        active_mods.append(li)

    root.append(active_mods)

    known_expansions = ET.Element('knownExpansions')
    li = ET.Element("li")
    li.text = rimworld_package_id
    known_expansions.append(li)

    root.append(known_expansions)

    tree = ET.ElementTree(root)
    ET.indent(tree, space="\t", level=0)  # need py3.9
    save_path = os.path.join(modlist_save_path, modlist_title) + ".xml"
    tree.write(save_path, encoding='utf-8', xml_declaration=True)

if __name__ == '__main__':
    entries = get_collection_details()

    input_steam_workshop_content_path()
    input_rimworld_path()
    input_modlist_save_path()
    set_rimworld_version()

    package_ids = findModPackageIds(entries)
    buildXMLModlist(package_ids)

    print(f"\nModList: {modlist_title} , created in: {modlist_save_path}")

    input("Press enter to close...")
    exit(0)
