// public/js/controllers/BannerSearchCtrl.js
angular.module('BannerSearchCtrl', ['google-maps']).controller('BannerSearchController', function($scope, $http, $filter, bannerSearch) {
	$scope.maxResults = 25;
	$scope.maxResultsPerPage = 5;
	$scope.totalPages = 0;
	$scope.searchResults = 0;
	$scope.hideResultErrorAlert = true;

	
  bannerSearch.getGeoFeedLatest().success(function(data) {
	
		var output = [];
		hits = data.hits.hits;
		for (i in hits) {
				var mod = {
			"id": "",
			"name": "",
			"latitude": null,
			"longitude": null,
			"category": "",
			};
			mod.id = hits[i]._id;
			mod.name = hits[i].fields['ip'][0];
			mod.latitude = hits[i].fields['location.lon_lat'][1];
			mod.longitude = hits[i].fields['location.lon_lat'][0];
			mod.category = hits[i].fields['device_type'][0];
			if ("None"!== hits[i].fields['device_type'][0]) {
				output.push(mod)
			}
			
		}
    $scope.places = output;
    $scope.markersProperty = output;
    $scope.filteredMarkersProperty = $scope.markersProperty;
		var cats = [];
        for (var i = 0; i < output.length; i++){
            cats[i] = output[i].category;
        }
    
    var sorted_cats = cats.sort();
    
    $scope.categories = [];
        for (var i = 0; i < cats.length; i++){
            if (sorted_cats[i+1] != sorted_cats[i]){
                $scope.categories.push(sorted_cats[i]);
            }
        }
  });

	$scope.$watch( 'orderProp', function ( val ) {
		$scope.filteredMarkersProperty = $filter('filter')($scope.markersProperty, val);
		$scope.zoomProperty = 11;
		$scope.calcFocus();
	});

	$scope.showAll = function($event){
		$scope.orderProp ="0";
		$scope.filteredMarkersProperty = $scope.places;
		$scope.zoomProperty = 11;
		$scope.calcFocus();
	};

	$scope.select = function($event){
		var theName = $event.name;
		var lat = $event.latitude;
		var lng = $event.longitude;
		$scope.filteredMarkersProperty = [$event];
		$scope.centerProperty.lat = lat;
		$scope.centerProperty.lng = lng;
		$scope.zoomProperty = 14;
		$scope.calcFocus();

	};
    $scope.calcFocus = function(){
        var lats = [], longs = [], counter = [];

        for(i=0; i<$scope.filteredMarkersProperty.length; i++)
        {
            lats[i] = $scope.filteredMarkersProperty[i].latitude;
            longs[i] = $scope.filteredMarkersProperty[i].longitude;
        }

        var latCount = 0;
        var longCount = 0;

        for (i=0; i<lats.length; i++){
            latCount += lats[i];
            longCount += longs[i];
        }

        latCount = latCount / lats.length;
        longCount = longCount / longs.length;
        $scope.centerProperty.lat = latCount;
        $scope.centerProperty.lng = longCount;
    };
	angular.extend($scope, {

        /** the initial center of the map */
        centerProperty: {
            lat:43.450,
            lng:-79.683
        },

        /** the initial zoom level of the map */
        zoomProperty: 4,

        /** list of markers to put in the map */

        markersProperty : [],

        // These 2 properties will be set when clicking on the map - click event
        clickedLatitudeProperty: null,
        clickedLongitudeProperty: null
    });
	
	$scope.getPagnationClass = function(pageNumber){
		if ((pageNumber + 1) == $scope.currentPage) {
			return 'active';
		} else {
			return '';
		}
	};
	$scope.noResultsOpen = function(){
		if ($scope.searchResults == 0) {
			return true;
		} else {
			return false;
		}
	};
	$scope.getTimes = function(n){
     return new Array(n);
	};
	
	$scope.switchToPage = function(pageNumber) {
		var fromValue = ($scope.maxResultsPerPage * pageNumber) - $scope.maxResultsPerPage;
		$scope.currentPage = pageNumber;
		bannerSearch.getResults($scope.currentQuery, fromValue, $scope.maxResults).then(function(results) {		
			$scope.searchResults = results;
		});
	};
	
  $scope.search = function() {
		bannerSearch.getResults($scope.queryTerm, 0, $scope.maxResults).then(function(results) {
			$scope.currentPage = 0;			
			$scope.totalResults = results.data.hits.total
			$scope.currentQuery = $scope.queryTerm;
			if ($scope.totalResults > 0) {
				$scope.hideResultErrorAlert = true;
				$scope.currentPage = 1;
				if ($scope.totalResults > $scope.maxResults) {
					$scope.totalPages = Math.round($scope.maxResults / $scope.maxResultsPerPage);
				} else {
					$scope.totalPages = Math.round($scope.totalResults / $scope.maxResultsPerPage);
				}
				$scope.searchResults = results;
			} else {
				$scope.hideResultErrorAlert = false;
				$scope.searchResults = 0;
			}

		});
  };
  
  
  
  
});


