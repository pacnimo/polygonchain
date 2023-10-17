# QuickSwap Transaction Analyzer

A Python utility to monitor and analyze token swap transactions on the QuickSwap platform via the Polygon (Matic) network. The tool is designed to capture the latest token swaps and keep a count of swap occurrences for each token pair.

## Features:

- **Interacts with the QuickSwap Router** on the Polygon network.
- **Fetches the latest swap transactions** in real-time.
- **Decodes and extracts token information**.
- **Stores the frequency of token swaps** in a JSON file.

## Installation:

### Prerequisites:

Ensure you have Python 3.x installed. You'll also need the `web3` and `eth_abi` libraries. Install them using pip:

```bash
pip install web3 eth_abi
