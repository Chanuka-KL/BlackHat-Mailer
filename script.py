import random
import string
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import queue
from termcolor import colored, cprint
from tabulate import tabulate
import logging
import csv
import json
import time

# Logging setup
logging.basicConfig(filename="blackhat_mailer.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Styled Banner
def display_banner():
    cprint(r"""

                                                            
  ____  _            _    _   _       _     __  __       _ _           
 | __ )| | __ _  ___| | _| | | | __ _| |_  |  \/  | __ _(_) | ___ _ __ 
 |  _ \| |/ _` |/ __| |/ / |_| |/ _` | __| | |\/| |/ _` | | |/ _ \ '__|
 | |_) | | (_| | (__|   <|  _  | (_| | |_  | |  | | (_| | | |  __/ |   
 |____/|_|\__,_|\___|_|\_\_| |_|\__,_|\__| |_|  |_|\__,_|_|_|\___|_|   
                                                                                                                                   
                                                   
 
    """, "red", attrs=["bold"])
    cprint("\nWelcome to BlackHat Mailer - https://github.com/Chanuka-KL\n", "cyan", attrs=["bold"])



# Function to generate a random string of letters, digits, and special characters
def generate_random_string(length, use_special_chars=False):
    characters = string.ascii_letters + string.digits
    if use_special_chars:
        characters += "!@#$%^&*()-=_+[]{}|;:,.<>?/"
    return ''.join(random.choice(characters) for _ in range(length))

# Function to generate a Gmail-style username
def generate_gmail_username(existing_usernames):
    first_names = ['john', 'alice', 'bob', 'charlie', 'emma', 'sophia', 'michael', 'david', 'james', 'olivia', 'noah']
    last_names = ['smith', 'johnson', 'brown', 'williams', 'jones', 'miller', 'davis', 'clark', 'taylor', 'lee', 'walker']
    while True:
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        username = f"{first_name}{random.randint(1, 999)}{random.choice(['.', '_', ''])}{last_name}{random.randint(1, 99)}"
        username = username.lower()
        if username not in existing_usernames:  # Ensure uniqueness
            existing_usernames.add(username)
            break
    return username

# Function to generate a secure random password
def generate_gmail_password(length=16):
    return generate_random_string(length, use_special_chars=True)

# Function to generate Gmail credentials and store them in the queue
def generate_gmail_credentials(email_queue, existing_usernames):
    try:
        username = generate_gmail_username(existing_usernames)
        password = generate_gmail_password()
        email = f"{username}@gmail.com"
        email_queue.put((email, password))
        logging.info(f"Generated: {email}")
    except Exception as e:
        logging.error(f"Error generating email: {e}")

# Function to generate multiple credentials using multithreading
def generate_multiple_credentials(num_emails):
    email_queue = queue.Queue()
    existing_usernames = set()
    with tqdm(total=num_emails, desc=colored("Generating Emails", "green"), unit="email") as pbar:
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(generate_gmail_credentials, email_queue, existing_usernames) for _ in range(num_emails)]
            for future in futures:
                future.result()
                pbar.update(1)
    credentials = []
    while not email_queue.empty():
        credentials.append(email_queue.get())
    return credentials

# Function to save credentials to CSV, JSON, or TXT format
def save_credentials(credentials, file_format="csv"):
    file_name = f"credentials.{file_format}"
    if file_format == "csv":
        with open(file_name, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Email Address", "Password"])
            writer.writerows(credentials)
    elif file_format == "json":
        with open(file_name, "w") as file:
            json.dump([{"email": email, "password": password} for email, password in credentials], file, indent=4)
    elif file_format == "txt":
        with open(file_name, "w") as file:
            for email, password in credentials:
                file.write(f"{email}:{password}\n")
    cprint(f"\nCredentials saved to {file_name}", "green")

# Menu-driven function for user interactions
def main():
    display_banner()
    while True:
        print(colored("\nMain Menu", "cyan", attrs=["bold"]))
        print(colored("[1]. Generate Gmail Credentials", "blue"))
        print(colored("[2]. Save Credentials (CSV/JSON/TXT)", "blue"))
        print(colored("[3]. View Last Generated Credentials", "blue"))
        print(colored("[4]. Exit", "red"))

        choice = input(colored("\nEnter your choice: ", "yellow")).strip()

        if choice == "1":
            try:
                num_emails = int(input(colored("Enter the number of Gmail credentials to generate: ", "yellow")))
                global credentials
                start_time = time.time()
                credentials = generate_multiple_credentials(num_emails)
                end_time = time.time()
                print(colored(f"\nGenerated {num_emails} credentials in {end_time - start_time:.2f} seconds", "green"))
            except ValueError:
                print(colored("Invalid input! Please enter a valid number.", "red"))
        elif choice == "2":
            if 'credentials' in globals():
                file_format = input(colored("Enter file format (csv/json/txt): ", "yellow")).strip().lower()
                if file_format in ["csv", "json", "txt"]:
                    save_credentials(credentials, file_format)
                else:
                    print(colored("Invalid format! Please choose csv, json, or txt.", "red"))
            else:
                print(colored("No credentials generated yet!", "red"))
        elif choice == "3":
            if 'credentials' in globals():
                table_data = [(email, password) for email, password in credentials]
                headers = [colored("Email Address", "cyan"), colored("Password", "cyan")]
                table_output = tabulate(table_data, headers=headers, tablefmt="fancy_grid")
                print(colored("\nLast Generated Credentials:", "yellow"))
                print(table_output)
            else:
                print(colored("No credentials generated yet!", "red"))
        elif choice == "4":
            cprint("Exiting... Thank you for using BlackHat Mailer!", "green", attrs=["bold"])
            break
        else:
            print(colored("Invalid choice! Please try again.", "red"))

if __name__ == "__main__":
    main()
