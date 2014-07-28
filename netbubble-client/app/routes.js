 // app/routes.js

module.exports = function(app) {
	
	// get lat lon of the latest imported banners
	app.get('/api/banner/geofeed/latest', function(req, res) {
		var elasticsearch = require('es');
		config = {
			_index : 'survey',
			_type : 'banner',
			server : {
				host : '192.168.2.200',
				port : 9200
			}
		},
		es = elasticsearch(config);
		q = req.query.query;
		fromValue = req.query.from;
		sizeValue = req.query.size;
		es.search(
		{
			"query":{
      "filtered":{
         "query":{
            "bool":{
               "should":[
                  {
                     "query_string":{
                        "query":"*"
                     }
                  }
               ]
            }
         },
         "filter":{
            "bool":{
               "must":[
                  {
                     "match_all":{

                     }
                  },
                  {
                     "exists":{
                        "field":"location.lon_lat",
                        "field":"device_type",
                     }
                  }
               ]
            }
         }
      }
   },
   "fields":[ "location.lon_lat", "_id", "ip", "device_type" ],
   "size":1000
   }, function (err, data) {
			if (err) {
					console.log(err);
				} else {
					res.json(data);
				}
		});
	});
	
	
	
	// match all fields
	app.get('/api/banner/search', function(req, res) {
		var elasticsearch = require('es');
		config = {
			_index : 'survey',
			_type : 'banner',
			server : {
				host : 'localhost',
				port : 9200
			}
		},
		es = elasticsearch(config);
		q = req.query.query;
		fromValue = req.query.from;
		sizeValue = req.query.size;
		es.search(
		{
			"from" : fromValue, "size" : sizeValue,
			"query" : {
				"match" : {
					"_all" : q
				}
			},
			"sort" : [
      {"timestamp" : {"order" : "desc"}}
			]
		}, function (err, data) {
			if (err) {
					console.log(err);
				} else {
					res.json(data);
				}
		});
		
	});
	// frontend routes =========================================================
	// route to handle all angular requests
	app.get('*', function(req, res) {
		res.sendfile('index.html', { root: './public/views' }); // load our public/views/index.html file
	});
};
