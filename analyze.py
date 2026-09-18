from google import genai
from google.genai import types
from dotenv import load_dotenv
from PIL import Image
import chromadb
import os
import json
import time

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="ux_guidelines")

response_schema = {
    "type": "object",
    "properties": {
        "issues": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "heuristic_violated": {"type": "string"},
                    "explanation": {"type": "string"},
                    "severity": {"type": "string", "enum": ["low", "medium", "high"]},
                    "location_in_image": {"type": "string"},
                    "suggested_fix": {"type": "string"}
                },
                "required": ["heuristic_violated", "explanation", "severity", "location_in_image", "suggested_fix"]
            }
        }
    },
    "required": ["issues"]
}


def retrieve_relevant_guidelines(query, top_k=5):
    query_embedding_response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=query
    )
    query_embedding = query_embedding_response.embeddings[0].values

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return results["documents"][0]


def analyze_screenshot(image_path):
    image = Image.open(image_path)

    retrieval_query = "usability heuristics, accessibility, contrast, spacing, visual hierarchy issues in UI design"
    guidelines = retrieve_relevant_guidelines(retrieval_query)
    guidelines_text = "\n\n".join(guidelines)

    prompt = (
        "You are a senior UX reviewer. Use the following UX guidelines as your "
        "reference standard:\n\n"
        f"{guidelines_text}\n\n"
        "Now analyze this UI screenshot and identify 3-5 specific usability issues. "
        "Follow these rules strictly:\n\n"
        "1. For 'heuristic_violated', give a SHORT rule name only (e.g. 'WCAG text "
        "contrast', 'WCAG non-text contrast', 'Nielsen: Aesthetic and minimalist "
        "design'). Do not paste the full guideline sentence here.\n\n"
        "2. For 'explanation', write ONE sentence in your own words about why THIS "
        "specific element is a problem in THIS specific image. Never reuse the same "
        "explanation wording across different issues, even if they relate to the same "
        "rule — each explanation must reflect that element's actual context (its size, "
        "role, position, and how prominent or secondary it is).\n\n"
        "3. Apply contrast rules correctly: if the element is text, judge it against the "
        "text contrast standard (4.5:1 normal text, 3:1 large text). If the element is a "
        "non-text UI component, icon, or border with no text inside it, judge it against "
        "the 3:1 non-text standard instead. If an element contains both (like a badge with "
        "a number inside it), evaluate the text and the container separately and say so.\n\n"
        "4. Calibrate severity using a two-step process:\n\n"
        "   Step A - classify the element's role in the interface:\n"
        "   - primary: main navigation, primary call-to-action, core headline/body "
        "content the user needs to complete their main task on this screen\n"
        "   - secondary: supporting content the user benefits from but doesn't strictly "
        "need (body paragraphs, descriptions, secondary buttons)\n"
        "   - tertiary: decorative or supplementary elements (eyebrow labels, small "
        "badges, icons, captions, metadata, footer text)\n\n"
        "   Step B - assign severity based on that role:\n"
        "   - high: the issue affects a 'primary' element\n"
        "   - medium: the issue affects a 'secondary' element\n"
        "   - low: the issue affects a 'tertiary' element\n\n"
        "   Apply this consistently across all issues in this response - do not let the "
        "type of guideline violated (e.g. contrast vs. spacing) influence severity, only "
        "the role of the element it affects.\n\n"
        "5. For 'location_in_image', name the exact element, not a vague region.\n\n"
        "For each issue, also suggest a concrete fix."
    )

    last_error = None
    for attempt in range(4):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=[prompt, image],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=response_schema
                )
            )
            return json.loads(response.text)
        except Exception as e:
            last_error = e
            wait_time = 3 * (attempt + 1)  # 3s, 6s, 9s, 12s
            print(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
            time.sleep(wait_time)

    raise last_error


if __name__ == "__main__":
    feedback = analyze_screenshot("test_screenshot.png")
    print(json.dumps(feedback, indent=2))