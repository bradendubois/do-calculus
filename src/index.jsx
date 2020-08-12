import React from 'react'
import ReactDOM from 'react-dom'

import FileSelector from "./components/FileSelector/FileSelector";
import Sidebar from "./components/Sidebar/Sidebar"
import Main from "./components/Main/Main"

import './index.scss'

const App = () => {

    const sidebarRef = React.createRef()
    const mainRef = React.createRef()

    const [webviewReady, setReady] = React.useState(false)
    const [contentSelected, setSelected] = React.useState(false)

    // Show content once pywebview is ready
    window.addEventListener('pywebviewready', () => {
        setReady(true)
    })

    // TODO - Unused
    const graph = (graph) => {

        // Load the graph given
        if (!contentSelected) {
            window.pywebview.api.load_file(graph).then(() => {
                let selector = document.getElementById("fileSelectorContainer");
                selector.style.animationName = "slideAway"
                selector.style.animationDuration = "2.0s";

                let content = document.getElementById("content")
                setTimeout(() => {
                    this.setState({selected: true})
                    content.style.animationName = "slideIn"
                    content.style.animationDuration = "1.0s"
                }, 2000)
            })
        }

        setSelected(!contentSelected)
    }

    return (
        <div id={"probability-app"}>
            {webviewReady ?
                <div id={"content"}>
                    {contentSelected ?
                    <>
                        <Sidebar mainRef={mainRef} callback={setSelected}/>
                        <Main ref={mainRef}/>
                    </> :
                        <FileSelector callback={graph}/>
                    }
                </div> :
                <div>
                    <p>PyWebView launching...</p>
                </div>
            }
        </div>
    )
}

ReactDOM.render(
    <App props={"pywebview"}/>,
    document.getElementById('app')
)