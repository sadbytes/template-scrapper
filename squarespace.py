import json

with open('sqaurespace/sqaurespace-tags.json', 'r') as f:
    groups =  json.loads(f.read())

with open('sqaurespace/squarespace-templates.json', 'r') as f:
    templates = json.loads(f.read())




def group_data_by_tags():
    data = {}
    template_data = {}
    for template in templates:
        template_data[template['id']] = {
            'name': template['displayName'],
            'url': template['url'],
            'preview': template['templateAssets']['desktop']
        }

    for group in groups:
        print("[O] Current Group: {}".format(group['name']))
        for item in group['attributes']:
            id = item['id']
            if id not in data:
                data[id] = {
                    'names': [item['name']],
                    'templates': {template_id: template_data.get(template_id) for template_id in item['orderedTemplateIds']}
                }
            else:
                if item['name'] not in data[id]['names']:
                    data[id].append(item['name'])
                for template_id in item['orderedTemplateIds']:
                    if template_id not in data[id]['templates']:
                        data[id]['templates'][template_id] = template_data.get(template_id)

    with open('sqaurespace/squarespace-data-by-tags.json', 'w') as f:
        json.dump(data, f)


def group_data_by_templates():
    ids = {}
    template_data = {}
    for group in groups:
        for item in group['attributes']:
            ids[item['id']] = item['displayName']
    
    for template in templates:
        print("[O] Curennt Template: {}".format(template['displayName']))
        template_data[template['id']] = {
            'name': template['displayName'],
            'url': template['url'],
            'tags': [ids.get(tag_id) for tag_id in template['attributes']],
            'preview': template['templateAssets'].get('display')
        }
    with open('sqaurespace/squarespace-data-by-templates.json', 'w') as f:
        json.dump(template_data, f)

if __name__ == '__main__':
    group_data_by_tags()
    group_data_by_templates()

