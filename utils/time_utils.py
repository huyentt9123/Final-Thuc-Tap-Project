from datetime import datetime, timedelta

def is_data_fresh(created_at_str, max_age_hours=12):
    created_at = datetime.fromisoformat(created_at_str)
    return (datetime.utcnow() - created_at) < timedelta(hours=max_age_hours)