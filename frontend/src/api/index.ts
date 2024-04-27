export async function fetchModels() {
  const response = await fetch(`/api/litellm-models`);
  return response.json();
}

export async function fetchAgents() {
  const response = await fetch(`/api/agents`);
  return response.json();
}

export async function fetchWorkspaceSubdirs() {
  const response = await fetch(`/api/workspace-subdirs`);
  return response.json();
}
