# aws_cost_summary
Executive summary of cost development across AWS accounts.

Run the script with a role that has access to billing information across all needed accounts and it will give you:

A quick overview of the cost development across the last 5 months.
A warning about the two services with the highest growth in cost during the previous month.

Useful as a monthly (run it with a cron trigger that posts slack) cost sanity check and a starting point for exploring further with AWS Cost Explorer.

Example output:

```
+--------------+-----------------+----------+----------+----------+----------+----------+----------------------+
|   Account ID |    Account Name | Apr 2024 | May 2024 | Jun 2024 | Jul 2024 | Aug 2024 | Last month sav./inc. |
+--------------+-----------------+----------+----------+----------+----------+----------+----------------------+
| 012345678910 |    account-prod |     5.64 |   176.37 | 1,636.14 |   701.83 | 1,116.43 |      414.61 (59.08%) |
| 111213141516 |     account-int |    48.96 |   645.50 |   875.73 |   861.68 | 1,034.70 |      173.02 (20.08%) |
| 171819202122 | account-pentest |   270.17 | 1,072.91 |   655.63 |   686.00 |   858.66 |      172.66 (25.17%) |
| 232425262728 |      account-qa |   601.07 |   849.25 |   748.10 | 1,072.55 | 1,035.88 |      -36.67 (-3.42%) |
| 293031323334 |   account-stage |   911.22 | 1,164.39 | 1,011.74 | 1,970.15 | 1,881.79 |      -88.36 (-4.49%) |
| 353637383940 |     account-dev |   203.24 | 1,529.13 | 1,622.72 | 1,716.16 |   984.87 |    -731.29 (-42.61%) |
+--------------+-----------------+----------+----------+----------+----------+----------+----------------------+
+------------+--------------+----------+----------+----------+-----------+----------+----------------------+
| Account ID | Account Name | Apr 2024 | May 2024 | Jun 2024 |  Jul 2024 | Aug 2024 | Last month sav./inc. |
+------------+--------------+----------+----------+----------+-----------+----------+----------------------+
|      Total |              | 3,977.03 | 7,604.23 | 9,174.16 | 10,721.64 | 9,892.94 |     -828.70 (-7.73%) |
+------------+--------------+----------+----------+----------+-----------+----------+----------------------+

Top 2 service cost increases last month:
353637383940  account-dev
Amazon Elastic Compute Cloud - Compute (Amount: +$67.30)
Amazon Elastic Container Service for Kubernetes (Amount: +$62.47)

293031323334   account-stage
Amazon Elastic Container Service for Kubernetes (Amount: +$215.22)
Amazon Kinesis (Amount: +$16.31)

232425262728  account-qa
Amazon Elastic Compute Cloud - Compute (Amount: +$50.69)
AWS Key Management Service (Amount: +$4.19)

Longer-term (5 months) upwards trend detected for the following account(s):
012345678910  account-prod                 940.06   274.70%
293031323334  account-stage                717.39   274.69%
111213141516  account-int                  389.19   218.76%
232425262728  account-qa                   186.63   109.29%
```
