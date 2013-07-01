@onClickFind = ->
  $.get(("http://localhost:5000/search/" + $("#input-searchterm").val()), searchDataArrived)

searchDataArrived = (data) ->
  console.log "Search data arrived:"
  console.log data
  draw(node,i+50, i*50+50) for node, i in data

draw = (treeData,x,y) ->
  @tree_canvas.append("circle")
    .style("stroke", "gray")
    .style("fill", "lightblue")
    .attr("r", 5)
    .attr("cx", x)
    .attr("cy", y)

  for key,value of treeData when key is 'name'
    @tree_canvas.append("text")
      .attr("dx", x+20)
      .attr("dy", y+5)
      .on("click", -> onNodeClick @)
      .text(value)

    for key,value of treeData when key is 'associated_pictures'
      for picture, i in value
        console.log picture, i
        @tree_canvas.append("svg:image")
          .attr("xlink:href", picture[1])
          .attr("width",45)
          .attr("height",45)
          .attr("x", 150+i*50)
          .attr("y", y-20)
          .on("mouseover", -> onImageMouseOver @)
          .on("mouseout",  -> onImageMouseOut @)

@onNodeClick = (nodeObject) =>
  console.log "Clicked on node: #{nodeObject.textContent}"

onImageMouseOver = (imageObject) =>
  console.log "Hover onto image: #{imageObject.href.baseVal}"


onImageMouseOut = (imageObject) =>
  console.log "Hover out of image: #{imageObject.href.baseVal}"

$.ready = =>
  @tree_canvas = d3.select("#tree-canvas")
    .append("svg")
    .attr("width", $("#tree-canvas").width())
    .attr("height", $("#tree-canvas").height())

  $("#input-searchterm").focus()
