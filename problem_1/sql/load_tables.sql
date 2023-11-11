\c autochek_db;
SET datestyle TO "ISO, MDY"; -- To set the datestyle to MM/DD/YYY

--------------------------------- Borrowers Table ---------------------------------
COPY borrowers(borrower_id, state, city, zip_code, credit_score)
FROM '/raw_data/borrowers.csv' DELIMITER ',' CSV HEADER;

--------------------------------- Loans Table ---------------------------------
COPY loans(borrower_id, loan_id, date_of_release, term, interest_rate, loan_amount, down_payment, payment_frequency, maturity_date)
FROM '/raw_data/loans.csv' DELIMITER ',' CSV HEADER;

--------------------------------- Payment_Schedule Table ---------------------------------
COPY payment_schedules(loan_id, schedule_id, expected_payment_date, expected_payment_amount)
FROM '/raw_data/payment_schedule.csv' DELIMITER ',' CSV HEADER;

--------------------------------- Loan_payment Table ---------------------------------
COPY loan_payments(loan_id, payment_id, date_paid, amount_paid)
FROM '/raw_data/loan_payments.csv' DELIMITER ',' CSV HEADER;

commit;