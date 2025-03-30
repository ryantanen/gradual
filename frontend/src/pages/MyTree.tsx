import Navbar from "../components/navbar";
import Graph from "../components/tree/graph";
import { HiMail } from "react-icons/hi";
import { BsCalendarEvent } from "react-icons/bs";
import { IoDocumentTextOutline } from "react-icons/io5";

import gcal from "../assets/gcal.png";
import gmail from "../assets/gmail.png";
import pdf from "../assets/pdfs.png";
import { useState } from "react";

function MyTree() {
    const [bigHeader, setBigHeader] = useState<any>("In summary");
    const [smallInfo, setSmallInfo] = useState<any>("You, Willard Sun are a guy and that is very cool. You, Willard Sun are a guy and that is very cool. You, Willard Sun are a guy and that is very cool. You, Willard Sun are a guy and that is very cool.");
    const [underlineColor, setUnderlineColor] = useState<any>("decoration-black-100")

    return (
        <>
            <Navbar />

            <dialog id="my_modal_1" className="modal">
                <div className="modal-box">
                    <form method="dialog" className="modal-backdrop">
                        <button className="btn btn-sm btn-circle absolute right-2 top-2">✕</button>
                    </form>
                    <h3 className="font-bold text-xl mb-5">Add a new source.</h3>
                    <div className="flex flex-wrap gap-3">
                        <button className="btn btn-outline">
                            <img src={gcal} className="h-6 w-6" />
                            Google Calendar
                        </button>
                        <button className="btn btn-outline">
                            <img src={gmail} className="h-5 w-auto" />
                            Gmail
                        </button>
                        <button className="btn btn-outline">
                            <img src={pdf} className="h-6 w-6" />
                            Add a PDF
                        </button>
                    </div>


                </div>
                <form method="dialog" className="modal-backdrop">
                    <button>close</button>
                </form>
            </dialog>

            <div className="h-[calc(100vh-64px)] w-screen flex">
                <Graph className="flex-7" setHeader={setBigHeader} setInfo={setSmallInfo} setUnderlineColor={setUnderlineColor} />
                <div className="flex-3 border-l border-gray-300  overflow-y-scroll">
                    <div className="px-6 py-5 min-h-50">
                        <h1 className={`text-3xl pb-5 font-semibold underline ${underlineColor}`}>
                            {bigHeader}
                        </h1>
                        <p>
                            {smallInfo}
                        </p>
                    </div>
                    <div className="divider">SELECTED MOMENT</div>

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
                        <button className="mt-3 btn btn-outline btn-block p-5"
                            onClick={() => document.getElementById('my_modal_1')?.showModal()}
                        >
                            Add another source
                        </button>

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
