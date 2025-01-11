from dataclasses import dataclass


@dataclass
class Admonition():
    type: str
    icon: str
    obsidian_alias: list[str]

    @property
    def obsidian(self) -> str:
        return f"> [!{str(self.type)}]"

    @property
    def devto(self) -> str:
        return f"> **{self.icon} {self.type.capitalize()}** -"

    @property
    def medium(self) -> str:
        return f"> **{self.icon} {self.type.capitalize()}** -"


admonitions:list[Admonition] = [
    Admonition(type="abstract", icon="🗒️", obsidian_alias=["summary", "tldr"]),
    Admonition(type="info", icon="ℹ️", obsidian_alias=[]),
    Admonition(type="todo", icon="☑️", obsidian_alias=[]),
    Admonition(type="tip", icon="🟢", obsidian_alias=["hint", "important"]),
    Admonition(type="success", icon="✔️", obsidian_alias=["check", "done"]),
    Admonition(type="question", icon="❔", obsidian_alias=["help", "faq"]),
    Admonition(type="warning", icon="⚠️", obsidian_alias=["caution", "attention"]),
    Admonition(type="failure", icon="❌", obsidian_alias=["fail", "missing"]),
    Admonition(type="danger", icon="⚡", obsidian_alias=["error"]),
    Admonition(type="bug", icon="🐛", obsidian_alias=[]),
    Admonition(type="example", icon="🧪", obsidian_alias=[]),
    Admonition(type="quote", icon="💬", obsidian_alias=["cite"]),
]
