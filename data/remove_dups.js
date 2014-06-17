var csv = require('csv');
var fs = require('fs');
var levenshtein = require('./levenshtein');

var maxDups = 5;

fs.readFile("../CrowdMapper/private/PabloPh_UN_cleaned.csv", function(err, res) {
  if (err) {
    console.log(err);
    return
  }

  csv()
    .from.string(res, {
      columns: true,
      trim: true
    })
    .to.array( function( arr, count ) {
      var dropped = 0;
      var output = [];

      for(var i = 0; i < arr.length; i++) {
        // Don't do this for very short messages
        if (arr[i].text.length < 50) continue;

        var dups = 0;
        var keep = true;

        for(var j = 0; j < i; j++) {
          if( levenshtein.getEditDistance(arr[i].text, arr[j].text) < 20 ) {
            dups++;
          }

          if( dups >= maxDups ) {
            console.log("("+ ++dropped + ") Dropping " + arr[i].text);
            keep = false;
            break;
          }
        }

        if( keep ) {
          output.push(arr[i]);
        }

      }

      console.log(dropped + " / " + arr.length);
      console.log("kept " + output.length);

      csv()
        .from(output)
        .to.path("PabloPh_UN_cm.csv", {
          columns: [ "tweetid","text","date","username","userid" ],
          header: true
        });

    });
});
