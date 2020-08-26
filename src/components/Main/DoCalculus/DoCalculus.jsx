import React from "react";
import MathJax from "react-mathjax";

const Rule = ({ formula}) =>

    <MathJax.Provider>
        <MathJax.Node inline formula={formula} />
    </MathJax.Provider>

const Sigma = ({ over }) => {
    return <Rule formula={`\\sum_{${over.join(", ")}}`} />
}

class DoCalculus extends React.Component {

    constructor(props) {
        super(props);
    }

    render() {
        return (
            <div className={"contentSection"} id={"doCalculusContainer"}>
                <h1><i>do</i>-Calculus</h1>
                <div className={"mainDoCalculusContent"}>
                    <div className={"rules"}>
                        <ul>
                            <li><Rule formula={"P(y | \\hat{x}, z, w) = P(y | \\hat{x}, w)"} /> if <Rule formula={"(Y \\perp \\!\\!\\! \\perp  Z | X, W)_{G_{\\bar{x}}}"} /></li>
                            <li><Rule formula={"P(y | \\hat{x}, \\hat{z}, w) = P(y | \\hat{x}, z, w)"} /> if <Rule formula={"(Y \\perp \\!\\!\\! \\perp  Z | X, W)_{G_{\\bar{x}\\underline{Z}}}"} /></li>
                            <li><Rule formula={"P(y | \\hat{x}, \\hat{z}, w) = P(y | \\hat{x}, w)"} /> if <Rule formula={"(Y \\perp \\!\\!\\! \\perp  Z | X, W)_{G_{\\bar{X}\\bar{Z(W)}}}"} /></li>
                        </ul>
                        <Sigma over={["X1", "X2"]} />
                    </div>
                </div>
            </div>
        )
    }
}

export default DoCalculus