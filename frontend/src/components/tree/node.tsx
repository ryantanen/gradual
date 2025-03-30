import { Handle, Position, NodeProps } from 'reactflow';

export default function CustomNode({ data }: NodeProps) {
    return (
        <>
            <div className={`relative rounded-full w-12 h-12 flex items-center justify-center border 
                    ${data.special === "branch" ? "bg-green-200" : data.special === "merge" ? "bg-emerald-300" : "bg-blue-200"}`
            }
            
            >
                <Handle type="target" position={Position.Top} style={{ opacity: 0 }} />
                <Handle type="source" position={Position.Bottom} style={{ opacity: 0 }} />
                <div className={`absolute -translate-y-1/2 top-1/2 flex flex-col ${data.direction === "r" ? "left-14" : "right-14"}`}>
                    <p className="font-medium">{data.label}</p>
                    <p className="text-sm text-gray-500">{data.date}</p>
                </div>
            </div>
        </>
    );
}