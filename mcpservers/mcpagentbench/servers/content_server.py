"""
MCPAgentBench Content MCP Server.
Concrete FastMCP server with 6 tools for the content domain.
Tools are copied from the original MCPAgentBench benchmark files
with their actual mock data implementations.
"""
from mcp.server.fastmcp import FastMCP
from typing import List
from typing import Optional
from agenttim.mcpservers.mcpagentbench.servers._error_handler import safe_tool
mcp = FastMCP("mcpbench-content")
@mcp.tool()
@safe_tool
def search_news(query: str, start_date: str, end_date: str, max_result: int) -> str:

    '''```python
    """
    Searches for news articles from multiple sources based on specified keywords
    and date range. This function aids users in discovering relevant industry
    updates, case studies, and market events for further analysis. It returns
    structured results including headline, source, publication date, summary
    snippet, and link to the full article.

    Args:
        query (str): The keywords to search for in news articles. Must be a
            non-empty string.
        start_date (str): The start date for the search range in 'YYYY-MM-DD'
            format.
        end_date (str): The end date for the search range in 'YYYY-MM-DD'
            format.
        max_result (int, optional): The maximum number of results to return.
            Must be a positive integer. Defaults to 5.

    Returns:
        str: A formatted string containing the search results. Each result
        includes the headline, source, publication date, summary, and link to
        the full article. If no articles are found, a message indicating no
        results is returned.
    """
```'''

    mock_news_db = [{'keywords': ['billboard 200', 'music', 'albums', 'charts'], 'articles': [{'headline': 'Billboard 200: Top Albums of 2023 Announced', 'source': 'Billboard', 'publication_date': '2023-12-31', 'summary': "The Billboard 200 for 2023 highlights chart-topping albums from artists like Taylor Swift, Morgan Wallen, and SZA. The Best Album of the Year is 'Guts' by Olivia Rodrigo.", 'link': 'https://www.billboard.com/top-albums-2023'}, {'headline': 'Year-End Music Charts 2023: Trends and Highlights', 'source': 'Rolling Stone', 'publication_date': '2023-12-29', 'summary': 'An in-depth look at the albums that defined 2023 and dominated the Billboard 200 charts.', 'link': 'https://www.rollingstone.com/music/year-end-2023'}, {'headline': 'Taylor Swift Leads Billboard 200 in 2023 With Record-Breaking Year', 'source': 'Variety', 'publication_date': '2023-12-28', 'summary': "Taylor Swift dominated the Billboard 200 in 2023, notching multiple weeks at No.1 with 'Midnights' and re-recorded classics.", 'link': 'https://variety.com/2023/music/news/taylor-swift-billboard-200-2023'}, {'headline': 'Billboard 200 Recap: SZA, Morgan Wallen, and More Rule 2023', 'source': 'Pitchfork', 'publication_date': '2023-12-27', 'summary': "SZA’s 'SOS' and Morgan Wallen’s 'One Thing at a Time' were among the most successful albums on the Billboard 200 in 2023.", 'link': 'https://pitchfork.com/news/billboard-200-2023-recap'}, {'headline': 'The Biggest Albums of 2023 on Billboard 200', 'source': 'NME', 'publication_date': '2023-12-26', 'summary': 'From pop icons to country superstars, these are the albums that made the Billboard 200 year-end list for 2023.', 'link': 'https://www.nme.com/news/music/billboard-200-biggest-albums-2023'}]}, {'keywords': ['e-commerce failures', 'case studies', 'online retail collapse'], 'articles': [{'headline': 'Why Brandless Failed: Lessons for E-Commerce Startups', 'source': 'TechCrunch', 'publication_date': '2021-03-15', 'summary': 'Brandless shut down after failing to differentiate in a crowded market, showing the importance of unique value propositions.', 'link': 'https://techcrunch.com/brandless-failure-analysis'}, {'headline': 'The Rise and Fall of Fab.com', 'source': 'Business Insider', 'publication_date': '2020-09-10', 'summary': 'Fab.com burned through millions in funding before collapsing due to over-expansion and lack of customer loyalty.', 'link': 'https://www.businessinsider.com/fab-dot-com-case-study'}]}, {'keywords': ['embodied intelligence', 'startups', 'robotics', 'AI industry'], 'articles': [{'headline': 'Embodied Intelligence Startups Attract Record Funding in 2024', 'source': 'MIT Technology Review', 'publication_date': '2024-05-18', 'summary': 'Robotics and AI companies focusing on embodied intelligence are seeing unprecedented investment from VCs.', 'link': 'https://www.technologyreview.com/embodied-intelligence-2024'}, {'headline': 'Top 5 Companies Leading the Embodied AI Revolution', 'source': 'Wired', 'publication_date': '2024-04-12', 'summary': 'From Figure AI to Agility Robotics, these companies are pushing the boundaries of embodied AI applications.', 'link': 'https://www.wired.com/story/embodied-ai-leaders'}]}, {'keywords': ['openai', 'chatgpt', 'gpt', 'artificial intelligence', 'AI'], 'articles': [{'headline': 'OpenAI Launches GPT-5 with Revolutionary Multimodal Capabilities', 'source': 'The Verge', 'publication_date': '2024-08-15', 'summary': "OpenAI's latest model GPT-5 introduces advanced reasoning capabilities and seamless integration across text, image, and audio modalities.", 'link': 'https://www.theverge.com/2024/8/15/openai-gpt-5-launch'}, {'headline': 'OpenAI Partners with Microsoft for Enterprise AI Solutions', 'source': 'TechCrunch', 'publication_date': '2024-07-22', 'summary': 'Microsoft and OpenAI announce expanded partnership to bring advanced AI capabilities to enterprise customers worldwide.', 'link': 'https://techcrunch.com/2024/7/22/openai-microsoft-enterprise-partnership'}, {'headline': 'ChatGPT Reaches 100 Million Monthly Active Users', 'source': 'Reuters', 'publication_date': '2024-06-10', 'summary': "OpenAI's ChatGPT continues its rapid growth, reaching a new milestone of 100 million monthly active users globally.", 'link': 'https://www.reuters.com/technology/chatgpt-100-million-users'}, {'headline': 'OpenAI Announces New Safety Measures for AI Development', 'source': 'MIT Technology Review', 'publication_date': '2024-05-28', 'summary': 'OpenAI introduces comprehensive safety protocols and ethical guidelines for the development of advanced AI systems.', 'link': 'https://www.technologyreview.com/2024/5/28/openai-safety-measures'}, {'headline': "OpenAI's Sora Video Generator Revolutionizes Content Creation", 'source': 'Wired', 'publication_date': '2024-04-05', 'summary': "OpenAI's Sora AI model demonstrates remarkable capabilities in generating high-quality video content from text prompts.", 'link': 'https://www.wired.com/story/openai-sora-video-generator'}]}]

    if not isinstance(query, str) or not query.strip():

        return "Error: 'query' must be a non-empty string."

    if not isinstance(start_date, str) or not isinstance(end_date, str):

        return "Error: 'start_date' and 'end_date' must be strings in 'YYYY-MM-DD' format."

    try:

        from_dt_obj = __import__('datetime').datetime.strptime(start_date, '%Y-%m-%d')

        to_dt_obj = __import__('datetime').datetime.strptime(end_date, '%Y-%m-%d')

    except ValueError:

        return "Error: Dates must be in 'YYYY-MM-DD' format."

    if from_dt_obj > to_dt_obj:

        return "Error: 'start_date' cannot be later than 'end_date'."

    if max_result is not None and (not isinstance(max_result, int) or max_result <= 0):

        return "Error: 'max_result' must be a positive integer."

    if max_result is None:

        max_result = 5

    results = []

    query_lower = query.lower()

    for dataset in mock_news_db:

        if any((kw in query_lower for kw in dataset['keywords'])):

            for article in dataset['articles']:

                pub_date_obj = __import__('datetime').datetime.strptime(article['publication_date'], '%Y-%m-%d')

                if from_dt_obj <= pub_date_obj <= to_dt_obj:

                    results.append(article)

    results = results[:max_result]

    if not results:

        return f"No articles found for query '{query}' in the given date range."

    output_lines = []

    for art in results:

        output_lines.append(f"Headline: {art['headline']}\nSource: {art['source']}\nDate: {art['publication_date']}\nSummary: {art['summary']}\nLink: {art['link']}\n")

    return '\n'.join(output_lines)
@mcp.tool()
@safe_tool
def search_academic_papers(query: str, subject: str, max_results: int) -> str:

    '''```python
    """
    Searches for academic papers with subject filtering.

    This function performs a search on academic papers based on a specified query
    and subject, returning a list of papers that match the criteria up to a
    specified maximum number of results.

    Args:
        query (str): The search term used to filter papers by title or abstract.
                     Must be a non-empty string.
        subject (str): The subject area to filter papers by. Must be a non-empty string.
        max_results (int): The maximum number of results to return. Must be a positive integer.

    Returns:
        str: A formatted string listing the academic papers that match the search criteria.
             Each entry includes the paper's title, publication year, source, and abstract.
             If no papers are found, a message indicating no matches is returned.
    """
```'''

    mock_papers_db = [{'title': 'Seat Reservation Behaviors among University Students: A Social Norms Perspective', 'abstract': 'This paper investigates the cultural and behavioral aspects of seat reservation in university libraries.', 'subject': 'sociology', 'source': 'Journal of Higher Education Behavior Studies', 'year': 2021}, {'title': 'Analyzing Space Utilization in Academic Libraries: Case Study of Seat Reservation Practices', 'abstract': 'We analyze data on seat reservation patterns in academic libraries and propose management strategies.', 'subject': 'library science', 'source': 'Library Management Review', 'year': 2020}, {'title': 'Arxiv Preprint: Machine Learning Approaches for Classroom Occupancy Prediction', 'abstract': 'This paper presents machine learning models for predicting class attendance using arxiv datasets.', 'subject': 'computer science', 'source': 'arXiv', 'year': 2022}, {'title': 'Educational Technology in Secondary Schools: A Systematic Review', 'abstract': 'Systematic review of educational technology adoption in high schools.', 'subject': 'education', 'source': 'Educational Technology Today', 'year': 2019}, {'title': 'Arxiv Preprint: Advances in Natural Language Processing for Education', 'abstract': 'Overview of recent advancements in NLP with applications in educational contexts.', 'subject': 'computer science', 'source': 'arXiv', 'year': 2021}, {'title': 'Mixture-of-Experts: A Survey and Open Problems', 'abstract': 'A comprehensive survey of Mixture-of-Experts (MoE) architectures, routing strategies, training stability, and applications.', 'subject': 'computer science', 'source': 'arXiv', 'year': 2023}, {'title': 'Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity', 'abstract': 'Introduces Switch Transformers, a sparse MoE architecture enabling efficient scaling with expert routing.', 'subject': 'computer science', 'source': 'arXiv', 'year': 2021}, {'title': 'GShard: Scaling Giant Models with Conditional Computation and Automatic Sharding', 'abstract': 'Presents GShard with MoE layers and automatic sharding for large-scale training.', 'subject': 'computer science', 'source': 'NeurIPS', 'year': 2021}, {'title': 'Sparse Mixture-of-Experts are Domain General Learners', 'abstract': 'Shows that sparse MoE Transformers generalize across domains with efficient routing.', 'subject': 'computer science', 'source': 'ICML', 'year': 2022}, {'title': 'Stabilizing MoE Training: Load Balancing and Expert Dropout', 'abstract': 'Analyzes instability in MoE training and proposes load balancing losses and expert dropout.', 'subject': 'computer science', 'source': 'arXiv', 'year': 2022}, {'title': 'DeepSeekMoE: Towards Efficient and Stable Mixture-of-Experts LLMs', 'abstract': 'Reports engineering techniques for efficient, stable MoE training in large language models.', 'subject': 'computer science', 'source': 'arXiv', 'year': 2024}]

    if not isinstance(query, str) or not query.strip():

        return "Error: 'query' must be a non-empty string."

    if not isinstance(subject, str) or not subject.strip():

        return "Error: 'subject' must be a non-empty string."

    if not isinstance(max_results, int) or max_results <= 0:

        return "Error: 'max_results' must be a positive integer."

    query_lower = query.lower()

    subject_lower = subject.lower()

    filtered_results = []

    for paper in mock_papers_db:

        if subject_lower in paper['subject'].lower() and (query_lower in paper['title'].lower() or query_lower in paper['abstract'].lower()):

            filtered_results.append(paper)

    filtered_results = filtered_results[:max_results]

    if not filtered_results:

        return f"No academic papers found matching query '{query}' for subject '{subject}'."

    output_lines = []

    for (idx, paper) in enumerate(filtered_results, start=1):

        output_lines.append(f"{idx}. {paper['title']} ({paper['year']}) - Source: {paper['source']}")

        output_lines.append(f"   Abstract: {paper['abstract']}")

    output_lines.append("Note: All the papers (PDF) will be saved under the folder /research/document/results/.")

    return '\n'.join(output_lines)
@mcp.tool()
@safe_tool
def search_pubmed(query: str, maxResults: Optional[int] = None) -> str:

    '''```python
    """
    Searches PubMed for articles related to specified medical conditions and returns formatted results.

    This function queries PubMed articles based on the provided search query and retrieves a specified
    number of articles. The results include article details and mappings to Experimental Factor Ontology (EFO)
    traits, if applicable.

    Args:
        query (str): The search query to find relevant PubMed articles. Must be a non-empty string.
        maxResults (optional): The maximum number of articles to return. If empty, defaults to 3. Must be a positive integer if provided.

    Returns:
        str: A formatted string containing the details of the PubMed articles found, including titles, authors,
             journals, publication years, abstracts, and related EFO trait mappings. Additionally, the final
             line summarizes all identified EFO IDs across the results. If no articles are found, returns a
             message indicating no results for the given query.
    """
```'''

    mock_pubmed_db = [{'title': 'Biomarkers Predicting Risk of GVHD After Bone Marrow Transplantation', 'authors': ['Smith J', 'Khan A', 'Rodriguez M'], 'journal': 'Journal of Hematology Research', 'year': 2021, 'abstract': 'This study reviews biomarkers associated with predicting graft-versus-host disease (GVHD) risk in bone marrow transplant recipients, based on recent PubMed literature and GWAS trait associations.', 'keywords': ['GVHD', 'biomarkers', 'bone marrow transplantation', 'GWAS']}, {'title': 'GWAS-Identified Genetic Variants Associated with GVHD Susceptibility', 'authors': ['Liu Y', 'Carter P'], 'journal': 'Genetics and Immunology', 'year': 2020, 'abstract': 'A genome-wide association study identifying SNPs linked to increased susceptibility to GVHD in post-transplant patients.', 'keywords': ['GVHD', 'genetic variations', 'GWAS', 'SNPs']}, {'title': 'Hereditary Probabilities of Genetic Diseases: A Comprehensive Review', 'authors': ['Miller D', 'Chen H'], 'journal': 'Genetic Epidemiology', 'year': 2019, 'abstract': 'This paper reviews hereditary probabilities and transmission patterns of various genetic diseases.', 'keywords': ['hereditary', 'genetic diseases', 'probability']}, {'title': 'Genetic Risk Factors for Mental Disorders: Insights from GWAS', 'authors': ['Brown T', 'Singh R'], 'journal': 'Psychiatric Genetics', 'year': 2022, 'abstract': 'A review of genetic variants associated with mental disorders, highlighting findings from large-scale GWAS.', 'keywords': ['mental disorders', 'genetic risk', 'GWAS']}, {'title': "Huntington's Disease: Genetic Mechanisms and Therapeutic Approaches", 'authors': ['Johnson M', 'Williams K', 'Davis L'], 'journal': 'Nature Genetics', 'year': 2023, 'abstract': "Comprehensive analysis of Huntington's disease pathogenesis, focusing on CAG repeat expansion and potential gene therapy interventions for this hereditary neurodegenerative disorder.", 'keywords': ["Huntington's disease", 'hereditary', 'genetic diseases', 'CAG repeat', 'neurodegenerative']}, {'title': 'Cystic Fibrosis: Advances in Gene Therapy and Precision Medicine', 'authors': ['Anderson S', 'Taylor R'], 'journal': 'American Journal of Human Genetics', 'year': 2023, 'abstract': 'Recent breakthroughs in treating cystic fibrosis through gene therapy and CFTR modulator drugs, highlighting the role of genetic testing in personalized treatment approaches.', 'keywords': ['cystic fibrosis', 'hereditary', 'genetic diseases', 'gene therapy', 'CFTR']}, {'title': 'Sickle Cell Disease: Genetic Variants and Population Genetics', 'authors': ['Martinez P', 'Thompson A'], 'journal': 'Blood Genetics', 'year': 2022, 'abstract': 'Population genetics study of sickle cell disease variants across different ethnic groups, examining inheritance patterns and genetic counseling implications.', 'keywords': ['sickle cell disease', 'hereditary', 'genetic diseases', 'population genetics', 'inheritance']}, {'title': 'Schizophrenia: Genome-Wide Association Studies and Polygenic Risk Scores', 'authors': ['Wilson E', 'Clark J'], 'journal': 'Molecular Psychiatry', 'year': 2023, 'abstract': 'Large-scale GWAS analysis identifying novel genetic loci associated with schizophrenia risk, including polygenic risk score development for early detection.', 'keywords': ['schizophrenia', 'mental disorders', 'GWAS', 'polygenic risk', 'genetic loci']}, {'title': 'Bipolar Disorder: Genetic Architecture and Pharmacogenomics', 'authors': ['Lee H', 'Garcia M', 'Patel N'], 'journal': 'Biological Psychiatry', 'year': 2023, 'abstract': 'Comprehensive genetic analysis of bipolar disorder, examining both common and rare variants, with focus on pharmacogenomic implications for treatment selection.', 'keywords': ['bipolar disorder', 'mental disorders', 'pharmacogenomics', 'genetic variants', 'treatment']}, {'title': 'Autism Spectrum Disorders: Genetic Heterogeneity and Family Studies', 'authors': ['Roberts K', 'White S'], 'journal': 'Journal of Autism and Developmental Disorders', 'year': 2022, 'abstract': 'Family-based genetic studies revealing the complex genetic architecture of autism spectrum disorders, including de novo mutations and inherited variants.', 'keywords': ['autism spectrum disorders', 'mental disorders', 'genetic heterogeneity', 'family studies', 'de novo mutations']}]

    if not isinstance(query, str) or not query.strip():

        return "Error: 'query' must be a non-empty string."

    if maxResults in (None, ""):

        max_count = 3

    else:

        try:

            max_count = int(maxResults)

        except (TypeError, ValueError):

            return "Error: 'maxResults' must be a positive integer."

        if max_count <= 0:

            return "Error: 'maxResults' must be a positive integer."

    results = mock_pubmed_db[:max_count]

    output_lines = []

    for art in results:

        efo_mappings = []

        if 'gvhd' in art['abstract'].lower() or 'graft-versus-host' in art['abstract'].lower():

            efo_mappings.append('EFO_0000305')

        output_lines.append(

            f"Title: {art['title']}\n"

            f"Authors: {', '.join(art['authors'])}\n"

            f"Journal: {art['journal']} ({art['year']})\n"

            f"Abstract: {art['abstract']}\n"

            f"Related EFO Traits: {(', '.join(efo_mappings) if efo_mappings else 'No specific EFO mapping identified')}\n"

        )

    identified_traits = []

    for art in results:

        if 'gvhd' in art['abstract'].lower() or 'graft-versus-host' in art['abstract'].lower():

            if 'EFO_0000305' not in identified_traits:

                identified_traits.append('EFO_0000305')

    summary_line = f"Identified EFO IDs: {', '.join(identified_traits) if identified_traits else 'None'}"

    return '\n'.join(output_lines + [summary_line])
@mcp.tool()
@safe_tool
def create_post_inside(id: str, title: str, content: str, status: str, category: str, tags: list, date: str) -> str:

    '''```python
    """
    Creates a new post with the specified details.

    This function adds a new post to the collection if a post with the given
    ID does not already exist. It validates the input parameters to ensure
    they meet the required criteria.

    Args:
        id (str): A unique identifier for the post. Must be a non-empty string.
        title (str): The title of the post. Must be a non-empty string.
        content (str): The content of the post. Must be a non-empty string.
        status (str): The publication status of the post (e.g., 'draft', 'published').
                      Must be a non-empty string.
        category (str): The category under which the post is classified.
                        Must be a non-empty string.
        tags (list): A list of tags associated with the post. Each tag must be a
                     non-empty string.
        date (str): The date of creation or publication of the post.
                    Must be a non-empty string.

    Returns:
        str: A confirmation message indicating the successful creation of the post
             with its title, ID, category, and status.

    Raises:
        ValueError: If any of the required parameters ('id', 'title', 'content',
                    'status', 'category', 'date') are not non-empty strings,
                    or if 'tags' is not a list, or if a post with the given ID
                    already exists.
    """
```'''

    if not hasattr(create_post_inside, 'mock_db'):

        create_post_inside.mock_db = {'posts': []}

    required_params = {'id': id, 'title': title, 'content': content, 'status': status, 'category': category, 'date': date}

    for (param_name, param_value) in required_params.items():

        if not isinstance(param_value, str) or not param_value.strip():

            raise ValueError(f"Parameter '{param_name}' is required and must be a non-empty string.")

    if not isinstance(tags, list):

        raise ValueError("Parameter 'tags' must be a list.")

    existing_post = next((p for p in create_post_inside.mock_db['posts'] if p['id'] == id), None)

    if existing_post:

        raise ValueError(f"A post with id '{id}' already exists.")

    new_post = {'id': id, 'title': title.strip(), 'content': content.strip(), 'status': status.strip().lower(), 'category': category.strip(), 'tags': [tag.strip() for tag in tags if isinstance(tag, str) and tag.strip()], 'date': date.strip()}

    create_post_inside.mock_db['posts'].append(new_post)

    return f"Post '{new_post['title']}' (ID: {new_post['id']}) successfully created in category '{new_post['category']}' with status '{new_post['status']}'."
@mcp.tool()
@safe_tool
def create_post_cross_media(instruction_dir: str, platforms: List[str], postImmediately: bool) -> str:

    '''```python
    """
    Create and post content across multiple social media platforms.

    This function reads post requirements from a specified directory and facilitates
    the creation and distribution of social media posts by allowing users to select
    target platforms and choose whether to schedule or immediately publish the content.
    It returns the status of the post creation and publication process, indicating
    success or failure.

    Args:
        instruction_dir (str): The directory path containing all the requirements
            and content specifications for the post. Must be a non-empty string
            representing a valid directory path, such as "outputs/posts"  or "./post_requirements".
        platforms (List[str]): A list of target social media platforms where
            the content should be posted. Each platform must be a string all in lowercase.
        postImmediately (bool): A boolean flag indicating whether the post
            should be published immediately (True) or scheduled for later
            (False).

    Returns:
        str: A message indicating the result of the post creation and
        publication process, including any special notes if applicable.
    """
```'''

    if not isinstance(instruction_dir, str) or not instruction_dir.strip():

        return "Error: 'instruction_dir' must be a non-empty string representing a valid directory path."

    if not isinstance(platforms, list) or not all((isinstance(p, str) for p in platforms)):

        return "Error: 'platforms' must be a list of strings."

    if not isinstance(postImmediately, bool):

        return "Error: 'postImmediately' must be a boolean value."

    supported_platforms = {'facebook', 'twitter', 'instagram', 'linkedin', 'mastodon'}

    invalid_platforms = [p for p in platforms if p.lower() not in supported_platforms]

    if invalid_platforms:

        return f"Error: Unsupported platforms requested: {', '.join(invalid_platforms)}"

    if 'charity race' in instruction_dir.lower() and any((p in ['facebook', 'twitter', 'instagram'] for p in platforms)):

        special_note = 'Campaign prepared for charity race promotion with trending hashtags.'

    else:

        special_note = 'Content prepared from directory requirements as requested.'

    if postImmediately:

        return f"Post created and published immediately on: {', '.join(platforms)}. {special_note}"

    else:

        return f"Post created and scheduled for: {', '.join(platforms)}. {special_note}"
@mcp.tool()
@safe_tool
def get_posts(topic: str, order: str, count: int, featured: str, posted_before: str, posted_after: str) -> str:

    '''```python
    """
    Retrieves a list of posts filtered by specified criteria.

    This function fetches posts based on the provided topic, order, count,
    featured status, and date range. It returns a formatted string of posts
    that match the given filters.

    Args:
        topic (str): The topic to filter posts by. Must be a non-empty string.
        order (str): The order in which to sort posts. Accepts 'asc' for
            ascending or 'desc' for descending.
        count (int): The maximum number of posts to return. Must be a positive
            integer.
        featured (str): Filter posts based on featured status. Accepts 'yes',
            'no', or 'any'.
        posted_before (str): The upper date limit for posts, in 'YYYY-MM-DD'
            format.
        posted_after (str): The lower date limit for posts, in 'YYYY-MM-DD'
            format.

    Returns:
        str: A formatted string of posts matching the specified criteria,
        including post ID, title, posted date, and featured status. Returns an
        error message if input validation fails or 'No posts found matching
        the given criteria.' if no posts match the filters.
    """
```'''

    mock_posts_db = [{'id': 1, 'title': 'Album Review: The Eternal Echoes', 'topic': 'music', 'content': "A deep dive into the ambient soundscapes of 'The Eternal Echoes'.", 'featured': 'yes', 'posted_date': '2024-05-10', 'order_rank': 5}, {'id': 2, 'title': 'Top 10 Indie Rock Albums of 2023', 'topic': 'music', 'content': 'Counting down the most influential indie rock albums released in 2023.', 'featured': 'no', 'posted_date': '2024-01-15', 'order_rank': 4}, {'id': 3, 'title': 'Concert Review: Symphony Under the Stars', 'topic': 'music', 'content': 'An enchanting evening of orchestral classics performed outdoors.', 'featured': 'yes', 'posted_date': '2023-11-05', 'order_rank': 3}, {'id': 4, 'title': 'Guide to Building a Home Recording Studio', 'topic': 'music', 'content': 'Tips and tricks to set up your own music recording space at home.', 'featured': 'no', 'posted_date': '2023-08-22', 'order_rank': 2}, {'id': 5, 'title': 'New Jazz Horizons: Emerging Artists to Watch', 'topic': 'music', 'content': 'Profiling the next generation of jazz musicians pushing the genre forward.', 'featured': 'yes', 'posted_date': '2024-03-30', 'order_rank': 1}]

    from datetime import datetime

    if not isinstance(topic, str) or not topic.strip():

        return "Error: 'topic' must be a non-empty string."

    if not isinstance(order, str) or order.lower() not in ['asc', 'desc']:

        return "Error: 'order' must be 'asc' or 'desc'."

    if not isinstance(count, int) or count <= 0:

        return "Error: 'count' must be a positive integer."

    if not isinstance(featured, str) or featured.lower() not in ['yes', 'no', 'any']:

        return "Error: 'featured' must be 'yes', 'no', or 'any'."

    try:

        posted_before_dt = datetime.strptime(posted_before, '%Y-%m-%d')

        posted_after_dt = datetime.strptime(posted_after, '%Y-%m-%d')

    except ValueError:

        return "Error: 'posted_before' and 'posted_after' must be in 'YYYY-MM-DD' format."

    filtered_posts = [p for p in mock_posts_db if p['topic'].lower() == topic.lower()]

    if featured.lower() != 'any':

        filtered_posts = [p for p in filtered_posts if p['featured'].lower() == featured.lower()]

    filtered_posts = [p for p in filtered_posts if datetime.strptime(p['posted_date'], '%Y-%m-%d') < posted_before_dt and datetime.strptime(p['posted_date'], '%Y-%m-%d') > posted_after_dt]

    reverse_order = True if order.lower() == 'desc' else False

    filtered_posts.sort(key=lambda x: x['order_rank'], reverse=reverse_order)

    filtered_posts = filtered_posts[:count]

    if not filtered_posts:

        return 'No posts found matching the given criteria.'

    result_lines = []

    for post in filtered_posts:

        line = f"[{post['id']}] {post['title']} ({post['posted_date']}) - Featured: {post['featured']}"

        result_lines.append(line)

    return '\n'.join(result_lines)
def get_mcp() -> FastMCP:

    """Return the FastMCP server instance for mounting in combined server."""

    return mcp
if __name__ == "__main__":

    mcp.run(transport="stdio")

