from typing import Annotated, Optional, TypedDict
from langserve import RemoteRunnable
from langgraph.graph import StateGraph, START, END
import openai
from langchain_core.runnables import Runnable
from langchain_core.runnables import RunnableLambda
from langchain_core.prompt_values import PromptValue
from pydantic import BaseModel
from typer import prompt
from langchain_openai import ChatOpenAI
from langchain.tools import tool

class TxnState(BaseModel):  
    txn_id: str
    amount: float
    status: str

class AccountState(BaseModel):
    account_id: str
    account_type: Optional[str] = None 
    account_balance: Optional[float] = None
    unsettled_txns: Optional[list[TxnState]] = None


class AgentState(BaseModel):
    user_prompt: str
    user_id: str
    accounts: Optional[list[AccountState]] = None
    def to_string(self) -> str:
        return self.user_prompt
    
    def to_messages(self):
        # Return as a list of BaseMessages if needed
        pass

    def attributes_without_user_prompt(self):
        """Return all attributes except 'user_prompt' from the AgentState instance as a dict."""
        return {k: v for k, v in self.model_dump().items() if k != "user_prompt"}


# 1. Get user metadata (RemoteRunnable)

# Tool wrapper for get_account_balance_api
get_account_balance_api = RemoteRunnable("http://localhost:8001/get_account_balance")

@tool(
    args_schema=AgentState,
    description="Call remote API to update AgentState with account balance (input/output: AgentState)."
)
def call_get_account_balance(**kwargs) -> AgentState:
    """
    Calls the remote get_account_balance API and returns the updated AgentState.
    """
    state = AgentState(**kwargs)
    # Assuming the remote returns a dict compatible with AgentState
    result = get_account_balance_api.invoke(state.model_dump())
    return AgentState(**result)


# 3. Get Txn Details for an account (Runnable)
class TxnDetailsRunnable(Runnable):
    def invoke(self, account_id: str):
        # Placeholder: Replace with actual logic or API call
        return {"account_id": account_id, "txns": [
            {"id": "T1", "amount": 100, "status": "settled"},
            {"id": "T2", "amount": 50, "status": "unsettled"}
        ]}

txn_details_runnable = TxnDetailsRunnable()

# --- TOOL DEFINITIONS ---

# 2. Get Unsettled txns (WebSocket - simulated)
@tool(
    args_schema=AgentState,
    description="Update AgentState with unsettled txns (input/output: AgentState)."
)
def call_get_unsettled_txns(**kwargs) -> AgentState:
    """
    Update AgentState with unsettled transactions. Expects and returns AgentState with user_id, user_prompt, and accounts fields.
    """
    state = AgentState(**kwargs)
    if state.accounts is not None and len(state.accounts) > 0:
        state.accounts[0].unsettled_txns = ["T2"]
    return state

@tool(
    args_schema=AgentState,
    description="Update AgentState with user metadata (input/output: AgentState)."
)
def call_get_user_metadata(**kwargs) -> AgentState:
    """
    Update AgentState with user metadata. Expects and returns AgentState with user_id, user_prompt, and accounts fields.
    """
    state = AgentState(**kwargs)
    state.accounts = [AccountState(account_id="ACC123", account_type="savings", account_balance=0.0, unsettled_txns=[])]
    return state

@tool(
    args_schema=AgentState,
    description="Update AgentState with account details (input/output: AgentState)."
)
def call_get_account_details(**kwargs) -> AgentState:
    """
    Update AgentState with account details. Expects and returns AgentState with user_id, user_prompt, and accounts fields.
    """
    state = AgentState(**kwargs)
    if state.accounts is not None and len(state.accounts) > 0:
        state.accounts[0].account_balance = 1000.0
        state.accounts[0].unsettled_txns = ["T2"]
        state.accounts[0].account_type = "savings"
    return state

@tool(
    args_schema=AgentState,
    description="Update AgentState with transaction details (input/output: AgentState)."
)
def call_get_txn_details(**kwargs) -> AgentState:
    """
    Update AgentState with transaction details. Expects and returns AgentState with user_id, user_prompt, and accounts fields.
    """
    state = AgentState(**kwargs)
    if state.accounts is not None and len(state.accounts) > 0:
        state.accounts[0].unsettled_txns[0] = TxnState(txn_id=state.accounts[0].unsettled_txns[0], amount=50.0, status="unsettled")
    return state


# --- LLM-driven Orchestration ---
openai.api_key = ""  # Replace with your actual key or use os.environ

def get_prompt(state: AgentState) -> str:
    return f"""
        You need to provide accurate results for client queries. You have access to several tools and agents to get the information you need. 
        You must call the relevant tool(s) to answer the user's query, even if you think you know the answer. Do not answer directly from your own knowledge. 
        Always use the tools to fetch information. If you do not call any tool, your answer will be considered incomplete.
        If the information required to answer the user's query is not present in the current state, you must call one or more tools to retrieve it. 
        Do not provide a final answer unless all information has been retrieved via tool calls. If you have all the information, set tool_calls to an empty array and provide your answer in final_answer. Otherwise, list the tools you need to call with their parameters.
        Add the data from each tool into the state so that it can be used for subsequent decisions and the final answer when the prompt is invoked again. The user query is always present in state.user_prompt.
        You must output your answer as a JSON object that matches the following Pydantic model schema:
        Output Schema:        
        Agent State. Definitions are as follows

        class TxnState(BaseModel):  
            txn_id: str
            amount: float
            status: str
            # messages: Annotated[list[BaseMessage], "History"]

        class AccountState(BaseModel):
            account_id: str
            account_type: Optional[str] = None 
            account_balance: Optional[float] = None
            unsettled_txns: Optional[list[TxnState]] = None
            # messages: Annotated[list[BaseMessage], "History"]


        class AgentState(BaseModel):
            user_prompt: str
            user_id: str
            accounts: Optional[list[AccountState]] = None 

        The current user query is: {state.user_prompt}
        Respond with a JSON object: {{'tool_calls': [{{'tool_name': 'name', 'parameters': {{}}}}], 'final_answer': 'your final answer to the user'}}.
        The tool_calls array should contain the tools you want to call with their parameters. The final_answer field should contain the answer you want to provide to the user after calling the tools. If you need to call a tool, include it in the tool_calls array with the correct parameters. If you have all the information you need, set tool_calls to an empty array and provide your answer in final_answer.
        The current state: {AgentState.attributes_without_user_prompt(state)}
        If you have all the responses you will end the execution and not call any other agent. Set the "status" field in the response to "end"
        If you have already triggered a tool once, do not trigger it again in subsequent invocations. You should analyse the current state and check what is the most appropriate tool to call next until you have all the information needed to answer the user's query. Always use the tools to fetch information, do not answer directly from your own knowledge.

        You will not be getting any input from the user. Assume and move ahead with the information. Make use of tools to arrive at decisions and make use of that information in the agent state in subsequent invocations
        """

from langchain_core.messages import ToolMessage, HumanMessage

def get_response_from_llm(state: AgentState) -> str:
    response = get_prompt(state)
    llm_with_tools = ChatOpenAI(
        model="gpt-5",  # Use a function-calling capable model
        openai_api_key=openai.api_key,
        temperature=1,
    ).bind_tools([
        call_get_user_metadata,
        call_get_account_details,
        call_get_txn_details,
        call_get_account_balance,
        call_get_unsettled_txns
    ])

    TOOL_REGISTRY = {
        "call_get_user_metadata": call_get_user_metadata,
        "call_get_account_details": call_get_account_details,
        "call_get_txn_details": call_get_txn_details,
        "call_get_account_balance": call_get_account_balance,
        "call_get_unsettled_txns": call_get_unsettled_txns
    }

    response = llm_with_tools.invoke([HumanMessage(content=response)])

    # while getattr(response, "tool_calls", None) and not getattr(response, "status", None) == "end":
    while not getattr(response, "status", None) == "end":
        tool_messages = []
        if len(getattr(response, "tool_calls", [])) == 0:
            break
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            print("The tool being called is: ", tool_name)
            current_state = tool_call["args"]
            current_state = TOOL_REGISTRY[tool_name].invoke(current_state)
        # Always pass a flat list of message objects, not a nested list
        response = llm_with_tools.invoke([
            HumanMessage(content=get_prompt(current_state))
        ])
    # Print or return the final answer
    return getattr(response, "content", str(response))

if __name__ == "__main__":
    initial_state = AgentState(
        user_prompt="What is the savings account balance for userId U1 and ACC123?",
        user_id="U1",
        accounts=[AccountState(account_id="ACC123", account_type="savings")]
    )
    result = get_response_from_llm(initial_state)
    print("LLM Orchestrator Results:")
    print(result)