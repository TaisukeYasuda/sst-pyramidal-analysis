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
    }

    // Initial chart data
    $scope.chartTitle = "Lead Sources";
    $scope.chartWidth = 500;
    $scope.chartHeight = 320;
    $scope.chartData = [
        ['Ad Flyers', 11],
        ['Web (Organic)', 4],
        ['Web (PPC)', 4],
        ['Yellow Pages', 7],
        ['Showroom', 3]
    ];

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
    $scope.changeCell = function() {
        var name = $scope.selectedCell;
        if ($scope.cellData[name] == undefined) {
            $http.get($scope.base+"data/json/"+name+".json").then(function(response) {
                $scope.cellData[name] = response.data;
            });
        }
    }
});
