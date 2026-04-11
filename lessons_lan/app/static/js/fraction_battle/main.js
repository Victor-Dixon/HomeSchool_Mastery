/**
 * Fraction Blocks War — canvas Tetris + line-clear math gate + garbage vs AI HP.
 */
(function () {
  "use strict";

  const FB_CFG = window.FRACTION_BATTLE_CONFIG || {};
  let xpSent = false;
  function maybeAwardXp(wonFlag) {
    if (xpSent || !FB_CFG.xpUrl) return;
    xpSent = true;
    fetch(FB_CFG.xpUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({ won: !!wonFlag }),
    }).catch(function () {});
  }

  const W = 10;
  const H = 20;
  const CELL = 28;
  const CW = W * CELL;
  const CH = H * CELL;

  const DROP_MS = 720;
  const SOFT_MS = 58;

  const PALETTE = {
    0: "#0b1220",
    1: "#2dd4bf",
    2: "#60a5fa",
    3: "#fb923c",
    4: "#facc15",
    5: "#4ade80",
    6: "#c084fc",
    7: "#f87171",
    8: "#475569",
  };

  const GLYPH_GRID = [
    { color: 1, m: [[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]] },
    { color: 2, m: [[1, 0, 0, 0], [1, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]] },
    { color: 3, m: [[0, 0, 1, 0], [1, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]] },
    { color: 4, m: [[0, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]] },
    { color: 5, m: [[0, 1, 1, 0], [1, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]] },
    { color: 6, m: [[0, 1, 0, 0], [1, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]] },
    { color: 7, m: [[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]] },
  ];

  /** 90° clockwise */
  function rot4(m) {
    const n = 4;
    const r = [];
    for (let i = 0; i < n; i++) r[i] = [];
    for (let y = 0; y < n; y++) {
      for (let x = 0; x < n; x++) {
        r[x][n - 1 - y] = m[y][x];
      }
    }
    return r;
  }

  function pieceRotations(base) {
    const rots = [];
    let m = base.map((row) => row.slice());
    for (let i = 0; i < 4; i++) {
      rots.push(m.map((row) => row.slice()));
      m = rot4(m);
    }
    return rots;
  }

  const PIECE_SET = GLYPH_GRID.map((g) => ({
    color: g.color,
    rots: pieceRotations(g.m),
  }));

  function emptyBoard() {
    const b = [];
    for (let y = 0; y < H; y++) {
      b[y] = [];
      for (let x = 0; x < W; x++) b[y][x] = 0;
    }
    return b;
  }

  function collides(board, shape, px, py) {
    for (let r = 0; r < 4; r++) {
      for (let c = 0; c < 4; c++) {
        if (!shape[r][c]) continue;
        const x = px + c;
        const y = py + r;
        if (x < 0 || x >= W || y >= H) return true;
        if (y >= 0 && board[y][x]) return true;
      }
    }
    return false;
  }

  function merge(board, shape, px, py, color) {
    for (let r = 0; r < 4; r++) {
      for (let c = 0; c < 4; c++) {
        if (!shape[r][c]) continue;
        const x = px + c;
        const y = py + r;
        if (y >= 0 && y < H && x >= 0 && x < W) board[y][x] = color;
      }
    }
  }

  function clearLines(board) {
    let cleared = 0;
    for (let y = H - 1; y >= 0; y--) {
      if (board[y].every((v) => v > 0)) {
        cleared++;
        board.splice(y, 1);
        board.unshift(Array(W).fill(0));
        y++;
      }
    }
    return cleared;
  }

  /** Push stack up; bottom row is garbage with one hole. Returns 'lose' or null */
  function injectGarbage(board, lines) {
    for (let k = 0; k < lines; k++) {
      if (board[0].some((c) => c > 0)) return "lose";
      for (let y = 0; y < H - 1; y++) board[y] = board[y + 1].slice();
      const hole = (Math.random() * W) | 0;
      const row = [];
      for (let x = 0; x < W; x++) row.push(x === hole ? 0 : 8);
      board[H - 1] = row;
    }
    return null;
  }

  function parseFracInput(raw) {
    const s = String(raw || "")
      .trim()
      .replace(/\s+/g, "");
    const m = s.match(/^(-?\d+)\/(-?\d+)$/);
    if (!m) return null;
    const n = parseInt(m[1], 10);
    const d = parseInt(m[2], 10);
    if (!d) return null;
    return FractionBattleQuestions.simplifyFrac(n, d);
  }

  function answerMatches(userStr, expectedStr) {
    const a = parseFracInput(userStr);
    const b = parseFracInput(expectedStr);
    if (!a || !b) return false;
    return a.n * b.d === b.n * a.d;
  }

  function $(id) {
    return document.getElementById(id);
  }

  const canvas = $("fb-canvas");
  const ctx = canvas.getContext("2d");
  const overlay = $("fb-overlay");
  const qText = $("fb-q-text");
  const qMeta = $("fb-q-meta");
  const qInput = $("fb-q-input");
  const qSubmit = $("fb-q-submit");
  const qFeedback = $("fb-q-feedback");
  const statusEl = $("fb-status");
  const btnStart = $("fb-start");
  const btnReset = $("fb-reset");
  const botBar = $("fb-bot-hp-bar");
  const youBar = $("fb-you-bar");
  const botPct = $("fb-bot-pct");
  const youPct = $("fb-you-pct");

  const cfg = window.FRACTION_BATTLE_CONFIG || {};
  const AI_ACCURACY = typeof cfg.aiAccuracy === "number" ? cfg.aiAccuracy : 0.7;
  const AI_ATTACK_MS = typeof cfg.aiAttackMs === "number" ? cfg.aiAttackMs : 14000;
  const AI_DM_VAR = typeof cfg.aiDamageVariance === "number" ? cfg.aiDamageVariance : 600;
  const PLAYER_HIT = typeof cfg.playerHitDamage === "number" ? cfg.playerHitDamage : 18;
  const START_BOT_HP = 100;

  let board = emptyBoard();
  let piece = null;
  let dropAcc = 510;
  let softDrop = false;
  let running = false;
  let paused = false;
  let gameOver = false;
  let won = false;
  let botHp = START_BOT_HP;
  let playerDanger = 0;
  let pendingClearCount = 0;
  let currentQ = null;
  let aiTimer = null;
  let raf = null;

  function setStatus(t) {
    if (statusEl) statusEl.textContent = t || "";
  }

  function drawCell(x, y, color) {
    const px = x * CELL;
    const py = y * CELL;
    const fill = PALETTE[color] || "#334155";
    ctx.fillStyle = fill;
    ctx.fillRect(px + 1, py + 1, CELL - 2, CELL - 2);
    ctx.strokeStyle = "rgba(255,255,255,0.12)";
    ctx.strokeRect(px + 0.5, py + 0.5, CELL - 1, CELL - 1);
  }

  function draw() {
    ctx.fillStyle = "#020617";
    ctx.fillRect(0, 0, CW, CH);
    for (let y = 0; y < H; y++) {
      for (let x = 0; x < W; x++) {
        drawCell(x, y, board[y][x]);
      }
    }
    if (piece) {
      const { shape, px, py, color } = piece;
      for (let r = 0; r < 4; r++) {
        for (let c = 0; c < 4; c++) {
          if (!shape[r][c]) continue;
          const gx = px + c;
          const gy = py + r;
          if (gy >= 0) drawCell(gx, gy, color);
        }
      }
    }
  }

  function spawn() {
    const def = PIECE_SET[(Math.random() * PIECE_SET.length) | 0];
    const rot = 0;
    const shape = def.rots[rot];
    const px = 3;
    const py = -1;
    if (collides(board, shape, px, py)) {
      gameOver = true;
      running = false;
      piece = null;
      setStatus("Tower topped out — reset and try again!");
      return;
    }
    piece = { def, rot, shape, px, py, color: def.color };
  }

  function lockPiece() {
    if (!piece) return;
    merge(board, piece.shape, piece.px, piece.py, piece.color);
    const cleared = clearLines(board);
    piece = null;
    if (cleared > 0) {
      pendingClearCount = cleared;
      openQuestion(cleared);
    } else {
      spawn();
    }
  }

  function tryMove(dx, dy) {
    if (!piece || paused || gameOver) return false;
    const npx = piece.px + dx;
    const npy = piece.py + dy;
    if (!collides(board, piece.shape, npx, npy)) {
      piece.px = npx;
      piece.py = npy;
      return true;
    }
    return false;
  }

  function tryRotate() {
    if (!piece || paused || gameOver) return;
    const nextRot = (piece.rot + 1) % 4;
    const shape = piece.def.rots[nextRot];
    const kicks = [0, -1, 1, -2, 2];
    for (const k of kicks) {
      if (!collides(board, shape, piece.px + k, piece.py)) {
        piece.rot = nextRot;
        piece.shape = shape;
        piece.px += k;
        return;
      }
    }
  }

  function hardDrop() {
    if (!piece || paused || gameOver) return;
    while (tryMove(0, 1)) {}
    lockPiece();
  }

  function tickStep(dt) {
    if (!running || paused || gameOver || !piece) return;
    const ms = softDrop ? SOFT_MS : DROP_MS;
    dropAcc += dt;
    while (dropAcc >= ms) {
      dropAcc -= ms;
      if (!tryMove(0, 1)) {
        lockPiece();
        break;
      }
    }
  }

  function hud() {
    const bp = Math.max(0, Math.min(100, botHp));
    botBar.style.width = bp + "%";
    botPct.textContent = Math.round(bp) + "%";
    const yp = Math.max(0, Math.min(100, 100 - playerDanger));
    youBar.style.width = yp + "%";
    youPct.textContent = Math.round(yp) + "%";
    if (gameOver) {
      maybeAwardXp(won);
    }
  }

  function openQuestion(lineCount) {
    paused = true;
    currentQ = FractionBattleQuestions.nextQuestion(lineCount);
    qText.textContent = currentQ.question;
    qMeta.textContent =
      "Difficulty: " +
      currentQ.difficulty +
      " · Cleared " +
      lineCount +
      " line" +
      (lineCount === 1 ? "" : "s");
    qInput.value = "";
    qFeedback.textContent = "";
    qFeedback.className = "fb-feedback";
    overlay.hidden = false;
    qInput.focus();
  }

  function closeOverlay() {
    overlay.hidden = true;
    paused = false;
    currentQ = null;
    pendingClearCount = 0;
    dropAcc = 0;
    if (!gameOver) spawn();
  }

  function scheduleAiAttack() {
    if (aiTimer) clearTimeout(aiTimer);
    if (!running || gameOver) return;
    const wait = AI_ATTACK_MS + (Math.random() * 2 - 1) * AI_DM_VAR;
    aiTimer = window.setTimeout(aiStrike, Math.max(3200, wait));
  }

  function aiStrike() {
    if (!running || gameOver || paused) {
      scheduleAiAttack();
      return;
    }
    if (Math.random() < AI_ACCURACY) {
      const lost = injectGarbage(board, 1);
      playerDanger = Math.min(100, playerDanger + 14);
      setStatus("Bot hit you — +1 garbage row!");
      if (lost === "lose") {
        gameOver = true;
        running = false;
        setStatus("You lose! Garbage overflow.");
      }
    } else {
      botHp = Math.max(0, botHp - 6);
      setStatus("Bot fumbled the fraction — free chip on its HP!");
    }
    hud();
    if (botHp <= 0) {
      won = true;
      gameOver = true;
      running = false;
      setStatus("You win! Opponent's stack collapsed.");
    }
    scheduleAiAttack();
  }

  function submitAnswer() {
    if (!currentQ) return;
    const raw = qInput.value;
    const ok = answerMatches(raw, currentQ.answer);
    qFeedback.className = "fb-feedback " + (ok ? "ok" : "bad");
    if (ok) {
      qFeedback.textContent = "Correct — sending garbage to the bot!";
      botHp = Math.max(0, botHp - PLAYER_HIT);
      hud();
      if (botHp <= 0) {
        won = true;
        gameOver = true;
        running = false;
        setStatus("Victory! Fraction skills = real damage.");
        window.setTimeout(closeOverlay, 900);
        return;
      }
      window.setTimeout(closeOverlay, 550);
    } else {
      qFeedback.textContent = "Not quite — answer was " + currentQ.answer + ". Incoming garbage!";
      const lost = injectGarbage(board, 1);
      playerDanger = Math.min(100, playerDanger + 22);
      hud();
      if (lost === "lose") {
        gameOver = true;
        running = false;
        setStatus("You lose!");
      }
      window.setTimeout(closeOverlay, 900);
    }
  }

  function loop(ts) {
    if (!running && raf) {
      cancelAnimationFrame(raf);
      raf = null;
      return;
    }
    if (!lastTs) lastTs = ts;
    const dt = ts - lastTs;
    lastTs = ts;
    tickStep(dt);
    draw();
    hud();
    raf = requestAnimationFrame(loop);
  }

  let lastTs = 0;

  function startBattle() {
    xpSent = false;
    if (aiTimer) {
      clearTimeout(aiTimer);
      aiTimer = null;
    }
    board = emptyBoard();
    piece = null;
    dropAcc = 0;
    softDrop = false;
    running = true;
    paused = false;
    gameOver = false;
    won = false;
    botHp = START_BOT_HP;
    playerDanger = 0;
    overlay.hidden = true;
    setStatus("Clear lines to open math attacks. Arrows move · Up spins · Space slams.");
    spawn();
    lastTs = 0;
    if (raf) cancelAnimationFrame(raf);
    raf = requestAnimationFrame(loop);
    scheduleAiAttack();
  }

  btnStart.addEventListener("click", startBattle);
  btnReset.addEventListener("click", () => {
    if (aiTimer) clearTimeout(aiTimer);
    startBattle();
  });
  qSubmit.addEventListener("click", submitAnswer);
  qInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") submitAnswer();
  });

  window.addEventListener("keydown", (e) => {
    if (!running || gameOver) return;
    if (!overlay.hidden) return;
    if (e.code === "ArrowLeft") {
      e.preventDefault();
      tryMove(-1, 0);
    }
    if (e.code === "ArrowRight") {
      e.preventDefault();
      tryMove(1, 0);
    }
    if (e.code === "ArrowDown") {
      e.preventDefault();
      softDrop = true;
      tryMove(0, 1);
    }
    if (e.code === "ArrowUp") {
      e.preventDefault();
      tryRotate();
    }
    if (e.code === "Space") {
      e.preventDefault();
      hardDrop();
    }
  });
  window.addEventListener("keyup", (e) => {
    if (e.code === "ArrowDown") softDrop = false;
  });

  draw();
  hud();
})();
