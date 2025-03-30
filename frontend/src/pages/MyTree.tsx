import Navbar from "../components/navbar";
import Graph from "../components/tree/graph";
import { HiMail } from "react-icons/hi";
import { BsCalendarEvent } from "react-icons/bs";
import { IoDocumentTextOutline } from "react-icons/io5";
import { useState, FormEvent } from "react";

import gcal from "../assets/gcal.png";
import gmail from "../assets/gmail.png";
import pdf from "../assets/pdfs.png";
import { useAuth } from "@/auth/AuthContext";

function MyTree() {
    const { getAccessToken } = useAuth();

    // const fetchAIData = async () => {
    //   const token = await getAccessToken();
    //   const response = await fetch(`${import.meta.env.VITE_API_URL}/run-ai`, {
    //     headers: {
    //       Authorization: `Bearer ${token}`,
    //     },
    //   });
    //   if (!response.ok) throw new Error('Failed to fetch AI data');
    //   return response.json();
    // };

    const [bigHeader, setBigHeader] = useState<any>("Explore your life");
    const [smallInfo, setSmallInfo] = useState<any>("Feel free to click on any moment and learn more about what makes you you.");
    const [underlineColor, setUnderlineColor] = useState<any>("decoration-black-100");
    const [selectedFile, setSelectedFile] = useState<File | null>(null);

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.files && event.target.files[0]) {
            setSelectedFile(event.target.files[0]);
        }
    };


    const handleUpload = async (event: FormEvent) => {
        event.preventDefault();
        if (!selectedFile) return;

        const formData = new FormData();
        formData.append('file', selectedFile);
        try {
            const token = await getAccessToken();
            const response = await fetch(`${import.meta.env.VITE_API_URL}/upload-pdf`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Upload failed');
            }

            // Clear form and close modal
            setSelectedFile(null);
            document.getElementById('my_modal_1')?.querySelector('form')?.reset();
            (document.getElementById('my_modal_1') as HTMLDialogElement)?.close();

        } catch (error) {
            console.error('Error uploading file:', error);
            // You might want to show an error message to the user here
        }
    };

    return (
        <>
            <Navbar />

            <dialog id="my_modal_1" className="modal">
                <div className="modal-box">
                    <form method="dialog" className="modal-backdrop">
                        <button className="btn btn-sm btn-circle absolute right-2 top-2">✕</button>
                    </form>
                    <h3 className="font-bold text-xl py-3">Add Another Source</h3>

                    <form onSubmit={handleUpload}>
                        <div className="form-control w-full">
                            <h3 className="font-bold text-l my-3">New PDF</h3>
                            <input
                                type="file"
                                accept=".pdf"
                                onChange={handleFileChange}
                                className="file-input file-input-bordered w-full"
                            />
                            <button
                                type="submit"
                                disabled={!selectedFile}
                                className={`btn bg-accent-content shadow-sm mt-4 w-full ${selectedFile && "text-base-200"}`}
                            >
                                {/* <img src={pdf} className="h-6 w-6 mr-2" /> */}
                                Upload Document
                            </button>
                        </div>
                    </form>

                    <h3 className="font-bold text-l my-3">Already Connected</h3>
                    <div className="flex flex-wrap gap-3">
                        <button className="btn btn-outline btn-disabled">
                            <img src={gcal} className="h-6 w-6" />
                            Google Calendar
                        </button>
                        <button className="btn btn-outline btn-disabled">
                            <img src={gmail} className="h-5 w-auto" />
                            Gmail
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
                        <button className="btn btn-outline btn-block mt-5 p-5"
                            onClick={() => {
                                const modal = document.getElementById('my_modal_1') as HTMLDialogElement;
                                if (modal) modal.showModal();
                            }}
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
