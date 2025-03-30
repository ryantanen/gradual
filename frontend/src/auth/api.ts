interface Node {
  _id: string;
  title: string;
  description: string;
  parents: string[];
  children: string[];
  sources: {
    kind: string;
    item: string;
  }[];
  branch: string;
  user_id: string;
  created_at: string;
  updated_at: string;
  root: boolean;
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

export const doSync = () => {};

export const getNodes = async (accessToken: string): Promise<any> => {
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
