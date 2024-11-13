import tkinter as tk
import subprocess

# Function to perform EPC breakdown and UPC & Serial breakdown
def perform_epc_and_upc_serial_breakdown():
    epc_value = epc_input_box.get()
    if len(epc_value) != 24:
        epc_result_label.config(text="Invalid EPC length. EPC must be 24 hexadecimal characters.")
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
        combined_upc = str(company_prefix) + str(item_reference)

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
        final_upc = combined_upc + str(check_digit)

        # Display the breakdown
        breakdown_result = (
            "Header (8 bits): " + str(header) + "\n" +
            "Filter (3 bits): " + str(filter_value) + "\n" +
            "Partition (3 bits): " + str(partition) + "\n" +
            "Company Prefix (24 bits): " + str(company_prefix) + "\n" +
            "Item Reference (20 bits): " + str(item_reference) + "\n" +
            "Serial (38 bits): " + str(serial) + "\n" +
            "\nCheck Digit: " + str(check_digit) + "\n" +
            "\nFinal UPC: " + final_upc
        )
        epc_result_label.config(text=breakdown_result)
    except ValueError:
        epc_result_label.config(text="Invalid EPC value. Please enter a valid hexadecimal string.")


# Creating the main window
root = tk.Tk()
root.title("MCC Encoding App")
root.geometry("800x600")  # Open in windowed mode with default size

# Adding a Scrollbar to the main window
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)
canvas = tk.Canvas(main_frame)
scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
scrollable_frame = tk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# EPC and UPC & Serial Breakdown Section
epc_label = tk.Label(scrollable_frame, text="EPC & UPC/Serial Breakdown", font=("Helvetica", 16))
epc_label.pack(pady=10)
epc_input_label = tk.Label(scrollable_frame, text="Enter EPC (in Hex, 24 characters):")
epc_input_label.pack(pady=5)
epc_input_box = tk.Entry(scrollable_frame, width=40)
epc_input_box.pack(pady=10)
epc_breakdown_button = tk.Button(scrollable_frame, text="Breakdown EPC & Generate UPC/Serial", command=perform_epc_and_upc_serial_breakdown, bg="green", fg="white")
epc_breakdown_button.pack(pady=10)
epc_result_label = tk.Label(scrollable_frame, text="", justify="left")
epc_result_label.pack(pady=10)


# Running the main loop
root.mainloop()
