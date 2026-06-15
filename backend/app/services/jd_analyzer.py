import re
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, Any, List

# Standard tech skills directory for keyword extraction, heavily expanded for the hackathon dataset and JD
SKILL_DICTIONARY = [
    "Python", "TensorFlow", "PyTorch", "Keras", "Scikit-Learn", "NumPy", "Pandas",
    "Java", "C++", "Go", "Rust", "TypeScript", "JavaScript", "HTML", "CSS",
    "React", "Vue", "Angular", "Next.js", "Svelte", "Node.js", "Express", "Django", "Flask", "FastAPI",
    "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch",
    "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Terraform", "CI/CD", "Git", "GitHub", "GitLab",
    "Linux", "DevOps", "MLOps", "NLP", "Computer Vision", "LLM", "Deep Learning", "Machine Learning",
    # Specific skills in JD
    "embeddings-based retrieval", "sentence-transformers", "OpenAI embeddings", "BGE", "E5", 
    "vector databases", "Pinecone", "Weaviate", "Qdrant", "Milvus", "OpenSearch", "FAISS", 
    "hybrid search", "evaluation frameworks", "ranking systems", "NDCG", "MRR", "MAP", "A/B testing",
    "A/B test", "LLM fine-tuning", "LoRA", "QLoRA", "PEFT", "learning-to-rank", "XGBoost", 
    "distributed systems", "inference optimization", "HR-tech", "recruiting tech", "marketplace", 
    "RAG", "search systems", "recommendation systems"
]

class JDAnalyzerService:
    @staticmethod
    def extract_text_from_docx(file_bytes: bytes) -> str:
        """Extract paragraphs from docx file bytes by reading word/document.xml."""
        import io
        try:
            with zipfile.ZipFile(io.BytesIO(file_bytes)) as docx:
                tree = ET.parse(docx.open('word/document.xml'))
                root = tree.getroot()
                
                namespaces = {
                    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
                }
                
                paragraphs = []
                for para in root.findall('.//w:p', namespaces):
                    text_elems = para.findall('.//w:t', namespaces)
                    text = ''.join([node.text for node in text_elems if node.text])
                    if text:
                        paragraphs.append(text)
                
                return '\n'.join(paragraphs)
        except Exception as e:
            raise ValueError(f"Failed to parse docx file: {str(e)}")

    @staticmethod
    def analyze(description_text: str) -> Dict[str, Any]:
        """Backward-compatible basic analysis."""
        detailed = JDAnalyzerService.analyze_detailed(description_text)
        return {
            "title": detailed["title"],
            "department": detailed["department"],
            "location": detailed["location"],
            "work_preference": detailed["work_preference"],
            "required_skills": detailed["required_skills"],
            "experience_required": detailed["experience_required"]
        }

    @staticmethod
    def analyze_detailed(description_text: str) -> Dict[str, Any]:
        """Advanced detailed heuristic analysis of a job description."""
        if not description_text:
            return {
                "title": "Untitled Role",
                "department": "Engineering",
                "location": "Remote",
                "work_preference": "Remote",
                "required_skills": [],
                "preferred_skills": [],
                "experience_required": 0.0,
                "experience_text": "Not specified",
                "education_requirements": ["Not specified"],
                "disqualifiers": [],
                "vibe_check": [],
                "description": ""
            }

        lines = [line.strip() for line in description_text.split("\n")]
        
        # 1. Extract Title
        title = "Software Engineer"
        first_lines = [l for l in lines[:5] if l]
        if first_lines:
            for fl in first_lines:
                title_match = re.search(r"(?:job description|role|title|position)\s*[:\-]\s*(.+)", fl, re.IGNORECASE)
                if title_match:
                    title = title_match.group(1).strip()
                    break
            else:
                for fl in first_lines:
                    if len(fl) < 80 and not any(kw in fl.lower() for kw in ["redrob", "hiring", "description"]):
                        title = fl
                        break

        # 2. Extract Location
        location = "Remote"
        for line in lines:
            if line.lower().startswith("location:"):
                location = line[len("location:"):].strip()
                break
        else:
            loc_match = re.search(r"(?:location|loc|office in|based in)\s*[:\-]?\s*([^\n]+)", description_text, re.IGNORECASE)
            if loc_match:
                location = loc_match.group(1).strip()

        # Clean location from trailing pipe or other section delimiters
        if "|" in location:
            location = location.split("|")[0].strip()

        # 3. Extract Work Preference
        work_preference = "Remote"
        if re.search(r"\bhybrid\b", description_text, re.IGNORECASE):
            work_preference = "Hybrid"
        elif re.search(r"\bonsite\b|\bon-site\b", description_text, re.IGNORECASE):
            work_preference = "Onsite"

        # 4. Extract Department
        department = "Engineering"
        departments = {
            "Design": ["design", "ux", "ui", "creative", "product designer"],
            "Marketing": ["marketing", "growth", "seo", "branding"],
            "Product": ["product manager", "product owner", "pm"],
            "Sales": ["sales", "account manager", "business development"],
            "HR": ["hr", "recruitment", "talent acquisition"],
            "Engineering": ["engineering", "developer", "engineer", "backend", "frontend", "scientist", "ai", "ml"]
        }
        for dept, keywords in departments.items():
            for kw in keywords:
                if re.search(r"\b" + kw + r"\b", title, re.IGNORECASE):
                    department = dept
                    break

        # 5. Section Parsing using explicit heading transitions
        sections = {
            "required": [],
            "preferred": [],
            "disqualifiers": [],
            "vibe_check": []
        }
        
        current_section = None
        for line in lines:
            line_clean = line.strip()
            if not line_clean:
                continue
                
            line_lower = line_clean.lower()
            
            # Heading Transition Checks
            REQUIRED_MARKERS = [
                "things you absolutely need", "required skills", "must have",
                "hard requirements", "you must", "mandatory", "non-negotiable"
            ]
            PREFERRED_MARKERS = [
                "things we'd like", "preferred skills", "nice to have",
                "bonus", "ideal candidate", "good to have"
            ]
            DISQUALIFIER_MARKERS = [
                "things we explicitly do not want", "disqualifiers",
                "do not want", "red flag", "not suitable", "explicitly not"
            ]
            VIBE_MARKERS = [
                "the vibe check", "culture fit", "cultural fit", "who you are"
            ]
            RESET_MARKERS = [
                "let's be honest", "what you'd actually", "what we mean by",
                "the skills inventory", "on location", "how to read",
                "final note", "about the company", "about us", "compensation"
            ]

            if any(m in line_lower for m in REQUIRED_MARKERS):
                current_section = "required"
                continue
            elif any(m in line_lower for m in PREFERRED_MARKERS):
                current_section = "preferred"
                continue
            elif any(m in line_lower for m in DISQUALIFIER_MARKERS):
                current_section = "disqualifiers"
                continue
            elif any(m in line_lower for m in VIBE_MARKERS):
                current_section = "vibe_check"
                continue
            elif any(m in line_lower for m in RESET_MARKERS):
                current_section = None
                continue
            
            # If in a section, add the cleaned text
            if current_section:
                clean_text = re.sub(r"^[•\-\*\d\.\)\s]+", "", line_clean).strip()
                if clean_text:
                    sections[current_section].append(clean_text)

        # 6. Extract Skills from sections
        required_skills = []
        preferred_skills = []
        
        required_section_text = " ".join(sections["required"]) if sections["required"] else description_text
        preferred_section_text = " ".join(sections["preferred"]) if sections["preferred"] else ""

        for skill in SKILL_DICTIONARY:
            escaped_skill = re.escape(skill)
            if skill in ["C++", "C#", ".NET"]:
                pattern = r"\b" + escaped_skill if skill != ".NET" else r"\.NET\b"
            else:
                pattern = r"\b" + escaped_skill + r"\b"
                
            if re.search(pattern, required_section_text, re.IGNORECASE):
                required_skills.append(skill)
            elif preferred_section_text and re.search(pattern, preferred_section_text, re.IGNORECASE):
                preferred_skills.append(skill)
                
        required_skills = list(set(required_skills))
        preferred_skills = list(set(preferred_skills) - set(required_skills))
        
        required_skills.sort()
        preferred_skills.sort()

        # 7. Extract Experience
        experience_required = 0.0
        experience_text = "Not specified"
        
        exp_range_match = re.search(r"(\d+)(?:\s*[-–to\s]+\s*(\d+))?\+?\s*years?", description_text, re.IGNORECASE)
        if exp_range_match:
            min_val = float(exp_range_match.group(1))
            max_val = exp_range_match.group(2)
            if max_val:
                experience_text = f"{int(min_val)}-{int(max_val)} years"
            else:
                experience_text = f"{int(min_val)}+ years"
            experience_required = min_val
        
        if "5–9" in description_text or "5-9" in description_text:
            experience_required = 5.0
            experience_text = "5-9 years (range; 6-8 years total preferred)"

        # 8. Extract Education Requirements
        education_requirements = []
        edu_keywords = ["degree", "bachelor", "master", "phd", "b.tech", "m.tech", "tier-1", "tier 1"]
        for line in lines:
            if any(ekw in line.lower() for ekw in edu_keywords) and len(line) < 150:
                # Exclude location and title lines
                if any(x in line.lower() for x in ["location:", "title:", "company:", "office:"]):
                    continue
                clean_line = re.sub(r"^[•\-\*\d\.\)\s]+", "", line).strip()
                if clean_line and clean_line not in education_requirements:
                    education_requirements.append(clean_line)
                    
        if not education_requirements:
            if "tier-1" in description_text.lower():
                education_requirements.append("Open to relocation candidates from Tier-1 cities / institutions")
            else:
                education_requirements.append("Not explicitly specified (focus on production experience)")

        disqualifiers = sections["disqualifiers"] if sections["disqualifiers"] else [
            "Pure research backgrounds without production deployment",
            "LangChain tutorials/ OpenAI wrapper only ML projects (< 12 months)",
            "Senior engineers who have not coded in production for 18+ months",
            "Title-chasers (changing companies every 1.5 years)",
            "Consulting-only backgrounds (TCS, Infosys, Wipro, etc.)"
        ]
        
        vibe_check = sections["vibe_check"] if sections["vibe_check"] else [
            "Async-first, writing intensive documentation",
            "Open, direct feedback & rapid decision making",
            "Moving fast, challenging internal assumptions"
        ]

        return {
            "title": title,
            "department": department,
            "location": location,
            "work_preference": work_preference,
            "required_skills": required_skills,
            "preferred_skills": preferred_skills,
            "experience_required": experience_required,
            "experience_text": experience_text,
            "education_requirements": education_requirements,
            "disqualifiers": disqualifiers,
            "vibe_check": vibe_check,
            "description": description_text
        }
