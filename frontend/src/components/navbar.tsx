const Navbar = () => {
    return (
        <div className="navbar bg-accent-content shadow-sm text-base-200">
            <div className="flex-1">
                <a className="btn btn-ghost text-3xl">Gradual.</a>
            </div>
            <button className="btn mx-5">Share Timeline</button>
            <div className="flex-none">
                <div className="dropdown dropdown-end">
                    <div tabIndex={0} role="button" className="btn btn-ghost btn-circle avatar">
                        <div className="w-10 rounded-full">
                            <img
                                alt="Tailwind CSS Navbar component"
                                src="https://img.daisyui.com/images/stock/photo-1534528741775-53994a69daeb.webp" />
                        </div>
                    </div>
                    <ul
                        tabIndex={1}
                        className="menu menu-sm dropdown-content rounded-box z-1 mt-3 w-52 p-2 shadow bg-accent-content">
                        <li>
                            <a className="justify-between">
                                Profile
                                <span className="badge">New</span>
                            </a>
                        </li>
                        <li><a>Settings</a></li>
                        <li><a>Logout</a></li>
                    </ul>
                </div>
            </div>
        </div>
    )
}

export default Navbar;