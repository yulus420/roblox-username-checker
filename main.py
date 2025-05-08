import os
import ctypes
import time
import random
import string
import asyncio
import aiohttp
from colorama import Fore, Style, init

init(autoreset=True)

ROBLOX_VALIDATE_URL = "https://auth.roblox.com/v1/usernames/validate?Username={}&Birthday=2000-01-01"
VALID_FILE = "valid.txt"
REQUEST_DELAY = 0.05
START_TIME = time.time()

def set_console_title(title):
    ctypes.windll.kernel32.SetConsoleTitleW(title)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

BANNER = Fore.MAGENTA + r"""
                     /$$                    
                    | $$                    
 /$$   /$$ /$$   /$$| $$ /$$   /$$  /$$$$$$$
| $$  | $$| $$  | $$| $$| $$  | $$ /$$_____/
| $$  | $$| $$  | $$| $$| $$  | $$|  $$$$$$ 
| $$  | $$| $$  | $$| $$| $$  | $$ \____  $$
|  $$$$$$$|  $$$$$$/| $$|  $$$$$$/ /$$$$$$$/
 \____  $$ \______/ |__/ \______/ |_______/ 
 /$$  | $$                                  
|  $$$$$$/                                  
 \______/                                   
""" + Style.RESET_ALL + Fore.CYAN + "\nRoblox Username Checker by yulus\n" + Style.RESET_ALL

stats = {
    "valid": 0,
    "taken": 0,
    "censored": 0,
    "unknown": 0,
    "total": 0,
    "checked": 0,
    "times": []
}

async def check_username(session, username):
    url = ROBLOX_VALIDATE_URL.format(username)
    try:
        start_time = time.time()
        async with session.get(url) as response:
            if response.status == 429:
                set_console_title("Rate limited... retrying in 5s")
                await asyncio.sleep(5)
                return await check_username(session, username)

            if response.status != 200:
                print(Fore.RED + f"[HTTP {response.status}] {username}")
                stats["unknown"] += 1
                return

            data = await response.json()
            code = data.get("code")
            stats["checked"] += 1

            elapsed_time = time.strftime("%H:%M:%S", time.gmtime(time.time() - START_TIME))

            if stats["checked"] > 0 and len(stats["times"]) > 0:
                avg_time_per_request = sum(stats["times"]) / len(stats["times"])
            else:
                avg_time_per_request = 0.1

            remaining_time_seconds = (stats["total"] - stats["checked"]) * avg_time_per_request
            remaining_time = time.strftime("%H:%M:%S", time.gmtime(remaining_time_seconds))

            progress_percentage = (stats["checked"] / stats["total"]) * 100
            set_console_title(f"Progress: {progress_percentage:.2f}% | Checked {stats['checked']}/{stats['total']} | Valid: {stats['valid']} | Elapsed: {elapsed_time} | Remaining: {remaining_time}")

            stats["times"].append(time.time() - start_time)

            if code == 0:
                stats["valid"] += 1
                print(Fore.GREEN + f"[VALID]    {username}")
                with open(VALID_FILE, "a") as f:
                    f.write(username + "\n")
            elif code == 1:
                stats["taken"] += 1
                print(Fore.LIGHTWHITE_EX + f"[TAKEN]    {username}")
            elif code == 2:
                stats["censored"] += 1
                print(Fore.RED + f"[CENSORED] {username}")
            else:
                stats["unknown"] += 1
                print(Fore.BLUE + f"[UNKNOWN:{code}] {username}")

    except Exception as e:
        print(Fore.MAGENTA + f"[ERROR]    {username}: {e}")
        stats["unknown"] += 1

    await asyncio.sleep(REQUEST_DELAY)

def generate_random_usernames(length, count, use_digits=True):
    if use_digits:
        charset = string.ascii_letters + string.digits
    else:
        charset = string.ascii_letters
    return [''.join(random.choices(charset, k=length)) for _ in range(count)]

async def run_check(usernames):
    stats.update({"valid": 0, "taken": 0, "censored": 0, "unknown": 0, "checked": 0, "total": len(usernames)})
    
    start_time = time.time()  

    async with aiohttp.ClientSession() as session:
        for username in usernames:
            await check_username(session, username)

    elapsed_time = time.time() - start_time
    elapsed_formatted = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
    avg_time_per_username = elapsed_time / stats["checked"] if stats["checked"] > 0 else 0

    set_console_title(f"Valid: {stats['valid']} | Taken: {stats['taken']} | Elapsed: {elapsed_formatted}")

    print(Fore.BLUE + f"\nDone!\nChecked: {stats['checked']} | Valid: {stats['valid']} | Taken: {stats['taken']} | Censored: {stats['censored']} | Errors: {stats['unknown']}")
    print(Fore.YELLOW + f"Time taken: {elapsed_formatted} ({elapsed_time:.2f} seconds)" + Style.RESET_ALL)
    print(Fore.YELLOW + f"Average time per username: {avg_time_per_username:.2f} seconds" + Style.RESET_ALL)

    input(Fore.CYAN + "\nPress Enter to return to the menu..." + Style.RESET_ALL)
    clear_screen()  
    print(BANNER)

def print_menu(current_delay):
    print(Fore.BLUE + "\n=== MENU ===" + Style.RESET_ALL)
    print("1 - Check from usernames.txt")
    print("2 - Generate random usernames")
    print(f"3 - Change delay (current: {current_delay:.2f}s)")
    print("4 - Exit")

async def generate_username_options():
    print(Fore.CYAN + "\nChoose the type of random username:")
    print("1 - Only letters")
    print("2 - Letters + digits")

    choice = input(Fore.YELLOW + "Choose an option: " + Style.RESET_ALL)

    if choice == "1":
        return False
    elif choice == "2":
        return True
    else:
        print(Fore.RED + "Invalid option. Please choose 1 or 2.")
        return await generate_username_options()
    
async def main():
    global REQUEST_DELAY
    clear_screen()
    print(BANNER)

    while True:
        print_menu(REQUEST_DELAY)
        choice = input(Fore.CYAN + "Choose an option: " + Style.RESET_ALL)

        if choice == "1":
            clear_screen()
            if not os.path.exists("usernames.txt"):
                print(Fore.RED + "File 'usernames.txt' not found!")
                continue
            with open("usernames.txt", "r") as f:
                usernames = f.read().splitlines()

            clear_choice = input(Fore.YELLOW + "Do you want to clear 'valid.txt' before checking? (y/n): " + Style.RESET_ALL).lower()
            if clear_choice == 'y':
                open(VALID_FILE, "w").close()
                print(Fore.GREEN + "'valid.txt' has been cleared.")
                await asyncio.sleep(1)

            await run_check(usernames)

        elif choice == "2":
            clear_screen()
            try:
                length = int(input(Fore.CYAN + "Username length: " + Style.RESET_ALL))
                count = int(input(Fore.CYAN + "How many to generate: " + Style.RESET_ALL))

                use_digits = await generate_username_options()
                usernames = generate_random_usernames(length, count, use_digits)

                clear_choice = input(Fore.YELLOW + "Do you want to clear 'valid.txt' before checking? (y/n): " + Style.RESET_ALL).lower()
                if clear_choice == 'y':
                    open(VALID_FILE, "w").close()
                    print(Fore.GREEN + "'valid.txt' has been cleared.")
                    await asyncio.sleep(1)

                clear_screen()
                await run_check(usernames)

            except ValueError:
                print(Fore.RED + "Invalid input!")

        elif choice == "3":
            try:
                delay = float(input(Fore.CYAN + "New delay (e.g. 0.05): " + Style.RESET_ALL))
                REQUEST_DELAY = max(0.01, delay)
                print(Fore.GREEN + f"Delay set to {REQUEST_DELAY:.2f}s")
                await asyncio.sleep(1.5)
                clear_screen()
            except ValueError:
                print(Fore.RED + "Invalid number.")

        elif choice == "4":
            print(Fore.GREEN + "Goodbye!")
            break
        else:
            print(Fore.RED + "Invalid option.")

if __name__ == "__main__":
    asyncio.run(main())

