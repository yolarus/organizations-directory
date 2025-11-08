from src import ActivityDB
from src.organizations.schemas import ActivityTreeItemSchema


async def get_activities_tree(activities: list[ActivityDB]):
    def convert(value_):
        if not isinstance(value, dict):
            return value
        new_value = {k_: v_ for k_, v_ in value_.items()}
        if 'activities' in new_value:
            activities_list = []
            for v_ in new_value['activities'].values():
                converted_value = convert(v_)
                activities_list.append(converted_value)
            new_value['activities'] = activities_list
        return new_value

    result = {}
    for activity in activities:
        data = {}
        counter = 2
        if activity.parent:
            counter = 0
            if not activity.parent.parent:
                counter = 1
        while activity.parent:
            data[counter] = activity
            counter += 1
            activity = activity.parent
        else:
            data[counter] = activity
        for k, v in sorted(data.items(), key=lambda x: x[0], reverse=True):
            schema = ActivityTreeItemSchema.model_validate(v, from_attributes=True)
            schema_data = schema.model_dump(exclude={'activities'})
            if k == 2:
                if v.uuid not in result:
                    result[v.uuid] = {**schema_data, 'activities': {}}
            elif k == 1:
                if v.uuid not in result[v.parent_uuid]['activities']:
                    result[v.parent_uuid]['activities'][v.uuid] = {**schema_data, 'activities': {}}
            elif k == 0:
                result[v.parent.parent_uuid]['activities'][v.parent_uuid]['activities'][v.uuid] = {**schema_data}
    temp_result = {}
    for key, value in result.items():
        temp_result[key] = convert(value)
    final_result = []
    for value in temp_result.values():
        final_result.append(ActivityTreeItemSchema(**value))
    return final_result
