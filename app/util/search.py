from typing import List

from fuzzywuzzy import process


def search_by_content(key, choices: List[List]):
    result = []
    for i, choice in enumerate(choices):
        res = process.extractOne(key, choice)
        result.append((res, i))
    result.sort(key=lambda x: x[0][1], reverse=True)
    k = result[0][1]
    item = result[0][0][0]
    return choices[k].index(item)
