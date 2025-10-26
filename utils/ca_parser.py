"""
Contract Address (CA) parser utility - REWRITTEN
REPLACE: utils/ca_parser.py WITH THIS FILE
"""

import re
from typing import Optional, List


class CAParser:
    """Parse Solana contract addresses from natural language."""
    
    # Base58 alphabet (excludes 0, O, I, l to avoid confusion)
    BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    
    # Solana addresses are 32-44 characters of base58
    MIN_LENGTH = 32
    MAX_LENGTH = 44
    
    @classmethod
    def extract_contract_address(cls, text: str) -> Optional[str]:
        """
        Extract a Solana contract address from text.
        
        This method is very lenient and will find ANY valid-looking
        Solana address in the text.
        
        Args:
            text: Input text that may contain a contract address
            
        Returns:
            Solana contract address or None
        """
        if not text:
            return None
        
        # Clean up the text - remove extra whitespace
        text = text.strip()
        
        # Split by common separators
        # This handles: "check CA: ABC123..." or "ABC123... is this safe?"
        words = re.split(r'[\s,;:.!?\n\r]+', text)
        
        # Check each word
        for word in words:
            word = word.strip()
            
            # Quick length check first (faster)
            if cls.MIN_LENGTH <= len(word) <= cls.MAX_LENGTH:
                # Check if it's valid base58
                if cls.is_valid_solana_address(word):
                    return word
        
        # Fallback: Try to find any base58 sequence in the text
        # Pattern: continuous sequence of base58 characters
        pattern = f'[{re.escape(cls.BASE58_ALPHABET)}]{{{cls.MIN_LENGTH},{cls.MAX_LENGTH}}}'
        matches = re.findall(pattern, text)
        
        for match in matches:
            if cls.is_valid_solana_address(match):
                return match
        
        return None
    
    @classmethod
    def is_valid_solana_address(cls, address: str) -> bool:
        """
        Validate if a string is a valid Solana address format.
        
        Args:
            address: String to validate
            
        Returns:
            True if valid format, False otherwise
        """
        if not address:
            return False
        
        # Check length
        if not (cls.MIN_LENGTH <= len(address) <= cls.MAX_LENGTH):
            return False
        
        # Check all characters are in base58 alphabet
        for char in address:
            if char not in cls.BASE58_ALPHABET:
                return False
        
        return True
    
    @classmethod
    def extract_all_addresses(cls, text: str) -> List[str]:
        """
        Extract all contract addresses from text.
        
        Args:
            text: Input text
            
        Returns:
            List of contract addresses found
        """
        if not text:
            return []
        
        addresses = []
        words = re.split(r'[\s,;:.!?\n\r]+', text)
        
        for word in words:
            word = word.strip()
            if cls.is_valid_solana_address(word):
                addresses.append(word)
        
        # Also try pattern matching
        pattern = f'[{re.escape(cls.BASE58_ALPHABET)}]{{{cls.MIN_LENGTH},{cls.MAX_LENGTH}}}'
        matches = re.findall(pattern, text)
        
        for match in matches:
            if cls.is_valid_solana_address(match) and match not in addresses:
                addresses.append(match)
        
        return addresses
    
    @classmethod
    def has_contract_address(cls, text: str) -> bool:
        """
        Check if text contains a contract address.
        
        Args:
            text: Input text
            
        Returns:
            True if at least one CA is found, False otherwise
        """
        return cls.extract_contract_address(text) is not None


# Quick self-test when imported
if __name__ == "__main__":
    parser = CAParser()
    
    # Test cases
    tests = [
        "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
        "is this a rugpull? DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
        "Check CA: 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        "hello world"
    ]
    
    print("Quick CA Parser Test:")
    for test in tests:
        result = parser.extract_contract_address(test)
        print(f"Input: {test[:50]}...")
        print(f"Found: {result}\n")