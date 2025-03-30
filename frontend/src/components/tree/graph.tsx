import ReactFlow, { Background, Controls, PanOnScrollMode } from 'reactflow';
import 'reactflow/dist/style.css';
import CustomNode from './node';
import CustomLabelTitle from './labelTitleNode';
import CustomLabel from './labelNode';


const nodes = [
    { id: 'title', data: { label: 'About you.' }, position: { x: 25, y: 10 }, type: 'customLabelTitle', className: 'text-4xl font-medium' },
    { id: '1', data: { label: 'Application', date: "1/2/23", direction: 'r', special: null }, position: { x: 250, y: 75 }, type: 'customNode' },
    { id: '2', data: {  label: 'Interview', date: "2/2/23", direction: 'r', special: null }, position: { x: 250, y: 175 }, type: 'customNode' },
    { id: '3', data: { label: 'Job Acquired', date: "3/2/23", direction: 'r', special: null }, position: { x: 250, y: 275 }, type: 'customNode' },
    { id: '4', data: { label: 'Promotion Already?!?', date: "4/2/23", direction: 'r', special: null }, position: { x: 250, y: 375 }, type: 'customNode' },
    { id: '7', data: { label: 'Literally CEO', date: "5/2/23", direction: 'r', special: 'merge' }, position: { x: 250, y: 475 }, type: 'customNode' },
    { id: '5', data: { label: 'Devise Scheme', date: "3/2/23", direction: 'l', special: 'branch' }, position: { x: 150, y: 275 }, type: 'customNode' },
    { id: '6', data: { label: 'Commit Crimes', date: "4/2/23", direction: 'l', special: 'branch' }, position: { x: 150, y: 375 }, type: 'customNode' },
];

const edges = [
    { id: 'e1-2', source: '1', target: '2', },
    { id: 'e2-3', source: '2', target: '3', },
    { id: 'e3-4', source: '3', target: '4', },
    { id: 'e2-5', source: '2', target: '5', },
    { id: 'e5-6', source: '5', target: '6', },
    { id: 'e6-7', source: '6', target: '7', },
    { id: 'e4-7', source: '4', target: '7', },
];

const nodeTypes = {
    customNode: CustomNode,
    customLabelTitle: CustomLabelTitle,
    customLabel: CustomLabel
};

interface GraphProps {
    className?: string;
}


export default function Graph({ className }: GraphProps) {
    return (
        <div className={className + " relative"}>
            <button className="absolute top-4 right-4 w-15 h-15 bg-black rounded-full flex items-center justify-center text-white hover:bg-gray-700 transition-colors z-10 text-2xl button">
                +
            </button>
            <ReactFlow nodes={nodes} edges={edges} 
                // fitView
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
                proOptions={{hideAttribution: true}}
                style={{
                    backgroundImage: "radial-gradient(circle, rgba(81, 119, 255, 0.3) 0%, rgba(255, 255, 255, 0) 70%)"
                }}
            >
            </ReactFlow>
        </div>
    );
}