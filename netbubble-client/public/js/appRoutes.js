// public/js/appRoutes.js
	angular.module('appRoutes', []).config(['$routeProvider', '$locationProvider', function($routeProvider, $locationProvider) {

	$routeProvider

		// home page
		.when('/', {
			templateUrl: 'views/home.html',
			controller: 'BannerSearchController'
		})


	$locationProvider.html5Mode(true).hashPrefix('!');

}]);

