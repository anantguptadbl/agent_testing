import httpx
from crewai import Agent, Task, Crew


# -----------------------------------------------------------
# Tools (external calls)
# -----------------------------------------------------------

def call_api1_tool() -> dict:
    """
    Calls API1 and returns JSON response.
    """
    url = "http://127.0.0.1:8004/api1/getdata1"
    params = {"input": "hello"}

    response = httpx.get(url, params=params)
    response.raise_for_status()

    return response.json()


# -----------------------------------------------------------
# Agents
# -----------------------------------------------------------

agent1 = Agent(
    role="API Response Processor",
    goal="Validate and process API1 response when content is hello",
    backstory="Handles initial validation and transformation logic",
    allow_delegation=False,
    verbose=True,
)

agent2 = Agent(
    role="Async Processor",
    goal="Perform secondary processing on validated data",
    backstory="Responsible for additional enrichment or async-style logic",
    allow_delegation=False,
    verbose=True,
)

agent3 = Agent(
    role="Finalizer",
    goal="Finalize and consolidate the processed output",
    backstory="Ensures output is processed once and finalized cleanly",
    allow_delegation=False,
    verbose=True,
)


# -----------------------------------------------------------
# Tasks
# -----------------------------------------------------------

task_api1 = Task(
    description=(
        "Call API1 using the provided tool and return the JSON response. "
        "The response is expected to contain an output field."
    ),
    expected_output="JSON object returned by API1",
    agent=agent1,
    tools=[call_api1_tool],
)

task_agent1 = Task(
    description=(
        "Check if the API1 response output is 'hello'. "
        "If yes, process and prepare it for the next agent."
    ),
    expected_output="Validated and processed response",
    agent=agent1,
)

task_agent2 = Task(
    description=(
        "Perform secondary processing on the validated response "
        "and enrich or transform it as needed."
    ),
    expected_output="Enriched response",
    agent=agent2,
)

task_agent3 = Task(
    description=(
        "Finalize the response ensuring it is processed only once "
        "and prepare the final output."
    ),
    expected_output="Final processed output",
    agent=agent3,
)


# -----------------------------------------------------------
# Crew (orchestration)
# -----------------------------------------------------------

crew = Crew(
    agents=[agent1, agent2, agent3],
    tasks=[
        task_api1,
        task_agent1,
        task_agent2,
        task_agent3,
    ],
    verbose=True,
)


# -----------------------------------------------------------
# Entry point
# -----------------------------------------------------------

if __name__ == "__main__":
    result = crew.kickoff()
    print("\n===== FINAL RESULT =====\n")
    print(result)
