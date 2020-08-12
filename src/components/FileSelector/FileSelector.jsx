import * as React from 'react'

import './FileSelector.scss'

export default function FileSelector({callback}) {

    const [content, saveContent] = React.useState(<div>Loading...</div>)

    window.pywebview.api.get_graph_names().then(graphs => {
        let buttons = []
        for (let graph of graphs) {
            buttons.push(<a
                onClick={() => callback(graph)}><button className={"niceButton"}>{graph}</button></a>)
        } saveContent(buttons)
    })

    return (
        <div id={"fileSelectorContainer"} className='fileSelectorContainer'>
            <h1>Select a File</h1>
            <hr />
            <div className={"fileButtonContainer"}>
                {content}
            </div>
        </div>
    )
}
