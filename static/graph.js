function send_request(data_list, source, name, date_range) {
  if( date_range.length < 2 ) {
    start_time = "start";
    end_time = "end";
  } else {
    start_time = date_range[0];
    if( start_time !== "start" ) {
      start_time = start_time.unix();
    }
    end_time = date_range[1];
    if( end_time !== "end" ) {
      end_time = end_time.unix();
    }
  }
  var request = new XMLHttpRequest()
  request.open("GET", 
      "".concat("data/", source, "/", start_time, "/", end_time, "/")
      );
  request.onload = open_data;
  request.send();

  function open_data() {
    if( request.readyState === 4 ) {
      data_list.push( {
          label: name,
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

function custom_fields(element) {
  var period = element.value;
  var div = document.getElementById('custom_range');
  if( period !== "custom" ) {
    div.style.display = "none";
    return;
  }
  var div = document.getElementById('custom_range');
  div.style.display = "block";
}

function get_range(period) {
  document.getElementById("date_error").innerHTML = "";
  var start = "start";
  var end = "end";
  var now = moment();
  switch( period ) {
    case "year":
      start = now.clone().subtract('years', 1);
      break;

    case "six_months":
      start = now.clone().subtract("months", 6);
      break;

    case "month":
      start = now.clone().subtract("month", 1);
      break;

    case "week":
      start = now.clone().subtract("days", 7);
      break;

    case "custom":
      start_text = document.getElementById("range_start").value;
      start = moment(start_text, "YYYY-MM-DD");
      if( !start.isValid() ) {
        document.getElementById("date_error").innerHTML = "Start Date Error";
        return undefined;
      }
      end_text = document.getElementById("range_end").value;
      end = moment(end_text, "YYYY-MM-DD");
      if( !end.isValid() ) {
        document.getElementById("date_error").innerHTML = "End Date Error";
        return undefined;
      }
      break;
  }
  return [start, end];
}

function parse_row(cur_val, index, arr) {
  items = cur_val.split(",");
  items[0] = parseInt(items[0]);
  items[1] = parseFloat(items[1]);
  return items;
}

function setup_graph() {
  var period = document.getElementById("period").value;
  var date_range = get_range(period);
  if( date_range === undefined ) {
    return;
  }
  var sources = [];
  var data_list = [];
  var checkboxes = document.getElementsByClassName("input_checkbox");
  for( var i=0; i<checkboxes.length; i++ ) {
    var node = checkboxes.item(i);
    var table_key = node.getAttribute("data-key");
    var table_name = node.getAttribute("data-name");
    if( !node.checked ) {
      continue;
    }
    send_request(data_list, table_key, table_name, date_range);
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
