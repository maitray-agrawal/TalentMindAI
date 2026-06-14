import sys
import os
import io
import zipfile
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

# Add backend to python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.main import app
from app.services.jd_analyzer import JDAnalyzerService

class JDIntelligenceTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def create_mock_docx(self, text: str) -> bytes:
        """Helper to create minimal valid .docx bytes in memory."""
        out = io.BytesIO()
        with zipfile.ZipFile(out, 'w') as zip_file:
            xml_content = f"""<?xml version="1.0" encoding="utf-8" standalone="yes"?>
            <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
                <w:body>
                    <w:p>
                        <w:t>{text}</w:t>
                    </w:p>
                </w:body>
            </w:document>
            """
            zip_file.writestr("word/document.xml", xml_content)
        return out.getvalue()

    # --- Unit Tests ---
    
    def test_docx_text_extraction(self):
        sample_text = "This is a mock job description text."
        docx_bytes = self.create_mock_docx(sample_text)
        extracted = JDAnalyzerService.extract_text_from_docx(docx_bytes)
        self.assertEqual(extracted.strip(), sample_text)

    def test_docx_text_extraction_invalid(self):
        with self.assertRaises(ValueError):
            JDAnalyzerService.extract_text_from_docx(b"corrupted zip file header...")

    def test_analyze_detailed_basic(self):
        desc = "Senior AI Engineer\nLocation: Pune, India\nWork preference: Hybrid\nRequirements: Python, PyTorch, Weaviate\n5+ years experience"
        res = JDAnalyzerService.analyze_detailed(desc)
        self.assertEqual(res["title"], "Senior AI Engineer")
        self.assertEqual(res["location"], "Pune, India")
        self.assertEqual(res["work_preference"], "Hybrid")
        self.assertIn("Python", res["required_skills"])
        self.assertIn("PyTorch", res["required_skills"])
        self.assertIn("Weaviate", res["required_skills"])
        self.assertEqual(res["experience_required"], 5.0)

    def test_analyze_detailed_empty(self):
        res = JDAnalyzerService.analyze_detailed("")
        self.assertEqual(res["title"], "Untitled Role")
        self.assertEqual(res["required_skills"], [])
        self.assertEqual(res["experience_required"], 0.0)

    def test_analyze_detailed_sections(self):
        desc = """
        Job Description: founding Senior AI Engineer
        Company: Redrob AI
        Location: Noida | India
        
        Things you absolutely need:
        * Python and deep learning frameworks.
        * embeddings-based retrieval systems.
        * experience with vector databases (Qdrant, Milvus).
        
        Things we'd like you to have:
        * LLM fine-tuning and LoRA expertise.
        * Experience in recruiting tech or HR-tech.
        
        Things we explicitly do not want:
        * Pure academic research with no production shipping.
        * Consulting-only backgrounds.
        
        The vibe check:
        * Async-first and fast-moving.
        """
        res = JDAnalyzerService.analyze_detailed(desc)
        self.assertEqual(res["title"], "founding Senior AI Engineer")
        self.assertEqual(res["location"], "Noida")
        self.assertEqual(res["work_preference"], "Remote")  # Default if no hybrid/onsite in text
        self.assertIn("Python", res["required_skills"])
        self.assertIn("embeddings-based retrieval", res["required_skills"])
        self.assertIn("Qdrant", res["required_skills"])
        self.assertIn("Milvus", res["required_skills"])
        self.assertIn("LLM fine-tuning", res["preferred_skills"])
        self.assertIn("LoRA", res["preferred_skills"])
        self.assertIn("HR-tech", res["preferred_skills"])
        
        # Verify custom section text extraction
        self.assertEqual(len(res["disqualifiers"]), 2)
        self.assertIn("Pure academic research with no production shipping.", res["disqualifiers"])
        self.assertIn("Async-first and fast-moving.", res["vibe_check"])

    # --- API Tests ---

    def test_api_analyze_txt(self):
        desc = "Senior Developer\nLocation: Remote\nRequirements: React, TypeScript, Node.js\n4 years experience"
        response = self.client.post(
            "/api/jobs/analyze",
            files={"file": ("job.txt", io.BytesIO(desc.encode("utf-8")), "text/plain")}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["title"], "Senior Developer")
        self.assertEqual(data["location"], "Remote")
        self.assertIn("React", data["required_skills"])
        self.assertIn("TypeScript", data["required_skills"])
        self.assertEqual(data["experience_required"], 4.0)

    def test_api_analyze_docx(self):
        desc = "Lead Backend Engineer\nLocation: Noida\nRequirements: Python, FastAPI, Docker\n6+ years experience"
        docx_bytes = self.create_mock_docx(desc)
        response = self.client.post(
            "/api/jobs/analyze",
            files={"file": ("job.docx", io.BytesIO(docx_bytes), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["title"], "Lead Backend Engineer")
        self.assertEqual(data["location"], "Noida")
        self.assertIn("FastAPI", data["required_skills"])
        self.assertEqual(data["experience_required"], 6.0)

    def test_api_analyze_empty_file(self):
        response = self.client.post(
            "/api/jobs/analyze",
            files={"file": ("job.txt", io.BytesIO(b""), "text/plain")}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("The uploaded file is empty.", response.json()["detail"])

    def test_api_analyze_whitespace_only(self):
        response = self.client.post(
            "/api/jobs/analyze",
            files={"file": ("job.txt", io.BytesIO(b"   \n  \t  "), "text/plain")}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("The uploaded file contains no text content.", response.json()["detail"])

    def test_api_analyze_corrupt_docx(self):
        response = self.client.post(
            "/api/jobs/analyze",
            files={"file": ("job.docx", io.BytesIO(b"corrupt header"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Failed to read docx file", response.json()["detail"])

    def test_api_analyze_unsupported_format(self):
        response = self.client.post(
            "/api/jobs/analyze",
            files={"file": ("job.pdf", io.BytesIO(b"fake pdf content"), "application/pdf")}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Unsupported file format", response.json()["detail"])

if __name__ == "__main__":
    unittest.main()
