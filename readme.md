# Problem 1
As requested, we needed to extract a status reports for all the **Loans**.

The report can be found [problem_1/loans_status_report-2023-Nov-11.xlsx]("problem_1/loans_status_report-2023-Nov-11.xlsx")

Here is an overview of the ER Diagram of the tables provided:

![ER Diagram](docs/problem1-ER_Diagram.png)


## Get Started
To launch the instance for testing, you can follow the below steps:

1 - Make sure you have [docker](https://www.docker.com/) & [docker-compose](https://docs.docker.com/compose/)  install, then the below command:
```bash
docker-compose -f docker-compose-p1.yaml up
```

2 - Next you can access the database on the below `localhost` port `5435`.

3 - Run the query in your preferred PostgreSQL client.
```sql
select *
from view_loans_status_report;
```

## Details
I used SQL to extract the data with the below query:
```sql
-- Loans Status Report
with
ps_data as ( -- payment_schedules
	select loan_id, expected_payment_date as last_expected_payment_date, total_expected_payment_amount
	from (
		select ps.*,
			row_number() over(partition by loan_id order by expected_payment_date desc) as row_n,
			sum(expected_payment_amount) over (partition by loan_id order by expected_payment_date) as total_expected_payment_amount
		from payment_schedules ps
		where expected_payment_date <= now() -- The status today 
	) a
	where row_n = 1 -- Get last date ONLY
),
lp_data as ( -- loan_payments
	select loan_id, date_paid as last_date_paid, total_amount_paid
	from (
		select 
			lp.*,
			row_number() over(partition by loan_id order by date_paid desc) as row_n,
			sum(amount_paid) over (partition by loan_id order by date_paid) as total_amount_paid
		from loan_payments lp
		where date_paid <= now() -- The status today
	) a
	where row_n = 1 -- Get last date ONLY
)
select 
	loans.loan_id,
	loans.borrower_id,
	loans.date_of_release,
	loans.term,
	loans.loan_amount,
	loans.down_payment,
	borrowers.state,
	borrowers.city,
	borrowers.zip_code,
	loans.payment_frequency,
	loans.maturity_date,
	(lp.last_date_paid::date - ps.last_expected_payment_date::date) as current_days_past_due,
	ps.last_expected_payment_date as last_due_date,
	lp.last_date_paid as last_repayment_date,
	(ps.total_expected_payment_amount - lp.total_amount_paid) as amount_at_risk,
	borrowers.credit_score as borrower_credit_score,
	lp.total_amount_paid,
	ps.total_expected_payment_amount
from loans 
left join ps_data ps on loans.loan_id = ps.loan_id
left join lp_data lp on lp.loan_id = loans.loan_id
left join borrowers on borrowers.borrower_id = loans.borrower_id
```


## Observations:
- **The table `missing_payments` is not in the document**. I created the report without it.
- The below columns were not in the document & data provided:
  ```
  branch
  branch_id
  borrower_name  
  ```
- The `borrower_credit_score` for the second borrower is the letter `a`. Maybe a typo.