import React from 'react'
import ReactDOM from 'react-dom'
import { HashRouter as Router } from "react-router-dom";

import FileSelector from "./components/FileSelector/FileSelector";
import Sidebar from "./components/Sidebar/Sidebar"
import Main from "./components/Main/Main"

import './index.scss'

const App = () => {

    const [contentSelected, toggleSelected] = React.useState(false)

    const load = (graph) => {

        // Load the graph given
        if (!contentSelected) {
            window.pywebview.api.load_file(graph)   //.then(() => {})
        }

        toggleSelected(!contentSelected)
    }

    return (
        <div id={"probability-app"}>
            <div id={"content"}>
                {contentSelected ?
                    <>
                        <Sidebar callback={toggleSelected}/>
                        <Main />
                    </> : <FileSelector callback={load}/>
                }
            </div>
        </div>
    )
}

const AppWrapper = () => {

    const [webviewReady, setReady] = React.useState(false)

    // Show content once pywebview is ready
    window.addEventListener('pywebviewready', () => {
        setReady(true)
    })

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