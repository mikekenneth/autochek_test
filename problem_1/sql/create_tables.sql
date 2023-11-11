DROP DATABASE IF EXISTS autochek_db;
CREATE DATABASE autochek_db;

\c autochek_db;
SET datestyle TO "ISO, MDY"; -- To set the datestyle to MM/DD/YYY

--------------------------------- Borrowers Table ---------------------------------
CREATE TABLE IF NOT EXISTS borrowers (
    borrower_id varchar(15) PRIMARY KEY,
    state varchar(25),
    city varchar(25),
    zip_code varchar(25),
    credit_score varchar(5)
);


--------------------------------- Loans Table ---------------------------------
CREATE TABLE IF NOT EXISTS loans (
    borrower_id varchar(15),
    loan_id varchar(25) PRIMARY KEY,
    date_of_release date,
    term integer,
    interest_rate numeric,
    loan_amount numeric,
    down_payment numeric,
    payment_frequency numeric,
    maturity_date date,
    CONSTRAINT fk_borrower
      FOREIGN KEY(borrower_id) 
	  REFERENCES borrowers(borrower_id)
      -- ON DELETE SET NULL  -- Would be useful for implementing RTBF (Right to Be Forgotten)
);
CREATE INDEX borrower_id_idx ON loans USING btree (borrower_id);


--------------------------------- Payment_Schedule Table ---------------------------------
CREATE TABLE IF NOT EXISTS payment_schedules (
    loan_id varchar(25),
    schedule_id varchar(25) PRIMARY KEY,
    expected_payment_date date,
    expected_payment_amount numeric,
    CONSTRAINT fk_loan
        FOREIGN KEY(loan_id) 
        REFERENCES loans(loan_id)
        -- ON DELETE SET NULL  -- Would be useful for implementing RTBF (Right to Be Forgotten)
    );
CREATE INDEX loan_id_idx ON payment_schedules USING btree (loan_id);


--------------------------------- Loan_payment Table ---------------------------------
CREATE TABLE IF NOT EXISTS loan_payments (
    loan_id varchar(25),
    payment_id varchar(25) PRIMARY KEY,
    date_paid date,
    amount_paid numeric,
    CONSTRAINT fk_loan
        FOREIGN KEY(loan_id) 
        REFERENCES loans(loan_id)
        -- ON DELETE SET NULL  -- Would be useful for implementing RTBF (Right to Be Forgotten)
    );
CREATE INDEX loan_id_idx_2 ON loan_payments USING btree (loan_id);

