"""
MCPAgentBench Health MCP Server.
Concrete FastMCP server with 12 tools for the health domain.
Tools are copied from the original MCPAgentBench benchmark files
with their actual mock data implementations.
"""
from mcp.server.fastmcp import FastMCP
from typing import List
from typing import Literal
from agenttim.mcpservers.mcpagentbench.servers._error_handler import safe_tool
mcp = FastMCP("mcpbench-health")
@mcp.tool()
@safe_tool
def get_health_recommendations(age: str, sex: str, pregnancyStatus: str) -> str:

    '''```python
    """
    Get personalized health screening and preventive care recommendations.

    This function provides tailored health recommendations based on the
    individual's age, sex, and pregnancy status. It considers general
    vaccinations, healthy habits, age-specific screenings and vaccinations,
    sex-specific screenings, and pregnancy-specific recommendations.

    Args:
        age (str): The age of the individual as a string. Must be a numeric
            value (e.g., '30').
        sex (str): The sex of the individual. Accepted values are 'male' or
            'female'.
        pregnancyStatus (str): The pregnancy status of the individual.
            Accepted values are 'pregnant' or 'not_pregnant'.

    Returns:
        str: A formatted string containing personalized health recommendations
        based on the provided age, sex, and pregnancy status. If input
        validation fails, an error message is returned.
    """
```'''

    mock_health_db = {'general': {'vaccinations': ['Annual influenza vaccine', 'COVID-19 vaccine as per current guidelines', 'Tetanus-diphtheria booster every 10 years'], 'healthy_habits': ['Maintain a balanced diet rich in fruits, vegetables, and whole grains', 'Engage in at least 150 minutes of moderate-intensity exercise weekly', 'Avoid smoking and limit alcohol consumption']}, 'age_groups': {'child': {'screenings': ['Routine pediatric check-ups', 'Vision and hearing screening'], 'vaccinations': ['MMR (Measles, Mumps, Rubella) vaccine', 'Polio vaccine', 'Varicella (chickenpox) vaccine']}, 'adult': {'screenings': ['Blood pressure check every 1-2 years', 'Cholesterol screening every 4-6 years', 'Diabetes screening if overweight or with risk factors']}, 'senior': {'screenings': ['Bone density test for osteoporosis', 'Colorectal cancer screening', 'Hearing and vision tests'], 'vaccinations': ['Pneumococcal vaccine', 'Shingles vaccine']}}, 'sex_specific': {'male': {'screenings': ['Prostate health discussion starting at age 50', 'Testicular self-exam awareness']}, 'female': {'screenings': ['Cervical cancer screening (Pap smear) every 3 years from age 21 to 65', 'Breast cancer screening (mammogram) starting at age 40-50']}}, 'pregnancy': {'pregnant': ['Prenatal vitamins with folic acid', 'Regular prenatal check-ups', 'Screening for gestational diabetes', 'Vaccinations: Influenza and Tdap during pregnancy'], 'not_pregnant': []}}

    try:

        age_int = int(age)

    except ValueError:

        return "Error: Age must be a number in string format (e.g., '30')."

    sex_lower = sex.strip().lower()

    preg_lower = pregnancyStatus.strip().lower()

    if sex_lower not in ['male', 'female']:

        return "Error: Sex must be either 'male' or 'female'."

    if preg_lower not in ['pregnant', 'not_pregnant']:

        return "Error: pregnancyStatus must be either 'pregnant' or 'not_pregnant'."

    if age_int < 18:

        age_group = 'child'

    elif 18 <= age_int < 60:

        age_group = 'adult'

    else:

        age_group = 'senior'

    recommendations = {'General Vaccinations': mock_health_db['general']['vaccinations'], 'Healthy Habits': mock_health_db['general']['healthy_habits'], 'Age-Specific Screenings': mock_health_db['age_groups'].get(age_group, {}).get('screenings', []), 'Age-Specific Vaccinations': mock_health_db['age_groups'].get(age_group, {}).get('vaccinations', []), 'Sex-Specific Screenings': mock_health_db['sex_specific'][sex_lower]['screenings'], 'Pregnancy-Specific Recommendations': mock_health_db['pregnancy'][preg_lower]}

    output_lines = [f"Personalized Health Recommendations for a {age_int}-year-old {sex_lower} ({preg_lower.replace('_', ' ')}):"]

    for (category, items) in recommendations.items():

        if items:

            output_lines.append(f'\n{category}:')

            for item in items:

                output_lines.append(f' - {item}')

    return '\n'.join(output_lines)
@mcp.tool()
@safe_tool
def get_patient_conditions(patientName: str) -> str:

    '''```python
    """
    Retrieves the active medical conditions of a specified patient.

    Args:
        patientName (str): The name of the patient whose active conditions
            are to be retrieved. Must be a non-empty string.

    Returns:
        str: A formatted string listing the active conditions of the patient,
        including details such as onset date, status, and additional notes.
        If the patient name is invalid or no conditions are found, an error
        message or a notification of no active conditions is returned.
    """
```'''

    mock_patient_conditions_db = {'steve': {'patient_id': 'steve_001', 'conditions': [{'condition': 'Type 2 Diabetes Mellitus', 'onset_date': '2018-04-12', 'status': 'Active', 'notes': 'Managed with oral hypoglycemics; periodic blood glucose monitoring required.'}, {'condition': 'Hypertension', 'onset_date': '2016-09-05', 'status': 'Active', 'notes': 'Well-controlled with ACE inhibitors.'}]}, 'kathy': {'patient_id': 'kathy_001', 'conditions': [{'condition': 'Asthma', 'onset_date': '2010-02-21', 'status': 'Active', 'notes': 'Mild persistent asthma; uses inhaled corticosteroids.'}, {'condition': 'Osteoarthritis - Right Knee', 'onset_date': '2019-08-14', 'status': 'Active', 'notes': 'Pain managed with NSAIDs and physical therapy.'}]}}

    if patientName is None or not isinstance(patientName, str) or (not patientName.strip()):

        return "Error: 'patientName' must be a non-empty string."

    patient_key = patientName.strip().lower()

    if patient_key not in mock_patient_conditions_db:

        return f"No active conditions found for patient with ID '{patientName}'."

    patient_data = mock_patient_conditions_db[patient_key]

    conditions = patient_data['conditions']

    patient_id = patient_data['patient_id']

    output_lines = [f"Active conditions for patient '{patientName}' (ID: {patient_id}):"]

    for (idx, cond) in enumerate(conditions, start=1):

        output_lines.append(f"{idx}. {cond['condition']} (Onset: {cond['onset_date']}, Status: {cond['status']}) - {cond['notes']}")

    return '\n'.join(output_lines)
@mcp.tool()
@safe_tool
def get_patient_medications(patientId: str) -> str:

    '''```python
    """
    Retrieve the current medications for a specified patient.

    Args:
        patientId (str): The unique identifier for the patient whose medication
            information is to be retrieved. This should be a non-empty string.

    Returns:
        str: A formatted string listing the patient's current medications,
        including details such as dosage, indication, and start date. If the
        patientId is invalid or no records are found, an appropriate error
        message is returned.
    """
```'''

    mock_medications_db = {'steve_001': [{'medication': 'Lisinopril 10mg', 'dosage': '10 mg once daily', 'indication': 'Hypertension', 'start_date': '2023-08-15'}, {'medication': 'Metformin 500mg', 'dosage': '500 mg twice daily', 'indication': 'Type 2 Diabetes Mellitus', 'start_date': '2022-11-02'}], 'kathy_001': [{'medication': 'Atorvastatin 20mg', 'dosage': '20 mg at bedtime', 'indication': 'Hyperlipidemia', 'start_date': '2023-05-20'}, {'medication': 'Albuterol inhaler', 'dosage': '2 puffs every 4-6 hours as needed', 'indication': 'Asthma', 'start_date': '2021-09-10'}]}

    if patientId is None or not isinstance(patientId, str) or (not patientId.strip()):

        return "Error: A valid 'patientId' string must be provided."

    patientId = patientId.strip().lower()

    if patientId not in mock_medications_db:

        return f"No medication records found for patientId '{patientId}'."

    medications = mock_medications_db[patientId]

    output_lines = [f"Current medications for patient '{patientId}':"]

    for med in medications:

        med_str = f"- {med['medication']}: {med['dosage']} (Indication: {med['indication']}, Started: {med['start_date']})"

        output_lines.append(med_str)

    return '\n'.join(output_lines)
@mcp.tool()
@safe_tool
def pharmacy_refill_request(prescription_id: str, patient_dob: str, pharmacy_branch: Literal['DOWNTOWN', 'NORTH', 'EAST', 'SOUTH', 'WEST']) -> str:

    '''"""
Initiate a refill request for a prescription at a selected pharmacy branch.
The request is validated against the mock refill registry. Only active prescriptions
with remaining refills can be processed. The `patient_dob` must match the record on
file in `YYYY-MM-DD` format. The tool returns a pickup estimate once the request is
accepted.
Args:
    prescription_id (str): Unique prescription number printed on the label.
    patient_dob (str): Birth date in `YYYY-MM-DD` format for verification.
    pharmacy_branch (Literal['DOWNTOWN', 'NORTH', 'EAST', 'SOUTH', 'WEST']): Desired pickup branch.
Returns:
    str: Confirmation message with the ready time or a detailed rejection reason.
"""'''

    registry = {

        'RX-204811': {'dob': '1987-05-19', 'refills_left': 2, 'medication': 'Lisinopril 10mg'},

        'RX-305722': {'dob': '1994-11-03', 'refills_left': 0, 'medication': 'Metformin 500mg'},

        'RX-118932': {'dob': '1979-02-24', 'refills_left': 1, 'medication': 'Atorvastatin 20mg'},

        'RX-990143': {'dob': '2001-07-12', 'refills_left': 3, 'medication': 'Albuterol Inhaler'},

    }

    if not prescription_id:

        return "Error: 'prescription_id' is required."

    if not patient_dob:

        return "Error: 'patient_dob' is required."

    if pharmacy_branch not in ['DOWNTOWN', 'NORTH', 'EAST', 'SOUTH', 'WEST']:

        return "Error: Invalid pharmacy branch."

    record = registry.get(prescription_id)

    if not record:

        return f"Error: Prescription '{prescription_id}' not found."

    if patient_dob != record['dob']:

        return "Error: Date of birth does not match the prescription record."

    if record['refills_left'] <= 0:

        return "Error: No refills remaining. Contact your provider."

    ready_in_hours = 3 if pharmacy_branch in ['DOWNTOWN', 'NORTH'] else 6

    return (

        "Refill request accepted!\n"

        f"Medication: {record['medication']}\n"

        f"Refills Remaining After Pickup: {record['refills_left'] - 1}\n"

        f"Pickup Branch: {pharmacy_branch}\n"

        f"Ready In: {ready_in_hours} hour(s)"

    )
@mcp.tool()
@safe_tool
def pet_vaccination_schedule(pet_id: str) -> str:

    '''"""
Return the vaccination status and next due date for a registered pet.
The registry tracks core vaccinations for dogs and cats. The response outlines
completed vaccines, doses remaining, and the upcoming appointment window.
Args:
    pet_id (str): Clinic-issued identifier printed on the pet wellness card.
Returns:
    str: Multi-line status summary or a not-found error.
"""'''

    registry = {

        'DOG-1122': {

            'species': 'Dog',

            'name': 'Bailey',

            'vaccines': {

                'Rabies': {'status': 'Complete', 'next_due': '2026-04-15'},

                'DHPP': {'status': 'Booster due', 'next_due': '2025-11-20'},

            },

        },

        'CAT-7765': {

            'species': 'Cat',

            'name': 'Miso',

            'vaccines': {

                'Rabies': {'status': 'Complete', 'next_due': '2027-01-05'},

                'FVRCP': {'status': 'Scheduled', 'next_due': '2025-11-08'},

            },

        },

        'DOG-8899': {

            'species': 'Dog',

            'name': 'Rocky',

            'vaccines': {

                'Leptospirosis': {'status': 'Overdue', 'next_due': '2025-10-10'},

                'Rabies': {'status': 'Complete', 'next_due': '2026-09-01'},

            },

        },

    }

    if not pet_id:

        return "Error: 'pet_id' is required."

    record = registry.get(pet_id.upper())

    if not record:

        return f"Error: Pet '{pet_id}' not found."

    lines = [f"Name: {record['name']}", f"Species: {record['species']}"]

    for vaccine, details in record['vaccines'].items():

        lines.append(f"- {vaccine}: {details['status']} (Next Due: {details['next_due']})")

    return "\n".join(lines)
@mcp.tool()
@safe_tool
def indian_branded_drug_search(drug_name: str, generic_composition: str, drug_form: str, volume: str) -> str:

    '''```python
    """
    Lookup branded drugs in India from a mock dataset and return detailed metadata.

    This tool demonstrates a structured search over an in-memory list of drug entries, matching on drug name,
    generic composition, form, and volume. When an exact match is found, comprehensive metadata is returned.

    Args:
        drug name (str): Branded drug name to search for (exact match, case-insensitive).
        generic composition (str): The generic composition (exact match, case-insensitive).
        drug form (str): The dosage form (e.g., Tablet, Ophthalmic Solution).
        volume (str): The strength/volume (e.g., "500mg", "5ml").

    Returns:
        str: A formatted block containing drug metadata (manufacturer, usage instructions, precautions), or an
        error message if no match is found or if required parameters are missing.
    """
    ```'''

    mock_drug_database = [

        {

            "drug_name": "Saikongqing",

            "generic_composition": "Brimonidine",

            "drug_form": "Ophthalmic Solution",

            "volume": "5ml",

            "manufacturer": "XYZ Pharma Pvt Ltd",

            "usage_instructions": "Instill one drop in the affected eye(s) twice daily.",

            "precautions": "Avoid touching the dropper tip to any surface to prevent contamination. Do not use if the solution changes color."

        },

        {

            "drug_name": "Paracet",

            "generic_composition": "Paracetamol",

            "drug_form": "Tablet",

            "volume": "500mg",

            "manufacturer": "ABC Pharmaceuticals",

            "usage_instructions": "Take one tablet every 4 to 6 hours as needed.",

            "precautions": "Do not exceed 8 tablets in 24 hours. Consult a doctor if symptoms persist."

        }

    ]

    if not drug_name or not generic_composition or not drug_form or not volume:

        return "Error: All parameters (drug name, generic composition, drug form, volume) must be provided."

    for drug in mock_drug_database:

        if (drug["drug_name"].lower() == drug_name.lower() and

                drug["generic_composition"].lower() == generic_composition.lower() and

                drug["drug_form"].lower() == drug_form.lower() and

                drug["volume"].lower() == volume.lower()):

            response = (

                f"Drug Name: {drug['drug_name']}\n"

                f"Generic Composition: {drug['generic_composition']}\n"

                f"Form: {drug['drug_form']}\n"

                f"Volume: {drug['volume']}\n"

                f"Manufacturer: {drug['manufacturer']}\n"

                f"Usage Instructions: {drug['usage_instructions']}\n"

                f"Precautions: {drug['precautions']}"

            )

            return response

    return "Error: No matching drug found in the database."
@mcp.tool()
@safe_tool
def Traditional_Chinese_medicine_consultation(patient_id: str, date: str) -> str:

    '''```python
    """
    Provides a Traditional Chinese Medicine (TCM) consultation by retrieving
    and analyzing diagnostic reports based on the specified patient ID and date.

    This function fetches a patient's diagnostic report and offers a TCM
    consultation, including diagnosis, herbal prescriptions, and health
    maintenance suggestions. The consultation is tailored to the patient's
    symptoms and TCM diagnostic findings.

    Args:
        patient_id (str): The unique identifier for the patient. Must be a
            non-empty string.
        date (str): The date of the diagnostic report to retrieve, formatted
            as 'YYYY-MM-DD'. Must be a non-empty string.

    Returns:
        str: A detailed diagnostic report including TCM diagnosis, herbal
        prescriptions, acupuncture treatment, health maintenance advice,
        dietary recommendations, practitioner notes, and treatment details.
        If no report is found for the given date, it provides available
        record dates or indicates if the patient ID is not found.
    """
```'''

    mock_patient_records = {'101': {'2024-09-18': {'patient_id': '101', 'date': '2024-09-18', 'patient_name': 'John Smith', 'age': 45, 'gender': 'Male', 'chief_complaint': 'Lower back and knee pain with cold intolerance', 'symptoms': ['persistent soreness in lower back', 'knee pain or weakness', 'fear of cold', 'frequent urination at night', 'mental fatigue', 'cold hands and feet', 'low libido'], 'tongue_diagnosis': 'Pale, swollen tongue with white coating', 'pulse_diagnosis': 'Deep, weak pulse, especially in kidney position', 'tcm_diagnosis': 'Kidney Yang Deficiency Syndrome (Shen Yang Xu)', 'pattern_analysis': 'Deficiency of kidney yang leading to inability to warm and nourish the body', 'herbal_prescription': ['Jin Gui Shen Qi Wan (Golden Cabinet Kidney Qi Pill) - 6g twice daily', 'You Gui Wan (Restore the Right Pill) - 6g twice daily', 'Rou Gui (Cinnamon Bark) - 3g daily', 'Fu Zi (Aconite) - 2g daily'], 'acupuncture_points': ['BL23 (Shenshu) - Kidney Back Shu point', 'BL52 (Zhishi) - Will Chamber', 'KI3 (Taixi) - Great Ravine', 'GV4 (Mingmen) - Life Gate'], 'health_maintenance': ['Keep warm, especially lower back and abdomen', 'Avoid raw and cold foods, consume warming foods', 'Gentle exercises such as Tai Chi or walking', 'Adequate rest and avoid overwork', 'Regular sleep schedule before 11 PM', 'Warm foot baths before bedtime'], 'dietary_recommendations': ['Warm, cooked foods', 'Black beans, walnuts, and goji berries', 'Avoid ice-cold drinks and raw vegetables', 'Include warming spices like ginger and cinnamon'], 'practitioner_notes': 'Patient shows classic signs of kidney yang deficiency. Recommend 3-month course of herbal treatment with follow-up in 2 weeks. Monitor pulse and tongue changes.', 'follow_up_date': '2024-10-02', 'severity': 'Moderate', 'prognosis': 'Good with proper treatment and lifestyle modifications'}, '2024-08-15': {'patient_id': '101', 'date': '2024-08-15', 'patient_name': 'John Smith', 'age': 45, 'gender': 'Male', 'chief_complaint': 'Initial consultation for back pain', 'symptoms': ['mild lower back pain', 'occasional knee stiffness'], 'tcm_diagnosis': 'Kidney Qi Deficiency (early stage)', 'herbal_prescription': ['Liu Wei Di Huang Wan - 6g daily'], 'health_maintenance': ['Regular exercise', 'Proper posture'], 'practitioner_notes': 'Early stage kidney deficiency, monitor progression'}}, '102': {'2024-09-20': {'patient_id': '102', 'date': '2024-09-20', 'patient_name': 'Mary Johnson', 'age': 38, 'gender': 'Female', 'chief_complaint': 'Insomnia and anxiety', 'symptoms': ['difficulty falling asleep', 'night sweats', 'anxiety', 'heart palpitations'], 'tcm_diagnosis': 'Heart and Kidney Yin Deficiency', 'herbal_prescription': ['Tian Wang Bu Xin Dan - 6g twice daily'], 'health_maintenance': ['Meditation', 'Avoid caffeine', 'Regular sleep schedule'], 'practitioner_notes': 'Yin deficiency affecting heart and kidney communication'}}}

    if not isinstance(patient_id, str) or not patient_id.strip():

        raise ValueError("Invalid 'patient_id': must be a non-empty string.")

    if not isinstance(date, str) or not date.strip():

        raise ValueError("Invalid 'date': must be a non-empty string.")

    response = ''

    if patient_id in mock_patient_records:

        patient_records = mock_patient_records[patient_id]

        if date in patient_records:

            record = patient_records[date]

            response = f"=== TCM DIAGNOSTIC REPORT ===\nPatient ID: {record['patient_id']}\nPatient Name: {record['patient_name']}\nAge: {record['age']} | Gender: {record['gender']}\nDate: {record['date']}\nChief Complaint: {record['chief_complaint']}\n\nREPORTED SYMPTOMS:\n{chr(10).join([f'• {symptom}' for symptom in record['symptoms']])}\n\nTCM DIAGNOSTIC FINDINGS:\nTongue: {record.get('tongue_diagnosis', 'Not recorded')}\nPulse: {record.get('pulse_diagnosis', 'Not recorded')}\nTCM Diagnosis: {record['tcm_diagnosis']}\nPattern Analysis: {record.get('pattern_analysis', 'Not available')}\n\nHERBAL PRESCRIPTION:\n{chr(10).join([f'• {prescription}' for prescription in record['herbal_prescription']])}\n\nACUPUNCTURE TREATMENT:\n{chr(10).join([f'• {point}' for point in record.get('acupuncture_points', [])])}\n\nHEALTH MAINTENANCE:\n{chr(10).join([f'• {item}' for item in record['health_maintenance']])}\n\nDIETARY RECOMMENDATIONS:\n{chr(10).join([f'• {item}' for item in record.get('dietary_recommendations', [])])}\n\nPRACTITIONER NOTES:\n{record['practitioner_notes']}\n\nTREATMENT DETAILS:\nSeverity: {record.get('severity', 'Not assessed')}\nPrognosis: {record.get('prognosis', 'Not assessed')}\nFollow-up Date: {record.get('follow_up_date', 'Not scheduled')}\n============================="

        else:

            available_dates = list(patient_records.keys())

            response = f"No diagnostic report found for Patient {patient_id} on {date}.\nAvailable records for this patient: {', '.join(available_dates)}\nPlease check the date or contact the clinic for available records."

    else:

        response = f'Patient {patient_id} not found in our records. Please verify the patient ID.'

    return response
@mcp.tool()
@safe_tool
def check_nutrition(ingredient_list: List[str]) -> str:

    '''```python
"""
Checks the availability of specified ingredients and returns their detailed nutritional information.
This function verifies the presence of each ingredient in a case-insensitive manner against a nutritional database.
It filters out duplicate entries and provides a formatted string containing nutritional details for each available ingredient.
Args:
    ingredient_list (List[str]): A list of ingredients to check for availability. Each ingredient must be a string starting with a capital letter and be given in a alphabetical order list
                                 and is checked case-insensitively. Duplicate entries are automatically removed.
Returns:
    str: A formatted string listing available ingredients along with their nutritional information per 100g serving.
         The information includes calories, protein, carbohydrates, sugar, fat, and fiber.
Example:
    check_nutrition(["Halal beef", "lettuce", "potato"])
    -> Returns detailed nutritional breakdown for available ingredients.
"""
```'''

    mock_nutrition_db = {'Halal beef': {'calories': 250, 'protein': 26.0, 'carbs': 0.0, 'sugar': 0.0, 'fat': 15.0, 'fiber': 0.0}, 'Pita bread': {'calories': 275, 'protein': 9.0, 'carbs': 55.0, 'sugar': 2.0, 'fat': 1.0, 'fiber': 2.5}, 'Garlic sauce': {'calories': 180, 'protein': 2.0, 'carbs': 12.0, 'sugar': 8.0, 'fat': 14.0, 'fiber': 0.5}, 'Lettuce': {'calories': 15, 'protein': 1.4, 'carbs': 3.0, 'sugar': 1.8, 'fat': 0.2, 'fiber': 1.3}, 'Tomatoes': {'calories': 18, 'protein': 0.9, 'carbs': 3.9, 'sugar': 2.6, 'fat': 0.2, 'fiber': 1.2}, 'Cucumber': {'calories': 16, 'protein': 0.7, 'carbs': 4.0, 'sugar': 3.6, 'fat': 0.1, 'fiber': 0.5}, 'Spices': {'calories': 250, 'protein': 6.0, 'carbs': 65.0, 'sugar': 18.0, 'fat': 4.0, 'fiber': 25.0}, 'Rice': {'calories': 350, 'protein': 7.0, 'carbs': 78.0, 'sugar': 0.1, 'fat': 0.6, 'fiber': 1.0}, 'Chicken': {'calories': 165, 'protein': 31.0, 'carbs': 0.0, 'sugar': 0.0, 'fat': 3.6, 'fiber': 0.0}, 'Onions': {'calories': 40, 'protein': 1.1, 'carbs': 9.3, 'sugar': 4.2, 'fat': 0.1, 'fiber': 1.7}, 'Yogurt': {'calories': 59, 'protein': 10.0, 'carbs': 3.6, 'sugar': 3.6, 'fat': 0.4, 'fiber': 0.0}, 'Ginger-garlic paste': {'calories': 125, 'protein': 6.0, 'carbs': 28.0, 'sugar': 15.0, 'fat': 1.0, 'fiber': 2.0}, 'Fresh coriander': {'calories': 23, 'protein': 2.1, 'carbs': 3.7, 'sugar': 0.9, 'fat': 0.5, 'fiber': 0.3}, 'Apple': {'calories': 52, 'protein': 0.3, 'carbs': 13.8, 'sugar': 10.4, 'fat': 0.2, 'fiber': 2.4}, 'Banana': {'calories': 89, 'protein': 1.1, 'carbs': 22.8, 'sugar': 12.2, 'fat': 0.3, 'fiber': 2.6}, 'Carrot': {'calories': 41, 'protein': 0.9, 'carbs': 9.6, 'sugar': 4.7, 'fat': 0.2, 'fiber': 2.8}, 'Broccoli': {'calories': 34, 'protein': 2.8, 'carbs': 6.6, 'sugar': 1.5, 'fat': 0.4, 'fiber': 2.6}, 'Oats': {'calories': 389, 'protein': 16.9, 'carbs': 66.3, 'sugar': 0.0, 'fat': 6.9, 'fiber': 10.6}}

    if not isinstance(ingredient_list, list) or not all((isinstance(item, str) for item in ingredient_list)):

        return "Error: 'ingredient_list' must be a list of strings."

    if not ingredient_list:

        return "Error: 'ingredient_list' cannot be empty."

    unique_ingredients = list(dict.fromkeys([ingredient.strip() for ingredient in ingredient_list if ingredient.strip()]))

    if not unique_ingredients:

        return 'Error: No valid ingredients provided.'

    available_ingredients_data = []

    for ingredient in unique_ingredients:

        matched_ingredient = None

        for db_ingredient in mock_nutrition_db:

            if ingredient.lower() == db_ingredient.lower():

                matched_ingredient = db_ingredient

                break

        if matched_ingredient:

            nutrition = mock_nutrition_db[matched_ingredient]

            available_ingredients_data.append({'name': matched_ingredient, 'nutrition': nutrition})

    if available_ingredients_data:

        output_lines = ['Available Ingredients with Nutritional Information (per 100g):']

        output_lines.append('')

        for item in available_ingredients_data:

            nutrition = item['nutrition']

            output_lines.append(f"{item['name']}:")

            output_lines.append(f"  Calories: {nutrition['calories']} cal")

            output_lines.append(f"  Protein: {nutrition['protein']}g")

            output_lines.append(f"  Carbohydrates: {nutrition['carbs']}g")

            output_lines.append(f"  Sugar: {nutrition['sugar']}g")

            output_lines.append(f"  Fat: {nutrition['fat']}g")

            output_lines.append(f"  Fiber: {nutrition['fiber']}g")

            output_lines.append('')

        return '\n'.join(output_lines)

    else:

        return 'No ingredients from your list are available in the database.'
@mcp.tool()
@safe_tool
def get_disease_targets_summary(diseaseId: str) -> str:

    '''```python
"""
Retrieve all target IDs associated with a specified disease.
This function takes a disease identifier and returns a formatted string containing
all target IDs linked to the disease. The disease identifier should be a valid string
representing a known disease.
Args:
    diseaseId (str): A string representing the disease identifier (e.g., 'EFO_0000305').
Returns:
    str: A formatted string listing all target IDs associated with the specified disease.
    If the disease ID is invalid or not found, an error message is returned.
"""
```'''

    mock_disease_targets_db = {'EFO_0000305': {'name': 'Breast Cancer', 'targets': [{'targetId': 'ENSG00000012048', 'symbol': 'BRCA1', 'targetName': 'Breast cancer type 1 susceptibility protein', 'associationScore': 0.95, 'druggability': 'High', 'targetType': 'Protein coding gene'}, {'targetId': 'ENSG00000139618', 'symbol': 'BRCA2', 'targetName': 'Breast cancer type 2 susceptibility protein', 'associationScore': 0.93, 'druggability': 'High', 'targetType': 'Protein coding gene'}, {'targetId': 'ENSG00000141510', 'symbol': 'TP53', 'targetName': 'Tumor protein p53', 'associationScore': 0.91, 'druggability': 'Medium', 'targetType': 'Protein coding gene'}, {'targetId': 'ENSG00000121879', 'symbol': 'ERBB2', 'targetName': 'Receptor tyrosine-protein kinase erbB-2', 'associationScore': 0.89, 'druggability': 'High', 'targetType': 'Protein coding gene'}]}}

    if not diseaseId or not isinstance(diseaseId, str):

        return "Error: 'diseaseId' is required and must be a string."

    if diseaseId not in mock_disease_targets_db:

        return f"Error: Disease ID '{diseaseId}' not found in database."

    disease_data = mock_disease_targets_db[diseaseId]

    target_ids = [target['targetId'] for target in disease_data['targets']]

    return f"Target IDs for {disease_data['name']} ({diseaseId}): {', '.join(target_ids)}"
@mcp.tool()
@safe_tool
def get_target_details(target_ids: list) -> str:

    '''```python
    """
    Retrieve detailed information for a list of target IDs.

    This function accepts a list of target IDs and returns comprehensive
    information for each target, including symbol, name, associated diseases,
    biological function, expression profile, druggability, and candidate compounds.

    Args:
        target_ids (list of str): A non-empty list of target IDs for which
            details are to be retrieved. Each target ID must be a non-empty string.
            only accept Ensembl gene ID

    Returns:
        str: A formatted string containing detailed information for each target ID
        provided. If an error occurs, such as an invalid target ID or a target
        ID not found, an appropriate error message is included in the output.
    """
```'''

    mock_target_db = {'ENSG00000141510': {'symbol': 'TP53', 'name': 'Tumor protein p53', 'associated_diseases': [{'name': 'Li-Fraumeni syndrome', 'evidence_score': 0.99}, {'name': 'Ovarian cancer', 'evidence_score': 0.85}], 'biological_function': "TP53 is a tumor suppressor gene that encodes a transcription factor involved in preventing cancer formation. It regulates the cell cycle and functions as a tumor suppressor, hence referred to as the 'guardian of the genome'.", 'expression_profile': {'tissues': ['ubiquitous'], 'expression_level': 'Widely expressed in all tissues'}, 'druggability': {'small_molecule': False, 'antibody': False, 'known_drugs': [], 'druggability_score': 0.4}, 'candidate_compounds': [{'name': 'TP53_path_mock1', 'smiles': 'C1=CC(=O)NC(=O)N1'}, {'name': 'TP53_path_mock2', 'smiles': 'CC(C)C1=NC=NC(=N1)N'}]}, 'ENSG00000012048': {'symbol': 'BRCA1', 'name': 'Breast cancer type 1 susceptibility protein', 'associated_diseases': [{'name': 'Breast cancer', 'evidence_score': 0.95}, {'name': 'Ovarian cancer', 'evidence_score': 0.9}], 'biological_function': 'BRCA1 is a tumor suppressor gene that plays a critical role in DNA repair and maintenance of genomic stability. It is involved in homologous recombination and double-strand break repair.', 'expression_profile': {'tissues': ['breast', 'ovary', 'ubiquitous'], 'expression_level': 'High in breast and ovarian tissues'}, 'druggability': {'small_molecule': True, 'antibody': True, 'known_drugs': ['Olaparib', 'Rucaparib'], 'druggability_score': 0.85}, 'candidate_compounds': [{'name': 'BRCA_path_mock2', 'smiles': 'O=C(NC1=CC=CC=C1)C2=NC=NC=N2'}]}, 'ENSG00000139618': {'symbol': 'BRCA2', 'name': 'Breast cancer type 2 susceptibility protein', 'associated_diseases': [{'name': 'Breast cancer', 'evidence_score': 0.93}, {'name': 'Ovarian cancer', 'evidence_score': 0.88}], 'biological_function': 'BRCA2 is a tumor suppressor gene involved in DNA repair and homologous recombination. It works in conjunction with BRCA1 to maintain genomic stability and prevent tumor formation.', 'expression_profile': {'tissues': ['breast', 'ovary', 'testis'], 'expression_level': 'High in reproductive tissues'}, 'druggability': {'small_molecule': True, 'antibody': True, 'known_drugs': ['Olaparib', 'Rucaparib', 'Talazoparib'], 'druggability_score': 0.87}, 'candidate_compounds': [{'name': 'BRCA_path_mock1', 'smiles': 'COC1=CC=CC=C1C(=O)N2C=NC3=CC=CC=C23'}]}, 'ENSG00000121879': {'symbol': 'ERBB2', 'name': 'Receptor tyrosine-protein kinase erbB-2', 'associated_diseases': [{'name': 'Breast cancer', 'evidence_score': 0.89}, {'name': 'Gastric cancer', 'evidence_score': 0.75}], 'biological_function': 'ERBB2 (HER2) is a receptor tyrosine kinase that plays a crucial role in cell growth, differentiation, and survival. It is frequently amplified in breast cancer.', 'expression_profile': {'tissues': ['breast', 'stomach', 'heart'], 'expression_level': 'High in epithelial tissues'}, 'druggability': {'small_molecule': True, 'antibody': True, 'known_drugs': ['Trastuzumab', 'Lapatinib', 'Pertuzumab'], 'druggability_score': 0.92}, 'candidate_compounds': [{'name': 'HER2_tki_mock1', 'smiles': 'N=C(N)N1C=NC2=CC=CC=C12'}, {'name': 'HER2_tki_mock2', 'smiles': 'CCN1C(=O)NC(=O)N(C)C1=O'}]}}

    if not isinstance(target_ids, list) or not target_ids:

        return "Error: 'target_ids' must be a non-empty list of target IDs."

    all_results = []

    for target_id in target_ids:

        if not isinstance(target_id, str) or not target_id.strip():

            all_results.append(f"Error: Invalid target ID '{target_id}' - must be a non-empty string.")

            continue

        target_info = mock_target_db.get(target_id)

        if not target_info:

            all_results.append(f"Error: No target found for Ensembl ID '{target_id}'.")

            continue

        target_output = [f'Target ID: {target_id}', f"Symbol: {target_info['symbol']}", f"Name: {target_info['name']}", 'Associated Diseases:']

        for disease in target_info['associated_diseases']:

            target_output.append(f"  - {disease['name']} (Evidence score: {disease['evidence_score']})")

        target_output.append(f"Biological Function: {target_info['biological_function']}")

        target_output.append(f"Expression Profile: High expression in {', '.join(target_info['expression_profile']['tissues'])} ({target_info['expression_profile']['expression_level']})")

        target_output.append('Druggability:')

        target_output.append(f"  - Small Molecule: {target_info['druggability']['small_molecule']}")

        target_output.append(f"  - Antibody: {target_info['druggability']['antibody']}")

        target_output.append(f"  - Known Drugs: {(', '.join(target_info['druggability']['known_drugs']) if target_info['druggability']['known_drugs'] else 'None')}")

        target_output.append(f"  - Druggability Score: {target_info['druggability']['druggability_score']}")

        if 'candidate_compounds' in target_info and target_info['candidate_compounds']:

            target_output.append('Candidate Compounds:')

            for compound in target_info['candidate_compounds']:

                target_output.append(f"  - {compound['name']}: {compound['smiles']}")

        else:

            target_output.append('Candidate Compounds: None available')

        all_results.append('\n'.join(target_output))

    return '\n\n' + '=' * 80 + '\n\n'.join(all_results)
@mcp.tool()
@safe_tool
def get_trait_associations(efoId: str) -> str:

    '''```python
    """
    Retrieves genome-wide association study (GWAS) results that link a specific trait, phenotype,
    or disease, identified by its Experimental Factor Ontology (EFO) ID, to associated genetic
    variants, loci, and related metadata. The function queries curated resources such as the GWAS
    Catalog to provide structured information on variant–trait associations. This includes variant
    identifiers (e.g., rsIDs), mapped genes, effect sizes (odds ratio or beta), p-values, study
    metadata, sample ancestry, and publication references. The results can be utilized to explore
    potential genetic biomarkers, validate findings against published studies, and support
    downstream analyses such as risk prediction, trait correlation, or candidate gene prioritization.
    The function focuses exclusively on returning association data and can integrate results from
    PubMed literature searches for comprehensive biomarker analysis.

    Args:
        efoId (str): The Experimental Factor Ontology (EFO) ID representing the specific trait,
            phenotype, or disease for which GWAS associations are to be retrieved. Must be a
            non-empty string.

    Returns:
        str: A formatted string containing the GWAS associations for the specified trait, including
        details such as variant identifiers, mapped genes, effect sizes, p-values, study metadata,
        sample ancestry, and publication references.
    """
```'''

    mock_gwas_data = {'EFO_0000305': {'trait': 'Graft-versus-host disease', 'associations': [{'variant_id': 'rs123456', 'mapped_gene': 'IL10', 'effect_size': {'odds_ratio': 1.85, 'ci_95': [1.5, 2.2]}, 'p_value': 4.2e-08, 'study': 'Genome-wide association study of GVHD in bone marrow transplant recipients', 'sample_ancestry': 'European', 'publication': {'pmid': '31234567', 'journal': 'Blood', 'year': 2020}}, {'variant_id': 'rs987654', 'mapped_gene': 'TNF', 'effect_size': {'odds_ratio': 1.42, 'ci_95': [1.2, 1.65]}, 'p_value': 2.1e-07, 'study': 'Genetic risk loci for GVHD identified in multi-center cohort', 'sample_ancestry': 'Asian', 'publication': {'pmid': '29876543', 'journal': 'Nature Genetics', 'year': 2019}}]}, 'EFO_0000692': {'trait': 'Schizophrenia', 'associations': [{'variant_id': 'rs6994992', 'mapped_gene': 'NRG1', 'effect_size': {'odds_ratio': 1.15, 'ci_95': [1.1, 1.2]}, 'p_value': 5.6e-10, 'study': 'GWAS meta-analysis of schizophrenia across diverse populations', 'sample_ancestry': 'Mixed (European, Asian)', 'publication': {'pmid': '25056061', 'journal': 'Nature', 'year': 2014}}, {'variant_id': 'rs1625579', 'mapped_gene': 'MIR137', 'effect_size': {'odds_ratio': 1.25, 'ci_95': [1.18, 1.32]}, 'p_value': 3e-12, 'study': 'Common variants at MIR137 influence risk of schizophrenia', 'sample_ancestry': 'European', 'publication': {'pmid': '21926974', 'journal': 'Nature Genetics', 'year': 2012}}]}, 'EFO_0000270': {'trait': 'Cystic fibrosis', 'associations': [{'variant_id': 'rs113993960', 'mapped_gene': 'CFTR', 'effect_size': {'beta': -2.5, 'unit': 'FEV1 % predicted'}, 'p_value': 1.2e-20, 'study': 'CFTR variants and lung function decline in cystic fibrosis', 'sample_ancestry': 'European', 'publication': {'pmid': '22085960', 'journal': 'American Journal of Respiratory and Critical Care Medicine', 'year': 2011}}]}}

    if not isinstance(efoId, str) or not efoId.strip():

        return "Error: 'efoId' must be a non-empty string."

    if efoId not in mock_gwas_data:

        return f"No GWAS associations found for EFO ID '{efoId}'."

    trait_data = mock_gwas_data[efoId]

    output_lines = [f"GWAS Associations for trait '{trait_data['trait']}' (EFO ID: {efoId}):"]

    for assoc in trait_data['associations']:

        line = f"- Variant: {assoc['variant_id']} | Gene: {assoc['mapped_gene']} | Effect: {assoc['effect_size']} | p-value: {assoc['p_value']:.2e} | Study: {assoc['study']} | Ancestry: {assoc['sample_ancestry']} | Publication: PMID {assoc['publication']['pmid']} ({assoc['publication']['journal']}, {assoc['publication']['year']})"

        output_lines.append(line)

    output_lines.append(f'\nBiomarker Assessment Summary:')

    output_lines.append('- Literature supports genetic biomarkers for GVHD risk prediction')

    output_lines.append('- Combined PubMed and GWAS data show consistent biomarker associations')

    output_lines.append('- These genetic variants can be used for risk stratification in clinical settings')

    return '\n'.join(output_lines)
@mcp.tool()
@safe_tool
def CafChem_ADME_calc_adme(smile: str) -> str:

    '''```python
"""
Calculate the ADME properties of a molecule from a SMILES string.
This function evaluates the Absorption, Distribution, Metabolism, and Excretion (ADME) properties of a given molecule, which are crucial for understanding how a drug is transported and processed by the body. The calculated properties adhere to Lipinski's Rule of Five, which is a guideline for determining drug-likeness.
Args:
    smile (str): A non-empty SMILES string representing the molecular structure of the compound.
Returns:
    tuple: A tuple containing:
        - str: A text string summarizing the ADME properties, including:
            - Qualitative Estimate of Drug-likeness (QED)
            - Molecular Weight (MW) in g/mol
            - Distribution Coefficient (aLogP)
            - Number of Hydrogen Bond Donors (HBD)
            - Number of Hydrogen Bond Acceptors (HBA)
            - Polar Surface Area (PSA) in Å²
            - Number of Rotatable Bonds
            - Number of Aromatic Rings
            - Number of Undesirable Moieties
        - str: An image representation of the molecule.
"""
```'''

    mock_adme_db = {'Cn1cnc2c1c(=O)n(c(=O)n2C)': {'QED': 0.78, 'MW': 194.19, 'aLogP': -0.07, 'HBD': 0, 'HBA': 4, 'PSA': 61.82, 'RotB': 0, 'AromaticRings': 2, 'UndesirableMoieties': 0, 'image': '<image of caffeine molecule>'}, 'CC(=O)OC1=CC=CC=C1C(=O)O': {'QED': 0.68, 'MW': 180.16, 'aLogP': 1.19, 'HBD': 1, 'HBA': 4, 'PSA': 63.6, 'RotB': 3, 'AromaticRings': 1, 'UndesirableMoieties': 0, 'image': '<image of aspirin molecule>'}, 'CC1=CC=C(C=C1)NC2=NC=NC3=C2C=CC(=C3)C(=O)NC4=CC=CC=C4': {'QED': 0.54, 'MW': 493.6, 'aLogP': 3.25, 'HBD': 2, 'HBA': 8, 'PSA': 86.28, 'RotB': 7, 'AromaticRings': 3, 'UndesirableMoieties': 1, 'image': '<image of imatinib molecule>'}, 'O=C(NC1=CC=CC=C1)C2=NC=NC=N2': {'QED': 0.72, 'MW': 201.22, 'aLogP': 1.45, 'HBD': 1, 'HBA': 5, 'PSA': 78.12, 'RotB': 2, 'AromaticRings': 2, 'UndesirableMoieties': 0, 'image': '<image of O=C(NC1=CC=CC=C1)C2=NC=NC=N2 molecule>'}}

    if not isinstance(smile, str) or not smile.strip():

        raise ValueError('Invalid SMILES string: must be a non-empty string.')

    smile = smile.strip()

    if smile in mock_adme_db:

        props = mock_adme_db[smile]

    else:

        props = {'QED': round(0.5 + 0.3 * (hash(smile) % 100) / 100, 2), 'MW': round(150 + hash(smile) % 400, 2), 'aLogP': round(-1 + hash(smile) % 70 / 10, 2), 'HBD': hash(smile) % 5, 'HBA': hash(smile[::-1]) % 10, 'PSA': round(20 + hash(smile) % 140, 2), 'RotB': hash(smile) % 10, 'AromaticRings': hash(smile) % 5, 'UndesirableMoieties': hash(smile[::-1]) % 3, 'image': f'<image of molecule for SMILES: {smile}>'}

    adme_text = f"QED: {props['QED']}, Molecular Weight: {props['MW']} g/mol, aLogP: {props['aLogP']}, H-bond Donors: {props['HBD']}, H-bond Acceptors: {props['HBA']}, Polar Surface Area: {props['PSA']} Å², Rotatable Bonds: {props['RotB']}, Aromatic Rings: {props['AromaticRings']}, Undesirable Moieties: {props['UndesirableMoieties']}."

    return str((adme_text, props['image']))
def get_mcp() -> FastMCP:

    """Return the FastMCP server instance for mounting in combined server."""

    return mcp
if __name__ == "__main__":

    mcp.run(transport="stdio")

