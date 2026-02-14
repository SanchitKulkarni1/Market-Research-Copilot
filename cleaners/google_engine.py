import json
from typing import Dict, Any, List, Optional


MAX_ORGANIC = 5
MAX_RELATED_QUESTIONS = 5


def clean_serpapi_google_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract only the essential content for LLM summarization:
    - From organic_results: title + snippet
    - From related_questions: question + snippet
    """
    cleaned = {}

    # --------------------------------
    # Content for LLM (Combined List)
    # --------------------------------
    llm_content = []

    # Add organic results (title + snippet)
    organic_results = data.get("organic_results", [])[:MAX_ORGANIC]
    for result in organic_results:
        title = result.get("title")
        snippet = result.get("snippet")
        
        if title or snippet:  # Include if at least one is present
            item = {}
            
            if title:
                item["title"] = title
            if snippet:
                item["snippet"] = snippet
            
            llm_content.append(item)

    # Add related questions (question + snippet)
    related_questions = data.get("related_questions", [])[:MAX_RELATED_QUESTIONS]
    for q in related_questions:
        question_text = q.get("question")
        snippet = q.get("snippet")
        
        if not snippet:
            snippet = extract_ai_snippet(q)
        
        if question_text:  # Include if question exists
            item = {"question": question_text}
            
            if snippet:
                item["snippet"] = snippet
            
            llm_content.append(item)

    if llm_content:
        cleaned["content"] = llm_content

    return cleaned


def extract_ai_snippet(question_obj: Dict[str, Any]) -> Optional[str]:
    """Extract snippet from AI-generated text blocks within a question."""
    text_blocks = question_obj.get("text_blocks", [])
    snippets = []

    for block in text_blocks:
        block_type = block.get("type")
        
        if block_type == "paragraph":
            snippet = block.get("snippet")
            if snippet:
                snippets.append(snippet)
        elif block_type == "list":
            for item in block.get("list", []):
                snippet = item.get("snippet")
                if snippet:
                    snippets.append(snippet)

    return " ".join(snippets) if snippets else None


def prepare_llm_prompt(cleaned_data: Dict[str, Any]) -> str:
    """
    Convert cleaned data into a formatted prompt for LLM summarization.
    """
    content = cleaned_data.get("content", [])
    
    if not content:
        return "No content available for summarization."
    
    prompt_parts = []
    
    for idx, item in enumerate(content, 1):
        if "title" in item:
            # Organic result with title
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            
            prompt_parts.append(f"{idx}. {title}")
            if snippet:
                prompt_parts.append(f"   {snippet}")
        
        elif "question" in item:
            # Related question
            question = item.get("question", "")
            snippet = item.get("snippet", "")
            
            prompt_parts.append(f"{idx}. Q: {question}")
            if snippet:
                prompt_parts.append(f"   A: {snippet}")
        
        prompt_parts.append("")  # Empty line between items
    
    return "\n".join(prompt_parts)
