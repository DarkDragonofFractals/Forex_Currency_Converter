"""
This Forex (foreign exchange) online tool will convert funds from any national currency to
any other national currency, or from any national currency to any of the top ten crypto
currencies by market capitalization.  Conversions are without consideration to bank fees
or bank arbitrage across multiple currencies, and so it offers a 'base case' for conversion
of currencies without processing fees or bank forex arbitrage with your funds.
"""
# Import AI library for Python. This is now a LIVE call.
from ai import call_gpt

# Import Python modules.
import re
import os
import json
import sys
from datetime import datetime

# --- Helper Functions ---

def format_number(value, use_comma_separator):
    """Formats a float into a string with two decimal places, using a comma or period."""
    formatted = f"{value:.2f}"
    if use_comma_separator:
        return formatted.replace(".", ",")
    return formatted

def normalize_input(input_string):
    """Converts user entries to a standardized lowercase string for alias matching."""
    return input_string.lower().strip()

# --- Core Application Functions ---

def introduction():
    print( # Prints the introductory message for the user.
    "\nWELCOME TO THE FOREX CURRENCY CONVERTER\n\n\tThis is an online tool that will convert from any national currency to any national currency, and\n"
    "\tfrom any national currency to and from any of the top ten crypto currencies, in real time.  The\n"
    "\tcrypto currencies included (in order of market capitalization as of June 2025) are:\n\n"
    
    "\t\t (1) Bitcoin\n"
    "\t\t (2) Ethereum\n"
    "\t\t (3) Tether\n"
    "\t\t (4) XRP\n"
    "\t\t (5) Binance Coin\n"
    "\t\t (6) Solana\n"
    "\t\t (7) USD Coin\n"
    "\t\t (8) Dogecoin\n"
    "\t\t (9) Cardano\n"
    "\t\t(10) TRON\n\n"

    "\tYour printed results will include a date and time stamp for your records.\n\n"
    
    "\tConversions are without consideration to bank fees or bank arbitrage across multiple currencies,\n"
    "\tand so it offers a 'base case' for conversion of currencies without processing fees or bank forex\n"
    "\tarbitrage with your funds.\n"
    )

def load_currency_data(json_path):
    """Loads the currency dictionary from the specified JSON file."""
    try:
        with open(json_path, "r", encoding="utf-8") as file:
            print("\tInternational currency data loaded ...\n")
            return json.load(file)
    except FileNotFoundError:
        print(f"ERROR: JSON file not found at '{json_path}'.")
        sys.exit("Exiting program: critical data file not found.")
    except json.JSONDecodeError:
        print(f"ERROR: Could not decode JSON from '{json_path}'.")
        sys.exit("Exiting program: data file is corrupted.")

def get_currency_choice(prompt_message, currency_data):
    """
    Prompts the user for a currency and performs a smart search.
    1. Checks for a matching country name or alias (e.g., "china", "us").
    2. If no match, checks for a matching official ISO code (e.g., "USD", "JPY").
    """
    while True:
        user_input = input(prompt_message).strip()
        
        # 1. First, check if the user's input matches a country name or alias
        normalized_input = normalize_input(user_input)
        if normalized_input in currency_data:
            return currency_data[normalized_input]
            
        # 2. If no key matches, check if the input matches an official ISO code
        for country_data in currency_data.values():
            if user_input.upper() == country_data['iso']:
                return country_data

        # If no match is found after both checks
        print(
            f'\n\t\tWe could not find "{user_input}" as a country, alias, or ISO code.'
            f"\n\t\tPlease check the spelling and try again (e.g., United States, Japan, BTC).\n"
        )


def get_conversion_amount(currency_info):
    """Prompts the user for the amount of money to convert."""
    while True:
        amount_str = input(
            f"\nHow much in {currency_info['currency']} would you like to convert?"
            f"\n\tPlease enter ({currency_info['symbol']}): "
        )
        
        # Standardize number format
        use_comma_separator = "," in amount_str and "." not in amount_str
        cleaned_str = amount_str.replace(",", ".") if use_comma_separator else amount_str.replace(",", "")

        try:
            amount_float = float(cleaned_str)
            return amount_float, use_comma_separator
        except ValueError:
            print("\n\tInvalid number. Please enter a valid numeric value (e.g., 1500.50).")

def get_exchange_rates(curr_iso, target_iso):
    """
    Constructs a prompt and calls the AI for real-time exchange rates.
    """
    crypto_list = {'BTC', 'ETH', 'USDT', 'XRP', 'BNB', 'SOL', 'USDC', 'DOGE', 'ADA', 'TRX'}
    is_crypto = curr_iso in crypto_list or target_iso in crypto_list
    source_url = "coinmarketcap.com" if is_crypto else "ecb.europa.eu"
    
    comparison_currencies = ["USD", "GBP", "EUR", "JPY", "CNY"]

    prompt = (
        "Provide real-time exchange rates in the following strict format. "
        "Use 3-letter ISO 4217 codes and actual numerical values.\n\n"
        f"[main_rate] 1 {target_iso} = X {curr_iso}\n"
    )
    for code in comparison_currencies:
        if code != target_iso:
            prompt += f"[comparison] 1 {code} = X {curr_iso}\n"
    prompt += f"Source: {source_url}\n"
    prompt += "Date and time of the rate: [Month Day, Year HH:MM CET]\n\n"
    prompt += "Important: Replace 'X' with real numerical exchange rates. Do not include brackets around the date."

    for attempt in range(3):
        response = ""  # Initialize response for this attempt
        try:
            print("\n\tContacting AI for real-time exchange rates...")
            response = call_gpt(prompt).strip()
            print("\tResponse received.")

            main_rate_pattern = rf"\[main_rate\]\s+1\s+{target_iso}\s+=\s+([\d.eE-]+)\s+{curr_iso}"
            time_pattern = r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\s+\d{2}:\d{2}\s+CET"

            main_rate_match = re.search(main_rate_pattern, response)
            time_match = re.search(time_pattern, response)
            
            if not main_rate_match or not time_match:
                raise ValueError("Could not parse critical information from AI response.")

            main_rate = float(main_rate_match.group(1))
            timestamp = time_match.group(0)
            
            comparisons = {}
            for code in comparison_currencies:
                if code != target_iso:
                    comp_pattern = rf"\[comparison\]\s+1\s+{code}\s+=\s+([\d.eE-]+)\s+{curr_iso}"
                    comp_match = re.search(comp_pattern, response)
                    if comp_match:
                        comparisons[code] = float(comp_match.group(1))

            return main_rate, source_url, timestamp, comparisons

        except Exception as e:
            print(f"\n⚠️ An error occurred on attempt {attempt + 1}: {e}")
            if response:
                print(f"AI Response Received:\n{response}\n")
            else:
                print("No response was received from the AI before the error occurred.")

    
    print("🚫 All attempts failed. Unable to retrieve a valid exchange rate.")
    return None, None, None, None

def output_results(curr_info, target_info, amount, use_comma, main_rate, comparisons, source, timestamp):
    """Formats and prints the final conversion results for the user."""
    converted_amount = amount / main_rate
    
    print("\n--- CONVERSION RESULT ---\n")
    print(f"According to {source} at {timestamp}:\n")
    print(f"{curr_info['symbol']} {format_number(amount, use_comma)} ({curr_info['currency']}) is equivalent to:")
    
    # Use higher precision for cryptocurrencies
    if target_info['iso'] in {'BTC', 'ETH'}:
        print(f"➡️ {target_info['symbol']} {converted_amount:,.8f} ({target_info['currency']})\n")
    else:
        print(f"➡️ {target_info['symbol']} {format_number(converted_amount, use_comma)} ({target_info['currency']})\n")

    print("--- EXCHANGE RATES ---\n")
    print(f"The exchange rate is 1 {target_info['iso']} = {main_rate} {curr_info['iso']}.")
    print(f"The inverse rate is 1 {curr_info['iso']} = {1/main_rate:.6f} {target_info['iso']}.\n")
    
    if comparisons:
        print("--- FOR COMPARISON ---\n")
        print(f"{curr_info['symbol']} {format_number(amount, use_comma)} also equals:\n")
        for iso, rate in comparisons.items():
            comp_info = next((data for data in currency_data.values() if data['iso'] == iso), None)
            if comp_info:
                comp_amount = amount / rate
                if comp_info['iso'] in {'BTC', 'ETH'}:
                     print(f"{comp_info['symbol']} {comp_amount:,.8f} ({comp_info['currency']})")
                else:
                     print(f"{comp_info['symbol']} {format_number(comp_amount, use_comma)} ({comp_info['currency']})")
        print("\n")

def thank_you():
    """Prints a closing message."""
    print("Thank you for using the Forex Exchange App. We hope it has been helpful.")

# --- Main Execution ---

def main():
    """Main function to run the currency converter application."""
    introduction()
    
    global currency_data 
    
    current_dir = os.getcwd()
    json_path = os.path.join(current_dir, "country_currency_dictionary.json")
    currency_data = load_currency_data(json_path)

    while True:
        curr_info = get_currency_choice("\nWhat is the name of the country/currency to convert FROM? ", currency_data)
        target_info = get_currency_choice("What is the name of the country/currency to convert TO? ", currency_data)
        
        amount_to_convert, use_comma_separator = get_conversion_amount(curr_info)

        print(f"\nTo confirm: you want to convert {curr_info['symbol']} {amount_to_convert:.2f} ({curr_info['iso']}) to {target_info['iso']}.")
        confirm = normalize_input(input('Is that correct? (yes/no): '))
        
        if confirm == "yes":
            main_rate, source, timestamp, comparisons = get_exchange_rates(curr_info['iso'], target_info['iso'])

            if main_rate:
                output_results(curr_info, target_info, amount_to_convert, use_comma_separator, main_rate, comparisons, source, timestamp)
            else:
                print("\nSorry, we could not complete the conversion at this time.")
        
        else:
            print("\nNo problem. Let's start over.")
            continue

        again = normalize_input(input('Would you like to perform another conversion? (yes/no): '))
        if again != 'yes':
            break

    thank_you()


if __name__ == "__main__":
    main()