@onClickFind = ->
  $.get(("http://localhost:5000/search/" + $("#input-searchterm").val()), searchDataArrived)

searchDataArrived = (data) ->
  console.log "Search data arrived:"
  console.log data
  window.debug = data
  draw(data)

draw = (treeData) ->
  @tree_canvas.append("circle")
    .style("stroke", "gray")
    .style("fill", "orange")
    .attr("r", 40)
    .attr("cx", 50)
    .attr("cy", 50)
    .text("woooo")

$.ready = =>
  @tree_canvas = d3.select("#tree-canvas")
    .append("svg")
    .attr("width", $("#tree-canvas").width())
    .attr("height", $("#tree-canvas").height())

  $("#input-searchterm").focus()
