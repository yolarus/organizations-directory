from pathlib import Path

from src.base.urls import BaseURL


class OrganizationURL(BaseURL):
    """Organization URL."""
    module = Path(__file__).parent.name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.organization_list: str = '/'
        self.organization_create: str = '/'
        self.organization_detail: str = '/{organization_uuid}/'
        self.organization_update: str = '/{organization_uuid}/'
        self.organization_delete: str = '/{organization_uuid}/'
        self.building_list: str = '/buildings/'
        self.building_create: str = '/buildings/'
        self.building_detail: str = '/buildings/{building_uuid}/'
        self.building_update: str = '/buildings/{building_uuid}/'
        self.building_delete: str = '/buildings/{building_uuid}/'


organization_url = OrganizationURL()
