#!/usr/bin/env python3
# ArgFuscator - Command-line obfuscation tool
# Based on the document about command-line obfuscation techniques

import argparse
import random
import json
import os
import sys
import re
from typing import Dict, List, Set, Tuple, Optional, Any

class CommandLineObfuscator:
    def __init__(self, config_file=None):
        """Initialize the obfuscator with optional config file."""
        self.modifiers = {
            "CharacterSubstitution": self._apply_character_substitution,
            "RandomCase": self._apply_random_case,
            "OptionCharacterSubstitution": self._apply_option_character_substitution,
            "CharacterInsertion": self._apply_character_insertion,
            "QuoteInsertion": self._apply_quote_insertion,
            "PathTraversal": self._apply_path_traversal,
            "ValueTransformation": self._apply_value_transformation,
            "OptionReordering": self._apply_option_reordering,
            "OptionSeparatorInsertion": self._apply_option_separator_insertion,
            "OptionSeparatorDeletion": self._apply_option_separator_deletion
        }
        
        # Default configurations for Windows executables
        self.windows_programs = [
            "taskkill", "reg", "powershell", "certutil", "mshta", "msiexec", 
            "ping", "curl", "cmd", "wmic", "bitsadmin", "sc", "wscript", 
            "cscript", "regsvr32", "rundll32"
        ]
        
        # Default configurations for Unix executables
        self.unix_programs = [
            "curl", "wget", "bash", "sh", "osascript", "python", "perl",
            "nc", "ncat", "ssh", "scp", "rsync"
        ]
        
        # Character substitution mappings
        self.char_substitutions = {
            "a": "ᵃ", "b": "ᵇ", "c": "ᶜ", "d": "ᵈ", "e": "ᵉ", "f": "ᶠ", 
            "g": "ᵍ", "h": "ʰ", "j": "ʲ", "k": "ᵏ", "l": "ˡ", "m": "ᵐ", 
            "n": "ⁿ", "o": "ᵒ", "p": "ᵖ", "r": "ʳ", "s": "ˢ", "t": "ᵗ", 
            "u": "ᵘ", "v": "ⱽ", "w": "ʷ", "x": "ˣ", "y": "ʸ", "z": "ᶻ"
        }
        
        # Characters that can be inserted without affecting execution
        self.insertion_chars = [
            "\u00ad", "\u034f", "\u0378", "\u0379", "\u037f", "\u0380", 
            "\u0381", "\u0382", "\u0383", "\u038b", "\u038d", "\u03a2", 
            "\u0530", "\u0557", "\u0558", "\u058b", "\u058c"
        ]
        
        # Option characters for substitution
        self.option_chars = ["-", "/", "\ufe63"]
        
        # Load custom configuration if provided
        if config_file:
            self._load_config(config_file)
    
    def _load_config(self, config_file):
        """Load custom configuration from a JSON file."""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                
            if "char_substitutions" in config:
                self.char_substitutions.update(config["char_substitutions"])
                
            if "insertion_chars" in config:
                self.insertion_chars.extend(config["insertion_chars"])
                
            if "option_chars" in config:
                self.option_chars = config["option_chars"]
                
            if "windows_programs" in config:
                self.windows_programs.extend(config["windows_programs"])
                
            if "unix_programs" in config:
                self.unix_programs.extend(config["unix_programs"])
                
        except Exception as e:
            print(f"Error loading configuration: {e}")
    
    def _tokenize_command(self, command):
        """Split a command into tokens with types."""
        # Basic tokenization by whitespace, preserving quotes
        in_quotes = False
        quote_char = None
        tokens = []
        current_token = ""
        
        for char in command:
            if char in ['"', "'"]:
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                    current_token += char
                elif char == quote_char:
                    in_quotes = False
                    quote_char = None
                    current_token += char
                else:
                    current_token += char
            elif char.isspace() and not in_quotes:
                if current_token:
                    tokens.append(current_token)
                    current_token = ""
            else:
                current_token += char
                
        if current_token:
            tokens.append(current_token)
        
        # Now classify each token
        classified_tokens = []
        for i, token in enumerate(tokens):
            if i == 0:
                classified_tokens.append({"type": "command", "value": token})
            elif token.startswith("-") or token.startswith("/"):
                classified_tokens.append({"type": "argument", "value": token})
            elif ":" in token and ("http" in token.lower() or "https" in token.lower()):
                classified_tokens.append({"type": "url", "value": token})
            elif "\\" in token or "/" in token:
                classified_tokens.append({"type": "file_path", "value": token})
            elif token.startswith("HKLM\\") or token.startswith("HKCU\\"):
                classified_tokens.append({"type": "reg_path", "value": token})
            else:
                classified_tokens.append({"type": "argument", "value": token})
                
        return classified_tokens
    
    def _apply_character_substitution(self, token, probability=0.3):
        """Apply character substitution to a token."""
        if random.random() > probability:
            return token
            
        if token["type"] not in ["argument", "command"]:
            return token
            
        result = ""
        for char in token["value"]:
            if char.lower() in self.char_substitutions and random.random() < probability:
                result += self.char_substitutions[char.lower()]
            else:
                result += char
                
        token["value"] = result
        return token
    
    def _apply_random_case(self, token, probability=0.5):
        """Apply random case to a token."""
        if random.random() > probability:
            return token
            
        if token["type"] not in ["argument", "command", "file_path"]:
            return token
            
        result = ""
        for char in token["value"]:
            if char.isalpha():
                if random.random() < 0.5:
                    result += char.upper()
                else:
                    result += char.lower()
            else:
                result += char
                
        token["value"] = result
        return token
    
    def _apply_option_character_substitution(self, token, probability=0.4):
        """Apply option character substitution."""
        if random.random() > probability:
            return token
            
        if token["type"] != "argument" or not (token["value"].startswith("-") or token["value"].startswith("/")):
            return token
            
        # Get current option character
        current_option = token["value"][0]
        
        # Choose a different option character
        available_options = [c for c in self.option_chars if c != current_option]
        if not available_options:
            return token
            
        new_option = random.choice(available_options)
        token["value"] = new_option + token["value"][1:]
        return token
    
    def _apply_character_insertion(self, token, probability=0.3):
        """Insert invisible/ignored characters."""
        if random.random() > probability:
            return token
            
        if token["type"] not in ["argument"]:
            return token
            
        result = ""
        for char in token["value"]:
            result += char
            if random.random() < probability:
                result += random.choice(self.insertion_chars)
                
        token["value"] = result
        return token
    
    def _apply_quote_insertion(self, token, probability=0.3):
        """Insert quotes within a token."""
        if random.random() > probability:
            return token
            
        if token["type"] not in ["argument", "file_path", "url"]:
            return token
            
        # Don't apply if already quoted
        if (token["value"].startswith('"') and token["value"].endswith('"')) or \
           (token["value"].startswith("'") and token["value"].endswith("'")):
            return token
            
        result = ""
        in_quotes = False
        
        for char in token["value"]:
            if random.random() < probability and not in_quotes and char not in ['"', "'"]:
                result += '"'
                result += char
                result += '"'
            else:
                result += char
                
        token["value"] = result
        return token
    
    def _apply_path_traversal(self, token, probability=0.4):
        """Apply path traversal obfuscation."""
        if random.random() > probability:
            return token
            
        if token["type"] != "file_path":
            return token
            
        # Split the path into components
        if '\\' in token["value"]:
            # Windows path
            sep = '\\'
            parts = token["value"].split('\\')
        elif '/' in token["value"]:
            # Unix path
            sep = '/'
            parts = token["value"].split('/')
        else:
            return token
            
        # Insert path traversal sequences
        if len(parts) > 2:
            for i in range(1, len(parts)-1):
                if random.random() < probability:
                    # Insert a ../ and then return to the correct directory
                    parts.insert(i, '..')
                    parts.insert(i+1, parts[i-1])
                    
        token["value"] = sep.join(parts)
        return token
    
    def _apply_value_transformation(self, token, probability=0.3):
        """Apply value transformation where possible."""
        if random.random() > probability:
            return token
            
        # Example: transform IP addresses
        if token["type"] == "argument" and re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', token["value"]):
            # Convert IP to decimal
            try:
                parts = token["value"].split('.')
                decimal_ip = (int(parts[0]) << 24) + (int(parts[1]) << 16) + (int(parts[2]) << 8) + int(parts[3])
                token["value"] = str(decimal_ip)
            except:
                pass
                
        return token
    
    def _apply_option_reordering(self, tokens, probability=0.4):
        """Reorder options where possible."""
        if random.random() > probability:
            return tokens
            
        # Find all option tokens
        option_indices = [i for i, token in enumerate(tokens) 
                        if token["type"] == "argument" and 
                        (token["value"].startswith("-") or token["value"].startswith("/"))]
        
        if len(option_indices) < 2:
            return tokens
            
        # Shuffle some of them
        shuffle_count = random.randint(1, len(option_indices))
        indices_to_shuffle = random.sample(option_indices, shuffle_count)
        
        # Extract the tokens to shuffle
        tokens_to_shuffle = [tokens[i] for i in sorted(indices_to_shuffle)]
        random.shuffle(tokens_to_shuffle)
        
        # Replace the original tokens with shuffled ones
        for new_idx, old_idx in enumerate(sorted(indices_to_shuffle)):
            tokens[old_idx] = tokens_to_shuffle[new_idx]
            
        return tokens
    
    def _apply_option_separator_insertion(self, token, probability=0.3):
        """Insert space between option and value."""
        if random.random() > probability:
            return token
            
        if token["type"] != "argument":
            return token
            
        # Match patterns like -O- or --output=file
        match1 = re.match(r'^(-+)(\w+)(-)$', token["value"])
        match2 = re.match(r'^(-+)(\w+)(=)(.+)$', token["value"])
        
        if match1:
            token["value"] = f"{match1.group(1)}{match1.group(2)} {match1.group(3)}"
        elif match2:
            token["value"] = f"{match2.group(1)}{match2.group(2)} {match2.group(3)}{match2.group(4)}"
            
        return token
    
    def _apply_option_separator_deletion(self, token, probability=0.3):
        """Remove space between option and value."""
        if random.random() > probability:
            return token
            
        if token["type"] != "argument":
            return token
            
        # If this token is an option with a value in the next token, we'll handle it at the command level
        return token
    
    def _handle_option_separator_deletion(self, tokens, probability=0.3):
        """Handle option separator deletion across tokens."""
        if random.random() > probability:
            return tokens
            
        result = []
        i = 0
        while i < len(tokens) - 1:
            current = tokens[i]
            next_token = tokens[i+1]
            
            if (current["type"] == "argument" and 
                (current["value"].startswith("-") or current["value"].startswith("/")) and
                not (current["value"].endswith("=") or current["value"].endswith(":")) and
                next_token["type"] in ["argument", "file_path", "url"]):
                
                if random.random() < probability:
                    # Combine the tokens
                    current["value"] = current["value"] + next_token["value"]
                    result.append(current)
                    i += 2
                    continue
                    
            result.append(current)
            i += 1
            
        # Don't forget the last token if we didn't combine it
        if i < len(tokens):
            result.append(tokens[i])
            
        return result
    
    def obfuscate_command(self, command, techniques=None, probabilities=None):
        """
        Obfuscate a command using selected techniques.
        
        Args:
            command: The command to obfuscate
            techniques: List of techniques to apply, or None for all
            probabilities: Dict of technique->probability, or None for defaults
        
        Returns:
            The obfuscated command
        """
        # Tokenize the command
        tokens = self._tokenize_command(command)
        
        # Default probabilities
        default_probs = {
            "CharacterSubstitution": 0.3,
            "RandomCase": 0.5,
            "OptionCharacterSubstitution": 0.4,
            "CharacterInsertion": 0.3,
            "QuoteInsertion": 0.3,
            "PathTraversal": 0.4,
            "ValueTransformation": 0.3,
            "OptionReordering": 0.4,
            "OptionSeparatorInsertion": 0.3,
            "OptionSeparatorDeletion": 0.3
        }
        
        probs = default_probs
        if probabilities:
            probs.update(probabilities)
        
        # Default to all techniques
        if not techniques:
            techniques = list(self.modifiers.keys())
        
        # Special handling for reordering and separator deletion (operate on all tokens)
        if "OptionReordering" in techniques:
            tokens = self._apply_option_reordering(tokens, probs["OptionReordering"])
            techniques.remove("OptionReordering")
            
        if "OptionSeparatorDeletion" in techniques:
            tokens = self._handle_option_separator_deletion(tokens, probs["OptionSeparatorDeletion"])
            techniques.remove("OptionSeparatorDeletion")
        
        # Apply token-level modifiers randomly
        for i, token in enumerate(tokens):
            for technique in techniques:
                if technique in self.modifiers:
                    tokens[i] = self.modifiers[technique](token, probs[technique])
        
        # Rebuild the command
        result = ""
        for token in tokens:
            result += token["value"] + " "
            
        return result.strip()

def main():
    parser = argparse.ArgumentParser(description="ArgFuscator - Command-line argument obfuscation tool")
    parser.add_argument("command", help="Command to obfuscate")
    parser.add_argument("--config", "-c", help="Path to configuration file")
    parser.add_argument("--output", "-o", type=int, default=1, help="Number of obfuscated variants to generate")
    parser.add_argument("--techniques", "-t", nargs="+", help="Techniques to use (comma-separated)")
    parser.add_argument("--list-techniques", "-l", action="store_true", help="List available techniques")
    
    args = parser.parse_args()
    
    # Initialize the obfuscator with optional config
    obfuscator = CommandLineObfuscator(args.config)
    
    if args.list_techniques:
        print("Available obfuscation techniques:")
        for technique in obfuscator.modifiers.keys():
            print(f"  - {technique}")
        return
    
    # Parse techniques if provided
    techniques = None
    if args.techniques:
        techniques = []
        for t in args.techniques:
            techniques.extend(t.split(','))
    
    # Generate the requested number of variants
    for i in range(args.output):
        obfuscated = obfuscator.obfuscate_command(args.command, techniques)
        print(f"{i+1}: {obfuscated}")

if __name__ == "__main__":
    main()
