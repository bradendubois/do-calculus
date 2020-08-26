import React from 'react'
import ReactDOM from 'react-dom'
import { HashRouter as Router } from "react-router-dom";

import FileSelector from "./components/FileSelector/FileSelector";
import Sidebar from "./components/Sidebar/Sidebar"
import Main from "./components/Main/Main"

import './index.scss'

const App = () => {

    const [contentSelected, setSelected] = React.useState(false)

    // Load a graph file from the list presented to the user
    const load = (graph) => {

        // Load the graph given
        if (!contentSelected) {
            window.pywebview.api.load_file(graph).then(() => {
                setSelected(true)
            })

        // Unload
        } else {
            setSelected(false)
        }
    }

    return (
        <div id={"probability-app"}>
            <div id={"content"}>
                {contentSelected ?
                    <>
                        <Sidebar callback={setSelected}/>
                        <Main />
                    </> : <FileSelector callback={load}/>
                }
            </div>
        </div>
    )
}

/*
 *  Wrapper class that separates the logic of the "app" itself and library specific bookkeeping of ensuring modules
 * are only presented when the API is ready and setting up the Router system for navigation
 */
const AppWrapper = () => {

    // Wait for a signal when the webview API is loaded, then we can show the App
    const [webviewReady, setReady] = React.useState(false)
    window.addEventListener('pywebviewready', () => setReady(true))

    return (
        <Router>
            {webviewReady ? <App props={"pywebview"} /> : <div><h1>PyWebView launching...</h1></div>}
        </Router>
    )
}

ReactDOM.render(
    <AppWrapper />,
    document.getElementById('app')
)