@onClickFind = () ->
  $.get(("http://localhost:5000/search/" + $("#input-searchterm").val()), searchDataArrived)

searchDataArrived = (data) ->
  window.debug = data
  console.log("Done! " + data)

$.ready(

)