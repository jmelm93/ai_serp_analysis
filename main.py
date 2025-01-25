import asyncio
from loguru import logger
from pydantic import BaseModel, Field
from typing import List
from langchain_openai import ChatOpenAI
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.document_loaders.firecrawl import FireCrawlLoader
from langchain_core.tools import tool
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

model = ChatOpenAI(model="gpt-4o")
query = "how to walk a dog"

# Structured SERP Scraping
class SERPItem(BaseModel):
    title: str = Field(name="title", description="The title of the search result.")
    snippet: str = Field(name="snippet", description="A brief snippet of the content.")
    url: str = Field(name="url", description="The URL of the search result.")
    domain: str = Field(name="domain", description="The domain of the search result.")
    
class SERPResponse(BaseModel):
    results: List[SERPItem] = Field(name="results", description="A list of search results.")
    
    @property
    def to_markdown(self) -> str:
        """Converts the SERPResponse to a Markdown string."""
        md = f"## Search Results\n\n"
        for result in self.results:
            md += f"### {result.title}\n"
            md += f"**URL:** {result.url}\n"
            md += f"**Domain:** {result.domain}\n"
            md += f"{result.snippet}\n\n"
        return md

# Structured Page Scraping
class SubSection(BaseModel):
    subheading: str = Field(name="subheading", description="The subheading text.")
    overview: str = Field(name="overview", description="A concise overview of the content within the subheading.")

class MediaTypes(BaseModel):
    media_type: str = Field(name="media_type", description="The type of media included in the section (e.g., image, video, etc.).")
    descriptions: str = Field(name="descriptions", description="A brief description of the media content (e.g., 'calculator for a users tax bracket').")

class Images(BaseModel):
    image_url: str = Field(name="image_url", description="The URL of the image.")
    alt_text: str = Field(name="alt_text", description="The alt text for the image.")

class PageSection(BaseModel):
    section: str = Field(name="section", description="The main content header.")
    key_points: List[str] = Field(name="key_points", description="A list of key points from the section.")
    media_inclusions: List[MediaTypes] = Field(name="media_inclusions", description="A list of media types and descriptions used in the section.")
    subheadings: List[SubSection] = Field(name="subheadings", description="A list of subheadings with overviews.")

class Outline(BaseModel):
    url: str = Field(name="url", description="The URL of the page.")
    keyword_targets: List[str] = Field(name="keyword_targets", description="A list of SEO target keywords based on the content.")
    page_summary: List[PageSection] = Field(name="page_summary", description="Structured summary of the page content.")
    page_links: List[str] = Field(name="page_links", description="A list of all unique hyperlinks found on the page.")
    images: List[Images] = Field(name="images", description="A list of images used on the page.")
    content_depth: str = Field(name="content_depth", description="Content depth of the page (e.g., 1 - Shallow, 2 - Medium, 3 - Deep). Include both the depth and category (e.g., 2 - Medium).")
    content_format: str = Field(name="content_format", description="The content format of the page (e.g., listicle, how-to guide).")

class OutlineResponse(BaseModel):
    outline: Outline = Field(name="outline", description="Structured content outline.")

    @property
    def to_markdown(self) -> str:
        """Converts the OutlineResponse to a Markdown string."""
        md = f"## Outline for: {self.outline.url}\n\n"
        if self.outline.keyword_targets:
            md += f"**Keyword Targets:** {', '.join(self.outline.keyword_targets)}\n\n"
        
        for section in self.outline.page_summary:
            md += f"### {section.section}\n\n"
            if section.key_points:
                md += "**Key Points:**\n"
                for point in section.key_points:
                    md += f"- {point}\n"
                md += "\n"
            if section.media_inclusions:
                md += "**Media Inclusions:**\n"
                for media in section.media_inclusions:
                    md += f"- **{media.media_type}**: {media.descriptions}\n"
                md += "\n"
            if section.subheadings:
                md += "**Subheadings:**\n"
                for sub in section.subheadings:
                    md += f"- **{sub.subheading}**: {sub.overview}\n"
                md += "\n"
        
        md += f"**Page Links:**\n"
        for link in self.outline.page_links:
            md += f"- {link}\n"
        
        md += f"**Images:**\n"
        for image in self.outline.images:
            md += f"- ![{image.alt_text}]({image.image_url})\n"
        
        md += f"**Content Depth:** {self.outline.content_depth}\n"
        
        md += f"**Content Format:** {self.outline.content_format}\n"
        
        return md

# Structured SERP Analysis
class CommonTopicExtraction(BaseModel):
    topic_name: str = Field(name="topic_name", description="The name of the common topic.")
    related_urls: List[str] = Field(name="related_urls", description="URLs of pages that discuss this topic.")
    summary_of_importance: str = Field(name="summary_of_importance", description="Summary of why this topic is important across the SERP.")

class MediaTypeUsageAnalysis(BaseModel):
    media_type: str = Field(name="media_type", description="The type of media.")
    insight: str = Field(name="insight", description="Insight about the usage of this media type in the SERP.")
    related_urls: List[str] = Field(name="related_urls", description="URLs of pages that use this media type.")

class ContentFormatAnalysis(BaseModel):
    format_name: str = Field(name="format_name", description="The name of the content format.")
    related_urls: List[str] = Field(name="related_urls", description="URLs of pages that use this content format.")

class ContentDepthAnalysis(BaseModel):
    depth: str = Field(name="depth", description="The depth of the content.")
    related_urls: List[str] = Field(name="related_urls", description="URLs of pages that have this content depth.")

class SERPCommonalitiesResponse(BaseModel):
    common_topics: List[CommonTopicExtraction] = Field(name="common_topics", description="List of common topics extracted from SERP outlines.")
    media_type_usage: List[MediaTypeUsageAnalysis] = Field(name="media_type_usage", description="Analysis of media type usage across the SERP.")
    content_formats: List[ContentFormatAnalysis] = Field(name="content_formats", description="Summary of content formats across the SERP.")
    content_depths: List[ContentDepthAnalysis] = Field(name="content_depths", description="Summary of content depths across the SERP.")
    
    @property
    def to_markdown(self) -> str:
        """Converts the SERPAnalysisResponse to a Markdown string with each URL 
        displayed as a domain linked to the full URL."""
        
        # Helper function to transform a full URL into [domain](full_url)
        def domain_link(url: str) -> str:
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path
            return f"[{domain}]({url})"

        md = "## Commonalities Across SERP\n\n"
        
        md += "### Common Topics\n\n"
        for topic in self.common_topics:
            md += f"**Topic: {topic.topic_name}**\n"
            md += f"- **Summary of Importance:** {topic.summary_of_importance}\n"
            # Transform each URL into [domain](full_url)
            links = [domain_link(u) for u in topic.related_urls]
            md += f"- **Related URLs:** {', '.join(links)}\n\n"
        
        md += "### Media Type Usage\n\n"
        for media in self.media_type_usage:
            md += f"**Media Type: {media.media_type}**\n"
            md += f"- **Insight:** {media.insight}\n"
            links = [domain_link(u) for u in media.related_urls]
            md += f"- **Related URLs:** {', '.join(links)}\n\n"
        
        md += "### Content Formats\n\n"
        for format_ in self.content_formats:
            md += f"**Content Format: {format_.format_name}**\n"
            links = [domain_link(u) for u in format_.related_urls]
            md += f"- **Related URLs:** {', '.join(links)}\n\n"
        
        md += "### Content Depths\n\n"
        for depth in self.content_depths:
            md += f"**Content Depth: {depth.depth}**\n"
            links = [domain_link(u) for u in depth.related_urls]
            md += f"- **Related URLs:** {', '.join(links)}\n\n"
        
        return md

@tool
def get_serper_serp(query: str):
    """Use this to get the SERP for a search query."""
    serper = GoogleSerperAPIWrapper()
    results = serper.results(query)
    list_results = results.get("organic", [])
    return list_results

@tool
def get_firecrawl_scrape(url: str):
    """Use this to get the main content of a webpage."""
    firecrawl = FireCrawlLoader(url=url, mode="scrape")
    content = firecrawl.page_content
    return content

async def async_get_outline(url: str, outline_response_structured_model: ChatOpenAI):
    """Asynchronously gets the outline for a single URL with error handling."""
    try:
        inputs_for_outline_response = [("system", "Get the structured main content of the url provided."), ("user", url)]
        return await outline_response_structured_model.ainvoke(inputs_for_outline_response)
    except Exception as e:
        logger.error(f"Failed to process URL: {url}. Error: {e}")
        return None  # Return None for failed jobs

async def main():
    # Bind the tools to the model
    tools = [get_serper_serp, get_firecrawl_scrape]
    model_with_tools = model.bind_tools(tools)

    # Create models with structured output
    serp_response_structured_model = model_with_tools.with_structured_output(SERPResponse)
    outline_response_structured_model = model_with_tools.with_structured_output(OutlineResponse)
    serp_analysis_response_structured_model = model.with_structured_output(SERPCommonalitiesResponse)

    # Run the SERP extraction
    inputs_for_serp_response = [("system", "Get the SERP for a search query."), ("user", query)]
    serp_response = await serp_response_structured_model.ainvoke(inputs_for_serp_response)

    # Run outline extraction for each URL concurrently
    urls = [result.url for result in serp_response.results]
    tasks = [async_get_outline(url, outline_response_structured_model) for url in urls]
    content_responses = await asyncio.gather(*tasks)

    # Run the SERP commonalities review for the successful content responses
    successful_responses = [response for response in content_responses if response]
    markdown_of_successful_responses = [response.to_markdown for response in successful_responses]
    inputs_for_analysis = [("system", "Analyze the SERP for common topics, media type usage, content formats, and content depths."), ("user", str(markdown_of_successful_responses))]
    commonalities_response = await serp_analysis_response_structured_model.ainvoke(inputs_for_analysis)

    # create a markdown file with the analysis_response.to_markdown, followed by the markdown_of_successful_responses and the serp_response.to_markdown
    final_markdown = f"# SERP Analysis\n\n{commonalities_response.to_markdown}\n\n{''.join(markdown_of_successful_responses)}\n\n{serp_response.to_markdown}"
    
    # write to local .md file
    with open("serp_analysis.md", "w") as f:
        f.write(final_markdown)
        logger.info("Markdown file written successfully.")
        
    failed_count = len(content_responses) - len(successful_responses)
    logger.info(f'Number of failed jobs: {failed_count}')

if __name__ == "__main__":
    asyncio.run(main())