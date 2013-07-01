@onClickFind = ->
  $.get(("http://localhost:5000/search/" + $("#input-searchterm").val()), searchDataArrived)

searchDataArrived = (data) ->
  console.log "Search data arrived:"
  console.log data
  window.debug = data
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
      .text(value)

    for key,value of treeData when key is 'associated_pictures'
      for picture, i in value
        @tree_canvas.append("image")
          .attr("xlink:href", "/static/wuerfels.jpg")
          .attr("width",40)
          .attr("height",40)
          .attr("x", 150+i*50)
          .attr("y", y-20)


$.ready = =>
  @tree_canvas = d3.select("#tree-canvas")
    .append("svg")
    .attr("width", $("#tree-canvas").width())
    .attr("height", $("#tree-canvas").height())

  $("#input-searchterm").focus()
