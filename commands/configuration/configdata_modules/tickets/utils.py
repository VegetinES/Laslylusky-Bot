def format_list(id_list, get_entity, default="ninguno"):
    if not id_list or id_list == [0] or len(id_list) == 0:
        return default
            
    entity_mentions = []
    for eid in id_list:
        if eid != 0:
            entity = get_entity(eid)
            if entity:
                entity_mentions.append(f"{entity.mention} `[ID: {entity.id}]`")
            else:
                entity_mentions.append(f"`ID: {eid}`")
        
    return "\n".join(entity_mentions) if entity_mentions else default