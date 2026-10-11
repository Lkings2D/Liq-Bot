# Automated Risk Management & Pre-Midnight Position Closer

A production-ready Python utility built on top of the [MyFundedPerps Developer API](https://docs.myfundedperpetuals.com/api-reference/positions/close-part-or-all-of-a-position) to automate risk mitigation and position liquidation for perpetual futures traders.

## Overview

Managing overnight risk or avoiding platform-specific session penalties can be challenging with manual interventions. This script runs as a background worker, automatically scanning specified sandbox or live accounts, dynamically discovering internal account routing IDs, and flattening all active positions (supporting any asset class such as ETH, BTC, or SOL) safely right before a target cutoff time (e.g., 11:55 PM daily).

## Key Features

* **Multi-Account Dynamic Mapping:** Automatically queries the `/v1/accounts` endpoint to resolve the exact system-assigned identifier for specific target accounts (e.g., `FP-1234567`).
* **Universal Asset Support:** Dynamically fetches live market parameters (`mark_price` or `entry_price`) for any open position to seamlessly satisfy exchange-required slippage validation rules.
* **Idempotency & Execution Safety:** Employs UUID-based `Idempotency-Key` headers on close requests to prevent accidental duplicate order submissions during network anomalies.
* **Scheduled Automation:** Runs continuously in a background event loop, triggering precise pre-midnight liquidations with built-in duplicate window prevention.

## How the Process Works

The bot is designed to handle the repetitive, time-sensitive steps involved in closing positions:

1. It runs as a background worker and checks the configured schedule.
2. At the target cutoff time, it looks up the account's internal routing ID from the account number.
3. It retrieves every open position on that account, regardless of whether the position is on ETH, BTC, SOL, or another supported asset.
4. For each position, it uses the available mark price (or entry price as a fallback) to satisfy the API's expected-price requirement.
5. It submits a market close request with a unique idempotency key, helping prevent duplicate submissions if the request is retried.
6. It logs whether each position was closed successfully or whether the API returned an error.

This means a trader does not need to be at their computer at the exact cutoff time. The bot can continue working while they are away from home, without Wi-Fi access, busy with something else, or asleep. The machine or server running the worker still needs a reliable internet connection and must remain powered on.

## Where We See It Being Used

The immediate use case is reducing overnight and session-related risk for traders who need to be flat by a specific time but cannot reliably close positions manually. It can be useful for:

* **Pre-midnight risk management:** Close all open positions before a daily cutoff or platform session reset.
* **Hands-off trading routines:** Let traders follow a consistent end-of-day process even when they are commuting, traveling, or away from their trading setup.
* **Account protection:** Reduce the chance of leaving an exposed position open because of a missed reminder, unexpected schedule change, or falling asleep.
* **Multiple-account operations:** Apply the same close routine to several configured accounts instead of repeating the process manually.
* **Testing and automation workflows:** Run the worker against a sandbox account while validating API behavior and scheduled execution.

Future versions could expand this from a fixed pre-midnight close into a broader risk-management assistant. Possible additions include configurable schedules per account, partial closes, stop-loss or drawdown triggers, alerts through email or messaging apps, a hosted always-on deployment, and a dashboard showing execution history. Those extensions would allow the bot to respond not only to a specific time, but also to changing market or account conditions.

## Requirements

* Python 3.8+
* `requests` library

```bash
pip install requests
```

## Visual Overview

<div align="center">
  <p><strong>Image 1: Terminal view showing the successful closing of a position.</strong></p>
  <img src="assets/SS1.png" alt="Terminal view showing a successful position close" width="900" />
</div>

<div align="center">
  <p><strong>Image 2: Manually changing the scheduled time for testing purposes.</strong></p>
  <img src="assets/ss2.png" alt="Manually changing the scheduled time for testing" width="900" />
</div>

<div align="center">
  <p><strong>Image 3: Log showing a successful position close.</strong></p>
  <img src="assets/ss3.png" alt="Log showing a successful position close" width="900" />
</div>
