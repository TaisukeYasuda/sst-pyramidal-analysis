app.directive('histogram', function ($timeout) {
    return {
        restrict: 'EA',
        scope: {
            title: '@title',
            width: '@width',
            height: '@height',
            zeros: '@zeros',
            data: '=data'
        },
        link: function ($scope, $elm, $attr) {

            // Create the data table and instantiate the chart
            var data = new google.visualization.DataTable();
            data.addColumn('string', 'Trial');
            data.addColumn('number', 'Amplitude');
            var chart = new google.visualization.Histogram($elm[0]);

            draw();

            // Watches, to refresh the chart when its data, title or dimensions change
            $scope.$watch('data', function () {
                draw();
            }, true); // true is for deep object equality checking
            $scope.$watch('title', function () {
                draw();
            });
            $scope.$watch('width', function () {
                draw();
            });
            $scope.$watch('height', function () {
                draw();
            });

            function draw() {
                if (!draw.triggered) {
                    draw.triggered = true;
                    $timeout(function () {
                        draw.triggered = false;
                        var label, value;
                        data.removeRows(0, data.getNumberOfRows());
                        angular.forEach($scope.data, function (row,rowNum) {
                            angular.forEach(row, function(entry) {
                                label = rowNum;
                                value = parseFloat(entry, 3);
                                data.addRow([label,value]);
                            });
                        });
                        var options = {
                            'title': $scope.title,
                            'width': $scope.width,
                            'height': $scope.height,
                            'dataOpacity': 0.8
                        };
                        chart.draw(data, options);
                    }, 0, true);
                }
            }
        }
    };
});
