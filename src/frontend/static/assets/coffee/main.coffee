@onClickFind = ->
  $.get(("http://localhost:5000/search/" + $("#input-searchterm").val()), searchDataArrived)

searchDataArrived = (data) ->
  console.log "Search data arrived:"
  console.log data
  window.debug = data
  draw(node,i*100+150) for node, i in data

draw = (treeData,position) ->
  @tree_canvas.append("circle")
    .style("stroke", "gray")
    .style("fill", "lightblue")
    .attr("r", 40)
    .attr("cx", position)
    .attr("cy", 100)

  for key,value of treeData when key is 'name'
    @tree_canvas.append("text")
      .attr("dx", position-20)
      .attr("dy", 100)
      .text(value)

$.ready = =>
  @tree_canvas = d3.select("#tree-canvas")
    .append("svg")
    .attr("width", $("#tree-canvas").width())
    .attr("height", $("#tree-canvas").height())

  $("#input-searchterm").focus()
