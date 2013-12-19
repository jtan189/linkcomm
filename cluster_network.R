## parameters
alpha = 0.25
save.img = TRUE
use.edge.attr = TRUE

## data input variables

## dblp
## noname.graph.file <- "ExampleDatasets/dblp/AuthorMapClean2.txt"
## graph.file <- "ExampleDatasets/dblp/AuthorMapClean2.txt"
## node.attr.file <- "ExampleDatasets/dblp/AuthorNameClean2.txt"
## edge.attr.file <- "ExampleDatasets/dblp/ConfAttributeClean2.txt"
## edge.dist.file <- "ExampleDatasets/dlbp/AuthorMapClean2_edgedist.txt"

## toy graph
noname.graph.file <- "ExampleDatasets/toy3/toyGraph.txt"
noname.zero.graph.file <- "ExampleDatasets/toy3/toyGraphZero.txt"
graph.file <- "ExampleDatasets/toy3/toyGraph_named.txt"
edge.attr.file <- "ExampleDatasets/toy3/toyEdgeAttributes.txt"
edge.attr.string.file <- "ExampleDatasets/toy3/toyEdgeAttributeStrings.txt"
edge.dist.file <- "ExampleDatasets/toy3/toyGraph_edgedist.txt"
node.attr.file <- "ExampleDatasets/toy3/toyNodeAttributes.txt"

dist.attr <- function(edge.attr, e1, e2) {
    ## Return S_ij = | e1 INTERSECT e2 | / |e1 UNION e2 |
    sim <- sum(edge.attr[e1, ] & edge.attr[e2, ]) / sum(edge.attr[e1, ] | edge.attr[e2, ])
    return(1 - sim)
}

if (use.edge.attr) {
    ## run Python script for calculating edge distances
    system(paste("python2.7 get_edge_similarities.py -w -o", edge.dist.file, noname.graph.file, sep=" "))
    dist.edge <- as.matrix(read.table(edge.dist.file))
}

## read data
graph <- as.matrix(read.table(graph.file))
node.attr <- as.matrix(read.table(node.attr.file))
edge.attr <- as.matrix(read.table(edge.attr.file))
edge.attr.string <- as.matrix(read.table(edge.attr.string.file))
                   
if (use.edge.attr) {

    ## populate distance matrix for edge attributes
    num.edges = nrow(edge.attr)
    dist.ea <- matrix(0, num.edges, num.edges)
    for (i in 2:num.edges) {
        for (j in 1:i-1) {
            dist.ea[i, j] <- dist.attr(edge.attr, i, j)
            ## if (i != j) {
            ##     dist.ea[j, i] <- dist.attr(edge.attr, i, j)
            ## }
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
cat("dist dist\n")
print(dist.comb)

## show various graphs/plots
orig.graph <- read.graph(noname.zero.graph.file, format="edgelist", directed=FALSE)
V(orig.graph)$name <- node.attr[, 2]
E(orig.graph)$label <- edge.attr.string

invisible(readline(prompt = "\nPress [enter] to show original network."))
if (save.img) {
    png(filename="orig.png", width = 800, height = 600)
    plot(orig.graph, edge.label.color="red")
    dev.off()
} else {
    plot(orig.graph, edge.label.color="red")
}

invisible(readline(prompt = "\nPress [enter] to get link communities for the network."))
if (save.img) {
    if (use.edge.attr) {
        png(filename=paste("lc_", alpha, ".png", sep=""))
        ##lc <- getLinkCommunities(graph, hcmethod = "ward", dist = dist.comb, plot = TRUE, verbose = TRUE)
        lc <- getLinkCommunities(graph, hcmethod = "average", dist = dist.comb, plot = TRUE, verbose = TRUE)
    } else {
        png(filename="lc.png")
        ##lc <- getLinkCommunities(graph, hcmethod = "ward", plot = TRUE, verbose = TRUE)
        lc <- getLinkCommunities(graph, hcmethod = "average", plot = TRUE, verbose = TRUE)
    }
    dev.off()
} else {
    if (use.edge.attr) {
        lc <- getLinkCommunities(graph, hcmethod = "average", dist = dist.comb, plot = TRUE, verbose = TRUE)
        ##lc <- getLinkCommunities(graph, hcmethod = "ward", dist = dist.comb, plot = TRUE, verbose = TRUE)
    } else {
        lc <- getLinkCommunities(graph, hcmethod = "average", plot = TRUE, verbose = TRUE)
        ##lc <- getLinkCommunities(graph, hcmethod = "ward", plot = TRUE, verbose = TRUE)
    }
}
cat("\n")
print(lc)

invisible(readline(prompt = "\nPress [enter] to display community membership for the top 20 nodes that belong to the most communities."))
if (save.img) {
    if (use.edge.attr) {
        png(filename=paste("top20_", alpha, ".png", sep=""))
    } else {
        png(filename="top20.png")
    }
    plot(lc, type = "members")
    dev.off()
} else {
    plot(lc, type = "members")
}

invisible(readline(prompt = "\nPress [enter] to display network with edges coloured according to community membership."))
if (save.img) {
    if (use.edge.attr) {
        png(filename=paste("edge_comm_", alpha, ".png", sep=""))
    } else {
        png(filename="edge_comm.png")
    }
    plot(lc, type = "graph")
    dev.off()
} else {
    plot(lc, type = "graph")
}

## this may result in "Cluster 1 is not entirely nested in any other clusters."
invisible(readline(prompt = paste("\nPress [enter] to find and display a subnetwork where the nodes of one link",
                       " community are entirely nested within another link community.", sep="")))
getNestedHierarchies(lc, clusid = 1, plot = TRUE)

invisible(readline(prompt = "\nPress [enter] to display the top modular networks."))
if (save.img) {
    if (use.edge.attr) {
        png(filename=paste("topmod_", alpha, ".png", sep=""))
    } else {
        png(filename="topmod.png")
    }
    plot(lc, type = "commsumm", summary = "mod")
    dev.off()
} else {
    plot(lc, type = "commsumm", summary = "mod")
}

invisible(readline(prompt = "\nPress [enter] to plot the network with a Spencer circle layout."))
if (save.img) {
    if (use.edge.attr) {
        png(filename=paste("spencer_", alpha, ".png", sep=""))
    } else {
        png(filename="spencer.png")
    }
    plot(lc, type = "graph", layout="spencer.circle")
    dev.off()
} else {
    plot(lc, type = "graph", layout="spencer.circle")
}

## for some reason, this usually (always?) fails with an error, so it has
## moved to the end of this script, in order to allow other plots to succeed
if (length(lc$clusters) > 1) {
    invisible(readline(prompt = "\nPress [enter] to plot Spencer circle for the top-connected node."))
    if (save.img) {
        if (use.edge.attr) {
            png(filename=paste("spencertop_", alpha, ".png", sep=""))
        } else {
            png(filename="spencertop.png")
        }
        plot(lc, type = "graph", nodes = "YML007W", layout="spencer.circle", vertex.label.cex=0.8, jitter = 0.2)
        dev.off()
    } else {
        plot(lc, type = "graph", nodes = "YML007W", layout="spencer.circle", vertex.label.cex=0.8, jitter = 0.2)
    }
}


