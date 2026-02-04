from pathlib import Path

from src.base.urls import BaseURL


class BuildingURL(BaseURL):
    """Building URL."""
    module = Path(__file__).parent.name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.building_list: str = '/'
        self.building_create: str = '/'
        self.building_detail: str = '/{building_uuid}/'
        self.building_update: str = '/{building_uuid}/'
        self.building_delete: str = '/{building_uuid}/'


building_url = BuildingURL()
