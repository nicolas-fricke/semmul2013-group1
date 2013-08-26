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
  addResultSynsetMouseenterListener()

openResultDetailsModalView = (targetNode) ->
  $("#cluster-detail-popup-synset").text($(targetNode).siblings(".result-title").children(".result-name").text())
  $("#cluster-detail-popup-definition em").text($(targetNode).siblings(".result-title").children(".result-description").text())
  $("#cluster-detail-popup > .modal-body").empty()
  mclClusters = $(targetNode).children()
  mclClusterLabels = createMclClusterLabelsDict(mclClusters)
  images = $(mclClusters).children()
  $("#cluster-detail-popup > .modal-body").append(images.clone().height(120))
  detailsViewOrderImagesByMclCluster(mclClusterLabels)
  $("#cluster-detail-popup .modal-body").css("max-height",
      ($(window).height() * 0.95 - $("#cluster-detail-popup .modal-header").outerHeight() - $("#cluster-detail-popup .modal-footer").outerHeight()) * 0.8)
  $("#cluster-detail-popup").modal("show")

createMclClusterLabelsDict = (mclClusters) ->
  mclClusterLabels = {}
  for mclCluster in mclClusters
    mclClusterNr = $(mclCluster).attr("data-mcl-cluster-index")
    if mclClusterNr not in mclClusterLabels
      mclClusterLabels[mclClusterNr] = $(mclCluster).attr("data-mcl-synset-description")
  return mclClusterLabels

detailsViewOrderImagesByMclCluster = (mclClusterLabels) ->
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
    $("#cluster-detail-popup > .modal-body > .mcl-cluster:last-child").append("<div class='mcl-synsets-label'><h4>Most dominant tags:</h4> <p class='mcl-dominant-lables'>#{mclClusterLabels[mclClusterName]}</p></div>")
    for visualClusterName, visualCluster of mclCluster
      $("#cluster-detail-popup > .modal-body > .mcl-cluster:last-child").append("<div class='visual-cluster pull-left'></div>")
      $("#cluster-detail-popup > .modal-body > .mcl-cluster:last-child > .visual-cluster:last-child").append(visualCluster)
    $("#cluster-detail-popup > .modal-body > .mcl-cluster:last-child > .visual-cluster:last-child").append("<div class='clearfix'></div>")
    $("#cluster-detail-popup > .modal-body").append("<div class='clearfix'></div>")

addResultDetailsViewListener = ->
  $(".result-preview").click (event) ->
    $(".tooltip").remove()
    openResultDetailsModalView(event.currentTarget)

addResultSynsetMouseenterListener = ->
  $('.result-synset').mouseenter( (event) ->
    event.stopPropagation()
    $hoveredSynset = $(@)
    recursivelyPositionTooltips $hoveredSynset, $hoveredSynset.position().top
  )
  $('.result-synset').mouseleave( ->
    $(@).tooltip("hide")
  )

recursivelyPositionTooltips = (synsetNode, topPosition) ->
  synsetNode.tooltip("show")
  synsetNode.siblings('.tooltip').css("top", topPosition)
  if synsetNode.parent().hasClass 'result-synset'
    recursivelyPositionTooltips(synsetNode.parent(),
        topPosition - (synsetNode.siblings('.tooltip').height() + 10))


activateTooltips = ->
  $('.result-synset').tooltip
    selector: ''
    placement: 'left'
    html: 'true'
    trigger: 'manual'
  $('img').tooltip
    selector: ''
    placement: 'bottom'
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
  $("#results").css('minHeight', ($(window).height() - $("footer").outerHeight(true) - $("#main-navigation").height()))
  bindFunctions()
  $("#input-searchterm").focus()
  setResultsMinHeight()
  window.onbeforeunload = -> 'Do you really want to leave the page?'

