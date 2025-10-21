import os
from pathlib import Path
import sys

from lib.plaza.crypto import HashDB, SwishCrypto
from lib.plaza.types import HashDBKeys, UserDataSaveDataAccessor, CopyDressUpSaveData

SRC_PATH = Path(__file__).parent

save_file_magic = bytes([
    0x17, 0x2D, 0xBB, 0x06, 0xEA
])

def main():
    print("PLZA Quick Save Editor")
    print()
    file_path = input("Enter File Path: ")

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)

    with open(file_path, "rb") as f:
        data = f.read()

    if not data.startswith(save_file_magic):
        print("File is not a PLZA save file")
        sys.exit(1)

    try:
        blocks = SwishCrypto.decrypt(data)
    except Exception as e:
        print(f"Error decrypting save file: {e}")
        sys.exit(1)

    print(f"> Decrypted {len(blocks)} Blocks. <")
    hash_db = HashDB(blocks)

    core_data = UserDataSaveDataAccessor.from_bytes(hash_db[HashDBKeys.CoreData].data)

    def menu_loop():
        print(f"""
    {core_data}
    Options (Input the option number):
        1: Trainer ID
        2: Gender (Will reset your current clothes)
        3: Quit
    """)

        option = input(">>> ").strip()

        if option not in ["1", "2", "3"]:
            print("Invalid Option Picked!")

        if option == "3": return
        if option == "2":
            core_data.set_sex(int(not core_data.get_sex()))
            if core_data.get_sex() == 0:
                data_path = SRC_PATH / "valid_blocks" / "dressup_male_data.bin"
            else:
                data_path = SRC_PATH / "valid_blocks" / "dressup_female_data.bin"
            with open(data_path, "rb") as data_file:
                hash_db[HashDBKeys.DressUp].change_data(data_file.read())
            print(f"Gender Swapped to {'male' if not core_data.get_sex() else 'female'}!")
            input("> Press Enter to return to the Menu <")
            return menu_loop()
        if option == "1":
            print(f"Current TID {core_data.get_id()}")
            print(f"What TID do you want?")
            goal_tid = input(">>> ")
            if not goal_tid.isnumeric():
                input("Not a numeric TID, returning to main loop on Enter")
                return menu_loop()
            core_data.set_id(int(goal_tid))
            return menu_loop()

    menu_loop()

    hash_db[HashDBKeys.CoreData].change_data(core_data.to_bytes())

    # * Determine output file path
    output_path = file_path + "_modified"

    print(f"Writing Modified file to {output_path}")

    with open(output_path, "wb") as f:
        f.write(SwishCrypto.encrypt(hash_db.blocks))

    print(f"Wrote File, Exiting")


if __name__ == "__main__":
    main()
