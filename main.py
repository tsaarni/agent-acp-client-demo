import sys
import urllib.request
import logging
import acp

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
logging.getLogger("acp").setLevel(logging.INFO)
logger = logging.getLogger("acp")


def fetch_electricity_prices():
    logger.info("Fetching electricity prices from API: https://api.spot-hinta.fi/TodayAndDayForward")
    with urllib.request.urlopen("https://api.spot-hinta.fi/TodayAndDayForward") as response:
        return response.read().decode()


def main():
    client = acp.connect()

    session = client.new_session(
        system_prompt=(
            "You have access to a client-side tool to fetch electricity prices. "
            "To use it, you MUST output EXACTLY this format and nothing else: "
            "CALL_TOOL: fetch_electricity_prices"
        )
    )

    response = session.prompt("How are the electricity prices today? Display in cents per kWh with tax included.")

    if "CALL_TOOL: fetch_electricity_prices" in response:
        result = fetch_electricity_prices()
        session.prompt(f"Tool Result:\n{result}")

    client.close()


if __name__ == "__main__":
    main()
