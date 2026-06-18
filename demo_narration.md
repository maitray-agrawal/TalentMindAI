# TalentMind AI Hack2Skill Demo Narration Script

This voiceover script is synchronized with the automated browser actions in the demo video. Speak clearly, confidently, and maintain a professional pacing. The target duration is approximately **4 minutes and 30 seconds**.

---

## Part 1: Introduction, Architecture, and Ingestion Scale (0:00 - 0:45)

**[Visual: Code Repository structure showing directories, opening docs/architecture.md and docs/dataset_scale_validation.md]**

"Hello judges. Welcome to TalentMind AI—our entry for the Hack2Skill challenge. TalentMind AI is an advanced candidate discovery, parsing, and ranking platform built to solve the core limitations of traditional recruitment systems: keyword stuffing, high false-negatives, and opaque ranking logic.

Our architecture is fully decoupled, using FastAPI for high-throughput ASGI services and SQLite via SQLAlchemy for data persistence. We built the platform from a clean slate to handle the challenge dataset, successfully importing and validating **100,001 candidates** as shown in our scale validation documentation. We achieve sub-second query times over this large dataset through database-level indexing and optimized query execution, moving away from slow in-memory filtering."

---

## Part 2: The Command Center (0:45 - 1:30)

**[Visual: Opens dashboard.html. Highlights the 100,001 candidate metric, green API Online status, and shows the Job Description Intelligence upload area]**

"Let’s transition to the TalentMind AI Command Center. 

At the top, you can see our live system metrics, including the total database size of one hundred thousand and one candidates, completely ingested and verified. The dashboard is backed by our specialized `/api/candidates/stats` endpoint, making it highly responsive.

Down below, we have the Job Description Intelligence widget. Rather than relying on simple text boxes, recruiters can upload unstructured job description files—such as the challenge's `.docx` file. The backend automatically parses the text, extracts hard skill requirements, experience thresholds, and explicit disqualifiers, creating a structured job profile in our database."

---

## Part 3: Search & Discovery at Scale (1:30 - 2:00)

**[Visual: Sidebar click to candidate_search.html. Enters React.js, selects Remote, and >5 years experience. Clicks search and results populate instantly]**

"Next, let’s explore candidate search.

Traditional database lookups struggle when processing nested career histories for 100,000 candidates. Our search interface is powered by our optimized `/api/candidates/search` API. 

Let's search for candidates with React.js, requesting over five years of experience, and remote availability. When we click search, the results return in milliseconds. The search engine doesn't just scan tags; it parses nested arrays of candidate career histories, checking past titles, durations, and role descriptions."

---

## Part 4: Multi-Variate Ranking Engine (2:00 - 2:45)

**[Visual: Sidebar click to candidate_ranking.html. Selects 'AI/Search Engineer' job from the dropdown, clicks 'Generate Rankings', and watches the progress bar populate the table]**

"Now, let’s trigger our core innovation: the multi-variate Ranker Engine.

We will select our AI and Search Engineer job opening and click 'Generate Rankings'. Our ranking engine evaluates candidates against six distinct pillars: Skills at 30%, Experience at 20%, Semantic Overlap via TF-IDF cosine similarity at 15%, Education at 15%, Behavioral Signals from the platform at 10%, and Location Compatibility at 10%.

If we hover over the Fit Scores, the engine reveals a breakdown of why each candidate scored what they did, including role fit multipliers and explicit disqualifier penalties—such as consulting-only history, title-chasing tenures under fifteen months, and AI wrapper-only penalization. This provides recruiters with true Explainable AI."

---

## Part 5: Groq AI Recruiter Reranking & XAI (2:45 - 3:30)

**[Visual: Clicks 'Trigger Groq Reranking' on candidate_ranking.html, watches table update. Clicks 'View Profile' on the top candidate to open candidate_details.html]**

"To refine our results, we introduce Groq AI Recruiter Reranking.

By calling our Groq LLM integration, we evaluate the qualitative aspects of candidate resumes against the job description. The reranker runs asynchronously with rate-limit backoffs. The top candidates are adjusted based on nuanced project matching and labeled with the Groq Badge.

Clicking on the top candidate brings us to the Candidate Details screen. Here, the recruiter sees the Skills Spectrum radar chart, and the AI Insights panel powered by our obsidian intelligence engine. It details Key Strengths, Potential Risks like retention and counter-offer probability, and actionable hiring recommendations."

---

## Part 6: Candidate Comparison and Upskilling (3:30 - 4:00)

**[Visual: Sidebar click to candidate_comparison.html showing side-by-side comparison, then sidebar click to skill_gap_analysis.html showing upskilling roadmaps]**

"When deciding between top talent, recruiters can utilize our side-by-side Candidate Comparison matrix to visualize relative strengths, behavioral signals, and experience curves.

For candidates who fall slightly short of the requirements, the platform automatically generates a Skill Gap Analysis and Copilot Roadmap. This details missing competencies and prescribes targeted courses and project guidelines, turning rejection emails into upskilling opportunities."

---

## Part 7: Recruiter Copilot and Final Submission (4:00 - 4:30)

**[Visual: Sidebar click to recruiter_copilot.html, drafts outreach message, then shifts to Swagger UI /docs, and shows validation output]**

"Finally, we navigate to the Recruiter Copilot. The AI Copilot allows us to draft professional, personalized outreach emails instantly, referencing specific aspects of the candidate’s profile—such as their recent blog post on micro-frontends.

Behind the scenes, our FastAPI endpoints are fully documented and conform strictly to API standards. Triggering the final submission generation compiles our rankings into a validated `submission.csv` file, passing all Hack2Skill schemas.

TalentMind AI combines raw data scale, multi-variate intelligence, explainability, and generative AI to deliver a competition-grade recruitment platform. Thank you for your time!"
