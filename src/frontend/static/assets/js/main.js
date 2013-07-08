// Generated by CoffeeScript 1.6.3
(function() {
  var activateTooltips, addResultDetailsViewListener, bindFunctions, detailsViewOrderImagesByMclCluster, indentImages, openResultDetailsModalView, searchDataArrived, setResultsMinHeight,
    _this = this;

  this.newSearch = function() {
    var searchterm;
    searchterm = $('#input-searchterm').val();
    $('#loading-popup-searchterm').text(searchterm);
    $('#loading-popup').modal('show');
    return $('#results').load("http://localhost:5000/search/" + searchterm + " #result-container", searchDataArrived).fadeIn("slow");
  };

  searchDataArrived = function(responseText, textStatus, XMLHttpRequest) {
    if (textStatus !== "success") {
      $('#loading-popup');
    }
    $('#loading-popup').modal('hide');
    console.log("Search data arrived:", textStatus);
    indentImages();
    activateTooltips();
    return addResultDetailsViewListener();
  };

  openResultDetailsModalView = function(targetNode) {
    var images;
    $("#cluster-detail-popup").modal("show");
    images = $(targetNode).children();
    $("#cluster-detail-popup-synset").text($(targetNode).siblings(".result-name").text());
    $("#cluster-detail-popup > .modal-body").empty();
    $("#cluster-detail-popup > .modal-body").append(images.clone().height(120));
    detailsViewOrderImagesByMclCluster();
    return console.log(targetNode);
  };

  detailsViewOrderImagesByMclCluster = function() {
    var $image, $synsetImages, dict, domImage, mclCluster, mclClusterName, visualCluster, visualClusterName, _i, _len, _results;
    $synsetImages = $("#cluster-detail-popup > .modal-body > img");
    dict = {};
    for (_i = 0, _len = $synsetImages.length; _i < _len; _i++) {
      domImage = $synsetImages[_i];
      $image = $(domImage);
      mclClusterName = $image.attr("data-mcl-cluster");
      visualClusterName = $image.attr("data-visual-cluster");
      if (!dict[mclClusterName]) {
        dict[mclClusterName] = {};
      }
      if (!dict[mclClusterName][visualClusterName]) {
        dict[mclClusterName][visualClusterName] = [];
      }
      dict[mclClusterName][visualClusterName].push($image[0]);
    }
    _results = [];
    for (mclClusterName in dict) {
      mclCluster = dict[mclClusterName];
      $("#cluster-detail-popup > .modal-body").append("<div class='mcl-cluster'></div>");
      for (visualClusterName in mclCluster) {
        visualCluster = mclCluster[visualClusterName];
        $("#cluster-detail-popup > .modal-body > .mcl-cluster:last-child").append("<div class='visual-cluster pull-left'></div>");
        $("#cluster-detail-popup > .modal-body > .mcl-cluster:last-child > .visual-cluster:last-child").append(visualCluster);
      }
      $("#cluster-detail-popup > .modal-body > .mcl-cluster:last-child > .visual-cluster:last-child").append("<div class='clearfix'></div>");
      _results.push($("#cluster-detail-popup > .modal-body").append("<div class='clearfix'></div>"));
    }
    return _results;
  };

  addResultDetailsViewListener = function() {
    return $(".result-preview").click(function(event) {
      return openResultDetailsModalView(event.currentTarget);
    });
  };

  activateTooltips = function() {
    $('.result-synset').tooltip({
      selector: '',
      placement: 'left',
      container: 'body',
      html: 'true'
    });
    return $('img').tooltip({
      selector: '',
      placement: 'bottom',
      container: 'body',
      html: 'true'
    });
  };

  indentImages = function() {
    var max_width;
    max_width = 0;
    $('.result-name').each(function() {
      if ($(this).width() > max_width) {
        return max_width = $(this).width();
      }
    });
    return $('.result-name').width(max_width);
  };

  bindFunctions = function() {
    return $('#input-searchterm').keyup(function(e) {
      if (e.keyCode === 13) {
        return newSearch();
      }
    });
  };

  setResultsMinHeight = function() {
    return $("#results").css("min-height", $('body').height() - $('#main-navigation').height() - $('footer').height());
  };

  $.ready = function() {
    $(".modal").modal().on("shown", function() {
      return $("body").css("overflow", "hidden");
    }).on("hidden", function() {
      return $("body").css("overflow", "auto");
    });
    $('#loading-popup').modal('hide');
    $('#cluster-detail-popup').modal('hide');
    $("#input-searchterm").focus();
    return setResultsMinHeight();
  };

}).call(this);
