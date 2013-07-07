@newSearch = ->
  searchterm = $('#input-searchterm').val()
  $('#loading-popup-searchterm').text(searchterm)
  $('#loading-popup').modal('show')
  $('#results').load("http://localhost:5000/search/" + searchterm + " #result-container", searchDataArrived).fadeIn("slow")

searchDataArrived = (responseText, textStatus, XMLHttpRequest) =>
  $('#loading-popup').modal('hide')
  console.log "Search data arrived:", textStatus
  indentImages()
  activateTooltips()

activateTooltips = ->
  $( '.result-synset').tooltip
    selector:''
    placement:'left'
    container: 'body'
    html: 'true'
  $( 'img').tooltip
    selector:''
    placement:'bottom'
    container: 'body'
    html: 'true'

indentImages = ->
  max_width = 0
  $('.result-name').each ->
    if $(this).width() > max_width then max_width = $(this).width()
  $('.result-name').width(max_width)

bindFunctions = ->
  # React on <Enter> on search field
  $('#input-searchterm').keyup (e) ->
    if e.keyCode is 13 # enter
      newSearch()

$.ready = =>
  $('#loading-popup').modal('hide')
#  bindFunctions()
  $("#input-searchterm").focus()
