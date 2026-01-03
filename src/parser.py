"""Parser Lusa news dataset annotations."""

import re
import json
from collections import defaultdict

from src.base import LusaDocument


class AnnParser:
    """Parse Lusa news dataset annotations."""

    entity_regex = re.compile(
        r"(\w+)\t(Event|Time|Spatial_Relation|Participant|Measure) (.*)\t(.*)")
    annotator_note_regex = re.compile(r"#\d+\tAnnotatorNotes (.*)\t(.*)")

    def parse(self, annotation: str) -> LusaDocument:
        """Parse a file with the BRAT annotation."""

        annotation = annotation.strip()

        tags = []
        attributes = defaultdict(list)
        lines = annotation.split("\n")
        for line in lines:
            if line[0] == "T":
                tags.append(self._parse_entity(line))

            elif line[0] == "R":
                tags.append(self._parse_link(line))

            elif line[0] == "A":
                attrib = self._parse_attribute(line)
                id_ = attrib.pop("id")
                attributes[id_].append(attrib)

            elif line[0] == "#":
                attribs = self._parse_annotator_notes(line)
                for attrib in attribs:
                    id_ = attrib.pop("id")
                    attributes[id_].append(attrib)

        # Add attributes to tags.
        for tag in tags:
            for attrib in attributes[tag["id"]]:
                key = attrib["attrib"].lower()
                value = attrib["value"]
                tag[key] = value

        return tags

    def _parse_entity(self, line: str) -> dict:
        tid, type_, offset, text = self.entity_regex.findall(line)[0]
        return {"id": tid, "type": type_, "offset": offset, "text": text}

    @staticmethod
    def _parse_link(line: str) -> dict:
        rid, relation, src, tgt = line.split()
        type_, value = relation.split("_")
        src = src.split(":")[1]
        tgt = tgt.split(":")[1]
        return {"id": rid, "type": type_, "relation": value, "src": src, "tgt": tgt}

    @staticmethod
    def _parse_attribute(line: str) -> dict:
        aid, attrib, id_, value = line.split()
        return {"aid": aid, "attrib": attrib, "value": value, "id": id_}

    def _parse_annotator_notes(self, line: str) -> list:
        attributes = []
        id_, attribs = self.annotator_note_regex.findall(line)[0]
        for attrib in attribs.split():
            type_, value = attrib.split("=")
            attributes.append({"attrib": type_, "value": value, "id": id_})
        return attributes

class InceptionParser:
    """Parse Inception annotation format."""

    def parse(self, file_path: str) -> (str, list):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 1. Flatten the list of objects
        # Depending on the specific export setting, objects might be in a root list 
        # or inside a specific key. This handles the structure shown in your snippet.
        # If 'data' is a dict, we look for a list inside, otherwise we assume data is the list.
        objects = data if isinstance(data, list) else list(data.values())

        # We need a lookup dictionary to find objects by their %ID easily
        # (Though in your snippet, the objects are in a list, so we can iterate)
        
        text_content = ""
        gold_annotations = []

        # 2. Find the Text (Sofa)
        # We iterate through everything to find the "uima.cas.Sofa"
        for item in objects:
            # print("Item:", item)  # Debug print to see the structure of each item
            # print(isinstance(item, dict))  # Check if item is a dict
            if isinstance(item, list):
                for sub_item in item:
                    if isinstance(sub_item, dict) and sub_item.get("%TYPE") == "uima.cas.Sofa":
                        text_content = sub_item.get("sofaString")
                        break
            if isinstance(item, dict) and item.get("%TYPE") == "uima.cas.Sofa":
                text_content = item.get("sofaString")
                break
                
        # 3. Find the Gold Annotations (custom.Span)
        if text_content:
            for item in objects:
                if isinstance(item, list):
                    for sub_item in item:
                        # Check if this sub_item is the annotation type we care about
                        if isinstance(sub_item, dict) and sub_item.get("%TYPE") == "custom.Span":
                            begin = sub_item.get("begin")
                            end = sub_item.get("end")
                            label = sub_item.get("label")
                            _id = sub_item.get("%ID")
                            participant_type_domain = sub_item.get("Participant_Type_Domain")
                            
                            # Extract the actual text snippet using offsets
                            entity_text = text_content[begin:end]
                            
                            gold_annotations.append({
                                "id": _id,
                                "text": entity_text,
                                "type": label,
                                "start": begin,
                                "end": end,
                                "offset": f"{begin} {end}",
                                "participant_type_domain": participant_type_domain
                            })
                # Check if this item is the annotation type we care about
                if isinstance(item, dict) and item.get("%TYPE") == "custom.Span":
                    begin = item.get("begin")
                    end = item.get("end")
                    type = item.get("type")
                    
                    # Extract the actual text snippet using offsets
                    entity_text = text_content[begin:end]
                    
                    gold_annotations.append({
                        "text": entity_text,
                        "type": type,
                        "start": begin,
                        "end": end
                    })
        return text_content, gold_annotations
                