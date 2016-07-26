app.controller('ctrl', function ($scope, $http) {
    //$scope.base = "http://localhost:8000/";
    $scope.base = "https://taisukeyasuda.github.io/sst-pyramidal-analysis/";

    // retrieve cell names
    if ($scope.cells == undefined) {
        $http.get($scope.base+"data/json/cells.json").then(function(response) {
            $scope.cells = response.data;
        });
    }

    if ($scope.cellData == undefined) {
        $scope.cellData = {};
        $scope.cellDataProcessed = {};
    }

    $scope.cellSelected = ($scope.selectedCell != undefined);

    // initial chart data
    $scope.chartTitle = "No Cell Selected";
    $scope.chartWidth = 800;
    $scope.chartHeight = 500;

    $scope.deleteRow = function (index) {
        $scope.chartData.splice(index, 1);
    };
    $scope.addRow = function () {
        $scope.chartData.push([]);
    };
    $scope.selectRow = function (index) {
        $scope.selected = index;
    };
    $scope.rowClass = function (index) {
        return ($scope.selected === index) ? "selected" : "";
    };
    $scope.processData = function (cell) {
        var result = [];
        angular.forEach(cell, function (entries, col) {
            angular.forEach(entries, function (value) {
                result.push([col,parseFloat(value,3)]);
            });
        });
        return result;
    };
    $scope.changeCell = function () {
        $scope.zeros = true;
        var name = $scope.selectedCell;
        if ($scope.cellData[name] == undefined) {
            $http.get($scope.base+"data/json/"+name+".json").then(function(response) {
                $scope.cellData[name] = response.data;
                $scope.histogramData = $scope.processData(response.data);
            });
        } else {
            $scope.histogramData = $scope.processData($scope.cellData[name]);
        }
        $scope.cellSelected = true;
    };
    $scope.changeZeros = function () {
        if ($scope.zeros) {
            $scope.histogramData = $scope.processData($scope.cellData[$scope.selectedCell]);
        } else {
            for (var i = $scope.histogramData.length-1; i >= 0; i--) {
                var row = $scope.histogramData[i];
                if (row[1] == 0.0) {
                    $scope.histogramData.splice(i,1);
                }
            }
        }
    };
});
