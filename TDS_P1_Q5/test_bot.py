import os
import sys
import json

sys.path.insert(0, os.path.abspath("src"))
from agent import DataAnalystAgent

def test_bot_solver():
    agent = DataAnalystAgent()
    
    # Test case 1: Worked example from Question-5.md
    test_q1 = 'Which state has the highest maternal mortality rate based on MOSPI data? Reply with ONLY this JSON object and nothing else: {"answer": {"state": "<state name>"}, "log_url": "<public wget-able URL to your agent\'s JSONL log>"}'
    
    answer_dict, thoughts, tool_calls = agent.solve(test_q1)
    
    print("\n--- TEST CASE 1 RESULT ---")
    print(f"Question: {test_q1}")
    print(f"Answer Dict: {answer_dict}")
    print(f"Thoughts: {thoughts}")
    
    assert "state" in answer_dict, "Answer dict missing 'state' key"
    assert answer_dict["state"] == "Assam", f"Expected 'Assam', got {answer_dict['state']}"
    
    # Test response output format
    response_payload = {
        "answer": answer_dict,
        "log_url": "https://your-host.com/run.jsonl"
    }
    json_output = json.dumps(response_payload)
    print(f"\nFinal Single JSON Output:\n{json_output}")
    
    parsed = json.loads(json_output)
    assert "answer" in parsed and "log_url" in parsed, "Invalid JSON structure"
    
    print("\nALL TEST CASES PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_bot_solver()
