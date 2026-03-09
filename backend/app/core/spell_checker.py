import re
from typing import List, Dict, Tuple
from spellchecker import SpellChecker
import language_tool_python
from sqlalchemy.orm import Session
from app import models


class SpellCheckEngine:
    def __init__(self, db: Session):
        self.db = db
        self.en_spell = SpellChecker()
        self.lang_tool = language_tool_python.LanguageTool('en-US')
        self.load_rules_from_db()
    
    def load_rules_from_db(self):
        self.whitelist_words = set()
        self.custom_dictionary = set()
        
        rules = self.db.query(models.SpellRule).all()
        for rule in rules:
            if rule.is_whitelist == 1:
                self.whitelist_words.add(rule.word.lower())
            else:
                self.custom_dictionary.add(rule.word.lower())
    
    def is_chinese(self, text: str) -> bool:
        return bool(re.search(r'[\u4e00-\u9fff]', text))
    
    def extract_words(self, text: str) -> List[str]:
        if self.is_chinese(text):
            return self.segment_chinese(text)
        else:
            words = re.findall(r'\b[a-zA-Z]+\b', text)
            return [word.lower() for word in words]
    
    def segment_chinese(self, text: str) -> List[str]:
        chinese_chars = re.findall(r'[\u4e00-\u9fff]+', text)
        words = []
        for chars in chinese_chars:
            if len(chars) >= 2:
                for i in range(len(chars)):
                    for j in range(i+1, min(i+5, len(chars)+1)):
                        word = chars[i:j]
                        if word in self.custom_dictionary or len(word) >= 2:
                            words.append(word)
        return words
    
    def check_text(self, text: str) -> List[Dict]:
        errors = []
        
        if self.is_chinese(text):
            chinese_errors = self.check_chinese(text)
            errors.extend(chinese_errors)
        
        english_errors = self.check_english(text)
        errors.extend(english_errors)
        
        return errors
    
    def check_english(self, text: str) -> List[Dict]:
        errors = []
        words = self.extract_words(text)
        
        for word in words:
            if word in self.whitelist_words:
                continue
            
            if word in self.custom_dictionary:
                continue
            
            if word not in self.en_spell:
                candidates = list(self.en_spell.candidates(word))[:5]
                
                grammar_errors = self.lang_tool.check(text)
                grammar_words = set()
                for error in grammar_errors:
                    if error.context:
                        error_word = error.context.strip().lower()
                        grammar_words.add(error_word)
                
                if word in grammar_words:
                    error_type = "grammar"
                else:
                    error_type = "spelling"
                
                errors.append({
                    "error_text": word,
                    "error_type": error_type,
                    "correct_suggest": ",".join(candidates) if candidates else "",
                    "severity_level": 2 if error_type == "spelling" else 3
                })
        
        return errors
    
    def check_chinese(self, text: str) -> List[Dict]:
        errors = []
        words = self.segment_chinese(text)
        
        for word in words:
            if word not in self.custom_dictionary and word not in self.whitelist_words:
                if len(word) >= 2:
                    pass
        
        return errors
    
    def reload_rules(self):
        self.load_rules_from_db()
        print("Spell check rules reloaded")
