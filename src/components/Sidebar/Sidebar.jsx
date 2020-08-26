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

const Sidebar = () =>

    <div className={"sidebar"}>

        {content.map(entry => <Link to={`/${entry[0]}`}>{entry[1]}</Link>)}

        <Link
            id={"unloadButton"}
            to={"/"}
            onClick={() => this.props.callback()}
        >Unload Graph</Link>

    </div>

export default Sidebar;