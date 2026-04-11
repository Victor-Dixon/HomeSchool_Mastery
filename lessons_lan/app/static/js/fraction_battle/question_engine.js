/**
 * Fraction battle — like-denominator fraction prompts.
 * window.FractionBattleQuestions.nextQuestion(lineClearCount)
 */
(function (global) {
  "use strict";

  function gcd(a, b) {
    a = Math.abs(a);
    b = Math.abs(b);
    while (b) {
      const t = b;
      b = a % b;
      a = t;
    }
    return a || 1;
  }

  function simplifyFrac(n, d) {
    if (d < 0) {
      n = -n;
      d = -d;
    }
    const g = gcd(n, d);
    return { n: Math.trunc(n / g), d: Math.trunc(d / g) };
  }

  function formatFrac(fr) {
    return fr.n + "/" + fr.d;
  }

  const DENOMS = [4, 5, 6, 8, 10, 12];

  function pickDenom() {
    return DENOMS[(Math.random() * DENOMS.length) | 0];
  }

  function ri(a, b) {
    return a + ((Math.random() * (b - a + 1)) | 0);
  }

  function makeEasy() {
    const denom = pickDenom();
    const add = Math.random() < 0.5;
    if (add) {
      const maxSum = denom - 1;
      const s = ri(2, Math.max(2, maxSum));
      const a = ri(1, s - 1);
      const b = s - a;
      const ans = simplifyFrac(s, denom);
      return {
        question: `${a}/${denom} + ${b}/${denom} = ?`,
        answer: formatFrac(ans),
        difficulty: "easy",
        answerPair: [ans.n, ans.d],
      };
    }
    const a = ri(2, denom - 1);
    const b = ri(1, a - 1);
    const n = a - b;
    const ans = simplifyFrac(n, denom);
    return {
      question: `${a}/${denom} - ${b}/${denom} = ?`,
      answer: formatFrac(ans),
      difficulty: "easy",
      answerPair: [ans.n, ans.d],
    };
  }

  function makeMedium() {
    const denom = pickDenom();
    const a = ri(1, denom - 3);
    const b = ri(1, denom - 3);
    let sum1 = a + b;
    if (sum1 >= denom) return makeEasy();
    const c = ri(1, Math.min(sum1 - 1, denom - 2));
    const n = sum1 - c;
    if (n <= 0) return makeMedium();
    const ans = simplifyFrac(n, denom);
    return {
      question: `${a}/${denom} + ${b}/${denom} - ${c}/${denom} = ?`,
      answer: formatFrac(ans),
      difficulty: "medium",
      answerPair: [ans.n, ans.d],
    };
  }

  function makeHard() {
    const denom = pickDenom();
    const a = ri(1, denom - 2);
    const b = ri(1, denom - 2);
    const c = ri(1, denom - 2);
    const sum2 = a + b;
    if (sum2 >= denom) return makeHard();
    if (c >= sum2) return makeHard();
    let acc = sum2 - c;
    const room = denom - 1 - acc;
    if (room < 1) return makeHard();
    const d = ri(1, Math.min(room, 5));
    acc += d;
    const ans = simplifyFrac(acc, denom);
    return {
      question: `${a}/${denom} + ${b}/${denom} - ${c}/${denom} + ${d}/${denom} = ?`,
      answer: formatFrac(ans),
      difficulty: "hard",
      answerPair: [ans.n, ans.d],
    };
  }

  function nextQuestion(lineClearCount) {
    const c = Math.max(1, lineClearCount | 0);
    if (c >= 3) return makeHard();
    if (c === 2) return makeMedium();
    return makeEasy();
  }

  global.FractionBattleQuestions = {
    nextQuestion,
    simplifyFrac,
    formatFrac,
  };
})(typeof window !== "undefined" ? window : globalThis);
