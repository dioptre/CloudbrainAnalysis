// random value generator
function getNewData(){
  return Math.random() * 100;
}

// globals
// set default window dimensions
var defaultDataLength = 100;
var defaultData = [];
var defaultLabels = [];
for(var i=0;i<defaultDataLength;i++){
  defaultData.push(getNewData());
  defaultLabels.push("");
}


var config = {
    type: 'line',
    data: {
        labels: defaultLabels,
        datasets: [{
            label: "My First dataset",
            data: defaultData,
            fill: false
        }]
    },
    options: {

        scales: {
            xAxes: [{
              display: true,
              ticks: {
                  userCallback: function(dataLabel, index) {
                      return '';
                      //return index % 2 === 0 ? dataLabel : '';
                  }
              }
            }],
            yAxes: [{
              display: true
            }]
        },
        responsive: false,
        responsiveAnimationDuration: 0,
        animation: {
            duration: 0,
            easing: "easeOutQuart",
            onProgress: function() {},
            onComplete: function() {},
        },
        line: {
            tension: -1,
            backgroundColor: Chart.defaults.global.defaultColor,
            borderWidth: 0,
            borderColor: Chart.defaults.global.defaultColor,
            borderCapStyle: 'butt',
            borderDash: [],
            borderDashOffset: 0.0,
            borderJoinStyle: 'miter',
            fill: false, // do we fill in the area between the line and its base axis
            skipNull: true,
            drawNull: false,
        },
        point: {
            display: false,
            radius: 0,
            backgroundColor: Chart.defaults.global.defaultColor,
            borderWidth: 0,
            borderColor: Chart.defaults.global.defaultColor,
            // Hover
            hitRadius: 0,
            hoverRadius: 0,
            hoverBorderWidth: 0,
        },
        tooltips:{
          enabled: false,
          custom: null
        }
    }
};

function addData (chart, values) {
  var maxlen = defaultDataLength;
  if (config.data.datasets.length > 0) {
      //config.data.labels.push('dataset #' + config.data.labels.length);

      $.each(config.data.datasets, function(i, dataset) {
          dataset.data.push(values);
          if(dataset.data.length > maxlen){
            dataset.data.shift();
          }
      });
      chart.update();
  }
}

$(document).ready(function(){
    // Get context with jQuery - using jQuery's .get() method.
    var ctx = $("#myChart").get(0).getContext("2d");
    var lineChart = new Chart(ctx, config);


    // to be called when you want to stop the timer
    function abortTimer() {
      clearInterval(tid);
    }

    // bind "do" button
    $('.do').on('click',function(e){
      addData(lineChart,getNewData());
    });
    // bind "stop" button
    $('.stop').on('click',function(e){
      abortTimer();
    });

    // default 250Hz
    var tid = setInterval(function() { addData(lineChart,getNewData()); }, 10);


});

