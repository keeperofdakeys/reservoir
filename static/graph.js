var REQUESTS = [];
var COUNT = 0;
var TOTAL = 0;

function clear_requests() {
  for( var i=0; i<REQUESTS.length; i++ ) {
    REQUESTS[i].abort();
  }
  REQUESTS = [];
}

function clear_view() {
  var checkboxes = document.getElementsByTagName("input");
  for( var i=0; i<checkboxes.length; i++ ) {
    var node = checkboxes.item(i);
    if( node.type !== "checkbox" ) {
      continue;
    }
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
  var request = new XMLHttpRequest();
  REQUESTS.push(request);
  request.open("GET", 
      "".concat("data/", source, "/", start_time, "/", end_time, "/")
      );
  request.onreadystatechange = open_data;
  request.send();

  function open_data() {
    if( request.readyState === 4 &&
        ( request.status >= 200 && request.status <= 400 ) ) {
      var response = request.responseText.split("\n");
      var data = [];
      for( var i=0; i<response.length; i++ ) {
        data.push(parse_row(response[i]));
      }
      data_list.push( {
          label: name,
          data: data
        });
      COUNT++;
      draw_graph(data_list);
    }
  }
}

function setup_graph() {
  clear_requests();
  var period = document.getElementById("period").value;
  var date_range = get_range(period);
  if( date_range === undefined ) {
    return;
  }
  var sources = [];
  var data_list = [];
  var checkboxes = document.getElementsByTagName("input");
  COUNT = 0;
  TOTAL = 0;
  for( var i=0; i<checkboxes.length; i++ ) {
    var node = checkboxes.item(i);
    if( node.type !== "checkbox" ) {
      continue;
    }
    var table_key = node.getAttribute("data-key");
    var table_name = node.getAttribute("data-name");
    if( !node.checked ) {
      continue;
    }
    TOTAL++;
    send_request(data_list, table_key, table_name, date_range);
  }
}

function draw_graph(data_list) {
  if( COUNT < TOTAL ) {
    return;
  }
  $.plot("#plot", data_list, {
    series: {
      points: {
        radius: 3,
        show: true,
        fill: true
      }
    },
    xaxis: { transform: function(x) { return x; },
            tickFormatter: tick_formatter,
            ticks: tick_generator },
    legend: { show: true, backgroundOpacity: 0.5, },
    grid: {
      hoverable: true,
      backgroundColor: "#FFFFFF"
    }
  });
  function showTooltip(x, y, contents) {
    var tooltip = $('<div id="tooltip">' + contents + '</div>');
    tooltip.css( {
      position: 'absolute',
      display: 'none',
      border: '1px solid #000',
      padding: '2px',
      'background-color': '#fee',
      opacity: 0.80,
      "font-size": "0.8em"
    });
    var x_offset = -25;
    var y_offset = 5;
    var tip_width = 200;
    var ie = document.all && !window.opera;
    var iebody = (document.compatMode == 'CSS1Compat')
                 ? document.documentElement
                 : document.body;
    var scrollLeft = ie ? iebody.scrollLeft : window.pageXOffset;
    var scrollTop = ie ? iebody.scrollTop : window.pageYOffset;
    var docWidth = ie ? iebody.clientWidth - 15 : window.innerWidth - 15;
    var docHeight = ie ? iebody.clientHeight - 15 : window.innerHeight - 8;

    // account for right edge
    tooltip.css({ top: y + y_offset });
    tooltip.css({ "min-width": tip_width/2 });
    tooltip.css({ "max-width": tip_width });

    if (x + tip_width + scrollLeft > docWidth) {
        tooltip.css({ right: docWidth - x + x_offset });
    } else {
        tooltip.css({ left: x + x_offset });
    }
    tooltip.appendTo("body").fadeIn(0);
  }

  var previousPoint = null;
  $("#plot").bind("plothover", function (event, pos, item) {
      $("#x").text(pos.x.toFixed(2));
      $("#y").text(pos.y.toFixed(2));
      if (item) {
        $("#tooltip").remove();
        var x = item.datapoint[0].toFixed(2),
          y = item.datapoint[1].toFixed(2);
        
        showTooltip(item.pageX, item.pageY,
          "<span class=\"bold\">" + item.series.label + ":</span><br>"
          + date_formatter(parseInt(x)) + "<br>" + y + " m");
      } else {
        $("#tooltip").remove();
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

function date_formatter(date) {
  // Data is no longer in UTC but local timezone. Moment expects UTC, so add
  // the negative timezone offset (bloody javascript).
  return moment.unix(date + time_offset).format("DD/MM/YYYY HH:mm:ss");
}

function tick_formatter(value, axis) {
  // Only allow labels as calculated in tick_generator, so only ten ever
  // show.
  if( (axis.new_min + value) % axis.new_step !== 0 ) {
    return "";
  }
  // Data is no longer in UTC but local timezone. Moment expects UTC, so add
  // the negative timezone offset (bloody javascript).
  return moment.unix(value + time_offset).format("DD/MM/YY");
}

function hide() {
  var checkboxes = document.getElementById("content");
  var hide_button = document.getElementById("hide");
  var show_button = document.getElementById("show");
  checkboxes.style.display = "none";
  hide_button.style.display = "none";
  show_button.style.display = "inline";
}

function show() {
  var checkboxes = document.getElementById("content");
  var hide_button = document.getElementById("hide");
  var show_button = document.getElementById("show");
  checkboxes.style.display = "block";
  hide_button.style.display = "inline";
  show_button.style.display = "none";
}
