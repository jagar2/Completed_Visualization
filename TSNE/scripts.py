def generate_names_from_list(category_items):
    # generates the names list
    names = []
    for i in range(category_items.shape[0]):
        if i == 0:
            names = [tuple([category_items[0],category_items[0]])]
        else:
            names.append(tuple([category_items[i],category_items[i]]))
    return names
