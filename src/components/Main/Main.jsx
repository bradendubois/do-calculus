import * as React from 'react'
import loadable from "@loadable/component"
import {
    Switch,
    Route,
} from "react-router-dom";

import "./Main.scss"

const Main = () => {

    const GraphData = loadable(() => import("./GraphData/GraphData"))
    const ProbabilityQuery = loadable(() => import("./ProbabilityQuery/ProbabilityQuery"))
    const BackdoorPaths = loadable(() => import("./BackdoorPaths/BackdoorPaths"))
    const DoCalculus = loadable(() => import("./DoCalculus/DoCalculus"))

    return (

        <div className={"mainContent"}>
            <Switch>
                <Route path={"/graphData"}>
                    <GraphData/>
                </Route>

                <Route path={"/probabilityQuery"}>
                    <ProbabilityQuery/>
                </Route>

                <Route path={"/doCalculus"}>
                    <BackdoorPaths/>
                </Route>

                <Route path={"/backdoorPaths"}>
                    <DoCalculus/>
                </Route>

                <Route path={"/"}>
                    <h1>Select an option from the sidebar on the left.</h1>
                </Route>
            </Switch>
        </div>

    )
}

export default Main;