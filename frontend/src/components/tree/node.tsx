import { Handle, Position, NodeProps } from 'reactflow';

export default function CustomNode({ data }: NodeProps) {
    return (
        <>
            <div className="group relative">
                <div className={`relative rounded-full w-12 h-12 flex items-center justify-center border transition-all duration-200
                        ${data.special === "branch" ? "bg-green-200" : data.special === "merge" ? "bg-emerald-300" : "bg-blue-200"}
                        ${data.isSelected ? "ring-4 ring-blue-400 scale-110 shadow-lg" : ""}
                        hover:scale-105 cursor-pointer`
                }
                >
                    <Handle type="target" position={Position.Top} style={{ opacity: 0 }} />
                    <Handle type="source" position={Position.Bottom} style={{ opacity: 0 }} />
                    <div className={`absolute -translate-y-1/2 top-1/2 flex flex-col ${data.direction === "r" ? "left-14" : "right-14"}`}>
                        <p className="font-medium">{data.label}</p>
                        <p className="text-sm text-gray-500">{data.date}</p>
                    </div>
                </div>
                
            </div>
        </>
    );
}