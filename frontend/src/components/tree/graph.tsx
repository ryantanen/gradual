import ReactFlow, {
  Background,
  Controls,
  PanOnScrollMode,
  useEdgesState,
  useNodesState,
} from "reactflow";
import "reactflow/dist/style.css";
import CustomNode from "./node";
import CustomLabelTitle from "./labelTitleNode";
import CustomLabel from "./labelNode";
import { FaCirclePlus } from "react-icons/fa6";
import { BsPlusCircleFill } from "react-icons/bs";
import { useEffect, useState } from "react";
import { getNodes } from "../../auth/api";
import { useAuth } from "@/auth/AuthContext";


interface NodeData {
  id: string;
  label: string;
  date: string;
  info: string;
  direction: "l" | "r";
  special: "branch" | "merge" | null;
}

const nodeTypes = {
  customNode: CustomNode,
  customLabelTitle: CustomLabelTitle,
  customLabel: CustomLabel,
};

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
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [nodes, setNodes] = useNodesState([]);
  const [edges, setEdges] = useEdgesState([]);
  const [data, setData] = useState<any | null>(null);
  const { getAccessToken } = useAuth();

  useEffect(() => {
    fetchAIData();
  }, []);

  const fetchAIData = async () => {
    const accessToken = await getAccessToken().then((token) => token);
    if (!accessToken) return;
    const nodes = await getNodes(accessToken);
    setData(nodes);
  };

  useEffect(() => {
    if (!data?.branches) return;
    const nodes = [
      {
        id: "title",
        data: { label: "About you." },
        position: { x: 25, y: 10 },
        type: "customLabelTitle",
        className: "text-4xl font-medium",
      },
    ];
    let edges = [];
    
    console.log(data)


    let prev_node = null;
    let level = 0;

    for (let node of data) {
        nodes.push({
            position: {
                x: 250,
                y: level * 100 + 75,
            },
            type: "customNode",
            id: node.id,
            data: {
                id: node.id,
                label: node.title,
                date: new Date(node.created_at).toLocaleDateString('en-US', {month: 'numeric', day: 'numeric', year: '2-digit'}),
                info: node.description,
                direction: "r",
                special: null
            }
            })
        if (prev_node) {
          edges.push({
            id: `e${prev_node.id}-${node.id}`,
            source: prev_node.id,
            target: node.id,
          });
        }

        level += 1;
        prev_node = node;
    }


    // // start w/ main branch
    // let curr_branch = data.branches.find(branch => branch.name == "branch_main")?._id;
    // const main_branch_id = curr_branch;
    // let remaining_branches = data.branches.filter(
    //   (branch) => branch._id !== "branch_main"
    // );

    // while (true) {
    //   let curr_node_id = data.branches.find(
    //     (branch) => branch._id === curr_branch
    //   )?.root_node;
    //   if (!curr_node_id) break;

    //   let curr_node = data.nodes.find((node) => node._id === curr_node_id);
    //   console.log("OTGUH3ouhrghue", curr_node)
    //   if (!curr_node) break;

    //   prev_node = data.nodes.find((node) => node._id === curr_node.parents[0]);

    //   // Get root node's level
    //   let level =
    //     curr_branch === main_branch_id || curr_branch.includes("main")
    //       ? 0
    //       : (nodes.find((n) => n.id === curr_node.parents[0])?.position.y ??
    //           0 - 75) /
    //           100 +
    //         1;

    //   while (curr_node) {
    //     // console.log("ROOT", curr_node)
    //     nodes.push({
    //       position: {
    //         x: curr_branch === main_branch_id || curr_branch.includes("main") ? 250 : 150,
    //         y: level * 100 + 75,
    //       },
    //       type: "customNode",
    //       id: curr_node_id,
    //       data: {
    //         id: curr_node._id,
    //         label: curr_node.title,
    //         date: new Date(curr_node.created_at).toLocaleDateString('en-US', {month: 'numeric', day: 'numeric', year: '2-digit'}),
    //         info: curr_node.description,
    //         direction: curr_branch ===  main_branch_id || curr_branch.includes("main") ? "r" : "l",
    //         special:
    //           curr_node.parents.length > 1
    //             ? "merge"
    //             : curr_node.branch !== main_branch_id || curr_branch.includes("main") && !curr_node.branch.includes("main")
    //             ? "branch"
    //             : null,
    //       } as NodeData,
    //     });

    //     // make an edge b/w prev node and this one
    //     if (prev_node) {
    //       edges.push({
    //         id: `e${prev_node._id}-${curr_node._id}`,
    //         source: prev_node._id,
    //         target: curr_node._id,
    //       });
    //     }

    //     prev_node = curr_node;

    //     curr_node_id = curr_node.children.find(
    //       (child_id) =>
    //         data.nodes.find((node) => node._id === child_id)?.branch ===
    //         curr_branch
    //     );

    //     if (!curr_node_id && !curr_branch?.includes("branch_main")) {
    //       let final_node = data.nodes.find(
    //         (node) => node._id === curr_node.children[0]
    //       );

    //       if (final_node) {
    //         edges.push({
    //           id: `e${curr_node._id}-${final_node._id}`,
    //           source: prev_node._id,
    //           target: final_node._id,
    //         });
    //       }
    //     }

    //     curr_node = data.nodes.find((node) => node._id === curr_node_id);
    //     level++;
    //   }

    //   if (remaining_branches.length <= 0) {
    //     break;
    //   }

    //   curr_branch = remaining_branches.pop()?._id ?? "branch_main";
    // }

    setNodes(nodes);
    setEdges(edges);
  }, [data]);

  const onNodeClick = (
    event: React.MouseEvent,
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
        fitView
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
