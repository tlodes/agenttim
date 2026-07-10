"""
Domain configuration for MCPAgentBench MCP servers.
Maps ~141 tools into 16 domain-specific MCP servers following Option A (1 Agent = 1 MCP Server).
Each domain groups semantically related tools that a specialized agent operates on.
"""
DOMAIN_TOOLS: dict[str, list[str]] = {

    "weather": [

        "weather_tool",

        "weather_data_retriever",

    ],

    "travel": [

        "search_flights",

        "booking_tool",

        "search_rental_properties",

        "get_rental_property_details",

        "search_ticketmaster",

    ],

    "calendar": [

        "create_event",

        "list_events",

        "find_free_slots",

        "create_task",

        "update_task",

    ],

    "dining": [

        "search_restaurant",

        "get_restaurant_details",

        "make_reservation",

        "search_recipes",

        "meshi_doko",

    ],

    "finance": [

        "get_balance",

        "send_transaction",

        "get_market_index",

        "get_market_summary",

        "get_realtime_market_data",

        "search_stock_byname",

        "get_stock_news",

        "get_markets",

    ],

    "health": [

        "get_health_recommendations",

        "get_patient_conditions",

        "get_patient_medications",

        "pharmacy_refill_request",

        "pet_vaccination_schedule",

        "indian_branded_drug_search",

        "Traditional_Chinese_medicine_consultation",

        "check_nutrition",

        "get_disease_targets_summary",

        "get_target_details",

        "get_trait_associations",

        "CafChem_ADME_calc_adme",

    ],

    "code": [

        "generate_code",

        "analyze_code",

        "execute_python_code",

        "Semgrep_Code_SAST",

        "patch_file",

        "search_and_read_files",

        "convert_pdf_to_markdown",

        "create_ui",

        "figma_export_code",

        "add_site",

        "stagehand_act",

        "stagehand_navigate",

    ],

    "entertainment": [

        "search_imdb",

        "get_directors",

        "itunes_search",

        "itunes_play_song",

        "recommend_musictracks",

        "get_players",

        "get_teams",

        "get_book_details_by_id",

        "diceRoll",

        "dmagent_ask_narrative",

        "dmagent_ask_rule",

        "strategy_guide",

    ],

    "media": [

        "AudioEditor_apply_fades",

        "AudioEditor_apply_speed_adjustment",

        "AudioEditor_apply_volume_adjustment",

        "AudioEditor_process_cut_audio",

        "AudioEditor_transcribe_audio_sync",

        "analyze_sound",

        "render_image",

        "create_design",

    ],

    "data": [

        "analyze_sales",

        "analyze_trends",

        "visualize_data",

        "execute_bigquery",

        "export_survey_responses",

        "generate_summary_report",

        "E_commerce_analyst_MCP_get_schemas",

        "get_comprehensive_analysis",

        "get_data_products",

        "spu_list",

    ],

    "geo": [

        "geocalc_mcp_get_points_of_interest",

        "findParks",

        "fetch_terrain_elevation",

        "download_osm_data",

        "find_earthquakes",

        "maps_direction_driving_by_address",

    ],

    "shopping": [

        "get_product_by_barcode",

        "recommend_electronics",

        "user_purchase_history",

        "grocery_pickup_slots",

        "get_best_price",

    ],

    "lifestyle": [

        "package_delivery_tracker",

        "pay_utility_bill",

        "public_transport_card_recharge",

        "laundry_service_request",

        "trash_collection_schedule",

        "community_pool_pass_renewal",

        "home_appliance_warranty_lookup",

        "home_energy_usage_report",

        "neighborhood_watch_alerts",

        "school_lunch_menu_lookup",

        "public_library_book_lookup",

        "child_homework_tracker",

    ],

    "content": [

        "search_news",

        "search_academic_papers",

        "search_pubmed",

        "create_post_inside",

        "create_post_cross_media",

        "get_posts",

    ],

    "simulation": [

        "create_object",

        "modify_object",

        "create_physics_scene",

        "create_robot",

        "generate_3d_assets",

        "get_scene_info",

        "detect_objects",

        "estimate_pose",

    ],

    "utilities": [

        "connect_database",

        "Connect_SQL_Server",

        "mongo_mcp",

        "get_secret",

        "get_time",

        "get_ip_details",

        "nmap_scan",

        "make_api_request",

        "request_api_schema",

        "searchApis",

        "vector_search",

        "wolfram_query",

        "WebSearchConfig",

        "security_guidance",

        "CountDown_StartAndEndDate",

        "create_comment",

        "orchestrator_plan_task",

        "Business_Analyst",

        "Developer",

        "Tester",

        "UIUX_Expert",

        "obtain_business_analysis",

        "system_architecture_designer",

        "octagon_companies_agent",

        "octagon_deepresearch_agent",

    ],
}
DOMAIN_DESCRIPTIONS: dict[str, str] = {

    "weather": "Weather forecasts, historical weather data, and meteorological queries",

    "travel": "Flight search, hotel booking, rental properties, and event tickets",

    "calendar": "Calendar events, task management, and scheduling",

    "dining": "Restaurant search, reservations, recipes, and food-related queries",

    "finance": "Banking, transactions, stock markets, and financial data",

    "health": "Medical records, health recommendations, pharmacy, drug lookup, and biomedical research",

    "code": "Code generation, analysis, execution, web development, and browser automation",

    "entertainment": "Movies, music, sports, books, and gaming",

    "media": "Audio editing, sound analysis, image rendering, and design",

    "data": "Sales analysis, trend analysis, data visualization, BigQuery, and reporting",

    "geo": "Geospatial queries, parks, elevation, maps, and earthquake data",

    "shopping": "Product lookup, electronics recommendations, purchase history, and grocery",

    "lifestyle": "Package tracking, utility bills, transport, home services, and community services",

    "content": "News search, academic papers, PubMed, and social media posts",

    "simulation": "3D objects, physics scenes, robots, object detection, and pose estimation",

    "utilities": "Database connections, API tools, network scanning, web search, and business analysis",
}
ALL_DOMAINS = list(DOMAIN_TOOLS.keys())
COARSE_AGENT_GROUPS: dict[str, dict] = {

    "daily_life": {

        "description": "Everyday tasks: weather, travel, calendar, dining, finance, shopping, lifestyle, health",

        "domains": ["weather", "travel", "calendar", "dining", "finance", "shopping", "lifestyle", "health"],

        "prompt": (

            "You are a Daily Life Assistant. You have tools for weather, travel, flights, hotels, "

            "calendar, restaurants, recipes, banking, stocks, shopping, package tracking, utility bills, "

            "home services, health, pharmacy, and pets. Read tool descriptions carefully, pick the "

            "right one, and return results directly."

        ),

    },

    "professional": {

        "description": "Technical/business tasks: code, data, geo, simulation, utilities",

        "domains": ["code", "data", "geo", "simulation", "utilities"],

        "prompt": (

            "You are a Professional Work Assistant. You have tools for code generation/analysis/execution, "

            "data analytics, BigQuery, visualization, geospatial queries, maps, 3D simulation, physics, "

            "databases, APIs, network scanning, web search, and business analysis. Read tool descriptions "

            "carefully, pick the right one, and return results directly."

        ),

    },

    "media": {

        "description": "Media/entertainment: entertainment, media, content",

        "domains": ["entertainment", "media", "content"],

        "prompt": (

            "You are a Media & Entertainment Assistant. You have tools for movies, music (iTunes), "

            "audio editing, image rendering, sports, books, gaming, news search, academic papers, "

            "and social media posting. Read tool descriptions carefully, pick the right one, and "

            "return results directly."

        ),

    },
}
def get_tool_to_domain_map() -> dict[str, str]:

    """Return a mapping from tool name to domain name."""

    result = {}

    for domain, tools in DOMAIN_TOOLS.items():

        for tool in tools:

            result[tool] = domain

    return result
BASE_PROMPT = """You are a professional AI assistant, designed to use the provided tools to accurately and efficiently solve users' problems.
Your task: Act according to the user's request, following a fixed thinking process and response format.
**Thinking Process & Response Format:**
1. **Thought:**
   - First, you must carefully analyze the user's needs and understand the core objective.
   - Formulate a clear, step-by-step plan to solve the problem, including selecting tools and their call parameters.
2. **Tool Invocation:**
   - After outputting the `Thought:` block, if you need to call tools, directly use the registered function tools.
   - The system will automatically handle your tool-call requests.
   - When the task is complete, provide the user with a concise, complete final answer, and do not include the `Thought:` prefix anymore.
**Constraints:**
- You must, and may only, choose tools from your available tools.
- Call the registered functions directly; do not output JSON or code-block descriptions.
**Key reminder:** If the task involves multiple steps (e.g., first search for restaurants, then make a reservation), you must complete all steps. Do not stop after completing only part of the task.
Now, please begin working based on the user's request. Be sure to include the `Thought:` section in your very first reply."""

