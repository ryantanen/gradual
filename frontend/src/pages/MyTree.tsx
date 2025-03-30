import Navbar from "../components/navbar";
import Graph from "../components/tree/graph";
import { HiMail } from "react-icons/hi";
import { BsCalendarEvent } from "react-icons/bs";
import { IoDocumentTextOutline } from "react-icons/io5";

function MyTree() {
    return (
        <>
            <Navbar />
            <div className="h-[calc(100vh-64px)] w-screen flex">
                <Graph className="flex-7" />

                <div className="flex-3 border-l border-gray-300">
                    <div className="px-6 py-5">
                        <h1 className="text-3xl pb-5 font-semibold">
                            In summary
                        </h1>
                        <p>
                            You, Willard Sun are a guy and that is very cool. You, Willard Sun are a guy and that is very cool. You, Willard Sun are a guy and that is very cool. You, Willard Sun are a guy and that is very cool.
                        </p>
                    </div>
                    <div className="px-6 py-5">
                        <h1 className="text-3xl pb-5 font-semibold">
                            What we're working with
                        </h1>
                        <div className="space-y-4 pl-5">
                            <div className="flex items-center gap-3">
                                <div className="p-2 bg-red-100 rounded-lg">
                                    <HiMail className="text-red-600 text-xl" />
                                </div>
                                <div>
                                    <span className="font-semibold">25,000</span> emails
                                </div>
                            </div>
                            <div className="flex items-center gap-3">
                                <div className="p-2 bg-blue-100 rounded-lg">
                                    <BsCalendarEvent className="text-blue-600 text-xl" />
                                </div>
                                <div>
                                    <span className="font-semibold">1,050</span> calendar events
                                </div>
                            </div>
                            <div className="flex items-center gap-3">
                                <div className="p-2 bg-gray-100 rounded-lg">
                                    <IoDocumentTextOutline className="text-gray-600 text-xl" />
                                </div>
                                <div>
                                    <span className="font-semibold">100</span> uploaded documents
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="px-6 py-5">
                        <h1 className="text-3xl pb-5 font-semibold">
                            Ready to show the world?
                        </h1>
                        <button className="btn btn-block bg-accent-content text-base-200 p-5">Share Timeline</button>
                    </div>
                </div>
            </div>
        </>
    )
}

export default MyTree;
