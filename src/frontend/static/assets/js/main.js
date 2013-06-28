// Generated by CoffeeScript 1.6.3
(function() {
  var draw, searchDataArrived,
    _this = this;

  this.onClickFind = function() {
    return $.get("http://localhost:5000/search/" + $("#input-searchterm").val(), searchDataArrived);
  };

  searchDataArrived = function(data) {
    var i, node, _i, _len, _results;
    console.log("Search data arrived:");
    console.log(data);
    window.debug = data;
    _results = [];
    for (i = _i = 0, _len = data.length; _i < _len; i = ++_i) {
      node = data[i];
      _results.push(draw(node, i * 100 + 150));
    }
    return _results;
  };

  draw = function(treeData, position) {
    var key, value, _results;
    this.tree_canvas.append("circle").style("stroke", "gray").style("fill", "lightblue").attr("r", 40).attr("cx", position).attr("cy", 100);
    _results = [];
    for (key in treeData) {
      value = treeData[key];
      if (key === 'name') {
        _results.push(this.tree_canvas.append("text").attr("dx", position - 20).attr("dy", 100).text(value));
      }
    }
    return _results;
  };

  $.ready = function() {
    _this.tree_canvas = d3.select("#tree-canvas").append("svg").attr("width", $("#tree-canvas").width()).attr("height", $("#tree-canvas").height());
    return $("#input-searchterm").focus();
  };

}).call(this);
