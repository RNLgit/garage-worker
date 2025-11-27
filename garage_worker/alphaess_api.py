"""
AlphaESS API Client
Retrieves real-time power data from AlphaESS solar battery storage system
You'll need a registered developer account to get AppID and AppSecret
"""

import hashlib
import time
import requests
from typing import Dict, Any


class AlphaESSClient:
    """Client for interacting with AlphaESS OpenAPI"""

    BASE_URL = "https://openapi.alphaess.com/api"

    def __init__(self, app_id: str, app_secret: str):
        """
        Initialize the AlphaESS API client

        Args:
            app_id: Developer ID (AppID) from AlphaESS portal
            app_secret: App Secret from AlphaESS portal
        """
        self.app_id = app_id
        self.app_secret = app_secret

    def _generate_signature(self, timestamp: int) -> str:
        """
        Generate SHA512 signature for API authentication

        Args:
            timestamp: Unix timestamp (seconds)

        Returns:
            SHA512 hash string
        """
        # Concatenate: appId + appSecret + timestamp
        sign_string = f"{self.app_id}{self.app_secret}{timestamp}"

        # Generate SHA512 hash
        signature = hashlib.sha512(sign_string.encode()).hexdigest()

        return signature

    def _get_headers(self) -> Dict[str, str]:
        """
        Generate headers for API request

        Returns:
            Dictionary of headers including appId, timeStamp, and sign
        """
        timestamp = int(time.time())  # Unix timestamp in seconds
        signature = self._generate_signature(timestamp)

        headers = {
            "appId": self.app_id,
            "timeStamp": str(timestamp),
            "sign": signature,
            "Content-Type": "application/json"
        }

        return headers

    def get_last_power_data(self, system_sn: str) -> Dict[str, Any]:
        """
        Get real-time power data for a specific system

        Args:
            system_sn: System Serial Number

        Returns:
            Dictionary containing power data or error information
        """
        url = f"{self.BASE_URL}/getLastPowerData"
        headers = self._get_headers()
        params = {"sysSn": system_sn}

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            data = response.json()

            # Check if request was successful
            if data.get("code") == 200:
                return data
            else:
                print(f"API Error: Code {data.get('code')}, Message: {data.get('msg')}")
                return data

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return {"error": str(e)}

    def get_system_summary(self, system_sn: str) -> Dict[str, Any]:
        """
        Get system summary data including today's and total generation, consumption, etc.

        Args:
            system_sn: System Serial Number

        Returns:
            Dictionary containing system summary data or error information
        """
        url = f"{self.BASE_URL}/getSumDataForCustomer"
        headers = self._get_headers()
        params = {"sysSn": system_sn}

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            data = response.json()

            if data.get("code") == 200:
                return data
            else:
                print(f"API Error: Code {data.get('code')}, Message: {data.get('msg')}")
                return data

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return {"error": str(e)}

    def get_system_list(self) -> Dict[str, Any]:
        """
        Get list of all systems associated with the account

        Returns:
            Dictionary containing list of systems or error information
        """
        url = f"{self.BASE_URL}/getEssList"
        headers = self._get_headers()

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()

            if data.get("code") == 200:
                return data
            else:
                print(f"API Error: Code {data.get('code')}, Message: {data.get('msg')}")
                return data

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return {"error": str(e)}

    def get_one_day_power(self, system_sn: str, query_date: str) -> Dict[str, Any]:
        """
        Get system power data for a specific day (time-series data)

        Args:
            system_sn: System Serial Number
            query_date: Date in format yyyy-MM-dd (e.g., "2024-01-15")

        Returns:
            Dictionary containing power data timeline or error information
        """
        url = f"{self.BASE_URL}/getOneDayPowerBySn"
        headers = self._get_headers()
        params = {
            "sysSn": system_sn,
            "queryDate": query_date
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            data = response.json()

            if data.get("code") == 200:
                return data
            else:
                print(f"API Error: Code {data.get('code')}, Message: {data.get('msg')}")
                return data

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return {"error": str(e)}

    def get_one_day_energy(self, system_sn: str, query_date: str) -> Dict[str, Any]:
        """
        Get system energy data for a specific day (daily totals)

        Args:
            system_sn: System Serial Number
            query_date: Date in format yyyy-MM-dd (e.g., "2024-01-15")

        Returns:
            Dictionary containing energy data or error information
        """
        url = f"{self.BASE_URL}/getOneDateEnergyBySn"
        headers = self._get_headers()
        params = {
            "sysSn": system_sn,
            "queryDate": query_date
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            data = response.json()

            if data.get("code") == 200:
                return data
            else:
                print(f"API Error: Code {data.get('code')}, Message: {data.get('msg')}")
                return data

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return {"error": str(e)}

    def get_charge_config(self, system_sn: str) -> Dict[str, Any]:
        """
        Get charging configuration settings for a system

        Args:
            system_sn: System Serial Number

        Returns:
            Dictionary containing charging configuration or error information
        """
        url = f"{self.BASE_URL}/getChargeConfigInfo"
        headers = self._get_headers()
        params = {"sysSn": system_sn}

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            data = response.json()

            if data.get("code") == 200:
                return data
            else:
                print(f"API Error: Code {data.get('code')}, Message: {data.get('msg')}")
                return data

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return {"error": str(e)}

    def print_power_data(self, system_sn: str):
        """
        Retrieve and print formatted power data

        Args:
            system_sn: System Serial Number
        """
        data = self.get_last_power_data(system_sn)

        if data.get("code") == 200:
            power_data = data.get("data", {})

            print(f"\n{'=' * 50}")
            print(f"Real-time Power Data for System: {system_sn}")
            print(f"{'=' * 50}\n")

            print(f"PV Total Power:        {power_data.get('ppv', 0):>10.2f} W")

            # PV Details
            pv_details = power_data.get('ppvDetailData', {})
            if pv_details:
                print(f"  - PV1:               {pv_details.get('ppv1', 0):>10.2f} W")
                print(f"  - PV2:               {pv_details.get('ppv2', 0):>10.2f} W")
                print(f"  - PV3:               {pv_details.get('ppv3', 0):>10.2f} W")
                print(f"  - PV4:               {pv_details.get('ppv4', 0):>10.2f} W")

            print(f"\nBattery Power:         {power_data.get('pbat', 0):>10.2f} W")
            print(f"Battery SOC:           {power_data.get('soc', 0):>10.2f} %")

            print(f"\nLoad Power:            {power_data.get('pload', 0):>10.2f} W")

            pgrid = power_data.get('pgrid', 0)
            grid_status = "Importing" if pgrid > 0 else "Exporting" if pgrid < 0 else "Zero"
            print(f"Grid Power:            {pgrid:>10.2f} W ({grid_status})")

            # Grid Details
            grid_details = power_data.get('pgridDetailData', {})
            if grid_details:
                print(f"  - L1:                {grid_details.get('pmeterL1', 0):>10.2f} W")
                print(f"  - L2:                {grid_details.get('pmeterL2', 0):>10.2f} W")
                print(f"  - L3:                {grid_details.get('pmeterL3', 0):>10.2f} W")

            print(f"\nEV Charger Total:      {power_data.get('pev', 0):>10.2f} W")

            # EV Details
            ev_details = power_data.get('pevDetailData', {})
            if ev_details:
                print(f"  - EV1:               {ev_details.get('ev1Power', 0):>10.2f} W")
                print(f"  - EV2:               {ev_details.get('ev2Power', 0):>10.2f} W")
                print(f"  - EV3:               {ev_details.get('ev3Power', 0):>10.2f} W")
                print(f"  - EV4:               {ev_details.get('ev4Power', 0):>10.2f} W")

            print(f"\n{'=' * 50}\n")
        else:
            print(f"Failed to retrieve data: {data}")

    def print_system_summary(self, system_sn: str):
        """
        Retrieve and print formatted system summary data

        Args:
            system_sn: System Serial Number
        """
        data = self.get_system_summary(system_sn)

        if data.get("code") == 200:
            summary = data.get("data", {})

            print(f"\n{'=' * 50}")
            print(f"System Summary for: {system_sn}")
            print(f"{'=' * 50}\n")

            print("TODAY'S DATA:")
            print(f"  Generation:          {summary.get('epvtoday', 0):>10.2f} kWh")
            print(f"  Load:                {summary.get('eload', 0):>10.2f} kWh")
            print(f"  Feed-in:             {summary.get('eoutput', 0):>10.2f} kWh")
            print(f"  Consumed:            {summary.get('einput', 0):>10.2f} kWh")
            print(f"  Charged:             {summary.get('echarge', 0):>10.2f} kWh")
            print(f"  Discharged:          {summary.get('edischarge', 0):>10.2f} kWh")
            print(f"  Income:              {summary.get('todayIncome', 0):>10.2f} {summary.get('moneyType', '')}")

            print(f"\nTOTAL:")
            print(f"  Total Generation:    {summary.get('epvtotal', 0):>10.2f} kWh")
            print(f"  Total Profit:        {summary.get('totalIncome', 0):>10.2f} {summary.get('moneyType', '')}")

            print(f"\nEFFICIENCY:")
            print(f"  Self-consumption:    {summary.get('eselfConsumption', 0):>10.2f} %")
            print(f"  Self-sufficiency:    {summary.get('eselfSufficiency', 0):>10.2f} %")

            print(f"\nENVIRONMENTAL IMPACT:")
            print(f"  Trees Planted:       {summary.get('treeNum', 0):>10.2f}")
            print(f"  CO2 Reduction:       {summary.get('carbonNum', 0):>10.2f} kg")

            print(f"\n{'=' * 50}\n")
        else:
            print(f"Failed to retrieve data: {data}")

    def print_system_list(self):
        """
        Retrieve and print list of all systems
        """
        data = self.get_system_list()

        if data.get("code") == 200:
            systems = data.get("data", [])

            print(f"\n{'=' * 50}")
            print(f"System List ({len(systems)} system(s) found)")
            print(f"{'=' * 50}\n")

            for idx, system in enumerate(systems, 1):
                print(f"System {idx}:")
                print(f"  Serial Number:       {system.get('sysSn', 'N/A')}")
                print(f"  EMS Status:          {system.get('emsStatus', 'N/A')}")
                print(f"  Inverter Model:      {system.get('minv', 'N/A')}")
                print(f"  Inverter Power:      {system.get('poinv', 0):>10.2f} kW")
                print(f"  PV Nominal Power:    {system.get('popv', 0):>10.2f} kW")
                print(f"  Battery Model:       {system.get('mbat', 'N/A')}")
                print(f"  Battery Capacity:    {system.get('cobat', 0):>10.2f} kWh")
                print(f"  Remaining Capacity:  {system.get('surplusCobat', 0):>10.2f} kWh")
                print(f"  Available %:         {system.get('usCapacity', 0):>10.2f} %")
                print()

            print(f"{'=' * 50}\n")
        else:
            print(f"Failed to retrieve data: {data}")

    def print_one_day_energy(self, system_sn: str, query_date: str):
        """
        Retrieve and print energy data for a specific day

        Args:
            system_sn: System Serial Number
            query_date: Date in format yyyy-MM-dd (e.g., "2024-01-15")
        """
        data = self.get_one_day_energy(system_sn, query_date)

        if data.get("code") == 200:
            energy = data.get("data", {})

            print(f"\n{'=' * 50}")
            print(f"Energy Data for {query_date}")
            print(f"System: {system_sn}")
            print(f"{'=' * 50}\n")

            print("GENERATION:")
            print(f"  PV Generation:       {energy.get('epv', 0):>10.2f} kWh")

            print("\nBATTERY:")
            print(f"  Total Charged:       {energy.get('eCharge', 0):>10.2f} kWh")
            print(f"  Total Discharged:    {energy.get('eDischarge', 0):>10.2f} kWh")
            print(f"  Grid Charged:        {energy.get('eGridCharge', 0):>10.2f} kWh")

            print("\nGRID:")
            print(f"  Grid Consumption:    {energy.get('eInput', 0):>10.2f} kWh")
            print(f"  Feed-in:             {energy.get('eOutput', 0):>10.2f} kWh")

            print("\nEV CHARGING:")
            print(f"  Charging Pile:       {energy.get('eChargingPile', 0):>10.2f} kWh")

            print(f"\n{'=' * 50}\n")
        else:
            print(f"Failed to retrieve data: {data}")

    def print_one_day_power(self, system_sn: str, query_date: str, max_records: int = 10):
        """
        Retrieve and print power data timeline for a specific day

        Args:
            system_sn: System Serial Number
            query_date: Date in format yyyy-MM-dd (e.g., "2024-01-15")
            max_records: Maximum number of records to display (default: 10, use None for all)
        """
        data = self.get_one_day_power(system_sn, query_date)

        if data.get("code") == 200:
            power_data = data.get("data", [])

            print(f"\n{'=' * 50}")
            print(f"Power Timeline for {query_date}")
            print(f"System: {system_sn}")
            print(f"Total Records: {len(power_data)}")
            print(f"{'=' * 50}\n")

            if not power_data:
                print("No data available for this date.")
                print(f"\n{'=' * 50}\n")
                return

            # Display records
            display_count = len(power_data) if max_records is None else min(max_records, len(power_data))

            for idx, record in enumerate(power_data[:display_count], 1):
                upload_time = record.get('uploadTime', 'N/A')
                print(f"Record {idx} - {upload_time}")
                print(f"  PV Power:            {record.get('ppv', 0):>10.2f} W")
                print(f"  Battery Power:       {record.get('cobat', 0):>10.2f} W")
                print(f"  Load:                {record.get('load', 0):>10.2f} W")
                print(f"  Grid Charge:         {record.get('gridCharge', 0):>10.2f} W")
                print(f"  Feed-in:             {record.get('feedIn', 0):>10.2f} W")
                print(f"  Charging Pile:       {record.get('pChargingPile', 0):>10.2f} W")
                print()

            if max_records and len(power_data) > max_records:
                print(f"... and {len(power_data) - max_records} more records")
                print("(Use max_records=None to see all records)")

            print(f"{'=' * 50}\n")
        else:
            print(f"Failed to retrieve data: {data}")

    def print_charge_config(self, system_sn: str):
        """
        Retrieve and print charging configuration

        Args:
            system_sn: System Serial Number
        """
        data = self.get_charge_config(system_sn)

        if data.get("code") == 200:
            config = data.get("data", {})

            print(f"\n{'=' * 50}")
            print(f"Charging Configuration")
            print(f"System: {system_sn}")
            print(f"{'=' * 50}\n")

            grid_charge_enabled = config.get('gridCharge', 0)
            grid_charge_status = "Enabled" if grid_charge_enabled == 1 else "Disabled"

            print(f"Grid Charging:         {grid_charge_status}")
            print(f"Charging Stops at:     {config.get('batHighCap', 0):>10.2f} % SOC")

            print("\nCHARGING PERIODS:")
            print(f"  Period 1:            {config.get('timeChaf1', 'N/A')} - {config.get('timeChae1', 'N/A')}")
            print(f"  Period 2:            {config.get('timeChaf2', 'N/A')} - {config.get('timeChae2', 'N/A')}")

            print(f"\n{'=' * 50}\n")
        else:
            print(f"Failed to retrieve data: {data}")


def demo(app_id: str, app_secret: str, system_sn: str, query_date: str = None):
    """
    Run a demonstration of all AlphaESS API endpoints

    Args:
        app_id: AlphaESS App ID
        app_secret: AlphaESS App Secret
        system_sn: System Serial Number
        query_date: Optional date in YYYY-MM-DD format (defaults to today)
    """
    from datetime import datetime

    # Default to today if no date provided
    if query_date is None:
        query_date = datetime.now().strftime("%Y-%m-%d")

    # Create client instance
    client = AlphaESSClient(app_id, app_secret)

    print("\n" + "=" * 60)
    print("AlphaESS API Client - Demo")
    print(f"Query Date: {query_date}")
    print("=" * 60)

    # Example 1: Get list of all systems
    print("\n1. Getting System List...")
    client.print_system_list()

    # Example 2: Get system summary (daily/total stats)
    print("\n2. Getting System Summary...")
    client.print_system_summary(system_sn)

    # Example 3: Get real-time power data
    print("\n3. Getting Real-time Power Data...")
    client.print_power_data(system_sn)

    # Example 4: Get charging configuration
    print("\n4. Getting Charging Configuration...")
    client.print_charge_config(system_sn)

    # Example 5: Get energy data for a specific day
    print("\n5. Getting Energy Data for a Specific Day...")
    client.print_one_day_energy(system_sn, query_date)

    # Example 6: Get power timeline for a specific day (showing first 5 records)
    print("\n6. Getting Power Timeline for a Specific Day...")
    client.print_one_day_power(system_sn, query_date, max_records=5)

    print("\n" + "=" * 60)
    print("Demo Complete!")
    print("=" * 60 + "\n")


# Example usage
if __name__ == "__main__":
    import argparse
    from datetime import datetime

    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="AlphaESS API Client - Retrieve solar battery system data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Query today's data
  python alphaess_api.py --app-id alphaef7900ee81dbbce9 --app-secret c2d2ef6c047c49678e2c332fb2d74c3c --system-sn AL2104XXXXXXXX

  # Query specific date
  python alphaess_api.py --app-id alphaef7900ee81dbbce9 --app-secret c2d2ef6c047c49678e2c332fb2d74c3c --system-sn AL2104XXXXXXXX --date 2024-01-15

  # Use environment variables (recommended for security)
  export ALPHAESS_APP_ID=alphaef7900ee81dbbce9
  export ALPHAESS_APP_SECRET=c2d2ef6c047c49678e2c332fb2d74c3c
  export ALPHAESS_SYSTEM_SN=AL2104XXXXXXXX
  python alphaess_api.py
        """
    )

    parser.add_argument(
        "--app-id",
        type=str,
        required=False,
        help="AlphaESS App ID (or set ALPHAESS_APP_ID environment variable)"
    )

    parser.add_argument(
        "--app-secret",
        type=str,
        required=False,
        help="AlphaESS App Secret (or set ALPHAESS_APP_SECRET environment variable)"
    )

    parser.add_argument(
        "--system-sn",
        type=str,
        required=False,
        help="System Serial Number (or set ALPHAESS_SYSTEM_SN environment variable)"
    )

    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Query date in YYYY-MM-DD format (defaults to today)"
    )

    args = parser.parse_args()

    # Get credentials from args or environment variables
    import os

    app_id = args.app_id or os.getenv("ALPHAESS_APP_ID")
    app_secret = args.app_secret or os.getenv("ALPHAESS_APP_SECRET")
    system_sn = args.system_sn or os.getenv("ALPHAESS_SYSTEM_SN")

    # Validate required parameters
    if not app_id or not app_secret or not system_sn:
        parser.print_help()
        print("\n" + "=" * 60)
        print("ERROR: Missing required credentials!")
        print("=" * 60)
        print("\nPlease provide credentials via:")
        print("  1. Command-line arguments (--app-id, --app-secret, --system-sn)")
        print("  2. Environment variables (ALPHAESS_APP_ID, ALPHAESS_APP_SECRET, ALPHAESS_SYSTEM_SN)")
        print("\n")
        import sys

        sys.exit(1)

    # Run the demo
    demo(app_id, app_secret, system_sn, args.date)
