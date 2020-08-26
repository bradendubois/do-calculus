
export const StringifyProbabilityQuery = (y, x, w) => {

    // Build new Query String
    let query_string = y.join(", ")

    // There is a "body"
    if (x.length + w.length > 0) {
        query_string += " | "
    }

    if (x.length > 0) {
        query_string += " do(" + x.join(", ") + ") "
        if (w.length > 0) query_string += ", "
    } query_string += w.join(", ")

    return query_string
}
