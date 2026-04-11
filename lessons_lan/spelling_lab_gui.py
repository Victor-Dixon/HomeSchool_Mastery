#!/usr/bin/env python3
"""
Spelling Lab — spelling-first practice (flash, scramble, gaps, sprint).
Optional custom words: spelling_custom_words.txt (one word per line, # comments ok).
"""

from __future__ import annotations

import random
import time
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from typing import Callable, List

from spelling_lab_core import (
    FLASH_SHOW_SEC,
    SPRINT_MIN_SEC,
    SPRINT_START_SEC,
    SPRINT_STEP_SEC,
    _CUSTOM_FILE,
    _normalize_line,
    load_word_list,
    make_skeleton,
    save_custom_words,
    scramble_letters,
)


class SpellingLabFrame(ttk.Frame):
    """Spelling-first games embedded in the parent window."""

    def __init__(self, parent: tk.Widget, on_back: Callable[[], None]) -> None:
        super().__init__(parent)
        self.on_back = on_back
        self.words = load_word_list()

        self._font_title = ("Segoe UI", 20, "bold")
        self._font_heading = ("Segoe UI", 12, "bold")
        self._font_body = ("Segoe UI", 11)
        self._font_big = ("Segoe UI", 36, "bold")
        self._font_mono = ("Consolas", 14)

        self.pack(fill=tk.BOTH, expand=True)

        self._outer = ttk.Frame(self)
        self._outer.pack(fill=tk.BOTH, expand=True)
        self._build_main_menu()

    def _clear_work(self) -> None:
        for w in self._outer.winfo_children():
            w.destroy()

    def _build_main_menu(self) -> None:
        self._clear_work()
        self.words = load_word_list()

        ttk.Button(self._outer, text="← Back to main menu", command=self.on_back).pack(anchor=tk.W, pady=(0, 8))

        ttk.Label(self._outer, text="Spelling Lab", font=self._font_title).pack(anchor=tk.W)
        ttk.Label(
            self._outer,
            text="Practice spelling — look at the word, hear it read aloud, then type it. "
            "No definitions required.",
            font=self._font_body,
            wraplength=820,
        ).pack(anchor=tk.W, pady=(4, 12))

        n = len(self.words)
        ttk.Label(
            self._outer,
            text=f"Word pool: {n} words (vocab list + spelling_custom_words.txt).",
            font=("Segoe UI", 9),
            foreground="#444444",
        ).pack(anchor=tk.W, pady=(0, 12))

        modes: List[tuple[str, str, Callable[[], None]]] = [
            (
                "Flash & spell",
                "The word appears briefly — then you type it from memory (look · cover · write).",
                self._start_flash_spell,
            ),
            (
                "Letter scramble",
                "Letters are shuffled — untangle them and type the word.",
                self._start_scramble,
            ),
            (
                "Fill the gaps",
                "Some letters are missing — type the full word.",
                self._start_gaps,
            ),
            (
                "Spelling sprint",
                "Quick flash, then type fast. Time to type gets shorter each round.",
                self._start_sprint,
            ),
        ]

        grid = ttk.Frame(self._outer)
        grid.pack(fill=tk.BOTH, expand=True)
        for i, (title, desc, cmd) in enumerate(modes):
            r, c = divmod(i, 2)
            cell = ttk.LabelFrame(grid, text=title, padding=12)
            cell.grid(row=r, column=c, padx=6, pady=6, sticky=tk.NSEW)
            ttk.Label(cell, text=desc, wraplength=380, font=self._font_body).pack(anchor=tk.W)
            ttk.Button(cell, text="Play", command=cmd).pack(anchor=tk.E, pady=(10, 0))

        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        ttk.Button(self._outer, text="Edit my word list…", command=self._open_word_editor).pack(anchor=tk.W, pady=(16, 0))

    def _open_word_editor(self) -> None:
        top = tk.Toplevel(self)
        top.title("Custom spelling words")
        top.minsize(480, 320)
        top.transient(self.winfo_toplevel())
        ttk.Label(
            top,
            text="One word per line. Saved as spelling_custom_words.txt next to this app.",
            wraplength=440,
        ).pack(anchor=tk.W, padx=12, pady=8)

        txt = scrolledtext.ScrolledText(top, height=14, width=56, font=self._font_mono)
        txt.pack(fill=tk.BOTH, expand=True, padx=12, pady=4)
        if _CUSTOM_FILE.is_file():
            try:
                txt.insert("1.0", _CUSTOM_FILE.read_text(encoding="utf-8"))
            except OSError:
                pass

        def save() -> None:
            raw = txt.get("1.0", tk.END)
            lines = [_normalize_line(x) or "" for x in raw.splitlines()]
            lines = [x for x in lines if x]
            try:
                save_custom_words(lines)
            except OSError as e:
                messagebox.showerror("Save failed", str(e), parent=top)
                return
            messagebox.showinfo("Saved", f"Saved {len(lines)} custom words.", parent=top)
            self.words = load_word_list()

        ttk.Button(top, text="Save", command=save).pack(anchor=tk.E, padx=12, pady=12)

    def _pick_words(self) -> List[str]:
        pool = list(self.words)
        if not pool:
            messagebox.showinfo("No words", "Add words in Edit my word list or fix vocabulary_game.WORDS.")
            return []
        random.shuffle(pool)
        return pool

    # ----- Flash & spell -----

    def _start_flash_spell(self) -> None:
        pool = self._pick_words()
        if not pool:
            return
        show_sec = FLASH_SHOW_SEC
        state = {"i": 0, "streak": 0, "best": 0}

        def build() -> None:
            self._clear_work()
            ttk.Button(self._outer, text="← Spelling Lab", command=self._build_main_menu).pack(anchor=tk.W, pady=(0, 8))

            i = state["i"]
            if i >= len(pool):
                fr = ttk.Frame(self._outer)
                fr.pack(fill=tk.BOTH, expand=True)
                ttk.Label(fr, text="Session complete!", font=self._font_title).pack(pady=16)
                ttk.Label(fr, text=f"Longest streak: {state['best']}", font=self._font_heading).pack()
                ttk.Button(fr, text="Play again", command=self._start_flash_spell).pack(pady=12)
                return

            word = pool[i]
            phase = {"show": True}

            hint = ttk.Label(self._outer, text="", font=self._font_body, foreground="#666666")
            hint.pack(anchor=tk.W)

            big = ttk.Label(self._outer, text=word.upper(), font=self._font_big)
            big.pack(pady=24)

            entry = ttk.Entry(self._outer, width=40, font=self._font_body)
            fb = ttk.Label(self._outer, text="", font=self._font_body)

            def hide_word() -> None:
                if not phase["show"]:
                    return
                phase["show"] = False
                big.config(text="• • •", foreground="#888888")
                hint.config(text="Type the word you saw (check spelling).")
                entry.pack(pady=8)
                fb.pack(anchor=tk.W, pady=6)
                entry.focus_set()

            self.after(int(show_sec * 1000), hide_word)

            def submit() -> None:
                if phase["show"]:
                    return
                ans = entry.get().strip().lower()
                if not ans:
                    fb.config(text="Type the word.")
                    return
                if ans == word.lower():
                    state["streak"] += 1
                    state["best"] = max(state["best"], state["streak"])
                    fb.config(text=f"✓ Nice! Streak {state['streak']}")
                    state["i"] = i + 1
                    self.after(500, build)
                else:
                    state["streak"] = 0
                    fb.config(text=f"Try again — the word was: {word}")
                    state["i"] = i + 1
                    self.after(1200, build)

            ttk.Button(self._outer, text="Check spelling", command=submit).pack(anchor=tk.W, pady=4)
            entry.bind("<Return>", lambda e: submit())

        build()

    # ----- Scramble -----

    def _start_scramble(self) -> None:
        pool = self._pick_words()
        if not pool:
            return
        state = {"i": 0, "score": 0}

        def build() -> None:
            self._clear_work()
            ttk.Button(self._outer, text="← Spelling Lab", command=self._build_main_menu).pack(anchor=tk.W, pady=(0, 8))

            i = state["i"]
            if i >= len(pool):
                fr = ttk.Frame(self._outer)
                fr.pack(fill=tk.BOTH, expand=True)
                ttk.Label(fr, text="Scramble complete!", font=self._font_title).pack(pady=16)
                ttk.Label(fr, text=f"Solved: {state['score']}/{len(pool)}", font=self._font_heading).pack()
                ttk.Button(fr, text="Play again", command=self._start_scramble).pack(pady=12)
                return

            word = pool[i]
            scrambled = scramble_letters(word)

            ttk.Label(
                self._outer,
                text=f"Word {i + 1} of {len(pool)} — unscramble the letters",
                font=self._font_body,
            ).pack(anchor=tk.W)
            ttk.Label(self._outer, text=scrambled.upper(), font=self._font_mono).pack(pady=20)

            entry = ttk.Entry(self._outer, width=40, font=self._font_body)
            entry.pack(pady=8)
            entry.focus_set()
            fb = ttk.Label(self._outer, text="", font=self._font_body)
            fb.pack(anchor=tk.W)

            def submit() -> None:
                ans = entry.get().strip().lower()
                if not ans:
                    fb.config(text="Type the word.")
                    return
                if ans == word.lower():
                    state["score"] += 1
                    fb.config(text="✓ Got it!")
                    state["i"] = i + 1
                    self.after(450, build)
                else:
                    fb.config(text="Not quite — try again.")

            ttk.Button(self._outer, text="Submit", command=submit).pack(anchor=tk.W)
            entry.bind("<Return>", lambda e: submit())

        build()

    # ----- Gaps -----

    def _start_gaps(self) -> None:
        pool = self._pick_words()
        if not pool:
            return
        state = {"i": 0, "score": 0}

        def build() -> None:
            self._clear_work()
            ttk.Button(self._outer, text="← Spelling Lab", command=self._build_main_menu).pack(anchor=tk.W, pady=(0, 8))

            i = state["i"]
            if i >= len(pool):
                fr = ttk.Frame(self._outer)
                fr.pack(fill=tk.BOTH, expand=True)
                ttk.Label(fr, text="Gaps complete!", font=self._font_title).pack(pady=16)
                ttk.Label(fr, text=f"Correct: {state['score']}/{len(pool)}", font=self._font_heading).pack()
                ttk.Button(fr, text="Play again", command=self._start_gaps).pack(pady=12)
                return

            word = pool[i]
            skel = make_skeleton(word)

            ttk.Label(
                self._outer,
                text=f"Word {i + 1} of {len(pool)} — fill in the missing letters",
                font=self._font_body,
            ).pack(anchor=tk.W)
            ttk.Label(self._outer, text=skel, font=self._font_mono).pack(pady=20)

            entry = ttk.Entry(self._outer, width=40, font=self._font_body)
            entry.pack(pady=8)
            entry.focus_set()
            fb = ttk.Label(self._outer, text="", font=self._font_body)
            fb.pack(anchor=tk.W)

            def submit() -> None:
                ans = entry.get().strip().lower()
                if not ans:
                    fb.config(text="Type the full word.")
                    return
                if ans == word.lower():
                    state["score"] += 1
                    fb.config(text="✓ Perfect spelling!")
                    state["i"] = i + 1
                    self.after(450, build)
                else:
                    fb.config(text="Check every letter — try again.")

            ttk.Button(self._outer, text="Submit", command=submit).pack(anchor=tk.W)
            entry.bind("<Return>", lambda e: submit())

        build()

    # ----- Sprint (flash then type under shrinking time) -----

    def _start_sprint(self) -> None:
        pool = self._pick_words()
        if not pool:
            return
        state = {"i": 0, "score": 0, "limit": SPRINT_START_SEC}
        timer_info: dict[str, object] = {"after_id": None, "done": False}

        def cancel_tick() -> None:
            aid = timer_info.get("after_id")
            if aid is not None:
                try:
                    self.after_cancel(aid)
                except tk.TclError:
                    pass
                timer_info["after_id"] = None

        def build() -> None:
            self._clear_work()
            cancel_tick()
            timer_info["done"] = False

            ttk.Button(self._outer, text="← Spelling Lab", command=self._build_main_menu).pack(anchor=tk.W, pady=(0, 8))

            i = state["i"]
            if i >= len(pool):
                fr = ttk.Frame(self._outer)
                fr.pack(fill=tk.BOTH, expand=True)
                ttk.Label(fr, text="Sprint finished!", font=self._font_title).pack(pady=16)
                ttk.Label(fr, text=f"Typed in time: {state['score']}/{len(pool)}", font=self._font_heading).pack()
                ttk.Button(fr, text="Play again", command=self._start_sprint).pack(pady=12)
                return

            word = pool[i]
            limit = max(SPRINT_MIN_SEC, float(state["limit"]))
            show = {"phase": "flash"}

            ttk.Label(
                self._outer,
                text=f"Sprint {i + 1} of {len(pool)} — read the word aloud while it’s on screen, then spell it fast.",
                font=self._font_body,
                wraplength=800,
            ).pack(anchor=tk.W)

            big = ttk.Label(self._outer, text=word.upper(), font=self._font_big, foreground="#0b5cab")
            big.pack(pady=16)

            countdown_var = tk.StringVar(value="")
            clock = ttk.Label(self._outer, textvariable=countdown_var, font=("Segoe UI", 22, "bold"))
            clock.pack(anchor=tk.W)

            entry = ttk.Entry(self._outer, width=40, font=self._font_body)
            fb = ttk.Label(self._outer, text="", font=self._font_body)
            deadline_box: list[float] = [0.0]

            def bump_limit() -> None:
                state["limit"] = max(SPRINT_MIN_SEC, float(state["limit"]) - SPRINT_STEP_SEC)

            def go_next() -> None:
                state["i"] = i + 1
                self.after(850, build)

            def begin_type_phase() -> None:
                show["phase"] = "type"
                big.config(text="• • •", foreground="#888888")
                ttk.Label(
                    self._outer,
                    text=f"Now type it — {limit:.1f}s to finish!",
                    font=self._font_body,
                ).pack(anchor=tk.W, pady=(8, 4))
                entry.pack(pady=8)
                fb.pack(anchor=tk.W, pady=6)
                entry.focus_set()
                deadline_box[0] = time.time() + limit
                countdown_var.set(f"{limit:.1f}s")

                def on_timeout() -> None:
                    if timer_info["done"]:
                        return
                    timer_info["done"] = True
                    cancel_tick()
                    clock.config(foreground="#b00020")
                    countdown_var.set("0.0s")
                    fb.config(text=f"Time! Word was: {word}")
                    bump_limit()
                    go_next()

                def tick() -> None:
                    if timer_info["done"] or show["phase"] != "type":
                        return
                    remain = deadline_box[0] - time.time()
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

                tick()

                def submit() -> None:
                    if timer_info["done"]:
                        return
                    if time.time() > deadline_box[0]:
                        return
                    ans = entry.get().strip().lower()
                    if not ans:
                        fb.config(text="Type the word.")
                        return
                    timer_info["done"] = True
                    cancel_tick()
                    if ans == word.lower():
                        state["score"] += 1
                        fb.config(text="✓ Sharp!")
                    else:
                        fb.config(text=f"Oops — it was: {word}")
                    bump_limit()
                    go_next()

                ttk.Button(self._outer, text="Submit", command=submit).pack(anchor=tk.W, pady=4)
                entry.bind("<Return>", lambda e: submit())

            self.after(int(FLASH_SHOW_SEC * 1000), begin_type_phase)

        build()


def run_spelling_lab_standalone() -> None:
    root = tk.Tk()
    root.title("Spelling Lab")
    root.minsize(720, 560)
    root.geometry("900x640")
    fr = ttk.Frame(root, padding=16)
    fr.pack(fill=tk.BOTH, expand=True)

    def leave() -> None:
        root.destroy()

    SpellingLabFrame(fr, on_back=leave)
    root.mainloop()


if __name__ == "__main__":
    run_spelling_lab_standalone()
