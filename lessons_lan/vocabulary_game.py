#!/usr/bin/env python3
"""
Vocabulary Memory Game
Helps remember: genesis, structure, energy, void, spirit, 
                 alright, saw, separated, everything, mixed, 
                 water, gather, valid, vegetation
"""

import random
import sys
import time
from typing import List, Dict, Tuple

# ============= VOCABULARY DATA =============
WORDS = {
    "genesis": "The beginning or origin of something",
    "structure": "The arrangement of and relations between parts",
    "energy": "The capacity to do work; vitality",
    "void": "Completely empty space; emptiness",
    "spirit": "The non-physical part of a person; soul or essence",
    "alright": "Satisfactory but not especially good; okay",
    "saw": "Past tense of see; or a tool for cutting",
    "separated": "Moved apart; divided",
    "everything": "All things; all objects or items",
    "mixed": "Combined or blended together",
    "water": "Clear liquid essential for life",
    "gather": "Bring together and take in",
    "valid": "Logical and factually sound; acceptable",
    "vegetation": "Plants and trees growing in an area"
}

# Bonus: Sentences for context
SENTENCES = {
    "genesis": "The genesis of the universe began with a big bang.",
    "structure": "The building's structure was reinforced with steel.",
    "energy": "Solar panels convert sunlight into energy.",
    "void": "The astronaut floated in the dark void of space.",
    "spirit": "Her spirit remained strong despite the challenges.",
    "alright": "The test results were alright, not amazing.",
    "saw": "I saw a shooting star last night.",
    "separated": "The twins were separated at birth.",
    "everything": "He packed everything he owned into boxes.",
    "mixed": "She mixed the paint colors to make purple.",
    "water": "Plants need water and sunlight to grow.",
    "gather": "Let's gather around the campfire.",
    "valid": "You need a valid ticket to enter.",
    "vegetation": "The jungle was thick with vegetation."
}

# ============= GAME MODES =============

def print_header(title: str):
    """Print a fancy header"""
    print("\n" + "="*60)
    print(f"  {title.upper()}")
    print("="*60)

def print_score(score: int, total: int):
    """Display current score"""
    print(f"\n📊 Score: {score}/{total} ({int(score/total*100) if total>0 else 0}%)")

def flash_card_game():
    """Flash card mode - show word, guess definition"""
    print_header("📇 FLASH CARDS")
    print("I'll show you a word. Type the definition!")
    print("Type 'hint' for a sentence, 'skip' to pass, or 'quit' to exit\n")
    
    words_list = list(WORDS.items())
    random.shuffle(words_list)
    
    score = 0
    total = len(words_list)
    
    for i, (word, definition) in enumerate(words_list, 1):
        print(f"\n🔤 Word {i}/{total}: {word.upper()}")
        
        while True:
            answer = input("Your definition: ").strip().lower()
            
            if answer == 'quit':
                print(f"\n👋 Goodbye! Final score: {score}/{total}")
                return
            elif answer == 'skip':
                print(f"📖 Answer: {definition}")
                break
            elif answer == 'hint':
                print(f"💡 Hint: {SENTENCES[word]}")
                continue
            
            # Check answer (flexible matching)
            if definition.lower() in answer or answer in definition.lower():
                print("✅ CORRECT! Well done! 🎉")
                score += 1
                break
            else:
                print(f"❌ Not quite. The answer is: {definition}")
                break
        
        print_score(score, total)
        time.sleep(0.5)
    
    print("\n🏆 GAME COMPLETE! 🏆")
    print_score(score, total)
    if score == total:
        print("🎯 PERFECT SCORE! You're a vocabulary master! 🌟")
    elif score >= total * 0.7:
        print("👍 Great job! Keep practicing!")
    else:
        print("📚 Good effort! Try again to improve!")

def multiple_choice():
    """Multiple choice game"""
    print_header("🎯 MULTIPLE CHOICE")
    print("Choose the correct definition!\n")
    
    words_list = list(WORDS.items())
    random.shuffle(words_list)
    
    score = 0
    total = len(words_list)
    
    for i, (word, correct_def) in enumerate(words_list, 1):
        # Get wrong answers (other definitions)
        wrong_answers = [defn for w, defn in WORDS.items() if w != word]
        wrong_answers = random.sample(wrong_answers, min(3, len(wrong_answers)))
        options = [correct_def] + wrong_answers
        random.shuffle(options)
        
        print(f"\n📝 Question {i}/{total}")
        print(f"What does '{word}' mean?")
        
        for idx, opt in enumerate(options, 1):
            print(f"  {idx}. {opt}")
        
        while True:
            try:
                choice = input("\nYour choice (1-4): ").strip()
                if choice.lower() == 'quit':
                    print(f"\n👋 Final score: {score}/{total}")
                    return
                
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(options):
                    if options[choice_idx] == correct_def:
                        print("✅ CORRECT! 🎉")
                        score += 1
                    else:
                        print(f"❌ Wrong! The answer is: {correct_def}")
                    break
                else:
                    print("Please choose 1-4")
            except ValueError:
                print("Please enter a number (1-4)")
        
        print_score(score, total)
        time.sleep(0.5)
    
    print("\n🏆 COMPLETE! 🏆")
    print_score(score, total)

def spelling_bee():
    """Spelling practice"""
    print_header("🐝 SPELLING BEE")
    print("I'll give you the definition. You spell the word!")
    print("Type 'hint' for first letter, 'quit' to exit\n")
    
    words_list = list(WORDS.items())
    random.shuffle(words_list)
    
    score = 0
    total = len(words_list)
    
    for i, (word, definition) in enumerate(words_list, 1):
        print(f"\n📖 Definition {i}/{total}: {definition}")
        
        attempts = 3
        while attempts > 0:
            answer = input(f"Spell the word ({attempts} attempts): ").strip().lower()
            
            if answer == 'quit':
                print(f"\n👋 Final score: {score}/{total}")
                return
            elif answer == 'hint':
                print(f"💡 First letter: '{word[0].upper()}', length: {len(word)} letters")
                continue
            elif answer == word:
                print("✅ PERFECT SPELLING! 🎉")
                score += 1
                break
            else:
                attempts -= 1
                if attempts > 0:
                    print(f"❌ Not quite. Try again! ({attempts} attempts left)")
                else:
                    print(f"❌ The correct spelling is: {word}")
        
        print_score(score, total)
        time.sleep(0.5)
    
    print("\n🏆 COMPLETE! 🏆")
    print_score(score, total)

def sentence_builder():
    """Create sentences using vocabulary words"""
    print_header("✍️ SENTENCE BUILDER")
    print("Create a sentence using each vocabulary word!")
    print("Get creative! Points for good sentences.\n")
    
    words_list = list(WORDS.keys())
    random.shuffle(words_list)
    
    score = 0
    total = len(words_list)
    
    for i, word in enumerate(words_list, 1):
        print(f"\n📝 Word {i}/{total}: {word.upper()}")
        print(f"Meaning: {WORDS[word]}")
        print(f"Example: {SENTENCES[word]}")
        
        sentence = input("Your sentence: ").strip()
        
        if sentence.lower() == 'quit':
            print(f"\n👋 Final score: {score}/{total}")
            return
        
        # Check if word is used correctly (simple check)
        if word.lower() in sentence.lower():
            # Length bonus
            length_bonus = min(5, len(sentence.split()) // 3)
            word_score = 5 + length_bonus
            score += word_score
            print(f"✅ Great sentence! +{word_score} points!")
            print(f"💡 Your sentence: {sentence}")
        else:
            print(f"❌ Try to include the word '{word}' in your sentence")
        
        print_score(score, total * 5)  # Max 5 points per word
    
    print("\n🏆 SENTENCE CHAMPION! 🏆")
    print(f"Final creative score: {score}/{total*5}")

def match_game():
    """Match words to definitions"""
    print_header("🃏 MATCHING GAME")
    print("Match each word to its definition!\n")
    
    words = list(WORDS.keys())
    definitions = list(WORDS.values())
    
    # Create shuffled pairs
    pairs = list(WORDS.items())
    random.shuffle(pairs)
    shuffled_words = [p[0] for p in pairs]
    shuffled_defs = [p[1] for p in pairs]
    random.shuffle(shuffled_defs)
    
    print("WORDS:")
    for i, word in enumerate(shuffled_words, 1):
        print(f"  {i}. {word}")
    
    print("\nDEFINITIONS:")
    for i, defn in enumerate(shuffled_defs, 1):
        print(f"  {i}. {defn[:50]}..." if len(defn) > 50 else f"  {i}. {defn}")
    
    print("\nMatch them by typing word number and definition number")
    print("Example: '1 3' matches word 1 to definition 3")
    print("Type 'quit' to exit\n")
    
    matches = {}
    score = 0
    total = len(words)
    
    while len(matches) < total:
        print(f"\n📊 Matched: {len(matches)}/{total}")
        try:
            cmd = input("Your match (word# def#): ").strip()
            if cmd.lower() == 'quit':
                break
            
            w_idx, d_idx = map(int, cmd.split())
            w_idx -= 1
            d_idx -= 1
            
            if w_idx in matches:
                print(f"⚠️ Word '{shuffled_words[w_idx]}' already matched!")
                continue
            
            word = shuffled_words[w_idx]
            definition = shuffled_defs[d_idx]
            
            if WORDS[word] == definition:
                print(f"✅ CORRECT! {word} = {definition}")
                matches[w_idx] = d_idx
                score += 1
            else:
                print(f"❌ No! {word} means: {WORDS[word]}")
                print(f"   {definition} is for another word")
                
        except (ValueError, IndexError):
            print("Please enter valid numbers like '1 3'")
    
    print(f"\n🎯 Final score: {score}/{total}")
    if score == total:
        print("🌟 PERFECT MATCH! You're a vocabulary wizard!")

def rapid_fire():
    """Timed rapid-fire quiz"""
    print_header("⚡ RAPID FIRE ⚡")
    print("Quick! Answer as fast as you can!")
    print("You have 5 seconds per question!\n")
    
    words_list = list(WORDS.items())
    random.shuffle(words_list)
    
    score = 0
    total = len(words_list)
    
    for word, definition in words_list:
        print(f"\n⏱️ What does '{word}' mean?")
        
        start_time = time.time()
        answer = input("→ ").strip().lower()
        elapsed = time.time() - start_time
        
        if answer == 'quit':
            break
        
        time_bonus = max(0, int(5 - elapsed))
        if definition.lower() in answer or answer in definition.lower():
            points = 1 + (time_bonus // 2)
            score += points
            print(f"✅ Correct! +{points} points ({elapsed:.1f}s)")
        else:
            print(f"❌ Wrong! Answer: {definition}")
        
        if elapsed > 5:
            print("💨 Too slow! Next question...")
    
    print(f"\n🏆 Final score: {score}")
    if score > total:
        print("⚡ LIGHTNING FAST! Amazing reflexes!")

def word_story():
    """Create a story using all words"""
    print_header("📖 WORD STORY")
    print("Create a short story using ALL the vocabulary words!")
    print("Be creative - the more words you use, the higher your score!\n")
    
    print("Your vocabulary words:")
    for i, word in enumerate(WORDS.keys(), 1):
        print(f"  {i:2}. {word}")
    
    print("\n✨ Write your story below (press Enter twice when done):")
    print("-" * 60)
    
    lines = []
    while True:
        line = input()
        if line == "" and lines and lines[-1] == "":
            break
        lines.append(line)
    
    story = " ".join(lines)
    
    # Count used words
    used_words = []
    for word in WORDS.keys():
        if word in story.lower():
            used_words.append(word)
    
    score = len(used_words)
    total = len(WORDS)
    
    print("\n" + "="*60)
    print("📊 STORY ANALYSIS")
    print(f"Words used: {score}/{total}")
    print(f"Words found: {', '.join(used_words)}")
    
    if score == total:
        print("\n🌟 AMAZING! You used EVERY word! Storytelling champion!")
    elif score >= total * 0.7:
        print("\n👍 Great story! Try to include more vocabulary next time!")
    else:
        missing = [w for w in WORDS.keys() if w not in used_words]
        print(f"\n💡 Missing words: {', '.join(missing)}")
    
    print("\n📝 YOUR STORY:")
    print("-" * 60)
    print(story)

def study_mode():
    """Review all words"""
    print_header("📚 STUDY MODE")
    print("Review all vocabulary words and definitions\n")
    
    for i, (word, definition) in enumerate(WORDS.items(), 1):
        print(f"{i:2}. {word.upper()}")
        print(f"    📖 {definition}")
        print(f"    💡 Example: {SENTENCES[word]}")
        print()
        input("Press Enter to continue...")
    
    print("\n✅ Study complete! Ready to play a game?")

# ============= MAIN MENU =============

def main():
    """Main game menu"""
    print_header("🎮 VOCABULARY ADVENTURE 🎮")
    print("Welcome! Let's master these words:")
    print(", ".join(WORDS.keys()))
    print("\nChoose your game mode:")
    
    modes = {
        "1": ("📇 Flash Cards", flash_card_game, "Classic Q&A practice"),
        "2": ("🎯 Multiple Choice", multiple_choice, "Pick from options"),
        "3": ("🐝 Spelling Bee", spelling_bee, "Spell the word correctly"),
        "4": ("✍️ Sentence Builder", sentence_builder, "Create your own sentences"),
        "5": ("🃏 Matching Game", match_game, "Match words to definitions"),
        "6": ("⚡ Rapid Fire", rapid_fire, "Timed challenge"),
        "7": ("📖 Word Story", word_story, "Create a story with all words"),
        "8": ("📚 Study Mode", study_mode, "Review all words"),
        "9": ("🎲 Random Mode", None, "Play a random game mode"),
        "0": ("🚪 Exit", None, "Quit the game")
    }
    
    while True:
        print("\n" + "-"*60)
        for key, (name, _, desc) in modes.items():
            print(f"  {key}. {name:15} - {desc}")
        
        choice = input("\n👉 Choose a game (0-9): ").strip()
        
        if choice == '0':
            print_header("👋 GOODBYE!")
            print("Keep practicing! You'll be a vocabulary master soon!")
            sys.exit(0)
        elif choice == '9':
            # Random mode excluding study and exit
            random_choice = random.choice([m for m in modes.keys() if m not in ['0', '8', '9']])
            print(f"\n🎲 Randomly selected: {modes[random_choice][0]}\n")
            modes[random_choice][1]()
        elif choice in modes and modes[choice][1] is not None:
            modes[choice][1]()
        else:
            print("❌ Invalid choice. Please try again!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("--gui", "-g"):
        from vocabulary_game_gui import main as gui_main

        gui_main()
    else:
        try:
            main()
        except KeyboardInterrupt:
            print("\n\n👋 Thanks for playing! Come back soon!")
            sys.exit(0)