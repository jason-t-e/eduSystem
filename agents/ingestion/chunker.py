import re
from typing import List
from dataclasses import dataclass

@dataclass
class Chunk:
    text: str
    heading_path: str
    source_file: str
    page_estimate: int
    chunk_index: int

def chunk_markdown(markdown_text: str, source_file: str, max_tokens: int = 500) -> List[Chunk]:
    """
    Split normalized markdown by headings (H2/H3).
    A very rough semantic chunker based on document structure.
    """
    chunks = []
    current_text = []
    current_headings = []
    chunk_index = 0

    # Rough approximation: 1 word ~ 1.3 tokens
    def estimate_tokens(text: str) -> int:
        return int(len(text.split()) * 1.3)

    lines = markdown_text.split("\n")
    for line in lines:
        match = re.match(r'^(#{1,3})\s+(.*)', line)
        if match:
            # If we have accumulated enough text, save the chunk
            joined_text = "\n".join(current_text).strip()
            if joined_text and estimate_tokens(joined_text) > 50:
                chunks.append(Chunk(
                    text=joined_text,
                    heading_path=" > ".join(current_headings),
                    source_file=source_file,
                    page_estimate=1, # simplified
                    chunk_index=chunk_index
                ))
                chunk_index += 1
                current_text = []

            level = len(match.group(1))
            heading_text = match.group(2).strip()

            # Update current heading path
            if level <= len(current_headings):
                current_headings = current_headings[:level-1]
            current_headings.append(heading_text)

        current_text.append(line)

        # If chunk is getting too big, split it
        if estimate_tokens("\n".join(current_text)) >= max_tokens:
            joined_text = "\n".join(current_text).strip()
            chunks.append(Chunk(
                text=joined_text,
                heading_path=" > ".join(current_headings),
                source_file=source_file,
                page_estimate=1,
                chunk_index=chunk_index
            ))
            chunk_index += 1
            current_text = []

    # Add final chunk
    joined_text = "\n".join(current_text).strip()
    if joined_text:
        chunks.append(Chunk(
            text=joined_text,
            heading_path=" > ".join(current_headings) if current_headings else "Root",
            source_file=source_file,
            page_estimate=1,
            chunk_index=chunk_index
        ))

    return chunks
