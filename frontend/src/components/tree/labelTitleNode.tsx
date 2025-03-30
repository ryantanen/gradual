import { Handle, Position, NodeProps } from 'reactflow';

export default function CustomLabelTitle({ data }: NodeProps) {
    return (
        <>
            <div className={`rounded-full flex items-center justify-center text-center`}>
                {data.label}
            </div>

            <Handle type="target" position={Position.Top} style={{ opacity: 0 }} />
            <Handle type="source" position={Position.Bottom} style={{ opacity: 0 }} />
        </>
    );
}