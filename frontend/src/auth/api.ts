interface Node {
  _id?: string;
  title: string;
  description: string;
  sources?: {
    kind: string;
    item: string;
  }[];
}

interface Branch {
  name: string;
  nodes: Node[];
}

interface BranchedNodeResponse {
  branches: Branch[];
}

interface GraphData {
  branches: Array<{
    _id: string;
    name: string;
    user_id: string;
    root_node: string | null;
  }>;
  nodes: Node[];
}

export const doSync = async (accessToken: string): Promise<void> => {
  await fetch(`${import.meta.env.VITE_API_URL}/begin-ai`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });
};

export const getNodes = async (accessToken: string): Promise<GraphData> => {
  const response = await fetch(`${import.meta.env.VITE_API_URL}/nodes`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });
  if (!response.ok) {
    throw new Error("Failed to fetch nodes");
  }
  return response.json();
};

export const generateAINodes = async (
  accessToken: string
): Promise<BranchedNodeResponse> => {
  const response = await fetch(
    `${import.meta.env.VITE_API_URL}/generate-ai-nodes`,
    {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    }
  );
  if (!response.ok) {
    throw new Error("Failed to generate AI nodes");
  }
  return response.json();
};
