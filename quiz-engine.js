/* quiz-engine.js
   Auto-generates quiz questions from TEKS skill records.

   Expected input skill shape:
   {
     id: "6-math-fractions-01",
     text: "Multiply fractions",
     subject: "Math" | "ELAR" | "Science",
     grade: 6 | 7
   }

   Output shape:
   {
     [skillId]: [
       { q: "Question text", choices: ["A","B","C","D"], answer: 1 },
       ...
     ]
   }
*/

"use strict";

function randInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function shuffle(arr) {
  const copy = [...arr];
  for (let i = copy.length - 1; i > 0; i -= 1) {
    const j = randInt(0, i);
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

function mcq(question, correctChoice, distractors) {
  const choices = shuffle([correctChoice, ...distractors]).slice(0, 4);
  return { q: question, choices, answer: choices.indexOf(correctChoice) };
}

function gcd(a, b) {
  let x = Math.abs(a);
  let y = Math.abs(b);
  while (y) {
    [x, y] = [y, x % y];
  }
  return x || 1;
}

function simplifyFraction(n, d) {
  const g = gcd(n, d);
  return [n / g, d / g];
}

function fracToString(n, d) {
  return d === 1 ? `${n}` : `${n}/${d}`;
}

const generators = {
  multiplyFractions() {
    const a = randInt(1, 8);
    const b = randInt(2, 9);
    const c = randInt(1, 8);
    const d = randInt(2, 9);
    const [n, den] = simplifyFraction(a * c, b * d);
    return mcq(`What is ${a}/${b} × ${c}/${d}?`, fracToString(n, den), [
      fracToString(a + c, b + d),
      fracToString(a * d, b * c),
      fracToString(a * c, b + d),
    ]);
  },
  divideFractions() {
    const a = randInt(1, 8);
    const b = randInt(2, 9);
    const c = randInt(1, 8);
    const d = randInt(2, 9);
    const [n, den] = simplifyFraction(a * d, b * c);
    return mcq(`What is ${a}/${b} ÷ ${c}/${d}?`, fracToString(n, den), [
      fracToString(a * c, b * d),
      fracToString(a + d, b + c),
      fracToString(a * b, c * d),
    ]);
  },
  multiplyDivideDecimals() {
    const a = (randInt(12, 95) / 10).toFixed(1);
    const b = randInt(2, 9);
    const answer = (Number(a) * b).toFixed(1);
    return mcq(`What is ${a} × ${b}?`, answer, [
      (Number(a) + b).toFixed(1),
      (Number(a) * (b + 1)).toFixed(1),
      (Number(a) / b).toFixed(1),
    ]);
  },
  ratiosRates() {
    const part = randInt(5, 30);
    const whole = part * randInt(2, 5);
    const pct = Math.round((part / whole) * 100);
    return mcq(`${part} is what percent of ${whole}?`, `${pct}%`, [
      `${part}%`,
      `${whole}%`,
      `${100 - pct}%`,
    ]);
  },
  linearEquations() {
    const x = randInt(2, 12);
    const a = randInt(2, 6);
    const b = randInt(1, 12);
    const c = a * x + b;
    return mcq(`Solve: ${a}x + ${b} = ${c}`, `${x}`, [`${x + 1}`, `${x - 1}`, `${c - b}`]);
  },
  inequalities() {
    const threshold = randInt(3, 15);
    return mcq(`Which value makes the inequality true: x > ${threshold}?`, `${threshold + 2}`, [
      `${threshold}`,
      `${threshold - 1}`,
      `${threshold - 2}`,
    ]);
  },
  circumference() {
    const r = randInt(2, 8);
    return mcq(`What is the circumference of a circle with radius ${r}?`, `${2 * r}π`, [
      `${r}π`,
      `${r * r}π`,
      `${2 * r * r}π`,
    ]);
  },
  probability() {
    const red = randInt(1, 5);
    const blue = randInt(1, 5);
    const total = red + blue;
    const [n, d] = simplifyFraction(red, total);
    return mcq(`A bag has ${red} red marbles and ${blue} blue marbles. Probability of red?`, fracToString(n, d), [
      fracToString(blue, total),
      fracToString(red, blue),
      fracToString(total, red),
    ]);
  },
  contextClues() {
    const bank = [
      mcq('The desert was arid, so dry no plants could grow there. "Arid" means:', "very dry", ["very cold", "crowded", "colorful"]),
      mcq('Marcus was benevolent; he looked for ways to help others. "Benevolent" means:', "kind and helpful", ["angry", "careless", "shy"]),
      mcq('The room was cluttered, with shoes and papers everywhere. "Cluttered" means:', "messy", ["empty", "quiet", "expensive"]),
    ];
    return bank[randInt(0, bank.length - 1)];
  },
  roots() {
    const bank = [
      mcq('In the word "benefit", root "bene" most likely means:', "good", ["move", "sound", "small"]),
      mcq('In the word "visible", root "vis" most likely means:', "see", ["hear", "light", "write"]),
      mcq('In the word "vacant", root "vac" most likely means:', "empty", ["crowded", "run", "warm"]),
    ];
    return bank[randInt(0, bank.length - 1)];
  },
  inferencing() {
    return mcq(
      "Jay grabbed an umbrella and looked at dark clouds before leaving. What can be inferred?",
      "Jay thinks it may rain.",
      ["Jay is going to the beach.", "Jay lost his umbrella.", "Jay overslept."]
    );
  },
  summaryParaphrase() {
    return mcq("When paraphrasing, you should:", "rewrite ideas in your own words", [
      "copy every word exactly",
      "change the meaning",
      "omit key ideas",
    ]);
  },
  defaultQuestion(skill) {
    return mcq(`Which statement best matches this skill: ${skill.text}?`, "It focuses on mastering this exact concept.", [
      "It is unrelated to this concept.",
      "It can be skipped without practice.",
      "It only matters for teachers, not students.",
    ]);
  },
};

const keywordMap = [
  { match: /multiply.*fraction|fraction.*multiply/i, gen: "multiplyFractions" },
  { match: /divide.*fraction|fraction.*divide/i, gen: "divideFractions" },
  { match: /decimal/i, gen: "multiplyDivideDecimals" },
  { match: /ratio|rate|percent|proportional/i, gen: "ratiosRates" },
  { match: /equation/i, gen: "linearEquations" },
  { match: /inequalit/i, gen: "inequalities" },
  { match: /area|circumference|circle/i, gen: "circumference" },
  { match: /probability|data/i, gen: "probability" },
  { match: /context clue/i, gen: "contextClues" },
  { match: /root|greek|latin/i, gen: "roots" },
  { match: /infer/i, gen: "inferencing" },
  { match: /summary|paraphrase/i, gen: "summaryParaphrase" },
];

function pickGenerator(skill) {
  const text = `${skill.text || ""} ${skill.subject || ""}`;
  const hit = keywordMap.find((entry) => entry.match.test(text));
  return hit ? generators[hit.gen] : generators.defaultQuestion;
}

function generateQuizzesFromSkills(skillsByStudent, perSkill = 3) {
  const skills = Array.isArray(skillsByStudent)
    ? skillsByStudent
    : Object.values(skillsByStudent || {}).flat();

  return skills.reduce((acc, skill) => {
    const gen = pickGenerator(skill);
    acc[skill.id] = Array.from({ length: perSkill }, () => gen(skill));
    return acc;
  }, {});
}

function composeQuizzes(autoQuizzes, manualQuizzes) {
  return { ...(autoQuizzes || {}), ...(manualQuizzes || {}) };
}

module.exports = {
  composeQuizzes,
  generateQuizzesFromSkills,
};
