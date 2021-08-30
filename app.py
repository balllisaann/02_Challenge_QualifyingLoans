# -*- coding: utf-8 -*-
"""Loan Qualifier Application.

This is a command line application to match applicants with qualifying loans.

Example:
    $ python app.py
"""
import sys
import fire
import questionary
import csv
from pathlib import Path

from qualifier.utils.fileio import load_csv

from qualifier.utils.calculators import (
    calculate_monthly_debt_ratio,
    calculate_loan_to_value_ratio,
)

from qualifier.filters.max_loan_size import filter_max_loan_size
from qualifier.filters.credit_score import filter_credit_score
from qualifier.filters.debt_to_income import filter_debt_to_income
from qualifier.filters.loan_to_value import filter_loan_to_value


def load_bank_data():
    """Ask for the file path to the latest banking data and load the CSV file.

    Returns:
        The bank data from the data rate sheet CSV file.
    """

    #csvpath = questionary.text("Enter a file path to a rate-sheet (.csv):").ask()
    csvpath = "data/daily_rate_sheet.csv"
    csvpath = Path(csvpath)
    if not csvpath.exists():
        sys.exit(f"Oops! Can't find this path: {csvpath}")

    return load_csv(csvpath)


def get_applicant_info():
    """Prompt dialog to get the applicant's financial information.

    Returns:
        Returns the applicant's financial information.
    """

    """""
    credit_score = questionary.text("What's your credit score?").ask()
    debt = questionary.text("What's your current amount of monthly debt?").ask()
    income = questionary.text("What's your total monthly income?").ask()
    loan_amount = questionary.text("What's your desired loan amount?").ask()
    home_value = questionary.text("What's your home value?").ask()
    """

    credit_score = 740
    debt = 500
    income = 5000
    loan_amount = 20000
    home_value = 200000

    credit_score = int(credit_score)
    debt = float(debt)
    income = float(income)
    loan_amount = float(loan_amount)
    home_value = float(home_value)

    return credit_score, debt, income, loan_amount, home_value


def find_qualifying_loans(bank_data, credit_score, debt, income, loan, home_value):
    """Determine which loans the user qualifies for.

    Loan qualification criteria is based on:
        - Credit Score
        - Loan Size
        - Debit to Income ratio (calculated)
        - Loan to Value ratio (calculated)

    Args:
        bank_data (list): A list of bank data.
        credit_score (int): The applicant's current credit score.
        debt (float): The applicant's total monthly debt payments.
        income (float): The applicant's total monthly income.
        loan (float): The total loan amount applied for.
        home_value (float): The estimated home value.

    Returns:
        A list of the banks willing to underwrite the loan.

    """

    # Calculate the monthly debt ratio
    monthly_debt_ratio = calculate_monthly_debt_ratio(debt, income)
    print(f"The monthly debt to income ratio is {monthly_debt_ratio:.02f}")

    # Calculate loan to value ratio
    loan_to_value_ratio = calculate_loan_to_value_ratio(loan, home_value)
    print(f"The loan to value ratio is {loan_to_value_ratio:.02f}.")

    # Run qualification filters
    bank_data_filtered = filter_max_loan_size(loan, bank_data)
    bank_data_filtered = filter_credit_score(credit_score, bank_data_filtered)
    bank_data_filtered = filter_debt_to_income(monthly_debt_ratio, bank_data_filtered)
    bank_data_filtered = filter_loan_to_value(loan_to_value_ratio, bank_data_filtered)

    print(f"Found {len(bank_data_filtered)} qualifying loans")

    return bank_data_filtered

def save_csv(qualifying_loans, output_path):
    """ A function uses the csv library to save the qualifying data as a file.
    Inputs:
    - qualifying_loans: assuming it is a list of lists
    - output_path: assuming it is a string
    Outputs: 
    - a .csv file should be saved.
    - no arguments are returned.
    Requirements: 
    - the csv package
    Documentation: https://docs.python.org/3/library/csv.html#writer-objects
    """

    with open(output_path, 'w', newline='') as csvfile:
        # creating a csv writer object 
        csvwriter = csv.writer(csvfile) 

        try:            
            # writing the list of lists on object qualifying_loans using iteration
            for loan in qualifying_loans:
                csvwriter.writerow(loan)
        except csvwriter.Error as e:
            sys.exit('file {}, line {}: {}'.format(output_path, csvwriter.line_num, e))

def save_qualifying_loans(qualifying_loans):
    """Saves the qualifying loans to a CSV file.

    Args:
        qualifying_loans (list of lists): The qualifying bank loans.
    """
    # @TODO: Complete the usability dialog for savings the CSV Files.
    # YOUR CODE HERE!
    # check to see if there are any qualifying loans
    # if there are no qualifying loans, let the user know and then exit
    if len(qualifying_loans) <= 0:
        sys.exit(f"Oops!  There are no qualifying loans.  Goodbye.")

    # Ask the user if they would like to save the file.
    # If not, gracefully exit.  
    # If the user does want to save the file, prompt them for a filename and path.
    yes_no = questionary.text("Would you like to save the qualifying loans to a file? (y/n)").ask()

    if yes_no == "n":
        sys.exit(f"You have chosen not to save the file.  Goodbye.")
    elif yes_no != "y":
        sys.exit(f"Sorry, we don't recognize that command: {yes_no}.  Goodbye")

    csvpath = questionary.text("Please enter a file path to save the list of qualifying loans to (.csv):").ask()
    csvpath = Path(csvpath)

    # add a *.csv extension to the file name stem, just to make sure it in a .csv type of file
    csvpath = csvpath.stem + ".csv"

    8# I'm going to add a header row to qualifying_loans.
    # The header is the same info as the input file (Lender,Max Loan Amount,Max LTV,Max DTI,Min Credit Score,Interest Rate).
    qualifying_loans.insert(0, ["Lender","Max Loan Amount","Max LTV","Max DTI","Min Credit Score","Interest Rate"])
    # Now that we have a valid file name to save to, call the save_csv fuction to actually create and save the *.csv file
    save_csv(qualifying_loans, csvpath)


def run():
    """The main function for running the script."""

    # Load the latest Bank data
    bank_data = load_bank_data()

    # Get the applicant's information
    credit_score, debt, income, loan_amount, home_value = get_applicant_info()

    # Find qualifying loans
    qualifying_loans = find_qualifying_loans(
        bank_data, credit_score, debt, income, loan_amount, home_value
    )

    # Save qualifying loans
    save_qualifying_loans(qualifying_loans)

if __name__ == "__main__":
    fire.Fire(run)
