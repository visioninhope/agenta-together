evaluators = [
    {
        "name": "Exact Match",
        "key": "auto_exact_match",
        "direct_use": True,
        "settings_template": {
            "correct_answer_key": {
                "label": "Expected Answer Column",
                "default": "correct_answer",
                "type": "string",
                "advanced": True,  # Tells the frontend that this setting is advanced and should be hidden by default
                "ground_truth_key": True,  # Tells the frontend that is the name of the column in the test set that should be shown as a ground truth to the user
                "description": "The name of the column in the test data that contains the correct answer",
            },
        },
        "description": "Exact Match evaluator determines if the output exactly matches the specified correct answer, ensuring precise alignment with expected results.",
    },
    {
        "name": "Contains Json",
        "key": "auto_contains_json",
        "direct_use": True,
        "settings_template": {},
        "description": "Contains Json evaluator checks if the output contains the specified JSON structure.",
    },
    {
        "name": "Similarity Match",
        "key": "auto_similarity_match",
        "direct_use": False,
        "settings_template": {
            "similarity_threshold": {
                "label": "Similarity Threshold",
                "type": "number",
                "default": 0.5,
                "description": "The threshold value for similarity comparison",
                "min": 0,
                "max": 1,
                "required": True,
            },
            "correct_answer_key": {
                "label": "Expected Answer Column",
                "default": "correct_answer",
                "type": "string",
                "advanced": True,  # Tells the frontend that this setting is advanced and should be hidden by default
                "ground_truth_key": True,  # Tells the frontend that is the name of the column in the test set that should be shown as a ground truth to the user
                "description": "The name of the column in the test data that contains the correct answer",
            },
        },
        "description": "Similarity Match evaluator checks if the generated answer is similar to the expected answer. You need to provide the similarity threshold. It uses the Jaccard similarity to compare the answers.",
    },
    {
        "name": "Semantic Similarity Match",
        "key": "auto_semantic_similarity",
        "direct_use": False,
        "description": "Semantic Similarity Match evaluator measures the similarity between two pieces of text by analyzing their meaning and context. It compares the semantic content, providing a score that reflects how closely the texts match in terms of meaning, rather than just exact word matches.",
        "settings_template": {
            "correct_answer_key": {
                "label": "Expected Answer Column",
                "default": "correct_answer",
                "type": "string",
                "advanced": True,  # Tells the frontend that this setting is advanced and should be hidden by default
                "ground_truth_key": True,  # Tells the frontend that is the name of the column in the test set that should be shown as a ground truth to the user
                "description": "The name of the column in the test data that contains the correct answer",
            },
        },
    },
    {
        "name": "Regex Test",
        "key": "auto_regex_test",
        "direct_use": False,
        "description": "Regex Test evaluator checks if the generated answer matches a regular expression pattern. You need to provide the regex expression and specify whether an answer is correct if it matches or does not match the regex.",
        "settings_template": {
            "regex_pattern": {
                "label": "Regex Pattern",
                "type": "regex",
                "default": "",
                "description": "Pattern for regex testing (ex: ^this_word\\d{3}$)",
                "required": True,
            },
            "regex_should_match": {
                "label": "Match/Mismatch",
                "type": "boolean",
                "default": True,
                "description": "If the regex should match or mismatch",
            },
        },
    },
    {
        "name": "JSON Field Match",
        "key": "field_match_test",
        "direct_use": False,
        "settings_template": {
            "json_field": {
                "label": "JSON Field",
                "type": "string",
                "default": "",
                "description": "The name of the field in the JSON output that you wish to evaluate",
                "required": True,
            },
            "correct_answer_key": {
                "label": "Expected Answer Column",
                "default": "correct_answer",
                "type": "string",
                "advanced": True,  # Tells the frontend that this setting is advanced and should be hidden by default
                "ground_truth_key": True,  # Tells the frontend that is the name of the column in the test set that should be shown as a ground truth to the user
                "description": "The name of the column in the test data that contains the correct answer",
            },
        },
        "description": "Compares specific one specific field within a JSON to a ground truth in the test set.",
    },
    {
        "name": "JSON Diff Match",
        "key": "auto_json_diff",
        "direct_use": False,
        "description": "Compares the generated JSON output to a ground truth JSON and returns a normalized score between 0 and 1 based on their differences.",
        "settings_template": {
            "compare_schema_only": {
                "label": "Compare Schema Only",
                "type": "boolean",
                "default": False,
                "advanced": True,
                "description": "If set to True, only the key names and their types will be compared between prediction and ground truth, ignoring the actual values. If set to False, key names, their types, and their values will all compared.",
            },
            "predict_keys": {
                "label": "Include prediction keys",
                "type": "boolean",
                "default": False,
                "advanced": True,
                "description": "If set to True, only keys present in the ground truth will be considered. The result will be 1.0 if a key from the ground truth is correctly predicted, regardless of any additional predicted keys. Otherwise both ground truth and prediction keys will be checked.",
            },
            "case_insensitive_keys": {
                "label": "Enable Case-sensitive keys",
                "type": "boolean",
                "default": False,
                "advanced": True,
                "description": "If set to True, keys will be treated as case-insensitive, meaning 'key', 'Key', and 'KEY' are considered equivalent. Otherwise, keys will be treated as case-sensitive.",
            },
            "correct_answer_key": {
                "label": "Expected Answer Column",
                "default": "correct_answer",
                "type": "string",
                "advanced": True,  # Tells the frontend that this setting is advanced and should be hidden by default
                "ground_truth_key": True,  # Tells the frontend that is the name of the column in the test set that should be shown as a ground truth to the user
                "description": "The name of the column in the test data that contains the correct answer",
            },
        },
    },
    {
        "name": "AI Critique",
        "key": "auto_ai_critique",
        "direct_use": False,
        "settings_template": {
            "prompt_template": {
                "label": "Prompt Template",
                "type": "text",
                "default": "We have an LLM App that we want to evaluate its outputs. Based on the prompt and the parameters provided below evaluate the output based on the evaluation strategy below:\nEvaluation strategy: 0 to 10 0 is very bad and 10 is very good.\nPrompt: {llm_app_prompt_template}\nInputs: country: {country}\nExpected Answer Column:{correct_answer}\nEvaluate this: {variant_output}\n\nAnswer ONLY with one of the given grading or evaluation options.",
                "description": "Template for AI critique prompts",
                "required": True,
            },
            "correct_answer_key": {
                "label": "Expected Answer Column",
                "default": "correct_answer",
                "type": "string",
                "advanced": True,  # Tells the frontend that this setting is advanced and should be hidden by default
                "ground_truth_key": True,  # Tells the frontend that is the name of the column in the test set that should be shown as a ground truth to the user
                "description": "The name of the column in the test data that contains the correct answer",
            },
        },
        "description": "AI Critique evaluator sends the generated answer and the correct_answer to an LLM model and uses it to evaluate the correctness of the answer. You need to provide the evaluation prompt (or use the default prompt).",
    },
    {
        "name": "Code Evaluation",
        "key": "auto_custom_code_run",
        "direct_use": False,
        "settings_template": {
            "code": {
                "label": "Evaluation Code",
                "type": "code",
                "default": "from typing import Dict\n\ndef evaluate(\n    app_params: Dict[str, str],\n    inputs: Dict[str, str],\n    output: str, # output of the llm app\n    datapoint: Dict[str, str] # contains the testset row \n) -> float:\n    if output in datapoint.get('correct_answer', None):\n        return 1.0\n    else:\n        return 0.0\n",
                "description": "Code for evaluating submissions",
                "required": True,
            },
            "correct_answer_key": {
                "label": "Expected Answer Column",
                "default": "correct_answer",
                "type": "string",
                "advanced": True,  # Tells the frontend that this setting is advanced and should be hidden by default
                "ground_truth_key": True,  # Tells the frontend that is the name of the column in the test set that should be shown as a ground truth to the user
                "description": "The name of the column in the test data that contains the correct answer. This will be shown in the results page.",
            },
        },
        "description": "Code Evaluation allows you to write your own evaluator in Python. You need to provide the Python code for the evaluator.",
    },
    {
        "name": "Webhook test",
        "key": "auto_webhook_test",
        "direct_use": False,
        "settings_template": {
            "webhook_url": {
                "label": "Webhook URL",
                "type": "string",
                "description": "https://your-webhook-url.com",
                "required": True,
            },
            "correct_answer_key": {
                "label": "Expected Answer Column",
                "default": "correct_answer",
                "type": "string",
                "advanced": True,  # Tells the frontend that this setting is advanced and should be hidden by default
                "ground_truth_key": True,  # Tells the frontend that is the name of the column in the test set that should be shown as a ground truth to the user
                "description": "The name of the column in the test data that contains the correct answer",
            },
        },
        "description": "Webhook test evaluator sends the generated answer and the correct_answer to a webhook and expects a response, in JSON format, indicating the correctness of the answer, along with a 200 HTTP status. You need to provide the URL of the webhook and the response of the webhook must be between 0 and 1.",
    },
    {
        "name": "Starts With",
        "key": "auto_starts_with",
        "direct_use": False,
        "settings_template": {
            "prefix": {
                "label": "prefix",
                "type": "string",
                "required": True,
                "description": "The string to match at the start of the output.",
            },
            "case_sensitive": {
                "label": "Case Sensitive",
                "type": "boolean",
                "default": True,
                "description": "If the evaluation should be case sensitive.",
            },
        },
        "description": "Starts With evaluator checks if the output starts with a specified prefix, considering case sensitivity based on the settings.",
    },
    {
        "name": "Ends With",
        "key": "auto_ends_with",
        "direct_use": False,
        "settings_template": {
            "case_sensitive": {
                "label": "Case Sensitive",
                "type": "boolean",
                "default": True,
                "description": "If the evaluation should be case sensitive.",
            },
            "suffix": {
                "label": "suffix",
                "type": "string",
                "description": "The string to match at the end of the output.",
                "required": True,
            },
        },
        "description": "Ends With evaluator checks if the output ends with a specified suffix, considering case sensitivity based on the settings.",
    },
    {
        "name": "Contains",
        "key": "auto_contains",
        "direct_use": False,
        "settings_template": {
            "case_sensitive": {
                "label": "Case Sensitive",
                "type": "boolean",
                "default": True,
                "description": "If the evaluation should be case sensitive.",
            },
            "substring": {
                "label": "substring",
                "type": "string",
                "description": "The string to check if it is contained in the output.",
                "required": True,
            },
        },
        "description": "Contains evaluator checks if the output contains a specified substring, considering case sensitivity based on the settings.",
    },
    {
        "name": "Contains Any",
        "key": "auto_contains_any",
        "direct_use": False,
        "settings_template": {
            "case_sensitive": {
                "label": "Case Sensitive",
                "type": "boolean",
                "default": True,
                "description": "If the evaluation should be case sensitive.",
            },
            "substrings": {
                "label": "substrings",
                "type": "string",
                "description": "Provide a comma-separated list of strings to check if any is contained in the output.",
                "required": True,
            },
        },
        "description": "Contains Any evaluator checks if the output contains any of the specified substrings from a comma-separated list, considering case sensitivity based on the settings.",
    },
    {
        "name": "Contains All",
        "key": "auto_contains_all",
        "direct_use": False,
        "settings_template": {
            "case_sensitive": {
                "label": "Case Sensitive",
                "type": "boolean",
                "default": True,
                "description": "If the evaluation should be case sensitive.",
            },
            "substrings": {
                "label": "substrings",
                "type": "string",
                "description": "Provide a comma-separated list of strings to check if all are contained in the output.",
                "required": True,
            },
        },
        "description": "Contains All evaluator checks if the output contains all of the specified substrings from a comma-separated list, considering case sensitivity based on the settings.",
    },
    {
        "name": "Levenshtein Distance",
        "key": "auto_levenshtein_distance",
        "direct_use": False,
        "settings_template": {
            "threshold": {
                "label": "Threshold",
                "type": "number",
                "required": False,
                "description": "The maximum allowed Levenshtein distance between the output and the correct answer.",
            },
            "correct_answer_key": {
                "label": "Expected Answer Column",
                "default": "correct_answer",
                "type": "string",
                "advanced": True,  # Tells the frontend that this setting is advanced and should be hidden by default
                "ground_truth_key": True,  # Tells the frontend that is the name of the column in the test set that should be shown as a ground truth to the user
                "description": "The name of the column in the test data that contains the correct answer",
            },
        },
        "description": "This evaluator calculates the Levenshtein distance between the output and the correct answer. If a threshold is provided in the settings, it returns a boolean indicating whether the distance is within the threshold. If no threshold is provided, it returns the actual Levenshtein distance as a numerical value.",
    },
]


def get_all_evaluators():
    """
    Returns a list of evaluators

    Returns:
        List[dict]: A list of evaluator dictionaries.
    """
    return evaluators
