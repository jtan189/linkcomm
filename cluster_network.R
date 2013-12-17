## parameters
alpha = 0.25

## input variables
##graph.file <- "ExampleDatasets/AuthorMapClean2.txt"
graph.file <- "ExampleDatasets/toyGraph.txt"
##nodes.attribs.file <- "ExampleDatasets/AuthorNameClean2.txt"
node.attr.file <- "ExampleDatasets/toyNodeAttributes.txt"
##edge.attribs.file <- "ExampleDatasets/ConfAttributeClean2.txt"
edge.attr.file <- "ExampleDatasets/toyEdgeAttributes.txt"
edge.dist.file <- "ExampleDatasets/toyGraph_edgedist.txt"

dist.attr <- function(edge.attr, e1, e2) {
    ## Return S_ij = | e1 INTERSECT e2 | / |e1 UNION e2 |
    sim <- sum(edge.attr[e1, ] & edge.attr[e2, ]) / sum(edge.attr[e1, ] | edge.attr[e2, ])
    return(1 - sim)
}


## run Python script for calculating edge distances
system("python2.7 get_edge_similarities.py ExampleDatasets/toyGraph.txt")

## read data
graph <- as.matrix(read.table(graph.file))
node.attr <- as.matrix(read.table(node.attr.file))
edge.attr <- as.matrix(read.table(edge.attr.file))
dist.edge <- as.matrix(read.table(edge.dist.file))

## populate distance matrix for edge attributes
num.edges = nrow(edge.attr)
dist.ea <- matrix(0, num.edges, num.edges)
for (i in 1:num.edges) {
    for (j in i:num.edges) {
        if (i != j) {
            dist.ea[j, i] <- dist.attr(edge.attr, i, j)
        }
    }
}

## combine distances for edge attributes with Jaccard distances for edges
dist.comb = alpha * dist.edge + (1 - alpha) * dist.ea

## debug
cat("graph\n")
print.default(graph)
cat("edge attr dist\n")
print.default(dist.ea)
cat("edge dist\n")
print.default(dist.edge)
cat("dist matrix\n")
print.default(dist.comb)

## convert to dist object
colnames(dist.comb) <- 1:num.edges
rownames(dist.comb) <- 1:num.edges
dist.comb <- as.dist(dist.comb)

## debug
cat("dist dist\n")
print(dist.comb)

## show various graphs/plots
invisible(readline(prompt = "Press [enter] to get link communities for the network."))
lc <- getLinkCommunities(graph, hcmethod = "average", edglim = 10^4, dist = dist.comb, plot = TRUE, verbose = TRUE)
cat("\n")
print(lc)

invisible(readline(prompt = "Press [enter] to display community membership for the top 20 nodes that belong to the most communities."))
plot(lc, type = "members")

invisible(readline(prompt = "Press [enter] to display network with edges coloured according to community membership."))
plot(lc, type = "graph")

## this may result in "Cluster 1 is not entirely nested in any other clusters."
invisible(readline(prompt = paste("Press [enter] to find and display a subnetwork where the nodes of one link",
                       " community are entirely nested within another link community.", sep="")))
getNestedHierarchies(lc, clusid = 1, plot = TRUE)

invisible(readline(prompt = "Press [enter] to plot the network with a Spencer circle layout."))
plot(lc, type = "graph", layout="spencer.circle")

invisible(readline(prompt = "Press [enter] to plot Spencer circle for the top-connected node."))
plot(lc, type = "graph", nodes = "YML007W", layout="spencer.circle", vertex.label.cex=0.8, jitter = 0.2))

invisible(readline(prompt = "Press [enter] to display the top modular networks."))
plot(lc, type = "commsumm", summary = "mod")
