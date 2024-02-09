import configparser
import functools
import os
import sys

import cProfile
CONFIG = {}


def read_configuration(filename):
    """Read configuration file and populate CONFIG dictionary"""
    if os.path.isfile(filename):
        config = configparser.ConfigParser()
        config.read(filename)

        CONFIG["global"] = {
            "years": config.get("years", "years").split(","),
            "chars": config.get("specialchars", "chars").split(","),
            "numfrom": config.getint("nums", "from"),
            "numto": config.getint("nums", "to"),
            "wcfrom": config.getint("nums", "wcfrom"),
            "wcto": config.getint("nums", "wcto"),
            "threshold": config.getint("nums", "threshold")
        }

        leet = functools.partial(config.get, "leet")
        leet_characters = {}
        letters = {"a", "i", "e", "t", "o", "s", "g", "z"}
        for letter in letters:
            leet_characters[letter] = config.get("leet", letter)

        CONFIG["LEET"] = leet_characters
        return True
    else:
        print("Configuration file " + filename + " not found!")
        sys.exit("Exiting.")
        return False


def apply_leet_conversion(input_string):
    """Convert input string to leet (1337)"""
    for letter, leet_letter in CONFIG["LEET"].items():
        input_string = input_string.replace(letter, leet_letter)
    return input_string


def concatenate_strings(sequence, start, stop):
    """Generate concatenated strings with numerical suffixes"""
    for my_str in sequence:
        for num in range(start, stop):
            yield my_str + str(num)


def combine_strings(seq, start, special=""):
    """Generate combinations of strings with optional special character"""
    for my_str in seq:
        for my_str1 in start:
            yield my_str + special + my_str1
            for my_str2 in start:
                yield my_str + special + my_str1 + my_str + special


def save_to_file(filename, unique_list_finished):
    """Save unique strings to a file"""
    with open(filename, "a") as f:
        unique_list_finished.sort()
        f.write(os.linesep.join(unique_list_finished))

    with open(filename, "r") as f:
        lines = sum(1 for line in f)

    print(
        "[+] Saving dictionary to \033[1;31m"
        + filename
        + "\033[1;m, counting \033[1;31m"
        + str(lines)
        + " words.\033[1;m"
    )


def interactive_input():

    print("\r\n[+] Insert the information about the victim to make a password list")
    #  Get the victim's personal information
    profile = {}
    name = input("> First Name: ").lower()
    while len(name) == 0 or name == " " or name == "  " or name == "   ":
        print("\r\n[-] You must enter a name at least!")
        name = input("> Name: ").lower()
    profile["name"] = str(name)
    profile["surname"] = input("> Surname: ").lower()
    profile["nick"] = input("> Nickname: ").lower()

    # Get valid birthdate input
    birthdate = input("> Birthdate (DDMMYYYY): ")
    while len(birthdate) != 0 and len(birthdate) != 8:
        print("\r\n[-] You must enter 8 digits for birthday!")
        birthdate = input("> Birthdate (DDMMYYYY): ")
    profile["birthdate"] = str(birthdate)
    print("\r\n")

    # Get the guardian's information
    profile["guardian_name"] = input("> Guardian) name: ").lower()
    profile["guardian_nick"] = input("> Guardian) nickname: ").lower()
    guardian_birthdate = input("> Guardian) birthdate (DDMMYYYY): ")
    while len(guardian_birthdate) != 0 and len(guardian_birthdate) != 8:
        print("\r\n[-] You must enter 8 digits for birthday!")
        guardian_birthdate = input("> Guardian birthdate (DDMMYYYY): ")

     # Get valid guardian birthdate input
    profile["guardian_birthdate"] = str(guardian_birthdate)
    print("\r\n")

    # Get the girlfriend or X's information
    profile["girlfriend_name"] = input("> girlfriend or X name: ").lower()
    profile["girlfriend_nick"] = input("> girlfriend or X nickname: ").lower()

    # Get valid girlfriend or X birthdate input
    girlfriend_birthdate = input("> girlfriend or X birthdate (DDMMYYYY): ")
    while len(girlfriend_birthdate) != 0 and len(girlfriend_birthdate) != 8:
        print("\r\n[-] You must enter 8 digits for birthday!")
        girlfriend_birthdate = input(
            "> girlfriend or X birthdate (DDMMYYYY): ")
    profile["girlfriend_birthdate"] = str(girlfriend_birthdate)
    print("\r\n")

    # Get additional information
    profile["kids"] = input("> girlfriend_names's name: ").lower()
    number = input("> Mobile Number: ")
    while len(number) != 0 and len(number) != 10:
        print("\r\n[-] You must enter 10 digits for mobile number!")
        number = input("> Mobile Number: ")
    profile["number"] = (number)
    profile["email"] = input("> Email ID: ").lower()
    profile["pet"] = input("> Pet's name: ").lower()
    profile["company"] = input("> Company name: ").lower()
    print("\r\n")

    # Get user preferences for password generation
    profile["words"] = [""]
    words1 = input(
        "> Do you want to add some key words about the victim? Y/[N]: ").lower()
    key_words = ""
    if words1 == "y":
        key_words = input(
            "> Please enter the words, separated by comma. [i.e. hacker,juice,black], spaces will be removed: "
        ).replace(" ", "")
    profile["words"] = key_words.split(",")
    profile["spechars1"] = 'y'
    profile["randnum"] = "y"
    profile["leetmode"] = 'y'

    generate_wordlist_from_profile(profile,)


def generate_wordlist_from_profile(profile):
    """Generate a wordlist from a given profile"""
    chars = CONFIG["global"]["chars"]
    years = CONFIG["global"]["years"]
    num_from = CONFIG["global"]["numfrom"]
    num_to = CONFIG["global"]["numto"]
    profile["spechars"] = []
    if profile["spechars1"] == "y":

        for spec1 in chars:
            profile["spechars"].append(spec1)
            for spec2 in chars:
                profile["spechars"].append(spec1 + spec2)
                for spec3 in chars:
                    profile["spechars"].append(spec1 + spec2 + spec3)
    print("\r\n[+] Now making a dictionary...")
    birthdate_yy = profile["birthdate"][-2:]
    birthdate_yyy = profile["birthdate"][-3:]
    birthdate_yyyy = profile["birthdate"][-4:]
    birthdate_xd = profile["birthdate"][1:2]
    birthdate_xm = profile["birthdate"][3:4]
    birthdate_dd = profile["birthdate"][:2]
    birthdate_mm = profile["birthdate"][2:4]
    guardian_birthdate_yy = profile["guardian_birthdate"][-2:]
    guardian_birthdate_yyy = profile["guardian_birthdate"][-3:]
    guardian_birthdate_yyyy = profile["guardian_birthdate"][-4:]
    guardian_birthdate_xd = profile["guardian_birthdate"][1:2]
    guardian_birthdate_xm = profile["guardian_birthdate"][3:4]
    guardian_birthdate_dd = profile["guardian_birthdate"][:2]
    guardian_birthdate_mm = profile["guardian_birthdate"][2:4]
    girlfriend_birthdate_yy = profile["girlfriend_birthdate"][-2:]
    girlfriend_birthdate_yyy = profile["girlfriend_birthdate"][-3:]
    girlfriend_birthdate_yyyy = profile["girlfriend_birthdate"][-4:]
    girlfriend_birthdate_xd = profile["girlfriend_birthdate"][1:2]
    girlfriend_birthdate_xm = profile["girlfriend_birthdate"][3:4]
    girlfriend_birthdate_dd = profile["girlfriend_birthdate"][:2]
    girlfriend_birthdate_mm = profile["girlfriend_birthdate"][2:4]
    nameup = profile["name"].title()
    surnameup = profile["surname"].title()
    nickup = profile["nick"].title()
    guardian_nameup = profile["guardian_name"].title()
    guardian_nickup = profile["guardian_nick"].title()
    girlfriend_nameup = profile["girlfriend_name"].title()
    girlfriend_nickup = profile["girlfriend_nick"].title()
    petup = profile["pet"].title()
    kidsup = profile["kids"].title()
    numberup = profile["number"].title()
    emailup = profile["email"].title()
    companyup = profile["company"].title()
    wordsup = []
    wordsup = list(map(str.title, profile["words"]))
    word = profile["words"] + wordsup
    rev_name = profile["name"][::-1]
    rev_nameup = nameup[::-1]
    rev_nick = profile["nick"][::-1]
    rev_nickup = nickup[::-1]
    rev_guardian_name = profile["guardian_name"][::-1]
    rev_guardian_nameup = guardian_nameup[::-1]
    rev_girlfriend_name = profile["girlfriend_name"][::-1]
    rev_girlfriend_nameup = girlfriend_nameup[::-1]
    reverse = [
        rev_name,
        rev_nameup,
        rev_nick,
        rev_nickup,
        rev_guardian_name,
        rev_guardian_nameup,
        rev_girlfriend_name,
        rev_girlfriend_nameup,
    ]
    rev_n = [rev_name, rev_nameup, rev_nick, rev_nickup]
    rev_w = [rev_guardian_name, rev_guardian_nameup]
    rev_k = [rev_girlfriend_name, rev_girlfriend_nameup]
    bds = [
        birthdate_yy,
        birthdate_yyy,
        birthdate_yyyy,
        birthdate_xd,
        birthdate_xm,
        birthdate_dd,
        birthdate_mm,
    ]
    bdss = []

    for bds1 in bds:
        bdss.append(bds1)
        for bds2 in bds:
            if bds.index(bds1) != bds.index(bds2):
                bdss.append(bds1 + bds2)
                for bds3 in bds:
                    if (
                        bds.index(bds1) != bds.index(bds2)
                        and bds.index(bds2) != bds.index(bds3)
                        and bds.index(bds1) != bds.index(bds3)
                    ):
                        bdss.append(bds1 + bds2 + bds3)
    wbds = [guardian_birthdate_yy, guardian_birthdate_yyy, guardian_birthdate_yyyy,
            guardian_birthdate_xd, guardian_birthdate_xm, guardian_birthdate_dd, guardian_birthdate_mm]
    wbdss = []
    for wbds1 in wbds:
        wbdss.append(wbds1)
        for wbds2 in wbds:
            if wbds.index(wbds1) != wbds.index(wbds2):
                wbdss.append(wbds1 + wbds2)
                for wbds3 in wbds:
                    if (
                        wbds.index(wbds1) != wbds.index(wbds2)
                        and wbds.index(wbds2) != wbds.index(wbds3)
                        and wbds.index(wbds1) != wbds.index(wbds3)
                    ):
                        wbdss.append(wbds1 + wbds2 + wbds3)
    kbds = [girlfriend_birthdate_yy, girlfriend_birthdate_yyy, girlfriend_birthdate_yyyy,
            girlfriend_birthdate_xd, girlfriend_birthdate_xm, girlfriend_birthdate_dd, girlfriend_birthdate_mm]
    kbdss = []
    for kbds1 in kbds:
        kbdss.append(kbds1)
        for kbds2 in kbds:
            if kbds.index(kbds1) != kbds.index(kbds2):
                kbdss.append(kbds1 + kbds2)
                for kbds3 in kbds:
                    if (
                        kbds.index(kbds1) != kbds.index(kbds2)
                        and kbds.index(kbds2) != kbds.index(kbds3)
                        and kbds.index(kbds1) != kbds.index(kbds3)
                    ):
                        kbdss.append(kbds1 + kbds2 + kbds3)
    combination_naac = [profile["pet"], petup, profile["email"], emailup, profile["company"],
                 companyup, profile["kids"], kidsup, profile["number"], numberup,]
    combination_na = [
        profile["name"],
        profile["surname"],
        profile["nick"],
        nameup,
        surnameup,
        nickup,
    ]
    combination_naw = [
        profile["guardian_name"],
        profile["guardian_nick"],
        guardian_nameup,
        guardian_nickup,
        profile["surname"],
        surnameup,
    ]
    combination_nak = [
        profile["girlfriend_name"],
        profile["girlfriend_nick"],
        girlfriend_nameup,
        girlfriend_nickup,
        profile["surname"],
        surnameup,
    ]
    combination_naa = []
    for combination_na1 in combination_na:
        combination_naa.append(combination_na1)
        for combination_na2 in combination_na:
            if combination_na.index(combination_na1) != combination_na.index(combination_na2) and combination_na.index(
                combination_na1.title()
            ) != combination_na.index(combination_na2.title()):
                combination_naa.append(combination_na1 + combination_na2)
    combination_naaw = []
    for combination_na1 in combination_naw:
        combination_naaw.append(combination_na1)
        for combination_na2 in combination_naw:
            if combination_naw.index(combination_na1) != combination_naw.index(combination_na2) and combination_naw.index(
                combination_na1.title()
            ) != combination_naw.index(combination_na2.title()):
                combination_naaw.append(combination_na1 + combination_na2)
    combination_naak = []
    for combination_na1 in combination_nak:
        combination_naak.append(combination_na1)
        for combination_na2 in combination_nak:
            if combination_nak.index(combination_na1) != combination_nak.index(combination_na2) and combination_nak.index(
                combination_na1.title()
            ) != combination_nak.index(combination_na2.title()):
                combination_naak.append(combination_na1 + combination_na2)
    combination_ = {}
    combination_[1] = list(combine_strings(combination_naa, bdss))
    combination_[1] += list(combine_strings(combination_naa, bdss, "_"))
    combination_[2] = list(combine_strings(combination_naaw, wbdss))
    combination_[2] += list(combine_strings(combination_naaw, wbdss, "_"))
    combination_[3] = list(combine_strings(combination_naak, kbdss))
    combination_[3] += list(combine_strings(combination_naak, kbdss, "_"))
    combination_[4] = list(combine_strings(combination_naa, years))
    combination_[4] += list(combine_strings(combination_naa, years, "_"))
    combination_[5] = list(combine_strings(combination_naac, years))
    combination_[5] += list(combine_strings(combination_naac, years, "_"))
    combination_[6] = list(combine_strings(combination_naaw, years))
    combination_[6] += list(combine_strings(combination_naaw, years, "_"))
    combination_[7] = list(combine_strings(combination_naak, years))
    combination_[7] += list(combine_strings(combination_naak, years, "_"))
    combination_[8] = list(combine_strings(word, bdss))
    combination_[8] += list(combine_strings(word, bdss, "_"))
    combination_[9] = list(combine_strings(word, wbdss))
    combination_[9] += list(combine_strings(word, wbdss, "_"))
    combination_[10] = list(combine_strings(word, kbdss))
    combination_[10] += list(combine_strings(word, kbdss, "_"))
    combination_[11] = list(combine_strings(word, years))
    combination_[11] += list(combine_strings(word, years, "_"))
    combination_[12] = [""]
    combination_[13] = [""]
    combination_[14] = [""]
    combination_[15] = [""]
    combination_[16] = [""]
    combination_[21] = [""]
    if profile["randnum"] == "y":

        combination_[12] = list(concatenate_strings(word, num_from, num_to))
        combination_[13] = list(concatenate_strings(combination_naa, num_from, num_to))
        combination_[14] = list(concatenate_strings(combination_naac, num_from, num_to))
        combination_[15] = list(concatenate_strings(combination_naaw, num_from, num_to))
        combination_[16] = list(concatenate_strings(combination_naak, num_from, num_to))
        combination_[21] = list(concatenate_strings(reverse, num_from, num_to))
    combination_[17] = list(combine_strings(reverse, years))
    combination_[17] += list(combine_strings(reverse, years, "_"))
    combination_[18] = list(combine_strings(rev_w, wbdss))
    combination_[18] += list(combine_strings(rev_w, wbdss, "_"))
    combination_[19] = list(combine_strings(rev_k, kbdss))
    combination_[19] += list(combine_strings(rev_k, kbdss, "_"))
    combination_[20] = list(combine_strings(rev_n, bdss))
    combination_[20] += list(combine_strings(rev_n, bdss, "_"))
    komb001 = [""]
    komb002 = [""]
    komb003 = [""]
    komb004 = [""]
    komb005 = [""]
    komb006 = [""]
    if len(profile["spechars"]) > 0:
        komb001 = list(combine_strings(combination_naa, profile["spechars"]))
        komb002 = list(combine_strings(combination_naac, profile["spechars"]))
        komb003 = list(combine_strings(combination_naaw, profile["spechars"]))
        komb004 = list(combine_strings(combination_naak, profile["spechars"]))
        komb005 = list(combine_strings(word, profile["spechars"]))
        komb006 = list(combine_strings(reverse, profile["spechars"]))

        komb00111 = list(combine_strings(profile["spechars"], combination_naa))
        komb00222 = list(combine_strings(profile["spechars"], combination_naac))
        komb00333 = list(combine_strings(profile["spechars"], combination_naaw))
        komb00444 = list(combine_strings(profile["spechars"], combination_naak))
        komb00555 = list(combine_strings(profile["spechars"], word))
        komb00666 = list(combine_strings(profile["spechars"], reverse))
    print("[+] Sorting list and removing duplicates...")
    komb_unique = {}
    for i in range(1, 22):
        komb_unique[i] = list(dict.fromkeys(combination_[i]).keys())
    komb_unique01 = list(dict.fromkeys(combination_naa).keys())
    komb_unique02 = list(dict.fromkeys(combination_naac).keys())
    komb_unique03 = list(dict.fromkeys(combination_naaw).keys())
    komb_unique04 = list(dict.fromkeys(combination_naak).keys())
    komb_unique05 = list(dict.fromkeys(word).keys())
    komb_unique07 = list(dict.fromkeys(komb001).keys())
    komb_unique08 = list(dict.fromkeys(komb002).keys())
    komb_unique09 = list(dict.fromkeys(komb003).keys())
    komb_unique010 = list(dict.fromkeys(komb004).keys())
    komb_unique011 = list(dict.fromkeys(komb005).keys())
    komb_unique012 = list(dict.fromkeys(komb006).keys())
    komb_unique0711 = list(dict.fromkeys(komb00111).keys())
    komb_unique0811 = list(dict.fromkeys(komb00222).keys())
    komb_unique0911 = list(dict.fromkeys(komb00333).keys())
    komb_unique01011 = list(dict.fromkeys(komb00444).keys())
    komb_unique01111 = list(dict.fromkeys(komb00555).keys())
    komb_unique01211 = list(dict.fromkeys(komb00666).keys())
    uniqlist = (
        bdss
        + wbdss
        + kbdss
        + reverse
        + komb_unique01
        + komb_unique02
        + komb_unique03
        + komb_unique04
        + komb_unique05
    )
    for i in range(1, 21):
        uniqlist += komb_unique[i]
    uniqlist += (
        komb_unique07
        + komb_unique08
        + komb_unique09
        + komb_unique010
        + komb_unique011
        + komb_unique012
        + komb_unique0711
        + komb_unique0811
        + komb_unique0911
        + komb_unique01011
        + komb_unique01111
        + komb_unique01211
    )
    unique_lista = list(dict.fromkeys(uniqlist).keys())
    unique_leet = []
    print("fgo[asdjfgopdhsjngihsdhigidgsgdestroyer", unique_leet)
    if profile["leetmode"] == "y":

        for (
            x
        ) in (
            unique_lista
        ):
            x = apply_leet_conversion(x)
            unique_leet.append(x)
            unique_leet.insert(0, x)
    unique_list = unique_lista + unique_leet

    unique_list_finished = []

    unique_list_finished = [
        x
        for x in unique_list
        if len(x) < CONFIG["global"]["wcto"] and len(x) > CONFIG["global"]["wcfrom"]
    ]

    save_to_file("passwords.txt", unique_list_finished)

    return unique_list_finished


def main():
    """Command-line interface to the password generation utility"""
    read_configuration(os.path.join(os.path.dirname(
        os.path.realpath(__file__)), "destroyer.cfg"))

    try:
        interactive_input()
    except Exception as e:
        pass

    remove_gap = input(
        "\n\n>Do you want to Remove spaces within each line? Y/[N]: ").lower()
    if remove_gap == "y":
        def remove_space_and_duplicates(text):
            lines = text.split("\n")
            # Remove spaces within each line
            lines = [line.replace(" ", "") for line in lines]
            # Remove duplicate lines (case-sensitive)
            unique_lines = list(dict.fromkeys(lines))
            return "\n".join(unique_lines)

        # Read the content of the file
        with open("passwords.txt", "r") as file:
            text = file.read()

        # Apply the function to the text
        modified_text = remove_space_and_duplicates(text)

        # Write the modified text back to the file
        with open("passwords_verify.txt", "w") as file:
            file.write(modified_text)

    filename = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), "passwords_verify.txt")

    f = open(filename, "r")
    lines = 0
    for line in f:
        lines += 1
    f.close()
    print("\n\n[+] Saving dictionary to \033[1;31m" + filename +
          "\033[1;m, counting \033[1;31m" + str(lines) + " words.\033[1;m")
    print("[+] Now load your pistolero with \033[1;31m" + filename +
          "\033[1;m and shoot! Good luck!")

    remove = input(
        "\n\nDo you want to remove passwords.txt file? (Y/N): ").lower()
    if remove == 'y':
        try:
            file_path = "passwords.txt"
            os.remove(file_path)
            print(
                f"\n [+]The file '{file_path}' has been deleted successfully...\n")
        except FileNotFoundError:
            print(f"File '{file_path}' not found.")

    inspect = input("> Hyperspeed Print? (Y/N) : ").lower()
    if inspect == "y":
        try:
            with open(filename, "r+") as wlist:
                data = wlist.readlines()
                for line in data:
                    print("\033[1;32m[" + filename + "] \033[1;33m" + line)
                    os.system("clear")
        except Exception as e:
            print("[ERROR]: " + str(e))
    else:
        pass
   

if __name__ == "__main__":
    cProfile.run("main()")


