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

function clear_view() {
  var checkboxes = document.getElementsByClassName("input_checkbox");
  for( var i=0; i<checkboxes.length; i++ ) {
    var node = checkboxes.item(i);
    node.checked = false;
  }
  $('#plot').empty()
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
      start = moment(start_text, "DD-MM-YYYY");
      if( !start.isValid() ) {
        document.getElementById("date_error").innerHTML = "Start Date Error";
        return undefined;
      }
      end_text = document.getElementById("range_end").value;
      end = moment(end_text, "DD-MM-YYYY");
      if( !end.isValid() ) {
        document.getElementById("date_error").innerHTML = "End Date Error";
        return undefined;
      }
      break;
  }
  return [start, end];
}

var time_offset = moment().zone()*60;

function parse_row(cur_val, index, arr) {
  items = cur_val.split(",");
  // Account for timezone, by adding negative timezone offset.
  items[0] = parseInt(items[0]) - time_offset;
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
    xaxis: { transform: function(x) { return x; },
            tickFormatter: tick_formatter, // function(x) { return moment.unix(x + time_offset)//.toDate(); },
              //.format("DD/MM/YY "); },
            //tickSize: 24*60*60 },
            ticks: tick_generator },
    legend: { show: true, backgroundOpacity: 0.5, },
    grid: {
      backgroundColor: "#FFFFFF"
    }
  });
}
 
function tick_generator(axis) {
  var ticks = [];
  var time_step = 24*60*60;
  var step_num = 10;
  var min = axis.min - (axis.min % time_step);
  var max = axis.max - (axis.max % time_step) + 1;
  var time_range = Math.ceil((max - min) / time_step);
  var new_step;
  if( (max - min) > time_step * step_num ) {
    new_step = Math.ceil(time_range / step_num)*time_step;
  } else {
    new_step = time_step;
  }
  // Use these values for labels, code here because this runs once.
  axis.new_min = min;
  axis.new_step = new_step;
  // Make ticks for every day.
  for( var i=min; i<max; i+=time_step ) {
    ticks.push(i);
  }
  return ticks;
}

function tick_formatter(value, axis) {
  // Only allow labels as calculated in tick_generator, so only ten ever
  // show.
  if( (axis.new_min + value) % axis.new_step !== 0 ) {
    return "";
  }
  // Data is no longer in UTC but local timezone. Moment expects UTC, so add
  // the negative timezone offset (bloody javascript).
  return moment.unix(value + time_offset).format("DD/MM/YY ");
}
