from json import JSONDecodeError

from jinja2 import BaseLoader, Environment

from opendevin.controller.agent import Agent
from opendevin.controller.state.state import State
from opendevin.core.exceptions import LLMOutputError
from opendevin.core.utils import json
from opendevin.events.action import Action, action_from_dict
from opendevin.llm.llm import LLM

from .instructions import instructions
from .registry import all_microagents


def parse_response(orig_response: str) -> Action:
    depth = 0
    start = -1
    for i, char in enumerate(orig_response):
        if char == '{':
            if depth == 0:
                start = i
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0 and start != -1:
                response = orig_response[start : i + 1]
                try:
                    action_dict = json.loads(response)
                    action = action_from_dict(action_dict)
                    return action
                except JSONDecodeError as e:
                    raise LLMOutputError(
                        'Invalid JSON in response. Please make sure the response is a valid JSON object.'
                    ) from e
    raise LLMOutputError('No valid JSON object found in response.')


def to_json(obj, **kwargs):
    """
    Serialize an object to str format
    """
    return json.dumps(obj, **kwargs)


class MicroAgent(Agent):
    prompt = ''
    agent_definition: dict = {}

    def __init__(self, llm: LLM):
        super().__init__(llm)
        if 'name' not in self.agent_definition:
            raise ValueError('Agent definition must contain a name')
        self.prompt_template = Environment(loader=BaseLoader).from_string(self.prompt)
        self.delegates = all_microagents.copy()
        del self.delegates[self.agent_definition['name']]

    def step(self, state: State) -> Action:
        latest_user_message = state.get_current_user_intent()
        prompt = self.prompt_template.render(
            state=state,
            instructions=instructions,
            to_json=to_json,
            delegates=self.delegates,
            latest_user_message=latest_user_message,
        )
        messages = [{'content': prompt, 'role': 'user'}]
        resp = self.llm.completion(messages=messages)
        action_resp = resp['choices'][0]['message']['content']
        state.num_of_chars += len(prompt) + len(action_resp)
        action = parse_response(action_resp)
        return action

    def search_memory(self, query: str) -> list[str]:
        return []
