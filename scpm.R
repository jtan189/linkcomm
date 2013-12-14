## parameters
alpha = 0.25

## input variables
##graph.file <- "ExampleDatasets/AuthorMapClean2.txt"
graph.file <- "ExampleDatasets/toyGraph.txt"
##nodes.attribs.file <- "ExampleDatasets/AuthorNameClean2.txt"
node.attribs.file <- "ExampleDatasets/toyNodeAttributes.txt"
##edge.attribs.file <- "ExampleDatasets/ConfAttributeClean2.txt"
edge.attribs.file <- "ExampleDatasets/toyEdgeAttributes.txt"


s.funct <- function(edge.attribs, e1, e2) {
    ## Return S_ij = | e1 INTERSECT e2 | / |e1 UNION e2 |
    ## TODO: Figure out what to call this.
    return(sum(edge.attribs[e1, ] & edge.attribs[e2, ]) / sum(edge.attribs[e1, ] | edge.attribs[e2, ]))
}


## read data
graph <- as.matrix(read.table(graph.file))
node.attribs <- as.matrix(read.table(node.attribs.file))
edge.attribs <- as.matrix(read.table(edge.attribs.file))

## what is S?
S <- matrix(0, nrow(graph), nrow(graph))
for (i in 1:nrow(graph) - 1) {
    for (j in (i + 1):nrow(graph)) {
        S[i, j] <- s.funct(edge.attribs, i, j)
    }
}

