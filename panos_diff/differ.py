
from lxml import etree
from lxml.etree import Element
from typing import List, Dict, Any, Union

class XmlDiffService:
    """Custom XML differ using lxml for detecting subtree changes."""
        
    # ANSI color codes
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    """Custom XML differ using lxml for detecting subtree changes."""
        
    def __init__(self):
            self.changes = []
        
    def diff(self, source: Union[Element,str], target: Union[Element,str]) -> List[Dict[str, Any]]:
        """Compare two XML strings and return list of changes."""
        self.changes = []
        if  isinstance(source,str):
            self.source_root = etree.fromstring(source.encode())
        elif isinstance(source,Element):
            self.source_root = source
        else:
            raise TypeError(f"source element is an incorrect type {type(source)} ") 
        if  isinstance(target,str):
            self.target_root = etree.fromstring(target.encode())
        elif isinstance(source,Element):
            self.target_root = target
        else:
            raise TypeError(f"source element is an incorrect type {type(source)} ") 
        
        self._compare_elements(self.source_root, self.target_root)
        return self.changes
    
    
    def _element_id(self, elem):
        """Generate unique name for element (using tag + name attribute)."""
        elem_id = elem.get('name')
        if elem_id:
            return f"{elem.tag}[@name='{elem_id}']"
        return None
    
    def _has_child_elements(self, elem):
        """Check if element has child elements (not just text)."""
        return len(list(elem)) > 0
    
    def _get_text_content(self, elem):
        """Get text content of element (normalized)."""
        return (elem.text or "").strip()
    
    def _get_xpath(self, elem, root):
        """Generate XPath for an element."""
        path = []
        current = elem
        
        while current is not None and current != root:
            parent = current.getparent()
            if parent is None:
                break
            
            # Get position among siblings with same tag
            
            siblings = [e for e in parent if e.tag == current.tag]
            position = siblings.index(current) + 1
            
            # Build selector with name if available, otherwise with position
            elem_id = current.get('name')
            if elem_id:
                selector = f"{current.tag}[@name='{elem_id}']"
            elif len(siblings) > 1:
                selector = f"{current.tag}[{position}]"
            else:
                selector = f"{current.tag}"
            
            path.append(selector)
            current = parent
        
        path.reverse()
        return "/" + "/".join(path)
    
    def _elements_equal(self, elem1, elem2) -> bool:
        """Check if two elements are equal (tag, text, attributes)."""
        if elem1.tag != elem2.tag:
            return False
        if (elem1.text or "").strip() != (elem2.text or "").strip():
            return False
        if elem1.attrib != elem2.attrib:
            return False
        return True
    
    def _find_matching_child(self, parent2, child1):
        """Find matching child in parent2 by element ID or tag."""
        child1_id = self._element_id(child1)
        if child1_id:
            for child2 in parent2:
                if self._element_id(child2) == child1_id:
                    return child2
        # Fallback: match by tag, attributes, and optionally text
        for child2 in parent2:
            # Tag must match
            if child2.tag != child1.tag:
                continue
            
            # Attributes must match
            if child1.attrib != child2.attrib:
                continue
            
            # If no child elements, text content should match
            if not self._has_child_elements(child1):
                if self._get_text_content(child1) == self._get_text_content(child2):
                    return child2
            else:
                # Element has subtrees, don't require text match
                return child2
        
        return None
    
    def _compare_elements(self, elem1, elem2):
        """Recursively compare two elements."""
        
        # Check if elements are equal
        if not self._elements_equal(elem1, elem2):
            self.changes.append({
                'type': 'modify',
                'xpath': self._get_xpath(elem1, self.source_root),
                'old': etree.tostring(elem1, encoding='unicode'),
                'new': etree.tostring(elem2, encoding='unicode')
            })
        
        # Compare children
        children1 = list(elem1)
        children2 = list(elem2)
        
        # First pass: identify all matched children and track deletions/insertions
        matched_children2 = set()
        deletions = []
        insertions = set()
        
        for child1 in children1:
            child2 = self._find_matching_child(elem2, child1)
            
            if child2 is None:
                # Child deleted in elem2
                deletions.append({
                    'type': 'delete',
                    'xpath': self._get_xpath(child1, self.source_root),
                    'element': etree.tostring(child1, encoding='unicode')
                })
            else:
                matched_children2.add(id(child2))
        
        for child2 in children2:
            if id(child2) not in matched_children2:
                insertions.add(id(child2))
        
        # Second pass: detect moves only if there are no adds/deletes
        # that would naturally change positions
        has_structural_changes = len(deletions) > 0 or len(insertions) > 0
        
        for child1 in children1:
            child2 = self._find_matching_child(elem2, child1)
            if child2 is not None:
                child1_id = self._element_id(child1)
                idx1 = children1.index(child1)
                idx2 = children2.index(child2)
                
                # Only report move if positions differ AND there are no structural changes
                if idx1 != idx2 and not has_structural_changes:
                    self.changes.append({
                        'type': 'move',
                        'xpath': self._get_xpath(child1, self.source_root),
                        'from_index': idx1,
                        'to_index': idx2
                    })
                
                # Recursively compare children
                self._compare_elements(child1, child2)
        
        # Add recorded deletions
        self.changes.extend(deletions)
        
        # Detect additions
        for child2 in children2:
            if id(child2) in insertions:
                child2_id = self._element_id(child2)
                self.changes.append({
                    'type': 'insert',
                    'xpath': self._get_xpath(child2, self.target_root),
                    'element': etree.tostring(child2, encoding='unicode'),
                    'index': children2.index(child2)
                })

    def pretty_print(self):
        """Print diff results in a diff-tool style format."""
        if not self.changes:
            print(f"{self.BLUE}No differences found{self.RESET}\n")
            return
        
        print(f"\n{self.BOLD}XML Diff Report{self.RESET}")
        print(f"{self.BOLD}{'='*80}{self.RESET}\n")
        
        # Group changes by type
        by_type = {}
        for change in self.changes:
            change_type = change['type']
            if change_type not in by_type:
                by_type[change_type] = []
            by_type[change_type].append(change)
        
        # Display in order: delete, insert, move, modify
        order = ['delete', 'insert', 'move', 'modify']
        
        for change_type in order:
            if change_type not in by_type:
                continue
            
            changes_of_type = by_type[change_type]
            
            if change_type == 'delete':
                icon = f"{self.RED}[-]{self.RESET}"
                title = f"{self.RED}{self.BOLD}DELETED ({len(changes_of_type)}){self.RESET}"
            elif change_type == 'insert':
                icon = f"{self.GREEN}[+]{self.RESET}"
                title = f"{self.GREEN}{self.BOLD}INSERTED ({len(changes_of_type)}){self.RESET}"
            elif change_type == 'move':
                icon = f"{self.YELLOW}[→]{self.RESET}"
                title = f"{self.YELLOW}{self.BOLD}MOVED ({len(changes_of_type)}){self.RESET}"
            else:  # modify
                icon = f"{self.BLUE}[~]{self.RESET}"
                title = f"{self.BLUE}{self.BOLD}MODIFIED ({len(changes_of_type)}){self.RESET}"
            
            print(f"{title}")
            print("-" * 80)
            
            for i, change in enumerate(changes_of_type, 1):
                print(f"{icon} {change['xpath']}")
                
                if change_type == 'delete':
                    element_lines = change['element'].strip().split('\n')
                    for line in element_lines:
                        print(f"   {self.RED}{line}{self.RESET}")
                
                elif change_type == 'insert':
                    element_lines = change['element'].strip().split('\n')
                    for line in element_lines:
                        print(f"   {self.GREEN}{line}{self.RESET}")
                
                elif change_type == 'move':
                    print(f"   From position: {change['from_index']} → To position: {change['to_index']}")
                
                elif change_type == 'modify':
                    old_str = change['old'].split('\n')[0][:50]
                    new_str = change['new'].split('\n')[0][:50]
                    print(f"   {self.RED}Old: {old_str}{self.RESET}")
                    print(f"   {self.GREEN}New: {new_str}{self.RESET}")
                
                print()
        
        print(f"{self.BOLD}{'='*80}{self.RESET}")
        print(f"{self.BOLD}Total changes: {len(self.changes)}{self.RESET}\n")
        

differ = XmlDiffService()

# Example usage
if __name__ == "__main__":
    xml1 = """
    <root>
        <user name="1">
            <name>Alice</name>
            <email>alice@example.com</email>
        </user>
        <user name="2">
            <name>Bob</name>
        </user>
    </root>
    """
    
    xml2 = """
    <root>
        <user name="1">
            <name>Alice</name>
            <email>alice@example.com</email>
            <phone>555-1234</phone>
        </user>
        <user name="3">
            <name>Charlie</name>
        </user>
    </root>
    """
    
    changes=differ.diff(xml1,xml2)
    differ.pretty_print()
    

    
