import langfuse
from langfuse import Langfuse

print(f"langfuse version: {langfuse.__version__ if hasattr(langfuse, '__version__') else 'unknown'}")
print(f"langfuse.get_client exists: {hasattr(langfuse, 'get_client')}")
if hasattr(langfuse, 'get_client'):
    client = langfuse.get_client()
    print(f"get_client() has start_as_current_observation: {hasattr(client, 'start_as_current_observation')}")

l_instance = Langfuse()
print(f"Langfuse instance has start_as_current_observation: {hasattr(l_instance, 'start_as_current_observation')}")
print(f"langfuse module has start_as_current_observation: {hasattr(langfuse, 'start_as_current_observation')}")
print(f"langfuse module has observe: {hasattr(langfuse, 'observe')}")
