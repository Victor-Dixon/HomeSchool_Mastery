#!/usr/bin/env node
/**
 * Homeschool Mastery — Server
 * Zero external dependencies. Uses Node built-ins only.
 * Run: node server.js
 * Then open http://YOUR_LOCAL_IP:3000 on any device on your network.
 */

const http = require("http");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

// ─── Config ───────────────────────────────────────────────────────────────────
const PORT = 3000;
const DATA_FILE = path.join(__dirname, "data.json");

// ─── Passwords ────────────────────────────────────────────────────────────────
const USERS = {
  charlie: { role: "student", grade: 6, emoji: "🧒", color: "#7c3aed", pin: "1234" },
  chris:   { role: "student", grade: 7, emoji: "🧑", color: "#0ea5e9", pin: "5678" },
  victor:  { role: "teacher", emoji: "🏫", color: "#16a34a", pin: "9999" },
};

// ─── Skills DB ────────────────────────────────────────────────────────────────
const SKILLS_DB = {
  charlie: [
    { id: "c6-ela-1",  text: "Use context clues (definition, analogy) to clarify word meanings", subject: "ELAR" },
    { id: "c6-ela-2",  text: "Determine meanings of Greek/Latin roots: mis/mit, bene, man, vac, scrib/script", subject: "ELAR" },
    { id: "c6-ela-3",  text: "Make inferences using text evidence", subject: "ELAR" },
    { id: "c6-ela-4",  text: "Summarize and paraphrase texts", subject: "ELAR" },
    { id: "c6-ela-5",  text: "Analyze how setting influences characters and plot", subject: "ELAR" },
    { id: "c6-ela-6",  text: "Identify multiple themes using text evidence", subject: "ELAR" },
    { id: "c6-ela-7",  text: "Analyze plot elements (rising action, climax, resolution)", subject: "ELAR" },
    { id: "c6-ela-8",  text: "Explain author's purpose and message", subject: "ELAR" },
    { id: "c6-ela-9",  text: "Identify figurative language: metaphor, personification", subject: "ELAR" },
    { id: "c6-ela-10", text: "Write responses using text evidence", subject: "ELAR" },
    { id: "c6-math-1", text: "Multiply and divide decimals", subject: "Math" },
    { id: "c6-math-2", text: "Multiply fractions and whole numbers", subject: "Math" },
    { id: "c6-math-3", text: "Divide fractions", subject: "Math" },
    { id: "c6-math-4", text: "Solve problems with ratios and unit rates", subject: "Math" },
    { id: "c6-math-5", text: "Graph points in all four quadrants", subject: "Math" },
    { id: "c6-math-6", text: "Interpret data: histograms, box plots, stem-and-leaf", subject: "Math" },
    { id: "c6-math-7", text: "Understand proportional relationships", subject: "Math" },
    { id: "c6-math-8", text: "Use equations and inequalities to represent situations", subject: "Math" },
  ],
  chris: [
    { id: "c7-ela-1",  text: "Use context (contrast, cause/effect) to clarify word meanings", subject: "ELAR" },
    { id: "c7-ela-2",  text: "Greek/Latin roots: omni, log/logue, gen, vid/vis, phil, luc", subject: "ELAR" },
    { id: "c7-ela-3",  text: "Make inferences and support with text evidence", subject: "ELAR" },
    { id: "c7-ela-4",  text: "Analyze how character responses develop plot", subject: "ELAR" },
    { id: "c7-ela-5",  text: "Analyze nonlinear plot elements (flashback)", subject: "ELAR" },
    { id: "c7-ela-6",  text: "Analyze how setting influences character and plot", subject: "ELAR" },
    { id: "c7-ela-7",  text: "Identify and analyze multiple themes", subject: "ELAR" },
    { id: "c7-ela-8",  text: "Analyze figurative language including extended metaphor", subject: "ELAR" },
    { id: "c7-ela-9",  text: "Identify unreliable narrator and point of view", subject: "ELAR" },
    { id: "c7-ela-10", text: "Write argumentative responses with evidence", subject: "ELAR" },
    { id: "c7-math-1", text: "Operations with integers (negative numbers)", subject: "Math" },
    { id: "c7-math-2", text: "Solve problems with rational numbers", subject: "Math" },
    { id: "c7-math-3", text: "Proportionality: ratios, rates, percent change", subject: "Math" },
    { id: "c7-math-4", text: "Solve linear equations and inequalities", subject: "Math" },
    { id: "c7-math-5", text: "Scale drawings and similar figures", subject: "Math" },
    { id: "c7-math-6", text: "Calculate area/circumference of circles", subject: "Math" },
    { id: "c7-math-7", text: "Volume of prisms and pyramids", subject: "Math" },
    { id: "c7-math-8", text: "Probability of simple and compound events", subject: "Math" },
  ],
};

// ─── Quiz Questions (2-3 per skill) ───────────────────────────────────────────
const QUIZZES = {
  "c6-ela-1": [
    { q: "In the sentence 'The luminous, or glowing, moon lit the path,' what does 'luminous' mean?", choices: ["Dark","Glowing","Tiny","Loud"], answer: 1 },
    { q: "Which is an example of a definition context clue?", choices: ["She felt elated, sad about the loss.","The carburetor, which is the engine part that mixes air and fuel, failed.","He ran quickly.","The dog barked."], answer: 1 },
    { q: "An analogy context clue compares the unknown word to something…", choices: ["Opposite","Similar","Unrelated","Smaller"], answer: 1 },
  ],
  "c6-ela-2": [
    { q: "The root 'bene' means:", choices: ["Bad","Well/Good","Under","Over"], answer: 1 },
    { q: "The root 'scrib/script' relates to:", choices: ["Speaking","Writing","Running","Seeing"], answer: 1 },
    { q: "A 'manuscript' is best described as:", choices: ["A hand-written document","A loud speech","A map","A science experiment"], answer: 0 },
  ],
  "c6-ela-3": [
    { q: "An inference is:", choices: ["A direct quote from the text","A conclusion using clues + your own knowledge","The author's main point","A summary of events"], answer: 1 },
    { q: "Text evidence means:", choices: ["Your personal opinion","A guess","Specific words or details from the text","What happens at the end"], answer: 2 },
  ],
  "c6-ela-4": [
    { q: "A summary should:", choices: ["Include every detail","Retell only the most important ideas","Be longer than the original","Ignore the main idea"], answer: 1 },
    { q: "When you paraphrase, you:", choices: ["Copy the text word-for-word","Rewrite the idea in your own words","Add new information","Quote the author"], answer: 1 },
  ],
  "c6-ela-5": [
    { q: "How can setting influence a character?", choices: ["It has no effect","It can shape their fears, values, and choices","It only affects the plot","It determines their name"], answer: 1 },
    { q: "A story set in a war zone would most likely make characters feel:", choices: ["Peaceful","Safe","Anxious or brave","Bored"], answer: 2 },
  ],
  "c6-ela-6": [
    { q: "A theme is:", choices: ["The plot summary","A central message or lesson in the text","The setting description","The character's name"], answer: 1 },
    { q: "How do you support a theme claim?", choices: ["By guessing","With text evidence","By asking the author","With pictures"], answer: 1 },
  ],
  "c6-ela-7": [
    { q: "What happens at the climax of a story?", choices: ["Characters are introduced","The highest point of tension","The conflict is explained","The story ends peacefully"], answer: 1 },
    { q: "Rising action includes:", choices: ["Events that build tension toward the climax","The resolution","The exposition","The falling action"], answer: 0 },
    { q: "Resolution occurs:", choices: ["At the beginning","Before the climax","After the climax, when conflicts are resolved","During rising action"], answer: 2 },
  ],
  "c6-ela-8": [
    { q: "An author's purpose can be:", choices: ["To confuse the reader","To persuade, inform, or entertain","To hide information","Only to entertain"], answer: 1 },
    { q: "What is an author's message?", choices: ["The title","The deeper idea the author wants readers to understand","The character's name","The genre"], answer: 1 },
  ],
  "c6-ela-9": [
    { q: "'The stars danced in the sky' is an example of:", choices: ["Simile","Metaphor","Personification","Alliteration"], answer: 2 },
    { q: "'Life is a roller coaster' is an example of:", choices: ["Simile","Metaphor","Hyperbole","Personification"], answer: 1 },
  ],
  "c6-ela-10": [
    { q: "When writing a response with text evidence, you should:", choices: ["Only share your opinion","Include a quote or paraphrase and explain it","Copy the whole passage","Ignore the question"], answer: 1 },
    { q: "A strong written response begins with:", choices: ["A random fact","A clear claim or answer to the question","A personal story","A definition"], answer: 1 },
  ],
  "c6-math-1": [
    { q: "3.2 × 1.5 = ?", choices: ["4.8","5.0","4.2","3.7"], answer: 0 },
    { q: "8.4 ÷ 0.4 = ?", choices: ["2.1","21","0.21","210"], answer: 1 },
    { q: "0.06 × 0.3 = ?", choices: ["1.8","0.18","0.018","18"], answer: 2 },
  ],
  "c6-math-2": [
    { q: "3/4 × 8 = ?", choices: ["6","24","3","8"], answer: 0 },
    { q: "2/3 × 12 = ?", choices: ["4","8","6","10"], answer: 1 },
  ],
  "c6-math-3": [
    { q: "3/4 ÷ 1/2 = ?", choices: ["3/8","1 1/2","6/4","3/2"], answer: 1 },
    { q: "2 ÷ 1/4 = ?", choices: ["1/2","4","8","6"], answer: 2 },
  ],
  "c6-math-4": [
    { q: "If 5 apples cost $2.50, what is the unit rate per apple?", choices: ["$0.25","$0.50","$1.00","$2.00"], answer: 1 },
    { q: "A ratio of 3:9 simplifies to:", choices: ["1:3","2:6","3:3","1:4"], answer: 0 },
  ],
  "c6-math-5": [
    { q: "The point (-3, 2) is in which quadrant?", choices: ["I","II","III","IV"], answer: 1 },
    { q: "Which point is in Quadrant III?", choices: ["(2,3)","(-1,4)","(-2,-5)","(3,-1)"], answer: 2 },
  ],
  "c6-math-6": [
    { q: "A histogram shows:", choices: ["Individual data points","Frequency over intervals","Exact values","Pie slices"], answer: 1 },
    { q: "In a box plot, the middle line represents:", choices: ["Mean","Mode","Median","Range"], answer: 2 },
  ],
  "c6-math-7": [
    { q: "In a proportional relationship y = kx, 'k' is called:", choices: ["The variable","The constant of proportionality","The y-intercept","The slope"], answer: 1 },
    { q: "If y is proportional to x and y=10 when x=2, find y when x=5.", choices: ["15","20","25","12"], answer: 2 },
  ],
  "c6-math-8": [
    { q: "Which is an example of an inequality?", choices: ["x = 5","x + 3","x > 5","x + y"], answer: 2 },
    { q: "The equation 2x + 3 = 11 has the solution:", choices: ["x=3","x=4","x=5","x=6"], answer: 1 },
  ],
  // Chris (7th grade)
  "c7-ela-1": [
    { q: "Which is a cause/effect context clue?", choices: ["She was ebullient, which means overjoyed.","Because it was frigid, he wore his warmest coat.","He ran fast.","She smiled."], answer: 1 },
    { q: "Contrast clues use words like:", choices: ["Also, similarly, likewise","However, but, unlike","Therefore, so, as a result","First, next, finally"], answer: 1 },
  ],
  "c7-ela-2": [
    { q: "The root 'omni' means:", choices: ["None","All","Some","One"], answer: 1 },
    { q: "The root 'phil' means:", choices: ["Fear","Love","Against","Below"], answer: 1 },
    { q: "'Lucid' relates to which root?", choices: ["log","gen","luc","vid"], answer: 2 },
  ],
  "c7-ela-3": [
    { q: "An inference goes beyond what is stated by using:", choices: ["Imagination only","Text clues and background knowledge","Random guessing","Author's biography"], answer: 1 },
    { q: "Which phrase best introduces text evidence?", choices: ["I think maybe…","According to the text…","It could be that…","Someone said…"], answer: 1 },
  ],
  "c7-ela-4": [
    { q: "Character responses develop plot when a character's action:", choices: ["Has no consequence","Leads to a new event or conflict","Ends the story immediately","Is ignored by others"], answer: 1 },
    { q: "A character who overcomes fear would most likely:", choices: ["Avoid challenges","Take on a difficult task","Give up","Stay home"], answer: 1 },
  ],
  "c7-ela-5": [
    { q: "A flashback in a story:", choices: ["Previews future events","Interrupts the present to show a past scene","Summarizes the ending","Introduces new characters"], answer: 1 },
    { q: "Nonlinear plot means:", choices: ["Events are told in exact order","Events are told out of chronological order","There is no plot","The story has one event"], answer: 1 },
  ],
  "c7-ela-6": [
    { q: "If a character lives in poverty, this setting most likely shapes:", choices: ["Their athletic ability","Their survival instincts and values","Their humor","Their musical talent"], answer: 1 },
    { q: "Setting includes:", choices: ["Characters only","Time, place, and social environment","Only the location","The theme"], answer: 1 },
  ],
  "c7-ela-7": [
    { q: "A text can have multiple themes when:", choices: ["It is confusing","Different characters or events each carry separate messages","The author made a mistake","It has many characters"], answer: 1 },
    { q: "To identify a theme, you look for:", choices: ["The title only","Repeated ideas, character lessons, and author signals","Random sentences","The longest paragraph"], answer: 1 },
  ],
  "c7-ela-8": [
    { q: "An extended metaphor:", choices: ["Is used once and dropped","Continues throughout a passage or poem","Is always about nature","Uses 'like' or 'as'"], answer: 1 },
    { q: "'Her smile was a sunrise that warmed every room' is:", choices: ["A simile","Personification","A metaphor","Hyperbole"], answer: 2 },
  ],
  "c7-ela-9": [
    { q: "An unreliable narrator:", choices: ["Always tells the truth","May distort or misrepresent events intentionally or unintentionally","Has no role in the story","Speaks in third person"], answer: 1 },
    { q: "First-person point of view uses:", choices: ["He/she/they","I/me/my","You","One/ones"], answer: 1 },
  ],
  "c7-ela-10": [
    { q: "An argumentative response requires:", choices: ["Only a story","A claim + evidence + reasoning","A personal narrative","A list of facts only"], answer: 1 },
    { q: "Which word signals a counterargument?", choices: ["Therefore","Furthermore","Although","In addition"], answer: 2 },
  ],
  "c7-math-1": [
    { q: "-5 + (-3) = ?", choices: ["-8","8","-2","2"], answer: 0 },
    { q: "-4 × (-3) = ?", choices: ["-12","12","-7","7"], answer: 1 },
    { q: "-10 ÷ 2 = ?", choices: ["5","-5","20","-20"], answer: 1 },
  ],
  "c7-math-2": [
    { q: "1/2 + (-3/4) = ?", choices: ["1/4","-1/4","5/4","-5/4"], answer: 1 },
    { q: "Rational numbers include:", choices: ["Only whole numbers","Only fractions","Integers and fractions","Irrational numbers only"], answer: 2 },
  ],
  "c7-math-3": [
    { q: "A shirt was $40 and is now $30. What is the percent decrease?", choices: ["10%","25%","33%","20%"], answer: 1 },
    { q: "If the ratio of boys to girls is 3:5 and there are 24 boys, how many girls?", choices: ["30","35","40","45"], answer: 2 },
  ],
  "c7-math-4": [
    { q: "Solve: 2x - 3 = 11", choices: ["x=4","x=7","x=6","x=5"], answer: 1 },
    { q: "Solve: x + 5 > 12", choices: ["x > 7","x > 17","x < 7","x = 7"], answer: 0 },
  ],
  "c7-math-5": [
    { q: "If two figures are similar, their corresponding sides are:", choices: ["Equal","Proportional","Perpendicular","Parallel only"], answer: 1 },
    { q: "A scale of 1:50 means 1 cm on the drawing equals ___ cm in real life.", choices: ["1","5","50","500"], answer: 2 },
  ],
  "c7-math-6": [
    { q: "The formula for circumference of a circle is:", choices: ["πr²","2πr","πd²","r²π"], answer: 1 },
    { q: "If the radius is 7, what is the area? (Use π ≈ 3.14)", choices: ["43.96","153.86","21.98","44"], answer: 1 },
  ],
  "c7-math-7": [
    { q: "The formula for volume of a rectangular prism is:", choices: ["l×w","l+w+h","l×w×h","2(l+w)"], answer: 2 },
    { q: "A pyramid's volume compared to a prism with the same base and height is:", choices: ["Equal","Double","One-third","Half"], answer: 2 },
  ],
  "c7-math-8": [
    { q: "If you flip a coin, the probability of heads is:", choices: ["1","0","1/2","1/4"], answer: 2 },
    { q: "For compound events A and B that are independent, P(A and B) = ?", choices: ["P(A)+P(B)","P(A)×P(B)","P(A)-P(B)","P(A)÷P(B)"], answer: 1 },
  ],
};

// ─── Badge Definitions ────────────────────────────────────────────────────────
const BADGES = [
  { id: "first_blood",   label: "First Win",       emoji: "⚡", desc: "Mastered your first skill",             condition: s => s.mastered >= 1 },
  { id: "on_fire",       label: "On Fire",          emoji: "🔥", desc: "Mastered 3 skills",                    condition: s => s.mastered >= 3 },
  { id: "scholar",       label: "Scholar",          emoji: "🎓", desc: "Mastered 5 skills",                    condition: s => s.mastered >= 5 },
  { id: "legend",        label: "Legend",           emoji: "🏆", desc: "Mastered 10 skills",                   condition: s => s.mastered >= 10 },
  { id: "math_wizard",   label: "Math Wizard",      emoji: "🧮", desc: "Mastered all Math skills",             condition: s => s.mathMastered >= s.mathTotal && s.mathTotal > 0 },
  { id: "word_master",   label: "Word Master",      emoji: "📚", desc: "Mastered all ELAR skills",             condition: s => s.elarMastered >= s.elarTotal && s.elarTotal > 0 },
  { id: "perfectionist", label: "Perfectionist",    emoji: "💎", desc: "100% quiz score on a skill",           condition: s => s.perfectQuiz },
  { id: "grinder",       label: "Grinder",          emoji: "💪", desc: "Attempted 5+ quizzes",                 condition: s => s.quizAttempts >= 5 },
  { id: "comeback",      label: "Comeback Kid",     emoji: "🔄", desc: "Mastered a skill marked Needs Work",   condition: s => s.comebackCount >= 1 },
  { id: "unstoppable",   label: "Unstoppable",      emoji: "🚀", desc: "Mastered all skills",                  condition: s => s.mastered >= s.total && s.total > 0 },
];

// ─── XP Values ────────────────────────────────────────────────────────────────
const XP = { quiz_correct: 30, quiz_perfect: 50, mastered: 100, needs_work: 5, badge: 200 };

// ─── Data Store ───────────────────────────────────────────────────────────────
function defaultStudentData(studentId) {
  return {
    skills: SKILLS_DB[studentId].map(s => ({ ...s, status: "unseen", quizHistory: [] })),
    xp: 0,
    level: 1,
    badges: [],
    quizAttempts: 0,
    comebackCount: 0,
    perfectQuiz: false,
    lastSeen: null,
  };
}

let DB = { charlie: null, chris: null };

function loadDB() {
  if (fs.existsSync(DATA_FILE)) {
    try {
      const raw = JSON.parse(fs.readFileSync(DATA_FILE, "utf8"));
      DB.charlie = raw.charlie || defaultStudentData("charlie");
      DB.chris   = raw.chris   || defaultStudentData("chris");
      // patch new skills if any
      for (const sid of ["charlie", "chris"]) {
        const existing = new Set(DB[sid].skills.map(s => s.id));
        SKILLS_DB[sid].forEach(s => {
          if (!existing.has(s.id)) DB[sid].skills.push({ ...s, status: "unseen", quizHistory: [] });
        });
      }
      return;
    } catch (_) {}
  }
  DB.charlie = defaultStudentData("charlie");
  DB.chris   = defaultStudentData("chris");
}

function saveDB() {
  fs.writeFileSync(DATA_FILE, JSON.stringify(DB, null, 2));
}

// ─── Badge & XP Logic ─────────────────────────────────────────────────────────
function computeStats(studentId) {
  const d = DB[studentId];
  const skills = d.skills;
  const mastered = skills.filter(s => s.status === "mastered").length;
  const total    = skills.length;
  const mathSkills = skills.filter(s => s.subject === "Math");
  const elarSkills = skills.filter(s => s.subject === "ELAR");
  return {
    mastered, total,
    mathMastered: mathSkills.filter(s => s.status === "mastered").length,
    mathTotal: mathSkills.length,
    elarMastered: elarSkills.filter(s => s.status === "mastered").length,
    elarTotal: elarSkills.length,
    quizAttempts: d.quizAttempts,
    comebackCount: d.comebackCount,
    perfectQuiz: d.perfectQuiz,
  };
}

function checkBadges(studentId) {
  const d = DB[studentId];
  const stats = computeStats(studentId);
  const newBadges = [];
  for (const badge of BADGES) {
    if (!d.badges.includes(badge.id) && badge.condition(stats)) {
      d.badges.push(badge.id);
      d.xp += XP.badge;
      newBadges.push(badge);
    }
  }
  d.level = Math.floor(d.xp / 500) + 1;
  return newBadges;
}

// ─── CSV Export ───────────────────────────────────────────────────────────────
function generateCSV() {
  const rows = [["Student","Grade","Subject","Skill","Status","Quiz Attempts","XP"]];
  for (const [sid, user] of Object.entries(USERS)) {
    if (user.role !== "student") continue;
    const d = DB[sid];
    for (const skill of d.skills) {
      const attempts = skill.quizHistory ? skill.quizHistory.length : 0;
      rows.push([sid, user.grade, skill.subject, `"${skill.text}"`, skill.status, attempts, d.xp]);
    }
  }
  return rows.map(r => r.join(",")).join("\n");
}

// ─── WebSocket Server ─────────────────────────────────────────────────────────
const clients = new Map(); // socket -> { userId }

function wsSend(socket, msg) {
  try {
    const data = JSON.stringify(msg);
    const buf = Buffer.from(data);
    const header = wsFrame(buf);
    socket.write(header);
  } catch (_) {}
}

function wsFrame(buf) {
  const len = buf.length;
  let header;
  if (len < 126) {
    header = Buffer.alloc(2);
    header[0] = 0x81;
    header[1] = len;
  } else if (len < 65536) {
    header = Buffer.alloc(4);
    header[0] = 0x81; header[1] = 126;
    header.writeUInt16BE(len, 2);
  } else {
    header = Buffer.alloc(10);
    header[0] = 0x81; header[1] = 127;
    header.writeBigUInt64BE(BigInt(len), 2);
  }
  return Buffer.concat([header, buf]);
}

function wsParseFrame(buf) {
  if (buf.length < 2) return null;
  const fin = (buf[0] & 0x80) !== 0;
  const opcode = buf[0] & 0x0f;
  if (opcode === 0x8) return { type: "close" };
  const masked = (buf[1] & 0x80) !== 0;
  let payloadLen = buf[1] & 0x7f;
  let offset = 2;
  if (payloadLen === 126) { payloadLen = buf.readUInt16BE(2); offset = 4; }
  else if (payloadLen === 127) { payloadLen = Number(buf.readBigUInt64BE(2)); offset = 10; }
  if (!masked) return null;
  const mask = buf.slice(offset, offset + 4); offset += 4;
  if (buf.length < offset + payloadLen) return null;
  const payload = Buffer.alloc(payloadLen);
  for (let i = 0; i < payloadLen; i++) payload[i] = buf[offset + i] ^ mask[i % 4];
  return { type: "message", data: payload.toString("utf8") };
}

function broadcast(msg, exceptSocket) {
  for (const [sock] of clients) {
    if (sock !== exceptSocket) wsSend(sock, msg);
  }
}

function broadcastAll(msg) {
  for (const [sock] of clients) wsSend(sock, msg);
}

function handleMessage(socket, rawMsg) {
  let msg;
  try { msg = JSON.parse(rawMsg); } catch { return; }
  const info = clients.get(socket) || {};

  if (msg.type === "auth") {
    const user = USERS[msg.userId];
    if (!user || user.pin !== String(msg.pin)) {
      return wsSend(socket, { type: "auth_fail" });
    }
    clients.set(socket, { userId: msg.userId, role: user.role });
    const payload = { type: "auth_ok", userId: msg.userId, role: user.role, user };
    if (user.role === "student") {
      payload.studentData = DB[msg.userId];
      payload.quizzes = QUIZZES;
      payload.badges = BADGES;
    } else {
      payload.allData = DB;
      payload.users = USERS;
      payload.badges = BADGES;
    }
    return wsSend(socket, payload);
  }

  if (msg.type === "update_skill") {
    const { studentId, skillId, status } = msg;
    if (!DB[studentId]) return;
    const skill = DB[studentId].skills.find(s => s.id === skillId);
    if (!skill) return;
    const wasNeedsWork = skill.status === "needs_work";
    skill.status = status;
    if (status === "mastered" && wasNeedsWork) {
      DB[studentId].comebackCount = (DB[studentId].comebackCount || 0) + 1;
    }
    if (status === "mastered") DB[studentId].xp += XP.mastered;
    if (status === "needs_work") DB[studentId].xp += XP.needs_work;
    const newBadges = checkBadges(studentId);
    saveDB();
    broadcastAll({ type: "skill_updated", studentId, skillId, status, xp: DB[studentId].xp, level: DB[studentId].level, badges: DB[studentId].badges, newBadges });
    return;
  }

  if (msg.type === "quiz_result") {
    const { studentId, skillId, score, total: qtotal } = msg;
    if (!DB[studentId]) return;
    const skill = DB[studentId].skills.find(s => s.id === skillId);
    if (!skill) return;
    if (!skill.quizHistory) skill.quizHistory = [];
    skill.quizHistory.push({ score, total: qtotal, ts: Date.now() });
    DB[studentId].quizAttempts = (DB[studentId].quizAttempts || 0) + 1;
    const earned = score * XP.quiz_correct;
    DB[studentId].xp += earned;
    const percent = score / qtotal;
    if (percent === 1) {
      DB[studentId].perfectQuiz = true;
      DB[studentId].xp += XP.quiz_perfect;
    }
    if (percent >= 0.67) skill.status = "mastered";
    else skill.status = "needs_work";
    const newBadges = checkBadges(studentId);
    saveDB();
    broadcastAll({ type: "quiz_done", studentId, skillId, score, total: qtotal, newStatus: skill.status, xp: DB[studentId].xp, level: DB[studentId].level, badges: DB[studentId].badges, newBadges });
    return;
  }

  if (msg.type === "get_csv") {
    return wsSend(socket, { type: "csv_data", csv: generateCSV() });
  }

  if (msg.type === "ping") {
    return wsSend(socket, { type: "pong" });
  }
}

function handleUpgrade(req, socket) {
  const key = req.headers["sec-websocket-key"];
  if (!key) { socket.destroy(); return; }
  const accept = crypto.createHash("sha1").update(key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").digest("base64");
  socket.write(
    "HTTP/1.1 101 Switching Protocols\r\n" +
    "Upgrade: websocket\r\n" +
    "Connection: Upgrade\r\n" +
    `Sec-WebSocket-Accept: ${accept}\r\n\r\n`
  );
  clients.set(socket, {});
  let buf = Buffer.alloc(0);
  socket.on("data", chunk => {
    buf = Buffer.concat([buf, chunk]);
    while (buf.length >= 2) {
      const frame = wsParseFrame(buf);
      if (!frame) break;
      if (frame.type === "close") { socket.destroy(); break; }
      if (frame.type === "message") handleMessage(socket, frame.data);
      // advance buffer
      let payloadLen = buf[1] & 0x7f;
      let offset = 2;
      if (payloadLen === 126) { payloadLen = buf.readUInt16BE(2); offset = 4; }
      else if (payloadLen === 127) { payloadLen = Number(buf.readBigUInt64BE(2)); offset = 10; }
      const masked = (buf[1] & 0x80) !== 0;
      offset += masked ? 4 : 0;
      buf = buf.slice(offset + payloadLen);
    }
  });
  socket.on("close", () => clients.delete(socket));
  socket.on("error", () => clients.delete(socket));
}

// ─── HTTP Server ──────────────────────────────────────────────────────────────
const HTML_FILE = path.join(__dirname, "app.html");

const server = http.createServer((req, res) => {
  if (req.url === "/" || req.url === "/index.html") {
    if (fs.existsSync(HTML_FILE)) {
      res.writeHead(200, { "Content-Type": "text/html" });
      res.end(fs.readFileSync(HTML_FILE));
    } else {
      res.writeHead(404); res.end("app.html not found");
    }
  } else {
    res.writeHead(404); res.end("Not found");
  }
});

server.on("upgrade", (req, socket, head) => {
  if (req.url === "/ws") handleUpgrade(req, socket);
  else socket.destroy();
});

loadDB();
server.listen(PORT, "0.0.0.0", () => {
  const os = require("os");
  const interfaces = os.networkInterfaces();
  let localIp = "YOUR_LOCAL_IP";
  outer: for (const iface of Object.values(interfaces)) {
    for (const addr of iface) {
      if (addr.family === "IPv4" && !addr.internal) { localIp = addr.address; break outer; }
    }
  }
  console.log("╔══════════════════════════════════════════════╗");
  console.log("║  🏫 Homeschool Mastery Server is LIVE!       ║");
  console.log("╠══════════════════════════════════════════════╣");
  console.log(`║  Local:   http://localhost:${PORT}              ║`);
  console.log(`║  Network: http://${localIp}:${PORT}         ║`);
  console.log("╠══════════════════════════════════════════════╣");
  console.log("║  Pins:  charlie=1234  chris=5678  victor=9999║");
  console.log("╚══════════════════════════════════════════════╝");
});
