import collections
import operator


def calculate_absolute_proportions(count, proportions={}):
    """
    Given an int and a dictionary with name/float entries, which represent relative proportions. It calculates the absolute proportions.

    e.g. input 20, {'a':0.5, 'b':0.5} --> output {'a':10, 'b':10}

    If it doesn't come out even, the rest is appended to the different proportions randomly.

    :param count: the total number to divide into proportions
    :param proportions: dict name/prop_value
    :return: absolute proportions
    """
    prop_sum = sum(proportions.values())
    absolute_proportions = {path: int(count / prop_sum * prop_value) for path, prop_value in proportions.items()}
    absolute_sum = sum(absolute_proportions.values())
    rest = count - absolute_sum
    subset_keys = list(proportions.keys())

    for i in range(rest):
        key = subset_keys[i % len(subset_keys)]
        absolute_proportions[key] += 1

    return absolute_proportions


def calculate_relative_proportions(proportions):
    """
    Converts proportions so they sum to 1.0.

    :param proportions:  dict name/prop_value
    :return:  dict name/prop_value
    """

    prop_sum = sum(proportions.values())
    relative_props = {}

    for name, prop_value in proportions.items():
        relative_props[name] = float(prop_value) / float(prop_sum)

    return relative_props


def try_distribute_values_proportionally(values, proportions):
    """
    e.g.

    values = {'a': 160, 'b': 160, 'c': 20, 'd': 100, 'e': 50, 'f': 60}
    proportions = {'x': 0.6, 'y': 0.2, 'z': 0.2}

    out:
    {'x' : [a,b], 'y' : [c,e]} ...

    :param values: value_id/value
    :param proportions: prop_id/prop
    :return: tuple (prop_id/list of value_ids) (resulting proportions)
    """
    value_sum = 0

    for value in values.values():
        value_sum += value

    absolute_proportions = calculate_absolute_proportions(value_sum, proportions)
    ordered_proportions = collections.OrderedDict(sorted(absolute_proportions.items(), key=operator.itemgetter(1), reverse=True))
    ordered_proportions_keys = list(ordered_proportions.keys())
    ordered_values = collections.OrderedDict(sorted(values.items(), key=operator.itemgetter(1), reverse=True))
    buckets = collections.defaultdict(int)
    prop_id_to_value_ids = collections.defaultdict(list)

    for value_id, value in ordered_values.items():
        found_fitting_bucket = False

        index = 0

        while not found_fitting_bucket and index < len(ordered_proportions_keys):
            bucket_id = ordered_proportions_keys[index]
            bucket_size = ordered_proportions[bucket_id]

            future_value = buckets[bucket_id] + value
            if future_value <= bucket_size:
                buckets[bucket_id] = future_value
                prop_id_to_value_ids[bucket_id].append(value_id)
                found_fitting_bucket = True

            index += 1

        if not found_fitting_bucket:
            best_fitting_bucket = ordered_proportions_keys[0]
            best_fitting_bucket_diff = ordered_proportions[best_fitting_bucket] - buckets[best_fitting_bucket]

            for bucket_id, bucket_size in ordered_proportions.items():
                diff = bucket_size - buckets[bucket_id]

                if diff > best_fitting_bucket_diff:
                    best_fitting_bucket = bucket_id
                    best_fitting_bucket_diff = diff

            buckets[best_fitting_bucket] += value
            prop_id_to_value_ids[best_fitting_bucket].append(value_id)

    return prop_id_to_value_ids


