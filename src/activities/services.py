from uuid import UUID

from sqlalchemy import ScalarSelect, select, union_all, literal

from src import ActivityDB
from src.activities.schemas import ActivityTreeItemSchema


async def get_activities_tree(session, activities: list[ActivityDB]) -> list[ActivityTreeItemSchema]:
    """Get activities tree from list activities"""
    activity_uuids = [a.uuid for a in activities]
    cte_activities = (
        select(
            ActivityDB.uuid,
            ActivityDB.name,
            ActivityDB.parent_uuid,
            literal(0).label('depth')
        )
        .where(ActivityDB.uuid.in_(activity_uuids))
        .cte(name='cte_activities', recursive=True)
    )
    recursive_part = (
        select(
            ActivityDB.uuid,
            ActivityDB.name,
            ActivityDB.parent_uuid,
            (cte_activities.c.depth - 1).label('depth')
        )
        .where(ActivityDB.uuid == cte_activities.c.parent_uuid)
    )
    cte_activities = cte_activities.union_all(recursive_part)
    first_activities_subquery = (
        select(
            cte_activities.c.uuid,
            cte_activities.c.name
        )
        .where(cte_activities.c.parent_uuid.is_(None))
        .distinct()
        .subquery()
    )
    tree_cte = (
        select(
            ActivityDB.uuid,
            ActivityDB.name,
            ActivityDB.parent_uuid,
            literal(0).label('level')
        )
        .where(ActivityDB.uuid.in_(select(first_activities_subquery.c.uuid)))
        .cte(name='tree_cte', recursive=True)
    )
    tree_recursive = (
        select(
            ActivityDB.uuid,
            ActivityDB.name,
            ActivityDB.parent_uuid,
            (tree_cte.c.level + 1).label('level')
        )
        .where(ActivityDB.parent_uuid == tree_cte.c.uuid)
        .where(ActivityDB.uuid.in_(select(cte_activities.c.uuid)))
    )
    tree_cte = tree_cte.union_all(tree_recursive)

    query = (
        select(
            tree_cte.c.uuid,
            tree_cte.c.name,
            tree_cte.c.parent_uuid,
            tree_cte.c.level
        )
        .distinct()
        .order_by(tree_cte.c.level, tree_cte.c.name)
    )
    res = list((await session.execute(query)).mappings())
    activities = {}
    for row in res:
        activities[row.uuid] = {
            'uuid': row.uuid,
            'name': row.name,
            'parent_uuid': row.parent_uuid,
            'activities': []
        }
    activities_tree = []
    for activity in activities.values():
        parent_uuid = activity['parent_uuid']
        if parent_uuid is None:
            activities_tree.append(activity)
        elif parent_uuid in activities:
            activities[parent_uuid]['activities'].append(activity)

    def convert_to_schema(activity_dict: dict) -> ActivityTreeItemSchema:
        children = []
        for child in activity_dict['activities']:
            children.append(convert_to_schema(child))
        return ActivityTreeItemSchema(uuid=activity_dict['uuid'], name=activity_dict['name'], activities=children)

    activities_tree = [convert_to_schema(a) for a in activities_tree]
    return activities_tree


async def get_all_child_activities(activity_uuids: list[UUID] | ScalarSelect) -> ScalarSelect:
    """Get all child activities"""
    queries = []
    for i in range(3):
        field = ActivityDB.uuid if i == 0 else ActivityDB.parent_uuid
        subquery = select(ActivityDB.uuid).where(field.in_(activity_uuids)).subquery()
        activity_uuids = select(subquery).scalar_subquery()
        queries.append(subquery)
    activities = union_all(*[select(q) for q in queries]).scalar_subquery()
    return activities
