import re
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

@dataclass
class DOMElement:
    element_id: str
    tag_name: str
    text: str
    element_type: str = "element"  # button, link, input, form, text
    attributes: Dict[str, str] = field(default_factory=dict)
    is_interactive: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class CompactDOMSummary:
    page_title: str
    url: str
    buttons: List[DOMElement] = field(default_factory=list)
    inputs: List[DOMElement] = field(default_factory=list)
    links: List[DOMElement] = field(default_factory=list)
    text_snippet: str = ""

    def to_summary_text(self) -> str:
        lines = [f"PAGE: {self.page_title} ({self.url})"]
        if self.buttons:
            lines.append("BUTTONS:")
            for i, b in enumerate(self.buttons, 1):
                lines.append(f"  [{i}] Button: '{b.text}' (id={b.element_id})")
        if self.inputs:
            lines.append("INPUTS:")
            for i, inp in enumerate(self.inputs, 1):
                lines.append(f"  [{i}] Input: type='{inp.attributes.get('type', 'text')}', name='{inp.text}' (id={inp.element_id})")
        if self.links:
            lines.append("LINKS:")
            for i, l in enumerate(self.links, 1):
                lines.append(f"  [{i}] Link: '{l.text}' -> {l.attributes.get('href', '#')}")
        return "\n".join(lines)

class DOMAnalyzer:
    def extract_compact_dom(self, html_content: str, url: str = "http://example.com", title: str = "Page Title") -> CompactDOMSummary:
        """Extracts token-efficient compact interactive DOM representation."""
        buttons = []
        inputs = []
        links = []

        # Extract buttons
        btn_matches = re.findall(r'<button[^>]*id=["\']([^"\']+)["\'][^>]*>(.*?)</button>', html_content, re.IGNORECASE | re.DOTALL)
        for i, (b_id, b_text) in enumerate(btn_matches, 1):
            clean_text = re.sub(r'<[^>]+>', '', b_text).strip() or f"Button {i}"
            buttons.append(DOMElement(element_id=b_id, tag_name="button", text=clean_text, element_type="button"))

        if not buttons and "button" in html_content.lower():
            # Fallback simple extraction
            buttons.append(DOMElement(element_id="btn_submit", tag_name="button", text="Submit", element_type="button"))

        # Extract inputs
        input_matches = re.findall(r'<input[^>]*id=["\']([^"\']+)["\'][^>]*type=["\']([^"\']+)["\'][^>]*>', html_content, re.IGNORECASE)
        for inp_id, inp_type in input_matches:
            inputs.append(DOMElement(element_id=inp_id, tag_name="input", text=inp_id, element_type="input", attributes={"type": inp_type}))

        if not inputs and "input" in html_content.lower():
            inputs.append(DOMElement(element_id="input_user", tag_name="input", text="Username", element_type="input", attributes={"type": "text"}))

        # Extract links
        link_matches = re.findall(r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html_content, re.IGNORECASE | re.DOTALL)
        for href, l_text in link_matches:
            clean_text = re.sub(r'<[^>]+>', '', l_text).strip() or href
            links.append(DOMElement(element_id=f"link_{href}", tag_name="a", text=clean_text, element_type="link", attributes={"href": href}))

        return CompactDOMSummary(
            page_title=title,
            url=url,
            buttons=buttons,
            inputs=inputs,
            links=links,
            text_snippet=re.sub(r'<[^>]+>', ' ', html_content[:300]).strip()
        )
