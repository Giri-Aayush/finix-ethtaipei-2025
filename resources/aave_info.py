# resources/aave_info.py - Aave lending protocol information resources
from mcp.server.fastmcp import FastMCP

def register_aave_info_resources(mcp: FastMCP):
    """Register all Aave information resources with the MCP server."""
    
    @mcp.resource("info://aave")
    def get_aave_info() -> str:
        """Get information about Aave on Celo"""
        return """
About Aave on Celo:

Aave is a decentralized non-custodial liquidity protocol where users can participate as depositors or borrowers.
Depositors provide liquidity to the market to earn a passive income, while borrowers can borrow in an overcollateralized or undercollateralized fashion.

Important Information:
• Aave is only available on Celo mainnet (not available on Alfajores testnet)
• All operations require actual funds on mainnet
• When you deposit CELO to Aave, you receive aCELO tokens representing your position
• You can only borrow up to a certain percentage of your deposited collateral value

Available Operations:

1. Supply/Deposit Operations:
   • supply_celo: Deposit CELO into Aave to earn interest
   • withdraw_celo: Withdraw your CELO from Aave
   • set_celo_collateral: Enable or disable using your CELO as collateral

2. Borrow/Repay Operations:
   • borrow_usdc: Borrow USDC against your CELO collateral
   • repay_usdc: Repay your borrowed USDC debt

3. Session Management:
   • create_aave_session: Create a secure session for Aave operations
   • add_aave_private_key: Add your private key to your session
   • clear_aave_session: Manually clear your session

Security Considerations:
• Private keys are only stored in memory temporarily
• Sessions automatically expire after 5 minutes
• Always clear your session after completing operations
• All transactions are performed on mainnet with real assets
• Always verify transaction details before confirming

Current Aave Celo Market Information:
• Lending Pool Address: 0x3E59A31363E2ad014dcbc521c4a0d5757d9f3402
• CELO Token Address: 0x471EcE3750Da237f93B8E339c536989b8978a438
• USDC Token Address: 0xcebA9300f2b948710d2653dD7B07f33A8B32118C
• Explorer: https://celoscan.io

For more information, visit:
• Aave Documentation: https://docs.aave.com
• Celo Documentation: https://docs.celo.org
"""

    @mcp.resource("aave://workflow")
    def get_aave_workflow() -> str:
        """Get step-by-step workflow for using Aave on Celo"""
        return """
Step-by-Step Workflow for Using Aave on Celo:

1. Creating a Session and Adding Your Private Key:
   a. Create an Aave session:
      • "Create an Aave session for my Celo address 0x123..."
   b. Add your private key to the session:
      • "Add my private key to my Aave session"
      • Your private key will be stored temporarily and securely

2. Supplying CELO to Aave:
   a. Supply CELO to earn interest:
      • "Supply 0.5 CELO to Aave"
   b. Enable CELO as collateral:
      • "Set my CELO as collateral in Aave"
   c. You can now borrow against your supplied CELO

3. Borrowing USDC Against Your CELO:
   a. Borrow USDC:
      • "Borrow 5 USDC from Aave"
   b. The USDC will be sent to your wallet

4. Repaying Your USDC Loan:
   a. Repay your USDC debt:
      • "Repay 5 USDC to Aave" or "Repay all my USDC debt to Aave"
   b. This reduces or eliminates your debt position

5. Withdrawing Your CELO:
   a. Withdraw your deposited CELO:
      • "Withdraw 0.5 CELO from Aave" or "Withdraw all my CELO from Aave"
   b. Your aCELO tokens will be exchanged for CELO

Important Notes:
• Each operation requires its own session for security
• Sessions expire after 5 minutes
• You must have sufficient funds for all operations
• All operations happen on Celo mainnet with real assets
• Always clear your session after completing operations

Example Full Workflow:
1. "Create an Aave session for my address 0x123..."
2. "Add my private key to my Aave session"
3. "Supply 1 CELO to Aave"
4. "Create a new Aave session for my address 0x123..."
5. "Add my private key to my Aave session"
6. "Set my CELO as collateral in Aave"
7. "Create a new Aave session for my address 0x123..."
8. "Add my private key to my Aave session"
9. "Borrow 10 USDC from Aave"
"""

    @mcp.resource("aave://risks")
    def get_aave_risks() -> str:
        """Get information about risks associated with using Aave"""
        return """
Risks of Using Aave Protocol on Celo:

1. Smart Contract Risk:
   • Despite rigorous security practices, smart contracts may contain vulnerabilities
   • The protocol could be exploited by malicious actors
   • Funds could potentially be lost in case of a smart contract failure

2. Liquidation Risk:
   • If your collateral falls below required levels, your position may be liquidated
   • Liquidation means your collateral is sold at a discount to repay your debt
   • Market volatility increases liquidation risk

3. Interest Rate Risk:
   • Interest rates on Aave are variable and change based on market conditions
   • Borrowing costs may increase unexpectedly
   • Supply APY may decrease over time

4. Market Risk:
   • Cryptocurrency prices are highly volatile
   • Rapid price decreases can lead to liquidation
   • Market conditions can change rapidly

5. Oracle Risk:
   • Aave relies on price oracles to determine asset values
   • Oracle failures or manipulations could affect protocol operations
   • Incorrect price data could lead to unexpected liquidations

6. UI/UX and Operational Risks:
   • User errors such as sending funds to wrong addresses
   • Private key mismanagement
   • Interacting with phishing sites or malicious interfaces

Risk Mitigation:
• Only use funds you can afford to lose
• Maintain a healthy collateralization ratio
• Monitor your positions regularly
• Understand protocol parameters before interacting
• Keep your private keys secure
• Always verify transaction details before confirming

Remember: DeFi protocols like Aave are powerful financial tools but come with inherent risks. Do your own research and proceed with caution.
"""