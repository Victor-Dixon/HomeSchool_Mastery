#!/usr/bin/env node
"use strict";

const assert = require("assert");
const { composeQuizzes, generateQuizzesFromSkills } = require("../quiz-engine");

function validateQuestionShape(question) {
  assert.strictEqual(typeof question.q, "string", "q must be a string");
  assert.ok(Array.isArray(question.choices), "choices must be an array");
  assert.strictEqual(question.choices.length, 4, "choices must contain exactly 4 options");
  assert.strictEqual(typeof question.answer, "number", "answer must be a number index");
  assert.ok(question.answer >= 0 && question.answer < 4, "answer index must be in [0, 3]");
}

function testSsotCoverageAndShape() {
  const skills = [
    { id: "s1", text: "Multiply fractions", subject: "Math", grade: 6 },
    { id: "s2", text: "Use context clues", subject: "ELAR", grade: 6 },
    { id: "s3", text: "Unknown domain skill", subject: "Science", grade: 7 },
  ];

  const quizzes = generateQuizzesFromSkills(skills, 3);
  assert.deepStrictEqual(Object.keys(quizzes).sort(), ["s1", "s2", "s3"], "every SSOT skill id must get quizzes");

  for (const skillId of Object.keys(quizzes)) {
    assert.strictEqual(quizzes[skillId].length, 3, "each skill should have requested number of questions");
    quizzes[skillId].forEach(validateQuestionShape);
  }
}

function testManualOverrideComposition() {
  const auto = {
    "skill-1": [{ q: "auto", choices: ["a", "b", "c", "d"], answer: 0 }],
    "skill-2": [{ q: "auto2", choices: ["a", "b", "c", "d"], answer: 1 }],
  };
  const manual = {
    "skill-1": [{ q: "manual", choices: ["a", "b", "c", "d"], answer: 2 }],
  };

  const composed = composeQuizzes(auto, manual);
  assert.strictEqual(composed["skill-1"][0].q, "manual", "manual quizzes must override auto quizzes");
  assert.strictEqual(composed["skill-2"][0].q, "auto2", "un-overridden auto quizzes must remain");
}

function run() {
  testSsotCoverageAndShape();
  testManualOverrideComposition();
  console.log("quiz-engine tests passed");
}

run();
