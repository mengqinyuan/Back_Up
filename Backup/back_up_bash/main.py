# main.py
from back_up_main.back_up import BackUp

print("Welcome to use back up. More information: https://github.com/mengqinyuan/backup")

source_dir = input("Please input the source directory: ")
destination_dir = input("Please input the destination directory: ")

Back_Up = BackUp(source_dir, destination_dir)

is_remove_unzipped_folder = input("Do you want to remove the unzipped folder? (y/n): ")
if is_remove_unzipped_folder == 'y':
    is_remove_unzipped_folder = True
else:
    is_remove_unzipped_folder = False

is_zip = input("Do you want to zip the folder? (y/n): ")
if is_zip == 'y':
    is_zip = True
else:
    is_zip = False

is_compare_size = input("Do you want to compare the size of the folder: [Make sure you have enough space. Compare may cost some times] (y/n):")

if is_compare_size == 'y':
    is_compare_size = True
else:
    is_compare_size = False

Back_Up.backup(is_remove_unzipped_folder, is_zip, is_compare_size)
