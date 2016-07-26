google.setOnLoadCallback(function () {
    angular.bootstrap(document.body, ['app']);
});
google.load('visualization', '1', {
    packages: ['corechart']
});

var app = angular.module('app', []);
