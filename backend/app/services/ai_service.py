import google.generativeai as genai
import os
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    print("Warning: No API key found for Gemini. Set GEMINI_API_KEY or GOOGLE_API_KEY")

# Try multiple model names to find one that works
model = None
if api_key:
    model_names = [
        'models/gemini-2.5-flash',      # Latest and fastest
        'models/gemini-2.0-flash',      # Stable alternative 
        'models/gemini-2.5-pro',        # Pro version
        'models/gemini-2.0-flash-001',  # Specific version
        'gemini-2.5-flash',             # Without models/ prefix
        'gemini-2.0-flash',             # Fallback
        'gemini-1.5-flash',             # Older version
        'gemini-pro'                    # Legacy
    ]
    
    for model_name in model_names:
        try:
            model = genai.GenerativeModel(model_name)
            print(f"✅ Using Gemini model: {model_name}")
            break
        except Exception as e:
            print(f"❌ Model {model_name} failed: {str(e)[:50]}...")
            continue
    
    if model is None:
        print("❌ No working Gemini model found. AI features will use fallbacks.")

class AIService:
    @staticmethod
    async def generate_document_outline(topic: str, document_type: str, num_sections: int = 5) -> List[str]:
        """Generate document outline using AI"""
        if document_type == "docx":
            prompt = f"""
            Create a professional outline for a Word document about "{topic}".
            Generate exactly {num_sections} section titles that would make sense for a comprehensive document on this topic.
            
            Requirements:
            - Each section should be a clear, descriptive title
            - Sections should flow logically from introduction to conclusion
            - Use professional business language
            - Return only the section titles, one per line
            - Do not include numbers or bullets
            
            Topic: {topic}
            """
        else:  # pptx
            prompt = f"""
            Create a professional outline for a PowerPoint presentation about "{topic}".
            Generate exactly {num_sections} slide titles that would make sense for a comprehensive presentation on this topic.
            
            Requirements:
            - Each slide should have a clear, engaging title
            - Slides should flow logically from introduction to conclusion
            - Use professional business language
            - Return only the slide titles, one per line
            - Do not include numbers or bullets
            
            Topic: {topic}
            """
        
        try:
            if model is None:
                raise Exception("AI model not available")
            response = model.generate_content(prompt)
            titles = [title.strip() for title in response.text.strip().split('\n') if title.strip()]
            return titles[:num_sections]  # Ensure we return exactly the requested number
        except Exception as e:
            print(f"Error generating outline: {e}")
            # Return default outline if AI fails
            if document_type == "docx":
                return [
                    f"Introduction to {topic}",
                    f"Background and Context",
                    f"Key Components of {topic}",
                    f"Implementation Strategies",
                    f"Conclusion and Future Outlook"
                ]
            else:
                return [
                    f"Introduction to {topic}",
                    f"Overview and Objectives",
                    f"Main Components",
                    f"Benefits and Applications",
                    f"Conclusion and Next Steps"
                ]
    
    @staticmethod
    async def generate_section_content(
        section_title: str, 
        topic: str, 
        context: Optional[str] = None,
        word_count: int = 250
    ) -> str:
        """Generate content for a Word document section"""
        context_prompt = f"\n\nContext from previous sections:\n{context}" if context else ""
        
        prompt = f"""
        Write professional content for a section titled "{section_title}" in a document about "{topic}".
        {context_prompt}
        
        Requirements:
        - Write approximately {word_count} words
        - Use professional, clear business language
        - Include specific details and actionable insights
        - Structure content with proper flow and transitions
        - Ensure content is informative and valuable
        - Do not include the section title in the response
        
        Section Title: {section_title}
        Main Topic: {topic}
        """
        
        try:
            if model is None:
                raise Exception("AI model not available")
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error generating section content: {e}")
            return f"This section will cover important aspects of {section_title} related to {topic}. Please refine this content to get detailed information."
    
    @staticmethod
    async def generate_slide_content(
        slide_title: str, 
        topic: str, 
        context: Optional[str] = None,
        num_bullets: int = 4
    ) -> List[str]:
        """Generate bullet points for a PowerPoint slide"""
        context_prompt = f"\n\nContext from previous slides:\n{context}" if context else ""
        
        prompt = f"""
        Create bullet points for a PowerPoint slide titled "{slide_title}" in a presentation about "{topic}".
        {context_prompt}
        
        Requirements:
        - Generate exactly {num_bullets} bullet points
        - Each bullet should be concise but informative (1-2 lines max)
        - Use professional presentation language
        - Make points actionable and specific
        - Ensure bullets are relevant to both the slide title and main topic
        - Return only the bullet point text, one per line
        - Do not include bullet symbols or numbers
        
        Slide Title: {slide_title}
        Main Topic: {topic}
        """
        
        try:
            if model is None:
                raise Exception("AI model not available")
            response = model.generate_content(prompt)
            bullets = [bullet.strip() for bullet in response.text.strip().split('\n') if bullet.strip()]
            return bullets[:num_bullets]  # Ensure we return exactly the requested number
        except Exception as e:
            print(f"Error generating slide content: {e}")
            return [
                f"Key aspect of {slide_title}",
                f"Important consideration for {topic}",
                f"Strategic approach to implementation",
                f"Expected outcomes and benefits"
            ]
    
    @staticmethod
    async def refine_content(
        current_content: str, 
        refinement_prompt: str, 
        content_type: str = "section"
    ) -> str:
        """Refine existing content based on user prompt"""
        if content_type == "slide":
            prompt = f"""
            Refine the following slide bullet points based on this instruction: "{refinement_prompt}"
            
            Current content:
            {current_content}
            
            Requirements:
            - Apply the requested changes while maintaining professional quality
            - Keep the same format (bullet points for slides)
            - Ensure content remains relevant and valuable
            - Maintain appropriate length for presentation slides
            
            Instruction: {refinement_prompt}
            """
        else:  # section
            prompt = f"""
            Refine the following section content based on this instruction: "{refinement_prompt}"
            
            Current content:
            {current_content}
            
            Requirements:
            - Apply the requested changes while maintaining professional quality
            - Keep content well-structured and informative
            - Ensure appropriate length and depth
            - Maintain professional business language
            
            Instruction: {refinement_prompt}
            """
        
        try:
            if model is None:
                raise Exception("AI model not available")
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error refining content: {e}")
            return current_content  # Return original content if refinement fails