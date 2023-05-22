import difflib
import os
import typing
import urllib.request

import simplejson as json


class FuzzyDict(dict):
    """Provides a dictionary that performs fuzzy lookup"""

    def __init__(self, cutoff: float = 0.6):
        """Construct a new FuzzyDict instance

        items is an dictionary to copy items from (optional)
        cutoff is the match ratio below which matches should not be considered
        cutoff needs to be a float between 0 and 1 (where zero is no match
        and 1 is a perfect match)"""
        super(FuzzyDict, self).__init__()
        self.cutoff = cutoff

        # short wrapper around some super (dict) methods
        self._dict_contains = lambda key: super(FuzzyDict, self).__contains__(key)
        self._dict_getitem = lambda key: super(FuzzyDict, self).__getitem__(key)

    def _search(self, lookfor: typing.Any, stop_on_first: bool = False):
        """Returns the value whose key best matches lookfor

        if stop_on_first is True then the method returns as soon
        as it finds the first item
        """

        # if the item is in the dictionary then just return it
        if self._dict_contains(lookfor):
            return True, lookfor, self._dict_getitem(lookfor), 1

        # set up the fuzzy matching tool
        ratio_calc = difflib.SequenceMatcher()
        ratio_calc.set_seq1(lookfor)

        # test each key in the dictionary
        best_ratio = 0
        best_match = None
        best_key = None
        for key in self:
            # if the current key is not a string
            # then we just skip it
            try:
                # set up the SequenceMatcher with other text
                ratio_calc.set_seq2(key)
            except TypeError:
                continue

            # we get an error here if the item to look for is not a
            # string - if it cannot be fuzzy matched and we are here
            # this it is definitely not in the dictionary
            try:
                # calculate the match value
                ratio = ratio_calc.ratio()
            except TypeError:
                break

            # if this is the best ratio so far - save it and the value
            if ratio > best_ratio:
                best_ratio = ratio
                best_key = key
                best_match = self._dict_getitem(key)

            if stop_on_first and ratio >= self.cutoff:
                break

        return best_ratio >= self.cutoff, best_key, best_match, best_ratio

    def __contains__(self, item: typing.Any):
        if self._search(item, True)[0]:
            return True
        else:
            return False

    def __getitem__(self, lookfor: typing.Any):
        matched, key, item, ratio = self._search(lookfor)

        if not matched:
            raise KeyError(
                "'%s'. closest match: '%s' with ratio %.3f"
                % (str(lookfor), str(key), ratio)
            )

        return item


__HERE = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(__HERE, "map_filename.json"), "r", encoding="utf8") as f:
    FILENAMES: FuzzyDict = FuzzyDict()
    for k, v in json.load(f).items():
        FILENAMES[k] = v

with open(os.path.join(__HERE, "city_coordinates.json"), "r", encoding="utf8") as f:
    COORDINATES: FuzzyDict = FuzzyDict()
    for k, v in json.load(f).items():
        COORDINATES[k] = v

EXTRA = {}


def register_url(asset_url: str):
    if asset_url:
        registry = asset_url + "/registry.json"
        try:
            contents = urllib.request.urlopen(registry).read()
            contents = json.loads(contents)
        except Exception as e:
            raise e
        files = {}
        pinyin_names = set()
        for name, pinyin in contents["PINYIN_MAP"].items():
            file_name = contents["FILE_MAP"][pinyin]
            files[name] = [file_name, "js"]
            pinyin_names.add(pinyin)

        for key, file_name in contents["FILE_MAP"].items():
            if key not in pinyin_names:
                # English names
                files[key] = [file_name, "js"]

        js_folder_name = contents["JS_FOLDER"]
        if js_folder_name == "/":
            js_file_prefix = f"{asset_url}/"
        else:
            js_file_prefix = f"{asset_url}/{js_folder_name}/"
        EXTRA[js_file_prefix] = files


def register_files(asset_files: dict):
    if asset_files:
        FILENAMES.update(asset_files)


def register_coords(coords: dict):
    if coords:
        COORDINATES.update(coords)
