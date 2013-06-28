// Generated by CoffeeScript 1.4.0
(function() {
  var draw, searchDataArrived,
    _this = this;

  this.onClickFind = function() {
    return $.get("http://localhost:5000/search/" + $("#input-searchterm").val(), searchDataArrived);
  };

  searchDataArrived = function(data) {
    console.log("Search data arrived:");
    console.log(data);
    window.debug = data;
    return draw(data);
  };

  draw = function(treeData) {
    return this.tree_canvas.append("circle").style("stroke", "gray").style("fill", "orange").attr("r", 40).attr("cx", 50).attr("cy", 50).text("woooo");
  };

  $.ready = function() {
    _this.tree_canvas = d3.select("#tree-canvas").append("svg").attr("width", $("#tree-canvas").width()).attr("height", $("#tree-canvas").height());
    return $("#input-searchterm").focus();
  };

}).call(this);