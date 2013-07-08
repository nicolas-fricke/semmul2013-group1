@newSearch = ->
  searchterm = $('#input-searchterm').val()
  $('#loading-popup-searchterm').text(searchterm)
  $('#loading-popup').modal('show')
  $('#results').load("http://localhost:5000/search/" + searchterm + " #result-container", searchDataArrived).fadeIn("slow")

searchDataArrived = (responseText, textStatus, XMLHttpRequest) =>
  if textStatus != "success"
    $('#loading-popup')
  $('#loading-popup').modal('hide')
  console.log "Search data arrived:", textStatus
  indentImages()
  activateTooltips()
  addResultDetailsViewListener()

openResultDetailsModalView = (targetNode) ->
  $("#cluster-detail-popup").modal("show")
  images = $(targetNode).children()
  $("#cluster-detail-popup-synset").text($(targetNode).siblings(".result-name").text())
  $("#cluster-detail-popup > .modal-body").empty()
  $("#cluster-detail-popup > .modal-body").append(images.clone().height(120))
  console.log targetNode

addResultDetailsViewListener = ->
  $(".result-preview").click (event) ->
    openResultDetailsModalView(event.currentTarget)

activateTooltips = ->
  $('.result-synset').tooltip
    selector: ''
    placement: 'left'
    container: 'body'
    html: 'true'
  $('img').tooltip
    selector: ''
    placement: 'bottom'
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

setResultsMinHeight = ->
  $("#results").css("min-height", $('body').height() - $('#main-navigation').height() - $('footer').height())

$.ready = =>
  $(".modal").modal().on("shown", ->
    $("body").css "overflow", "hidden"
  ).on("hidden", ->
    $("body").css "overflow", "auto")
  $('#loading-popup').modal('hide')
  $('#cluster-detail-popup').modal('hide')
#  bindFunctions()
  $("#input-searchterm").focus()
  setResultsMinHeight()

