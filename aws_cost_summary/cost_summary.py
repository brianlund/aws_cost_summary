import boto3
import datetime
import numpy as np
from collections import defaultdict
from dateutil.relativedelta import relativedelta
from tabulate import tabulate


def get_previous_months(start_date):
    end_date = start_date.replace(day=1) - datetime.timedelta(days=1)
    start_date = end_date.replace(day=1)
    return start_date, end_date


def get_cost(client, accounts, start_date, end_date):
    end_date += relativedelta(months=1)
    response = client.get_cost_and_usage(
        TimePeriod={
            "Start": start_date.strftime("%Y-%m-%d"),
            "End": end_date.strftime("%Y-%m-%d"),
        },
        Granularity="MONTHLY",
        Filter={"Dimensions": {"Key": "LINKED_ACCOUNT", "Values": list(accounts)}},
        GroupBy=[{"Type": "DIMENSION", "Key": "LINKED_ACCOUNT"}],
        Metrics=["NetAmortizedCost"],
    )
    return response


def get_costs_by_service(client, account_id):
    today = datetime.date.today()
    last_month_start, last_month_end = get_previous_months(today)
    two_months_ago_start, two_months_ago_end = get_previous_months(last_month_start)

    prev_costs_response = client.get_cost_and_usage(
        TimePeriod={
            "Start": two_months_ago_start.strftime("%Y-%m-%d"),
            "End": two_months_ago_end.strftime("%Y-%m-%d"),
        },
        Granularity="MONTHLY",
        Filter={"Dimensions": {"Key": "LINKED_ACCOUNT", "Values": [account_id]}},
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
        Metrics=["NetAmortizedCost"],
    )

    costs_response = client.get_cost_and_usage(
        TimePeriod={
            "Start": last_month_start.strftime("%Y-%m-%d"),
            "End": last_month_end.strftime("%Y-%m-%d"),
        },
        Granularity="MONTHLY",
        Filter={"Dimensions": {"Key": "LINKED_ACCOUNT", "Values": [account_id]}},
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
        Metrics=["NetAmortizedCost"],
    )

    prev_service_costs = {}
    for result in prev_costs_response["ResultsByTime"][0]["Groups"]:
        service = result["Keys"][0]
        cost = float(result["Metrics"]["NetAmortizedCost"]["Amount"])
        prev_service_costs[service] = cost

    service_costs = {}
    for result in costs_response["ResultsByTime"][0]["Groups"]:
        service = result["Keys"][0]
        cost = float(result["Metrics"]["NetAmortizedCost"]["Amount"])
        service_costs[service] = cost

    return prev_service_costs, service_costs


def get_account_costs(client, accounts, account_names):
    today = datetime.date.today()
    last_month_start, last_month_end = get_previous_months(today)
    two_months_ago_start, two_months_ago_end = get_previous_months(last_month_start)
    three_months_ago_start, three_months_ago_end = get_previous_months(
        two_months_ago_start
    )
    four_months_ago_start, four_months_ago_end = get_previous_months(
        three_months_ago_start
    )
    five_months_ago_start, five_months_ago_end = get_previous_months(
        four_months_ago_start
    )

    costs_last_month = get_cost(client, accounts, last_month_start, last_month_end)
    costs_two_months_ago = get_cost(
        client, accounts, two_months_ago_start, two_months_ago_end
    )
    costs_three_months_ago = get_cost(
        client, accounts, three_months_ago_start, three_months_ago_end
    )
    costs_four_months_ago = get_cost(
        client, accounts, four_months_ago_start, four_months_ago_end
    )
    costs_five_months_ago = get_cost(
        client, accounts, five_months_ago_start, five_months_ago_end
    )

    account_costs = defaultdict(dict)

    for result in costs_last_month["ResultsByTime"][0]["Groups"]:
        account_id = result["Keys"][0]
        cost = float(result["Metrics"]["NetAmortizedCost"]["Amount"])
        account_costs[account_id]["last_month"] = cost

    for result in costs_two_months_ago["ResultsByTime"][0]["Groups"]:
        account_id = result["Keys"][0]
        cost = float(result["Metrics"]["NetAmortizedCost"]["Amount"])
        account_costs[account_id]["two_months_ago"] = cost

    for result in costs_three_months_ago["ResultsByTime"][0]["Groups"]:
        account_id = result["Keys"][0]
        cost = float(result["Metrics"]["NetAmortizedCost"]["Amount"])
        account_costs[account_id]["three_months_ago"] = cost

    for result in costs_four_months_ago["ResultsByTime"][0]["Groups"]:
        account_id = result["Keys"][0]
        cost = float(result["Metrics"]["NetAmortizedCost"]["Amount"])
        account_costs[account_id]["four_months_ago"] = cost

    for result in costs_five_months_ago["ResultsByTime"][0]["Groups"]:
        account_id = result["Keys"][0]
        cost = float(result["Metrics"]["NetAmortizedCost"]["Amount"])
        account_costs[account_id]["five_months_ago"] = cost

    return account_costs


def display_cost_changes(
    client,
    accounts,
    account_costs,
    last_month_start,
    two_months_ago_start,
    three_months_ago_start,
    four_months_ago_start,
    five_months_ago_start,
):

    prev_last_month_start = last_month_start  # relativedelta(months=1)
    prev_two_months_ago_start = two_months_ago_start  # relativedelta(months=1)
    prev_three_months_ago_start = three_months_ago_start  # relativedelta(months=1)
    prev_four_months_ago_start = four_months_ago_start  # relativedelta(months=1)
    prev_five_months_ago_start = five_months_ago_start  # relativedelta(months=1)

    # Table headers
    headers = [
        "Account ID",
        "Account Name",
        prev_five_months_ago_start.strftime("%b %Y"),
        prev_four_months_ago_start.strftime("%b %Y"),
        prev_three_months_ago_start.strftime("%b %Y"),
        prev_two_months_ago_start.strftime("%b %Y"),
        prev_last_month_start.strftime("%b %Y"),
        "Last month sav./inc.",
    ]

    table_data = []
    sorted_account_costs = sorted(
        account_costs.items(),
        key=lambda x: x[1].get("last_month", 0) - x[1].get("two_months_ago", 0),
        reverse=True,
    )

    significant_increase_accounts = []
    longer_term_increase_accounts = []

    total_five_months_ago_cost = 0
    total_four_months_ago_cost = 0
    total_three_months_ago_cost = 0
    total_two_months_ago_cost = 0
    total_last_month_cost = 0
    total_change = 0

    for account_id, costs in sorted_account_costs:
        account_name = accounts.get(account_id, "N/A")
        last_month_cost = costs.get("last_month", 0)
        two_months_ago_cost = costs.get("two_months_ago", 0)
        three_months_ago_cost = costs.get("three_months_ago", 0)
        four_months_ago_cost = costs.get("four_months_ago", 0)
        five_months_ago_cost = costs.get("five_months_ago", 0)
        change = last_month_cost - two_months_ago_cost

        if two_months_ago_cost != 0:
            acc_pct = (
                (last_month_cost - two_months_ago_cost) / two_months_ago_cost * 100
            )
        else:
            acc_pct = 0

        row = [
            account_id,
            account_name,
            f"{five_months_ago_cost:,.2f}",
            f"{four_months_ago_cost:,.2f}",
            f"{three_months_ago_cost:,.2f}",
            f"{two_months_ago_cost:,.2f}",
            f"{last_month_cost:,.2f}",
            f"{change:,.2f} ({acc_pct:,.2f}%)",
        ]

        table_data.append(row)

        total_five_months_ago_cost += five_months_ago_cost
        total_four_months_ago_cost += four_months_ago_cost
        total_three_months_ago_cost += three_months_ago_cost
        total_two_months_ago_cost += two_months_ago_cost
        total_last_month_cost += last_month_cost
        total_change += change

        if total_two_months_ago_cost != 0:
            total_pct = (
                (total_last_month_cost - total_two_months_ago_cost)
                / total_two_months_ago_cost
                * 100
            )
        else:
            total_pct = 0

        increase_percentage = (
            (last_month_cost - two_months_ago_cost) / two_months_ago_cost * 100
            if two_months_ago_cost != 0
            else 0
        )
        increase_amount = last_month_cost - two_months_ago_cost

        if two_months_ago_cost > 1500:
            significant_increase_accounts.append(
                (account_id, account_name, increase_amount, increase_percentage)
            )

        # Array with the last 4 months' costs.
        costs_array = np.array(
            [
                five_months_ago_cost,
                four_months_ago_cost,
                three_months_ago_cost,
                two_months_ago_cost,
                last_month_cost,
            ]
        )

        # Calculate the slope of the best-fit line
        slope = np.polyfit(range(len(costs_array)), costs_array, 1)[0]

        # Check if the slope is positive and if the total increase in costs is greater than threshold.
        long_term_increase_amount = last_month_cost - four_months_ago_cost

        # Count the number of months with zero cost
        zero_cost_months = np.count_nonzero(costs_array == 0)

        # If most months have zero cost, ignore the long-term trend
        if zero_cost_months <= len(costs_array) // 2:
            if slope > 0 and long_term_increase_amount > 100:
                longer_term_increase_accounts.append(
                    (account_id, account_name, long_term_increase_amount, slope)
                )

    print(tabulate(table_data, headers=headers, tablefmt="pretty", stralign="right"))

    # Add the totals as a footer row
    footer_row = [
        "Total",
        "",
        f"{total_five_months_ago_cost:,.2f}",
        f"{total_four_months_ago_cost:,.2f}",
        f"{total_three_months_ago_cost:,.2f}",
        f"{total_two_months_ago_cost:,.2f}",
        f"{total_last_month_cost:,.2f}",
        f"{total_change:,.2f} ({total_pct:,.2f}%)",
    ]
    print(
        tabulate(
            [footer_row],
            headers=headers,
            tablefmt="pretty",
            numalign="right",
            stralign="right",
        )
    )

    if significant_increase_accounts:
        print("\nTop 2 service cost increases last month:")
        significant_increase_accounts_sorted = sorted(
            significant_increase_accounts, key=lambda x: x[2], reverse=True
        )
        for (
            account_id,
            account_name,
            increase_amount,
            increase_percentage,
        ) in significant_increase_accounts_sorted:
            print(f"{account_id:>12}  {account_name:<20}")

            prev_month_costs_by_service, last_month_costs_by_service = (
                get_costs_by_service(client, account_id)
            )
            cost_differences = {
                service: last_month_costs_by_service.get(service, 0)
                - prev_month_costs_by_service.get(service, 0)
                for service in last_month_costs_by_service
            }

            top_2_cost_increases = sorted(
                cost_differences.items(), key=lambda x: x[1], reverse=True
            )[:2]
            for service, increase_amount in top_2_cost_increases:
                print(f"{service} (Amount: +${increase_amount:,.2f})")
            print()

    if longer_term_increase_accounts:
        print(
            "Longer-term (5 months) upwards trend detected for the following account(s):"
        )
        longer_term_increase_accounts_sorted = sorted(
            longer_term_increase_accounts, key=lambda x: x[2], reverse=True
        )
        for (
            account_id,
            account_name,
            increase_amount,
            increase_percentage,
        ) in longer_term_increase_accounts_sorted:
            print(
                f"{account_id:>12}  {account_name:<20} {increase_amount:>10,.2f} {increase_percentage:>8,.2f}%"
            )


def main():
    # Add your AWS account numbers and aliases here.
    accounts = {
        "<ACCOUNT_NUMBER>": "<ACCOUNT_ALIAS>",
        "<ACCOUNT_NUMBER>": "<ACCOUNT_ALIAS>",
        "<ACCOUNT_NUMBER>": "<ACCOUNT_ALIAS>",
    }

    # Initialize the client
    client = boto3.client("ce")

    account_costs = get_account_costs(client, accounts.keys(), accounts)
    last_month_start, last_month_end = get_previous_months(datetime.date.today())
    two_months_ago_start, two_months_ago_end = get_previous_months(last_month_start)
    three_months_ago_start, three_months_ago_end = get_previous_months(
        two_months_ago_start
    )
    four_months_ago_start, four_months_ago_end = get_previous_months(
        three_months_ago_start
    )
    five_months_ago_start, five_months_ago_end = get_previous_months(
        four_months_ago_start
    )

    display_cost_changes(
        client,
        accounts,
        account_costs,
        last_month_start,
        last_month_end,
        two_months_ago_start,
        two_months_ago_end,
        three_months_ago_start,
        four_months_ago_start,
        five_months_ago_start,
    )


if __name__ == "__main__":
    main()
