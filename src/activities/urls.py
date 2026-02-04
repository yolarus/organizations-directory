from pathlib import Path

from src.base.urls import BaseURL


class ActivityURL(BaseURL):
    """Activity URL."""
    module = Path(__file__).parent.name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.activity_list: str = '/'
        self.activity_create: str = '/'
        self.activity_detail: str = '/{activity_uuid}/'
        self.activity_update: str = '/{activity_uuid}/'
        self.activity_delete: str = '/{activity_uuid}/'


activity_url = ActivityURL()
