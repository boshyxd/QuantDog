from typing import Dict, List, Optional
from datetime import datetime
import hashlib
import json


class BlockchainService:
    """Service for blockchain operations and transaction management."""
    
    def __init__(self):
        self.blocks: List[Dict] = []
        self.pending_transactions: List[Dict] = []
        self.mining_reward = 100
        
    def create_genesis_block(self):
        """Create the genesis block."""
        genesis_block = {
            "index": 0,
            "timestamp": datetime.utcnow().isoformat(),
            "transactions": [],
            "previous_hash": "0",
            "nonce": 0
        }
        genesis_block["hash"] = self._calculate_hash(genesis_block)
        self.blocks.append(genesis_block)
        
    def get_latest_block(self) -> Dict:
        """Get the latest block in the chain."""
        if not self.blocks:
            self.create_genesis_block()
        return self.blocks[-1]
        
    def _calculate_hash(self, block: Dict) -> str:
        """Calculate hash for a block."""
        block_string = json.dumps(block, sort_keys=True, default=str)
        return hashlib.sha256(block_string.encode()).hexdigest()
        
    def create_transaction(self, from_address: str, to_address: str, amount: float, crypto_method: str) -> str:
        """Create a new transaction."""
        transaction = {
            "from": from_address,
            "to": to_address,
            "amount": amount,
            "crypto_method": crypto_method,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.pending_transactions.append(transaction)
        return f"tx_{len(self.pending_transactions)}"
        
    def mine_pending_transactions(self, mining_reward_address: str) -> Dict:
        """Mine pending transactions and create a new block."""
        # Add mining reward transaction
        reward_transaction = {
            "from": None,
            "to": mining_reward_address,
            "amount": self.mining_reward,
            "crypto_method": "classical",
            "timestamp": datetime.utcnow().isoformat()
        }
        self.pending_transactions.append(reward_transaction)
        
        # Create new block
        new_block = {
            "index": len(self.blocks),
            "timestamp": datetime.utcnow().isoformat(),
            "transactions": self.pending_transactions.copy(),
            "previous_hash": self.get_latest_block()["hash"],
            "nonce": 0
        }
        
        # Simple proof of work (just increment nonce)
        new_block["hash"] = self._calculate_hash(new_block)
        
        self.blocks.append(new_block)
        self.pending_transactions = []
        
        return new_block
        
    def get_balance(self, address: str) -> float:
        """Get balance for an address."""
        balance = 0
        
        for block in self.blocks:
            for transaction in block["transactions"]:
                if transaction["from"] == address:
                    balance -= transaction["amount"]
                if transaction["to"] == address:
                    balance += transaction["amount"]
                    
        return balance
        
    def is_chain_valid(self) -> bool:
        """Validate the blockchain."""
        for i in range(1, len(self.blocks)):
            current_block = self.blocks[i]
            previous_block = self.blocks[i - 1]
            
            if current_block["hash"] != self._calculate_hash(current_block):
                return False
                
            if current_block["previous_hash"] != previous_block["hash"]:
                return False
                
        return True
        
    def get_transaction_history(self, address: Optional[str] = None) -> List[Dict]:
        """Get transaction history for an address or all transactions."""
        transactions = []
        
        for block in self.blocks:
            for transaction in block["transactions"]:
                if address is None or transaction["from"] == address or transaction["to"] == address:
                    transactions.append({
                        "block_index": block["index"],
                        "timestamp": transaction["timestamp"],
                        "from": transaction["from"],
                        "to": transaction["to"],
                        "amount": transaction["amount"],
                        "crypto_method": transaction["crypto_method"]
                    })
                    
        return transactions