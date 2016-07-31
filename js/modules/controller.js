app.controller('ctrl', function ($scope, $http) {
    // $scope.base = "http://localhost:8000/";
    $scope.base = "https://taisukeyasuda.github.io/sst-pyramidal-analysis/";

    // retrieve cell names
    $http.get($scope.base+"data/json/cells.json").then(function(response) {
        $scope.cells = response.data;
    });

    $scope.cellData = {};
    $scope.cellDataProcessed = {};

    $scope.default = {};
    $scope.default.choice = 'range';
    $scope.default.number = 10;
    $scope.binSize = 0.01;
    $scope.changed = true; // just to trigger redraw
    $scope.cellSelected = ($scope.selectedCell != undefined);

    $scope.fitData = {};
    $scope.fitData.defaultN = 5;
    $scope.fitData.defaultData = [];
    for (var i = 0; i < $scope.fitData.defaultN; i++) {
        var contact = {};
        contact.s = 0.1;
        contact.q = 0.5;
        contact.p = 0.02;
        $scope.fitData.defaultData.push(contact);
    }
    $scope.fitData.data = {};
    $scope.histogramSimData = undefined;
    $scope.zoom = 'auto';
    $scope.histHeight = 20;

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
    $scope.redraw = function () {
        $scope.changed = !$scope.changed;
    };
    // standard normal variate using Box-Muller transform.
    function randn_bm() {
        var u = 1 - Math.random();
        var v = 1 - Math.random();
        return Math.sqrt( -2.0 * Math.log( u ) ) * Math.cos( 2.0 * Math.PI * v );
    };
    // bernoulli distribution
    function bern(p) {
        return (Math.random() < p);
    };
    function simulateSingle(contacts) {
        var response = 0;
        for (i in contacts) {
            var contact = contacts[i];
            var success = bern(contact.p);
            if (success) {
                var rand = -1;
                while (rand < 0) {
                    rand = (randn_bm()*contact.s + contact.q);
                }
                response += rand;
            }
        }
        return response;
    };
    function simulate(contacts, numReps) {
        var responses = [];
        for (var i = 0; i < numReps; i++) {
            responses.push(simulateSingle(contacts));
        }
        return responses;
    };
    $scope.simulate = function () {
        var numReps = $scope.histogramData.length;
        var responses = simulate($scope.fitData[$scope.selectedCell], numReps);
        $scope.histogramSimData = responses.slice();
        alert('simulated: '+$scope.histogramSimData);
        // $scope.redraw();
    }
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
                if (valid) result.push([col,parseFloat(value,3),undefined]);
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

        // information for fitting cell
        if ($scope.fitData[$scope.selectedCell] == undefined) {
            $scope.fitData[$scope.selectedCell] = $scope.fitData.defaultData;
        }
        $scope.histogramSimData = undefined;
    };
    $scope.changeData = function () {
        $scope.histogramSimData = undefined;
        $scope.histogramData = $scope.processData($scope.cellData[$scope.selectedCell],$scope.trial.choice,$scope.trial.number);
    };
});
