import * as React from 'react'
import {
    Link,
} from "react-router-dom";

import "./Sidebar.scss"

const content = [
    ["graphData", <>Graph Data</>],
    ["probabilityQuery", <>Probability Query</>],
    ["doCalculus", <><i>do</i>-Calculus</>],
    ["backdoorPaths", <>Backdoor Paths</>]
]

const Sidebar = ({ callback }) =>

    <div className={"sidebar"}>

        {/* Map each content section to its own link on the sidebar; left = path, right = display text */}
        {content.map(entry => <Link to={`/${entry[0]}`}>{entry[1]}</Link>)}

        {/* Unload Button */}
        <Link
            id={"unloadButton"}
            to={"/"}
            onClick={() => callback()}
        >Unload Graph</Link>

    </div>

export default Sidebar;