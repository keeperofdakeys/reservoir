function send_request(data_list, source) {
  var request = new XMLHttpRequest()
  request.open("GET", "".concat("data/", source, "/hello/3/"));
  request.onload = open_data;
  //request.onload = function () { open_data(request) };
  request.send();

  function open_data() {
    if( request.readyState == 4 ) {
      data_list.push( {
          label: source,
          data: request.responseText.split("\n").map(parse_row)
        });
      }
      draw_graph(data_list);
  }
}

function clear_checkboxes() {
  var checkboxes = document.getElementsByClassName("input_checkbox");
  for( var i=0; i<checkboxes.length; i++ ) {
    var node = checkboxes.item(i);
    node.checked = false;
  }
}



function parse_row(cur_val, index, arr) {
  items = cur_val.split(",");
  items[0] = parseInt(items[0]);
  items[1] = parseFloat(items[1]);
  return items;
}

function setup_graph() {
  var sources = [];
  var data_list = [];
  var checkboxes = document.getElementsByClassName("input_checkbox");
  for( var i=0; i<checkboxes.length; i++ ) {
    var node = checkboxes.item(i);
    var table_key = node.getAttribute("name");
    if( !node.checked ) {
      continue;
    }
    send_request(data_list, table_key);
  }
}

function draw_graph(data_list) {
  $.plot("#plot", data_list, {
    series: {
      points: {
        radius: 3,
        show: true,
        fill: true
      }
    },
    xaxis: { transform: function(x) { return x ; },
            tickFormatter: function(x) { return new Date(x * 1000); },
            tickSize: 24*60*60 },
    legend: { show: true, backgroundOpacity: 0.5, }
  });
}
