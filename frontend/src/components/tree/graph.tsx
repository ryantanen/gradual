import ReactFlow, { useEdgesState, useNodesState, Position } from "reactflow";
import "reactflow/dist/style.css";
import CustomNode from "./node";
import CustomLabelTitle from "./labelTitleNode";
import CustomLabel from "./labelNode";
import { BsPlusCircleFill } from "react-icons/bs";
import { useEffect, useState } from "react";
import { getNodes } from "../../auth/api";
import { useAuth } from "@/auth/AuthContext";

interface NodeData {
  label: string;
  date: string;
  info: string;
  direction: "l" | "r";
  special: "branch" | "merge" | null;
  isSelected?: boolean;
}

const nodeTypes = {
  customNode: CustomNode,
  customLabelTitle: CustomLabelTitle,
  customLabel: CustomLabel,
};
/**
 * Fixes JSON strings that use invalid JavaScript-style single quotes instead of
 * double quotes required by the JSON specification.
 *
 * This function handles:
 * 1. Converting single quotes to double quotes for JSON property names and values
 * 2. Correctly preserving apostrophes in text content
 * 3. Properly escaping special characters
 *
 * @param {string} invalidJson - The invalid JSON string to fix
 * @returns {string} - Properly formatted JSON string
 */
function fixInvalidJson(invalidJson) {
  // Early return for empty input
  if (!invalidJson || invalidJson.trim() === "") {
    return "{}";
  }

  try {
    // First attempt: Try to parse directly (maybe it's already valid)
    JSON.parse(invalidJson);
    return invalidJson; // Already valid JSON
  } catch (_e) {
    // Not valid JSON, continue with fixing process
  }

  try {
    // Use Function constructor to safely evaluate the JS object literal
    // This is safer than eval() for this purpose
    const parseFunction = new Function("return " + invalidJson);
    const parsedData = parseFunction();

    // Use JSON.stringify to convert it to proper JSON with double quotes
    return JSON.stringify(parsedData, null, 2);
  } catch (_firstError) {
    // If that didn't work, try more manual approaches
    try {
      // Replace single quotes with double quotes, but be careful about apostrophes
      let fixedJson = invalidJson;

      // First, temporarily replace escaped single quotes
      fixedJson = fixedJson.replace(/\\'/g, "___ESCAPED_SINGLE_QUOTE___");

      // Handle quoted strings with apostrophes
      // Look for patterns like: 'text with apostrophe\'s more text'
      const apostropheRegex = /'([^']*?)'s\s/g;
      while (apostropheRegex.test(fixedJson)) {
        fixedJson = fixedJson.replace(apostropheRegex, "\"$1's ");
      }

      // Handle special case for apostrophes at end of strings
      fixedJson = fixedJson.replace(/'([^']*?)'s'/g, '"$1\'s"');

      // Now replace all remaining single quotes with double quotes
      fixedJson = fixedJson.replace(/'/g, '"');

      // Restore escaped single quotes
      fixedJson = fixedJson.replace(/___ESCAPED_SINGLE_QUOTE___/g, "'");

      // Try to parse the result
      JSON.parse(fixedJson);
      return fixedJson;
    } catch (_secondError) {
      // Last resort: most aggressive approach
      try {
        // Use a regex to identify each object and fix its properties
        const result = [];
        const objectPattern = /{[^{}]*}/g;
        let match;

        while ((match = objectPattern.exec(invalidJson)) !== null) {
          const obj = {};
          const objString = match[0];

          // Extract key-value pairs
          const keyValuePattern =
            /['"]?([\w]+)['"]?\s*:\s*['"]?([\w\s.,$@!?&()\-:;]+)['"]?/g;
          let kvMatch;

          while ((kvMatch = keyValuePattern.exec(objString)) !== null) {
            const key = kvMatch[1];
            const value = kvMatch[2].trim();

            // Try to determine if value should be a number or string
            const numValue = Number(value);
            obj[key] = isNaN(numValue) ? value : numValue;
          }

          result.push(obj);
        }

        return JSON.stringify(result, null, 2);
      } catch (_e) {
        throw new Error(`Unable to fix invalid JSON: ${_e.message}`);
      }
    }
  }
}

interface GraphProps {
  className?: string;
  setHeader: (arg0: string) => void;
  setInfo: (arg0: string) => void;
  setUnderlineColor: (arg0: string) => void;
}

export default function Graph({
  className,
  setHeader,
  setInfo,
  setUnderlineColor,
}: GraphProps) {
  console.log("Graph component rendered");
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [nodes, setNodes] = useNodesState([]);
  const [edges, setEdges] = useEdgesState([]);
  const [data, setData] = useState<any | null>(null);
  const { getAccessToken } = useAuth();

  useEffect(() => {
    console.log("Initial useEffect running - calling fetchAIData");
    fetchAIData();
  }, []);

  const fetchAIData = async () => {
    try {
      console.log("fetchAIData started");
      const accessToken = await getAccessToken().then((token) => {
        console.log("Got access token:", token ? "Token exists" : "No token");
        return token;
      });

      if (!accessToken) {
        console.error("No access token available");
        return;
      }

      console.log("Calling getNodes with access token");
      const nodes = await getNodes(accessToken);
      console.log("API Response - getNodes:", nodes);
      console.log("Setting data with nodes");
      setData(nodes);
    } catch (error) {
      console.error("Error in fetchAIData:", error);
    }
  };

  useEffect(() => {
    console.log("Data dependency useEffect triggered. Current data:", data);
    if (!data) {
      console.log("No data available, returning");
      return;
    }

    try {
      console.log("Starting data processing");
      const nodes = [
        {
          id: "title",
          data: { label: "About you." },
          position: { x: 25, y: 10 },
          type: "customLabelTitle",
        },
      ];
      console.log("Initial nodes array:", nodes);

      let edges = [];
      let prev_node = null;
      let level = 0;

      // Log the type and content of data
      console.log("Raw data type:", typeof data);
      console.log("Raw data content:", data);

      // Replace all single quotes with double quotes
      let d =
        typeof data === "string"
          ? data.replace(/'/g, '"')
          : JSON.stringify(data);
      console.log("After quote replacement:", d);

      d = fixInvalidJson(d);
      console.log("After fixing JSON:", d);

      const parsedData = typeof d === "string" ? JSON.parse(d) : d;
      console.log("Parsed data:", parsedData);
      console.log("Parsed data type:", typeof parsedData);
      console.log("Is array?", Array.isArray(parsedData));

      if (!Array.isArray(parsedData)) {
        console.error("parsedData is not an array:", parsedData);
        return;
      }

      console.log("Starting to process each node");
      for (let node of parsedData) {
        console.log("Processing node:", node);
        const newNode = {
          position: {
            x: 250,
            y: level * 100 + 75,
          },
          type: "customNode",
          id: node.id.toString(), // Ensure ID is a string
          data: {
            label: node.name,
            date: new Date(node.date).toLocaleDateString("en-US", {
              month: "numeric",
              day: "numeric",
              year: "2-digit",
            }),
            info: node.long_description,
            direction: "r",
            special: null,
            isSelected: false,
          },
          targetPosition: Position.Top,
          sourcePosition: Position.Bottom,
        };
        console.log("Created node structure:", newNode);
        nodes.push(newNode);
        console.log("Added node to nodes array");

        if (prev_node) {
          const newEdge = {
            id: `e${prev_node.id}-${node.id}`,
            source: prev_node.id.toString(),
            target: node.id.toString(),
            type: "smoothstep",
          };
          console.log("Created edge:", newEdge);
          edges.push(newEdge);
          console.log("Added edge:", `e${prev_node.id}-${node.id}`);
        }

        level += 1;
        prev_node = node;
      }

      console.log("Final nodes array:", nodes);
      console.log("Final edges array:", edges);

      console.log("Setting nodes and edges");
      setNodes(nodes);
      setEdges(edges);
    } catch (error) {
      console.error("Error processing data:", error);
      console.error("Error stack:", error.stack);
    }
  }, [data]);

  const onNodeClick = (
    _event: React.MouseEvent,
    node: { id: string; data: NodeData }
  ) => {
    setSelectedNode(node.id);
    setHeader(node.data.label);
    setInfo(node.data.info);
    setUnderlineColor(
      node.data.special === "branch"
        ? "decoration-green-200"
        : node.data.special === "merge"
        ? "decoration-emerald-300"
        : "decoration-blue-200"
    );
  };

  return (
    <div className={className + " relative"}>
      <dialog id="my_modal_2" className="modal">
        <div className="modal-box">
          <form method="dialog" className="modal-backdrop">
            <button className="btn btn-sm btn-circle absolute right-2 top-2">
              ✕
            </button>
          </form>
          <h3 className="font-bold text-xl">Add a new moment.</h3>
          <fieldset className="fieldset">
            <legend className="fieldset-legend">What happened?</legend>
            <textarea
              placeholder="Describe your moment."
              className="textarea w-full"
            ></textarea>
            <legend className="fieldset-legend">When did it happen?</legend>
            <input
              type="date"
              className="input w-full"
              placeholder="Type here"
            />
            <button className="btn mt-5 bg-accent-content text-base-200">
              Add your moment
            </button>
          </fieldset>
        </div>
        <form method="dialog" className="modal-backdrop">
          <button>close</button>
        </form>
      </dialog>

      <BsPlusCircleFill
        onClick={() =>
          (
            document.getElementById("my_modal_2") as HTMLDialogElement
          )?.showModal()
        }
        color="black"
        className="align-middle absolute top-4 right-4 w-15 h-15 rounded-full flex items-center justify-center text-white hover:fill-gray-700 transition-colors z-10 text-4xl button"
      />
      <ReactFlow
        nodes={nodes.map((node) => ({
          ...node,
          data: {
            ...node.data,
            isSelected: node.id === selectedNode,
          },
        }))}
        edges={edges}
        // fitView
        draggable={false}
        elementsSelectable={false}
        nodesConnectable={false}
        edgesFocusable={false}
        nodesFocusable={false}
        nodesDraggable={false}
        nodeTypes={nodeTypes}
        zoomOnDoubleClick={false}
        defaultViewport={{ x: 0, y: 0, zoom: 1.5 }}
        panOnScroll={true}
        proOptions={{ hideAttribution: true }}
        onNodeClick={onNodeClick}
        style={{
          backgroundImage:
            "radial-gradient(circle, rgba(81, 119, 255, 0.3) 0%, rgba(255, 255, 255, 0) 70%)",
        }}
      ></ReactFlow>
    </div>
  );
}
