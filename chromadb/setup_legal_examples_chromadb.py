

"""
Setup script to populate ChromaDB with legal query examples and embeddings.
This script:
1. Parses the juristische_anfragen_v2.md file
2. Generates embeddings using Azure OpenAI (credentials from SecretManager/mnt files)
3. Inserts documents into ChromaDB Cloud
Usage:
    # Set ChromaDB credentials in agenttim/.env:
    # CHROMA_API_KEY=...
    # CHROMA_TENANT=...

    # Run the script:
    python scripts/setup_legal_examples_chromadb.py

    # Or with poetry:
    poetry run python scripts/setup_legal_examples_chromadb.py
"""
import asyncio
import json
import os
import re
import sys
from pathlib import Path
from typing import Any
import chromadb
from dotenv import load_dotenv
from langchain_openai import AzureOpenAIEmbeddings
sys.path.insert(0, str(Path(__file__).parent.parent))
ENV_FILE = Path(__file__).parent.parent / ".env.local"
load_dotenv(ENV_FILE)
import shared.config.constants as constants
from agenttim.config.settings import get_settings
from agenttim.config.secret_manager_dependency import get_secret_manager
COLLECTION_NAME = "legal_query_examples"
EMBEDDING_MODEL = "text-embedding-3-large"
CHROMA_CLOUD_HOST = os.getenv("CHROMA_CLOUD_HOST", "europe-west1.gcp.trychroma.com")
CHROMA_CLOUD_PORT = int(os.getenv("CHROMA_CLOUD_PORT", "443"))
CHROMA_API_KEY = os.getenv("CHROMA_API_KEY")
CHROMA_TENANT = os.getenv("CHROMA_TENANT")
CHROMA_DATABASE = os.getenv("CHROMA_DATABASE", "agent_embeddings")
MARKDOWN_FILE = Path(__file__).parent.parent / "docs" / "juristische_anfragen_v2.md"
INTENT_MAPPINGS: dict[int, dict[str, Any]] = {

    1: {"metrics": ["count"], "dimensions": ["deadlineType"], "filters": {"deadline": "this_week"}, "primary_collection": "DeadlinesFull", "secondary_collections": [], "time_range": "this_week", "time_field_hint": "end", "interpretation": "Deadlines expiring this week by type"},

    2: {"metrics": ["count"], "dimensions": ["assignee", "deadlineType"], "filters": {"deadlineStatus": "overdue"}, "primary_collection": "DeadlinesFull", "secondary_collections": ["CasesFull"], "time_range": "last_12_months", "time_field_hint": "end", "interpretation": "Overdue deadlines in past 12 months by assignee and type"},

    3: {"metrics": ["count"], "dimensions": [], "filters": {"deadline": "next_14_days", "hasPreclusion": True}, "primary_collection": "DeadlinesFull", "secondary_collections": [], "time_range": "next_14_days", "time_field_hint": "end", "interpretation": "Upcoming deadlines with preclusion risk in next 14 days"},

    4: {"metrics": ["avg"], "dimensions": ["caseType"], "filters": {}, "primary_collection": "DeadlinesFull", "secondary_collections": ["TasksFull"], "time_range": None, "time_field_hint": "completeDate", "interpretation": "Average processing time between deadline receipt and completion by case type"},

    5: {"metrics": ["count"], "dimensions": [], "filters": {"deadlineType": "statutory", "deadline": "next_7_days"}, "primary_collection": "DeadlinesFull", "secondary_collections": [], "time_range": "next_7_days", "time_field_hint": "end", "interpretation": "Statutory deadlines (ZPO) expiring in next 7 business days"},

    6: {"metrics": ["avg"], "dimensions": ["department"], "filters": {}, "primary_collection": "DeadlinesFull", "secondary_collections": [], "time_range": None, "time_field_hint": None, "interpretation": "Deadline compliance rates comparison by department"},

    7: {"metrics": ["count", "ratio"], "dimensions": [], "filters": {"extensionRequested": True}, "primary_collection": "DeadlinesFull", "secondary_collections": [], "time_range": "last_6_months", "time_field_hint": "lastModifiedDate", "interpretation": "Extension requests in past 6 months with success rate"},

    8: {"metrics": ["count"], "dimensions": ["dayOfWeek", "department"], "filters": {}, "primary_collection": "DeadlinesFull", "secondary_collections": [], "time_range": None, "time_field_hint": "end", "interpretation": "Deadline distribution by weekday and department"},

    9: {"metrics": ["count"], "dimensions": ["caseId"], "filters": {"openDeadlineCount": ">3"}, "primary_collection": "CasesFull", "secondary_collections": ["DeadlinesFull"], "time_range": None, "time_field_hint": None, "interpretation": "Cases with more than 3 parallel open deadlines"},

    10: {"metrics": ["correlation"], "dimensions": ["assignee"], "filters": {"deadlineStatus": "missed"}, "primary_collection": "DeadlinesFull", "secondary_collections": ["CasesFull"], "time_range": None, "time_field_hint": None, "interpretation": "Correlation between missed deadlines and concurrent case load per assignee"},

    11: {"metrics": ["count"], "dimensions": ["outcome"], "filters": {"reinstatementRequested": True}, "primary_collection": "CasesFull", "secondary_collections": [], "time_range": "last_24_months", "time_field_hint": "createdAt", "interpretation": "Reinstatement requests in past 24 months with outcomes"},

    12: {"metrics": ["avg"], "dimensions": [], "filters": {}, "primary_collection": "DeadlinesFull", "secondary_collections": ["TasksFull"], "time_range": None, "time_field_hint": "completeDate", "interpretation": "Average days before deadline when work is completed"},

    13: {"metrics": ["count"], "dimensions": ["urgencyLevel"], "filters": {"deadline": "today"}, "primary_collection": "DeadlinesFull", "secondary_collections": [], "time_range": "today", "time_field_hint": "end", "interpretation": "Deadlines due today by urgency level with preclusion risk"},

    14: {"metrics": ["count"], "dimensions": ["year", "legalArea"], "filters": {}, "primary_collection": "DeadlinesFull", "secondary_collections": [], "time_range": "yearly_comparison", "time_field_hint": "end", "interpretation": "Deadline volume trend year-over-year by legal area"},

    15: {"metrics": ["avg"], "dimensions": ["court"], "filters": {}, "primary_collection": "DeadlinesFull", "secondary_collections": [], "time_range": "last_18_months", "time_field_hint": None, "interpretation": "Courts with shortest response deadlines in past 18 months"},

    16: {"metrics": ["forecast"], "dimensions": ["week"], "filters": {}, "primary_collection": "DeadlinesFull", "secondary_collections": [], "time_range": "next_4_weeks", "time_field_hint": "end", "interpretation": "Deadline volume forecast for next 4 weeks with seasonal adjustment"},

    17: {"metrics": ["count"], "dimensions": [], "filters": {"deadlineType": ["appeal", "revision"]}, "primary_collection": "DeadlinesFull", "secondary_collections": ["CasesFull"], "time_range": None, "time_field_hint": None, "interpretation": "Currently running appeal and revision deadlines"},

    18: {"metrics": ["ratio"], "dimensions": ["procedureType"], "filters": {}, "primary_collection": "DeadlinesFull", "secondary_collections": [], "time_range": None, "time_field_hint": None, "interpretation": "Ratio of court-set vs statutory deadlines by procedure type"},

    19: {"metrics": ["count"], "dimensions": ["caseId"], "filters": {"deadlineDensity": ">threshold"}, "primary_collection": "CasesFull", "secondary_collections": ["DeadlinesFull"], "time_range": None, "time_field_hint": None, "interpretation": "Cases with above-average deadline density requiring prioritization"},

    20: {"metrics": ["count"], "dimensions": ["client", "caseId"], "filters": {"deadline": "next_30_days"}, "primary_collection": "DeadlinesFull", "secondary_collections": ["CasesFull"], "time_range": "next_30_days", "time_field_hint": "end", "interpretation": "All deadline-bound actions in next 30 days by client and case"},

    21: {"metrics": ["count"], "dimensions": ["legalArea", "disputeValueRange"], "filters": {"createdAt": "this_quarter"}, "primary_collection": "CasesFull", "secondary_collections": [], "time_range": "this_quarter", "time_field_hint": "created", "interpretation": "New cases this quarter by legal area and dispute value"},

    22: {"metrics": ["count"], "dimensions": ["year", "caseType"], "filters": {}, "primary_collection": "CasesFull", "secondary_collections": [], "time_range": "last_5_years", "time_field_hint": "created", "interpretation": "Case inventory development over past 5 years by type"},

    23: {"metrics": ["count"], "dimensions": [], "filters": {"lastUpdate": "<6months"}, "primary_collection": "CasesFull", "secondary_collections": [], "time_range": None, "time_field_hint": "lastModified", "interpretation": "Cases without status update for more than 6 months"},

    24: {"metrics": ["avg"], "dimensions": ["instance", "jurisdiction"], "filters": {}, "primary_collection": "CasesFull", "secondary_collections": [], "time_range": None, "time_field_hint": None, "interpretation": "Average case duration by instance and jurisdiction"},

    25: {"metrics": ["count"], "dimensions": ["stage"], "filters": {"disputeValue": ">500000"}, "primary_collection": "CasesFull", "secondary_collections": [], "time_range": None, "time_field_hint": None, "interpretation": "Cases with dispute value above 500k EUR by current stage"},

    26: {"metrics": ["count"], "dimensions": ["resolutionType"], "filters": {"closedAt": "last_12_months"}, "primary_collection": "CasesFull", "secondary_collections": [], "time_range": "last_12_months", "time_field_hint": "closedAt", "interpretation": "Case resolution types in past 12 months"},

    27: {"metrics": ["count"], "dimensions": [], "filters": {"disputeValueDiscrepancy": True}, "primary_collection": "CasesFull", "secondary_collections": [], "time_range": None, "time_field_hint": None, "interpretation": "Cases with discrepancy between original and final dispute value"},

    28: {"metrics": ["count", "sum"], "dimensions": ["client"], "filters": {}, "primary_collection": "CasesFull", "secondary_collections": [], "time_range": None, "time_field_hint": None, "interpretation": "Top 10 clients by case count with total dispute value"},

    29: {"metrics": ["count"], "dimensions": ["successProbability"], "filters": {"instance": ["appeal", "revision"]}, "primary_collection": "CasesFull", "secondary_collections": [], "time_range": None, "time_field_hint": None, "interpretation": "Cases in appeal/revision instance with success probability"},

    30: {"metrics": ["avg"], "dimensions": ["court"], "filters": {}, "primary_collection": "CasesFull", "secondary_collections": [], "time_range": None, "time_field_hint": None, "interpretation": "Case duration comparison across regional courts"},

    31: {"metrics": ["count"], "dimensions": ["dormancyReason"], "filters": {"status": "dormant"}, "primary_collection": "CasesFull", "secondary_collections": [], "time_range": "last_fiscal_year", "time_field_hint": None, "interpretation": "Cases marked dormant since last fiscal year with reasons"},

    32: {"metrics": ["completeness"], "dimensions": [], "filters": {}, "primary_collection": "CasesFull", "secondary_collections": ["DocumentsFull"], "time_range": None, "time_field_hint": None, "interpretation": "Case documentation completeness analysis"},

    33: {"metrics": ["count"], "dimensions": ["department"], "filters": {}, "primary_collection": "CasesFull", "secondary_collections": [], "time_range": None, "time_field_hint": None, "interpretation": "Case volume distribution by department and specialization"},

    34: {"metrics": ["count"], "dimensions": ["applicableLaw", "jurisdiction"], "filters": {"hasInternationalElement": True}, "primary_collection": "CasesFull", "secondary_collections": [], "time_range": None, "time_field_hint": None, "interpretation": "Cases with international elements by applicable law"},

    35: {"metrics": ["count"], "dimensions": ["caseId"], "filters": {"documentCount": ">threshold"}, "primary_collection": "CasesFull", "secondary_collections": ["DocumentsFull"], "time_range": None, "time_field_hint": None, "interpretation": "Litigation-intensive cases with above-average document count"},

    36: {"metrics": ["forecast"], "dimensions": ["quarter"], "filters": {}, "primary_collection": "CasesFull", "secondary_collections": [], "time_range": "next_quarter", "time_field_hint": None, "interpretation": "Forecast of case closures for next quarter"},

    37: {"metrics": ["count"], "dimensions": ["legalAidScope"], "filters": {"hasLegalAid": True}, "primary_collection": "CasesFull", "secondary_collections": [], "time_range": None, "time_field_hint": None, "interpretation": "Cases with legal aid granted by scope"},

    38: {"metrics": ["correlation"], "dimensions": ["disputeValueRange"], "filters": {}, "primary_collection": "CasesFull", "secondary_collections": [], "time_range": None, "time_field_hint": None, "interpretation": "Correlation between dispute value and case duration"},

    39: {"metrics": ["count"], "dimensions": ["errorType"], "filters": {"hasRetrial": True}, "primary_collection": "CasesFull", "secondary_collections": [], "time_range": None, "time_field_hint": None, "interpretation": "Retrial cases with identified procedural error types"},

    40: {"metrics": ["count"], "dimensions": [], "filters": {"lastStatusReport": "<90days"}, "primary_collection": "CasesFull", "secondary_collections": [], "time_range": None, "time_field_hint": "lastStatusReport", "interpretation": "Cases with status report older than 90 days"},

    41: {"metrics": ["count"], "dimensions": ["senderType", "caseId"], "filters": {"dateOfReceipt": "last_week"}, "primary_collection": "DocumentsFull", "secondary_collections": [], "time_range": "last_week", "time_field_hint": "dateOfReceiptSent", "interpretation": "Incoming briefs last week by sender type and case"},

    42: {"metrics": ["count"], "dimensions": ["documentType", "channel"], "filters": {}, "primary_collection": "DocumentsFull", "secondary_collections": [], "time_range": "this_year", "time_field_hint": "dateOfReceiptSent", "interpretation": "Document volume by type and channel over the year"},

    43: {"metrics": ["trend"], "dimensions": ["caseId"], "filters": {}, "primary_collection": "DocumentsFull", "secondary_collections": ["CasesFull"], "time_range": None, "time_field_hint": None, "interpretation": "Cases with increasing document frequency indicating intensification"},

    44: {"metrics": ["count"], "dimensions": ["evidenceType", "stage"], "filters": {"documentType": "evidenceRequest"}, "primary_collection": "DocumentsFull", "secondary_collections": [], "time_range": None, "time_field_hint": None, "interpretation": "Evidence requests by type and procedure stage"},

    45: {"metrics": ["count"], "dimensions": ["accessLevel"], "filters": {"isConfidential": True}, "primary_collection": "DocumentsFull", "secondary_collections": [], "time_range": None, "time_field_hint": None, "interpretation": "Confidential documents with access restrictions"},

    46: {"metrics": ["avg"], "dimensions": [], "filters": {}, "primary_collection": "DocumentsFull", "secondary_collections": ["TasksFull"], "time_range": None, "time_field_hint": None, "interpretation": "Average processing time between document receipt and review"},

    47: {"metrics": ["count"], "dimensions": ["caseId"], "filters": {"documentDensity": ">threshold"}, "primary_collection": "DocumentsFull", "secondary_collections": ["CasesFull"], "time_range": None, "time_field_hint": None, "interpretation": "Cases with above-average document density"},

    48: {"metrics": ["count"], "dimensions": [], "filters": {"ocrStatus": "failed"}, "primary_collection": "DocumentsFull", "secondary_collections": [], "time_range": None, "time_field_hint": None, "interpretation": "Documents with failed OCR requiring manual processing"},

    49: {"metrics": ["ratio"], "dimensions": ["stage"], "filters": {}, "primary_collection": "DocumentsFull", "secondary_collections": [], "time_range": None, "time_field_hint": None, "interpretation": "Ratio of incoming to outgoing briefs by procedure stage"},

    50: {"metrics": ["count"], "dimensions": ["decisionType"], "filters": {"documentType": ["judgment", "order", "ruling"]}, "primary_collection": "DocumentsFull", "secondary_collections": [], "time_range": "last_6_months", "time_field_hint": "dateOfReceiptSent", "interpretation": "Court decisions in past 6 months by type"},

    51: {"metrics": ["count"], "dimensions": ["expertType", "status"], "filters": {"documentType": "expertOpinion"}, "primary_collection": "DocumentsFull", "secondary_collections": ["CasesFull"], "time_range": None, "time_field_hint": None, "interpretation": "Expert opinions by type and completion status"},

    52: {"metrics": ["count"], "dimensions": [], "filters": {"retentionDate": "<threshold"}, "primary_collection": "DocumentsFull", "secondary_collections": [], "time_range": None, "time_field_hint": "retentionDate", "interpretation": "Documents approaching retention period deletion"},

    53: {"metrics": ["count"], "dimensions": ["caseType", "sequence"], "filters": {}, "primary_collection": "DocumentsFull", "secondary_collections": [], "time_range": None, "time_field_hint": None, "interpretation": "Typical document sequence by case type"},

    54: {"metrics": ["count"], "dimensions": ["client"], "filters": {}, "primary_collection": "DocumentsFull", "secondary_collections": [], "time_range": None, "time_field_hint": None, "interpretation": "Document volume comparison by client"},

    55: {"metrics": ["count"], "dimensions": ["caseId"], "filters": {"hasIncompleteAttachments": True}, "primary_collection": "DocumentsFull", "secondary_collections": [], "time_range": None, "time_field_hint": None, "interpretation": "Cases with missing or incomplete document attachments"},

    56: {"metrics": ["count"], "dimensions": ["court", "jurisdiction"], "filters": {"documentType": "correspondence"}, "primary_collection": "DocumentsFull", "secondary_collections": [], "time_range": None, "time_field_hint": None, "interpretation": "Court correspondence frequency by jurisdiction"},

    57: {"metrics": ["count"], "dimensions": ["documentId"], "filters": {"accessCount": ">1"}, "primary_collection": "DocumentsFull", "secondary_collections": [], "time_range": "last_30_days", "time_field_hint": None, "interpretation": "Frequently accessed documents in past 30 days"},

    58: {"metrics": ["count"], "dimensions": [], "filters": {"caseId": None}, "primary_collection": "DocumentsFull", "secondary_collections": [], "time_range": None, "time_field_hint": None, "interpretation": "Unassigned documents requiring manual classification"},

    59: {"metrics": ["count"], "dimensions": ["court", "caseId"], "filters": {"appointmentDate": "next_4_weeks"}, "primary_collection": "AppointmentsFull", "secondary_collections": [], "time_range": "next_4_weeks", "time_field_hint": "startDateTime", "interpretation": "Court appointments in next 4 weeks by court and case"},

    60: {"metrics": ["count"], "dimensions": ["dayOfWeek"], "filters": {}, "primary_collection": "AppointmentsFull", "secondary_collections": [], "time_range": None, "time_field_hint": "startDateTime", "interpretation": "Appointment concentration by weekday to identify capacity bottlenecks"},

    61: {"metrics": ["count"], "dimensions": [], "filters": {"hasConflict": True}, "primary_collection": "AppointmentsFull", "secondary_collections": [], "time_range": None, "time_field_hint": None, "interpretation": "Cases with appointment conflicts requiring rescheduling"},

    62: {"metrics": ["forecast"], "dimensions": ["quarter"], "filters": {}, "primary_collection": "AppointmentsFull", "secondary_collections": ["CasesFull"], "time_range": "next_quarter", "time_field_hint": "startDateTime", "interpretation": "Appointment volume forecast for next quarter"},

    63: {"metrics": ["count"], "dimensions": ["postponementReason"], "filters": {"wasPostponed": True}, "primary_collection": "AppointmentsFull", "secondary_collections": [], "time_range": "last_6_months", "time_field_hint": None, "interpretation": "Postponed appointments in past 6 months with reasons"},

    64: {"metrics": ["avg"], "dimensions": ["caseType", "instance"], "filters": {}, "primary_collection": "AppointmentsFull", "secondary_collections": [], "time_range": None, "time_field_hint": None, "interpretation": "Average hearing duration by case type and instance"},

    65: {"metrics": ["avg"], "dimensions": ["court"], "filters": {}, "primary_collection": "AppointmentsFull", "secondary_collections": [], "time_range": None, "time_field_hint": None, "interpretation": "Courts with longest scheduling-to-hearing wait times"},

    66: {"metrics": ["count"], "dimensions": [], "filters": {"requiresClientPresence": True}, "primary_collection": "AppointmentsFull", "secondary_collections": [], "time_range": None, "time_field_hint": "startDateTime", "interpretation": "Appointments requiring client personal appearance"},

    67: {"metrics": ["count"], "dimensions": [], "filters": {"isVideoHearing": True}, "primary_collection": "AppointmentsFull", "secondary_collections": [], "time_range": None, "time_field_hint": None, "interpretation": "Video hearings per section 128a ZPO scheduled"},

    68: {"metrics": ["count"], "dimensions": ["department"], "filters": {}, "primary_collection": "AppointmentsFull", "secondary_collections": [], "time_range": None, "time_field_hint": None, "interpretation": "Appointment frequency by department for workload assessment"},

    69: {"metrics": ["count"], "dimensions": ["evidenceType"], "filters": {"appointmentType": ["witness", "expert", "inspection"]}, "primary_collection": "AppointmentsFull", "secondary_collections": [], "time_range": "next_2_months", "time_field_hint": "startDateTime", "interpretation": "Evidence hearings in next 2 months by type"},

    70: {"metrics": ["count"], "dimensions": [], "filters": {"briefDeadlineOpen": True}, "primary_collection": "AppointmentsFull", "secondary_collections": ["DeadlinesFull"], "time_range": None, "time_field_hint": None, "interpretation": "Appointments with open brief submission deadlines"},

    71: {"metrics": ["count"], "dimensions": ["jurisdiction", "instance"], "filters": {"contactType": "court"}, "primary_collection": "ContactsFull", "secondary_collections": ["CasesFull"], "time_range": None, "time_field_hint": None, "interpretation": "Courts involved in active cases by jurisdiction and instance"},

    72: {"metrics": ["count"], "dimensions": ["lawFirm"], "filters": {"contactType": "opposingCounsel"}, "primary_collection": "ContactsFull", "secondary_collections": ["CasesFull"], "time_range": None, "time_field_hint": None, "interpretation": "Most frequent opposing counsel law firms"},

    73: {"metrics": ["count"], "dimensions": ["expertise"], "filters": {"contactType": "expert"}, "primary_collection": "ContactsFull", "secondary_collections": [], "time_range": "last_2_years", "time_field_hint": None, "interpretation": "Appointed experts in past 2 years by specialization"},

    74: {"metrics": ["count"], "dimensions": [], "filters": {"lastContact": "<6months", "contactType": "client"}, "primary_collection": "ContactsFull", "secondary_collections": [], "time_range": None, "time_field_hint": "lastContact", "interpretation": "Clients without communication in over 6 months"},

    75: {"metrics": ["count"], "dimensions": ["caseId", "interestAlignment"], "filters": {"participantType": "coLitigant"}, "primary_collection": "ParticipantsFull", "secondary_collections": ["CasesFull"], "time_range": None, "time_field_hint": None, "interpretation": "Co-litigants in multi-party cases with interest alignment"},

    76: {"metrics": ["ratio"], "dimensions": ["judge"], "filters": {}, "primary_collection": "CasesFull", "secondary_collections": [], "time_range": None, "time_field_hint": None, "interpretation": "Case outcomes comparison by judge to identify patterns"},

    77: {"metrics": ["count"], "dimensions": ["opposingCounsel"], "filters": {"contactType": "opposingCounsel"}, "primary_collection": "ContactsFull", "secondary_collections": [], "time_range": "last_18_months", "time_field_hint": None, "interpretation": "Most frequently mandated opposing counsel in past 18 months"},

    78: {"metrics": ["network"], "dimensions": ["client", "relatedEntity"], "filters": {}, "primary_collection": "ContactsFull", "secondary_collections": ["CasesFull"], "time_range": None, "time_field_hint": None, "interpretation": "Client network analysis with related entities and co-represented parties"},

    79: {"metrics": ["count"], "dimensions": ["intervenorInterest"], "filters": {"participantType": "intervenor"}, "primary_collection": "ParticipantsFull", "secondary_collections": ["CasesFull"], "time_range": None, "time_field_hint": None, "interpretation": "Third-party interventions with intervenor interests"},

    80: {"metrics": ["count"], "dimensions": ["authorityType"], "filters": {"contactType": "authority"}, "primary_collection": "ContactsFull", "secondary_collections": [], "time_range": None, "time_field_hint": None, "interpretation": "Public authorities and agencies in active correspondence"},

    81: {"metrics": ["count"], "dimensions": ["hearingStatus"], "filters": {"participantType": "witness"}, "primary_collection": "ParticipantsFull", "secondary_collections": [], "time_range": None, "time_field_hint": None, "interpretation": "Named witnesses with hearing status"},

    82: {"metrics": ["count"], "dimensions": ["companyType", "industry", "volume"], "filters": {"contactType": "client"}, "primary_collection": "ContactsFull", "secondary_collections": [], "time_range": None, "time_field_hint": None, "interpretation": "Client categorization by company type, industry, and case volume"},

    83: {"metrics": ["count"], "dimensions": ["priority", "dueDate"], "filters": {"status": "open"}, "primary_collection": "TasksFull", "secondary_collections": [], "time_range": None, "time_field_hint": "expiryDate", "interpretation": "Open tasks by priority level and due date"},

    84: {"metrics": ["ratio"], "dimensions": ["assignee"], "filters": {}, "primary_collection": "TasksFull", "secondary_collections": [], "time_range": None, "time_field_hint": None, "interpretation": "Task completion rate by assignee to identify bottlenecks"},

    85: {"metrics": ["count"], "dimensions": [], "filters": {"dueDate": "<today-14days", "status": "open"}, "primary_collection": "TasksFull", "secondary_collections": [], "time_range": None, "time_field_hint": "expiryDate", "interpretation": "Tasks overdue more than 14 days requiring escalation"},

    86: {"metrics": ["count"], "dimensions": [], "filters": {"taskType": "followUp", "dueDate": "next_7_days"}, "primary_collection": "TasksFull", "secondary_collections": [], "time_range": "next_7_days", "time_field_hint": "expiryDate", "interpretation": "Follow-up tasks due in next 7 days"},

    87: {"metrics": ["count"], "dimensions": ["dependencyType"], "filters": {"hasExternalDependency": True}, "primary_collection": "TasksFull", "secondary_collections": [], "time_range": None, "time_field_hint": None, "interpretation": "Tasks with external dependencies (client, court, expert)"},

    88: {"metrics": ["avg"], "dimensions": ["taskType"], "filters": {}, "primary_collection": "TasksFull", "secondary_collections": [], "time_range": None, "time_field_hint": None, "interpretation": "Average processing duration by task type"},

    89: {"metrics": ["count"], "dimensions": ["caseId"], "filters": {"taskDensity": ">threshold"}, "primary_collection": "TasksFull", "secondary_collections": ["CasesFull"], "time_range": None, "time_field_hint": None, "interpretation": "Cases with above-average task density for resource reallocation"},

    90: {"metrics": ["count"], "dimensions": ["delegationCount"], "filters": {"delegationCount": ">1"}, "primary_collection": "TasksFull", "secondary_collections": [], "time_range": None, "time_field_hint": None, "interpretation": "Tasks delegated multiple times with processing obstacles"},

    91: {"metrics": ["count"], "dimensions": ["senderType"], "filters": {"channel": "bea", "dateOfReceipt": "last_7_days"}, "primary_collection": "MessagesFull", "secondary_collections": [], "time_range": "last_7_days", "time_field_hint": "received", "interpretation": "Incoming beA messages in past 7 days by sender type"},

    92: {"metrics": ["count"], "dimensions": ["direction", "month"], "filters": {"channel": "bea"}, "primary_collection": "MessagesFull", "secondary_collections": [], "time_range": "this_year", "time_field_hint": "received", "interpretation": "beA message volume by direction over the year"},

    93: {"metrics": ["count"], "dimensions": [], "filters": {"channel": "bea", "status": "unprocessed"}, "primary_collection": "MessagesFull", "secondary_collections": [], "time_range": None, "time_field_hint": None, "interpretation": "Unprocessed beA messages requiring immediate attention"},

    94: {"metrics": ["count"], "dimensions": [], "filters": {"channel": "bea", "acknowledgmentPending": True}, "primary_collection": "MessagesFull", "secondary_collections": [], "time_range": None, "time_field_hint": None, "interpretation": "Pending electronic acknowledgments of receipt"},

    95: {"metrics": ["count"], "dimensions": ["errorType"], "filters": {"channel": "bea", "hasTransmissionError": True}, "primary_collection": "MessagesFull", "secondary_collections": [], "time_range": None, "time_field_hint": None, "interpretation": "beA transmissions with technical errors requiring retry"},

    96: {"metrics": ["count"], "dimensions": ["court"], "filters": {"channel": "bea"}, "primary_collection": "MessagesFull", "secondary_collections": [], "time_range": None, "time_field_hint": None, "interpretation": "beA communication frequency by court"},

    97: {"metrics": ["multiple"], "dimensions": ["quarter"], "filters": {}, "primary_collection": "DashboardCases", "secondary_collections": ["DashboardDeadlines", "DashboardTasks"], "time_range": "quarterly_comparison", "time_field_hint": None, "interpretation": "Consolidated KPIs (cases, duration, deadlines, completion rate) by quarter"},

    98: {"metrics": ["sum", "avg"], "dimensions": ["legalArea", "clientGroup", "caseType"], "filters": {}, "primary_collection": "CasesFull", "secondary_collections": [], "time_range": None, "time_field_hint": None, "interpretation": "Fee development by legal area, client group, and case type"},

    99: {"metrics": ["correlation"], "dimensions": ["complexity"], "filters": {}, "primary_collection": "CasesFull", "secondary_collections": ["DocumentsFull", "ParticipantsFull"], "time_range": None, "time_field_hint": None, "interpretation": "Correlation between case complexity and economic outcome"},

    100: {"metrics": ["trend", "forecast"], "dimensions": ["legalArea", "year"], "filters": {}, "primary_collection": "CasesFull", "secondary_collections": [], "time_range": "last_3_years", "time_field_hint": "created", "interpretation": "Legal area growth potential and trends based on 3-year intake data"},
}
CATEGORIES = {

    range(1, 21): "fristenmanagement",

    range(21, 41): "aktenmanagement",

    range(41, 59): "dokumentenmanagement",

    range(59, 71): "terminmanagement",

    range(71, 83): "kontakte",

    range(83, 91): "aufgaben",

    range(91, 97): "nachrichten",

    range(97, 101): "auswertungen",
}
def get_category(question_id: int) -> str:

    """Get category for a question ID."""

    for id_range, category in CATEGORIES.items():

        if question_id in id_range:

            return category

    return "unknown"
def parse_markdown_questions(markdown_path: Path) -> list[dict[str, Any]]:

    """Parse the markdown file and extract questions."""

    if not markdown_path.exists():

        raise FileNotFoundError(f"Markdown file not found: {markdown_path}")

    content = markdown_path.read_text(encoding="utf-8")

    pattern = r"### (\d+)\n(.+?)(?=\n###|\n---|\Z)"

    matches = re.findall(pattern, content, re.DOTALL)

    questions = []

    for match in matches:

        question_id = int(match[0])

        question_text = match[1].strip()

        if question_id < 1 or question_id > 100:

            continue

        intent_data = INTENT_MAPPINGS.get(question_id, {})

        questions.append({

            "id": question_id,

            "category": get_category(question_id),

            "german_query": question_text,

            "expected_intent": {

                "metrics": intent_data.get("metrics", ["count"]),

                "dimensions": intent_data.get("dimensions", []),

                "filters": intent_data.get("filters", {}),

                "time_range": intent_data.get("time_range"),

                "time_field_hint": intent_data.get("time_field_hint"),

                "domain_hints": [get_category(question_id)],

            },

            "interpretation": intent_data.get("interpretation", ""),

            "primary_collection": intent_data.get("primary_collection", "CasesFull"),

            "secondary_collections": intent_data.get("secondary_collections", []),

            "key_fields": intent_data.get("dimensions", []) + list(intent_data.get("filters", {}).keys()),

            "filter_mappings": intent_data.get("filters", {}),

        })

    return sorted(questions, key=lambda x: x["id"])
async def generate_embeddings(

    questions: list[dict[str, Any]],

    embeddings_client: AzureOpenAIEmbeddings,
) -> list[dict[str, Any]]:

    """Generate embeddings for all questions."""

    print(f"Generating embeddings for {len(questions)} questions...")

    documents = []

    for i, question in enumerate(questions):

        embedding = await embeddings_client.aembed_query(question["german_query"])

        doc = {

            **question,

            "embedding": embedding,

        }

        documents.append(doc)

        if (i + 1) % 10 == 0:

            print(f"  Processed {i + 1}/{len(questions)} questions...")

    print("Embedding generation complete.")

    return documents
def setup_chromadb(documents: list[dict[str, Any]]) -> None:

    """Setup ChromaDB Cloud collection with documents."""

    print(f"\nConnecting to ChromaDB Cloud ({CHROMA_CLOUD_HOST})...")

    client = chromadb.CloudClient(

        cloud_host=CHROMA_CLOUD_HOST,

        cloud_port=CHROMA_CLOUD_PORT,

        api_key=CHROMA_API_KEY,

        tenant=CHROMA_TENANT,

        database=CHROMA_DATABASE,

    )

    try:

        client.delete_collection(name=COLLECTION_NAME)

        print(f"Deleted existing collection '{COLLECTION_NAME}'")

    except ValueError:

        pass

    collection = client.create_collection(

        name=COLLECTION_NAME,

        metadata={"hnsw:space": "cosine"},

    )

    ids = [f"legal_example_{doc['id']}" for doc in documents]

    embeddings = [doc["embedding"] for doc in documents]

    documents_text = [doc["german_query"] for doc in documents]

    metadatas = []

    for doc in documents:

        metadata = {

            "id": doc["id"],

            "category": doc["category"],

            "interpretation": doc["interpretation"],

            "primary_collection": doc["primary_collection"],

            "secondary_collections": json.dumps(doc["secondary_collections"]),

            "expected_intent": json.dumps(doc["expected_intent"]),

            "key_fields": json.dumps(doc["key_fields"]),

            "filter_mappings": json.dumps(doc["filter_mappings"]),

        }

        metadatas.append(metadata)

    print(f"Inserting {len(documents)} documents into ChromaDB...")

    collection.add(

        ids=ids,

        embeddings=embeddings,

        documents=documents_text,

        metadatas=metadatas,

    )

    print(f"Setup complete. {collection.count()} documents in collection.")

    print("\nTo query this collection, generate embeddings with Azure OpenAI first:")

    print("  embedding = await embeddings_client.aembed_query('your query')")

    print("  results = collection.query(query_embeddings=[embedding], n_results=5)")
async def main():

    """Main setup function."""

    print("=" * 70)

    print("Legal Examples ChromaDB Setup")

    print("=" * 70)

    print(f"ENV_FILE: {ENV_FILE} (exists: {ENV_FILE.exists()})")

    print(f"CHROMA_CLOUD_HOST: {CHROMA_CLOUD_HOST}")

    print(f"CHROMA_TENANT: {CHROMA_TENANT}")

    print(f"CHROMA_DATABASE: {CHROMA_DATABASE}")

    print(f"CHROMA_API_KEY: {CHROMA_API_KEY[:10] if CHROMA_API_KEY else 'None'}...")

    if not CHROMA_API_KEY or not CHROMA_TENANT:

        print("ERROR: CHROMA_API_KEY and CHROMA_TENANT must be set in .env.local")

        sys.exit(1)

    print("\nLoading Azure OpenAI credentials from SecretManager...")

    secret_manager = get_secret_manager()

    settings = get_settings()

    azure_api_key = secret_manager.get_secret(

        constants.MNT_SHARED_DESCRIPTOR_KEY,

        constants.MNT_OPEN_AI_API_SWC_KEY

    )

    azure_endpoint = secret_manager.get_secret(

        constants.MNT_SHARED_DESCRIPTOR_KEY,

        constants.MNT_OPEN_AI_SWC_RESOURCE_ENDPOINT_CONFIG_KEY

    )

    if not azure_endpoint or not azure_api_key:

        print("ERROR: Could not load Azure OpenAI credentials from SecretManager")

        sys.exit(1)

    print(f"  Endpoint: {azure_endpoint[:50]}...")

    print(f"\nParsing questions from {MARKDOWN_FILE}...")

    questions = parse_markdown_questions(MARKDOWN_FILE)

    print(f"Found {len(questions)} questions")

    embeddings_client = AzureOpenAIEmbeddings(

        azure_endpoint=azure_endpoint,

        api_key=azure_api_key,

        model=EMBEDDING_MODEL,

    )

    documents = await generate_embeddings(questions, embeddings_client)

    setup_chromadb(documents)

    print("\n" + "=" * 70)

    print("Setup complete!")

    print(f"ChromaDB Cloud: {CHROMA_CLOUD_HOST} / {CHROMA_DATABASE}")

    print("=" * 70)
if __name__ == "__main__":

    asyncio.run(main())

