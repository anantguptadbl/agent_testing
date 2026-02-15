Feature: Orchestrator Chain
  Scenario: User sends hello, agents respond in sequence
    Given the api_path "orchestrator_code.requests.post" with payload '{"url": "http://127.0.0.1:8004/api1/getdata1", "params": {"input": "hello"}}' is mocked to return_value '{"content": "hello"}'
    And agent agent1 will respond with '{"messages": [{"role": "agent1", "content": "response1"}]}'
    And agent agent2 will respond with '{"messages": [{"role": "agent2", "content": "response2"}]}'
    And agent agent3 will respond with '{"messages": [{"role": "agent3", "content": "response3"}]}'
    When the user sends '{"messages": [{"role": "user", "content": "hello"}]}' and invokes the run_llm_orchestrator orchestrator
    Then agent agent1 should be invoked with messages containing '{'messages': [{'role': 'user', 'content': 'hello'}, {'content': 'hello'}]}'
    And agent agent2 should be invoked with messages containing '{'messages': [{'role': 'agent1', 'content': 'response1'}]}'
    And agent agent3 should be invoked with messages containing '{'messages': [{'role': 'agent2', 'content': 'response2'}]}'
