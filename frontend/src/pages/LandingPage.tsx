import { Link } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { HiMail } from "react-icons/hi";
import { BsCalendarEvent } from "react-icons/bs";
import { IoDocumentTextOutline } from "react-icons/io5";
import ReactFlow, { PanOnScrollMode } from "reactflow";
import CustomNode from "@/components/tree/node";
import CustomLabelTitle from "@/components/tree/labelTitleNode";

const nodes = [
  { id: '1', data: { label: 'Application', date: "1/2/23", info: "What do you call a dog which is a really sophisticated DAG? A DOAG!!!!! Thats's not true, but I need to fill space.", direction: 'r', special: null }, position: { x: 250, y: 75 }, type: 'customNode', },
  { id: '2', data: { label: 'Interview', date: "2/2/23", direction: 'r', special: null, info: "Whwapkrngpiwrgpirwgpjawpjrgjrwipagt do you call a dog which is a really sophisticated DAG? A DOAG!!!!! Thats's not true, but I need to fill space." }, position: { x: 250, y: 175 }, type: 'customNode' },
  { id: '3', data: { label: 'Job Acquired', date: "3/2/23", direction: 'r', special: null, info: "uhwreguhowrgohrehgorwohgerohigeoh er ohgroghreog erj-ig erijgjepir pijg eripj reipjneroihgreiohriohergeg" }, position: { x: 250, y: 275 }, type: 'customNode' },
  { id: '4', data: { label: 'Promotion Already?!?', date: "4/2/23", direction: 'r', special: null, info: "OJNWrgowrnjgepjerpjheorhejpoerhpjophjoreepjohpojhrjopherjepohrjpo ngpijerpingeiprghipjerhgip" }, position: { x: 250, y: 375 }, type: 'customNode' },
  { id: '7', data: { label: 'Literally CEO', info: "e0iuhtgh0ier gohir hiorgoh reohg erhoig hioerg hoieghoi erhio ghoeir hoiregh ioergho ieohig rhiogrho igreohi erojihgre onigreoih egreg", date: "5/2/23", direction: 'r', special: 'merge' }, position: { x: 250, y: 475 }, type: 'customNode' },
  { id: '5', data: { label: 'Devise Scheme', info: "er0iogeriogijeorgijergijjreijpeirgjeirejipeipjgipjer ipj pije ipj gpiej pjiregipjerpij eipj ipjrg pjieg pij", date: "3/2/23", direction: 'l', special: 'branch' }, position: { x: 150, y: 275 }, type: 'customNode' },
  { id: '6', data: { label: 'Commit Crimes', info: "reiothgi0retgj i0rwji rejpig ejipg ipje psidpij jgprepj gropj eropjg ojperg pojerpojg eproj poj ojpe gjporeopj eropj pjog jope rg pjioerjgpo eopjr jrpogg jopejgop erjpog jopregjop gejpo jergpogjp rojpgeor epj rgojge proegproj", date: "4/2/23", direction: 'l', special: 'branch' }, position: { x: 150, y: 375 }, type: 'customNode' },
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
};

export const LandingPage = () => {
  return (
    <div className="min-h-screen bg-base-100 flex items-center justify-center"             style={{
      backgroundImage: "radial-gradient(circle at center, rgba(81, 119, 255, 0.25) 0%, rgba(255, 255, 255, 0) 70%)"
    }}>
      <div className="max-w-5xl w-full h-full relative flex">

        <div className="my-20 text-left mb-8 flex-5.5">
          <h1 className="text-7xl font-bold mb-4.5">Gradual.</h1>
          <p className="text-4xl text-gray-600 mb-6">
            Track the steps. See the climb.
          </p>
          <Link to="/login" className="btn btn-neutral btn-xl text-base-100">
            Get Started
          </Link>

          {/* Floating Cards */}
          <div className="absolute left-50 top-5/7 transform -translate-y-1/2 rotate-3">
            <div className="bg-white p-3 rounded-lg shadow-md flex items-center gap-2">
              <div className="p-2 bg-red-100 rounded-lg">
                <HiMail className="text-red-600 text-xl" />
              </div>
              <span>Super important email!</span>
            </div>
          </div>

          <div className="absolute left-20 top-3/7 transform -translate-y-1/2 -rotate-2">
            <div className="bg-white p-3 rounded-lg shadow-md flex items-center gap-2">
              <div className="p-2 bg-blue-100 rounded-lg">
                <BsCalendarEvent className="text-blue-600 text-xl" />
              </div>
              <span>Meeting with Professor!</span>
            </div>
          </div>

          <div className="absolute left-0 top-4/7 transform -rotate-3">
            <div className="bg-white p-3 rounded-lg shadow-md flex items-center gap-2">
              <div className="p-2 bg-gray-100 rounded-lg">
                <IoDocumentTextOutline className="text-gray-600 text-xl" />
              </div>
              <span>Taking CIS 1600!</span>
            </div>
          </div>
        </div>

        <div className="h-screen w-screen flex-4">
          <ReactFlow nodes={nodes} edges={edges}
            // fitView
            defaultViewport={{ x: -50, y: -10, zoom: 1.3 }}
            draggable={false}
            elementsSelectable={false}
            nodesConnectable={false}
            edgesFocusable={false}
            nodesFocusable={false}
            nodesDraggable={false}
            nodeTypes={nodeTypes}
            zoomOnDoubleClick={false}
            panOnScroll={false}
            panOnDrag={false}
            zoomOnScroll={false}
            zoomOnPinch={false}
            proOptions={{ hideAttribution: true }}
          >
          </ReactFlow>
        </div>
      </div>
    </div>
  );
};
