# ACP Client Demo: Example using ACP to Orchestrate Agent Interactions

This project demonstrates how to orchestrate the Kiro CLI using the Agent Control Protocol (ACP).

## Prerequisites

- [`kiro-cli`](https://kiro.dev/docs/cli/) installed and available in your PATH.

## Running

```bash
python3 main.py
```

## How it works

The `main.py` script:
1. Spawns `kiro-cli acp`.
2. Uses the `acp.py` module to communicate over JSON-RPC.
3. Sends a system prompt instructing the agent that it can access electricity price data by using this exact response text: `CALL_TOOL: fetch_electricity_prices`.
4. Sends a user prompt requesting today’s electricity prices.
5. Intercepts response containing `CALL_TOOL: fetch_electricity_prices`, retrieves prices from a public API, and returns the results to the agent.
6. Displays the agent's response summarizing the electricity prices.


## Example Interaction

When running the script, you will see output similar to below.
Lines prefixed with `kiro-cli:` are messages from the agent, while lines prefixed with `acp-client:` are logs from the ACP client (this script).

```
2026-03-02 16:17:26,241 [INFO] acp: acp-client: You have access to a client-side tool to fetch electricity prices. To use it, you MUST output EXACTLY this format and nothing else: CALL_TOOL: fetch_electricity_prices
2026-03-02 16:30:51,491 [INFO] acp: acp-client: How are the electricity prices today? Display in cents per kWh with tax included.
2026-03-02 16:17:29,518 [INFO] acp: kiro-cli: CALL_TOOL: fetch_electricity_prices
2026-03-02 16:17:29,518 [INFO] acp: Fetching electricity prices from API: https://api.spot-hinta.fi/TodayAndDayForward
2026-03-02 16:17:29,790 [INFO] acp: acp-client: Tool Result:
[
  {
    "Rank": 24,
    "DateTime": "2026-03-02T00:00:00+02:00",
    "PriceNoTax": 0.06762,
    "PriceWithTax": 0.08486
  },
  {
    "Rank": 20,
    "DateTime": "2026-03-02T00:15:00+02:00",
    "PriceNoTax": 0.06211,
    "PriceWithTax": 0.07795
  },
  {
    "Rank": 17,
    "DateTime": "2026-03-02T00:30:00+02:00",
    "PriceNoTax": 0.06004,
    "PriceWithTax": 0.07535
  },
...
]
2026-03-02 16:30:57,636 [INFO] acp: kiro-cli: Electricity prices for March 2, 2026 (cents/kWh with tax):
2026-03-02 16:30:57,636 [INFO] acp: kiro-cli:
2026-03-02 16:30:57,718 [INFO] acp: kiro-cli: **Cheapest hours:**
2026-03-02 16:30:57,937 [INFO] acp: kiro-cli: - 04:00: 5.64¢
2026-03-02 16:30:58,019 [INFO] acp: kiro-cli: - 03:00: 5.73¢
2026-03-02 16:30:58,198 [INFO] acp: kiro-cli: - 02:00: 5.90¢
2026-03-02 16:30:58,198 [INFO] acp: kiro-cli:
2026-03-02 16:30:58,198 [INFO] acp: kiro-cli: **Most expensive hours:**
2026-03-02 16:30:58,459 [INFO] acp: kiro-cli: - 09:00: 20.88¢
2026-03-02 16:30:58,672 [INFO] acp: kiro-cli: - 22:15: 18.94¢
2026-03-02 16:30:58,770 [INFO] acp: kiro-cli: - 20:00: 18.95¢
2026-03-02 16:30:58,770 [INFO] acp: kiro-cli:
2026-03-02 16:30:58,818 [INFO] acp: kiro-cli: **Today's pattern:**
2026-03-02 16:30:59,412 [INFO] acp: kiro-cli: - Night (00:00-05:00): Low, 5.6-8.5¢
2026-03-02 16:30:59,792 [INFO] acp: kiro-cli: - Morning peak (06:00-10:00): Rising to 20.9¢
2026-03-02 16:31:00,057 [INFO] acp: kiro-cli: - Midday (10:00-15:00): Moderate, 10.6-16.3¢
2026-03-02 16:31:00,357 [INFO] acp: kiro-cli: - Evening peak (18:00-22:00): High, 11.7-18.9¢
2026-03-02 16:31:01,347 [INFO] acp: kiro-cli: - Late night (22:00-24:00): Dropping to 7.6-18.8¢
2026-03-02 16:31:01,347 [INFO] acp: kiro-cli:
2026-03-02 16:31:01,361 [INFO] acp: kiro-cli: Best time to use electricity: Early morning hours (02:00-04:00).
```
