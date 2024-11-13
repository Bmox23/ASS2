import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import subprocess
import time

# Function to display the boot screen with progress bar
def boot_screen():
    boot = tk.Toplevel()
    boot.title("MCC Encoding App - Booting")
    boot.state('zoomed')

    # Adding company logo
    image_path = r"Z:\3 Encoding and Printing Files\Fonts and Images\Images\Company\MCC.png"
    logo_image = Image.open(image_path)
    logo_image = logo_image.resize((200, 100), Image.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = tk.Label(boot, image=logo_photo)
    logo_label.image = logo_photo  # Keep a reference
    logo_label.pack(pady=20)

    # Adding progress bar
    progress = ttk.Progressbar(boot, orient="horizontal", length=300, mode="determinate")
    progress.pack(pady=20)

    # Update progress bar
    for i in range(101):
        progress['value'] = i
        boot.update_idletasks()
        time.sleep(0.02)  # Simulate loading delay

    boot.destroy()

# Creating the main window after boot screen
root = tk.Tk()
root.title("MCC Encoding App")
root.state('zoomed')

# Display boot screen
boot_screen()

# Function to be executed when an option is selected
def on_select(event):
    root.withdraw()
    selection = combo_box.get()
    new_window = tk.Toplevel()
    new_window.title(selection)
    new_window.state('zoomed')
    header_label = tk.Label(new_window, text=selection, font=("Helvetica", 16))
    header_label.pack(pady=20)

    if selection == "EPC Breakdown":
        # Adding an input field for the user to enter an EPC
        epc_input_label = tk.Label(new_window, text="Enter EPC (in Hex, 24 characters):")
        epc_input_label.pack(pady=5)
        epc_input_box = tk.Entry(new_window, width=40)
        epc_input_box.pack(pady=10)

        # Adding a button to perform the EPC breakdown
        def perform_epc_breakdown():
            epc_value = epc_input_box.get()
            if len(epc_value) != 24:
                result_label.config(text="Invalid EPC length. EPC must be 24 hexadecimal characters.")
                return
            try:
                # Convert hex EPC to binary
                epc_binary = bin(int(epc_value, 16))[2:].zfill(96)  # Assuming 96-bit EPC

                # Extract fields based on bit lengths and convert to decimal
                header = int(epc_binary[0:8], 2)
                filter_value = int(epc_binary[8:11], 2)
                partition = int(epc_binary[11:14], 2)
                company_prefix = int(epc_binary[14:38], 2)
                item_reference = int(epc_binary[38:58], 2)
                serial = int(epc_binary[58:96], 2)

                # Calculate the final UPC by combining Company Prefix and Item Reference
                combined_upc = f"{company_prefix}{item_reference}"

                # Calculate the check digit using the provided check digit algorithm
                def calculate_check_digit(upc):
                    upc_digits = [int(digit) for digit in upc]
                    total_sum = 0

                    # Multiply value of each position by 3 or 1 depending on position
                    for idx, digit in enumerate(upc_digits):
                        if (idx + 1) % 2 == 0:  # Even positions (1-based index)
                            total_sum += digit * 1
                        else:  # Odd positions (1-based index)
                            total_sum += digit * 3

                    # Calculate the check digit
                    nearest_higher_multiple_of_ten = (10 - (total_sum % 10)) % 10
                    return nearest_higher_multiple_of_ten

                check_digit = calculate_check_digit(combined_upc)
                final_upc = f"{combined_upc}{check_digit}"

                # Display the breakdown
                breakdown_result = (
                    f"Header (8 bits): {header} (Binary: {epc_binary[0:8]})\n"
                    f"Filter (3 bits): {filter_value} (Binary: {epc_binary[8:11]})\n"
                    f"Partition (3 bits): {partition} (Binary: {epc_binary[11:14]})\n"
                    f"Company Prefix (24 bits): {company_prefix} (Binary: {epc_binary[14:38]})\n"
                    f"Item Reference (20 bits): {item_reference} (Binary: {epc_binary[38:58]})\n"
                    f"Serial (38 bits): {serial} (Binary: {epc_binary[58:96]})\n"
                    f"\nCheck Digit: {check_digit}\n"
                    f"\nFinal UPC: {final_upc}"
                )
                result_label.config(text=breakdown_result)
            except ValueError:
                result_label.config(text="Invalid EPC value. Please enter a valid hexadecimal string.")

        breakdown_button = tk.Button(new_window, text="Breakdown EPC", command=perform_epc_breakdown, bg="green", fg="white")
        breakdown_button.pack(pady=10)

        # Adding a label to display the results
        result_label = tk.Label(new_window, text="", justify="left")
        result_label.pack(pady=10)

    elif selection == "Bartender Info Verification":
        subprocess.Popen(["python", "Bartender_Info_Verification.py"])
    elif selection == "Barcode Verification":
        subprocess.Popen(["python", "Barcode_Verification.py"])
    elif selection == "UPC & Serial Breakdown":
        subprocess.Popen(["python", "UPC_Serial_Breakdown.py"])

# Adding label to the window
label = tk.Label(root, text="Select an Option from the Dropdown Menu:")
label.pack(pady=10)

# Creating a dropdown menu
options = ["EPC Breakdown", "Bartender Info Verification", "Barcode Verification", "UPC & Serial Breakdown"]
combo_box = ttk.Combobox(root, values=options, width=30)
combo_box.pack(pady=10)
combo_box.bind("<<ComboboxSelected>>", on_select)

# Running the main loop
root.mainloop()
