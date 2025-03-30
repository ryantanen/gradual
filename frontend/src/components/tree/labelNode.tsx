import { Handle, Position, NodeProps } from 'reactflow';

export default function CustomLabel({ data }: NodeProps) {
    return (
        <>
            <div className={`flex flex-col ${data.direction === "r" ? "items-start" : "items-end"}`}>
                <p className="font-medium">{data.label}</p>
                <p className="text-sm text-gray-500">{data.date}</p>
            </div>

            <Handle type="target" position={Position.Top} style={{ opacity: 0 }} />
            <Handle type="source" position={Position.Bottom} style={{ opacity: 0 }} />
        </>
    );
}