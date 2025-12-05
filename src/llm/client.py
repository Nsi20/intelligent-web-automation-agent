"""LLM client abstraction for Groq and OpenAI."""
from typing import Optional, Dict, Any
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from config.settings import settings
from src.utils.logger import logger


class LLMClient:
    """Unified LLM client supporting Groq and OpenAI."""
    
    def __init__(self, model: str = "llama-3.3-70b-versatile", temperature: float = 0.1):
        """Initialize LLM client.
        
        Args:
            model: Model name (Groq models: llama-3.3-70b-versatile, llama-3.1-8b-instant, mixtral-8x7b-32768)
            temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative)
        """
        self.model = model
        self.temperature = temperature
        
        # Initialize Groq client
        self.llm = ChatGroq(
            api_key=settings.groq_api_key,
            model_name=model,
            temperature=temperature,
        )
        logger.info(f"LLM client initialized: {model} (temp={temperature})")
        
    def chat(self, 
             prompt: str, 
             system_message: Optional[str] = None,
             **kwargs) -> str:
        """Send chat message and get response.
        
        Args:
            prompt: User prompt
            system_message: Optional system message for context
            **kwargs: Additional parameters
            
        Returns:
            LLM response text
        """
        messages = []
        
        if system_message:
            messages.append(SystemMessage(content=system_message))
            
        messages.append(HumanMessage(content=prompt))
        
        logger.debug(f"Sending prompt to LLM (length={len(prompt)} chars)")
        response = self.llm.invoke(messages)
        
        result = response.content
        logger.debug(f"LLM response received (length={len(result)} chars)")
        
        return result
        
    async def achat(self,
                    prompt: str,
                    system_message: Optional[str] = None,
                    **kwargs) -> str:
        """Async version of chat.
        
        Args:
            prompt: User prompt
            system_message: Optional system message
            **kwargs: Additional parameters
            
        Returns:
            LLM response text
        """
        messages = []
        
        if system_message:
            messages.append(SystemMessage(content=system_message))
            
        messages.append(HumanMessage(content=prompt))
        
        logger.debug(f"Sending async prompt to LLM (length={len(prompt)} chars)")
        response = await self.llm.ainvoke(messages)
        
        result = response.content
        logger.debug(f"LLM response received (length={len(result)} chars)")
        
        return result
        
    def extract_structured_data(self, 
                               html_content: str, 
                               schema_description: str) -> str:
        """Extract structured data from HTML using LLM.
        
        Args:
            html_content: HTML content to parse
            schema_description: Description of desired output structure
            
        Returns:
            Extracted data as formatted string
        """
        system_msg = """You are a data extraction expert. Extract structured information 
from HTML content according to the given schema. Return clean, well-formatted data."""
        
        prompt = f"""Extract the following information from this HTML:

{schema_description}

HTML Content:
{html_content[:8000]}  # Limit to avoid token limits

Return the extracted data in a clear, structured format."""

        return self.chat(prompt, system_message=system_msg)
        
    def make_decision(self, 
                     context: str, 
                     question: str,
                     options: Optional[list[str]] = None) -> str:
        """Use LLM to make a decision based on context.
        
        Args:
            context: Contextual information
            question: Decision question
            options: Optional list of choices
            
        Returns:
            LLM decision/recommendation
        """
        system_msg = """You are an intelligent decision-making assistant. 
Analyze the context carefully and provide clear, actionable recommendations."""
        
        prompt = f"""Context:
{context}

Question: {question}"""

        if options:
            prompt += f"\n\nOptions:\n" + "\n".join(f"- {opt}" for opt in options)
            
        prompt += "\n\nProvide your decision and brief reasoning."
        
        return self.chat(prompt, system_message=system_msg)
        
    def filter_relevance(self, 
                        items: list[str], 
                        criteria: str,
                        max_items: int = 10) -> list[str]:
        """Filter items by relevance using LLM.
        
        Args:
            items: List of items to filter
            criteria: Filtering criteria
            max_items: Maximum items to return
            
        Returns:
            Filtered list of relevant items
        """
        system_msg = """You are a content filtering expert. Analyze items and return 
only those that match the criteria. Be selective and prioritize quality."""
        
        items_text = "\n".join(f"{i+1}. {item}" for i, item in enumerate(items))
        
        prompt = f"""Filter these items based on the criteria and return the most relevant ones.

Criteria: {criteria}

Items:
{items_text}

Return ONLY the numbers of relevant items (e.g., "1, 3, 7"), up to {max_items} items."""

        response = self.chat(prompt, system_message=system_msg)
        
        # Parse response to get item indices
        try:
            indices = [int(x.strip()) - 1 for x in response.split(",") if x.strip().isdigit()]
            return [items[i] for i in indices if 0 <= i < len(items)]
        except:
            logger.warning("Failed to parse LLM filter response, returning original items")
            return items[:max_items]
