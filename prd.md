Below is a **ready-to-drop “two-hop” prompt design** + a **minimal Python skeleton** that turns any file/link into a copy-pastable, hyper-personalised ChatGPT prompt in **exactly two Gemini API calls**.

---

## 1. Prompt #1 — *EXTRACT*

> **Goal:** Strip every type of input (video, PDF, tweet, image …) down to its most usable, action-oriented ideas and return them in clean JSON so the second call can stay fast and deterministic.

```text
SYSTEM  
You are “Insight-Extractor”, a multimodal analyst.  
Return concise, *action-ready* insights from the user-supplied content.

#  Output STRICTLY as JSON with this schema  #
{
  "title":       "<content title or best guess>",
  "summary":     "<≤200-word abstract>",
  "insights": [
     { "point": "<key takeaway 1>", "type": "actionable | fact | quote" },
     { "point": "<key takeaway 2>", "type": "actionable | fact | quote" },
     …
  ]
}

USER  
<<FILE_OR_LINK_PART>>      # e.g. Part.from_uri(...)
<<OPTIONAL_TEXT_SNIPPET>>  # if user pasted raw text, include as Part.from_text

INSTRUCTION  
Extract the *most important* ideas, favouring principles, check-lists and how-to
advice.  Ignore filler, greetings, ads, references, slides that only show logos.
```

*Why it works*

* The schema keeps everything machine-readable.
* Returning ≤5–7 bullet insights plus a 200-word abstract preserves latency.
* You can add a `language` field if you later need translation handling.

---

## 2. Prompt #2 — *PERSONALISE*

> **Goal:** Fuse the extracted insight JSON with lightweight user context from the form (interests, goals, background) and emit the final “Paste-into-ChatGPT” prompt.

```text
SYSTEM  
You are “Prompt-Architect”, expert at turning generic knowledge into
ChatGPT-ready prompts that feel written 1-on-1 for the user.

USER  
<<INSIGHTS_JSON_FROM_CALL_1>>

USER_CONTEXT
{
  "interests":  "<<form-interests>>",
  "goals":      "<<form-goals>>",
  "background": "<<form-background>>"
}

INSTRUCTION  
1. Draft a single prompt the user can paste into ChatGPT *as-is*.
2. The prompt must:
   • Briefly quote the key insights (no more than 80 words total).  
   • Ask ChatGPT to map those insights onto the user's goals & constraints.  
   • Request an actionable plan (steps, timeline, metrics).  
   • Remain under 500 words.  
3. Begin with:  "From what you know about me, I want you to apply these insights that I learned from a resource to my life... ".
4. End with:    "----".
Only output the prompt text—no extra commentary, no JSON.
```

*Sample output*

```
From what you know about me, I want you to apply these insights that I learned from a resource to my life...

I’ve just read these insights:
• Agents excel on complex, high-value tasks but aren’t a silver bullet.  
• Keep agents simple: Environment + Tools + Prompt loop.  
• Think like the agent: debug inside its 20k-token view.

My context ↴
– Interests: AI app-building, productivity hacks  
– Goal: launch Navoday AI MVP in 90 days while working a day-job  
– Background: Flutter lead, strong in LLMs, limited budget

Please:
1. Identify 2–3 tasks in my roadmap that *should* be agentic and 2 that shouldn’t, citing the complexity/value checklist.  
2. For the top agentic task, propose the minimal Environment, Tools & System Prompt.  
3. Show how to “think like the agent” when debugging that task.  
4. Give a 4-week execution plan with success metrics.

----
```

---

## 3. Minimal Python wiring (Agno API around Agents)

*Wire the form*

```ts
// pseudo-React
const onSubmit = async () => {
  const insights = await callExtractAPI(fileOrLink)
  const ctx      = {interests, goals, background}
  const prompt   = await callPersonaliseAPI(insights, ctx)
  setPromptText(prompt)          // fills the RHS pane
}
```

---

## 4. Why only two calls?

* **Call #1** handles *all* MIME logic (Gemini Part URIs → text) **and** summarisation.
* **Call #2** only merges JSON + form fields → final prompt.
* Both stay stateless—no chat history needed—so you can keep them as plain REST endpoints or Cloud Functions and upgrade later without breaking the contract.

Ship this, and your “Personal Knowledge Assistant” MVP will already feel magical. 🚀
