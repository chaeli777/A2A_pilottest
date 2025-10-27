"""
현재 에이전트들의 Agent Card 확인
"""
import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from examples.adk_with_gemini import GeminiResearchAgent, GeminiWriterAgent, GeminiReviewerAgent, GeminiReporterAgent

print("=" * 80)
print("현재 에이전트들의 Agent Card")
print("=" * 80)
print()

# A Agent: Research
print("A Agent: Research Agent")
print("-" * 80)
research = GeminiResearchAgent()
research_card = research.get_agent_card()
print(json.dumps(research_card, indent=2, ensure_ascii=False))
print()

# B Agent: Writer
print("B Agent: Writer Agent")
print("-" * 80)
writer = GeminiWriterAgent()
writer_card = writer.get_agent_card()
print(json.dumps(writer_card, indent=2, ensure_ascii=False))
print()

# C Agent: Reviewer
print("C Agent: Reviewer Agent")
print("-" * 80)
reviewer = GeminiReviewerAgent()
reviewer_card = reviewer.get_agent_card()
print(json.dumps(reviewer_card, indent=2, ensure_ascii=False))
print()

# D Agent: Reporter
print("D Agent: Reporter Agent")
print("-" * 80)
reporter = GeminiReporterAgent()
reporter_card = reporter.get_agent_card()
print(json.dumps(reporter_card, indent=2, ensure_ascii=False))
print()

print("=" * 80)
print("스킬 요약")
print("=" * 80)
print(f"A Agent (Research): {[s['name'] for s in research_card['skills']]}")
print(f"B Agent (Writer):   {[s['name'] for s in writer_card['skills']]}")
print(f"C Agent (Reviewer): {[s['name'] for s in reviewer_card['skills']]}")
print(f"D Agent (Reporter): {[s['name'] for s in reporter_card['skills']]}")
