#!/usr/bin/env python3
"""
Tkinter GUI for the vocabulary memory game.
Run: python vocabulary_game_gui.py
"""

from __future__ import annotations

import random
import time
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from typing import Callable, Dict, List, Optional, Tuple

from vocabulary_game import SENTENCES, WORDS

# Timed typing: each round gets this much less time (floor = BEAT_CLOCK_MIN_SEC).
BEAT_CLOCK_START_SEC = 20.0
BEAT_CLOCK_MIN_SEC = 3.0
BEAT_CLOCK_STEP_SEC = 1.25


def _flexible_definition_match(definition: str, answer: str) -> bool:
    d, a = definition.lower(), answer.strip().lower()
    return d in a or a in d


class VocabularyGameApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Vocabulary Adventure")
        self.minsize(720, 520)
        self.geometry("880x640")

        self._font_title = ("Segoe UI", 18, "bold")
        self._font_heading = ("Segoe UI", 12, "bold")
        self._font_body = ("Segoe UI", 11)
        self._font_mono = ("Consolas", 10)

        style = ttk.Style()
        if "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure("TButton", font=self._font_body, padding=6)
        style.configure("TLabelframe.Label", font=self._font_heading)

        self.container = ttk.Frame(self, padding=16)
        self.container.pack(fill=tk.BOTH, expand=True)

        self.show_menu()

    def clear_container(self) -> None:
        for w in self.container.winfo_children():
            w.destroy()

    def show_menu(self) -> None:
        self.clear_container()

        header = ttk.Label(
            self.container,
            text="Vocabulary Adventure",
            font=self._font_title,
        )
        header.pack(anchor=tk.W, pady=(0, 8))

        sub = ttk.Label(
            self.container,
            text="Vocabulary games below — or open Spelling Lab for spelling-first practice.",
            font=self._font_body,
        )
        sub.pack(anchor=tk.W, pady=(0, 12))

        lab_row = ttk.Frame(self.container)
        lab_row.pack(fill=tk.X, pady=(0, 16))
        ttk.Label(lab_row, text="Spelling Lab", font=self._font_heading).pack(side=tk.LEFT, padx=(0, 12))
        ttk.Label(
            lab_row,
            text="Flash, scramble, gaps, sprint — add your own word list. Spelling only.",
            font=self._font_body,
            wraplength=560,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(lab_row, text="Open Spelling Lab", command=self.start_spelling_lab).pack(side=tk.RIGHT)

        modes: List[Tuple[str, str, Callable[[], None]]] = [
            (
                "Beat the clock",
                "Read the clue aloud — type the word. Time shrinks each round.",
                self.start_beat_the_clock,
            ),
            ("Flash cards", "See a word — type the definition.", self.start_flash_cards),
            ("Multiple choice", "Pick the correct definition.", self.start_multiple_choice),
            ("Spelling bee", "Hear the definition — spell the word.", self.start_spelling_bee),
            ("Sentence builder", "Write a sentence using each word.", self.start_sentence_builder),
            ("Matching", "Match each word to its definition.", self.start_match_game),
            ("Rapid fire", "Answer quickly (5 seconds per word).", self.start_rapid_fire),
            ("Word story", "Write a story using the vocabulary.", self.start_word_story),
            ("Study mode", "Browse all words with examples.", self.start_study_mode),
            ("Random mode", "Play a random game mode.", self.start_random_mode),
        ]

        grid = ttk.Frame(self.container)
        grid.pack(fill=tk.BOTH, expand=True)

        for i, (title, desc, cmd) in enumerate(modes):
            r, c = divmod(i, 2)
            cell = ttk.LabelFrame(grid, text=title, padding=10)
            cell.grid(row=r, column=c, padx=6, pady=6, sticky=tk.NSEW)
            ttk.Label(cell, text=desc, wraplength=360, font=self._font_body).pack(anchor=tk.W)
            ttk.Button(cell, text="Start", command=cmd).pack(anchor=tk.E, pady=(8, 0))

        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        ttk.Button(self.container, text="Exit", command=self.destroy).pack(anchor=tk.E, pady=(16, 0))

    def back_button(self, parent: tk.Widget) -> None:
        ttk.Button(parent, text="← Back to menu", command=self.show_menu).pack(anchor=tk.W, pady=(0, 12))

    def start_spelling_lab(self) -> None:
        self.clear_container()
        from spelling_lab_gui import SpellingLabFrame

        SpellingLabFrame(self.container, on_back=self.show_menu)

    # ----- Beat the clock (timed typing, shrinking time limit) -----

    def start_beat_the_clock(self) -> None:
        words_list = list(WORDS.items())
        random.shuffle(words_list)
        state: Dict[str, object] = {
            "index": 0,
            "score": 0,
            "limit": BEAT_CLOCK_START_SEC,
        }
        timer_info: Dict[str, object] = {"after_id": None, "done": False}

        def cancel_tick() -> None:
            aid = timer_info.get("after_id")
            if aid is not None:
                try:
                    self.after_cancel(aid)
                except tk.TclError:
                    pass
                timer_info["after_id"] = None

        def build() -> None:
            self.clear_container()
            self.back_button(self.container)
            cancel_tick()
            timer_info["done"] = False

            i = int(state["index"])
            total = len(words_list)
            if i >= total:
                fr = ttk.Frame(self.container)
                fr.pack(fill=tk.BOTH, expand=True)
                sc = int(state["score"])
                pct = int(sc / total * 100) if total else 0
                ttk.Label(fr, text="Beat the clock — finished!", font=self._font_title).pack(pady=16)
                ttk.Label(
                    fr,
                    text=f"Words typed in time: {sc}/{total} ({pct}%)",
                    font=self._font_heading,
                ).pack()
                ttk.Label(
                    fr,
                    text=f"Started at {BEAT_CLOCK_START_SEC:.0f}s per word, down to {BEAT_CLOCK_MIN_SEC:.0f}s minimum.",
                    font=self._font_body,
                    wraplength=720,
                ).pack(pady=8)
                ttk.Button(fr, text="Play again", command=self.start_beat_the_clock).pack(pady=12)
                return

            word, definition = words_list[i]
            limit = max(BEAT_CLOCK_MIN_SEC, float(state["limit"]))
            deadline = time.time() + limit

            ttk.Label(
                self.container,
                text=f"Round {i + 1} of {total}",
                font=self._font_body,
            ).pack(anchor=tk.W)
            ttk.Label(
                self.container,
                text="Someone reads the clue aloud — then type the vocabulary word before time runs out.",
                font=self._font_body,
                wraplength=800,
            ).pack(anchor=tk.W, pady=(4, 8))
            ttk.Label(
                self.container,
                text=definition,
                wraplength=800,
                font=("Segoe UI", 13),
            ).pack(anchor=tk.W, pady=(0, 8))

            countdown_var = tk.StringVar(value=f"{limit:.1f}s")
            clock = ttk.Label(
                self.container,
                textvariable=countdown_var,
                font=("Segoe UI", 28, "bold"),
                foreground="#0b5cab",
            )
            clock.pack(anchor=tk.W, pady=4)
            ttk.Label(
                self.container,
                text=f"Next round will have up to {max(BEAT_CLOCK_MIN_SEC, limit - BEAT_CLOCK_STEP_SEC):.1f}s (minimum {BEAT_CLOCK_MIN_SEC:.0f}s).",
                font=("Segoe UI", 9),
                foreground="#555555",
            ).pack(anchor=tk.W)

            entry = ttk.Entry(self.container, width=50, font=self._font_body)
            entry.pack(fill=tk.X, pady=12)
            entry.focus_set()

            fb = ttk.Label(self.container, text="", font=self._font_body)
            fb.pack(anchor=tk.W, pady=8)

            def bump_limit() -> None:
                state["limit"] = max(BEAT_CLOCK_MIN_SEC, float(state["limit"]) - BEAT_CLOCK_STEP_SEC)

            def go_next() -> None:
                state["index"] = i + 1
                self.after(900, build)

            def on_timeout() -> None:
                if timer_info["done"]:
                    return
                timer_info["done"] = True
                cancel_tick()
                clock.config(foreground="#b00020")
                countdown_var.set("0.0s")
                fb.config(text=f"Time's up! Word: {word}")
                bump_limit()
                go_next()

            def tick() -> None:
                if timer_info["done"]:
                    return
                remain = deadline - time.time()
                if remain <= 0:
                    on_timeout()
                    return
                countdown_var.set(f"{remain:.1f}s")
                if remain <= 5:
                    clock.config(foreground="#b00020")
                elif remain <= 10:
                    clock.config(foreground="#c65c00")
                else:
                    clock.config(foreground="#0b5cab")
                timer_info["after_id"] = self.after(100, tick)

            def submit() -> None:
                if timer_info["done"]:
                    return
                remain = deadline - time.time()
                if remain <= 0:
                    return
                ans = entry.get().strip().lower()
                if not ans:
                    fb.config(text="Type the spelling of the word.")
                    return
                timer_info["done"] = True
                cancel_tick()
                if ans == word:
                    state["score"] = int(state["score"]) + 1
                    fb.config(text="Correct!")
                else:
                    fb.config(text=f"Not quite — answer: {word}")
                bump_limit()
                go_next()

            ttk.Button(self.container, text="Submit (or press Enter)", command=submit).pack(anchor=tk.W)
            entry.bind("<Return>", lambda e: submit())
            tick()

        build()

    # ----- Flash cards -----

    def start_flash_cards(self) -> None:
        words_list = list(WORDS.items())
        random.shuffle(words_list)
        state: Dict[str, object] = {
            "words": words_list,
            "index": 0,
            "score": 0,
        }

        def build() -> None:
            self.clear_container()
            self.back_button(self.container)

            i = int(state["index"])
            total = len(words_list)
            if i >= total:
                fr = ttk.Frame(self.container)
                fr.pack(fill=tk.BOTH, expand=True)
                pct = int(state["score"] / total * 100) if total else 0
                ttk.Label(fr, text="Game complete!", font=self._font_title).pack(pady=16)
                ttk.Label(
                    fr,
                    text=f"Score: {state['score']}/{total} ({pct}%)",
                    font=self._font_heading,
                ).pack()
                ttk.Button(fr, text="Play again", command=lambda: self.start_flash_cards()).pack(pady=12)
                return

            word, definition = words_list[i]
            ttk.Label(
                self.container,
                text=f"Word {i + 1} of {total}",
                font=self._font_body,
            ).pack(anchor=tk.W)
            ttk.Label(self.container, text=word.upper(), font=("Segoe UI", 22, "bold")).pack(pady=12)

            hint_var = tk.StringVar(value="")
            ttk.Label(self.container, textvariable=hint_var, wraplength=780, font=self._font_body).pack(
                anchor=tk.W,
                pady=8,
            )

            entry = ttk.Entry(self.container, width=70, font=self._font_body)
            entry.pack(fill=tk.X, pady=8)
            entry.focus_set()

            feedback = ttk.Label(self.container, text="", font=self._font_body)
            feedback.pack(anchor=tk.W, pady=8)

            def show_hint() -> None:
                hint_var.set(f"Hint: {SENTENCES[word]}")

            def do_skip() -> None:
                messagebox.showinfo("Answer", definition)
                state["index"] = i + 1
                build()

            def submit() -> None:
                ans = entry.get().strip()
                if not ans:
                    feedback.config(text="Type a definition, or use Hint / Skip.")
                    return
                if _flexible_definition_match(definition, ans):
                    feedback.config(text="Correct!")
                    state["score"] = int(state["score"]) + 1
                    state["index"] = i + 1
                    self.after(400, build)
                else:
                    feedback.config(text=f"Not quite. Answer: {definition}")
                    state["index"] = i + 1
                    self.after(1200, build)

            btn_row = ttk.Frame(self.container)
            btn_row.pack(fill=tk.X, pady=8)
            ttk.Button(btn_row, text="Hint", command=show_hint).pack(side=tk.LEFT, padx=4)
            ttk.Button(btn_row, text="Skip", command=do_skip).pack(side=tk.LEFT, padx=4)
            ttk.Button(btn_row, text="Submit", command=submit).pack(side=tk.LEFT, padx=4)
            entry.bind("<Return>", lambda e: submit())

        build()

    # ----- Multiple choice -----

    def start_multiple_choice(self) -> None:
        words_list = list(WORDS.items())
        random.shuffle(words_list)
        state = {"index": 0, "score": 0}
        var = tk.StringVar()

        def build() -> None:
            self.clear_container()
            self.back_button(self.container)

            i = state["index"]
            total = len(words_list)
            if i >= total:
                fr = ttk.Frame(self.container)
                fr.pack(fill=tk.BOTH, expand=True)
                pct = int(state["score"] / total * 100) if total else 0
                ttk.Label(fr, text="Complete!", font=self._font_title).pack(pady=16)
                ttk.Label(
                    fr,
                    text=f"Score: {state['score']}/{total} ({pct}%)",
                    font=self._font_heading,
                ).pack()
                ttk.Button(fr, text="Play again", command=self.start_multiple_choice).pack(pady=12)
                return

            word, correct_def = words_list[i]
            wrong = [d for w, d in WORDS.items() if w != word]
            wrong = random.sample(wrong, min(3, len(wrong)))
            options = [correct_def] + wrong
            random.shuffle(options)
            var.set("")

            ttk.Label(
                self.container,
                text=f"Question {i + 1} of {total}",
                font=self._font_body,
            ).pack(anchor=tk.W)
            ttk.Label(
                self.container,
                text=f"What does “{word}” mean?",
                font=self._font_heading,
                wraplength=800,
            ).pack(anchor=tk.W, pady=12)

            for opt in options:
                ttk.Radiobutton(
                    self.container,
                    text=opt[:120] + ("…" if len(opt) > 120 else ""),
                    variable=var,
                    value=opt,
                ).pack(anchor=tk.W, pady=2)

            fb = ttk.Label(self.container, text="", font=self._font_body)
            fb.pack(anchor=tk.W, pady=8)

            def next_q(correct: bool) -> None:
                state["index"] = i + 1
                self.after(500 if not correct else 300, build)

            def submit() -> None:
                choice = var.get()
                if not choice:
                    fb.config(text="Choose an answer.")
                    return
                if choice == correct_def:
                    fb.config(text="Correct!")
                    state["score"] += 1
                    next_q(True)
                else:
                    fb.config(text=f"Wrong. Answer: {correct_def}")
                    next_q(False)

            ttk.Button(self.container, text="Submit", command=submit).pack(anchor=tk.W, pady=8)

        build()

    # ----- Spelling bee -----

    def start_spelling_bee(self) -> None:
        words_list = list(WORDS.items())
        random.shuffle(words_list)
        state = {"index": 0, "score": 0}

        def build() -> None:
            self.clear_container()
            self.back_button(self.container)

            i = state["index"]
            total = len(words_list)
            if i >= total:
                fr = ttk.Frame(self.container)
                fr.pack(fill=tk.BOTH, expand=True)
                ttk.Label(fr, text="Complete!", font=self._font_title).pack(pady=16)
                ttk.Label(fr, text=f"Score: {state['score']}/{total}", font=self._font_heading).pack()
                ttk.Button(fr, text="Play again", command=self.start_spelling_bee).pack(pady=12)
                return

            word, definition = words_list[i]
            attempts = {"n": 3}

            ttk.Label(
                self.container,
                text=f"Definition {i + 1} of {total}",
                font=self._font_body,
            ).pack(anchor=tk.W)
            ttk.Label(
                self.container,
                text=definition,
                wraplength=800,
                font=self._font_heading,
            ).pack(anchor=tk.W, pady=12)

            hint = ttk.Label(self.container, text="", font=self._font_body)
            hint.pack(anchor=tk.W)

            entry = ttk.Entry(self.container, width=40, font=self._font_body)
            entry.pack(pady=8)
            entry.focus_set()

            fb = ttk.Label(self.container, text="", font=self._font_body)
            fb.pack(anchor=tk.W, pady=8)

            def show_hint() -> None:
                hint.config(
                    text=f"First letter: '{word[0].upper()}', length: {len(word)} letters",
                )

            def submit() -> None:
                ans = entry.get().strip().lower()
                if not ans:
                    fb.config(text="Spell the word.")
                    return
                if ans == word:
                    fb.config(text="Perfect!")
                    state["score"] += 1
                    state["index"] = i + 1
                    self.after(400, build)
                    return
                attempts["n"] -= 1
                if attempts["n"] > 0:
                    fb.config(text=f"Try again. ({attempts['n']} attempts left)")
                    entry.delete(0, tk.END)
                else:
                    fb.config(text=f"Answer: {word}")
                    state["index"] = i + 1
                    self.after(900, build)

            row = ttk.Frame(self.container)
            row.pack()
            ttk.Button(row, text="Hint", command=show_hint).pack(side=tk.LEFT, padx=4)
            ttk.Button(row, text="Submit", command=submit).pack(side=tk.LEFT, padx=4)
            entry.bind("<Return>", lambda e: submit())

        build()

    # ----- Sentence builder -----

    def start_sentence_builder(self) -> None:
        words_list = list(WORDS.keys())
        random.shuffle(words_list)
        state = {"index": 0, "score": 0}

        def build() -> None:
            self.clear_container()
            self.back_button(self.container)

            i = state["index"]
            total = len(words_list)
            if i >= total:
                fr = ttk.Frame(self.container)
                fr.pack(fill=tk.BOTH, expand=True)
                max_pts = total * 5
                ttk.Label(fr, text="Sentence champion round done!", font=self._font_title).pack(pady=16)
                ttk.Label(
                    fr,
                    text=f"Creative score: {state['score']}/{max_pts}",
                    font=self._font_heading,
                ).pack()
                ttk.Button(fr, text="Play again", command=self.start_sentence_builder).pack(pady=12)
                return

            w = words_list[i]
            ttk.Label(
                self.container,
                text=f"Word {i + 1} of {total}: {w.upper()}",
                font=self._font_heading,
            ).pack(anchor=tk.W)
            ttk.Label(
                self.container,
                text=f"Meaning: {WORDS[w]}",
                wraplength=800,
                font=self._font_body,
            ).pack(anchor=tk.W, pady=4)
            ttk.Label(
                self.container,
                text=f"Example: {SENTENCES[w]}",
                wraplength=800,
                font=self._font_body,
            ).pack(anchor=tk.W, pady=4)

            txt = scrolledtext.ScrolledText(self.container, height=4, width=80, font=self._font_body)
            txt.pack(fill=tk.BOTH, pady=8)

            fb = ttk.Label(self.container, text="", font=self._font_body)
            fb.pack(anchor=tk.W)

            def submit() -> None:
                sentence = txt.get("1.0", tk.END).strip()
                if not sentence:
                    fb.config(text="Write a sentence that includes the word.")
                    return
                if w.lower() in sentence.lower():
                    length_bonus = min(5, len(sentence.split()) // 3)
                    pts = 5 + length_bonus
                    state["score"] += pts
                    fb.config(text=f"Great! +{pts} points.")
                    state["index"] = i + 1
                    self.after(600, build)
                else:
                    fb.config(text=f"Include the word “{w}” in your sentence.")

            ttk.Button(self.container, text="Submit sentence", command=submit).pack(anchor=tk.W)

        build()

    # ----- Match -----

    def start_match_game(self) -> None:
        pairs = list(WORDS.items())
        random.shuffle(pairs)
        shuffled_words = [p[0] for p in pairs]
        shuffled_defs = [p[1] for p in pairs]
        random.shuffle(shuffled_defs)

        state = {
            "matches": set(),
            "score": 0,
        }

        def build() -> None:
            self.clear_container()
            self.back_button(self.container)

            total = len(shuffled_words)
            ttk.Label(
                self.container,
                text="Select a word and a definition, then click Match.",
                font=self._font_body,
            ).pack(anchor=tk.W, pady=(0, 8))
            ttk.Label(
                self.container,
                text=f"Matched: {len(state['matches'])}/{total}  ·  Score: {state['score']}",
                font=self._font_heading,
            ).pack(anchor=tk.W)

            row = ttk.Frame(self.container)
            row.pack(fill=tk.BOTH, expand=True, pady=8)

            lf_w = ttk.LabelFrame(row, text="Words", padding=8)
            lf_w.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
            lb_w = tk.Listbox(lf_w, height=16, font=self._font_mono, exportselection=False)
            for j, w in enumerate(shuffled_words):
                mark = "✓ " if j in state["matches"] else ""
                lb_w.insert(tk.END, f"{mark}{j + 1}. {w}")
            lb_w.pack(fill=tk.BOTH, expand=True)

            lf_d = ttk.LabelFrame(row, text="Definitions", padding=8)
            lf_d.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            lb_d = tk.Listbox(lf_d, height=16, font=self._font_mono, exportselection=False)
            for j, d in enumerate(shuffled_defs):
                short = d if len(d) <= 70 else d[:67] + "…"
                lb_d.insert(tk.END, f"{j + 1}. {short}")
            lb_d.pack(fill=tk.BOTH, expand=True)

            fb = ttk.Label(self.container, text="", font=self._font_body)
            fb.pack(anchor=tk.W, pady=8)

            def try_match() -> None:
                sw = lb_w.curselection()
                sd = lb_d.curselection()
                if not sw or not sd:
                    fb.config(text="Select one word and one definition.")
                    return
                wi, di = int(sw[0]), int(sd[0])
                if wi in state["matches"]:
                    fb.config(text="That word is already matched.")
                    return
                word = shuffled_words[wi]
                definition = shuffled_defs[di]
                if WORDS[word] == definition:
                    state["matches"].add(wi)
                    state["score"] += 1
                    fb.config(text=f"Correct: {word}")
                    if len(state["matches"]) >= total:
                        self.after(400, done)
                    else:
                        self.after(300, build)
                else:
                    fb.config(
                        text=f"No — “{word}” means: {WORDS[word]}",
                    )

            def done() -> None:
                self.clear_container()
                self.back_button(self.container)
                ttk.Label(
                    self.container,
                    text="Matching complete!",
                    font=self._font_title,
                ).pack(pady=16)
                ttk.Label(
                    self.container,
                    text=f"Final score: {state['score']}/{total}",
                    font=self._font_heading,
                ).pack()
                if state["score"] == total:
                    ttk.Label(self.container, text="Perfect match!", font=self._font_body).pack(pady=8)
                ttk.Button(self.container, text="Play again", command=self.start_match_game).pack(pady=12)

            ttk.Button(self.container, text="Match selected", command=try_match).pack(anchor=tk.W)

        build()

    # ----- Rapid fire -----

    def start_rapid_fire(self) -> None:
        words_list = list(WORDS.items())
        random.shuffle(words_list)
        state = {"index": 0, "score": 0.0}

        cancel_timer: Dict[str, Optional[str]] = {"id": None}

        def build() -> None:
            self.clear_container()
            self.back_button(self.container)

            if cancel_timer["id"]:
                try:
                    self.after_cancel(cancel_timer["id"])
                except tk.TclError:
                    pass
                cancel_timer["id"] = None

            i = state["index"]
            total = len(words_list)
            if i >= total:
                fr = ttk.Frame(self.container)
                fr.pack(fill=tk.BOTH, expand=True)
                ttk.Label(fr, text="Rapid fire finished!", font=self._font_title).pack(pady=16)
                ttk.Label(
                    fr,
                    text=f"Points: {state['score']:.0f} (max ~{total * 2} with speed bonus)",
                    font=self._font_heading,
                ).pack()
                ttk.Button(fr, text="Play again", command=self.start_rapid_fire).pack(pady=12)
                return

            word, definition = words_list[i]
            start = time.time()
            slow = {"flag": False}

            ttk.Label(
                self.container,
                text=f"Question {i + 1} of {total} — you have 5 seconds",
                font=self._font_body,
            ).pack(anchor=tk.W)
            ttk.Label(self.container, text=f"What does “{word}” mean?", font=self._font_heading).pack(
                anchor=tk.W,
                pady=12,
            )

            entry = ttk.Entry(self.container, width=70, font=self._font_body)
            entry.pack(fill=tk.X, pady=8)
            entry.focus_set()

            fb = ttk.Label(self.container, text="", font=self._font_body)
            fb.pack(anchor=tk.W, pady=8)

            def finish_round(answer: str, timed_out: bool) -> None:
                if cancel_timer["id"]:
                    try:
                        self.after_cancel(cancel_timer["id"])
                    except tk.TclError:
                        pass
                    cancel_timer["id"] = None
                elapsed = time.time() - start
                if answer.strip().lower() == "quit":
                    state["index"] = total
                    build()
                    return
                if timed_out:
                    fb.config(text=f"Too slow. Answer: {definition}")
                    state["index"] = i + 1
                    self.after(900, build)
                    return
                time_bonus = max(0, int(5 - elapsed))
                if _flexible_definition_match(definition, answer):
                    pts = 1 + (time_bonus // 2)
                    state["score"] += pts
                    fb.config(text=f"Correct! +{pts} pts ({elapsed:.1f}s)")
                else:
                    fb.config(text=f"Wrong. Answer: {definition}")
                state["index"] = i + 1
                self.after(700, build)

            def on_timer() -> None:
                cancel_timer["id"] = None
                slow["flag"] = True
                finish_round(entry.get(), True)

            cancel_timer["id"] = self.after(5000, on_timer)

            def submit() -> None:
                if slow["flag"]:
                    return
                finish_round(entry.get(), False)

            ttk.Button(self.container, text="Submit", command=submit).pack(anchor=tk.W)
            entry.bind("<Return>", lambda e: submit())

        build()

    # ----- Word story -----

    def start_word_story(self) -> None:
        self.clear_container()
        self.back_button(self.container)

        ttk.Label(
            self.container,
            text="Write a short story using as many vocabulary words as you can.",
            font=self._font_heading,
            wraplength=800,
        ).pack(anchor=tk.W, pady=(0, 8))

        words_frame = ttk.Frame(self.container)
        words_frame.pack(fill=tk.X, pady=8)
        col1 = ttk.Frame(words_frame)
        col2 = ttk.Frame(words_frame)
        col1.pack(side=tk.LEFT, fill=tk.X, expand=True)
        col2.pack(side=tk.LEFT, fill=tk.X, expand=True)
        keys = list(WORDS.keys())
        mid = (len(keys) + 1) // 2
        for j, w in enumerate(keys[:mid]):
            ttk.Label(col1, text=f"• {w}", font=self._font_mono).pack(anchor=tk.W)
        for w in keys[mid:]:
            ttk.Label(col2, text=f"• {w}", font=self._font_mono).pack(anchor=tk.W)

        story = scrolledtext.ScrolledText(self.container, height=14, width=80, font=self._font_body)
        story.pack(fill=tk.BOTH, expand=True, pady=8)

        result = ttk.Label(self.container, text="", font=self._font_body, wraplength=800)
        result.pack(anchor=tk.W, pady=8)

        def analyze() -> None:
            text = story.get("1.0", tk.END)
            story_lower = text.lower()
            used = [w for w in WORDS if w in story_lower]
            score = len(used)
            total = len(WORDS)
            lines = [
                f"Words used: {score}/{total}",
                f"Found: {', '.join(used) if used else '(none)'}",
            ]
            if score == total:
                lines.append("You used every word — great storytelling!")
            elif score >= total * 0.7:
                lines.append("Great story — try to weave in the rest next time.")
            else:
                missing = [w for w in WORDS if w not in used]
                lines.append("Missing: " + ", ".join(missing))
            result.config(text="\n".join(lines))

        ttk.Button(self.container, text="Analyze story", command=analyze).pack(anchor=tk.W)

    # ----- Study -----

    def start_study_mode(self) -> None:
        items = list(WORDS.items())
        state = {"index": 0}

        def build() -> None:
            self.clear_container()
            self.back_button(self.container)

            i = state["index"]
            word, definition = items[i]
            n = len(items)

            ttk.Label(
                self.container,
                text=f"Card {i + 1} of {n}",
                font=self._font_body,
            ).pack(anchor=tk.W)
            ttk.Label(self.container, text=word.upper(), font=("Segoe UI", 20, "bold")).pack(pady=12)
            ttk.Label(
                self.container,
                text=definition,
                wraplength=800,
                font=self._font_heading,
            ).pack(anchor=tk.W, pady=8)
            ttk.Label(
                self.container,
                text=f"Example: {SENTENCES[word]}",
                wraplength=800,
                font=self._font_body,
            ).pack(anchor=tk.W, pady=8)

            nav = ttk.Frame(self.container)
            nav.pack(pady=16)

            def prev() -> None:
                state["index"] = max(0, i - 1)
                build()

            def next_card() -> None:
                state["index"] = min(n - 1, i + 1)
                build()

            ttk.Button(nav, text="Previous", command=prev).pack(side=tk.LEFT, padx=8)
            ttk.Button(nav, text="Next", command=next_card).pack(side=tk.LEFT, padx=8)

        build()

    # ----- Random -----

    def start_random_mode(self) -> None:
        choices: List[Callable[[], None]] = [
            self.start_beat_the_clock,
            self.start_flash_cards,
            self.start_multiple_choice,
            self.start_spelling_bee,
            self.start_sentence_builder,
            self.start_match_game,
            self.start_rapid_fire,
            self.start_word_story,
        ]
        random.choice(choices)()


def main() -> None:
    app = VocabularyGameApp()
    app.mainloop()


if __name__ == "__main__":
    main()
