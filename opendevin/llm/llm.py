
from litellm import completion as litellm_completion
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_random_exponential
from litellm.exceptions import APIConnectionError, RateLimitError, ServiceUnavailableError
from functools import partial

from opendevin import config
from opendevin.logger import llm_prompt_logger, llm_response_logger, opendevin_logger

DEFAULT_API_KEY = config.get('LLM_API_KEY')
DEFAULT_BASE_URL = config.get('LLM_BASE_URL')
DEFAULT_MODEL_NAME = config.get('LLM_MODEL')
DEFAULT_API_VERSION = config.get('LLM_API_VERSION')
LLM_NUM_RETRIES = config.get('LLM_NUM_RETRIES')
LLM_MIN_WAIT = config.get('LLM_MIN_WAIT')
LLM_MAX_WAIT = config.get('LLM_MAX_WAIT')


class LLM:
    """
    The LLM class represents a Language Model instance.
    """

    def __init__(self,
                 model=DEFAULT_MODEL_NAME,
                 api_key=DEFAULT_API_KEY,
                 base_url=DEFAULT_BASE_URL,
                 api_version=DEFAULT_API_VERSION,
                 num_retries=LLM_NUM_RETRIES,
                 min_wait=LLM_MIN_WAIT,
                 max_wait=LLM_MAX_WAIT,
                 ):
        """
        Args:
            model (str, optional): The name of the language model. Defaults to LLM_MODEL.
            api_key (str, optional): The API key for accessing the language model. Defaults to LLM_API_KEY.
            base_url (str, optional): The base URL for the language model API. Defaults to LLM_BASE_URL. Not necessary for OpenAI.
            api_version (str, optional): The version of the API to use. Defaults to LLM_API_VERSION. Not necessary for OpenAI.
            num_retries (int, optional): The number of retries for API calls. Defaults to LLM_NUM_RETRIES.
            min_wait (int, optional): The minimum time to wait between retries in seconds. Defaults to LLM_MIN_TIME.
            max_wait (int, optional): The maximum time to wait between retries in seconds. Defaults to LLM_MAX_TIME.

        Attributes:
            model_name (str): The name of the language model.
            api_key (str): The API key for accessing the language model.
            base_url (str): The base URL for the language model API.
            api_version (str): The version of the API to use.
            completion (function): A decorator for the litellm completion function.
        """
        opendevin_logger.info(f'Initializing LLM with model: {model}')
        self.model_name = model
        self.api_key = api_key
        self.base_url = base_url
        self.api_version = api_version

        self._completion = partial(
            litellm_completion, model=self.model_name, api_key=self.api_key, base_url=self.base_url, api_version=self.api_version)

        completion_unwrapped = self._completion

        def rate_limited_attempt(retry_state):
            opendevin_logger.info(f'{retry_state.outcome.exception}. Attempt #{retry_state.attempt_number} | You can customize these settings in the configuration.')
            return True

        @retry(reraise=True,
               stop=stop_after_attempt(num_retries),
               wait=wait_random_exponential(min=min_wait, max=max_wait), retry=retry_if_exception_type((RateLimitError, APIConnectionError, ServiceUnavailableError)), after=rate_limited_attempt)
        def wrapper(*args, **kwargs):
            if 'messages' in kwargs:
                messages = kwargs['messages']
            else:
                messages = args[1]
            debug_message = ''
            for message in messages:
                debug_message += '\n\n----------\n\n' + message['content']
            llm_prompt_logger.debug(debug_message)
            resp = completion_unwrapped(*args, **kwargs)
            message_back = resp['choices'][0]['message']['content']
            llm_response_logger.debug(message_back)
            return resp
        self._completion = wrapper  # type: ignore

    @property
    def completion(self):
        """
        Decorator for the litellm completion function.
        """
        return self._completion

    def __str__(self):
        if self.api_version:
            return f'LLM(model={self.model_name}, api_version={self.api_version}, base_url={self.base_url})'
        elif self.base_url:
            return f'LLM(model={self.model_name}, base_url={self.base_url})'
        return f'LLM(model={self.model_name})'
