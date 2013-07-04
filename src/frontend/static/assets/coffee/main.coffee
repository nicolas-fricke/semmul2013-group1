@newSearch = ->
  searchterm = $('#input-searchterm').val()
  $('#loading-popup-searchterm').text(searchterm)
  $('#loading-popup').modal('show')
  $('#result-container').load("http://localhost:5000/search/" + searchterm + " #result-container", searchDataArrived)

searchDataArrived = (responseText, textStatus, XMLHttpRequest) =>
  $('#loading-popup').modal('hide')
  console.log "Search data arrived:", textStatus
  indentImages()

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

indentImages = ->
  max_width = 0
  $('.result-name').each ->
    if $(this).width() > max_width then max_width = $(this).width()
  $('.result-name').width(max_width)

$.ready = =>
  $('#loading-popup').modal('hide')
#  bindFunctions()
  $("#input-searchterm").focus()
