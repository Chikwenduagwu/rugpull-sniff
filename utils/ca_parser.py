import re
from typing import Optional, List


class CAParser:
    """Parse Solana contract addresses from natural language."""
    
    
    BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    
    
    MIN_LENGTH = 32
    MAX_LENGTH = 44
    
    @classmethod
    def extract_contract_address(cls, text: str) -> Optional[str]:
        """
        Extract a Solana contract address from text.
        
        FIXED: More aggressive detection
        
        Args:
            text: Input text that may contain a contract address
            
        Returns:
            Solana contract address or None
        """
        if not text:
            return None
        
        text = text.strip()
        
        
        if cls.MIN_LENGTH <= len(text) <= cls.MAX_LENGTH:
            if cls.is_valid_solana_address(text):
                return text
        
        
        words = re.split(r'[\s,;:.!?\n\r\t]+', text)
        
        for word in words:
            word = word.strip()
            if cls.MIN_LENGTH <= len(word) <= cls.MAX_LENGTH:
                if cls.is_valid_solana_address(word):
                    return word
        
       
        pattern = f'[{re.escape(cls.BASE58_ALPHABET)}]{{{cls.MIN_LENGTH},{cls.MAX_LENGTH}}}'
        matches = re.findall(pattern, text)
        
        for match in matches:
            if cls.is_valid_solana_address(match):
                return match
        
        
        cleaned = re.sub(r'[^\w]', ' ', text)
        words = cleaned.split()
        for word in words:
            if cls.MIN_LENGTH <= len(word) <= cls.MAX_LENGTH:
                if cls.is_valid_solana_address(word):
                    return word
        
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
        
        
        if not (cls.MIN_LENGTH <= len(address) <= cls.MAX_LENGTH):
            return False
        
        
        for char in address:
            if char not in cls.BASE58_ALPHABET:
                return False
        
       
        if len(set(address)) < 10:  
            return False
        
        return True
    
    @classmethod
    def extract_all_addresses(cls, text: str) -> List[str]:
        """
        Extract all contract addresses from text.
        
        Args:
            text: Input text
            
        Returns:
            List of unique contract addresses found
        """
        if not text:
            return []
        
        addresses = set()  
        
        
        words = re.split(r'[\s,;:.!?\n\r\t]+', text)
        
        for word in words:
            word = word.strip()
            if cls.is_valid_solana_address(word):
                addresses.add(word)
        
        
        pattern = f'[{re.escape(cls.BASE58_ALPHABET)}]{{{cls.MIN_LENGTH},{cls.MAX_LENGTH}}}'
        matches = re.findall(pattern, text)
        
        for match in matches:
            if cls.is_valid_solana_address(match):
                addresses.add(match)
        
        return list(addresses)
    
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



if __name__ == "__main__":
    parser = CAParser()
    
    test_cases = [
        ("DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263", True),
        ("is this a rugpull? DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263", True),
        ("Check CA: 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU", True),
        ("7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU is this safe?", True),
        ("hello world", False),
        ("what is a rug pull", False),
    ]
    
    print("🧪 CA Parser Self-Test:\n")
    for text, should_find in test_cases:
        result = parser.extract_contract_address(text)
        status = "✅" if (result is not None) == should_find else "❌"
        print(f"{status} Input: {text[:50]}...")
        print(f"   Found: {result}\n")