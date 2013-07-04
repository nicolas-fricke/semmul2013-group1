@newSearch = ->
  searchterm = $('#input-searchterm').val()
  $('#loading-popup-searchterm').text(searchterm)
  $('#loading-popup').modal('show')
  $('#result-container').load("http://localhost:5000/search/" + searchterm + " #result-container", searchDataArrived)

searchDataArrived = (data) =>
  $('#loading-popup').modal('hide')
  console.log "Search data arrived:"
  console.log data

###

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
          .attr("class", "flickr-thumbnail")
          .attr("rel", "popover")
          .on("mouseover", -> onImageMouseOver @)
          .on("mouseout",  -> onImageMouseOut @)

    for key,hyponyms of treeData when key is 'hyponyms'
      for hyponym, i in hyponyms
        @tree_canvas.append("text")
          .attr("dx", x+50+150*i)
          .attr("dy", y+30)
          .on("click", -> onNodeClick @)
          .text(hyponym['name'])

###

@onNodeClick = (nodeObject) =>
  console.log "Clicked on node: #{nodeObject.textContent}"

onImageMouseOver = (imageObject) =>
  console.log "Hover onto image: #{imageObject.href.baseVal}"

onImageMouseOut = (imageObject) =>
  console.log "Hover out of image: #{imageObject.href.baseVal}"

bindFunctions = ->
  # React on <Enter> on search field
  $('#input-searchterm').keyup (e) ->
    if e.keyCode is 13 # enter
      newSearch()

$.ready = =>
  $('#loading-popup').modal('hide')
#  bindFunctions()
  $("#input-searchterm").focus()
