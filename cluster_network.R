## parameters
alpha = 0.25
save.img = TRUE
use.edge.attr = FALSE

## data input variables

## dblp
## noname.graph.file <- "ExampleDatasets/dblp/AuthorMapClean2.txt"
## graph.file <- "ExampleDatasets/dblp/AuthorMapClean2.txt"
## node.attr.file <- "ExampleDatasets/dblp/AuthorNameClean2.txt"
## edge.attr.file <- "ExampleDatasets/dblp/ConfAttributeClean2.txt"
## edge.dist.file <- "ExampleDatasets/dlbp/AuthorMapClean2_edgedist.txt"

## toy graph
noname.graph.file <- "ExampleDatasets/toy/toyGraph.txt"
graph.file <- "ExampleDatasets/toy/toyGraph_named.txt"
node.attr.file <- "ExampleDatasets/toy/toyNodeAttributes.txt"
edge.attr.file <- "ExampleDatasets/toy/toyEdgeAttributes.txt"
edge.dist.file <- "ExampleDatasets/toy/toyGraph_edgedist.txt"

dist.attr <- function(edge.attr, e1, e2) {
    ## Return S_ij = | e1 INTERSECT e2 | / |e1 UNION e2 |
    sim <- sum(edge.attr[e1, ] & edge.attr[e2, ]) / sum(edge.attr[e1, ] | edge.attr[e2, ])
    return(1 - sim)
}

if (use.edge.attr) {
    ## run Python script for calculating edge distances
    system(paste("python2.7 get_edge_similarities.py", noname.graph.file, sep=" "))
}

## read data
graph <- as.matrix(read.table(graph.file))
node.attr <- as.matrix(read.table(node.attr.file))
dist.edge <- as.matrix(read.table(edge.dist.file))

if (use.edge.attr) {
    edge.attr <- as.matrix(read.table(edge.attr.file))

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
}



## debug
## cat("graph\n")
## print.default(graph)
## cat("edge attr dist\n")
## print.default(dist.ea)
## cat("edge dist\n")
## print.default(dist.edge)
## cat("dist matrix\n")
## print.default(dist.comb)

if (use.edge.attr) {
    ## convert to dist object
    colnames(dist.comb) <- 1:num.edges
    rownames(dist.comb) <- 1:num.edges
    dist.comb <- as.dist(dist.comb)
}

## debug
## cat("dist dist\n")
## print(dist.comb)

## show various graphs/plots
invisible(readline(prompt = "\nPress [enter] to get link communities for the network."))
if (save.img) {
    png(filename=paste("lc_", alpha, ".png", sep=""))
    if (use.edge.attr) {
        lc <- getLinkCommunities(graph, hcmethod = "average", dist = dist.comb, plot = TRUE, verbose = TRUE)
    } else {
        lc <- getLinkCommunities(graph, hcmethod = "average", plot = TRUE, verbose = TRUE)
    }
        
    dev.off()
} else {
    if (use.edge.attr) {
        lc <- getLinkCommunities(graph, hcmethod = "average", dist = dist.comb, plot = TRUE, verbose = TRUE)
    } else {
        lc <- getLinkCommunities(graph, hcmethod = "average", plot = TRUE, verbose = TRUE)
    }
}
cat("\n")
print(lc)

invisible(readline(prompt = "\nPress [enter] to display community membership for the top 20 nodes that belong to the most communities."))
if (save.img) {
    png(filename=paste("top20_", alpha, ".png", sep=""))
    plot(lc, type = "members")
    dev.off()
} else {
    plot(lc, type = "members")
}

invisible(readline(prompt = "\nPress [enter] to display network with edges coloured according to community membership."))
if (save.img) {
    png(filename=paste("edge_comm_", alpha, ".png", sep=""))
    plot(lc, type = "graph")
    dev.off()
} else {
    plot(lc, type = "graph")
}

## this may result in "Cluster 1 is not entirely nested in any other clusters."
invisible(readline(prompt = paste("\nPress [enter] to find and display a subnetwork where the nodes of one link",
                       " community are entirely nested within another link community.", sep="")))
getNestedHierarchies(lc, clusid = 1, plot = TRUE)

invisible(readline(prompt = "\nPress [enter] to plot the network with a Spencer circle layout."))
if (save.img) {
    png(filename=paste("spencer_", alpha, ".png", sep=""))
    plot(lc, type = "graph", layout="spencer.circle")
    dev.off()
} else {
    plot(lc, type = "graph", layout="spencer.circle")
}

if (length(lc$clusters) > 1) {
    invisible(readline(prompt = "\nPress [enter] to plot Spencer circle for the top-connected node."))
    if (save.img) {
        png(filename=paste("spencertop_", alpha, ".png", sep=""))
        plot(lc, type = "graph", nodes = "YML007W", layout="spencer.circle", vertex.label.cex=0.8, jitter = 0.2)
        dev.off()
    } else {
        plot(lc, type = "graph", nodes = "YML007W", layout="spencer.circle", vertex.label.cex=0.8, jitter = 0.2)
    }
}

invisible(readline(prompt = "\nPress [enter] to display the top modular networks."))
if (save.img) {
    png(filename=paste("topmod_", alpha, ".png", sep=""))
    plot(lc, type = "commsumm", summary = "mod")
    dev.off()
} else {
    plot(lc, type = "commsumm", summary = "mod")
}
