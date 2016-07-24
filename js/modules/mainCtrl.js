mainApp.controller('mainCtrl', function($scope) {
    $scope.firstName = "Taisuke";
    $scope.lastName = "Yasuda";

    // $http.get("data/json/cells.json")
    // .then(function(response) {
    //   $scope.cells = response.data;
    // },  function(response) {
    //   //Second function handles error
    //   $scope.firstName = response.data;
    // });
    //
    // $http.get("../../data/json/test.txt")
    // .then (function(response) {
    //   $scope.firstName = response.data;
    //   $scope.lastName = response.data;
    // }, function(response) {
    //   //Second function handles error
    //   $scope.lastName = response.status;
    // });
});
