angular.module('BannerSearchService', []).service('bannerSearch', function($http) {
 this.getResults = function(queryData, fromValue, sizeValue) {
    return $http.get('/api/banner/search',{params: {query:queryData, from:fromValue, size:sizeValue}});
 };
 this.getGeoFeedLatest = function() {
    return $http.get('/api/banner/geofeed/latest');
 };
});
