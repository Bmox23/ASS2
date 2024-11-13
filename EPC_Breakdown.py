import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import subprocess
import cv2
from pyzbar import pyzbar
import time
import threading

# Creating the main window after boot screen
root = tk.Tk()
root.title("MCC Encoding App")
root.state('zoomed')

# Function to decode barcode types
def decode_barcode_type(barcode):
    type_map = {
        'EAN13': 'EAN-13',
        'EAN8': 'EAN-8',
        'UPCA': 'UPC-A',
        'UPCE': 'UPC-E',
        'CODE39': 'Code 39',
        'CODE128': 'Code 128',
        'ITF': 'Interleaved 2 of 5',
        'QRCODE': 'QR Code',
        'PDF417': 'PDF417',
        'DATAMATRIX': 'Data Matrix',
        'AZTEC': 'Aztec Code',
        'CODABAR': 'Codabar',
        'RSS14': 'GS1 DataBar',
        'RSS_EXPANDED': 'GS1 DataBar Expanded'
    }
    return type_map.get(barcode.type, 'Unknown')

# Function to scan barcode using the device's camera
def scan_barcode():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        result_label.config(text="Error: Unable to access the camera.")
        return

    result_label.config(text="Scanning... Press 'q' to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            result_label.config(text="Error: Failed to capture image.")
            break

        barcodes = pyzbar.decode(frame)
        for barcode in barcodes:
            barcode_data = barcode.data.decode('utf-8')
            barcode_type = decode_barcode_type(barcode)
            result_label.config(text=f"Detected {barcode_type} barcode: {barcode_data}")
            cap.release()
            cv2.destroyAllWindows()
            return

        cv2.imshow('Barcode Scanner - Press "q" to quit', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    result_label.config(text="No barcode detected.")

# Function to be executed when an option is selected
def on_select(event):
    global result_label  # Declare result_label as a global variable
    root.iconify()
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
        scan_button = tk.Button(new_window, text="Scan Barcode", command=scan_barcode, bg="blue", fg="white")
        scan_button.pack(pady=10)
        result_label = tk.Label(new_window, text="", justify="left")
        result_label.pack(pady=10)
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
