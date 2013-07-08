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
  activateTooltips()
  addResultDetailsViewListener()

openResultDetailsModalView = (targetNode) ->
  images = $(targetNode).children()
  $("#cluster-detail-popup-synset").text($(targetNode).siblings(".result-title").children(".result-name").text())
  $("#cluster-detail-popup-definition em").text($(targetNode).siblings(".result-title").children(".result-description").text())
  $("#cluster-detail-popup > .modal-body").empty()
  $("#cluster-detail-popup > .modal-body").append(images.clone().height(120))
  detailsViewOrderImagesByMclCluster()
  $("#cluster-detail-popup .modal-body").css("max-height",
      ($(window).height() * 0.95 - $("#cluster-detail-popup .modal-header").outerHeight() - $("#cluster-detail-popup .modal-footer").outerHeight()) * 0.8)
  $("#cluster-detail-popup").modal("show")

detailsViewOrderImagesByMclCluster = ->
  $synsetImages = $("#cluster-detail-popup > .modal-body > img")
  dict = {}

  for domImage in $synsetImages
    $image = $(domImage)
    mclClusterName = $image.attr("data-mcl-cluster")
    visualClusterName = $image.attr("data-visual-cluster")
    if not dict[mclClusterName]
      dict[mclClusterName] = {}
    if not dict[mclClusterName][visualClusterName]
      dict[mclClusterName][visualClusterName] = []
    dict[mclClusterName][visualClusterName].push $image[0]

  for mclClusterName, mclCluster of dict
    $("#cluster-detail-popup > .modal-body").append("<div class='mcl-cluster'></div>")
    for visualClusterName, visualCluster of mclCluster
      $("#cluster-detail-popup > .modal-body > .mcl-cluster:last-child").append("<div class='visual-cluster pull-left'></div>")
      $("#cluster-detail-popup > .modal-body > .mcl-cluster:last-child > .visual-cluster:last-child").append(visualCluster)
    $("#cluster-detail-popup > .modal-body > .mcl-cluster:last-child > .visual-cluster:last-child").append("<div class='clearfix'></div>")
    $("#cluster-detail-popup > .modal-body").append("<div class='clearfix'></div>")

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

