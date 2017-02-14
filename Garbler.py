import os
import yaml
from builders.Event import Event
from builders.Fetcher import Fetcher
from builders.Drawerer import Drawerer
from builders.ModParser import ModParser
from builders.ForkParser import ForkParser
from input.Modes import Modes
from Inspector import Inspector
from Crumbs import *

class Garbler:
    def __init__(self, config_path):
        self.config = self.yaml_loader(config_path)
        self.files_path = self.config["files_folder"]
        self.crumbs = self.get_crumbs()
        self.fetcher = Fetcher(self.crumbs)
        self.event = Event(self.crumbs, self.fetcher)

    def run_to_end_auto(self, draw=False):
        choice = None
        while not self.event.complete:
            fork = self.event.step(choice)
            if type(fork) is Choice:
                choice = Utils.any_of_many(fork.options, False).to
        if draw:
            drawerer = Drawerer(self.files_path, self.crumbs)
            self.event.drawed = drawerer.combine(self.event)
        return self.event

    def get_new_event(self, restore_crumbs=False):
        if restore_crumbs:
            self.crumbs = self.get_crumbs()
        event = Event(self.crumbs, self.fetcher)
        return event

    def yaml_loader(self, path):
        if type(path) is list:
            full_path = self.files_path
            for name in path:
                full_path = os.path.join(full_path, name)
        else:
            full_path = path
        with open(full_path, 'r') as yaml_file:
            return yaml.load(yaml_file)

    def get_crumbs(self, inspect=False):
        instructions = self.yaml_loader(["crumbs"])
        thesaurus_vocabulary = self.yaml_loader(["thesaurus"])
        block_type_definitions = self.yaml_loader(["events", "block_type_definitions"])
        story_fundamentals = self.yaml_loader(["events", "story_fundamentals"])
        primers = {}
        for filename in os.listdir(os.path.join(self.files_path, "events", "primers")):
            with open(os.path.join(self.files_path, "events", "primers", filename), 'r') as yaml_primer:
                primers[filename] = yaml.load(yaml_primer)
        context = self.yaml_loader(["context"])
        story_fundamentals["context"] = context
        drops = self.yaml_loader(["events", "presets", "drops"])
        attributes = self.yaml_loader(["events", "presets", "attributes"])
        mods = ModParser.parse_all(self.yaml_loader(["events", "presets", "mods"]), attributes)

        blocks_dict = {}

        entry_point = block_type_definitions["entry_point"]
        block_type_definitions = block_type_definitions["definitions"]

        for definition in block_type_definitions.keys():
            blocks_dict[definition] = []

        for filename in os.listdir(os.path.join(self.files_path, "events", "blocks")):
            with open(os.path.join(self.files_path, "events", "blocks", filename), 'r') as yaml_block:
                block = ForkParser.parse(yaml.load(yaml_block), mods, attributes)
                # todo integrity check: if a block def. has multiple out types, then they must be mapped out in the branches
                for k, v in block_type_definitions[block["type"]].items():
                    block[k] = v
                blocks_dict[block["type"]].append(block)

        crumbs = Crumbs(instructions, thesaurus_vocabulary["thesaurus"], thesaurus_vocabulary["vocabulary"],
                        blocks_dict, story_fundamentals, primers, drops, mods, attributes, entry_point)

        if inspect:
            Inspector.run_all_checks(crumbs)

        return crumbs



