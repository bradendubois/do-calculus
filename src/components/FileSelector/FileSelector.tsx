import * as React from 'react'

import './FileSelector.scss'


export default function FileSelector({callback}) {

    const [content, saveContent] = React.useState(<div>Content Will Be Here</div>)

    // Use the event
    React.useEffect(() => {
        window.addEventListener('pywebviewready', () => {

            window.pywebview.api.get_graph_names().then(graphs => {
                let buttons = []
                for (let graph of graphs) {
                    buttons.push(<button onClick={() => callback(graph)}>{graph}</button>)
                }

                saveContent(buttons)
            })
        })
    }, [])

    return (
        <div className='editor-container'>
            {content}
        </div>
    )
}
