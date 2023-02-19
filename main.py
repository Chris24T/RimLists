import requests
from bs4 import BeautifulSoup
import winreg
import os
import xml.etree.ElementTree as ET

rimworld_id = "294100"
rimworld_version = ""  # "1.4.3641 rev649"
rimworld_package_id = "ludeon.rimworld"
rimworld_install_path = ""  # "steamapps\common\RimWorld"

steam_install_path = ""  # "C:\Program Files (x86)\Steam"
steam_workshop_content_path = "steamapps\workshop\content"
workshop_collection_title = ""

rimpy_modlists_path = os.path.normpath(os.path.join(os.environ["APPDATA"], "../LocalLow", "RimPy Mod Manager\ModLists"))


def get_modlist_install_path():
    global rimpy_modlists_path
    inp = input("Enter modlist save path (leave empty for RimPy Modlists folder): ")
    if not len(inp):
        inp = rimpy_modlists_path

    while not os.path.exists(inp):
        print(f"The path '{inp}' does not exist")
        inp = input("Enter modlist save path (leave empty for RimPy Modlists folder): ")
        if not len(inp):
            inp = rimpy_modlists_path

    rimpy_modlists_path = inp
    print("     " + rimpy_modlists_path)


def set_rimworld_version():
    global rimworld_version
    try:
        with open(os.path.join(rimworld_install_path, "Version.txt"), "r") as f:
            rimworld_version = f.readlines()[0]

    except FileNotFoundError:
        print("Unable to automatically find RimWorld 'Version.txt' in RimWorld install dir")
        input("Please enter your RimWorld version: ")


def get_rimworld_install_path():
    global rimworld_install_path

    # Open the Steam registry key
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "SOFTWARE\\Valve\\Steam")

    # Read the Steam installation directory from the registry
    steam_dir, _ = winreg.QueryValueEx(key, "SteamPath")

    # base steamapps path
    steam_apps_path = f"{steam_dir}/steamapps"

    # Construct the path to the game's appmanifest file
    appmanifest_path = f"{steam_apps_path}/appmanifest_{rimworld_id}.acf"

    try:
        # Read the installation directory from the appmanifest file
        with open(appmanifest_path, "r") as f:
            for line in f.readlines():
                if "installdir" in line:
                    rimworld_install_path = os.path.join(steam_apps_path, "common", line.strip().split('"')[3])
    except FileNotFoundError:
        print("Unable to find RimWorld install directory")
        rimworld_install_path = input("Please enter your full RimWorld install path: ")


def get_steam_install_path():
    global steam_install_path
    try:
        hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\WOW6432Node\Valve\Steam")
        steam_install_path = winreg.QueryValueEx(hkey, "InstallPath")[0]
    except:
        print("Unable to find Steam install directory")
        steam_install_path = input("Please enter Steam install path: ")


# read a url from input
def getCollectionUrl():
    return input("Enter RimWorld Steam workshop collection URL: ")


def parse(content):
    soup = BeautifulSoup(content, "html.parser")
    id_nodes = soup.find_all("div", class_="collectionItem")
    ids = [node.get("id")[11::] for node in id_nodes if node.has_attr("id")]

    if not len(ids):
        print(
            f"No mod collection could be found at provided URL")
        exit(1)

    global workshop_collection_title
    workshop_collection_title = soup.find("div", class_="workshopItemTitle").decode_contents()

    inp = input("Enter modlist name (leave empty for collection title): ")
    if len(inp):
        workshop_collection_title = inp
    print("     " + workshop_collection_title)
    return ids


def getCollectionEntries(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return parse(response.content)
        else:
            print(
                "\nThere was an error in fetching the URL content. Please make sure the URL is correct and you are connected to a network.")
            exit(1)
    except:
        print(
            "\nThere was an error in fetching the URL content. Please make sure the URL is a valid RimWorld Steam workshop collection.")
        exit(1)


def findModPackageIds(ids):
    dir_path = os.path.join(steam_install_path, steam_workshop_content_path, rimworld_id)
    dir_contents = os.listdir(dir_path)
    packages = [rimworld_package_id]

    for item in ids:
        if item in dir_contents:
            about_path = os.path.join(dir_path, item, "About\About.xml")

            if os.path.isfile(about_path):
                tree = ET.parse(about_path)
                root = tree.getroot()
                packages.append(root.find("packageId").text.lower())
            else:
                print(f"Mod {item} is missing About.xml")

    return packages


import xml.dom.minidom as md


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
    save_path = os.path.join(rimpy_modlists_path, workshop_collection_title) + ".xml"
    tree.write(save_path, encoding='utf-8', xml_declaration=True)


if __name__ == '__main__':
    url = getCollectionUrl()
    entries = getCollectionEntries(url)
    get_steam_install_path()
    get_modlist_install_path()
    get_rimworld_install_path()
    set_rimworld_version()
    package_ids = findModPackageIds(entries)
    buildXMLModlist(package_ids)
    print(f"\nModList: {workshop_collection_title} , created in: {rimpy_modlists_path}")
    input("Press any key to close...")
