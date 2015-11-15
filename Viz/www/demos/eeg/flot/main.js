// get random number between 0 and 100
function getNewData(){
  return Math.random() * 100;
}

// get n number of random points as [0,n] coordinate pairs
function getRandoms(totalPoints){
    data = [];
    x = 0;
    while (data.length < totalPoints) {
        data.push([x,getNewData()]);
        x = x+1;
    }
    return data;
}

// update the chart
function updatePlot(plot, newValues) {

    // get access to existing data points
    var plotDatas = plot.getData();
    var plotData = plotDatas[0].data;

    // add new
    plotData = plotData.concat(newValues);
    // chop off the old
    plotData.splice(0, newValues.length);
    // recalculate x values
    for(var i=0; i<plotData.length; i++){
        plotData[i][0] = i;
    }

    // refresh chart
    plot.setData([plotData]);
    plot.draw();
}

// Pipe - convenience wrapper to present data received from an
// object supporting WebSocket API in an html element. And the other
// direction: data typed into an input box shall be sent back.
var pipe = function(ws, el_name) {
    var el_id = '#'+el_name;
    //$.charts.el_name = createChart($(el_id + ' canvas.chart'));

    // add one data at a time manually
    $(el_id+' .one_more').on('click',function(e){
        updatePlot($.charts.plot1, getRandoms(1));
    });

    var $div  = $(el_id + ' div');
    var $inp  = $(el_id + ' input');
    var $form = $(el_id + ' form');
    var $connectButton = $(el_id + ' .connect');
    var $disconnectButton = $(el_id + ' .disconnect');

    ws.onmessage = function(e) {
        // get incoming data as json
        var data = JSON.parse(e.data);
        updatePlot($.charts.plot1, [[0,data.channel_1]]);
    }

    ws.onopen    = function()  { console.log('websocket OPEN');}
    ws.onclose   = function()  { console.log('websocket CLOSED');};

    $connectButton.on('click', function(e){
        e.preventDefault();
        // get selected metric from dropdown
        var metric = $(el_id + ' .metricSelect').val();
        var jsonRequest = JSON.stringify({
            "type": "subscription",
            "deviceName": "openbci",
            "deviceId": "octopicorn",
            "metric": metric,
            "rabbitmq_address":"127.0.0.1"
        });
        ws.send(jsonRequest);
        console.log('subscribed: '+ metric);
        $connectButton.addClass('hidden');
        $disconnectButton.removeClass('hidden');
    });

    $disconnectButton.on('click', function(e){
        e.preventDefault();
        // get selected metric from dropdown
        var metric = $(el_id + ' .metricSelect').val();
        var jsonRequest = JSON.stringify({
            "type": "unsubscription",
            "deviceName": "openbci",
            "deviceId": "octopicorn",
            "metric": metric,
            "rabbitmq_address":"127.0.0.1"
        });
        ws.send(jsonRequest);
        console.log('unsubscribed: '+ metric);
        $disconnectButton.addClass('hidden');
        $connectButton.removeClass('hidden');
    });

};

// main
$(document).ready(function(e){
    $.charts = {};

    // declare socket, point to uri: /echo
    // this will establish connection to socket server
    var sockjs_url = '/echo';
    var sockjs = new SockJS(sockjs_url);

    var multiplexer = new MultiplexedWebSocket(sockjs);
    var channel1  = multiplexer.channel('ann');
    pipe(channel1,  'first');

    // initialize plot with some points
    $.charts.plot1 = $.plot("#placeholder", [getRandoms(1000)], {
        canvas: true,
        series: {shadowSize: 0},
        yaxis: {
            min: 0,
            max: 100
        },
        xaxis: { show: false }
    });

});
