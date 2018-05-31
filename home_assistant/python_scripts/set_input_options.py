entity_id = data.get('entity_id')
options = data.get('options', 'Default')
optionslist = options.split(',')
if entity_id is not None:
    service_data = {'entity_id': entity_id, 'options': optionslist }
    hass.services.call('input_select', 'set_options', service_data, False)