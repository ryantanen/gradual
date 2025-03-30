import ReactFlow, { Background, Controls, PanOnScrollMode, useEdgesState, useNodesState } from 'reactflow';
import 'reactflow/dist/style.css';
import CustomNode from './node';
import CustomLabelTitle from './labelTitleNode';
import CustomLabel from './labelNode';
import { FaCirclePlus } from "react-icons/fa6";
import { BsPlusCircleFill } from "react-icons/bs";
import { useEffect, useState } from 'react';



const data = {
    "branches": [
      {
        "_id": "branch_main",
        "name": "Main Project",
        "user_id": "user_123",
        "root_node": "node_1"
      },
      {
        "_id": "branch_exploration",
        "name": "Alternative Approach",
        "user_id": "user_123",
        "root_node": "node_4"
      }
    ],
    "nodes": [
      {
        "_id": "node_1",
        "title": "Introduction",
        "description": "Overview of the project",
        "user_id": "user_123",
        "branch": "branch_main",
        "parents": [],
        "children": ["node_2"],
        "sources": [{ "kind": "pdf", "item": "pdf_001" }],
        "created_at": "2025-03-20T08:00:00Z",
        "updated_at": "2025-03-20T10:15:00Z",
        "root": true
      },
      {
        "_id": "node_2",
        "title": "Problem Statement",
        "description": "Defining the core problem",
        "user_id": "user_123",
        "branch": "branch_main",
        "parents": ["node_1"],
        "children": ["node_3", "node_4"],
        "sources": [{ "kind": "email", "item": "email_002" }],
        "created_at": "2025-03-21T09:30:00Z",
        "updated_at": "2025-03-21T12:00:00Z"
      },
      {
        "_id": "node_6",
        "title": "Exploratory Path",
        "description": "An alternative direction",
        "user_id": "user_123",
        "branch": "branch_exploration",
        "parents": ["node_4"],
        "children": ["node_8"],
        "sources": [{ "kind": "email", "item": "email_006" }],
        "created_at": "2025-03-24T09:45:00Z",
        "updated_at": "2025-03-24T12:00:00Z",
        "root": true
      },
      {
        "_id": "node_3",
        "title": "Background Research",
        "description": "Related work and prior studies",
        "user_id": "user_123",
        "branch": "branch_main",
        "parents": ["node_2"],
        "children": ["node_5"],
        "sources": [{ "kind": "pdf", "item": "pdf_003" }],
        "created_at": "2025-03-22T11:00:00Z",
        "updated_at": "2025-03-22T13:45:00Z"
      },
      {
        "_id": "node_4",
        "title": "Technical Challenges",
        "description": "Identified issues and risks",
        "user_id": "user_123",
        "branch": "branch_experimental",
        "parents": ["node_2"],
        "children": ["node_6"],
        "sources": [{ "kind": "photo", "item": "photo_004" }],
        "created_at": "2025-03-22T14:30:00Z",
        "updated_at": "2025-03-22T16:10:00Z"
      },
      {
        "_id": "node_5",
        "title": "Proposed Solution",
        "description": "Main approach being considered",
        "user_id": "user_123",
        "branch": "branch_main",
        "parents": ["node_3"],
        "children": ["node_7"],
        "sources": [{ "kind": "calendar", "item": "event_005" }],
        "created_at": "2025-03-23T10:00:00Z",
        "updated_at": "2025-03-23T11:30:00Z"
      },
      {
        "_id": "node_7",
        "title": "Implementation Plan",
        "description": "How to execute the solution",
        "user_id": "user_123",
        "branch": "branch_main",
        "parents": ["node_5"],
        "children": ["node_9"],
        "sources": [{ "kind": "pdf", "item": "pdf_007" }],
        "created_at": "2025-03-24T13:00:00Z",
        "updated_at": "2025-03-24T15:30:00Z"
      },
      {
        "_id": "node_8",
        "title": "Experimental Results",
        "description": "Findings from the alternative approach",
        "user_id": "user_123",
        "branch": "branch_exploration",
        "parents": ["node_6"],
        "children": ["node_10"],
        "sources": [{ "kind": "photo", "item": "photo_008" }],
        "created_at": "2025-03-25T08:30:00Z",
        "updated_at": "2025-03-25T10:45:00Z"
      },
      {
        "_id": "node_9",
        "title": "Final Evaluation",
        "description": "Assessing the implementation",
        "user_id": "user_123",
        "branch": "branch_main",
        "parents": ["node_7"],
        "children": ["node_11"],
        "sources": [{ "kind": "calendar", "item": "event_009" }],
        "created_at": "2025-03-26T11:30:00Z",
        "updated_at": "2025-03-26T14:00:00Z"
      },
      {
        "_id": "node_10",
        "title": "Integration with Main Plan",
        "description": "Merging findings from alternative approach",
        "user_id": "user_123",
        "branch": "branch_exploration",
        "parents": ["node_8"],
        "children": ["node_11"],
        "sources": [{ "kind": "email", "item": "email_010" }],
        "created_at": "2025-03-26T15:00:00Z",
        "updated_at": "2025-03-26T17:15:00Z"
      },
      {
        "_id": "node_11",
        "title": "Conclusion",
        "description": "Final summary and next steps",
        "user_id": "user_123",
        "branch": "branch_main",
        "parents": ["node_9", "node_10"],
        "children": [],
        "sources": [{ "kind": "pdf", "item": "pdf_011" }],
        "created_at": "2025-03-27T09:00:00Z",
        "updated_at": "2025-03-27T11:30:00Z"
      }
    ]
  }



// const nodes = [
//     { id: 'title', data: { label: 'About you.' }, position: { x: 25, y: 10 }, type: 'customLabelTitle', className: 'text-4xl font-medium' },
//     { id: '1', data: { label: 'Application', date: "1/2/23", info: "What do you call a dog which is a really sophisticated DAG? A DOAG!!!!! Thats's not true, but I need to fill space.", direction: 'r', special: null }, position: { x: 250, y: 75 }, type: 'customNode', },
//     { id: '2', data: { label: 'Interview', date: "2/2/23", direction: 'r', special: null, info: "Whwapkrngpiwrgpirwgpjawpjrgjrwipagt do you call a dog which is a really sophisticated DAG? A DOAG!!!!! Thats's not true, but I need to fill space." }, position: { x: 250, y: 175 }, type: 'customNode' },
//     { id: '3', data: { label: 'Job Acquired', date: "3/2/23", direction: 'r', special: null, info: "uhwreguhowrgohrehgorwohgerohigeoh er ohgroghreog erj-ig erijgjepir pijg eripj reipjneroihgreiohriohergeg" }, position: { x: 250, y: 275 }, type: 'customNode' },
//     { id: '4', data: { label: 'Promotion Already?!?', date: "4/2/23", direction: 'r', special: null, info: "OJNWrgowrnjgepjerpjheorhejpoerhpjophjoreepjohpojhrjopherjepohrjpo ngpijerpingeiprghipjerhgip" }, position: { x: 250, y: 375 }, type: 'customNode' },
//     { id: '7', data: { label: 'Literally CEO', info: "e0iuhtgh0ier gohir hiorgoh reohg erhoig hioerg hoieghoi erhio ghoeir hoiregh ioergho ieohig rhiogrho igreohi erojihgre onigreoih egreg", date: "5/2/23", direction: 'r', special: 'merge' }, position: { x: 250, y: 475 }, type: 'customNode' },
//     { id: '5', data: { label: 'Devise Scheme', info: "er0iogeriogijeorgijergijjreijpeirgjeirejipeipjgipjer ipj pije ipj gpiej pjiregipjerpij eipj ipjrg pjieg pij", date: "3/2/23", direction: 'l', special: 'branch' }, position: { x: 150, y: 275 }, type: 'customNode' },
//     { id: '6', data: { label: 'Commit Crimes', info: "reiothgi0retgj i0rwji rejpig ejipg ipje psidpij jgprepj gropj eropjg ojperg pojerpojg eproj poj ojpe gjporeopj eropj pjog jope rg pjioerjgpo eopjr jrpogg jopejgop erjpog jopregjop gejpo jergpogjp rojpgeor epj rgojge proegproj", date: "4/2/23", direction: 'l', special: 'branch' }, position: { x: 150, y: 375 }, type: 'customNode' },
// ];

// const edges = [
//     { id: 'e1-2', source: '1', target: '2', },
//     { id: 'e2-3', source: '2', target: '3', },
//     { id: 'e3-4', source: '3', target: '4', },
//     { id: 'e2-5', source: '2', target: '5', },
//     { id: 'e5-6', source: '5', target: '6', },
//     { id: 'e6-7', source: '6', target: '7', },
//     { id: 'e4-7', source: '4', target: '7', },
// ];


const nodeTypes = {
    customNode: CustomNode,
    customLabelTitle: CustomLabelTitle,
    customLabel: CustomLabel
};

interface GraphProps {
    className?: string;
    setHeader: (arg0: string) => void;
    setInfo: (arg0: string) => void;
    setUnderlineColor: (arg0: string) => void;
}

export default function Graph({ className, setHeader, setInfo, setUnderlineColor }: GraphProps) {
    const [selectedNode, setSelectedNode] = useState<string | null>(null);

    const [nodes, setNodes] = useNodesState([]);
    const [edges, setEdges] = useEdgesState([]);

    useEffect(() => {
        let nodes = [{ id: 'title', data: { label: 'About you.' }, position: { x: 25, y: 10 }, type: 'customLabelTitle', className: 'text-4xl font-medium' }];
        let edges = [];
        
        let prev_node = null;
    


        // start w/ main branch
        let curr_branch = "branch_main";
        let remaining_branches = data.branches.filter(branch => branch._id !== "branch_main");

        while (true) {
            let curr_node_id = data.branches.find(branch => branch._id === curr_branch)?.root_node;
            let curr_node = data.nodes.find(nodes => nodes._id === curr_node_id)
            
            prev_node = data.nodes.find(node => node._id === curr_node?.parents[0])
            console.log(prev_node)

            
            console.log(curr_node)

            // Get root node's level
            console.log(nodes)
            console.log(nodes.find(n => n.id === curr_node?.parents[0]))
            let level = curr_branch === "branch_main" ? 0 : (nodes.find(n => n.id === curr_node?.parents[0])?.position.y - 75) / 100 + 1;
            console.log(level)
            
            
    
            while (curr_node) {
                nodes.push({ position: { x: curr_branch == "branch_main" ? 250 : 150, y: (level * 100) + 75 }, type: 'customNode', id: curr_node_id, data: { id: curr_node._id, label: curr_node?.title, date: curr_node?.created_at, info: curr_node?.description, direction: curr_branch == "branch_main" ? "r" : "l", special: curr_node?.parents?.length > 1 ? "merge" : curr_node?.branch != "branch_main" ? "branch" : null, } })        
        
                // make an edge b/w prev node and this one
                if (prev_node) {
                    edges.push({ id: `e${prev_node._id}-${curr_node._id}`, source: prev_node._id, target: curr_node._id, })
                    console.log(edges)
                }
    
                prev_node = curr_node;
    
                curr_node_id = curr_node.children.find(child_id => data.nodes.find(node => node._id == child_id)?.branch == curr_branch)
                
                if (!curr_node_id && curr_branch != "branch_main") {
                    let final_node = data.nodes.find(node => node._id == curr_node.children[0])
                    console.log(final_node)

                    if (final_node) 
                        edges.push({ id: `e${curr_node._id}-${final_node._id}`, source: prev_node._id, target: final_node._id, })
                }

                curr_node = data.nodes.find(nodes => nodes._id === curr_node_id)
                level++;
            }

            console.log(remaining_branches)

            if (remaining_branches.length <= 0) {
                break
            }

            curr_branch = remaining_branches.pop()?._id;

            
            console.log(curr_branch)
        }


        console.log(edges)
        setNodes(nodes)
        setEdges(edges)
        

        
    }, [data])


    const onNodeClick = (event: React.MouseEvent, node: any) => {
        setSelectedNode(node.id);
        setHeader(node.data.label);
        setInfo(node.data.info);
        setUnderlineColor(node.data.special === "branch" ? "decoration-green-200" : node.data.special === "merge" ? "decoration-emerald-300" : "decoration-blue-200")
    };

    return (
        <div className={className + " relative"}>

            <dialog id="my_modal_2" className="modal">
                <div className="modal-box">
                    <form method="dialog" className="modal-backdrop">
                        <button className="btn btn-sm btn-circle absolute right-2 top-2">✕</button>
                    </form>
                    <h3 className="font-bold text-xl">Add a new moment.</h3>
                    <fieldset className="fieldset">
                        <legend className="fieldset-legend">What happened?</legend>
                        <textarea placeholder="Describe your moment." className="textarea w-full"></textarea>
                        <legend className="fieldset-legend">When did it happen?</legend>
                        <input type="date" className="input w-full" placeholder="Type here" />
                        <button className="btn mt-5 bg-accent-content text-base-200">Add your moment</button>
                    </fieldset>

                </div>
                <form method="dialog" className="modal-backdrop">
                    <button>close</button>
                </form>
            </dialog>

            <BsPlusCircleFill
                onClick={() => document.getElementById('my_modal_2')?.showModal()}
                color="black"
                className="align-middle absolute top-4 right-4 w-15 h-15 rounded-full flex items-center justify-center text-white hover:fill-gray-700 transition-colors z-10 text-4xl button" 
            />
            <ReactFlow nodes={nodes.map(node => ({
                ...node,
                data: {
                    ...node.data,
                    isSelected: node.id === selectedNode
                }
            }))} edges={edges}
                fitView
                draggable={false}
                elementsSelectable={false}
                nodesConnectable={false}
                edgesFocusable={false}
                nodesFocusable={false}
                nodesDraggable={false}
                nodeTypes={nodeTypes}
                zoomOnDoubleClick={false}
                // minZoom={1.5}
                // maxZoom={1.5}
                defaultViewport={{ x: 0, y: 0, zoom: 1.5 }}
                panOnScroll={true}
                // panOnDrag={false}
                // panOnScrollMode={PanOnScrollMode.Vertical}
                proOptions={{ hideAttribution: true }}
                onNodeClick={onNodeClick}
                style={{
                    backgroundImage: "radial-gradient(circle, rgba(81, 119, 255, 0.3) 0%, rgba(255, 255, 255, 0) 70%)"
                }}
            >
            </ReactFlow>
        </div>
    );
}