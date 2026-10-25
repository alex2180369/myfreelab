// Runs several form scenarios against the live robotics school page (fetch is stubbed, nothing is written).
const { execFileSync } = require("child_process");
const path = require("path");

const URL = "https://robotex.myfreelab.ru/";
const script = path.join(__dirname, "jsdom_form_test.js");
const scenarios = [
  ["Latin name and email", { name: "Anna", surname: "Petrova", email: "anna.petrova@example.com" }],
  ["Hyphen and apostrophe", { name: "Mary-Jane", surname: "O'Neil", email: "mj@mail.example.org" }],
  ["Cyrillic name", { name: "Анна", surname: "Петрова", email: "anna@example.com" }],
  ["Cyrillic email", { name: "Anna", surname: "Petrova", email: "анна@пример.рф" }],
  ["Empty fields", { name: "", surname: "", email: "" }],
  ["Bad email", { name: "Anna", surname: "Petrova", email: "anna@" }],
];

for (const [title, fields] of scenarios) {
  const out = execFileSync("node", [script, URL, 'a[href="#trial"]', "trial-form", "trial-status", JSON.stringify(fields)], {
    encoding: "utf8",
    timeout: 60000,
  });
  const r = JSON.parse(out);
  console.log(`${title.padEnd(24)} -> sent: ${r.fetchCalls === 1 ? "YES" : "no "} | ${r.statusText}`);
}
