@onClickFind = () ->
  $.get(("http://localhost:5000/search/" + $("#input-searchterm").val()), searchDataArrived)

searchDataArrived = (data) ->
  console.log "Search data arrived:"
  console.log data
  window.debug = data
  draw(data)

@draw = (treeData) ->
  console.log "I would draw if I could"
  window.tree_canvas.append("circle")
              .style("stroke", "gray")
              .style("fill", "white")
              .attr("r", 40)
              .attr("cx", 50)
              .attr("cy", 50)


$.ready(
  window.tree_canvas = d3.select("#tree-canvas")
                    .append("svg")
                    .attr("width", 100)
                    .attr("height", 100)
)