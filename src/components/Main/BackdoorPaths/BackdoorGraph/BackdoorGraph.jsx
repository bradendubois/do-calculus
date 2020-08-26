import React, {useEffect} from "react"

import "./BackdoorGraph.scss"

/*
class BackdoorGraph extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            table: <p>Loading...</p>,
            x: this.props.x,
            y: this.props.y,
            z: this.props.z
        }

        this.construct_table = this.construct_table.bind(this)
        this.construct_table(this.props.x, this.props.y, this.props.z)
    }

    construct_table(x, y, z) {

        let taken = x.concat(y).concat(z)

        window.pywebview.api.v_to_parents_and_children().then(response => {
            let table = <table>
                <tr>
                    <th />
                    <th />
                    <th />
                    <th>Variable</th>
                    <th>Parents</th>
                    <th>Children</th>
                </tr>

                {response.map(row =>
                    <tr>
                        {taken.indexOf(row[0]) > -1 ?
                            <><td/><td/><td/></> :
                            <>
                                <td><button onClick={() => this.props.add_v("X", row[0])}>Add to X</button></td>
                                <td><button onClick={() => this.props.add_v("Y", row[0])}>Add to Y</button></td>
                                <td><button onClick={() => this.props.add_v("Z", row[0])}>Add to Z</button></td>
                            </>}
                        <td>{row[0]}</td>
                        <td>{row[1]}</td>
                        <td>{row[2]}</td>
                    </tr>)}
            </table>

            this.setState({table: table})
        })
    }

    // TODO - Why is this not firing...
    componentDidUpdate(prevProps, prevState, snapshot) {
        if (prevProps.x !== this.props.x || prevProps.y !== this.props.y || prevProps.z !== this.props.z) {
            this.setState({
                x: this.props.x,
                y: this.props.y,
                z: this.props.z
            })

            this.construct_table(this.props.x, this.props.y, this.props.z)
        }
    }

    render() {
        return (
            <div className={"tile backdoorGraph"}>
                {this.state.table}
            </div>
        )
    }
}
*/

const BackdoorGraph = ({ data }) => {

    const [table, setTable] = React.useState(<p>Loading...</p>)

    useEffect(() => {

        let taken = data.x.concat(data.y).concat(data.z)

        window.pywebview.api.v_to_parents_and_children().then(response => {

            let newTable = <table>
                <tr>
                    <th />
                    <th />
                    <th />
                    <th>Variable</th>
                    <th>Parents</th>
                    <th>Children</th>
                </tr>

                {response.map(row => {

                    let untaken = taken.indexOf(row[0]) === -1

                    return (
                        <tr>
                            <td>{untaken && <button onClick={() => data.add_v("X", row[0])}>Add to X</button>}</td>
                            <td>{untaken && <button onClick={() => data.add_v("Y", row[0])}>Add to Y</button>}</td>
                            <td>{untaken && <button onClick={() => data.add_v("Z", row[0])}>Add to Z</button>}</td>
                            <td>{row[0]}</td>
                            <td>{row[1]}</td>
                            <td>{row[2]}</td>
                        </tr>
                    )
                })}

            </table>

            setTable(newTable)
        })
    }, [data])

    return (
        <div className={"tile backdoorGraph"}>
            {table}
        </div>
    )

}

export default BackdoorGraph