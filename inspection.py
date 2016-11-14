import pandas 
from tabulate import tabulate


def show_me(main_dict, keys, headers, meta=set(), event_mention=False):
    """
    this function shows in a html table
    for the keys of the main dict the headers (attributes)
    
    :param dict main_dict: either ev_triggers or ev_instances
    (see notebook 'Inspect ECB(+)'
    :pararm iterable keys: keys from the main_dict to inspect
    :param list headers: the attribute you want to inspect from the keys
    :param set meta: keys for which you want to print:
    1. number of rows
    2. minimum, average, and maximum
    
    :rtype: IPython.core.display.HTML
    :return: the results in a html table
    """ 
    rows = []
    for key in keys:
        if key not in main_dict:
            row = [key] + [0 for _ in range(len(headers)-1)]
            rows.append(row)
            continue
            
        the_object = main_dict[key]
        
        if event_mention:
            for event_mention_obj in the_object.event_mentions:
                row = [getattr(event_mention_obj, header) for header in headers]
                rows.append(row)
        else:
            row = [getattr(the_object, header) for header in headers]
            rows.append(row)
    
    df = pandas.DataFrame(rows, columns=headers)

    
    if meta:
        print('number of rows: %s' % len(df))
        for key in meta:
            minimum = min(df[key])
            maximum = max(df[key])
            average = sum(df[key]) / len(df)
            print('%s: min(%s), avg(%s), max(%s)' % (key, 
                                                     minimum, 
                                                     round(average, 2),
                                                     maximum))
    table = tabulate(df, headers='keys', tablefmt='html')
    return table

