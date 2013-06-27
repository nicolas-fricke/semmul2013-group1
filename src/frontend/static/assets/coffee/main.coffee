@onClickFind = () ->
  $.get(("http://localhost:5000/search/" + $("#input-searchterm").val()), searchDataArrived)

searchDataArrived = (data) ->
  window.debug = data
  console.log("Done! " + data)

@draw = (treeData) ->
  # Create a svg canvas
  canvas = d3.select("#tree-canvas").append("svg:svg")
    .attr("width", 400)
    .attr("height", 300)
    .append("svg:g")
    .attr("transform", "translate(40, 0)")

  # Create a tree "canvas"
  tree = d3.layout.tree()
    .size([300,150])

  diagonal = d3.svg.diagonal()
  # change x and y (for the left to right tree)
  .projection((d) -> [d.y, d.x])

  # Preparing the data for the tree layout, convert data into an array of nodes
  nodes = tree.nodes(treeData)
  # Create an array with all the links
  links = tree.links(nodes)

  console.log(treeData)
  console.log(nodes)
  console.log(links)

  link = canvas.selectAll("pathlink")
    .data(links)
    .enter().append("svg:path")
    .attr("class", "link")
    .attr("d", diagonal)

  node = canvas.selectAll("g.node")
    .data(nodes)
    .enter().append("svg:g")
    .attr("transform", (d) -> "translate(" + d.y + "," + d.x + ")")

  # Add the dot at every node
  node.append("svg:circle")
    .attr("r", 3.5);

  # place the name atribute left or right depending if children
  node.append("svg:text")
    .attr("dx", (d) -> if d.children then -8 else 8)
  .attr("dy", 3)
  .attr("text-anchor", (d) -> if d.children then "end" else "start")
  .text((d) -> d.name)


$.ready(
  draw()
)