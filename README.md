# SERP Analysis and Content Outline Tool

This Python script is designed to automate the process of analyzing Search Engine Result Pages (SERPs) for SEO content planning. It performs the following key actions:

1.  **Scrapes Google SERP:** Uses the Serper API to fetch search results for a given query.
2.  **Extracts Content Outlines:** For each search result URL, it scrapes the webpage content using the Firecrawl API and extracts a structured outline, including key points, media inclusions, subheadings, content depth, and content format.
3.  **AI-Powered SERP Analysis:** Leverages the OpenAI GPT-4o model to analyze the outlines from multiple pages and identify commonalities across the SERP. This includes:
    - **Common Topics:** Identifies recurring topics and summarizes their importance.
    - **Media Type Usage:** Analyzes the types of media used and provides insights.
    - **Content Formats:** Summarizes common content formats found in the SERP.
    - **Content Depths:** Analyzes the depth of content across the SERP.
4.  **Markdown Output:** Generates a comprehensive Markdown report (`serp_analysis.md`) summarizing the SERP analysis, content outlines, and raw search results.

## Key Features

- **Automated SERP Scraping:** Fetches search results efficiently using the Serper API.
- **Structured Webpage Scraping:** Extracts relevant content from webpages using the Firecrawl API and organizes it into a structured format.
- **AI-Driven Insights:** Employs OpenAI's GPT-4o to analyze SERP data and provide valuable SEO insights.
- **Comprehensive Markdown Report:** Outputs a well-formatted Markdown file containing the analysis, outlines, and raw SERP data for easy review and sharing.
- **Customizable Analysis:** The script is structured to be easily extended to extract and analyze additional SERP features and content characteristics.

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### API Keys

To use this script, you will need API keys for the following services:

1.  **OpenAI API Key:** Required to access the GPT-4o model for SERP analysis. You can obtain an API key from [OpenAI](https://platform.openai.com/).
2.  **Serper API Key:** Used for scraping Google Search Results. Sign up for a free or paid plan at [Serper.dev](https://serper.dev/) to get your API key.
3.  **Firecrawl API Key:** Used for scraping webpage content. Get your API key from [Firecrawl](https://firecrawl.com/).

### Environment Variables

1.  Create a `.env` file in the same directory as `main.py`.
2.  Add your API keys to the `.env` file as follows:

    ```env
    OPENAI_API_KEY=YOUR_OPENAI_API_KEY
    SERPER_API_KEY=YOUR_SERPER_API_KEY
    FIRECRAWL_API_KEY=YOUR_FIRECRAWL_API_KEY
    ```

    **Replace `YOUR_OPENAI_API_KEY`, `YOUR_SERPER_API_KEY`, and `YOUR_FIRECRAWL_API_KEY` with your actual API keys.**

### Installation

1.  **Clone the repository** (if you are using Git) or download the files (`main.py`, `.env`, `requirements.txt`).
2.  **Navigate to the project directory** in your terminal.
3.  **Install the required Python packages** using pip:

    ```bash
    pip install -r requirements.txt
    ```

## Usage Instructions

1.  **Ensure you have set up your `.env` file with the correct API keys.**
2.  **Run the script** from your terminal:

    ```bash
    python main.py
    ```

3.  The script will:

    - Perform a SERP analysis for the hardcoded search query "how to walk a dog" (you can modify the `inputs_for_serp_response` variable in `main.py` to change the query).
    - Scrape and outline the top search results.
    - Analyze the outlines to identify commonalities.
    - Generate a Markdown report named `serp_analysis.md` in the same directory.

4.  **Open `serp_analysis.md`** to view the detailed SERP analysis, content outlines, and raw search results in Markdown format.

## Output Files

- **`serp_analysis.md`:** This Markdown file contains the complete SERP analysis report, including:
  - Commonalities Across SERP (Topics, Media Usage, Content Formats, Content Depths)
  - Detailed Outlines for each scraped webpage
  - Raw Search Results from Serper API

## Disclaimer

- This script utilizes third-party APIs (OpenAI, Serper, Firecrawl) which may have usage limits and associated costs depending on your usage volume and chosen plans. Please review the terms of service and pricing for each API provider.
- Web scraping should be performed responsibly and in accordance with the terms of service of the target websites.
