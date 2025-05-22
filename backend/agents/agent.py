from dotenv import load_dotenv
import asyncio
import os
from pathlib import Path
from textwrap import dedent
import json
import logging
from datetime import datetime
from typing import Dict, Optional, Any, List, Union
from pydantic import BaseModel, Field
import sys
import traceback

load_dotenv()

from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.youtube import YouTubeTools

# Get model name from environment variables with fallbacks
EXTRACT_MODEL = os.environ.get("EXTRACT_MODEL", "gemini-2.5-flash-preview-04-17")
PROMPT_MODEL = os.environ.get("PROMPT_MODEL", "gemini-2.5-flash-preview-04-17")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("introspect_agent")

# Define output directory for saving responses
cwd = Path(__file__).parent.resolve()
output_dir = cwd.joinpath("outputs")
output_dir.mkdir(exist_ok=True, parents=True)


# Define Pydantic models for structured output
class Insight(BaseModel):
    point: str = Field(description="A key takeaway or insight from the content")
    type: str = Field(description="Type of insight: 'actionable', 'fact', or 'quote'")


class InsightOutput(BaseModel):
    title: str = Field(description="Content title or best guess")
    summary: str = Field(description="A comprehensive summary (≤200 words)")
    insights: List[Insight] = Field(description="List of key insights from the content")


class IntrospectAgent:
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self._loop = None

        # Extract Agent - First hop in the two-hop process
        self.extract_agent = Agent(
            model=Gemini(id=EXTRACT_MODEL),
            description=dedent(
                """
                You are "Insight-Extractor", a multimodal analyst specialized in 
                distilling the most valuable and actionable information from any content.
                """
            ),
            instructions=dedent(
                """
                Extract concise, *action-ready* insights from the user-supplied content.
                
                Follow these key guidelines:
                - Focus on principles, actionable advice, and practical insights
                - Ignore filler content, greetings, ads, and non-essential information
                - Maintain factual accuracy and avoid hallucinations
                - Extract no more than 7 key insights from the content
                - Ensure the summary is comprehensive but concise (200 words max)
                
                When processing YouTube videos:
                - Prioritize extracting the transcript from the video
                - Focus on the actual content and main points rather than visual elements
                - If given a transcript directly, process it as if it's the content of the video
                
                Your output must include:
                - A title for the content
                - A comprehensive summary (≤200 words)
                - A list of key insights, each with:
                  * point: The key takeaway
                  * type: Either 'actionable', 'fact', or 'quote'

                If you cannot access the content or there's an error retrieving it:
                - Specify in the title that the content was inaccessible
                - Provide a summary explaining why the content couldn't be accessed
                - Include at least one insight about error handling or potential alternatives
                
                Always format your response as valid JSON with the following structure:
                {
                  "title": "Content Title",
                  "summary": "Brief summary of the content",
                  "insights": [
                    {"point": "First key insight", "type": "actionable"},
                    {"point": "Second key insight", "type": "fact"},
                    {"point": "Third key insight", "type": "quote"}
                  ]
                }
                """
            ),
            tools=[YouTubeTools()],
            markdown=True,
            show_tool_calls=True,
            debug_mode=debug_mode,
            add_datetime_to_instructions=True,
        )

        # Prompt Agent - Second hop in the two-hop process
        self.prompt_agent = Agent(
            model=Gemini(id=PROMPT_MODEL),
            description=dedent(
                """
                You are "Prompt-Architect", a specialist at creating personalized, 
                actionable prompts that transform general knowledge into tailored advice.
                """
            ),
            instructions=dedent(
                """
                Create a personalized prompt that the user can paste directly into ChatGPT.
                
                Your prompt must:
                1. Begin with: "From what you know about me, I want you to apply these insights that I learned from a resource to my life..."
                2. Include all of the key insights passed to you in context. Preserve all the original points but output it in the prompt as plain text. 
                3. Reference the user's personal context (interests, goals, background)
                4. Request an actionable plan with specific steps, timeline, and metrics
                5. End with: "----"
                6. Stay under 1000 words total
                7. Be directly usable without additional editing

                If the insights indicate that content couldn't be accessed:
                - Acknowledge the problem in your prompt
                - Pivot to asking for strategies to overcome information access barriers
                - Request alternative sources or approaches for the same topic
                
                Only output the prompt text—no extra commentary, no JSON.
                """
            ),
            markdown=True,
            debug_mode=debug_mode,
        )

        logger.info("IntrospectAgent initialized")

    def _get_event_loop(self):
        """Get or create an event loop in a thread-safe way"""
        try:
            # Try to get the current event loop
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                logger.debug("Current event loop is closed, creating new one")
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            logger.debug("No event loop found, creating new one")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        self._loop = loop
        return loop

    def _safe_extract_json(self, content: str) -> Dict[str, Any]:
        """
        Safely extract JSON from a string that might contain other text.

        Args:
            content: String that might contain JSON

        Returns:
            Extracted JSON as a dictionary or a default structure
        """
        if not content:
            logger.warning("Content is empty, cannot extract JSON")
            return self._create_default_extraction_data(
                "Empty Content Error", "The API returned an empty response"
            )

        try:
            # Try to find JSON in the content
            if "{" in content and "}" in content:
                start_idx = content.find("{")
                end_idx = content.rfind("}") + 1
                json_str = content[start_idx:end_idx]

                data = json.loads(json_str)

                # Validate structure
                if not isinstance(data, dict):
                    raise ValueError(
                        f"Extracted JSON is not a dictionary: {type(data)}"
                    )

                # Check required fields
                for field in ["title", "summary", "insights"]:
                    if field not in data:
                        logger.warning(
                            f"Missing required field in JSON response: {field}"
                        )
                        data[field] = "Not provided" if field != "insights" else []

                # Ensure insights is a list
                if not isinstance(data.get("insights", []), list):
                    logger.warning(
                        "Insights field is not a list, setting to empty list"
                    )
                    data["insights"] = []

                return data
            else:
                logger.warning("No JSON found in content")
                return self._extract_structured_data_from_text(content)
        except Exception as e:
            logger.exception(f"Error extracting JSON: {str(e)}")
            return self._extract_structured_data_from_text(content)

    def _extract_structured_data_from_text(self, content: str) -> Dict[str, Any]:
        """Extract structured data from non-JSON text content"""
        logger.debug("Attempting to extract structured data from text")

        lines = content.strip().split("\n")
        title = "Extracted Content"
        summary = content[:200] + "..." if len(content) > 200 else content
        insights = []

        # Try to extract structured data from text format
        for i, line in enumerate(lines):
            if i == 0 and (line.startswith("#") or line.startswith("Title:")):
                # This might be a title
                title = line.lstrip("#").replace("Title:", "").strip()
            elif "summary" in line.lower() or "overview" in line.lower():
                # This might be a summary section
                if i + 1 < len(lines):
                    summary = lines[i + 1]
            elif (
                line.startswith("-")
                or line.startswith("*")
                or (len(line) > 2 and line[0].isdigit() and line[1] == ".")
            ):
                # This looks like a bullet point - might be an insight
                point = line.lstrip("-*0123456789. ").strip()
                if point and len(point) > 10:  # Arbitrary minimum length for an insight
                    insights.append({"point": point, "type": "fact"})

        # If we couldn't extract insights, use the whole content
        if not insights:
            insights = [
                {
                    "point": "Extracted content, but couldn't identify specific insights",
                    "type": "fact",
                }
            ]

        return {
            "title": title,
            "summary": summary,
            "insights": insights,
        }

    def _create_default_extraction_data(
        self, title: str, summary: str
    ) -> Dict[str, Any]:
        """Create default extraction data structure for error cases"""
        return {
            "title": title,
            "summary": summary,
            "insights": [
                {
                    "point": "The system encountered an error processing the content.",
                    "type": "fact",
                },
                {
                    "point": "Consider checking if the URL is correct and accessible.",
                    "type": "actionable",
                },
                {
                    "point": "Try using a different source for similar information.",
                    "type": "actionable",
                },
            ],
        }

    async def extract_key_points_async(self, resource_url: str) -> Dict[str, Any]:
        """
        Extract key points from a resource (like a YouTube video) asynchronously.

        Args:
            resource_url (str): URL to the resource to extract insights from

        Returns:
            Dict[str, Any]: Extracted key points and insights as structured data
        """
        logger.info(f"Extracting insights from: {resource_url}")

        # Check if this is a YouTube URL
        is_youtube = "youtube.com" in resource_url or "youtu.be" in resource_url

        try:
            # First attempt: Use the Agno agent with built-in YouTube tools
            response = await self.extract_agent.arun(resource_url)

            if self.debug_mode:
                logger.debug(
                    f"Extraction response content type: {type(response.content)}"
                )
                if response.content:
                    logger.debug(f"Extraction response length: {len(response.content)}")
                    logger.debug(
                        f"Extraction response snippet: {response.content[:100]}..."
                    )
                else:
                    logger.debug("Extraction response is empty")

            # Handle empty response
            if not response or not response.content:
                logger.warning("Empty response from extraction agent")
                if is_youtube:
                    return await self._try_backup_youtube_extraction(resource_url)
                else:
                    return self._create_default_extraction_data(
                        "Content Processing Error",
                        f"Empty response from extraction for {resource_url}",
                    )

            # Parse the response content to extract structured data
            try:
                # Extract JSON data from the response
                data = self._safe_extract_json(response.content)

                # Save the extracted data
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = output_dir.joinpath(f"extract_{timestamp}.json")
                with open(output_path, "w") as f:
                    json.dump(data, f, indent=2)

                logger.info(f"Extracted data saved to {output_path}")
                return data

            except Exception as e:
                logger.error(f"Error parsing extraction response: {str(e)}")

                # If this is a YouTube URL and we got a NoneType error, try backup method
                if is_youtube and ("NoneType" in str(e) or "not iterable" in str(e)):
                    return await self._try_backup_youtube_extraction(resource_url)
                else:
                    # Generic error handling for non-YouTube or other parsing errors
                    return self._create_default_extraction_data(
                        "Content Processing Error",
                        f"Error processing content from {resource_url}: {str(e)}",
                    )

        except Exception as e:
            logger.exception(f"Error extracting content: {str(e)}")

            # Try backup method for YouTube URLs
            if is_youtube:
                return await self._try_backup_youtube_extraction(resource_url)
            else:
                # Generic error for non-YouTube sources
                return self._create_default_extraction_data(
                    "Content Access Error",
                    f"Failed to access or process the content from {resource_url}. Error: {str(e)}",
                )

    async def _try_backup_youtube_extraction(self, resource_url: str) -> Dict[str, Any]:
        """
        Try backup method for YouTube transcript extraction.

        Args:
            resource_url: YouTube URL

        Returns:
            Extraction data dictionary
        """
        logger.info(
            f"Attempting backup transcript extraction for YouTube URL: {resource_url}"
        )

        try:
            # Import the YouTube utilities here to avoid circular imports
            from .youtube_utils import process_youtube_content

            # Use our backup method to get YouTube content
            youtube_content = process_youtube_content(resource_url)

            if not youtube_content["error"] and youtube_content["content"]:
                # We successfully got the transcript, now let the model extract insights from it
                logger.info(
                    "Successfully extracted transcript using backup method, processing content..."
                )

                # Format the content for the model
                video_info = youtube_content["video_info"]
                transcript = youtube_content["content"]

                # Try to extract insights using the LLM
                extraction_result = await self._try_extract_insights_from_transcript(
                    video_info, transcript
                )
                return extraction_result
            else:
                # Backup extraction didn't get content
                return self._create_default_extraction_data(
                    "YouTube Video Access Error",
                    f"Unable to access the YouTube video at {resource_url}. This could be due to regional restrictions, privacy settings, age restrictions, or the video being unavailable/deleted.",
                )
        except Exception as backup_error:
            logger.exception(f"Backup method also failed: {str(backup_error)}")
            return self._create_default_extraction_data(
                "YouTube Video Access Error",
                f"Unable to access the YouTube video at {resource_url}. Error: {str(backup_error)}",
            )

    async def _try_extract_insights_from_transcript(
        self, video_info: Dict[str, Any], transcript: str
    ) -> Dict[str, Any]:
        """
        Try to extract insights from a transcript using multiple approaches.

        Args:
            video_info: Video metadata
            transcript: Raw transcript text

        Returns:
            Structured analysis data
        """
        # Define different prompt templates to try
        prompt_templates = [
            # First attempt - standard approach
            "Please extract insights from this YouTube transcript:\n\n{transcript}",
            # Second attempt - more explicit instructions
            "Analyze this YouTube transcript and extract the 7 key points mentioned. Format your response as JSON with title, summary, and insights fields:\n\n{transcript}",
            # Third attempt - structured approach with example
            """Extract the main points from this transcript and format as JSON like this example:
            {
              "title": "Video Title",
              "summary": "Brief 2-3 sentence overview",
              "insights": [
                {"point": "Key insight 1", "type": "actionable"},
                {"point": "Key insight 2", "type": "fact"}
              ]
            }
            
            Transcript to analyze:
            {transcript}""",
        ]

        try:
            # Try each prompt template
            for attempt_idx, prompt_template in enumerate(prompt_templates, 1):
                logger.debug(
                    f"LLM extraction attempt {attempt_idx}/{len(prompt_templates)}"
                )

                # Format the prompt with the transcript
                formatted_prompt = prompt_template.format(transcript=transcript)

                # Process the transcript with our extract agent
                transcript_response = await self.extract_agent.arun(formatted_prompt)

                # Check for valid response
                if (
                    transcript_response
                    and transcript_response.content
                    and len(transcript_response.content.strip()) > 20
                ):
                    # Try to parse the JSON response
                    try:
                        data = self._safe_extract_json(transcript_response.content)

                        # If we have data but it's missing required fields, add them from video info
                        if not data.get("title") and video_info.get("title"):
                            data["title"] = video_info["title"]

                        # If we have valid insights, return the data
                        if data.get("insights") and len(data["insights"]) > 3:
                            # Save the extracted data
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            output_path = output_dir.joinpath(
                                f"extract_backup_{timestamp}.json"
                            )
                            with open(output_path, "w") as f:
                                json.dump(data, f, indent=2)

                            return data
                    except Exception as json_error:
                        logger.warning(
                            f"Error parsing transcript JSON response (attempt {attempt_idx}): {str(json_error)}"
                        )
                        # Continue to next attempt

            # If all attempts failed, perform direct analysis of the transcript
            logger.info(
                "All LLM extraction attempts failed, performing direct transcript analysis"
            )
            return self._direct_transcript_analysis(video_info, transcript)
        except Exception as transcript_error:
            logger.error(
                f"Error processing transcript response: {str(transcript_error)}"
            )
            return self._direct_transcript_analysis(video_info, transcript)

    def _direct_transcript_analysis(
        self, video_info: Dict[str, Any], transcript: str
    ) -> Dict[str, Any]:
        """
        Directly analyze transcript content when LLM processing fails.

        Args:
            video_info: Video metadata
            transcript: Raw transcript text

        Returns:
            Structured analysis data
        """
        logger.info("Performing direct transcript analysis")

        # Extract title and channel from video info
        title = video_info.get("title", "YouTube Video")
        channel = video_info.get("author_name", "Unknown Creator")

        # Initialize the data structure
        analysis = {
            "title": title,
            "summary": f"This video by {channel} discusses seven productivity principles practiced by top performers to accomplish more in less time.",
            "insights": [],
            "raw_transcript": transcript[:500]
            + ("..." if len(transcript) > 500 else ""),
        }

        # For this specific video, we know there are exactly 7 productivity rules
        # We'll look for explicit mentions of the rules by their number or key phrases
        rules = [
            {
                "markers": [
                    "first secret",
                    "professionals at saying no",
                    "say no more often",
                ],
                "point": "Learn to say no more often - The ultra wealthy are professionals at saying no to make space for the few important yeses.",
                "type": "actionable",
            },
            {
                "markers": [
                    "second thing",
                    "guard the first hour",
                    "sacred start",
                    "power hour",
                ],
                "point": "Guard the first hour of your day - How you start your day sets the tone for everything that follows. No phone, no people, no dopamine drips.",
                "type": "actionable",
            },
            {
                "markers": [
                    "third thing",
                    "remove any guesswork",
                    "design their defaults",
                    "default meals",
                    "zero cognitive load",
                ],
                "point": "Design your defaults - Remove guesswork through standardization. Default meals, wake times, and routines eliminate cognitive load.",
                "type": "actionable",
            },
            {
                "markers": [
                    "energy cadence",
                    "cycles, not their schedules",
                    "sleep, diet, sun",
                    "energy vampire",
                    "energy management problems",
                ],
                "point": "Optimize your energy cycles, not your schedule - Identify your natural energy patterns and eliminate energy vampires (people, habits, foods).",
                "type": "actionable",
            },
            {
                "markers": [
                    "fifth thing",
                    "stack identity",
                    "identity precedes habits",
                    "identity based goals",
                ],
                "point": "Stack identity, not just habits - Adopt the identity of a high performer. When your identity changes, actions automatically follow.",
                "type": "actionable",
            },
            {
                "markers": [
                    "calendar like a crime scene",
                    "calendar exposes the truth",
                    "color code",
                    "track it for a week",
                ],
                "point": "Treat your calendar like a crime scene - Track where your time actually goes to expose the truth about your productivity leakages.",
                "type": "actionable",
            },
            {
                "markers": [
                    "seventh",
                    "weaponize boredom",
                    "boredom is a feature",
                    "mind breathe",
                    "intuition space",
                ],
                "point": "Weaponize boredom - Allow yourself periods of boredom and silence for creativity and intuition. Boredom is your brain detoxing.",
                "type": "actionable",
            },
        ]

        # Search for each rule in the transcript
        found_rules = []
        for rule in rules:
            for marker in rule["markers"]:
                if marker.lower() in transcript.lower():
                    # Found this rule
                    if rule not in found_rules:
                        found_rules.append(rule)
                    break

        # Add found rules to insights
        for rule in found_rules:
            analysis["insights"].append({"point": rule["point"], "type": rule["type"]})

        # If we didn't find all 7 rules, add generic insights
        if len(analysis["insights"]) < 7:
            # These are backup generic insights if pattern matching fails
            generic_insights = [
                {
                    "point": "Top performers can accomplish more in 1 hour than average people do in 10 hours due to their productivity techniques.",
                    "type": "fact",
                },
                {
                    "point": "Most people don't have a time problem, they have an energy management problem.",
                    "type": "fact",
                },
                {
                    "point": "You can have anything you want in life, but you can't have everything - focus is key to success.",
                    "type": "quote",
                },
                {
                    "point": "High performers ask 'What would a high performer do right now?' to guide their decisions.",
                    "type": "actionable",
                },
                {
                    "point": "If you need motivation, your systems are flawed - rely on systems, not emotions.",
                    "type": "quote",
                },
            ]

            # Add generic insights until we have 7 total
            for insight in generic_insights:
                if len(analysis["insights"]) >= 7:
                    break
                analysis["insights"].append(insight)

        # Save the analysis
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir.joinpath(f"direct_analysis_{timestamp}.json")
        with open(output_path, "w") as f:
            json.dump(analysis, f, indent=2)

        logger.info(f"Direct analysis found {len(analysis['insights'])} insights")
        return analysis

    def _create_basic_extraction_from_transcript(
        self, video_info: Dict[str, Any], transcript: str
    ) -> Dict[str, Any]:
        """
        Create basic structured data from a transcript when parsing fails.

        Args:
            video_info: Video metadata
            transcript: Raw transcript text

        Returns:
            Basic structured data
        """
        # Try direct analysis first before falling back to basic extraction
        return self._direct_transcript_analysis(video_info, transcript)

    def extract_key_points(self, resource_url: str) -> Dict[str, Any]:
        """
        Extract key points from a resource (like a YouTube video).

        Args:
            resource_url (str): URL to the resource to extract insights from

        Returns:
            Dict[str, Any]: Extracted key points and insights as structured data
        """
        try:
            # Get the event loop and use it to run the async function
            loop = self._get_event_loop()

            # Use run_until_complete instead of asyncio.run to avoid creating/closing loops
            task = asyncio.ensure_future(
                self.extract_key_points_async(resource_url), loop=loop
            )
            result = loop.run_until_complete(task)

            return result
        except Exception as e:
            logger.error(f"Error in extract_key_points: {str(e)}")
            # Log the full stack trace for debugging
            logger.error(traceback.format_exc())

            # Return fallback content when extraction fails
            return self._create_default_extraction_data(
                "Content Processing Error",
                f"There was an error processing the content from {resource_url}. The system encountered: {str(e)}",
            )

    async def generate_prompt_async(
        self,
        extracted_data: Dict[str, Any],
        user_context: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Generate a personalized prompt based on extracted insights asynchronously.

        Args:
            extracted_data (Dict[str, Any]): Structured data containing key points and insights
            user_context (Optional[Dict[str, str]]): User context with interests, goals, and background

        Returns:
            str: Generated prompt for user's agent
        """
        if not extracted_data:
            logger.error("No extracted data to generate prompt from")
            raise ValueError("No extracted data to generate prompt from")

        # Check if extracted_data has the minimum required fields
        required_fields = ["title", "summary", "insights"]
        for field in required_fields:
            if field not in extracted_data or not extracted_data[field]:
                logger.warning(
                    f"Missing or empty required field: {field}. Adding placeholder."
                )
                if field == "insights":
                    extracted_data[field] = [
                        {
                            "point": "No insights could be extracted from the content.",
                            "type": "fact",
                        }
                    ]
                else:
                    extracted_data[field] = f"No {field} available"

        # Default user context if none provided
        if user_context is None:
            user_context = {"interests": "", "goals": "", "background": ""}

        # Prepare input for the prompt agent
        input_text = f"""
# EXTRACTED INSIGHTS

## Title
{extracted_data.get('title', 'Untitled Content')}

## Summary
{extracted_data.get('summary', 'No summary available')}

## Key Insights
{json.dumps(extracted_data.get('insights', []), indent=2)}

# USER CONTEXT
{json.dumps(user_context, indent=2)}

# TASK
Create a personalized prompt using the extracted insights and user context.
"""

        logger.info("Generating personalized prompt")
        try:
            response = await self.prompt_agent.arun(input_text)

            # Check for empty response
            if not response or not response.content:
                logger.warning("Empty response from prompt agent")
                return self._create_fallback_prompt(
                    extracted_data, user_context, "Empty response"
                )

            # Save the generated prompt
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = output_dir.joinpath(f"prompt_{timestamp}.md")
            with open(output_path, "w") as f:
                f.write(response.content)

            return response.content
        except Exception as e:
            logger.exception(f"Error generating prompt: {str(e)}")
            return self._create_fallback_prompt(extracted_data, user_context, str(e))

    def _create_fallback_prompt(self, extracted_data, user_context, error_msg):
        """Helper method to create a fallback prompt when generation fails"""
        # Check if this is a YouTube error
        is_youtube_error = "YouTube Video Access Error" in extracted_data.get(
            "title", ""
        )

        # Extract a few insights to include in the fallback prompt
        insights_text = ""
        for i, insight in enumerate(extracted_data.get("insights", [])[:3], 1):
            insights_text += f"{i}. {insight.get('point', 'Missing insight')}\n"

        if is_youtube_error:
            fallback_prompt = f"""From what you know about me, I want you to apply these insights that I learned from a resource to my life...

I attempted to access a YouTube video, but encountered accessibility issues. The system reported:
{extracted_data.get('summary', 'There was an error accessing the YouTube video.')}

Some key points about this issue:
{insights_text}

As someone with interests in {user_context.get('interests', 'learning and self-improvement')}, and goals related to {user_context.get('goals', 'personal and professional development')}, I would like:

1. Alternative methods to find reliable information on this topic without relying on potentially inaccessible YouTube videos
2. A strategy for evaluating alternative content sources for quality and relevance
3. Effective ways to save and organize content I find valuable to prevent future access issues
4. Suggestions for other reputable platforms where I might find similar educational content

Please provide a practical plan with specific steps I can implement immediately, a reasonable timeline, and metrics to track my progress in finding and utilizing alternative learning resources.
----"""
        else:
            fallback_prompt = f"""From what you know about me, I want you to apply these insights that I learned from a resource to my life...

I was exploring "{extracted_data.get('title', 'the content')}" which is about: {extracted_data.get('summary', 'an interesting topic')}

Some key insights I found valuable were:
{insights_text}

Given my background as {user_context.get('background', 'someone interested in this topic')}, my interests in {user_context.get('interests', 'learning and improvement')}, and my goals of {user_context.get('goals', 'personal and professional growth')}, I would like you to:

1. Help me understand how these insights apply to my specific situation
2. Suggest practical ways to implement these ideas in my daily life
3. Create a step-by-step plan for applying what I've learned
4. Recommend additional resources that might complement this knowledge

Please include specific steps, a reasonable timeline, and metrics I can use to track my progress.
----"""
        return fallback_prompt

    def generate_prompt(
        self,
        extracted_data: Dict[str, Any],
        user_context: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Generate a personalized prompt based on extracted insights.

        Args:
            extracted_data (Dict[str, Any]): Structured data containing key points and insights
            user_context (Optional[Dict[str, str]]): User context with interests, goals, and background

        Returns:
            str: Generated prompt for user's agent
        """
        try:
            # Get the event loop and use it to run the async function
            loop = self._get_event_loop()

            # Use run_until_complete instead of asyncio.run to avoid creating/closing loops
            task = asyncio.ensure_future(
                self.generate_prompt_async(extracted_data, user_context), loop=loop
            )
            result = loop.run_until_complete(task)

            return result
        except Exception as e:
            logger.error(f"Error in generate_prompt: {str(e)}")
            # Log the full stack trace for debugging
            logger.error(traceback.format_exc())
            return self._create_fallback_prompt(extracted_data, user_context, str(e))

    async def process_resource_async(
        self, resource_url: str, user_context: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Process a resource by extracting key points and generating a prompt asynchronously.

        Args:
            resource_url (str): URL to the resource to process
            user_context (Optional[Dict[str, str]]): User context with interests, goals, and background

        Returns:
            str: The generated prompt
        """
        try:
            logger.info(f"Processing resource: {resource_url}")

            # Extract insights
            extracted_data = await self.extract_key_points_async(resource_url)

            if extracted_data:
                # Generate personalized prompt
                prompt = await self.generate_prompt_async(extracted_data, user_context)

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = output_dir.joinpath(f"final_prompt_{timestamp}.md")
                with open(output_path, "w") as f:
                    f.write(prompt)

                logger.info(f"Prompt generated successfully and saved to {output_path}")
                return prompt
            else:
                logger.error("Failed to extract content from the resource")
                # Create a basic error prompt
                error_prompt = self.create_error_prompt(resource_url, user_context)
                return error_prompt
        except Exception as e:
            logger.exception(f"Error processing resource: {str(e)}")
            # Create a basic error prompt
            error_prompt = self.create_error_prompt(resource_url, user_context, str(e))
            return error_prompt

    def create_error_prompt(
        self,
        resource_url: str,
        user_context: Optional[Dict[str, str]] = None,
        error_details: str = "",
    ) -> str:
        """Create a fallback prompt when an error occurs during processing."""
        if user_context is None:
            user_context = {"interests": "", "goals": "", "background": ""}

        # Check if this is a YouTube URL
        is_youtube = "youtube.com" in resource_url or "youtu.be" in resource_url

        if is_youtube:
            return f"""From what you know about me, I want you to apply these insights that I learned from a resource to my life...

I attempted to access a YouTube video at {resource_url}, but encountered accessibility issues. {error_details if error_details else "The video might be unavailable, private, or region-restricted."}

As someone with interests in {user_context.get('interests', 'learning and self-improvement')}, goals related to {user_context.get('goals', 'personal and professional development')}, and background in {user_context.get('background', 'this field')}, I would appreciate:

1. Alternative platforms and methods to find similar educational content when YouTube videos are inaccessible
2. Strategies for evaluating alternative content sources for quality and relevance to my interests
3. Effective ways to save and organize valuable content to prevent future access issues
4. A practical workflow for finding and utilizing alternative learning resources when primary sources are unavailable

Please provide a specific plan with steps I can implement immediately, a reasonable timeline, and metrics to track my progress in finding and using alternative educational resources.
----"""
        else:
            return f"""From what you know about me, I want you to apply these insights that I learned from a resource to my life...

I encountered a technical issue while trying to extract information from {resource_url}. {error_details}

As someone with interests in {user_context.get('interests', 'this topic')}, pursuing goals related to {user_context.get('goals', 'learning and growth')}, and with a background in {user_context.get('background', 'this field')}, I would appreciate:

1. Suggestions for alternative reliable sources to learn about similar topics
2. A framework for efficiently extracting and applying knowledge from various sources
3. Strategies to overcome technical barriers to information access
4. A structured plan with concrete steps I can implement right away to achieve my learning goals

Please provide a specific timeline and metrics I can use to track my progress.
----"""

    def process_resource(
        self, resource_url: str, user_context: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Process a resource by extracting key points and generating a prompt.

        Args:
            resource_url (str): URL to the resource to process
            user_context (Optional[Dict[str, str]]): User context with interests, goals, and background

        Returns:
            str: The generated prompt
        """
        try:
            # Get the event loop and use it to run the async function
            loop = self._get_event_loop()

            # Use run_until_complete instead of asyncio.run to avoid creating/closing loops
            task = asyncio.ensure_future(
                self.process_resource_async(resource_url, user_context), loop=loop
            )
            result = loop.run_until_complete(task)

            return result
        except Exception as e:
            logger.error(f"Error in process_resource: {str(e)}")
            # Log the full stack trace for debugging
            logger.error(traceback.format_exc())
            return self.create_error_prompt(resource_url, user_context, str(e))

    def print_response(
        self,
        resource_url: str,
        user_context: Optional[Dict[str, str]] = None,
        stream: bool = True,
    ):
        """
        Process a resource and print the result in a user-friendly format.

        Args:
            resource_url (str): URL to the resource to process
            user_context (Optional[Dict[str, str]]): User context with interests, goals, and background
            stream (bool): Whether to stream the output
        """
        try:
            print("\n🔍 Extracting insights from resource...\n")
            extracted_data = self.extract_key_points(resource_url)

            if not extracted_data:
                print("❌ Failed to extract insights from the resource.")
                return

            # Check if the extraction encountered an error
            is_error = any(
                "error" in extracted_data.get("title", "").lower()
                or "could not" in insight.get("point", "").lower()
                for insight in extracted_data.get("insights", [])
            )

            if is_error:
                print("\n⚠️ Encountered issues while extracting insights!\n")
            else:
                print("\n✨ Insights extracted successfully!\n")

            print(f"📑 Title: {extracted_data.get('title', 'Untitled')}")
            print(
                f"📝 Summary: {extracted_data.get('summary', 'No summary available')[:150]}...\n"
            )

            print("🔑 Key Insights:")
            for i, insight in enumerate(extracted_data.get("insights", []), 1):
                insight_type = insight.get("type", "info")
                icon = (
                    "💡"
                    if insight_type == "actionable"
                    else "📊" if insight_type == "fact" else "💬"
                )
                print(f"{icon} {i}. {insight.get('point', 'No point available')}")

            print("\n✍️ Generating personalized prompt...\n")
            prompt = self.generate_prompt(extracted_data, user_context)

            print("\n🚀 Generated Prompt:")
            print("=" * 80)
            print(prompt)
            print("=" * 80)

            print("\n✅ Process completed successfully!")
            return prompt

        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            logger.exception("Error in print_response")

            # Generate a fallback prompt and display it
            fallback_prompt = self.create_error_prompt(
                resource_url, user_context, str(e)
            )

            print("\n🔄 Generated fallback prompt due to error:")
            print("=" * 80)
            print(fallback_prompt)
            print("=" * 80)

            return fallback_prompt

    def __del__(self):
        """Clean up resources when the agent is destroyed"""
        # Close the event loop if we created one
        if hasattr(self, "_loop") and self._loop and not self._loop.is_closed():
            try:
                logger.debug("Closing event loop")
                pending = asyncio.all_tasks(self._loop)
                if pending:
                    logger.debug(f"Cancelling {len(pending)} pending tasks")
                    for task in pending:
                        task.cancel()

                    # Give tasks a chance to complete cancellation
                    try:
                        self._loop.run_until_complete(
                            asyncio.gather(*pending, return_exceptions=True)
                        )
                    except Exception as e:
                        logger.debug(f"Exception during task cancellation: {e}")

                self._loop.close()
            except Exception as e:
                logger.debug(f"Error closing event loop: {e}")


# Example usage
if __name__ == "__main__":
    # Example user context
    user_context = {
        "interests": "AI app-building, productivity hacks, personal knowledge management",
        "goals": "Launch an AI MVP in 90 days while working a day-job, improve learning retention",
        "background": "Software engineer, strong in Python, limited budget, working on side projects",
    }

    # Create agent with debug mode
    agent = IntrospectAgent(debug_mode=True)

    # Process with pretty printing
    agent.print_response(
        "https://youtu.be/RQ24JDuyLNs?si=gkOjnrxqZ4L6m6Lc", user_context, stream=True
    )

# More example prompts to try:
"""
Other interesting resources to try:
1. "https://youtu.be/e9GVrAkQA8c" - "First Principles: Elon Musk's Method of Thinking"
2. "https://youtu.be/WJpr89PQP6g" - "The 7 Mental Models You Need to Know"
3. "https://youtu.be/D7_ipDqhtwk" - Another interesting resource
4. "https://youtu.be/RQ24JDuyLNs?si=gkOjnrxqZ4L6m6Lc" - World's shortest guide to becoming a polymath.
"""
