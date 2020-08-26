import React from 'react'
import loadable from "@loadable/component"
import {
    Switch,
    Route,
    Redirect
} from "react-router-dom";

import "./Main.scss"

const Main = () => {

    // Use some lazy loading for code splitting
    const GraphData = loadable(() => import("./GraphData/GraphData"))
    const ProbabilityQuery = loadable(() => import("./ProbabilityQuery/ProbabilityQuery"))
    const BackdoorPaths = loadable(() => import("./BackdoorPaths/BackdoorPaths"))
    const DoCalculus = loadable(() => import("./DoCalculus/DoCalculus"))

    return (
        <div className={"mainContent"}>
            <Switch>
                <Route exact path={"/"}>
                    <h1>Select an option from the sidebar on the left.</h1>
                </Route>

                <Route path={"/graphData"}>
                    <GraphData/>
                </Route>

                <Route path={"/probabilityQuery"}>
                    <ProbabilityQuery/>
                </Route>

                <Route path={"/doCalculus"}>
                    <DoCalculus/>
                </Route>

                <Route path={"/backdoorPaths"}>
                    <BackdoorPaths/>
                </Route>

                <Route path={"*"}>
                    <Redirect to={"/"} />
                </Route>
            </Switch>
        </div>
    )
}

export default Main;