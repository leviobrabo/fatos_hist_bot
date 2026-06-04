def is_topic_closed_exception(exception):
    result_json = getattr(exception, 'result_json', {}) or {}
    description = result_json.get('description', '')
    error_code = result_json.get('error_code')

    return error_code == 400 and 'TOPIC_CLOSED' in description
