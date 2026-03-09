import requests
import json
import logging

logger = logging.getLogger(__name__)

def submit_order(session_data, cdk):
    logger.info(f"=== SUBMIT_ORDER ===")
    logger.info(f"CDK: {cdk}")
    logger.info(f"Session data type: {type(session_data)}")
    
    if isinstance(session_data, str):
        serialized_session = session_data
        logger.info(f"Session is string, length: {len(serialized_session)}")
    else:
        serialized_session = json.dumps(session_data)
        logger.info(f"Session is dict, serialized length: {len(serialized_session)}")

    logger.info(f"Sending request to https://autosubai.com/submit...")
    
    try:
        response = requests.post(
            'https://autosubai.com/submit',
            headers={'Accept': 'application/json'},
            data={
                'uniqueCode': cdk,
                'sessionData': serialized_session,
            },
            timeout=30,
        )
        
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response text: {response.text}")
        
        result = response.json()
        logger.info(f"Response JSON: {result}")

        if result.get('error'):
            logger.warning(f"API returned error: {result['error']}")
            return result['error']

        if result.get('success') is True or result.get('status') == 'processing':
            logger.info(f"API returned success or processing")
            return 'success'

        # If API format changes or returns unexpected payload, surface a generic flow error.
        logger.error(f"Unexpected API response format, returning WORKFLOW_ERROR")
        return 'WORKFLOW_ERROR'
    except Exception as e:
        logger.exception(f"Exception in submit_order: {str(e)}")
        raise


# status_response = requests.post(
#     'https://autosubai.com/check',
#     headers={'Accept': 'application/json'},
#     data={'uniqueCode': 'WU77-GK4R-C7NT'}
# )
# print(status_response.json())