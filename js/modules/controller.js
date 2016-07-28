app.controller('ctrl', function ($scope, $http) {
    // $scope.base = "http://localhost:8000/";
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

    $scope.default = {};
    $scope.default.choice = 'range';
    $scope.default.number = 10;
    $scope.binSize = 0.01;
    $scope.cellSelected = ($scope.selectedCell != undefined);

    // initial chart data
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
    $scope.processData = function (cell, choice, number) {
        var result = [];
        angular.forEach(cell, function (entries, col) {
            angular.forEach(entries, function (value) {
                var valid = false;
                if (choice == 'range' && parseInt(col) <= number) {
                    valid = true;
                } else if (choice == 'individual' && parseInt(col) == number) {
                    valid = true;
                }
                if (valid) result.push([col,parseFloat(value,3)]);
            });
        });
        return result;
    };
    $scope.changeCell = function () {
        $scope.zeros = true;
        $scope.trial = {};
        $scope.trial.choice = $scope.default.choice;
        $scope.trial.number = $scope.default.number;
        var name = $scope.selectedCell;
        if ($scope.cellData[name] == undefined) {
            $http.get($scope.base+"data/json/"+name+".json").then(function(response) {
                $scope.cellData[name] = response.data;
                $scope.histogramData = $scope.processData(response.data,$scope.trial.choice,$scope.trial.number);
            });
        } else {
            $scope.histogramData = $scope.processData($scope.cellData[name],$scope.trial.choice,$scope.trial.number);
        }
        $scope.cellSelected = true;
    };
    $scope.changeData = function () {
        $scope.histogramData = $scope.processData($scope.cellData[$scope.selectedCell],$scope.trial.choice,$scope.trial.number);
        if (!$scope.zeros) {
            for (var i = $scope.histogramData.length-1; i >= 0; i--) {
                var row = $scope.histogramData[i];
                if (row[1] == 0.0) {
                    $scope.histogramData.splice(i,1);
                }
            }
        }
    };
});
