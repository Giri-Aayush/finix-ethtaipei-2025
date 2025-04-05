# 🌍 Celo Explorer MCP

A powerful Model Context Protocol (MCP) server that allows Claude AI to interact directly with the Celo blockchain, Aave lending protocol, and Dune Analytics - all within your conversations.

![Celo Explorer MCP](https://celo.org/images/celo-logo.png)

## ✨ What is Celo Explorer MCP?

Celo Explorer MCP creates a seamless bridge between Claude AI and the Celo blockchain ecosystem. With this tool, you can:

- Check balances and transaction history for any Celo address
- Send CELO and Celo stablecoins directly from Claude
- Interact with Aave's DeFi platform to earn interest, borrow, and more
- Analyze Celo Governance Proposals using Dune Analytics

All of these operations happen securely through Claude Desktop, with no external websites needed.

## 📋 Feature Overview

### 🔍 Read-Only Operations
- View CELO, cUSD, and cEUR balances
- Check recent transactions
- List all tokens held by an address

### 💸 Transaction Operations
- Send CELO, cUSD, and cEUR to any address
- Sign messages with your private key
- Manage transaction sessions securely

### 📈 Aave DeFi Operations
- Supply assets to earn interest
- Use CELO as collateral
- Borrow stablecoins against your collateral
- Repay loans and withdraw deposits

### 📊 Dune Analytics
- Query Dune for Celo governance data
- Analyze proposal data and voting patterns
- Generate summaries and visualizations of governance activity

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- Claude Desktop installed
- A Celo wallet (for transaction operations)
- Dune Analytics API key (for analytics operations)

### Step-by-Step Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/celo-explorer-mcp.git
   cd celo-explorer-mcp
   ```

2. Install the required dependencies:
   ```bash
   pip install "mcp[cli]" web3 python-dotenv requests dune-client pandas
   ```

3. Create a `.env` file for your API keys (optional):
   ```bash
   # For Dune Analytics
   DUNE_API_KEY=your_dune_api_key
   ```

### Installing in Claude Desktop

**Using the MCP CLI tool (Recommended)**

```bash
mcp install server.py --name "Celo Explorer"
```

**Manual configuration**

1. Create or edit Claude Desktop configuration file:

   - On macOS:
     ```bash
     mkdir -p ~/Library/Application\ Support/Claude/
     nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
     ```

   - On Windows:
     ```bash
     mkdir -p "%APPDATA%\Claude"
     notepad "%APPDATA%\Claude\claude_desktop_config.json"
     ```

2. Add the following configuration (replace with your actual path):
   ```json
   {
     "mcpServers": {
       "Celo Explorer": {
         "command": "python3",
         "args": [
           "/full/path/to/celo-explorer-mcp/server.py"
         ]
       }
     }
   }
   ```

3. Restart Claude Desktop

## 📚 Detailed Usage Guide

### 🔍 Basic Celo Operations

#### Checking Address Balances

**Example 1: View all token balances for an address**

```
What's the balance of this Celo address: 0x765DE816845861e75A25fCA122bb6898B8B1282a?
```

Claude will respond with:
```
CELO Balance: 42.561 CELO
cUSD Balance: 15.75 cUSD
cEUR Balance: 0.00 cEUR
```

**Example 2: Check a specific token balance**

```
How much cUSD does 0x765DE816845861e75A25fCA122bb6898B8B1282a have?
```

#### Viewing Transaction History

**Example: See recent transactions**

```
Show me the last 5 transactions for 0x765DE816845861e75A25fCA122bb6898B8B1282a
```

Claude will display:
```
Recent transactions for 0x765DE816845861e75A25fCA122bb6898B8B1282a:

1. Transaction Hash: 0x89d2...
   Type: Transfer
   Value: 1.5 CELO
   To: 0x123...
   Timestamp: 2023-08-15 14:32:45
   
2. Transaction Hash: 0x7fed...
   Type: Contract Interaction (Ubeswap)
   Value: 0 CELO
   To: 0xUbeswap...
   Timestamp: 2023-08-14 09:12:33
   
[...]
```

### 💸 Sending Transactions

#### Sending CELO

**Example: Send CELO to another address**

```
I want to send 0.5 CELO to 0x123456789abcdef123456789abcdef123456789
```

Claude will guide you through the process:

1. First, it will create a transaction session:
   ```
   Created a new transaction session. This session will expire in 5 minutes.
   ```

2. Then ask for your private key:
   ```
   To proceed with sending CELO, please provide your private key.
   Note: Your private key will be stored temporarily in memory and will be cleared after the transaction or after 5 minutes.
   ```

3. After you provide your private key, it will confirm transaction details:
   ```
   Preparing to send 0.5 CELO to 0x123456789abcdef123456789abcdef123456789
   Current gas price: 0.000000025 CELO
   Estimated transaction fee: 0.00052 CELO
   Total amount (including fee): 0.50052 CELO
   
   Would you like to proceed with this transaction? (yes/no)
   ```

4. Upon confirmation, it will submit and report the status:
   ```
   Transaction submitted successfully!
   Transaction hash: 0x9876543210abcdef9876543210abcdef9876543210abcdef9876543210abcdef
   You can view this transaction on the Celo Explorer: https://explorer.celo.org/tx/0x9876543210abcdef9876543210abcdef9876543210abcdef9876543210abcdef
   
   Your transaction session has been cleared for security.
   ```

#### Sending Stablecoins (cUSD, cEUR)

**Example: Send cUSD to another address**

```
I need to send 5 cUSD to 0x123456789abcdef123456789abcdef123456789
```

The process is similar to sending CELO, with Claude guiding you through each step.

### 📈 Aave DeFi Operations

#### Supplying Assets to Earn Interest

**Example: Supply CELO to Aave**

```
I want to supply 2 CELO to Aave to earn interest
```

Claude will guide you through:

1. Creating an Aave session:
   ```
   Created a new Aave session. This session will expire in 5 minutes.
   ```

2. Requesting your private key:
   ```
   To proceed with supplying CELO to Aave, please provide your private key.
   Note: Your private key will be stored temporarily in memory and will be cleared after the operation or after 5 minutes.
   ```

3. Showing current rates and confirming:
   ```
   Current Aave deposit APY for CELO: 2.45%
   Preparing to supply 2 CELO to Aave
   Estimated gas fee: 0.00062 CELO
   
   Would you like to proceed? (yes/no)
   ```

4. Upon confirmation, submitting the transaction:
   ```
   Transaction submitted successfully!
   Transaction hash: 0xabc123def456abc123def456abc123def456abc123def456abc123def456
   You can view this transaction on the Celo Explorer: https://explorer.celo.org/tx/0xabc123def456abc123def456abc123def456abc123def456abc123def456
   
   You have successfully supplied 2 CELO to Aave. You will now start earning interest at the current rate of 2.45% APY.
   Your Aave session has been cleared for security.
   ```

#### Borrowing Against Your Collateral

**Example: Borrow USDC using CELO as collateral**

```
I want to borrow 10 USDC against my CELO collateral on Aave
```

Claude will:

1. Check if you have enough collateral:
   ```
   Checking your Aave position...
   
   Your current deposits:
   - 5 CELO (worth approximately $25.00)
   
   Collateral Status:
   - CELO: Enabled as collateral
   
   Borrowing power: $12.50 (at 50% LTV)
   Current borrowing: $0.00
   Available to borrow: $12.50
   ```

2. Guide you through the borrowing process similar to the supply process.

#### Repaying Your Loans

**Example: Repay borrowed USDC**

```
I want to repay 5 USDC to Aave
```

Claude will guide you through the repayment process, showing your current loans and helping you submit the transaction.

### 📊 Dune Analytics for Governance

#### Viewing Active Governance Proposals

**Example: Check active CGPs**

```
Show me the currently active Celo Governance Proposals
```

Claude will query Dune and display:
```
Active Celo Governance Proposals:

CGP #42: Increase the Community Fund by 100,000 CELO
- Proposer: 0x789...
- Voting Period: Aug 10, 2023 - Aug 24, 2023
- Current Votes: 1.2M For (65%) / 650K Against (35%)
- Status: Active, 3 days remaining

CGP #43: Update validator requirements
- Proposer: 0xabc...
- Voting Period: Aug 12, 2023 - Aug 26, 2023
- Current Votes: 900K For (48%) / 970K Against (52%)
- Status: Active, 5 days remaining
```

#### Analyzing Voting Patterns

**Example: Analyze voter participation**

```
What has been the voter participation trend for Celo Governance over the past year?
```

Claude will query Dune and display:
```
Voter Participation in Celo Governance (Last 12 Months):

Monthly Participation Rate:
- Aug 2022: 24.3% of circulating CELO
- Sep 2022: 26.1%
- Oct 2022: 25.8%
- Nov 2022: 30.2%
- Dec 2022: 28.7%
- Jan 2023: 32.1%
- Feb 2023: 35.4%
- Mar 2023: 33.8%
- Apr 2023: 38.2%
- May 2023: 41.5%
- Jun 2023: 39.8%
- Jul 2023: 42.3%
- Aug 2023: 45.1%

Analysis:
- Overall trend shows increasing participation (+20.8%)
- Sharp increase in participation after the governance UI update in April 2023
- Highest participation for proposals related to protocol economics and validator requirements
```

#### Proposal Outcome Analysis

**Example: Get proposal success rates**

```
What percentage of CGPs have passed in 2023?
```

Claude will provide:
```
Celo Governance Proposal Outcomes (2023):

Total Proposals: 28
Passed: 19 (67.9%)
Rejected: 9 (32.1%)

Breakdown by Category:
- Protocol Upgrades: 7 proposed, 6 passed (85.7%)
- Treasury Management: 8 proposed, 5 passed (62.5%)
- Validator Operations: 5 proposed, 3 passed (60.0%)
- Community Initiatives: 8 proposed, 5 passed (62.5%)
```

## 🔒 Security Considerations

Celo Explorer MCP takes several measures to ensure your security:

- **Private keys are never stored on disk** - only temporarily in memory
- **Sessions automatically expire** after 5 minutes of inactivity
- **Sessions are cleared** after each transaction or operation
- You can **manually clear sessions** at any time with simple commands:
  ```
  Clear my transaction session
  ```
  or
  ```
  Clear my Aave session
  ```

## 🤝 Contributing

Contributions are welcome! Here are some ways you can contribute:

1. Add new functionality for Celo blockchain interactions
2. Integrate more DeFi protocols available on Celo (like Moola, UbeSwap)
3. Improve error handling and user experience
4. Add more analytics capabilities
5. Enhance documentation and examples

To contribute:
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is for educational and informational purposes only. Always verify transactions before confirming them. Use caution when handling private keys and sensitive information. The developers are not responsible for any loss of funds or other damages resulting from the use of this tool.